# -*- coding: utf-8 -*-
import feedparser
from typing import List, Dict
from rss_feeds import RSS_FEEDS
from utils import normalise_date, now_utc

def fetch_rss_articles(max_items: int = 100) -> List[Dict]:
    articles: List[Dict] = []
    for source_name, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            if feed.status != 200 or not feed.entries:
                print(f"[{now_utc()}] Ошибка RSS {feed.status}: {source_name}")
                continue
        except Exception as e:
            print(f"[{now_utc()}] Ошибка парсинга {source_name}: {str(e)}")
            continue
        
        count = 0
        for entry in feed.entries:
            if count >= max_items: break
            try:
                articles.append({
                    "source":    source_name,
                    "title":     entry.get("title", ""),
                    "content":   entry.get("summary", ""),
                    "published": normalise_date(entry.get("published")),
                    "url":       entry.get("link"),
                    "author":    entry.get("author")
                })
                count += 1
            except Exception as e:
                print(f"[{now_utc()}] Ошибка обработки статьи: {str(e)}")
    return articles
