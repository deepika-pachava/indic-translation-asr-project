# Task 2: ASR-Based Transcription and Transliteration System

An end-to-end deployable system for multilingual speech recognition and script conversion.

## System Architecture

```
Audio Input
     ↓
Buffer Queue (queue.Queue — async, overflow-safe)
     ↓
ASR Module (OpenAI Whisper-small/medium)
     ↓
Transcript
     ↓
Transliteration Engine (indic-transliteration)
     ↓
Interactive Gradio Interface
```

## Features
- 🎙️ Audio upload + microphone recording support
- 🌐 Multilingual ASR (Tamil, English, Hindi, Telugu, auto-detect)
- 🔄 Bidirectional transliteration: Tamil ↔ Latin (ITRANS/ISO/HK)
- 📦 Queue-based buffer for chunked/async audio processing
- 🐳 Fully Dockerized for reproducible deployment

## Installation

```bash
git clone <repo>
cd task2_asr_transliteration
pip install -r requirements.txt
```

## Local Run

```bash
python app/main.py
```

Visit `http://localhost:7860`

## Docker Build

```bash
docker build -t asr-system .
```

## Docker Run

```bash
docker run -p 7860:7860 asr-system
```

## Docker Compose

```bash
docker-compose up
```

## Run Tests

```bash
pytest tests/test_pipeline.py -v
```

## Key Components

| File | Description |
|------|-------------|
| `app/main.py` | Entry point — launches Gradio |
| `app/asr_pipeline.py` | Whisper ASR wrapper |
| `app/transliteration.py` | Script conversion engine |
| `app/buffer_manager.py` | Queue-based audio buffer |
| `app/interface.py` | Gradio UI builder |
| `app/utils.py` | Shared utilities |
| `models/model_config.py` | Model configuration registry |
| `tests/test_pipeline.py` | Unit tests |

## Model Details

- **ASR**: `openai/whisper-small` — 244M params, multilingual, strong Tamil support
- **Transliteration**: `indic-transliteration` library — ITRANS, ISO 15919, Harvard-Kyoto schemes
