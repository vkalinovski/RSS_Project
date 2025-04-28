# -*- coding: utf-8 -*-
import feedparser
from typing import List, Dict
from rss_feeds import RSS_FEEDS
from utils import normalise_date, now_utc
from database_utils import create_database, save_news_to_db, categorize_news, remove_duplicates

def fetch_rss_news(max_items: int = 50):
    """
    Сбор и сохранение статей из всех RSS_FEEDS (до max_items на каждый источник).
    """
    # Убедимся, что есть таблица
    create_database()

    all_articles: List[Dict] = []
    for source_name, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        if not hasattr(feed, "entries") or not feed.entries:
            print(f"[{now_utc()}] RSS пуст или недоступен: {source_name}")
            continue
        count = 0
        for entry in feed.entries:
            if count >= max_items:
                break
            all_articles.append({
                "source":    source_name,
                "title":     entry.get("title", ""),
                "content":   entry.get("summary", ""),
                "published": normalise_date(entry.get("published")),
                "url":       entry.get("link"),
                "author":    entry.get("author")
            })
            count += 1
        print(f"[{now_utc()}] Получено {count} из RSS «{source_name}»")

    # Оставляем только Trump/Biden
    filtered = []
    for art in all_articles:
        txt = ((art["title"] or "") + " " + (art["content"] or "")).lower()
        if "trump" in txt or "biden" in txt:
            filtered.append(art)

    trump_news, biden_news, both_news = categorize_news(filtered)
    save_news_to_db(trump_news, "Trump")
    save_news_to_db(biden_news, "Biden")
    save_news_to_db(both_news, "Trump/Biden")

    remove_duplicates()
    print(f"[{now_utc()}] RSS-обновление завершено.")
