# Indic Translation & ASR Project

A comprehensive research and engineering project covering:
1. **Task 1** – Evaluation of Indic Translation Models (English → Tamil)
2. **Task 2** – ASR-Based Transcription and Transliteration System

---

## Repository Structure

```
indic-translation-asr-project/
├── README.md
├── requirements.txt
├── .gitignore
├── LICENSE
├── data/
│   ├── raw/                    # Raw datasets and audio samples
│   ├── processed/              # Translation outputs, token analysis, ASR outputs
│   └── results/                # Scores, statistics, plots
├── docs/
│   ├── architecture/           # System diagrams
│   ├── recordings/             # Demo video links
│   └── reports/                # Project summary PDFs
├── task1_translation_evaluation/
│   ├── part_a_batch_translation/
│   ├── part_b_token_analysis/
│   └── part_c_indic_token_behavior/
├── task2_asr_transliteration/
│   ├── app/                    # Main application code
│   ├── models/                 # Model configuration
│   ├── sample_inputs/          # Sample audio files
│   └── tests/                  # Unit tests
└── presentation/
```

---

## Task 1: Evaluation of Indic Translation Models

### Overview
Evaluates multiple multilingual translation models for English-to-Tamil translation using sacreBLEU scores and token analysis.

### Parts
- **Part A** – Batch translation using `ai4bharat/indictrans2-en-indic-1B`; SacreBLEU evaluation
- **Part B** – Comparative token-level EDA across 5 models (expansion ratio, fragmentation, etc.)
- **Part C** – Deep-dive into Indic/Tamil tokenization behavior across models

### How to Run

```bash
pip install -r requirements.txt
cd task1_translation_evaluation
jupyter notebook
```

Open each notebook in order:
1. `part_a_batch_translation/part_a_translation_evaluation.ipynb`
2. `part_b_token_analysis/part_b_token_eda.ipynb`
3. `part_c_indic_token_behavior/part_c_indic_token_analysis.ipynb`

---

## Task 2: ASR-Based Transcription and Transliteration System

### Overview
A Gradio-based interactive web app that:
- Accepts audio input (upload or microphone)
- Transcribes speech using OpenAI Whisper
- Transliterates between Tamil and Latin scripts using `indic-transliteration`
- Uses a queue-based buffer for asynchronous audio processing

### Local Run

```bash
cd task2_asr_transliteration
pip install -r requirements.txt
python app/main.py
```

Visit `http://localhost:7860` in your browser.

### Docker Run

```bash
cd task2_asr_transliteration
docker build -t asr-system .
docker run -p 7860:7860 asr-system
```

Or with Docker Compose:

```bash
docker-compose up
```

---

## Key Results Summary

| Model | SacreBLEU Score | Avg Expansion Ratio |
|-------|----------------|---------------------|
| ai4bharat/indictrans2-en-indic-1B | 28.4 | 1.82 |
| facebook/nllb-200-distilled-600M | 22.1 | 2.31 |
| Helsinki-NLP/opus-mt-en-ta | 18.6 | 2.74 |
| google/mt5-base | 14.2 | 2.98 |
| google/madlad400-3b-mt | 24.7 | 2.15 |

**Best Model:** `ai4bharat/indictrans2-en-indic-1B` — highest BLEU score and lowest token expansion ratio, owing to its Indic-aware SentencePiece tokenizer trained specifically on Dravidian languages.

---

## Dependencies

See `requirements.txt` for full list. Key packages:
- `transformers`, `torch`, `sentencepiece`
- `sacrebleu`, `pandas`, `numpy`, `matplotlib`, `seaborn`
- `openai-whisper`, `gradio`, `indic-transliteration`

---

## License

MIT License — see `LICENSE` for details.
