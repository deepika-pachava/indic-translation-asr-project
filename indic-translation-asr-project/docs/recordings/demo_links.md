DEMO RECORDINGS:
Task 1 Demo: https://drive.google.com/file/d/1x6Ohb_snMC5OyLTuneBRAPRcp1pUH__b/view?usp=sharing
Task 2 Demo: https://drive.google.com/file/d/1XCJ8use2fvOEd43EjfnTUNEMD4XqEG8A/view?usp=sharing

─────────────────────────────────────────────

REPOSITORY SUMMARY:

This repository contains two completed projects for the TAMIZH Round 2 evaluation.

TASK 1 — Evaluation of Indic Translation Models (English to Tamil)

Part A: Batch translated 20 English sentences to Tamil using
ai4bharat/indictrans2-en-indic-1B model and evaluated using SacreBLEU.
Corpus BLEU score achieved: 52.72. Outputs include translation CSV and
score analysis charts.

Part B: Compared 5 multilingual models (indictrans2, NLLB-200, mT5-base,
Helsinki opus-mt, MADLAD400) on token-level metrics including expansion
ratio, subword fragmentation, and unknown token rate. indictrans2 achieved
the best expansion ratio of 1.82 due to its Dravidian-aware SentencePiece
tokenizer.

Part C: Deep analysis of Tamil tokenization behavior across all 5 models.
indictrans2 achieved 97.8% Tamil vocabulary coverage and only 3.1% Unicode
fragmentation, significantly outperforming general-purpose models like
mT5-base (78.3% coverage, 34.2% fragmentation).

TASK 2 — ASR-Based Transcription and Transliteration System

Built an end-to-end deployable system using OpenAI Whisper (small model)
for multilingual speech recognition and indic-transliteration library for
Tamil to Latin script conversion. Key components include a queue-based
AudioBufferManager for asynchronous audio processing, a Gradio web
interface for live interaction, and full Docker + docker-compose deployment
setup. 19 unit tests written and passing covering all core modules.
