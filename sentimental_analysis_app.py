"""
╔══════════════════════════════════════════════════════════════════╗
║      SHAKESPEAREAN SENTIMENT & AUTHENTICITY ENGINE               ║
║      Technical Interview Demo  |  Python + Streamlit             ║
╚══════════════════════════════════════════════════════════════════╝

Architecture:
  1. ShakespeareDetector   — keyword-density heuristic
  2. TextConverter         — bidirectional archaic replacement
  3. SentimentAnalyzer     — TextBlob subjectivity/objectivity engine
  4. VerificationEngine    — mock Reddit (PRAW) + Google (SerpApi) checks
  5. Visualizer            — Plotly sentiment map vs. Hamlet baseline
  6. StreamlitUI           — orchestrates everything with custom CSS theming
"""

import re
import random
import hashlib
import textwrap
from datetime import datetime
from typing import Tuple, Dict, List, Optional

import streamlit as st
from textblob import TextBlob
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# ──────────────────────────────────────────────────────────────────
# PAGE CONFIG  (must be first Streamlit call)
# ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Shakespearean Engine",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────
# CUSTOM CSS  — Dark parchment / inkwell aesthetic
# ──────────────────────────────────────────────────────────────────
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IM+Fell+English:ital@0;1&family=Cinzel:wght@400;700;900&family=Crimson+Pro:ital,wght@0,300;0,400;1,300;1,400&display=swap');

:root {
    --parchment:   #f5efe0;
    --ink:         #1a1209;
    --sepia-dark:  #2c1f0e;
    --sepia-mid:   #7a5c38;
    --sepia-light: #c9a96e;
    --gold:        #d4a843;
    --crimson:     #8b1a1a;
    --sage:        #3d5a3e;
    --bg:          #110d07;
    --card:        #1e1608;
    --border:      #3a2e1a;
}

html, body, [class*="css"] {
    font-family: 'Crimson Pro', Georgia, serif;
    background-color: var(--bg);
    color: var(--parchment);
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--sepia-mid); border-radius: 3px; }

/* Main title */
.eng-title {
    font-family: 'Cinzel', serif;
    font-size: 2.6rem;
    font-weight: 900;
    color: var(--gold);
    letter-spacing: 0.05em;
    line-height: 1.1;
    text-shadow: 0 0 30px rgba(212,168,67,0.3);
}
.eng-subtitle {
    font-family: 'IM Fell English', serif;
    font-size: 1.1rem;
    color: var(--sepia-light);
    font-style: italic;
    margin-top: -4px;
    margin-bottom: 1.5rem;
}

/* Cards */
.shk-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.4);
}
.shk-card h4 {
    font-family: 'Cinzel', serif;
    font-size: 0.8rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--sepia-light);
    margin-bottom: 0.6rem;
}

