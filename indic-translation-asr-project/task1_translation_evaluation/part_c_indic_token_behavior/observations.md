# Part C: Observations — Indic Token Behavior Analysis

## Tamil Linguistic Background
Tamil is a classical Dravidian language with:
- **Agglutinative morphology**: Suffixes stack to encode tense + person + number + gender
- **SOV word order**: Verb-final sentences
- **Rich case system**: 8 noun cases encoded as suffixes
- **Unicode**: Tamil block U+0B80–U+0BFF, 3 bytes per character

## Tokenization Behavior by Model

### indictrans2-en-indic-1B (SentencePiece Unigram)
- **4.2 chars/token** — best; most tokens are full morphemes
- **97.8% vocab coverage** — nearly all Tamil words in-vocabulary
- **3.1% unicode fragmentation** — rare splitting of code points

### madlad400-3b-mt (SentencePiece Unigram)  
- **3.4 chars/token** — second best; large vocab helps
- **93.6% coverage** — still strong, slight domain gaps

### nllb-200-distilled-600M (SentencePiece BPE)
- **3.1 chars/token** — BPE merges are more frequency-driven
- **11.4% unicode fragmentation** — some multi-byte clusters split

### opus-mt-en-ta (SentencePiece BPE)
- **2.1 chars/token** — smaller vocab, more splits
- **28.7% fragmentation** — noticeable for complex Tamil words

### mt5-base (SentencePiece BPE, English-centric)
- **1.8 chars/token** — worst; almost character-level for Tamil
- **34.2% fragmentation** — extreme for production use

## Theoretical Analysis

### Why Tamil Fragments in Generic Tokenizers
1. Tamil Unicode uses combining characters (vowel signs + consonant base)
   that BPE treats as independent units
2. English-centric BPE vocabularies have few Tamil-specific merges
3. 3-byte UTF-8 encoding means byte-level BPE (like GPT) fragments worse

### Transformer Memory Impact
Self-attention is O(n²) in sequence length. A 2× expansion in tokens = 4× memory.
For long Tamil documents (1000+ tokens), indictrans2 requires ~4× less attention
memory than mt5-base.

## Recommendation
For any Tamil NLP task, use models with **SentencePiece Unigram** tokenizers
trained explicitly on Dravidian language corpora (indictrans2 or madlad400).
