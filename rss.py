"""
Парсит все ленты из файла rss_feeds.py,
выбирает статьи, где упоминаются Trump / Putin / Xi Jinping,
определяет, кому принадлежит статья, и сохраняет её в news.db.
"""

import feedparser
from datetime import datetime
from pathlib import Path

# локальные модули проекта
from database import create, categorize, save
from rss_feeds import RSS_FEEDS            # ← берем большой список отсюда

# ───────────────────────── helpers ─────────────────────────
def to_iso(dt: datetime) -> str:
    """2025-04-28T12:34:56Z"""
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_feed(url: str, source: str) -> list[dict]:
    """Читает RSS-ленту, возвращает список «черновых» статей."""
    feed = feedparser.parse(url)
    arts = []

    for e in feed.entries:
        if not getattr(e, "published_parsed", None):
            continue  # без даты пропускаем

        dt = datetime(*e.published_parsed[:6])
        arts.append(
            dict(
                source=source,
                title=e.get("title", "").strip(),
                url=e.get("link", "").strip(),
                publishedAt=to_iso(dt),
                content=(
                    e.get("content", [{}])[0].get("value")
                    or e.get("summary", "")
                ).strip(),
            )
        )
    return arts


# ───────────────────────── main routine ─────────────────────────
def main():
    create()                       # таблица news гарантированно есть
    raw = []

    for name, url in RSS_FEEDS.items():
        print("RSS:", name)
        raw.extend(parse_feed(url, name))

    # раскладываем на 4 корзины
    buckets = categorize(raw)

    # добавляем поле politician и сохраняем
    for politician, bunch in buckets.items():
        for art in bunch:
            art["politician"] = politician
        save(bunch)

    print("✅  RSS-ленты обработаны и занесены в news.db")


if __name__ == "__main__":
    main()
