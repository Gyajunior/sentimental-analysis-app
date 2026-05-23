cat << 'EOF' > config.py
import random

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

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--sepia-mid); border-radius: 3px; }

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

.kw-highlight {
    background: rgba(212,168,67,0.18);
    color: var(--gold);
    padding: 1px 4px;
    border-radius: 2px;
    font-style: normal;
}

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

.ink-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.5rem 0;
}

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

textarea {
    background: #130f05 !important;
    color: var(--parchment) !important;
    border: 1px solid var(--border) !important;
    font-family: 'Crimson Pro', serif !important;
    font-size: 1.05rem !important;
}

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

.section-label {
    font-family: 'Cinzel', serif;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--sepia-light);
    margin-bottom: 0.6rem;
}

.stProgress > div > div { background-color: var(--gold) !important; }
</style>
"""

ARCHAIC_KEYWORDS = {
    "thou": 3, "thee": 3, "thy": 3, "thine": 3, "hath": 3, "doth": 3,
    "wouldst": 3, "couldst": 3, "shouldst": 3, "hast": 3, "art": 2,
    "wilt": 3, "dost": 3, "canst": 3,
    "wherefore": 2, "whither": 2, "hither": 2, "thither": 2,
    "forsooth": 2, "prithee": 2, "methinks": 2, "perchance": 2,
    "betwixt": 2, "beseech": 2, "albeit": 2, "nay": 2, "yea": 2,
    "ere": 2, "oft": 2, "henceforth": 2, "verily": 2, "marry": 2,
    "good morrow": 1, "fie": 1, "alas": 1, "mayhaps": 1, "yon": 1,
    "yonder": 1, "hence": 1, "hark": 1, "lo": 1, "pray": 1,
    "sirrah": 1, "wench": 1, "knave": 1, "tis": 1,
    "'tis": 1, "o'er": 1, "ne'er": 1, "e'er": 1, "whence": 1,
    "naught": 1, "nought": 1, "twas": 1, "'twas": 1,
}

MODERN_TO_ARCHAIC = [
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
    (r"\bhe has\b",           "he hath"),
    (r"\bshe has\b",          "she hath"),
    (r"\bit has\b",           "it hath"),
    (r"\bhas\b",              "hath"),
    (r"\bhe does\b",          "he doth"),
    (r"\bshe does\b",         "she doth"),
    (r"\bit does\b",          "it doth"),
    (r"\bdoes\b",             "doth"),
    (r"\bhe is\b",            "he is"),
    (r"\bshe is\b",           "she is"),
    (r"\bwill not\b",         "shall not"),
    (r"\bwon't\b",            "shall not"),
    (r"\bcan't\b",            "canst not"),
    (r"\bcannot\b",           "canst not"),
    (r"\bdon't\b",            "dost not"),
    (r"\bdo not\b",           "dost not"),
    (r"\bdoesn't\b",          "doth not"),
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
    (r"\bthat\b",             "that"),
    (r"\bwhich\b",            "which"),
]

ETH_VERBS = [
    "walk", "speak", "run", "know", "see", "love", "hate",
    "come", "go", "live", "die", "fall", "rise", "stand",
    "seek", "find", "bring", "take", "make", "give",
]

HAMLET_BASELINE = {
    "polarity":     -0.04,
    "subjectivity":  0.42,
    "label":        "Hamlet — Act III.i",
}

SONNET_BASELINE = {
    "polarity":      0.35,
    "subjectivity":  0.72,
    "label":        "Sonnet XVIII",
}

RICHARD_BASELINE = {
    "polarity":     -0.25,
    "subjectivity":  0.55,
    "label":        "Richard III — Act I.i",
}

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
EOF