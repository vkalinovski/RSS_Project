# -*- coding: utf-8 -*-
import os
from typing import List, Dict
from utils import now_utc
from database_utils import save_news_to_db, categorize_news
from newsapi import NewsApiClient  # pip install newsapi-python

# Используем библиотеку newsapi-python для упрощения запросов
API_KEY_VAR = "NEWSAPI_KEY"

def fetch_newsapi_articles(
    keywords: List[str],
    max_items: int = 100,
    language: str = "en"
) -> List[Dict]:
    """
    Сбор статей из NewsAPI.org по ключевым словам.
    """
    api_key = os.getenv(API_KEY_VAR)
    if not api_key:
        print(f"[{now_utc()}] Ошибка: не задан {API_KEY_VAR}")
        return []
    client = NewsApiClient(api_key=api_key)
    all_articles: List[Dict] = []
    for kw in keywords:
        resp = client.get_everything(q=kw, language=language, page_size=max_items, sort_by="publishedAt")
        arts = resp.get("articles", [])
        for art in arts:
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

def update_news(keywords: List[str] = ["Trump","Biden"], max_items: int = 100):
    """
    Загружает и сохраняет новости по списку keywords.
    """
    raw = fetch_newsapi_articles(keywords, max_items=max_items)
    if not raw:
        return
    trump_news, biden_news, both_news = categorize_news(raw)
    save_news_to_db(trump_news, "Trump")
    save_news_to_db(biden_news, "Biden")
    save_news_to_db(both_news, "Trump/Biden")
    print(f"[{now_utc()}] Обновление новостей через NewsAPI завершено.")
