"""
Качает новости через NewsAPI (https://newsapi.org).
Персоналии: Trump, Putin, Xi Jinping.
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
import requests
from dotenv import load_dotenv
from database import categorize_news, save_news_to_db

load_dotenv()
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
DB_PATH = Path(__file__).parent / "news.db"

POLITICIANS = {
    "Trump": "Trump",
    "Putin": "Putin",
    "Xi": '"Xi Jinping"',
}

PAGE_SIZE = 100
MAX_PAGES = 5                      # 5 × 100 = 500 статьей / персона

def fetch(query: str) -> list[dict]:
    url = "https://newsapi.org/v2/everything"
    headers = {"Authorization": NEWSAPI_KEY}
    date_from = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
    date_to   = datetime.utcnow().strftime("%Y-%m-%d")

    params = dict(
        q=query,
        from_param=date_from,      # ← так называется параметр в NewsAPI
        to=date_to,
        language="en",
        sortBy="publishedAt",
        pageSize=PAGE_SIZE,
    )

    articles = []
    for page in range(1, MAX_PAGES + 1):
        params["page"] = page
        r = requests.get(url, headers=headers, params=params, timeout=30)
        if r.status_code != 200:
            print("⚠️  NewsAPI:", r.json())
            break
        batch = r.json().get("articles", [])
        if not batch:
            break
        articles.extend(batch)
        if len(batch) < PAGE_SIZE:
            break
    return articles

def to_std(a: dict) -> dict:
    return {
        "source": {"name": a["source"]["name"]},
        "title": a.get("title"),
        "url": a.get("url"),
        "publishedAt": a.get("publishedAt"),
        "content": a.get("content") or a.get("description", ""),
        "author": a.get("author"),
    }

def update_news():
    all_rows = []
    for name, q in POLITICIANS.items():
        raw = fetch(q)
        conv = [to_std(a) for a in raw]
        print(f"{name}: {len(conv)} статей")
        all_rows.extend(conv)

    print("Всего получено", len(all_rows), "статей")
    trump, putin, xi, mixed = categorize_news(all_rows)

    save_news_to_db(trump, "Trump")
    save_news_to_db(putin, "Putin")
    save_news_to_db(xi,    "Xi")
    save_news_to_db(mixed, "Mixed")
    print("✅  База news.db обновлена")

if __name__ == "__main__":
    update_news()


