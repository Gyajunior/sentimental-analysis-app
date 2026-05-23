cat << 'EOF' > logic/detector.py
import re
from typing import Tuple, List
from config import ARCHAIC_KEYWORDS

def detect_shakespearean(text: str, threshold: float) -> Tuple[bool, float, List[str]]:
    words = re.findall(r"[a-z']+", text.lower())
    total_words = max(len(words), 1)

    score = 0
    matched = []
    for word, weight in ARCHAIC_KEYWORDS.items():
        pattern = r'\b' + re.escape(word) + r'\b'
        hits = len(re.findall(pattern, text.lower()))
        if hits:
            score += hits * weight
            matched.extend([word] * hits)

    density = (score / total_words) * 100
    return density >= threshold, round(density, 2), list(set(matched))

def highlight_keywords(text: str, keywords: List[str]) -> str:
    highlighted = text
    for kw in sorted(keywords, key=len, reverse=True):
        pattern = r'(?i)\b' + re.escape(kw) + r'\b'
        highlighted = re.sub(
            pattern,
            lambda m: f'<span class="kw-highlight">{m.group()}</span>',
            highlighted
        )
    return highlighted
EOF