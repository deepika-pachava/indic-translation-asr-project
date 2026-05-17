"""
model_config.py — Central configuration for all models used in this project.
"""

# ── Whisper ASR Models ────────────────────────────────────────────────────────
WHISPER_CONFIGS = {
    "tiny": {
        "model_id": "openai/whisper-tiny",
        "params_millions": 39,
        "multilingual": True,
        "relative_speed": "~32x",
        "recommended_for": "Quick demos, low RAM",
    },
    "small": {
        "model_id": "openai/whisper-small",
        "params_millions": 244,
        "multilingual": True,
        "relative_speed": "~6x",
        "recommended_for": "Good accuracy/speed balance ✅ RECOMMENDED",
    },
    "medium": {
        "model_id": "openai/whisper-medium",
        "params_millions": 769,
        "multilingual": True,
        "relative_speed": "~2x",
        "recommended_for": "High accuracy Tamil ASR",
    },
    "large": {
        "model_id": "openai/whisper-large-v3",
        "params_millions": 1550,
        "multilingual": True,
        "relative_speed": "1x (baseline)",
        "recommended_for": "Best accuracy, needs GPU",
    },
}

# ── Translation Models ────────────────────────────────────────────────────────
TRANSLATION_MODELS = {
    "indictrans2": {
        "model_id": "ai4bharat/indictrans2-en-indic-1B",
        "tokenizer": "SentencePiece (Unigram)",
        "vocab_size": 64000,
        "src_lang_code": "eng_Latn",
        "tgt_lang_code": "tam_Taml",
        "recommended": True,
        "notes": "Best for Tamil; Indic-aware tokenizer",
    },
    "nllb": {
        "model_id": "facebook/nllb-200-distilled-600M",
        "tokenizer": "SentencePiece (BPE)",
        "vocab_size": 256000,
        "src_lang_code": "eng_Latn",
        "tgt_lang_code": "tam_Taml",
        "recommended": False,
        "notes": "Good multilingual coverage; not Tamil-specific",
    },
    "mt5": {
        "model_id": "google/mt5-base",
        "tokenizer": "SentencePiece (BPE)",
        "vocab_size": 250000,
        "src_lang_code": None,
        "tgt_lang_code": None,
        "recommended": False,
        "notes": "General seq2seq; requires fine-tuning for Tamil",
    },
    "opus_ta": {
        "model_id": "Helsinki-NLP/opus-mt-en-ta",
        "tokenizer": "SentencePiece (BPE)",
        "vocab_size": 65000,
        "src_lang_code": None,
        "tgt_lang_code": None,
        "recommended": False,
        "notes": "Lightweight EN→TA; limited domain coverage",
    },
    "madlad": {
        "model_id": "google/madlad400-3b-mt",
        "tokenizer": "SentencePiece (Unigram)",
        "vocab_size": 256000,
        "src_lang_code": None,
        "tgt_lang_code": None,
        "recommended": False,
        "notes": "Massive multilingual; strong Tamil performance",
    },
}

# ── Default Settings ──────────────────────────────────────────────────────────
DEFAULT_CONFIG = {
    "asr_model": "small",
    "translation_model": "indictrans2",
    "transliteration_scheme": "itrans",
    "device": "cpu",
    "batch_size": 4,
    "max_audio_length_seconds": 300,
    "buffer_maxsize": 50,
    "gradio_port": 7860,
    "gradio_host": "0.0.0.0",
}
