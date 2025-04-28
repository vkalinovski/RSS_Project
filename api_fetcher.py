# -*- coding: utf-8 -*-
import os
import requests
from typing import List, Dict
from utils import normalise_date, now_utc

def fetch_newsapi_articles(
    keywords: List[str],
    max_items: int = 100,
    language: str = "en"
) -> List[Dict]:
    """
    Сбор статей из NewsAPI.org по ключевым словам.
    При ошибках возвращает [].
    """
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        print(f"[{now_utc()}] Ошибка: не задан NEWSAPI_KEY")
        return []
    url = "https://newsapi.org/v2/everything"
    articles: List[Dict] = []
    for kw in keywords:
        params = {
            "q":       kw,
            "language":language,
            "pageSize":max_items,
            "sortBy":  "publishedAt",
            "apiKey":  api_key,
        }
        try:
            resp = requests.get(url, params=params, timeout=15)
            if resp.status_code != 200:
                print(f"[{now_utc()}] NewsAPI status {resp.status_code}: {resp.text}")
                return []
            data = resp.json().get("articles", [])
        except requests.exceptions.RequestException as e:
            print(f"[{now_utc()}] NewsAPI request failed: {e}")
            return []
        for art in data:
            articles.append({
                "source":   art.get("source", {}).get("name"),
                "title":    art.get("title"),
                "content":  art.get("description") or art.get("content"),
                "published":normalise_date(art.get("publishedAt")),
                "url":      art.get("url"),
                "author":   art.get("author"),
            })
            if len(articles) >= max_items:
                break
    print(f"[{now_utc()}] Получено через NewsAPI: {len(articles)} статей")
    return articles
