# -*- coding: utf-8 -*-
import feedparser
from typing import List, Dict
from rss_feeds import RSS_FEEDS
from utils import normalise_date, now_utc

def fetch_rss_articles(max_items: int = 100) -> List[Dict]:
    """
    Сбор статей из всех RSS_FEEDS.
    max_items — максимум статей на каждый источник.
    """
    articles: List[Dict] = []
    for source_name, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        if not feed.entries:
            print(f"[{now_utc()}] RSS пуст или недоступен: {source_name}")
            continue
        count = 0
        for entry in feed.entries:
            if count >= max_items:
                break
            articles.append({
                "source":    source_name,
                "title":     entry.get("title", ""),
                "content":   entry.get("summary", ""),
                "published": normalise_date(entry.get("published")),
                "url":       entry.get("link"),
                "author":    entry.get("author")
            })
            count += 1
        print(f"[{now_utc()}] Получено {count} из RSS «{source_name}»")
    return articles
