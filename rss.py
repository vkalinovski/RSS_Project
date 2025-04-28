import feedparser
from datetime import datetime
from database import (
    create_database, save_news_to_db,
    categorize_news, remove_duplicates
)

RSS_FEEDS = {
    "NY Times Politics":      "https://rss.nytimes.com/services/xml/rss/nyt/Upshot.xml",
    "Politico":               "http://www.politico.com/rss/Top10Blogs.xml",
    "Washington Post":        "http://feeds.washingtonpost.com/rss/politics",
    "Fox News Latest":        "http://feeds.foxnews.com/foxnews/latest?format=xml",
    "BBC Politics":           "http://feeds.bbci.co.uk/news/politics/rss.xml",
    "РИА Политика":           "https://ria.ru/export/rss2/politics/index.xml",
    "ТАСС":                   "https://tass.ru/rss/v2.xml",
    "RT English":             "https://www.rt.com/rss/news/",
    "Xinhua":                 "http://www.xinhuanet.com/english/rss/worldrss.xml",
    "China Daily":            "https://www.chinadaily.com.cn/rss/china_rss.xml",
}

def parse(url, source):
    feed = feedparser.parse(url)
    arts = []
    for e in feed.entries:
        if "published_parsed" not in e or not e.published_parsed:
            continue  # без даты пропускаем
        dt = datetime(*e.published_parsed[:6])
        arts.append(
            dict(
                source=source,
                title=e.get("title", "").strip(),
                url=e.get("link", "").strip(),
                publishedAt=dt.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
                content=e.get("content", [{}])[0].get("value", "").strip(),
                description=e.get("description", "").strip(),
                author=e.get("author", "").strip() if e.get("author") else None,
            )
        )
    return arts

def fetch_rss_news():
    create_database()
    all_arts = []
    for name, url in RSS_FEEDS.items():
        print("RSS:", name)
        all_arts.extend(parse(url, name))

    kw = ["trump", "putin", "xi jinping", " xi "]
    filtered = [
        a for a in all_arts
        if any(k in (a["title"] + " " + a["description"] + " " + a["content"]).lower() for k in kw)
    ]
    print("Найдено", len(filtered), "релевантных статей")

    trump, putin, xi, mixed = categorize_news(filtered)
    save_news_to_db(trump, "Trump")
    save_news_to_db(putin, "Putin")
    save_news_to_db(xi,    "Xi")
    save_news_to_db(mixed, "Mixed")
    remove_duplicates()
    print("✅  RSS обработан")

if __name__ == "__main__":
    fetch_rss_news()
