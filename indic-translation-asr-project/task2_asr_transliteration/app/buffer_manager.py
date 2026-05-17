"""
buffer_manager.py — Queue-based buffer system for chunked audio processing.

Implements an asynchronous producer-consumer pattern using queue.Queue()
to handle audio chunks without overflow and support real-time interaction.
"""

import queue
import threading
import logging
from typing import Optional, Callable, Any

logger = logging.getLogger(__name__)


class AudioBufferManager:
    """
    Manages a bounded FIFO queue for audio chunks.
    
    - Producer (audio input) puts chunks into the queue.
    - Consumer (ASR pipeline) gets chunks for processing.
    - Prevents buffer overflow with maxsize limit.
    - Supports graceful shutdown via sentinel value.
    """

    SENTINEL = None  # Poison pill to signal end of stream

    def __init__(self, maxsize: int = 50):
        """
        Args:
            maxsize: Maximum number of chunks in the buffer.
                     If full, put() will block until space is available.
        """
        self._queue: queue.Queue = queue.Queue(maxsize=maxsize)
        self._lock = threading.Lock()
        self._dropped = 0
        self._processed = 0
        self._running = False

    # ── Producer API ────────────────────────────────────────────────────

    def put(self, chunk: Any, block: bool = True, timeout: float = 2.0) -> bool:
        """
        Add an audio chunk to the buffer.

        Args:
            chunk: Audio data (numpy array, bytes, or file path).
            block: If True, block until space is available (up to timeout).
            timeout: Max seconds to wait when buffer is full.

        Returns:
            True if successfully enqueued, False if dropped (overflow).
        """
        try:
            self._queue.put(chunk, block=block, timeout=timeout)
            return True
        except queue.Full:
            with self._lock:
                self._dropped += 1
            logger.warning(f"Buffer overflow — chunk dropped (total dropped: {self._dropped})")
            return False

    def put_nowait(self, chunk: Any) -> bool:
        """Non-blocking put; drops chunk immediately if buffer is full."""
        return self.put(chunk, block=False)

    def signal_done(self):
        """Send sentinel to notify consumer that the stream has ended."""
        self._queue.put(self.SENTINEL)

    # ── Consumer API ────────────────────────────────────────────────────

    def get(self, block: bool = True, timeout: float = 5.0) -> Optional[Any]:
        """
        Retrieve the next audio chunk from the buffer.

        Returns:
            Audio chunk, or None (sentinel = stream ended), or raises queue.Empty.
        """
        try:
            chunk = self._queue.get(block=block, timeout=timeout)
            if chunk is not self.SENTINEL:
                with self._lock:
                    self._processed += 1
            return chunk
        except queue.Empty:
            return ...  # Ellipsis signals timeout (no sentinel)

    def task_done(self):
        """Mark last retrieved chunk as processed (for join() support)."""
        self._queue.task_done()

    # ── Control ─────────────────────────────────────────────────────────

    def clear(self):
        """Empty the buffer (e.g., on user cancel)."""
        with self._lock:
            while not self._queue.empty():
                try:
                    self._queue.get_nowait()
                except queue.Empty:
                    break

    def start_consumer(self, callback: Callable, daemon: bool = True) -> threading.Thread:
        """
        Start a background thread that continuously calls callback(chunk)
        for each chunk until the sentinel is received.

        Args:
            callback: Function to call with each audio chunk.
            daemon:   If True, thread exits when main program exits.

        Returns:
            The started Thread object.
        """
        self._running = True

        def _worker():
            logger.info("Buffer consumer thread started")
            while self._running:
                chunk = self.get(timeout=3.0)
                if chunk is ...:
                    continue  # Timeout — keep waiting
                if chunk is self.SENTINEL:
                    logger.info("Buffer consumer received sentinel — stopping")
                    break
                try:
                    callback(chunk)
                    self.task_done()
                except Exception as e:
                    logger.error(f"Consumer callback error: {e}")
            logger.info("Buffer consumer thread stopped")

        t = threading.Thread(target=_worker, daemon=daemon)
        t.start()
        return t

    def stop(self):
        """Signal the consumer worker to stop."""
        self._running = False
        self.signal_done()

    # ── Stats ────────────────────────────────────────────────────────────

    @property
    def qsize(self) -> int:
        return self._queue.qsize()

    @property
    def is_empty(self) -> bool:
        return self._queue.empty()

    @property
    def dropped_count(self) -> int:
        return self._dropped

    @property
    def processed_count(self) -> int:
        return self._processed

    def stats(self) -> dict:
        return {
            "queued": self.qsize,
            "processed": self._processed,
            "dropped": self._dropped,
            "running": self._running,
        }

    def __repr__(self):
        return (
            f"AudioBufferManager(qsize={self.qsize}, "
            f"processed={self._processed}, dropped={self._dropped})"
        )
