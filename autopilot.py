"""
DataWithEla — AUTOPILOT
Full autonomous system: find trends → write articles → publish → repeat.
Set it and forget it.

Usage:
  export GEMINI_API_KEY="your_key"
  python3 autopilot.py           # default: 3 articles
  python3 autopilot.py 5         # 5 articles
"""

import sys
import time
import random
from trend_agent import pick_best_topics
from agent import create_and_publish


def autopilot(num_articles: int = 3):
    """Full autonomous pipeline: trend discovery → content creation → publishing."""

    print("""
    ╔══════════════════════════════════════════╗
    ║     DataWithEla — AUTOPILOT MODE        ║
    ║     Trend → Write → Publish → Repeat    ║
    ╚══════════════════════════════════════════╝
    """)

    # Step 1: Find trending high-revenue topics
    print("STEP 1: Finding trending topics with highest revenue potential...\n")
    topics = pick_best_topics(num_to_pick=num_articles)

    if not topics:
        print("No topics found. Falling back to topic bank.")
        from agent import TOPIC_BANK
        topics = random.sample(TOPIC_BANK, min(num_articles, len(TOPIC_BANK)))

    # Step 2: Generate and publish each article
    print(f"\nSTEP 2: Generating {len(topics)} articles...\n")
    published = []
    failed = []

    for i, topic in enumerate(topics):
        try:
            print(f"\n[{i+1}/{len(topics)}] Publishing: {topic}")
            article = create_and_publish(topic)
            published.append(article["title"])

            if i < len(topics) - 1:
                wait = random.randint(10, 30)
                print(f"  Cooling down {wait}s...")
                time.sleep(wait)

        except Exception as e:
            print(f"  FAILED: {e}")
            failed.append(topic)
            continue

    # Step 3: Report
    print(f"""
    ╔══════════════════════════════════════════╗
    ║           AUTOPILOT COMPLETE            ║
    ╠══════════════════════════════════════════╣
    ║  Published: {len(published):>3} articles                 ║
    ║  Failed:    {len(failed):>3} articles                 ║
    ╚══════════════════════════════════════════╝
    """)

    for title in published:
        print(f"  ✓ {title}")
    for topic in failed:
        print(f"  ✗ {topic}")

    return published


if __name__ == "__main__":
    num = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    autopilot(num_articles=num)
