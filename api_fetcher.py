"""
Скачивает статьи по трем политикам через NewsAPI и сохраняет в SQLite.
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
import requests
from dotenv import load_dotenv

from database import categorize_news, save_news_to_db

load_dotenv()
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")        # ключ берём из .env
DB_PATH = Path(__file__).parent / "news.db"

POLITICIANS = {
    "Trump": "Trump",
    "Putin": "Putin",
    "Xi": '"Xi Jinping"',
}

PAGE_SIZE = 100
MAX_PAGES = 5          # 5×100 = 500 статей на персону

def fetch(query: str) -> list[dict]:
    url = "https://newsapi.org/v2/everything"
    headers = {"Authorization": NEWSAPI_KEY}
    date_from = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
    date_to   = datetime.utcnow().strftime("%Y-%m-%d")

    params = {
        "q": query,
        "from": date_from,
        "to": date_to,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": PAGE_SIZE,
        "page": 1,
    }

    articles = []
    for p in range(1, MAX_PAGES + 1):
        params["page"] = p
        r = requests.get(url, headers=headers, params=params, timeout=30)
        if r.status_code != 200:
            print("⚠️  NewsAPI error:", r.json())
            break
        chunk = r.json().get("articles", [])
        if not chunk:
            break
        articles.extend(chunk)
        if len(chunk) < PAGE_SIZE:
            break
    return articles

def std(article: dict) -> dict:
    """NewsAPI → универсальный формат"""
    return {
        "source": {"name": article["source"]["name"]},
        "title": article.get("title"),
        "url": article.get("url"),
        "publishedAt": article.get("publishedAt"),
        "content": article.get("content") or article.get("description", ""),
        "author": article.get("author"),
    }

def update_news():
    all_rows = []
    for name, q in POLITICIANS.items():
        raw = fetch(q)
        conv = [std(a) for a in raw]
        print(f"{name}: {len(conv)} статей")
        all_rows.extend(conv)

    print(f"Всего получено {len(all_rows)} статей, классифицируем…")
    trump, putin, xi, mixed = categorize_news(all_rows)

    save_news_to_db(trump, "Trump")
    save_news_to_db(putin, "Putin")
    save_news_to_db(xi,    "Xi")
    save_news_to_db(mixed, "Mixed")
    print("✅  База обновлена")

if __name__ == "__main__":
    update_news()


