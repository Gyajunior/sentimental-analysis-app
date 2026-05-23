# 🎭 Shakespearean Sentiment & Authenticity Engine
### Technical Interview Demo — Python + Streamlit

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt
python -m textblob.download_corpora    # downloads punkt tokenizer

# 2. Launch
streamlit run app.py
```

App runs at **http://localhost:8501**

---

## Architecture Overview

```
User Input
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. ShakespeareDetector                                      │
│    └─ Weighted keyword-density heuristic (per 100 words)    │
│       If score < threshold → pipe to converter              │
├─────────────────────────────────────────────────────────────┤
│ 2. TextConverter  (modern → archaic)                        │
│    └─ 30+ cascading regex rules (pronoun, modal, suffix)    │
├─────────────────────────────────────────────────────────────┤
│ 3. SentimentAnalyzer (TextBlob)                             │
│    └─ polarity [-1..1], subjectivity [0..1]                 │
│       → Authoritative Score = (1 - subjectivity) × 100     │
│       → Emotional Score     = subjectivity × 100            │
├─────────────────────────────────────────────────────────────┤
│ 4. VerificationEngine                                       │
│    ├─ Mock mode  (default, zero API keys needed)            │
│    ├─ Live Reddit via PRAW   (opt-in, sidebar toggle)       │
│    └─ Live Google via SerpApi (opt-in, sidebar toggle)      │
│       a) Exact match  → Jaccard similarity > 0.55           │
│       b) Thematic     → content-word Jaccard overlap        │
├─────────────────────────────────────────────────────────────┤
│ 5. Visualizer (Plotly)                                      │
│    ├─ Sentiment Map    (2D scatter vs Shakespeare corpus)   │
│    ├─ Sentence Polarity (bar chart per sentence)            │
│    └─ Literary Profile  (radar: 5 literary dimensions)      │
└─────────────────────────────────────────────────────────────┘
```

---

## How to Explain the Subjectivity/Objectivity Logic in an Interview

### The 30-second pitch
> "TextBlob's sentiment model returns two values. The *polarity* is intuitive —
> positive or negative. The *subjectivity* score is the interesting one:
> it measures how much a sentence relies on personal opinion, emotive adjectives,
> and first-person assertions versus neutral, declarative statement.
> I invert it to get objectivity, which I relabel as 'Regal Authority' —
> because royal proclamations and Shakespearean edicts are grammatically objective:
> 'The King commands,' not 'I feel the King should command.'
> Conversely, soliloquies are maximally subjective: 'Whether 'tis nobler in the mind...'
> That's pure inner deliberation — high subjectivity, low regal authority."

### The technical explanation
```
TextBlob uses a PatternAnalyzer trained on the Subjectivity Dataset (Pang & Lee 2004).
Each word/phrase carries a pre-trained (subjectivity, polarity) pair.
Sentence score = mean of token scores.

Our mapping:
  subjectivity  ∈ [0, 1]  →  Emotional/Narrative Scale (×100)
  objectivity   = 1 - subjectivity  →  Authoritative/Regal Scale (×100)

Why this is valid for Shakespeare:
  - Soliloquies (Hamlet III.i): high subjectivity (~0.4–0.6) — internal debate
  - Proclamations (Henry V):    low subjectivity (~0.1–0.25) — command rhetoric
  - Love sonnets:               high subjectivity (~0.6–0.8) — personal metaphor
```

### Talking points on limitations
- TextBlob's lexicon was trained on movie reviews, not Elizabethan English.
  Archaic words may score as neutral (missing from lexicon) → slight objectivity bias.
- Mitigation: use VADER or a custom Elizabethan lexicon for production.
- Extension: fine-tune a BERT model on Project Gutenberg Shakespeare texts.

---

## API Integration Notes

### Reddit (PRAW) — live mode
1. Create an app at https://www.reddit.com/prefs/apps
2. Enter `client_id` and `client_secret` in the sidebar
3. Toggle "Live Reddit" on

### Google Search (SerpApi) — live mode
1. Get a key at https://serpapi.com
2. Enter key in sidebar under "SerpApi Key"
3. Toggle "Live Google" on

Without keys, the engine runs a realistic mock with pre-seeded Shakespeare corpus snippets.

---

## File Structure

```
shakespeare_engine/
├── app.py           ← Full Streamlit application (~550 lines)
└── requirements.txt ← Python dependencies
```

---

## Interview Talking Points by Section

| Section | What to say |
|---------|-------------|
| Detection | "Weighted keyword density — rare archaic words score 3×, common ones 1×. Prevents false positives from a single 'lo' or 'alas'." |
| Conversion | "Cascading regex — order matters. 'you are' → 'thou art' before 'you' → 'thee', otherwise you get 'thou art' mangled by the second rule." |
| Sentiment | "Two-dimensional sentiment space. Polarity tells you dark vs. light. Subjectivity tells you who's speaking — the character's inner self or an authoritative narrator." |
| Verification | "Two layers: exact (Jaccard > 0.55 on all words) and thematic (Jaccard on content words after stopword removal). Mirrors how real plagiarism detectors work." |
| Visualisation | "The sentiment map puts the input text in a 2D space alongside Hamlet, Sonnet 18, and Richard III. You can immediately see if the text clusters with tragic or comedic works." |
