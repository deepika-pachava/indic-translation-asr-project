"""
transliteration.py — Script conversion using the indic-transliteration library.

Supports transliteration between:
  - Tamil (Grantha) → Latin (ISO 15919 / ITRANS / HK / Velthuis)
  - Latin (ITRANS) → Tamil
  - Tamil → Devanagari, and other cross-script pairs
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TransliterationEngine:
    """
    Wraps indic-transliteration for bidirectional script conversion.

    Primary use-case:
      Tamil script  → Latin (Romanised Tamil)  for non-Tamil readers
      Latin (ITRANS) → Tamil script              for keyboard input
    """

    # Supported scheme identifiers from indic-transliteration
    SCHEMES = {
        "tamil": "tamil",         # Tamil Unicode script
        "devanagari": "devanagari",
        "itrans": "itrans",       # Popular Romanisation scheme
        "iso": "iast",            # ISO 15919 / IAST
        "hk": "hk",               # Harvard-Kyoto
        "slp1": "slp1",
        "velthuis": "velthuis",
    }

    def __init__(self):
        self._lib_available = False
        self._load_library()

    def _load_library(self):
        try:
            from indic_transliteration import sanscript
            from indic_transliteration.sanscript import transliterate
            self._sanscript = sanscript
            self._transliterate = transliterate
            self._lib_available = True
            logger.info("indic-transliteration library loaded ✓")
        except ImportError:
            logger.warning(
                "indic-transliteration not installed. "
                "Run: pip install indic-transliteration\n"
                "Falling back to basic Romanisation."
            )
            self._lib_available = False

    def transliterate(
        self,
        text: str,
        from_scheme: str = "tamil",
        to_scheme: str = "itrans",
    ) -> str:
        """
        Convert text from one script to another.

        Args:
            text:        Input text in the source script.
            from_scheme: Source scheme key (see SCHEMES).
            to_scheme:   Target scheme key (see SCHEMES).

        Returns:
            Transliterated string.

        Example:
            engine.transliterate("வணக்கம்", "tamil", "itrans")
            → "vaNakkam"
        """
        if not text or not text.strip():
            return ""

        if self._lib_available:
            try:
                src = getattr(self._sanscript, from_scheme.upper(), self._sanscript.TAMIL)
                tgt = getattr(self._sanscript, to_scheme.upper(), self._sanscript.ITRANS)
                result = self._transliterate(text, src, tgt)
                return result
            except Exception as e:
                logger.error(f"Transliteration error: {e}")
                return self._fallback_romanise(text)
        else:
            return self._fallback_romanise(text)

    def tamil_to_latin(self, text: str, scheme: str = "itrans") -> str:
        """Convenience: Tamil script → Latin Romanisation."""
        return self.transliterate(text, from_scheme="tamil", to_scheme=scheme)

    def latin_to_tamil(self, text: str, scheme: str = "itrans") -> str:
        """Convenience: Latin ITRANS → Tamil script."""
        return self.transliterate(text, from_scheme=scheme, to_scheme="tamil")

    def tamil_to_devanagari(self, text: str) -> str:
        """Convert Tamil script to Devanagari."""
        return self.transliterate(text, from_scheme="tamil", to_scheme="devanagari")

    def _fallback_romanise(self, text: str) -> str:
        """
        Basic character-level Tamil → Latin mapping as fallback
        when indic-transliteration is not installed.
        """
        mapping = {
            'அ': 'a', 'ஆ': 'aa', 'இ': 'i', 'ஈ': 'ii', 'உ': 'u', 'ஊ': 'uu',
            'எ': 'e', 'ஏ': 'ee', 'ஐ': 'ai', 'ஒ': 'o', 'ஓ': 'oo', 'ஔ': 'au',
            'க': 'ka', 'ங': 'nga', 'ச': 'cha', 'ஞ': 'nya', 'ட': 'ta', 'ண': 'na',
            'த': 'tha', 'ந': 'na', 'ப': 'pa', 'ம': 'ma', 'ய': 'ya', 'ர': 'ra',
            'ல': 'la', 'வ': 'va', 'ழ': 'zha', 'ள': 'lla', 'ற': 'rra', 'ன': 'nna',
            'ஜ': 'ja', 'ஶ': 'sha', 'ஷ': 'sha', 'ஸ': 'sa', 'ஹ': 'ha',
            '்': '', 'ா': 'aa', 'ி': 'i', 'ீ': 'ii', 'ு': 'u', 'ூ': 'uu',
            'ெ': 'e', 'ே': 'ee', 'ை': 'ai', 'ொ': 'o', 'ோ': 'oo', 'ௌ': 'au',
            '்': '', ' ': ' ', '\n': '\n',
        }
        result = []
        for char in text:
            result.append(mapping.get(char, char))
        return ''.join(result)

    def detect_script(self, text: str) -> str:
        """
        Heuristically detect if text is Tamil or Latin script.

        Returns:
            'tamil', 'latin', or 'mixed'
        """
        if not text:
            return "unknown"
        
        tamil_chars = sum(1 for c in text if '\u0B80' <= c <= '\u0BFF')
        latin_chars = sum(1 for c in text if c.isascii() and c.isalpha())
        total = len(text.replace(" ", ""))
        
        if total == 0:
            return "unknown"
        
        tamil_ratio = tamil_chars / total
        latin_ratio = latin_chars / total
        
        if tamil_ratio > 0.5:
            return "tamil"
        elif latin_ratio > 0.5:
            return "latin"
        else:
            return "mixed"

    def auto_transliterate(self, text: str, target: str = "itrans") -> str:
        """
        Auto-detect source script and transliterate to target.

        Args:
            text:   Input text (Tamil or Latin).
            target: Target scheme ('itrans', 'iso', etc.)

        Returns:
            Transliterated text.
        """
        script = self.detect_script(text)
        if script == "tamil":
            return self.tamil_to_latin(text, scheme=target)
        elif script == "latin":
            return self.latin_to_tamil(text, scheme=target)
        else:
            return text  # Mixed — return as-is

    @property
    def is_available(self) -> bool:
        return self._lib_available

    def __repr__(self):
        return f"TransliterationEngine(lib_available={self._lib_available})"
