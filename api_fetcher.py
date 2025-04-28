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

MEDIASTACK_KEY = os.getenv("MEDIASTACK_KEY")
db_path = Path(__file__).parent / "news.db"

# лимит бесплатного тарифа
MAX_REQUESTS = 100
request_count = 0


def fetch_news_from_mediastack(query: str) -> list[dict]:
    """Получает все новости MediaStack по ключевому слову/фразе."""
    global request_count

    start_date = get_last_saved_date()
    if not start_date:
        start_date = (datetime.today() - timedelta(days=240)).strftime("%Y-%m-%d")

    end_date = datetime.today().strftime("%Y-%m-%d")
    print(f"MediaStack: {query!r}  {start_date} → {end_date}")

    params = {
        "access_key": MEDIASTACK_KEY,
        "keywords": query,
        "countries": "us,gb,ru,cn",
        "languages": "en,ru",
        "date": f"{start_date},{end_date}",
        "limit": 100,
        "offset": 0,
    }

    url = "http://api.mediastack.com/v1/news"
    articles = []

    while request_count < MAX_REQUESTS:
        resp = requests.get(url, params=params)
        request_count += 1

        if resp.status_code != 200:
            print("⚠️", resp.json())
            break

        data = resp.json()
        if not data.get("data"):
            break

        articles.extend(data["data"])
        params["offset"] += 100

    return articles


def convert_mediastack_to_standard(rows: list[dict]) -> list[dict]:
    conv = []
    for a in rows:
        conv.append(
            {
                "source": {"name": a.get("source")},
                "title": a.get("title"),
                "url": a.get("url"),
                "publishedAt": a.get("published_at"),
                "content": a.get("description", ""),
                "author": "Unknown",
            }
        )
    return conv


# ------------------- ГЛАВНАЯ ФУНКЦИЯ ------------------- #
def update_news():
    POLITICIANS = {
        "Trump": "Trump",
        "Putin": "Putin",
        "Xi": '"Xi Jinping"',
    }

    all_raw = []
    for name, q in POLITICIANS.items():
        rows = convert_mediastack_to_standard(fetch_news_from_mediastack(q))
        print(f"{name}: {len(rows)} статей")
        all_raw.extend(rows)

    print(f"Всего получено {len(all_raw)} статей, классифицируем…")
    trump, putin, xi, mixed = categorize_news(all_raw)

    save_news_to_db(trump, "Trump")
    save_news_to_db(putin, "Putin")
    save_news_to_db(xi, "Xi")
    save_news_to_db(mixed, "Mixed")

    print("✅ Обновление базы завершено.")


if __name__ == "__main__":
    update_news()

