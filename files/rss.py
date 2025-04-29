# -*- coding: utf-8 -*-
"""
Парсит RSS-ленты из rss_feeds.py, классифицирует по политикам
и дописывает в базу news.db (путь DB_PATH).
"""

import feedparser
from datetime import datetime
from database import create, categorize, save
from rss_feeds import RSS_FEEDS

def iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def parse(url: str, src: str):
    f = feedparser.parse(url)
    rows = []
    for e in f.entries:
        if not getattr(e, "published_parsed", None): continue
        dt = datetime(*e.published_parsed[:6])
        rows.append(
            dict(
                source=src,
                title=e.get("title", "").strip(),
                url=e.get("link", "").strip(),
                publishedAt=iso(dt),
                content=(e.get("content", [{}])[0].get("value")
                         or e.get("summary", "")).strip(),
            )
        )
    return rows

def main():
    create()
    raw = []
    for name, url in RSS_FEEDS.items():
        print("RSS:", name)
        raw.extend(parse(url, name))

    for pol, bunch in categorize(raw).items():
        for art in bunch:
            art["politician"] = pol
        save(bunch)

    print("✅ RSS-ленты сохранены")

if __name__ == "__main__":
    main()