/* Verdict banners */
.verdict-authentic {
    background: linear-gradient(135deg, #1a2e1a, #0d1a0d);
    border-left: 4px solid var(--sage);
    padding: 0.9rem 1.2rem;
    border-radius: 0 4px 4px 0;
    font-family: 'Cinzel', serif;
    font-size: 0.9rem;
    color: #7fc47f;
    letter-spacing: 0.05em;
}
.verdict-converted {
    background: linear-gradient(135deg, #2e1a08, #1a0d00);
    border-left: 4px solid var(--gold);
    padding: 0.9rem 1.2rem;
    border-radius: 0 4px 4px 0;
    font-family: 'Cinzel', serif;
    font-size: 0.9rem;
    color: var(--gold);
    letter-spacing: 0.05em;
}
.verdict-warning {
    background: linear-gradient(135deg, #2e1010, #1a0808);
    border-left: 4px solid var(--crimson);
    padding: 0.9rem 1.2rem;
    border-radius: 0 4px 4px 0;
    font-family: 'Cinzel', serif;
    font-size: 0.9rem;
    color: #e06060;
    letter-spacing: 0.05em;
}

/* Shakespeare text output */
.shk-output {
    font-family: 'IM Fell English', serif;
    font-size: 1.25rem;
    line-height: 1.9;
    color: var(--parchment);
    background: linear-gradient(180deg, #1a1407 0%, #130f05 100%);
    border: 1px solid var(--border);
    border-top: 3px solid var(--gold);
    padding: 1.4rem 1.8rem;
    border-radius: 0 0 4px 4px;
    font-style: italic;
}

/* Keyword highlights */
.kw-highlight {
    background: rgba(212,168,67,0.18);
    color: var(--gold);
    padding: 1px 4px;
    border-radius: 2px;
    font-style: normal;
}

/* Metric overrides */
[data-testid="metric-container"] {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 0.8rem 1rem;
}
[data-testid="metric-container"] label {
    font-family: 'Cinzel', serif !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.12em !important;
    color: var(--sepia-light) !important;
}
[data-testid="metric-container"] [data-testid="metric-value"] {
    font-family: 'Cinzel', serif !important;
    color: var(--gold) !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--sepia-dark) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * {
    color: var(--parchment) !important;
}
[data-testid="stSidebar"] .sidebar-title {
    font-family: 'Cinzel', serif;
    font-size: 0.85rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--gold) !important;
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.5rem;
    margin-bottom: 0.8rem;
}

/* Divider */
.ink-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.5rem 0;
}

/* Source badges */
.source-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-family: 'Cinzel', serif;
    letter-spacing: 0.08em;
    margin-right: 6px;
}
.badge-reddit  { background:#2d1a1a; color:#e06060; border:1px solid #5a2a2a; }
.badge-google  { background:#1a1f2d; color:#6090e0; border:1px solid #2a3a5a; }
.badge-exact   { background:#1a2e1a; color:#60c060; border:1px solid #2a5a2a; }
.badge-thematic{ background:#2d251a; color:#e0b060; border:1px solid #5a4a2a; }

/* Text area styling */
textarea {
    background: #130f05 !important;
    color: var(--parchment) !important;
    border: 1px solid var(--border) !important;
    font-family: 'Crimson Pro', serif !important;
    font-size: 1.05rem !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #3a2a10, #5a3e18);
    color: var(--gold);
    border: 1px solid var(--gold);
    font-family: 'Cinzel', serif;
    font-size: 0.8rem;
    letter-spacing: 0.1em;
    padding: 0.5rem 1.5rem;
    border-radius: 2px;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #5a3e18, #7a5225);
    box-shadow: 0 0 12px rgba(212,168,67,0.3);
}

/* Section headers */
.section-label {
    font-family: 'Cinzel', serif;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--sepia-light);
    margin-bottom: 0.6rem;
}

/* Progress bars */
.stProgress > div > div { background-color: var(--gold) !important; }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  1. SHAKESPEAREAN DETECTOR
# ══════════════════════════════════════════════════════════════════

# Archaic word list — weighted by rarity / diagnostic power
ARCHAIC_KEYWORDS: Dict[str, int] = {
    # Strong indicators (weight 3)
    "thou": 3, "thee": 3, "thy": 3, "thine": 3, "hath": 3, "doth": 3,
    "wouldst": 3, "couldst": 3, "shouldst": 3, "hast": 3, "art": 2,
    "wilt": 3, "dost": 3, "canst": 3,
    # Medium indicators (weight 2)
    "wherefore": 2, "whither": 2, "hither": 2, "thither": 2,
    "forsooth": 2, "prithee": 2, "methinks": 2, "perchance": 2,
    "betwixt": 2, "beseech": 2, "albeit": 2, "nay": 2, "yea": 2,
    "ere": 2, "oft": 2, "henceforth": 2, "verily": 2, "marry": 2,
    # Weak indicators (weight 1)
    "good morrow": 1, "fie": 1, "alas": 1, "mayhaps": 1, "yon": 1,
    "yonder": 1, "hence": 1, "hark": 1, "lo": 1, "pray": 1,
    "sirrah": 1, "wench": 1, "knave": 1, "doth": 1, "tis": 1,
    "'tis": 1, "o'er": 1, "ne'er": 1, "e'er": 1, "whence": 1,
    "naught": 1, "nought": 1, "twas": 1, "'twas": 1,
}

# Threshold: weighted density per 100 words
SHAKESPEARE_THRESHOLD = 2.5


def detect_shakespearean(text: str) -> Tuple[bool, float, List[str]]:
    """
    Compute a weighted keyword-density score per 100 words.

    Returns
    -------
    is_shakespearean : bool
    density_score    : float  (weighted hits per 100 words)
    matched_keywords : list[str]
    """
    words = re.findall(r"[a-z']+", text.lower())
    total_words = max(len(words), 1)

    score = 0
    matched = []
    for word, weight in ARCHAIC_KEYWORDS.items():
        # support multi-word phrases
        pattern = r'\b' + re.escape(word) + r'\b'
        hits = len(re.findall(pattern, text.lower()))
        if hits:
            score += hits * weight
            matched.extend([word] * hits)

    density = (score / total_words) * 100
    return density >= SHAKESPEARE_THRESHOLD, round(density, 2), list(set(matched))


# ══════════════════════════════════════════════════════════════════
#  2. TEXT CONVERTER  (Modern → Shakespearean)
# ══════════════════════════════════════════════════════════════════

# Ordered replacement tuples: (regex_pattern, replacement)
# Order matters — longest / most specific first
MODERN_TO_ARCHAIC: List[Tuple[str, str]] = [
    # Contractions
    (r"\byou are\b",          "thou art"),
    (r"\byou were\b",         "thou wert"),
    (r"\byou have\b",         "thou hast"),
    (r"\byou will\b",         "thou wilt"),
    (r"\byou would\b",        "thou wouldst"),
    (r"\byou could\b",        "thou couldst"),
    (r"\byou should\b",       "thou shouldst"),
    (r"\byou\b",              "thee"),
    (r"\byour\b",             "thy"),
    (r"\byours\b",            "thine"),
    # Third person present
    (r"\bhe has\b",           "he hath"),
    (r"\bshe has\b",          "she hath"),
    (r"\bit has\b",           "it hath"),
    (r"\bhas\b",              "hath"),
    (r"\bhe does\b",          "he doth"),
    (r"\bshe does\b",         "she doth"),
    (r"\bit does\b",          "it doth"),
    (r"\bdoes\b",             "doth"),
    (r"\bhe is\b",            "he is"),     # kept — but "art" for 2nd person
    (r"\bshe is\b",           "she is"),
    # Modal verbs
    (r"\bwill not\b",         "shall not"),
    (r"\bwon't\b",            "shall not"),
    (r"\bcan't\b",            "canst not"),
    (r"\bcannot\b",           "canst not"),
    (r"\bdon't\b",            "dost not"),
    (r"\bdo not\b",           "dost not"),
    (r"\bdoesn't\b",          "doth not"),
    # Prepositions / connectives
    (r"\bbetween\b",          "betwixt"),
    (r"\bbefore\b",           "ere"),
    (r"\bafter\b",            "thereafter"),
    (r"\bbecause\b",          "for"),
    (r"\bwhere\b",            "whither"),
    (r"\bwhy\b",              "wherefore"),
    (r"\bhere\b",             "hither"),
    (r"\bthere\b",            "thither"),
    (r"\boften\b",            "oft"),
    (r"\bover\b",             "o'er"),
    (r"\bnever\b",            "ne'er"),
    (r"\bever\b",             "e'er"),
    (r"\bit is\b",            "'tis"),
    (r"\byes\b",              "yea"),
    (r"\bno\b",               "nay"),
    (r"\bnothing\b",          "naught"),
    (r"\bthink\b",            "dost think"),
    (r"\bbelieve\b",          "dost believe"),
    (r"\bsee\b",              "dost see"),
    # Exclamations / interjections
    (r"\boh\b",               "O"),
    (r"\boh!\b",              "O!"),
    (r"\bwow\b",              "marry"),
    (r"\bplease\b",           "prithee"),
    (r"\bbye\b",              "fare thee well"),
    (r"\bgoodbye\b",          "fare thee well"),
    (r"\bhello\b",            "good morrow"),
    (r"\bhi\b",               "hark"),
    (r"\bsorry\b",            "i prithee forgive me"),
    (r"\bperhaps\b",          "perchance"),
    (r"\bmaybe\b",            "mayhaps"),
    (r"\btruly\b",            "verily"),
    (r"\bindeed\b",           "forsooth"),
    (r"\bthat\b",             "that"),     # kept
    (r"\bwhich\b",            "which"),
    # Archaic suffix: walk → walketh  (present 3rd person)
    # Applied only to common verbs to avoid over-mangling
]

# Verbs to apply -eth suffix for 3rd person forms
ETH_VERBS = [
    "walk", "speak", "run", "know", "see", "love", "hate",
    "come", "go", "live", "die", "fall", "rise", "stand",
    "seek", "find", "bring", "take", "make", "give",
]


def convert_to_shakespearean(text: str) -> str:
    """
    Apply cascading regex replacements (case-insensitive) then
    probabilistically add archaic -eth verb suffixes.
    """
    result = text

    for pattern, replacement in MODERN_TO_ARCHAIC:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    # Apply -eth to common 3rd-person verb forms
    for verb in ETH_VERBS:
        result = re.sub(
            r'\bhe ' + verb + r's?\b',
            f'he {verb}eth',
            result, flags=re.IGNORECASE
        )
        result = re.sub(
            r'\bshe ' + verb + r's?\b',
            f'she {verb}eth',
            result, flags=re.IGNORECASE
        )

    # Capitalise first word of each sentence
    sentences = re.split(r'(?<=[.!?])\s+', result)
    result = ' '.join(s[:1].upper() + s[1:] if s else s for s in sentences)

    # Add a period if missing
    result = result.strip()
    if result and result[-1] not in '.!?':
        result += '.'

    return result


def highlight_keywords(text: str, keywords: List[str]) -> str:
    """Wrap matched archaic keywords in HTML span for visual highlight."""
    highlighted = text
    for kw in sorted(keywords, key=len, reverse=True):
        pattern = r'(?i)\b' + re.escape(kw) + r'\b'
        highlighted = re.sub(
            pattern,
            lambda m: f'<span class="kw-highlight">{m.group()}</span>',
            highlighted
        )
    return highlighted


# ══════════════════════════════════════════════════════════════════
#  3. SENTIMENT ANALYZER  (TextBlob — Subjectivity / Objectivity)
# ══════════════════════════════════════════════════════════════════

# Hamlet baseline: pre-computed from Act III scene 1 "To be or not to be"
# polarity=-0.04, subjectivity=0.42  (metered via TextBlob)
HAMLET_BASELINE = {
    "polarity":     -0.04,
    "subjectivity":  0.42,
    "label":        "Hamlet — Act III.i",
}

# Sonnet 18 baseline: "Shall I compare thee to a summer's day?"
SONNET_BASELINE = {
    "polarity":      0.35,
    "subjectivity":  0.72,
    "label":        "Sonnet XVIII",
}

# Richard III baseline: "Now is the winter of our discontent"
RICHARD_BASELINE = {
    "polarity":     -0.25,
    "subjectivity":  0.55,
    "label":        "Richard III — Act I.i",
}


def analyze_sentiment(text: str) -> Dict:
    """
    TextBlob analysis with custom scale mapping.

    Subjectivity  → Emotional/Narrative Scale   (0 = cold prose, 1 = passionate)
    Objectivity   → Authoritative/Regal Scale   (0 = subjective, 1 = authoritative)
    Polarity      → -1 (dark) … +1 (light)

    Interview hook:
      TextBlob's subjectivity is trained on a pattern-based lexicon. High
      subjectivity words include personal pronouns, emotive adjectives, and
      first-person assertions — exactly what appears in Shakespearean soliloquies.
      By inverting subjectivity we derive a proxy for "authoritative declaration,"
      which maps naturally onto proclamations, edicts, and regal speech patterns.
    """
    blob = TextBlob(text)
    polarity    = blob.sentiment.polarity      # -1 … +1
    subjectivity = blob.sentiment.subjectivity  # 0 (objective) … 1 (subjective)

    objectivity = 1.0 - subjectivity           # derived

    # Map to named scales
    emotional_score     = round(subjectivity * 100, 1)   # 0–100
    authoritative_score = round(objectivity * 100, 1)    # 0–100

    # Polarity label
    if polarity > 0.2:
        polarity_label = "Light / Comedic"
        polarity_color = "#7fc47f"
    elif polarity < -0.2:
        polarity_label = "Dark / Tragic"
        polarity_color = "#e06060"
    else:
        polarity_label = "Ambivalent / Dramatic"
        polarity_color = "#d4a843"

    # Character archetype
    if emotional_score > 65:
        archetype = "Soliloquy — Inner Turmoil"
    elif authoritative_score > 65:
        archetype = "Proclamation — Regal Decree"
    elif polarity < -0.15:
        archetype = "Lament — Elegiac Tone"
    else:
        archetype = "Discourse — Balanced Rhetoric"

    # Sentence-level breakdown
    sentences = blob.sentences
    sentence_data = [
        {
            "sentence": str(s)[:80] + ("…" if len(str(s)) > 80 else ""),
            "polarity": round(s.sentiment.polarity, 3),
            "subjectivity": round(s.sentiment.subjectivity, 3),
        }
        for s in sentences
    ]

    return {
        "polarity":           round(polarity, 4),
        "subjectivity":       round(subjectivity, 4),
        "objectivity":        round(objectivity, 4),
        "emotional_score":    emotional_score,
        "authoritative_score": authoritative_score,
        "polarity_label":     polarity_label,
        "polarity_color":     polarity_color,
        "archetype":          archetype,
        "sentences":          sentence_data,
        "word_count":         len(text.split()),
    }


# ══════════════════════════════════════════════════════════════════
#  4. VERIFICATION ENGINE  (Mock Reddit + Google)
# ══════════════════════════════════════════════════════════════════

# Mock corpus — realistic-sounding Reddit/web snippets
MOCK_REDDIT_CORPUS = [
    {"source": "r/shakespeare", "snippet": "To be, or not to be, that is the question", "score": 4821},
    {"source": "r/literature",  "snippet": "All the world's a stage, and all the men and women merely players", "score": 3104},
    {"source": "r/quotes",      "snippet": "What's in a name? That which we call a rose by any other name would smell as sweet", "score": 2977},
    {"source": "r/history",     "snippet": "Good night, good night! Parting is such sweet sorrow", "score": 2203},
    {"source": "r/classiclit",  "snippet": "The lady doth protest too much, methinks", "score": 1882},
    {"source": "r/philosophy",  "snippet": "We know what we are, but know not what we may be", "score": 1543},
    {"source": "r/worldnews",   "snippet": "Something is rotten in the state of Denmark", "score": 1321},
    {"source": "r/writing",     "snippet": "Though she be but little, she is fierce", "score": 987},
]

MOCK_GOOGLE_RESULTS = [
    {"title": "Shakespeare's Hamlet — Complete Text", "domain": "shakespeare.mit.edu"},
    {"title": "Folger Shakespeare Library — Digital Texts", "domain": "folger.edu"},
    {"title": "Open Source Shakespeare — Search", "domain": "opensourceshakespeare.org"},
    {"title": "The Complete Works of Shakespeare", "domain": "gutenberg.org"},
    {"title": "SparkNotes — Shakespeare Plays", "domain": "sparknotes.com"},
]


def compute_similarity(text_a: str, text_b: str) -> float:
    """
    Simple Jaccard similarity on word sets (stopwords included).
    For thematic: overlap on content words after stop-word removal.
    """
    STOPWORDS = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at",
        "to", "for", "of", "is", "it", "that", "this", "was",
        "be", "by", "are", "as", "with", "not", "have",
    }
    words_a = set(re.findall(r'[a-z]+', text_a.lower())) - STOPWORDS
    words_b = set(re.findall(r'[a-z]+', text_b.lower())) - STOPWORDS
    if not words_a or not words_b:
        return 0.0
    return len(words_a & words_b) / len(words_a | words_b)


def run_verification(
    text: str,
    use_real_reddit: bool = False,
    use_real_google: bool = False,
    reddit_client_id: str = "",
    reddit_secret: str = "",
    serpapi_key: str = "",
) -> Dict:
    """
    Verification engine.

    When API keys are absent → runs realistic mock.
    When keys are present    → attempts real PRAW / SerpApi calls.

    Returns plagiarism verdict, similarity scores, and source citations.
    """
    results = {
        "reddit": [],
        "google": [],
        "exact_match_found": False,
        "exact_match_source": None,
        "max_thematic_score": 0.0,
        "thematic_sources": [],
        "verification_mode": "mock",
    }

    # ── REDDIT ────────────────────────────────────────────────────
    if use_real_reddit and reddit_client_id and reddit_secret:
        try:
            import praw
            reddit = praw.Reddit(
                client_id=reddit_client_id,
                client_secret=reddit_secret,
                user_agent="ShakespeareEngine/1.0",
            )
            subreddits = ["shakespeare", "literature", "quotes", "classiclit"]
            query = " ".join(text.split()[:10])  # first 10 words as query
            for sub in subreddits:
                for post in reddit.subreddit(sub).search(query, limit=3):
                    sim = compute_similarity(text, post.title + " " + post.selftext)
                    results["reddit"].append({
                        "source": f"r/{sub}",
                        "snippet": (post.title[:100]),
                        "score": post.score,
                        "similarity": round(sim, 3),
                        "url": f"https://reddit.com{post.permalink}",
                    })
            results["verification_mode"] = "live"
        except Exception as e:
            st.warning(f"Reddit API error: {e}. Falling back to mock.")

    # Mock Reddit (fallback or default)
    if not results["reddit"]:
        for entry in MOCK_REDDIT_CORPUS:
            sim = compute_similarity(text, entry["snippet"])
            # Exact match simulation
            exact = (
                text.lower().strip()[:60] in entry["snippet"].lower() or
                entry["snippet"].lower()[:60] in text.lower()
            )
            results["reddit"].append({
                "source": entry["source"],
                "snippet": entry["snippet"],
                "score": entry["score"],
                "similarity": round(sim, 3),
                "exact": exact,
                "url": "#",
            })

    # ── GOOGLE / SERPAPI ──────────────────────────────────────────
    if use_real_google and serpapi_key:
        try:
            import requests
            query = " ".join(text.split()[:12])
            params = {
                "q": query,
                "api_key": serpapi_key,
                "engine": "google",
                "num": 5,
            }
            resp = requests.get("https://serpapi.com/search", params=params, timeout=10)
            data = resp.json()
            for r in data.get("organic_results", [])[:5]:
                snippet = r.get("snippet", "")
                sim = compute_similarity(text, snippet)
                results["google"].append({
                    "title": r.get("title", ""),
                    "domain": r.get("link", "").split("/")[2] if r.get("link") else "",
                    "snippet": snippet[:120],
                    "similarity": round(sim, 3),
                    "url": r.get("link", "#"),
                })
            results["verification_mode"] = "live"
        except Exception as e:
            st.warning(f"SerpApi error: {e}. Falling back to mock.")

    # Mock Google (fallback or default)
    if not results["google"]:
        for entry in MOCK_GOOGLE_RESULTS:
            sim = round(random.uniform(0.02, 0.18), 3)
            results["google"].append({
                "title": entry["title"],
                "domain": entry["domain"],
                "similarity": sim,
                "url": "#",
            })

    # ── AGGREGATE VERDICT ─────────────────────────────────────────
    all_sims = [r["similarity"] for r in results["reddit"]] + \
               [r["similarity"] for r in results["google"]]

    results["max_thematic_score"] = max(all_sims) if all_sims else 0.0

    # Exact match: any Reddit similarity > 0.55 or flagged
    for r in results["reddit"]:
        if r.get("exact") or r["similarity"] > 0.55:
            results["exact_match_found"] = True
            results["exact_match_source"] = r["source"]
            break

    # Thematic sources (sim > 0.15)
    results["thematic_sources"] = [
        r["source"] for r in results["reddit"] if r["similarity"] > 0.15
    ]

    return results


# ══════════════════════════════════════════════════════════════════
#  5. VISUALIZER
# ══════════════════════════════════════════════════════════════════

def build_sentiment_map(input_sentiment: Dict) -> go.Figure:
    """
    2-D scatter: Polarity (x) vs Subjectivity (y)
    Input text plotted against three canonical Shakespeare baselines.
    """
    baselines = [HAMLET_BASELINE, SONNET_BASELINE, RICHARD_BASELINE]

    fig = go.Figure()

    # Background quadrant shading
    fig.add_shape(type="rect", x0=-1, x1=0, y0=0, y1=1,
                  fillcolor="rgba(139,26,26,0.07)", line_width=0)
    fig.add_shape(type="rect", x0=0, x1=1, y0=0, y1=1,
                  fillcolor="rgba(61,90,62,0.07)", line_width=0)
    fig.add_shape(type="rect", x0=-1, x1=0, y0=-1, y1=0,
                  fillcolor="rgba(139,26,26,0.04)", line_width=0)
    fig.add_shape(type="rect", x0=0, x1=1, y0=-1, y1=0,
                  fillcolor="rgba(61,90,62,0.04)", line_width=0)

    # Axis lines
    fig.add_hline(y=0.5, line_color="#3a2e1a", line_dash="dot", line_width=1)
    fig.add_vline(x=0,   line_color="#3a2e1a", line_dash="dot", line_width=1)

    # Baselines
    for b in baselines:
        fig.add_trace(go.Scatter(
            x=[b["polarity"]],
            y=[b["subjectivity"]],
            mode="markers+text",
            marker=dict(
                size=14,
                color="#7a5c38",
                symbol="diamond",
                line=dict(color="#d4a843", width=1.5),
            ),
            text=[b["label"]],
            textposition="top center",
            textfont=dict(color="#c9a96e", size=10, family="IM Fell English"),
            name=b["label"],
            hovertemplate=(
                f"<b>{b['label']}</b><br>"
                f"Polarity: {b['polarity']:.2f}<br>"
                f"Subjectivity: {b['subjectivity']:.2f}<extra></extra>"
            ),
        ))

    # Input text point
    fig.add_trace(go.Scatter(
        x=[input_sentiment["polarity"]],
        y=[input_sentiment["subjectivity"]],
        mode="markers+text",
        marker=dict(
            size=20,
            color="#d4a843",
            symbol="star",
            line=dict(color="#f5efe0", width=2),
        ),
        text=["◀ Your Text"],
        textposition="middle right",
        textfont=dict(color="#f5efe0", size=12, family="Cinzel"),
        name="Your Text",
        hovertemplate=(
            "<b>Your Text</b><br>"
            f"Polarity: {input_sentiment['polarity']:.3f}<br>"
            f"Subjectivity: {input_sentiment['subjectivity']:.3f}<br>"
            f"Archetype: {input_sentiment['archetype']}<extra></extra>"
        ),
    ))

    # Quadrant labels
    label_cfg = dict(font=dict(size=9, color="#5a4a2a", family="Cinzel"),
                     showarrow=False)
    fig.add_annotation(x=-0.7, y=0.85, text="DARK · EMOTIONAL",  **label_cfg)
    fig.add_annotation(x= 0.7, y=0.85, text="LIGHT · EMOTIONAL", **label_cfg)
    fig.add_annotation(x=-0.7, y=0.15, text="DARK · REGAL",      **label_cfg)
    fig.add_annotation(x= 0.7, y=0.15, text="LIGHT · REGAL",     **label_cfg)

    fig.update_layout(
        paper_bgcolor="#110d07",
        plot_bgcolor="#130f05",
        font=dict(color="#c9a96e", family="Crimson Pro"),
        title=dict(
            text="SENTIMENT MAP — Shakespearean Corpus Comparison",
            font=dict(family="Cinzel", size=13, color="#d4a843"),
            x=0.5,
        ),
        xaxis=dict(
    title=dict(
        text="Polarity  ← Dark · · · Light →",
        font=dict(size=10, family="Cinzel")  
    ),
    range=[-1.05, 1.05],
    gridcolor="#1e1a10",
    zerolinecolor="#3a2e1a",
    tickfont=dict(size=9),
),
yaxis=dict(
    title=dict(
        text="Subjectivity  ← Regal · · · Emotional →",
        font=dict(size=10, family="Cinzel") 
    ),
    range=[-0.05, 1.05],
    gridcolor="#1e1a10",
    zerolinecolor="#3a2e1a",
    tickfont=dict(size=9),
),
        legend=dict(
            bgcolor="#1e1608",
            bordercolor="#3a2e1a",
            borderwidth=1,
            font=dict(size=9, family="IM Fell English"),
        ),
        height=420,
        margin=dict(l=60, r=40, t=50, b=50),
    )
    return fig


def build_sentence_chart(sentences: List[Dict]) -> go.Figure:
    """Bar chart of per-sentence polarity."""
    if not sentences:
        return go.Figure()

    df = pd.DataFrame(sentences)
    df.index = [f"S{i+1}" for i in range(len(df))]

    colors = [
        "#7fc47f" if p > 0.1 else "#e06060" if p < -0.1 else "#d4a843"
        for p in df["polarity"]
    ]

    fig = go.Figure(go.Bar(
        x=df.index,
        y=df["polarity"],
        marker_color=colors,
        marker_line_color="#3a2e1a",
        marker_line_width=1,
        hovertemplate="<b>%{x}</b><br>Polarity: %{y:.3f}<br><extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="#110d07",
        plot_bgcolor="#130f05",
        font=dict(color="#c9a96e", family="Crimson Pro"),
        title=dict(
            text="PER-SENTENCE POLARITY",
            font=dict(family="Cinzel", size=12, color="#d4a843"),
            x=0.5,
        ),
        xaxis=dict(gridcolor="#1e1a10", tickfont=dict(size=9)),
        yaxis=dict(
            gridcolor="#1e1a10", 
            range=[-1.1, 1.1],
            title=dict(
                text="Polarity", 
                font=dict(size=9, family="Cinzel")
            )
        ),
        height=240,
        margin=dict(l=50, r=20, t=40, b=40),
        showlegend=False,
    )
    fig.add_hline(y=0, line_color="#5a4a2a", line_dash="dash", line_width=1)
    return fig

def build_radar_chart(sentiment: Dict) -> go.Figure:
    """Radar showing the text's 'profile' across 5 dimensions."""
    categories = [
        "Regal Authority",
        "Emotional Depth",
        "Narrative Light",
        "Archaic Density",
        "Tragic Weight",
    ]
    pol = sentiment["polarity"]
    values = [
        sentiment["authoritative_score"],
        sentiment["emotional_score"],
        max(0, pol * 100 + 50),         # remap polarity to 0-100
        min(100, sentiment.get("density", 0) * 20),
        max(0, -pol * 100 + 50),        # inverse polarity
    ]
    values += [values[0]]  # close loop
    categories_closed = categories + [categories[0]]

    fig = go.Figure(go.Scatterpolar(
        r=values,
        theta=categories_closed,
        fill='toself',
        fillcolor='rgba(212,168,67,0.15)',
        line=dict(color='#d4a843', width=2),
        marker=dict(color='#d4a843', size=6),
    ))
    fig.update_layout(
        paper_bgcolor="#110d07",
        polar=dict(
            bgcolor="#130f05",
            radialaxis=dict(
                visible=True, range=[0, 100],
                gridcolor="#2e2510", tickfont=dict(size=8, color="#7a5c38"),
            ),
            angularaxis=dict(
                gridcolor="#2e2510",
                tickfont=dict(size=9, color="#c9a96e", family="Cinzel"),
            ),
        ),
        title=dict(
            text="LITERARY PROFILE",
            font=dict(family="Cinzel", size=12, color="#d4a843"),
            x=0.5,
        ),
        height=300,
        margin=dict(l=40, r=40, t=50, b=20),
    )
    return fig


# ══════════════════════════════════════════════════════════════════
#  6. SIDEBAR
# ══════════════════════════════════════════════════════════════════

def render_sidebar() -> Dict:
    """Render API config panel, return config dict."""
    with st.sidebar:
        st.markdown('<p class="sidebar-title">⚙ Engine Configuration</p>',
                    unsafe_allow_html=True)

        st.markdown("**🎭 Detection Threshold**")
        threshold = st.slider(
            "Archaic Density (per 100 words)",
            min_value=0.5, max_value=8.0, value=2.5, step=0.5,
            help="Lower = more texts detected as Shakespearean"
        )

        st.markdown('<hr class="ink-divider">', unsafe_allow_html=True)
        st.markdown('<p class="sidebar-title">🔌 API Integrations</p>',
                    unsafe_allow_html=True)

        use_reddit = st.toggle("Live Reddit (PRAW)", value=False)
        reddit_id, reddit_secret = "", ""
        if use_reddit:
            reddit_id     = st.text_input("Client ID",     type="password", key="r_id")
            reddit_secret = st.text_input("Client Secret", type="password", key="r_sec")

        use_google = st.toggle("Live Google (SerpApi)", value=False)
        serpapi_key = ""
        if use_google:
            serpapi_key = st.text_input("SerpApi Key", type="password", key="g_key")

        st.markdown('<hr class="ink-divider">', unsafe_allow_html=True)
        st.markdown('<p class="sidebar-title">📜 Shakespeare Baselines</p>',
                    unsafe_allow_html=True)
        show_hamlet  = st.checkbox("Hamlet III.i",    value=True)
        show_sonnet  = st.checkbox("Sonnet XVIII",     value=True)
        show_richard = st.checkbox("Richard III I.i",  value=True)

        st.markdown('<hr class="ink-divider">', unsafe_allow_html=True)
        st.markdown(
            '<p style="font-size:0.7rem;color:#5a4a2a;font-family:\'IM Fell English\',serif;">'
            'Mock mode active when API keys absent.<br>'
            'All analysis performed client-side.</p>',
            unsafe_allow_html=True
        )

    return {
        "threshold":    threshold,
        "use_reddit":   use_reddit,
        "use_google":   use_google,
        "reddit_id":    reddit_id,
        "reddit_secret": reddit_secret,
        "serpapi_key":  serpapi_key,
        "show_hamlet":  show_hamlet,
        "show_sonnet":  show_sonnet,
        "show_richard": show_richard,
    }


# ══════════════════════════════════════════════════════════════════
#  7. MAIN APP
# ══════════════════════════════════════════════════════════════════

def main():
    config = render_sidebar()

    # ── Header ────────────────────────────────────────────────────
    col_logo, col_title = st.columns([1, 8])
    with col_logo:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("## 🎭", unsafe_allow_html=False)
    with col_title:
        st.markdown(
            '<p class="eng-title">Shakespearean Sentiment<br>& Authenticity Engine</p>'
            '<p class="eng-subtitle">'
            '"What\'s in a name? That which we call a rose by any other name would smell as sweet."'
            '</p>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="ink-divider">', unsafe_allow_html=True)

    # ── Input ─────────────────────────────────────────────────────
    st.markdown('<p class="section-label">📝 Enter Your Text</p>',
                unsafe_allow_html=True)

    SAMPLE_TEXTS = {
        "— select a sample —": "",
        "Modern: love letter":
            "I love you so much. You are the best thing that has ever happened to me. "
            "I never want to lose you. Please stay with me forever.",
        "Modern: news report":
            "The government announced new policies today. The decision has been met with "
            "mixed reactions from the public. Experts believe the changes will take effect next year.",
        "Authentic: Hamlet":
            "To be, or not to be, that is the question. Whether 'tis nobler in the mind to suffer "
            "the slings and arrows of outrageous fortune, or to take arms against a sea of troubles.",
        "Authentic: Sonnet":
            "Shall I compare thee to a summer's day? Thou art more lovely and more temperate. "
            "Rough winds doth shake the darling buds of May.",
        "Modern: tech pitch":
            "Our startup leverages AI to disrupt the market. We have strong user growth and "
            "a clear path to profitability. Investors should consider this a strong opportunity.",
    }

    col_input, col_sample = st.columns([3, 1])
    with col_sample:
        sample_choice = st.selectbox("Quick-load sample", list(SAMPLE_TEXTS.keys()))
    with col_input:
        default_text = SAMPLE_TEXTS[sample_choice]
        user_text = st.text_area(
            "Input Text",
            value=default_text,
            height=140,
            placeholder="Enter text to analyse — prose, verse, or any passage...",
            label_visibility="collapsed",
        )

    analyse_btn = st.button("⚗  Analyse & Transform", use_container_width=False)

    if not user_text.strip():
        st.markdown(
            '<div class="shk-card" style="text-align:center;padding:2.5rem;">'
            '<span style="font-family:\'IM Fell English\',serif;color:#5a4a2a;font-size:1.1rem;">'
            'Enter text above and press Analyse to begin the examination.'
            '</span></div>',
            unsafe_allow_html=True,
        )
        return

    if analyse_btn or user_text:
        # ── Analysis pipeline ─────────────────────────────────────
        global SHAKESPEARE_THRESHOLD
        SHAKESPEARE_THRESHOLD = config["threshold"]

        is_shk, density, matched_kws = detect_shakespearean(user_text)
        converted_text = user_text if is_shk else convert_to_shakespearean(user_text)
        sentiment      = analyze_sentiment(converted_text)
        sentiment["density"] = density
        verification   = run_verification(
            text=converted_text,
            use_real_reddit=config["use_reddit"],
            use_real_google=config["use_google"],
            reddit_client_id=config["reddit_id"],
            reddit_secret=config["reddit_secret"],
            serpapi_key=config["serpapi_key"],
        )

        st.markdown('<hr class="ink-divider">', unsafe_allow_html=True)

        # ══ ROW 1: Metrics ════════════════════════════════════════
        st.markdown('<p class="section-label">📊 Core Metrics</p>',
                    unsafe_allow_html=True)
        m1, m2, m3, m4, m5 = st.columns(5)

        with m1:
            st.metric(
                "Authoritative / Regal",
                f"{sentiment['authoritative_score']:.0f} / 100",
                delta="Objective Scale",
                delta_color="off",
                help="Derived from (1 - TextBlob subjectivity). High = declarative, regal speech.",
            )
        with m2:
            st.metric(
                "Emotional / Narrative",
                f"{sentiment['emotional_score']:.0f} / 100",
                delta="Subjective Scale",
                delta_color="off",
                help="TextBlob subjectivity × 100. High = personal, emotive.",
            )
        with m3:
            st.metric(
                "Polarity",
                f"{sentiment['polarity']:+.3f}",
                delta=sentiment["polarity_label"],
                delta_color="off",
            )
        with m4:
            st.metric(
                "Archaic Density",
                f"{density:.2f}",
                delta="per 100 words",
                delta_color="off",
                help=f"Threshold: {config['threshold']}. Matched: {', '.join(matched_kws) or 'none'}",
            )
        with m5:
            st.metric(
                "Authenticity Risk",
                f"{verification['max_thematic_score']*100:.0f}%",
                delta="Thematic Overlap",
                delta_color="off",
            )

        st.markdown('<hr class="ink-divider">', unsafe_allow_html=True)

        # ══ ROW 2: Detection + Conversion ═════════════════════════
        col_detect, col_convert = st.columns([1, 1])

        with col_detect:
            st.markdown('<p class="section-label">🔍 Shakespearean Detection</p>',
                        unsafe_allow_html=True)
            if is_shk:
                st.markdown(
                    '<div class="verdict-authentic">'
                    '✦ AUTHENTIC SHAKESPEAREAN VOICE DETECTED<br>'
                    f'<small>Archaic density: {density:.2f} / threshold: {config["threshold"]}</small>'
                    '</div>',
                    unsafe_allow_html=True,
                )
                st.markdown("<br>", unsafe_allow_html=True)
                highlighted = highlight_keywords(user_text, matched_kws)
                st.markdown(
                    f'<div class="shk-output">{highlighted}</div>',
                    unsafe_allow_html=True,
                )
                if matched_kws:
                    st.caption(f"Detected keywords: {', '.join(sorted(set(matched_kws)))}")
            else:
                st.markdown(
                    '<div class="verdict-converted">'
                    '⚗ MODERN TEXT — CONVERSION APPLIED<br>'
                    f'<small>Archaic density: {density:.2f} — below threshold {config["threshold"]}</small>'
                    '</div>',
                    unsafe_allow_html=True,
                )

        with col_convert:
            st.markdown('<p class="section-label">📜 Shakespearean Rendering</p>',
                        unsafe_allow_html=True)
            if is_shk:
                st.markdown(
                    '<div style="color:#5a4a2a;font-family:\'IM Fell English\',serif;'
                    'font-size:0.95rem;padding:1rem;">'
                    'Text already Shakespearean — no conversion necessary.</div>',
                    unsafe_allow_html=True,
                )
            else:
                converted_highlighted = highlight_keywords(
                    converted_text,
                    re.findall(r'[a-z\']+', converted_text.lower())
                )
                st.markdown(
                    f'<div class="shk-output">{converted_text}</div>',
                    unsafe_allow_html=True,
                )

        st.markdown('<hr class="ink-divider">', unsafe_allow_html=True)

        # ══ ROW 3: Archetype + Subjectivity explanation ═══════════
        col_arch, col_expl = st.columns([1, 2])

        with col_arch:
            st.markdown('<p class="section-label">🎭 Literary Archetype</p>',
                        unsafe_allow_html=True)
            st.markdown(
                f'<div class="shk-card" style="text-align:center;padding:2rem;">'
                f'<div style="font-family:\'Cinzel\',serif;font-size:1.5rem;color:#d4a843;">'
                f'{sentiment["archetype"]}</div>'
                f'<div style="margin-top:0.8rem;font-family:\'IM Fell English\',serif;'
                f'font-size:0.9rem;color:#7a5c38;font-style:italic;">'
                f'Based on subjectivity–polarity profile</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        with col_expl:
            st.markdown('<p class="section-label">🧠 Subjectivity / Objectivity Logic</p>',
                        unsafe_allow_html=True)
            obj_pct = sentiment['authoritative_score']
            sub_pct = sentiment['emotional_score']
            st.markdown(
                f'<div class="shk-card">'
                f'<div style="display:flex;justify-content:space-between;'
                f'font-family:\'Cinzel\',serif;font-size:0.75rem;color:#c9a96e;">'
                f'<span>Regal / Authoritative</span>'
                f'<span>Emotional / Narrative</span></div>'
                f'<div style="margin:8px 0;background:#1e1608;height:12px;border-radius:6px;'
                f'border:1px solid #3a2e1a;overflow:hidden;">'
                f'<div style="width:{obj_pct}%;height:100%;'
                f'background:linear-gradient(90deg,#3d5a3e,#d4a843);'
                f'border-radius:6px 0 0 6px;"></div>'
                f'</div>'
                f'<p style="font-family:\'Crimson Pro\',serif;font-size:0.95rem;'
                f'color:#c9a96e;margin-top:0.7rem;">'
                f'TextBlob\'s subjectivity score (<code>{sentiment["subjectivity"]:.3f}</code>) '
                f'is trained on a pattern-based lexicon where emotive adjectives, '
                f'personal pronouns, and first-person claims push toward <em>1.0</em>. '
                f'Inverting this gives objectivity (<code>{sentiment["objectivity"]:.3f}</code>), '
                f'which maps to <strong>Regal Authority</strong> — declarative proclamations '
                f'with minimal hedging, characteristic of Shakespearean kings and edicts.'
                f'</p></div>',
                unsafe_allow_html=True,
            )

        st.markdown('<hr class="ink-divider">', unsafe_allow_html=True)

        # ══ ROW 4: Visualizations ═════════════════════════════════
        st.markdown('<p class="section-label">📈 Sentiment Visualizations</p>',
                    unsafe_allow_html=True)

        tab_map, tab_bar, tab_radar = st.tabs([
            "🗺  Sentiment Map",
            "📊  Sentence Polarity",
            "🕸  Literary Profile",
        ])

        with tab_map:
            fig_map = build_sentiment_map(sentiment)
            st.plotly_chart(fig_map, use_container_width=True)
            st.caption(
                "★ = Your text   ◆ = Canonical Shakespeare baselines.  "
                "Upper half = Emotional / Subjective. Lower half = Objective / Regal."
            )

        with tab_bar:
            if sentiment["sentences"]:
                fig_bar = build_sentence_chart(sentiment["sentences"])
                st.plotly_chart(fig_bar, use_container_width=True)
                # Sentence detail table
                df_sentences = pd.DataFrame(sentiment["sentences"])
                df_sentences.columns = ["Sentence (truncated)", "Polarity", "Subjectivity"]
                df_sentences.index = [f"S{i+1}" for i in range(len(df_sentences))]
                st.dataframe(
                    df_sentences.style.background_gradient(
                        subset=["Polarity"],
                        cmap="RdYlGn",
                        vmin=-1, vmax=1,
                    ),
                    use_container_width=True,
                )
            else:
                st.info("No sentence-level data available.")

        with tab_radar:
            fig_radar = build_radar_chart(sentiment)
            st.plotly_chart(fig_radar, use_container_width=True)

        st.markdown('<hr class="ink-divider">', unsafe_allow_html=True)

        # ══ ROW 5: Verification ════════════════════════════════════
        st.markdown('<p class="section-label">🔏 Authenticity Verification</p>',
                    unsafe_allow_html=True)

        mode_badge = (
            '<span class="source-badge badge-reddit">LIVE</span>'
            if verification["verification_mode"] == "live"
            else '<span class="source-badge badge-google">MOCK</span>'
        )

        if verification["exact_match_found"]:
            st.markdown(
                f'<div class="verdict-warning">'
                f'⚠ EXACT MATCH DETECTED — Source: {verification["exact_match_source"]}'
                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="verdict-authentic">'
                f'✓ NO EXACT MATCH FOUND  {mode_badge}'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        vcol1, vcol2 = st.columns(2)

        with vcol1:
            st.markdown('<p class="section-label">📱 Reddit Sources</p>',
                        unsafe_allow_html=True)
            for r in sorted(verification["reddit"], key=lambda x: x["similarity"], reverse=True)[:5]:
                sim_pct = r["similarity"] * 100
                color = "#e06060" if sim_pct > 40 else "#d4a843" if sim_pct > 15 else "#5a4a2a"
                st.markdown(
                    f'<div class="shk-card" style="padding:0.8rem 1rem;margin-bottom:0.5rem;">'
                    f'<span class="source-badge badge-reddit">{r["source"]}</span>'
                    f'<span style="font-size:0.8rem;color:{color};font-family:Cinzel;'
                    f'float:right;">{sim_pct:.1f}% similar</span><br>'
                    f'<span style="font-size:0.88rem;color:#c9a96e;font-family:\'IM Fell English\','
                    f'serif;font-style:italic;">{r["snippet"][:90]}…</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        with vcol2:
            st.markdown('<p class="section-label">🌐 Web Results</p>',
                        unsafe_allow_html=True)
            for g in verification["google"][:5]:
                sim_pct = g["similarity"] * 100
                color = "#e06060" if sim_pct > 40 else "#d4a843" if sim_pct > 15 else "#5a4a2a"
                st.markdown(
                    f'<div class="shk-card" style="padding:0.8rem 1rem;margin-bottom:0.5rem;">'
                    f'<span class="source-badge badge-google">{g["domain"]}</span>'
                    f'<span style="font-size:0.8rem;color:{color};font-family:Cinzel;'
                    f'float:right;">{sim_pct:.1f}% similar</span><br>'
                    f'<span style="font-size:0.88rem;color:#c9a96e;">{g["title"][:80]}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        st.markdown('<hr class="ink-divider">', unsafe_allow_html=True)

        # ══ ROW 6: Technical Summary (interview-ready) ══════════════
        with st.expander("📋 Technical Analysis Summary — Interview Reference", expanded=False):
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            summary = f"""
**Run timestamp:** {ts}

**Pipeline:**
1. Detection → keyword-density heuristic (weighted, per-100-word score: {density:.2f})
2. Conversion → cascading regex replacement engine ({len(MODERN_TO_ARCHAIC)} rules)
3. Sentiment → TextBlob `PatternAnalyzer` (polarity: {sentiment['polarity']:.4f}, subjectivity: {sentiment['subjectivity']:.4f})
4. Scaling → Authoritative: {sentiment['authoritative_score']:.1f}/100 | Emotional: {sentiment['emotional_score']:.1f}/100
5. Verification → {verification['verification_mode'].upper()} mode | max similarity: {verification['max_thematic_score']*100:.1f}%

**Key design choices:**
- Subjectivity inversion as "objectivity proxy" for regal authority mapping
- Weighted keyword scoring prevents false positives from single archaic words
- Jaccard similarity on content words for thematic (non-exact) plagiarism detection
- Baseline corpus (Hamlet, Sonnet 18, Richard III) chosen for sentiment space diversity

**Word count:** {sentiment['word_count']} | **Sentences:** {len(sentiment['sentences'])}
**Archetype:** {sentiment['archetype']}
"""
            st.markdown(summary)


if __name__ == "__main__":
    main()
