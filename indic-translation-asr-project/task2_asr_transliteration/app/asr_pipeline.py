"""
asr_pipeline.py — OpenAI Whisper-based Automatic Speech Recognition pipeline.

Supports:
  - Audio file transcription (WAV, MP3, M4A, etc.)
  - Language detection
  - Tamil and multilingual transcription
  - Integration with AudioBufferManager for chunked processing
"""

import os
import logging
import tempfile
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class ASRPipeline:
    """
    Wraps OpenAI Whisper for speech-to-text transcription.

    Recommended models:
      - 'small'  : Fast, good for demos (~244M params)
      - 'medium' : Better accuracy (~769M params)
      - 'large'  : Best accuracy (~1.5B params), slow on CPU
    """

    SUPPORTED_LANGUAGES = {
        "auto": None,
        "tamil": "ta",
        "english": "en",
        "hindi": "hi",
        "telugu": "te",
        "kannada": "kn",
        "malayalam": "ml",
    }

    def __init__(self, model_size: str = "small", device: str = "cpu"):
        """
        Args:
            model_size: Whisper model variant ('tiny','small','medium','large').
            device:     'cpu' or 'cuda'.
        """
        self.model_size = model_size
        self.device = device
        self.model = None
        self._loaded = False

    def load(self):
        """Load the Whisper model (lazy loading — call once before transcription)."""
        if self._loaded:
            return
        try:
            import whisper
            logger.info(f"Loading Whisper '{self.model_size}' on {self.device}...")
            self.model = whisper.load_model(self.model_size, device=self.device)
            self._loaded = True
            logger.info("Whisper model loaded ✓")
        except ImportError:
            raise ImportError(
                "openai-whisper not installed. Run: pip install openai-whisper"
            )

    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        task: str = "transcribe",
    ) -> Dict[str, Any]:
        """
        Transcribe an audio file.

        Args:
            audio_path: Path to audio file (WAV/MP3/M4A).
            language:   ISO 639-1 code (e.g. 'ta', 'en') or None for auto-detect.
            task:       'transcribe' or 'translate' (translate → English).

        Returns:
            dict with keys: text, language, segments, duration
        """
        if not self._loaded:
            self.load()

        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info(f"Transcribing: {audio_path} | lang={language} | task={task}")

        options = {
            "task": task,
            "verbose": False,
        }
        if language:
            options["language"] = language

        result = self.model.transcribe(audio_path, **options)

        output = {
            "text": result.get("text", "").strip(),
            "language": result.get("language", "unknown"),
            "segments": result.get("segments", []),
            "duration": result["segments"][-1]["end"] if result.get("segments") else 0.0,
        }

        logger.info(f"Transcription complete: '{output['text'][:80]}...'")
        return output

    def transcribe_bytes(
        self,
        audio_bytes: bytes,
        suffix: str = ".wav",
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Transcribe raw audio bytes by writing to a temp file first.

        Args:
            audio_bytes: Raw audio data.
            suffix:      File extension ('.wav', '.mp3').
            language:    Language code or None.

        Returns:
            Same dict as transcribe().
        """
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        try:
            return self.transcribe(tmp_path, language=language)
        finally:
            os.unlink(tmp_path)

    def detect_language(self, audio_path: str) -> str:
        """
        Detect the language of an audio file.

        Returns:
            ISO 639-1 language code string.
        """
        if not self._loaded:
            self.load()
        import whisper
        audio = whisper.load_audio(audio_path)
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
        _, probs = self.model.detect_language(mel)
        detected = max(probs, key=probs.get)
        logger.info(f"Detected language: {detected}")
        return detected

    def transcribe_with_buffer(self, buffer_manager, output_callback, language=None):
        """
        Process audio chunks from a buffer manager asynchronously.

        Args:
            buffer_manager: AudioBufferManager instance.
            output_callback: Called with transcription dict for each chunk.
            language: Language code or None.
        """
        def process_chunk(audio_path):
            result = self.transcribe(audio_path, language=language)
            output_callback(result)

        thread = buffer_manager.start_consumer(process_chunk)
        return thread

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def __repr__(self):
        return f"ASRPipeline(model={self.model_size}, device={self.device}, loaded={self._loaded})"
