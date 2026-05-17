"""
main.py — Entry point for the ASR-Based Transcription and Transliteration System.
Launches the Gradio interface on port 7860.
"""

import os
import sys

# Ensure app directory is in path
sys.path.insert(0, os.path.dirname(__file__))

from interface import build_interface

if __name__ == "__main__":
    print("=" * 60)
    print("  ASR Transcription & Transliteration System")
    print("  Powered by OpenAI Whisper + indic-transliteration")
    print("=" * 60)
    
    demo = build_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
    )
