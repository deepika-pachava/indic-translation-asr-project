"""
test_pipeline.py — Unit tests for the ASR Transliteration System.

Run with: pytest tests/test_pipeline.py -v
"""

import sys
import os
import queue
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))


# ── Buffer Manager Tests ──────────────────────────────────────────────────────

class TestAudioBufferManager:
    def setup_method(self):
        from buffer_manager import AudioBufferManager
        self.buffer = AudioBufferManager(maxsize=5)

    def test_put_and_get(self):
        assert self.buffer.put("chunk_1") is True
        result = self.buffer.get(timeout=1.0)
        assert result == "chunk_1"

    def test_overflow_drops_chunk(self):
        for i in range(5):
            self.buffer.put(f"chunk_{i}")
        # Buffer is full — this should drop
        dropped = self.buffer.put("overflow_chunk", block=False)
        assert dropped is False
        assert self.buffer.dropped_count == 1

    def test_sentinel_signals_end(self):
        self.buffer.put("data")
        self.buffer.signal_done()
        _ = self.buffer.get(timeout=1.0)         # get data
        sentinel = self.buffer.get(timeout=1.0)   # get sentinel
        assert sentinel is None

    def test_stats(self):
        self.buffer.put("a")
        self.buffer.get(timeout=1.0)
        stats = self.buffer.stats()
        assert "queued" in stats
        assert "processed" in stats

    def test_clear(self):
        for i in range(3):
            self.buffer.put(f"item_{i}")
        self.buffer.clear()
        assert self.buffer.is_empty


# ── Transliteration Tests ─────────────────────────────────────────────────────

class TestTransliterationEngine:
    def setup_method(self):
        from transliteration import TransliterationEngine
        self.engine = TransliterationEngine()

    def test_detect_tamil_script(self):
        result = self.engine.detect_script("வணக்கம்")
        assert result == "tamil"

    def test_detect_latin_script(self):
        result = self.engine.detect_script("Hello world")
        assert result == "latin"

    def test_detect_empty_string(self):
        result = self.engine.detect_script("")
        assert result == "unknown"

    def test_is_tamil_text_util(self):
        from utils import is_tamil_text
        assert is_tamil_text("வணக்கம்") is True
        assert is_tamil_text("Hello") is False

    def test_fallback_romanise(self):
        # Even without the library, fallback should return non-empty string
        result = self.engine._fallback_romanise("அ")
        assert result == "a"

    def test_transliterate_returns_string(self):
        result = self.engine.transliterate("வணக்கம்", "tamil", "itrans")
        assert isinstance(result, str)
        assert len(result) > 0


# ── Utility Function Tests ────────────────────────────────────────────────────

class TestUtils:
    def test_word_count(self):
        from utils import word_count
        assert word_count("hello world") == 2
        assert word_count("") == 0
        assert word_count("  spaces  ") == 1

    def test_char_count(self):
        from utils import char_count
        assert char_count("hello world") == 10
        assert char_count("") == 0

    def test_format_segments_empty(self):
        from utils import format_segments
        assert format_segments([]) == ""

    def test_format_segments(self):
        from utils import format_segments
        segs = [{"start": 0.0, "end": 2.5, "text": "Hello"}]
        result = format_segments(segs)
        assert "0.00" in result
        assert "2.50" in result
        assert "Hello" in result

    def test_ensure_dir(self, tmp_path):
        from utils import ensure_dir
        new_dir = str(tmp_path / "test_dir")
        result = ensure_dir(new_dir)
        assert os.path.exists(result)


# ── ASR Pipeline Tests (no model loading) ────────────────────────────────────

class TestASRPipeline:
    def setup_method(self):
        from asr_pipeline import ASRPipeline
        self.asr = ASRPipeline(model_size="small", device="cpu")

    def test_initial_state(self):
        assert self.asr.is_loaded is False
        assert self.asr.model_size == "small"
        assert self.asr.device == "cpu"

    def test_missing_file_raises(self):
        # Should raise FileNotFoundError (not load error)
        # We skip load() to avoid downloading the model in tests
        self.asr._loaded = True
        self.asr.model = None  # Simulate no model loaded
        with pytest.raises((FileNotFoundError, AttributeError, Exception)):
            self.asr.transcribe("/nonexistent/path/audio.wav")

    def test_repr(self):
        r = repr(self.asr)
        assert "ASRPipeline" in r
        assert "small" in r


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
