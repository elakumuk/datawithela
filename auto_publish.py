"""
DataWithEla — Auto Publisher
Runs agent multiple times, generates articles, publishes all.
Usage: export GEMINI_API_KEY="your_key" && python3 auto_publish.py
"""

import random
import time
from agent import create_and_publish, TOPIC_BANK, client, MODEL
import json
import re

# Extended topic bank — agent picks from these
EXTRA_TOPICS = [
    "Best free tools for learning SQL in 2026",
    "Python vs R for data analytics: which should you learn first",
    "How to build a data analytics portfolio that gets interviews",
    "The rise of AI agents: what they are and why they matter",
    "5 SQL mistakes that make senior analysts cringe",
    "What is RAG and why every data professional should understand it",
    "ChatGPT vs Claude vs Gemini: which AI is best for data work",
    "How to transition from Excel to Python without losing your mind",
    "Why every data analyst should learn about LLMs",
    "Prompt engineering for data analysts: a practical guide",
    "How to automate your boring work with Python in 30 minutes",
    "The truth about data science bootcamps in 2026",
    "What hiring managers actually look for in data analyst resumes",
    "Power BI vs Tableau in 2026: an honest comparison",
    "Is a master's degree in data analytics worth it in 2026",
    "How to ace a data analyst technical interview",
    "The most underrated Python libraries for data analysis",
    "Why your dashboard isn't getting used and how to fix it",
    "AI startups to watch in 2026",
    "How to use ChatGPT for data cleaning without losing accuracy",
    "The future of business intelligence: trends for 2026-2027",
    "Remote data analyst jobs: where to find them and how to land one",
    "What is an AI agent and how will it change data work",
    "The biggest mistakes junior data analysts make",
    "How to go from data analyst to data scientist",
    "No-code AI tools that actually work for business analytics",
    "Why storytelling is the most important skill for data analysts",
    "How tech layoffs are reshaping the data job market in 2026",
    "The complete guide to A/B testing for beginners",
    "How to use AI to 10x your productivity as a data analyst",
]

ALL_TOPICS = list(set(TOPIC_BANK + EXTRA_TOPICS))


def generate_trending_topic() -> str:
    """Ask LLM to suggest a trending topic."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You suggest blog post topics about data analytics, AI, and tech careers. Topics should be timely, SEO-friendly, and interesting to aspiring data professionals."},
            {"role": "user", "content": "Suggest ONE trending blog topic for a data analytics blog in April 2026. Just the topic title, nothing else. Make it specific and clickable."}
        ],
        temperature=0.9,
        max_tokens=100
    )
    return response.choices[0].message.content.strip().strip('"')


def run_batch(num_articles: int = 3, use_ai_topics: bool = True):
    """Generate and publish multiple articles."""

    print(f"\n{'='*60}")
    print(f"  DataWithEla Auto Publisher")
    print(f"  Generating {num_articles} articles...")
    print(f"{'='*60}\n")

    published = []

    for i in range(num_articles):
        try:
            # Mix: some from bank, some AI-generated
            if use_ai_topics and random.random() > 0.5:
                topic = generate_trending_topic()
                print(f"\n[{i+1}/{num_articles}] AI-suggested topic: {topic}")
            else:
                topic = random.choice(ALL_TOPICS)
                print(f"\n[{i+1}/{num_articles}] Bank topic: {topic}")

            article = create_and_publish(topic)
            published.append(article["title"])

            # Wait between articles to avoid API rate limits
            if i < num_articles - 1:
                wait = random.randint(5, 15)
                print(f"\n  Waiting {wait}s before next article...")
                time.sleep(wait)

        except Exception as e:
            print(f"\n  ERROR on article {i+1}: {e}")
            continue

    print(f"\n{'='*60}")
    print(f"  DONE! Published {len(published)}/{num_articles} articles:")
    for title in published:
        print(f"    - {title}")
    print(f"{'='*60}")


if __name__ == "__main__":
    import sys

    num = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    run_batch(num_articles=num)
