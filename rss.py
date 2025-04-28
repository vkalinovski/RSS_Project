"""
Парсит RSS-ленты, выбирает статьи о Трампе, Путине, Си.
"""

import feedparser
from datetime import datetime
from database import create, categorize, save

FEEDS = {
    "NYT Politics":          "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml",
    "BBC Politics":          "http://feeds.bbci.co.uk/news/politics/rss.xml",
    "Politico":              "http://www.politico.com/rss/Top10Blogs.xml",
    "Washington Post":       "http://feeds.washingtonpost.com/rss/politics",
    "FoxNews":               "http://feeds.foxnews.com/foxnews/latest?format=xml",
    "РИА":                   "https://ria.ru/export/rss2/politics/index.xml",
    "ТАСС":                  "https://tass.ru/rss/v2.xml",
    "RT":                    "https://www.rt.com/rss/news/",
    "Xinhua":                "http://www.xinhuanet.com/english/rss/worldrss.xml",
    "China Daily":           "https://www.chinadaily.com.cn/rss/china_rss.xml",
}

def iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")

def parse(url, src):
    f = feedparser.parse(url)
    rows=[]
    for e in f.entries:
        if not getattr(e,"published_parsed",None): continue
        dt = datetime(*e.published_parsed[:6])
        rows.append(
            dict(
                source=src,
                title=e.get("title",""),
                url=e.get("link",""),
                publishedAt=iso(dt),
                content=(e.get("content",[{}])[0].get("value") or e.get("summary","")),
            )
        )
    return rows

def main():
    create()
    rows=[]
    for name,url in FEEDS.items():
        rows.extend(parse(url,name))
    buckets = categorize(rows)
    for bunch in buckets.values(): save(bunch)

if __name__=="__main__":
    main()

