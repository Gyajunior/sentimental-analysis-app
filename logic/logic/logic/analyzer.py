cat << 'EOF' > logic/analyzer.py
from textblob import TextBlob
from typing import Dict

def analyze_sentiment(text: str) -> Dict:
    blob = TextBlob(text)
    polarity    = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    objectivity = 1.0 - subjectivity

    emotional_score     = round(subjectivity * 100, 1)
    authoritative_score = round(objectivity * 100, 1)

    if polarity > 0.2:
        polarity_label = "Light / Comedic"
        polarity_color = "#7fc47f"
    elif polarity < -0.2:
        polarity_label = "Dark / Tragic"
        polarity_color = "#e06060"
    else:
        polarity_label = "Ambivalent / Dramatic"
        polarity_color = "#d4a843"

    if emotional_score > 65:
        archetype = "Soliloquy — Inner Turmoil"
    elif authoritative_score > 65:
        archetype = "Proclamation — Regal Decree"
    elif polarity < -0.15:
        archetype = "Lament — Elegiac Tone"
    else:
        archetype = "Discourse — Balanced Rhetoric"

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
EOF