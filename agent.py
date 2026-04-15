"""
DataWithEla — AI Content Agent
Generates SEO-optimized articles and auto-publishes to GitHub Pages.
"""

import os
import json
import subprocess
import re
from datetime import datetime
from openai import OpenAI

# === CONFIG ===
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyDCe6k3rGR3jmheHhiAM8oku2kMhTzaSZM")
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(REPO_DIR, "posts")
MODEL = "gemini-2.5-flash-lite"

client = OpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

os.makedirs(POSTS_DIR, exist_ok=True)


def generate_article(topic: str) -> dict:
    """Generate a full SEO-optimized article on the given topic."""

    prompt = f"""Write a blog article about: {topic}

Requirements:
- Title should be catchy, curiosity-driven, SEO-friendly (under 65 chars)
- 1000-1500 words
- Written in first person, casual but credible tone
- Include 3-5 specific statistics or data points (cite sources)
- Use headers (H2, H3) to break up content
- End with actionable takeaways
- Include a "bottom line" summary box
- Target audience: aspiring data analysts and tech professionals
- Do NOT include any personal names, school names, or identifying info

Return as JSON:
{{
  "title": "article title",
  "slug": "url-friendly-slug",
  "description": "SEO meta description under 155 chars",
  "tags": ["tag1", "tag2", "tag3"],
  "content_html": "full article body in HTML (use h2, h3, p, ul, li, strong, em tags)"
}}

Return ONLY valid JSON."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a tech blogger who writes data-driven, engaging articles about AI, data analytics, and tech careers. You write like a smart friend explaining things over coffee — not like a textbook."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=4000
    )

    raw = response.choices[0].message.content
    cleaned = re.sub(r'^```json\s*|```\s*$', '', raw.strip())

    # Try parsing, if fails try to fix common issues
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to extract JSON from response
        match = re.search(r'\{[\s\S]*\}', cleaned)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        # Last resort: ask LLM to fix the JSON
        fix_response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Fix this broken JSON. Return ONLY valid JSON, nothing else."},
                {"role": "user", "content": cleaned}
            ],
            temperature=0,
            max_tokens=4000
        )
        fixed = fix_response.choices[0].message.content
        fixed = re.sub(r'^```json\s*|```\s*$', '', fixed.strip())
        return json.loads(fixed)


def build_post_html(article: dict) -> str:
    """Wrap article content in the site's HTML template."""

    tags_html = "".join([f'<span class="tag">{t}</span>' for t in article["tags"]])
    date = datetime.now().strftime("%B %Y")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{article['description']}">
    <title>{article['title']} | DataWithEla</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Georgia', serif; color: #1a1a1a; background: #fafaf8; line-height: 1.8; }}
        header {{ background: linear-gradient(135deg, #0f1b2d 0%, #1c3b2e 100%); color: white; padding: 60px 20px; text-align: center; }}
        header a {{ color: white; text-decoration: none; font-size: 1.2em; font-weight: bold; }}
        .article-header {{ max-width: 720px; margin: 0 auto; padding: 40px 20px 0; }}
        .article-header h1 {{ font-size: 2.2em; line-height: 1.3; color: #0f1b2d; }}
        .article-header .meta {{ color: #888; margin: 12px 0 30px; font-size: 0.9em; }}
        .tag {{ display: inline-block; background: #f0f4f0; color: #1c3b2e; padding: 3px 10px; border-radius: 12px; font-size: 0.8em; margin-right: 6px; }}
        article {{ max-width: 720px; margin: 0 auto; padding: 0 20px 60px; font-size: 1.05em; }}
        article h2 {{ font-size: 1.5em; color: #0f1b2d; margin: 35px 0 15px; }}
        article h3 {{ font-size: 1.2em; color: #1c3b2e; margin: 25px 0 10px; }}
        article p {{ margin-bottom: 18px; color: #333; }}
        article ul {{ margin: 10px 0 20px 25px; }}
        article li {{ margin-bottom: 8px; color: #333; }}
        article strong {{ color: #0f1b2d; }}
        .highlight-box {{ background: #f0f4f0; border-left: 4px solid #1c3b2e; padding: 20px; margin: 25px 0; border-radius: 0 8px 8px 0; }}
        .cta-box {{ background: #0f1b2d; color: white; border-radius: 8px; padding: 30px; text-align: center; margin: 40px 0; }}
        .cta-box h3 {{ margin-bottom: 10px; }}
        .cta-box p {{ opacity: 0.8; margin-bottom: 15px; }}
        .cta-box input {{ padding: 10px 14px; border: none; border-radius: 6px; width: 220px; margin-right: 8px; }}
        .cta-box button {{ padding: 10px 20px; background: #1c3b2e; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; }}
        footer {{ text-align: center; padding: 30px; color: #999; font-size: 0.85em; border-top: 1px solid #e8e8e8; }}
        footer a {{ color: #666; text-decoration: none; }}
        @media (max-width: 600px) {{ .article-header h1 {{ font-size: 1.7em; }} .cta-box input {{ width: 100%; margin-bottom: 10px; }} }}
    </style>
</head>
<body>
<header><a href="../index.html">DataWithEla</a></header>
<div class="article-header">
    <h1>{article['title']}</h1>
    <div class="meta">{date} &middot; 7 min read</div>
    {tags_html}
</div>
<article>
{article['content_html']}
</article>
<div style="max-width: 720px; margin: 0 auto; padding: 0 20px;">
    <div class="cta-box">
        <h3>Get new articles in your inbox</h3>
        <p>No spam. One email when something new drops.</p>
        <input type="email" placeholder="your@email.com">
        <button>Subscribe</button>
    </div>
</div>
<footer><p><a href="../index.html">&larr; Back to DataWithEla</a> &middot; &copy; 2026</p></footer>
</body>
</html>"""


def update_index(article: dict):
    """Add the new article to index.html."""

    index_path = os.path.join(REPO_DIR, "index.html")
    with open(index_path, "r") as f:
        index = f.read()

    tags_html = "".join([f'<span class="tag">{t}</span>' for t in article["tags"]])
    date = datetime.now().strftime("%B %Y")

    new_card = f"""<div class="post-card">
        <h3><a href="posts/{article['slug']}.html">{article['title']}</a></h3>
        <div class="meta">{date} &middot; 7 min read</div>
        <p>{article['description']}</p>
        {tags_html}
    </div>

    <h2"""

    # Insert before the first <h2 after "Latest Articles"
    insert_point = index.find('<h2>Tech &')
    if insert_point == -1:
        insert_point = index.find('</div>\n\n    <div id="about"')

    if insert_point > 0:
        index = index[:insert_point] + new_card[:-7] + "\n\n    " + index[insert_point:]
        with open(index_path, "w") as f:
            f.write(index)
        print(f"  Updated index.html")


def git_push(message: str):
    """Commit and push to GitHub."""

    os.chdir(REPO_DIR)
    subprocess.run(["git", "add", "-A"], check=True)
    subprocess.run(["git", "commit", "-m", message], check=True)
    result = subprocess.run(["git", "push"], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  Pushed to GitHub!")
    else:
        print(f"  Push failed: {result.stderr}")


def create_and_publish(topic: str):
    """Full pipeline: generate article → save → update index → push to GitHub."""

    print(f"\n{'='*50}")
    print(f"GENERATING: {topic}")
    print(f"{'='*50}")

    # 1. Generate
    print("  Writing article...")
    article = generate_article(topic)
    print(f"  Title: {article['title']}")

    # 2. Save post
    post_html = build_post_html(article)
    post_path = os.path.join(POSTS_DIR, f"{article['slug']}.html")
    with open(post_path, "w") as f:
        f.write(post_html)
    print(f"  Saved: {post_path}")

    # 3. Update index
    update_index(article)

    # 4. Push
    git_push(f"New article: {article['title']}")

    print(f"  LIVE: https://elakumuk.github.io/datawithela/posts/{article['slug']}.html")
    return article


# === TOPIC IDEAS (agent picks from these or generates new ones) ===
TOPIC_BANK = [
    "Best free tools for learning SQL in 2026",
    "Python vs R for data analytics: which should you learn first",
    "How to build a data analytics portfolio that actually gets interviews",
    "The rise of AI agents: what they are and why they matter",
    "5 SQL mistakes that make senior analysts cringe",
    "What is RAG and why every data professional should understand it",
    "ChatGPT vs Claude vs Gemini: which AI is best for data work",
    "How to transition from Excel to Python without losing your mind",
    "The highest paying data skills in 2026 according to job postings",
    "Why every data analyst should learn about LLMs",
    "Prompt engineering for data analysts: a practical guide",
    "How to automate your boring work with Python in 30 minutes",
    "The truth about data science bootcamps in 2026",
    "What hiring managers actually look for in data analyst resumes",
    "Power BI vs Tableau in 2026: an honest comparison",
]


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        # Pick a random topic
        import random
        topic = random.choice(TOPIC_BANK)

    create_and_publish(topic)
