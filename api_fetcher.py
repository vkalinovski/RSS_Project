import requests
from datetime import datetime, timedelta
import os
from database import get_last_saved_date, categorize_news, save_news_to_db

# Ваш ключ NewsAPI
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "3564e31ed0dc4e379fb768bb30e6b865")
BASE_URL = "https://newsapi.org/v2/everything"

def fetch_from_newsapi(query, from_date, to_date, page_size=100):
    """Скачивает до 500 статей (5 страниц по 100) для одного запроса."""
    all_articles = []
    for page in range(1, 6):
        params = {
            "apiKey": NEWSAPI_KEY,
            "q": query,
            "from": from_date,
            "to": to_date,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": page_size,
            "page": page
        }
        resp = requests.get(BASE_URL, params=params)
        if resp.status_code != 200:
            print("NewsAPI Error", resp.json())
            break
        data = resp.json().get("articles", [])
        if not data:
            break
        all_articles.extend(data)
        if len(data) < page_size:
            break
    print(f"  → Найдено {len(all_articles)} статей по «{query}»")
    return all_articles

def convert_to_standard(articles):
    """Приводит формат NewsAPI к единому виду для DB."""
    out = []
    for a in articles:
        out.append({
            "source": a.get("source"),
            "title": a.get("title"),
            "url": a.get("url"),
            "publishedAt": a.get("publishedAt"),
            "content": a.get("content") or a.get("description") or "",
            "author": a.get("author") or "Unknown"
        })
    return out

def update_news():
    """Скачивает и сохраняет новости для Trump, Putin, Xi Jinping."""
    last = get_last_saved_date()
    if last:
        start = last
    else:
        start = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
    end = datetime.utcnow().strftime("%Y-%m-%d")

    print(f"Обновляем с {start} по {end}:")

    all_raw = []
    for q in ["Trump", "Putin", "\"Xi Jinping\""]:
        arts = fetch_from_newsapi(q, start, end)
        all_raw.extend(convert_to_standard(arts))

    t, p, x, m = categorize_news(all_raw)
    save_news_to_db(t, "Trump")
    save_news_to_db(p, "Putin")
    save_news_to_db(x, "Xi Jinping")
    save_news_to_db(m, "Multiple")

    print("Обновление через NewsAPI завершено.")

if __name__ == "__main__":
    update_news()

