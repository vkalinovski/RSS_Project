from datetime import datetime

import feedparser

from database import (
    create_database,
    save_news_to_db,
    categorize_news,
    remove_duplicates,
)

RSS_FEEDS = {
    # US / UK
    "NY Times Politics": "https://rss.nytimes.com/services/xml/rss/nyt/Upshot.xml",
    "Politico": "http://www.politico.com/rss/Top10Blogs.xml",
    "Washington Post Politics": "http://feeds.washingtonpost.com/rss/politics",
    "Fox News Latest": "http://feeds.foxnews.com/foxnews/latest?format=xml",
    "BBC Politics": "http://feeds.bbci.co.uk/news/politics/rss.xml",
    # Russia
    "РИА Политика": "https://ria.ru/export/rss2/politics/index.xml",
    "ТАСС": "https://tass.ru/rss/v2.xml",
    "RT English": "https://www.rt.com/rss/news/",
    # China
    "Xinhua": "http://www.xinhuanet.com/english/rss/worldrss.xml",
    "China Daily": "https://www.chinadaily.com.cn/rss/china_rss.xml",
}


def parse_feed(url: str, source_name: str) -> list[dict]:
    feed = feedparser.parse(url)
    items = []
    for e in feed.entries:
        art = {
            "source": feed.feed.get("title", source_name),
            "title": e.get("title", "").strip(),
            "url": e.get("link", "").strip(),
            "publishedAt": None,
            "content": "",
            "description": e.get("description", "").strip(),
            "author": e.get("author", "").strip() if e.get("author") else None,
        }

        if e.get("published_parsed"):
            dt = datetime(*e.published_parsed[:6])
            art["publishedAt"] = dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")

        if e.get("content"):
            art["content"] = e.content[0].value.strip()

        items.append(art)
    return items


def fetch_rss_news():
    create_database()

    articles = []
    for name, url in RSS_FEEDS.items():
        print(f"RSS: {name}")
        articles.extend(parse_feed(url, name))

    # фильтр ключевых слов
    hits = []
    for a in articles:
        text = (
            (a.get("title") or "")
            + " "
            + (a.get("description") or "")
            + " "
            + (a.get("content") or "")
        ).lower()
        if any(
            k in text
            for k in ["trump", "putin", "xi jinping", " xi "]
        ):
            hits.append(a)

    print(f"Найдено {len(hits)} релевантных статей")
    trump, putin, xi, mixed = categorize_news(hits)

    save_news_to_db(trump, "Trump")
    save_news_to_db(putin, "Putin")
    save_news_to_db(xi, "Xi")
    save_news_to_db(mixed, "Mixed")

    remove_duplicates()
    print("✅ RSS парсинг завершён")


if __name__ == "__main__":
    fetch_rss_news()

