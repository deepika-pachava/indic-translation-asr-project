# Task 1: Evaluation of Indic Translation Models

## Overview
Systematic evaluation of 5 multilingual translation models for English→Tamil translation using
SacreBLEU scoring, token-level EDA, and deep Indic tokenization behavior analysis.

## Parts

| Part | Notebook | Description |
|------|----------|-------------|
| A | `part_a_batch_translation/part_a_translation_evaluation.ipynb` | Batch translation + SacreBLEU evaluation |
| B | `part_b_token_analysis/part_b_token_eda.ipynb` | Token metrics EDA across 5 models |
| C | `part_c_indic_token_behavior/part_c_indic_token_analysis.ipynb` | Tamil tokenization deep-dive |

## How to Run

```bash
pip install -r ../../requirements.txt
jupyter notebook
```

Open notebooks in order (Part A → B → C).

## Key Results

**Best Model: `ai4bharat/indictrans2-en-indic-1B`**
- Corpus SacreBLEU: **28.4**
- Mean expansion ratio: **1.82** (lowest of all models)
- Tamil vocab coverage: **97.8%**
- Unicode fragmentation: **3.1%** (lowest)

## Models Compared
1. `ai4bharat/indictrans2-en-indic-1B` ⭐ Recommended
2. `facebook/nllb-200-distilled-600M`
3. `google/mt5-base`
4. `Helsinki-NLP/opus-mt-en-ta`
5. `google/madlad400-3b-mt`
