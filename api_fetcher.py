import os
from typing import List, Dict
from utils import now_utc
from database_utils import save_news_to_db, categorize_news
from newsapi import NewsApiClient

API_KEY_VAR = "NEWSAPI_KEY"


def fetch_newsapi_articles(
    keywords: List[str],
    max_items: int = 100,
    language: str = "en"
) -> List[Dict]:
    api_key = os.getenv(API_KEY_VAR)
    if not api_key:
        print(f"[{now_utc()}] Ошибка: не задан {API_KEY_VAR}")
        return []
    client = NewsApiClient(api_key=api_key)
    all_articles: List[Dict] = []
    for kw in keywords:
        resp = client.get_everything(q=kw, language=language, page_size=max_items, sort_by="publishedAt")
        for art in resp.get("articles", []):
            all_articles.append({
                "source":   art.get("source", {}).get("name"),
                "title":    art.get("title"),
                "content":  art.get("description") or art.get("content"),
                "published":art.get("publishedAt"),
                "url":      art.get("url"),
                "author":   art.get("author"),
            })
    print(f"[{now_utc()}] Получено через NewsAPI: {len(all_articles)} статей")
    return all_articles


def update_news(
    keywords: List[str] = ["Trump", "Xi Jinping", "Putin"],
    max_items: int = 100
):
    raw = fetch_newsapi_articles(keywords, max_items=max_items)
    if not raw:
        return
    trump_news, xi_news, putin_news, multiple_news = categorize_news(raw)
    save_news_to_db(trump_news, "Trump")
    save_news_to_db(xi_news, "Xi Jinping")
    save_news_to_db(putin_news, "Putin")
    save_news_to_db(multiple_news, "Multiple")
    print(f"[{now_utc()}] Обновление новостей через NewsAPI завершено.")
