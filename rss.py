# -*- coding: utf-8 -*-
import feedparser
from typing import List, Dict
from rss_feeds import RSS_FEEDS
from utils import normalise_date, now_utc
from database_utils import create_database, save_news_to_db, categorize_news, remove_duplicates

def fetch_rss_news(max_items: int = 50):
    # 1) Создаём таблицу, если она ещё не существует
    create_database()

    all_articles: List[Dict] = []
    for source_name, url in RSS_FEEDS.items():
        ...
    # фильтрация по Trump/Xi/Putin
    trump, xi, putin, multiple = categorize_news(filtered)
    save_news_to_db(trump, "Trump")
    save_news_to_db(xi,    "Xi Jinping")
    save_news_to_db(putin, "Putin")
    save_news_to_db(multiple, "Multiple")

    # 2) Удаляем дубликаты в той же БД
    remove_duplicates()
    print(f"[{now_utc()}] RSS-обновление завершено.")

