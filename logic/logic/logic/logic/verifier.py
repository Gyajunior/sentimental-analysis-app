cat << 'EOF' > logic/verifier.py
import re
import random
import streamlit as st
from typing import Dict
from config import MOCK_REDDIT_CORPUS, MOCK_GOOGLE_RESULTS

def compute_similarity(text_a: str, text_b: str) -> float:
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
    results = {
        "reddit": [],
        "google": [],
        "exact_match_found": False,
        "exact_match_source": None,
        "max_thematic_score": 0.0,
        "thematic_sources": [],
        "verification_mode": "mock",
    }

    if use_real_reddit and reddit_client_id and reddit_secret:
        try:
            import praw
            reddit = praw.Reddit(
                client_id=reddit_client_id,
                client_secret=reddit_secret,
                user_agent="ShakespeareEngine/1.0",
            )
            subreddits = ["shakespeare", "literature", "quotes", "classiclit"]
            query = " ".join(text.split()[:10])
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

    if not results["reddit"]:
        for entry in MOCK_REDDIT_CORPUS:
            sim = compute_similarity(text, entry["snippet"])
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

    if not results["google"]:
        for entry in MOCK_GOOGLE_RESULTS:
            sim = round(random.uniform(0.02, 0.18), 3)
            results["google"].append({
                "title": entry["title"],
                "domain": entry["domain"],
                "similarity": sim,
                "url": "#",
            })

    all_sims = [r["similarity"] for r in results["reddit"]] + \
               [r["similarity"] for r in results["google"]]

    results["max_thematic_score"] = max(all_sims) if all_sims else 0.0

    for r in results["reddit"]:
        if r.get("exact") or r["similarity"] > 0.55:
            results["exact_match_found"] = True
            results["exact_match_source"] = r["source"]
            break

    results["thematic_sources"] = [
        r["source"] for r in results["reddit"] if r["similarity"] > 0.15
    ]

    return results
EOF