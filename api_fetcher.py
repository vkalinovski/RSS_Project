"""
Скачивает новости через NewsAPI (https://newsapi.org) по трём политикам
и сохраняет их в SQLite-базу news.db.

Персоналии: Trump, Putin, Xi Jinping.
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
import requests
from dotenv import load_dotenv

from database import (
    categorize_news,
    save_news_to_db,
    get_last_saved_date,
)

load_dotenv()
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")          # <-- теперь NEWSAPI
db_path = Path(__file__).parent / "news.db"

PAGE_SIZE = 100        # максимум NewsAPI
MAX_PAGES  = 10        # 100 × 10 = 1000 статей на запрос

def fetch_news_from_newsapi(query: str) -> list[dict]:
    """
    Забирает все статьи NewsAPI «Everything» за период от last_saved_date
    (или −240 дней) до сегодня. Возвращает list[dict] как выдаёт NewsAPI.
    """
    start_date = get_last_saved_date()
    if not start_date:
        start_date = (datetime.utcnow() - timedelta(days=240)).strftime("%Y-%m-%d")
    end_date = datetime.utcnow().strftime("%Y-%m-%d")

    print(f"NewsAPI: {query!r}  {start_date} → {end_date}")

    url = "https://newsapi.org/v2/everything"
    headers = {"Authorization": NEWSAPI_KEY}
    params = {
        "q": query,
        "from": start_date,
        "to": end_date,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": PAGE_SIZE,
        "page": 1,
    }

    articles = []
    for page in range(1, MAX_PAGES + 1):
        params["page"] = page
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code != 200:
            print("⚠️  NewsAPI error:", resp.json())
            break

        chunk = resp.json().get("articles", [])
        if not chunk:
            break

        articles.extend(chunk)
        if len(chunk) < PAGE_SIZE:
            break  # достигли конца

    return articles


def convert_newsapi_to_standard(rows: list[dict]) -> list[dict]:
    """Приводит формат NewsAPI к 'универсальному' словарю."""
    conv = []
    for a in rows:
        conv.append(
            {
                "source": {"name": a["source"]["name"]},
                "title": a.get("title"),
                "url": a.get("url"),
                "publishedAt": a.get("publishedAt"),
                "content": a.get("content") or a.get("description", ""),
                "author": a.get("author"),
            }
        )
    return conv


def update_news():
    POLITICIANS = {
        "Trump": "Trump",
        "Putin": "Putin",
        "Xi": '"Xi Jinping"',
    }

    all_raw = []
    for name, query in POLITICIANS.items():
        rows_raw = fetch_news_from_newsapi(query)
        rows_std = convert_newsapi_to_standard(rows_raw)
        print(f"{name}: {len(rows_std)} статей")
        all_raw.extend(rows_std)

    print(f"Всего получено {len(all_raw)} статей, классифицируем…")
    trump, putin, xi, mixed = categorize_news(all_raw)

    save_news_to_db(trump, "Trump")
    save_news_to_db(putin, "Putin")
    save_news_to_db(xi,    "Xi")
    save_news_to_db(mixed, "Mixed")

    print("✅  Обновление базы завершено.")


if __name__ == "__main__":
    update_news()

