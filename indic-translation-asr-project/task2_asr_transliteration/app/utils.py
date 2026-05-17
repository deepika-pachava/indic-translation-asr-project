"""
utils.py — Shared utility functions for the ASR Transliteration System.
"""

import os
import json
import logging
import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO"):
    """Configure root logger with timestamp format."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def ensure_dir(path: str) -> str:
    """Create directory if it doesn't exist; return the path."""
    os.makedirs(path, exist_ok=True)
    return path


def save_transcript(
    text: str,
    language: str,
    output_dir: str = "outputs/transcripts",
    prefix: str = "transcript",
) -> str:
    """
    Save a transcript to a timestamped text file.

    Returns:
        Path to the saved file.
    """
    ensure_dir(output_dir)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.txt"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Language:  {language}\n")
        f.write(f"{'=' * 50}\n")
        f.write(text + "\n")
    
    logger.info(f"Transcript saved: {filepath}")
    return filepath


def save_transliteration(
    original: str,
    transliterated: str,
    from_scheme: str,
    to_scheme: str,
    output_dir: str = "outputs/transliterations",
) -> str:
    """
    Save transliteration result to a JSON file.

    Returns:
        Path to the saved file.
    """
    ensure_dir(output_dir)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"transliteration_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    data = {
        "timestamp": timestamp,
        "from_scheme": from_scheme,
        "to_scheme": to_scheme,
        "original": original,
        "transliterated": transliterated,
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Transliteration saved: {filepath}")
    return filepath


def format_segments(segments: list) -> str:
    """
    Format Whisper segment list into readable timestamped text.

    Args:
        segments: List of dicts with 'start', 'end', 'text'.

    Returns:
        Formatted string like: "[0.00 → 3.40] Hello world."
    """
    if not segments:
        return ""
    lines = []
    for seg in segments:
        start = seg.get("start", 0)
        end = seg.get("end", 0)
        text = seg.get("text", "").strip()
        lines.append(f"[{start:.2f} → {end:.2f}] {text}")
    return "\n".join(lines)


def is_tamil_text(text: str) -> bool:
    """Return True if text contains Tamil Unicode characters."""
    return any('\u0B80' <= c <= '\u0BFF' for c in text)


def word_count(text: str) -> int:
    """Count words in text."""
    return len(text.split()) if text.strip() else 0


def char_count(text: str) -> int:
    """Count non-space characters."""
    return len(text.replace(" ", ""))
