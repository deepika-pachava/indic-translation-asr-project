"""
interface.py — Gradio-based interactive UI for ASR Transcription & Transliteration.

Architecture:
  Audio Input → Buffer Queue → ASR Module → Transcript → Transliteration Engine → UI
"""

import os
import logging
import tempfile
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

# Lazy imports — only loaded when interface is actually used
_asr = None
_transliterator = None
_buffer = None


def _get_asr():
    global _asr
    if _asr is None:
        from asr_pipeline import ASRPipeline
        _asr = ASRPipeline(model_size="small", device="cpu")
    return _asr


def _get_transliterator():
    global _transliterator
    if _transliterator is None:
        from transliteration import TransliterationEngine
        _transliterator = TransliterationEngine()
    return _transliterator


def _get_buffer():
    global _buffer
    if _buffer is None:
        from buffer_manager import AudioBufferManager
        _buffer = AudioBufferManager(maxsize=20)
    return _buffer


def process_audio(
    audio_path: Optional[str],
    language_choice: str,
    transliteration_target: str,
    save_outputs: bool,
) -> Tuple[str, str, str, str]:
    """
    Main processing function called by Gradio.

    Args:
        audio_path:            Path to uploaded audio file.
        language_choice:       Language selection from dropdown.
        transliteration_target: Target transliteration scheme.
        save_outputs:          Whether to save outputs to disk.

    Returns:
        (transcript_text, transliterated_text, detected_language, status_message)
    """
    if audio_path is None:
        return "", "", "", "⚠️ Please upload an audio file first."

    from utils import save_transcript, save_transliteration, format_segments

    # Language mapping
    lang_map = {
        "Auto-detect": None,
        "Tamil": "ta",
        "English": "en",
        "Hindi": "hi",
        "Telugu": "te",
    }
    language_code = lang_map.get(language_choice, None)

    status_parts = []

    # ── Step 1: Buffer the audio ────────────────────────────────────────
    buffer = _get_buffer()
    buffer.put(audio_path)
    status_parts.append("✅ Audio buffered")

    # ── Step 2: ASR Transcription ────────────────────────────────────────
    asr = _get_asr()
    try:
        asr.load()
        result = asr.transcribe(audio_path, language=language_code)
        transcript = result["text"]
        detected_lang = result.get("language", "unknown")
        segments = result.get("segments", [])
        status_parts.append(f"✅ Transcription complete (lang: {detected_lang})")
    except Exception as e:
        logger.error(f"ASR failed: {e}")
        return "", "", "error", f"❌ ASR Error: {str(e)}"

    # ── Step 3: Transliteration ──────────────────────────────────────────
    transliterator = _get_transliterator()
    scheme_map = {
        "ITRANS (Romanised)": "itrans",
        "ISO 15919": "iast",
        "Harvard-Kyoto": "hk",
        "Devanagari": "devanagari",
    }
    target_scheme = scheme_map.get(transliteration_target, "itrans")

    if transcript:
        try:
            transliterated = transliterator.auto_transliterate(transcript, target=target_scheme)
            status_parts.append(f"✅ Transliteration complete ({target_scheme})")
        except Exception as e:
            logger.error(f"Transliteration failed: {e}")
            transliterated = transcript
            status_parts.append(f"⚠️ Transliteration fallback: {e}")
    else:
        transliterated = ""
        status_parts.append("⚠️ Empty transcript — no transliteration performed")

    # ── Step 4: Save outputs ─────────────────────────────────────────────
    if save_outputs and transcript:
        try:
            base = os.path.join(
                os.path.dirname(__file__), "..", "outputs"
            )
            save_transcript(transcript, detected_lang, os.path.join(base, "transcripts"))
            if transliterated:
                save_transliteration(
                    transcript, transliterated,
                    "auto", target_scheme,
                    os.path.join(base, "transliterations")
                )
            status_parts.append("✅ Outputs saved")
        except Exception as e:
            status_parts.append(f"⚠️ Save failed: {e}")

    status = "\n".join(status_parts)
    return transcript, transliterated, detected_lang, status


def build_interface():
    """Build and return the Gradio Blocks interface."""
    try:
        import gradio as gr
    except ImportError:
        raise ImportError("Gradio not installed. Run: pip install gradio")

    with gr.Blocks(
        title="ASR Transcription & Transliteration",
        theme=gr.themes.Soft(),
        css="""
        .header { text-align: center; margin-bottom: 20px; }
        .output-box { font-size: 15px; }
        """
    ) as demo:

        gr.HTML("""
        <div class='header'>
            <h1>🎙️ ASR Transcription & Transliteration System</h1>
            <p>Upload audio → Get Tamil transcript → Convert to Romanised text</p>
            <p><i>Powered by OpenAI Whisper + indic-transliteration</i></p>
        </div>
        """)

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📤 Input")
                audio_input = gr.Audio(
                    label="Upload Audio File (WAV/MP3/M4A)",
                    type="filepath",
                    sources=["upload", "microphone"],
                )
                language_dropdown = gr.Dropdown(
                    label="Language",
                    choices=["Auto-detect", "Tamil", "English", "Hindi", "Telugu"],
                    value="Auto-detect",
                )
                translit_dropdown = gr.Dropdown(
                    label="Transliteration Target Script",
                    choices=["ITRANS (Romanised)", "ISO 15919", "Harvard-Kyoto", "Devanagari"],
                    value="ITRANS (Romanised)",
                )
                save_checkbox = gr.Checkbox(label="Save outputs to disk", value=False)
                submit_btn = gr.Button("🚀 Transcribe & Transliterate", variant="primary")

            with gr.Column(scale=1):
                gr.Markdown("### 📋 Output")
                transcript_out = gr.Textbox(
                    label="Transcript",
                    placeholder="Transcribed text will appear here...",
                    lines=5,
                    elem_classes=["output-box"],
                )
                translit_out = gr.Textbox(
                    label="Transliteration",
                    placeholder="Transliterated text will appear here...",
                    lines=5,
                    elem_classes=["output-box"],
                )
                detected_lang_out = gr.Textbox(label="Detected Language", interactive=False)
                status_out = gr.Textbox(
                    label="Processing Status",
                    lines=4,
                    interactive=False,
                )

        gr.Markdown("---")
        gr.Markdown("""
        ### ℹ️ How it works
        1. **Audio Buffer** — Your audio is placed into a queue-based buffer
        2. **Whisper ASR** — OpenAI Whisper transcribes the audio to text
        3. **Script Detection** — Detects Tamil or Latin script automatically  
        4. **Transliteration** — Converts Tamil → Latin (or Latin → Tamil) using `indic-transliteration`

        ### 📁 Supported Formats
        WAV · MP3 · M4A · FLAC · OGG

        ### 🔧 Running with Docker
        ```bash
        docker build -t asr-system .
        docker run -p 7860:7860 asr-system
        ```
        """)

        submit_btn.click(
            fn=process_audio,
            inputs=[audio_input, language_dropdown, translit_dropdown, save_checkbox],
            outputs=[transcript_out, translit_out, detected_lang_out, status_out],
        )

        # Example inputs
        gr.Examples(
            examples=[
                [None, "Tamil", "ITRANS (Romanised)", False],
            ],
            inputs=[audio_input, language_dropdown, translit_dropdown, save_checkbox],
            label="Examples",
        )

    return demo
