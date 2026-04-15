"""
DataWithEla — Trend Agent
Finds high-CPC, trending topics that will generate the most ad revenue.
Analyzes what's hot in data/AI/tech and picks topics with money potential.
"""

import os
import json
import re
from openai import OpenAI

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
MODEL = "gemini-2.5-flash-lite"

client = OpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)


def find_trending_topics(num_topics: int = 10) -> list:
    """Find high-revenue trending topics using LLM analysis."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": """You are an expert SEO strategist and content monetization specialist.
You analyze trends in data analytics, AI, and tech careers to find topics that:
1. Have HIGH search volume (people are actively googling this)
2. Have HIGH CPC (advertisers pay a lot for these keywords — think $5-20 per click)
3. Are TIMELY (trending right now, not evergreen boring stuff)
4. Have LOW competition (not every blog has covered this yet)
5. Appeal to professionals willing to spend money (courses, tools, career changes)

High-CPC niches: cloud certifications, AI tools, data engineering, career transitions, salary negotiation, interview prep, specific tool comparisons."""},
            {"role": "user", "content": f"""It's April 2026. Find {num_topics} blog topics that will generate the MOST ad revenue for a data analytics blog.

For each topic, provide:
- title: SEO-optimized, clickable blog title
- estimated_cpc: estimated cost-per-click in USD for related keywords
- search_intent: what the reader wants (informational/commercial/transactional)
- money_angle: why advertisers pay for this keyword
- urgency: why write this NOW vs later (1-10, 10 = must publish today)

Return as JSON array:
[
  {{
    "title": "...",
    "estimated_cpc": 8.50,
    "search_intent": "commercial",
    "money_angle": "...",
    "urgency": 8
  }}
]

Sort by revenue potential (CPC × likely traffic). Return ONLY valid JSON."""}
        ],
        temperature=0.8,
        max_tokens=3000
    )

    raw = response.choices[0].message.content
    cleaned = re.sub(r'^```json\s*|```\s*$', '', raw.strip())

    try:
        topics = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r'\[[\s\S]*\]', cleaned)
        if match:
            topics = json.loads(match.group())
        else:
            topics = []

    # Sort by CPC × urgency
    topics.sort(key=lambda x: x.get("estimated_cpc", 0) * x.get("urgency", 5), reverse=True)

    return topics


def pick_best_topics(num_to_pick: int = 3) -> list:
    """Get trending topics and pick the best ones for publishing."""

    print("Scanning for high-revenue trending topics...")
    topics = find_trending_topics(num_topics=15)

    print(f"\nFound {len(topics)} topics, ranked by revenue potential:\n")
    for i, t in enumerate(topics):
        cpc = t.get('estimated_cpc', 0)
        urgency = t.get('urgency', 0)
        score = cpc * urgency
        print(f"  [{i+1}] ${cpc:.1f} CPC × {urgency}/10 urgency = {score:.0f} score")
        print(f"      {t['title']}")
        print(f"      Intent: {t.get('search_intent', '?')} | {t.get('money_angle', '')[:80]}")
        print()

    picked = topics[:num_to_pick]
    print(f"Selected top {num_to_pick} for publishing:")
    for t in picked:
        print(f"  → {t['title']}")

    return [t["title"] for t in picked]


if __name__ == "__main__":
    topics = pick_best_topics(5)
    print("\n\nReady to publish. Run:")
    for t in topics:
        print(f'  python3 agent.py "{t}"')
