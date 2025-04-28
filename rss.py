"""
Собирает новости из набора RSS-лент, отфильтровывает статьи,
где упоминаются Trump / Putin / Xi Jinping, классифицирует и
сохраняет в базу news.db.

Все выходные файлы (news.db, graphs, csv) хранятся в
/content/drive/MyDrive/test/RSS_Project – путь задаётся в Colab-ячейке.
"""

import feedparser
from datetime import datetime
from pathlib import Path
from database import create, categorize, save

# ────────── RSS-источники ──────────
FEEDS = {
    "NYT Politics":    "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml",
    "BBC Politics":    "http://feeds.bbci.co.uk/news/politics/rss.xml",
    "Politico":        "http://www.politico.com/rss/Top10Blogs.xml",
    "Washington Post": "http://feeds.washingtonpost.com/rss/politics",
    "Fox News":        "http://feeds.foxnews.com/foxnews/latest?format=xml",
    "РИА Политика":    "https://ria.ru/export/rss2/politics/index.xml",
    "ТАСС":            "https://tass.ru/rss/v2.xml",
    "RT English":      "https://www.rt.com/rss/news/",
    "Xinhua":          "http://www.xinhuanet.com/english/rss/worldrss.xml",
    "China Daily":     "https://www.chinadaily.com.cn/rss/china_rss.xml",
}

# ────────── helpers ──────────
def iso8601(dt: datetime) -> str:
    """Дата → ISO 8601 с суффиксом Z"""
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def parse_feed(url: str, source: str) -> list[dict]:
    """Парсит одну RSS-ленту и возвращает список черновых статей."""
    feed = feedparser.parse(url)
    items = []
    for e in feed.entries:
        if not getattr(e, "published_parsed", None):
            continue  # без даты пропускаем

        dt = datetime(*e.published_parsed[:6])
        items.append(
            dict(
                source      = source,
                title       = e.get("title", "").strip(),
                url         = e.get("link", "").strip(),
                publishedAt = iso8601(dt),
                content     = (
                    e.get("content", [{}])[0].get("value")
                    or e.get("summary", "")
                ).strip(),
            )
        )
    return items

# ────────── основной процесс ──────────
def main():
    create()                   # гарантируем, что таблица news есть
    raw_articles = []

    for name, url in FEEDS.items():
        print("RSS:", name)
        raw_articles.extend(parse_feed(url, name))

    # классифицируем на 4 корзины
    buckets = categorize(raw_articles)

    # для каждой корзины дописываем поле politician и сохраняем
    for politician, bunch in buckets.items():
        for art in bunch:
            art["politician"] = politician
        save(bunch)

    print("✅  RSS обработан и сохранён")

if __name__ == "__main__":
    main()

