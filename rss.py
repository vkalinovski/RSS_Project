import feedparser
from datetime import datetime
from database import create_database, categorize_news, save_news_to_db, remove_duplicates

RSS_FEEDS = {
    "NY Times Politics":   "https://rss.nytimes.com/services/xml/rss/nyt/Upshot.xml",
    # ... другие ленты по вкусу
}

def parse_feed(url, name):
    feed = feedparser.parse(url)
    out = []
    for e in feed.entries:
        dt = None
        if e.get("published_parsed"):
            dt = datetime(*e.published_parsed[:6]).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        out.append({
            "source": feed.feed.get("title", name),
            "title":   e.get("title","").strip(),
            "url":     e.get("link","").strip(),
            "publishedAt": dt,
            "content": e.get("content",[{"value":""}])[0]["value"].strip() if e.get("content") else e.get("description","").strip(),
            "description": e.get("description","").strip(),
            "author":  e.get("author","").strip() if e.get("author") else None
        })
    return out

def fetch_rss_news():
    create_database()
    all_arts = []
    for name, url in RSS_FEEDS.items():
        print("Парсим", name)
        all_arts.extend(parse_feed(url, name))

    # Оставляем только статьи с нашими ключевыми словами
    filtered = []
    for a in all_arts:
        txt = (a["title"] + a.get("description","") + a.get("content","")).lower()
        if any(w in txt for w in ["trump","putin","xi jinping"]):
            filtered.append(a)
    print(f"Найдено {len(filtered)} статей в RSS")

    t,p,x,m = categorize_news(filtered)
    save_news_to_db(t, "Trump")
    save_news_to_db(p, "Putin")
    save_news_to_db(x, "Xi Jinping")
    save_news_to_db(m, "Multiple")
    remove_duplicates()

if __name__ == "__main__":
    fetch_rss_news()
