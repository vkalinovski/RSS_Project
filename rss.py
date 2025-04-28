import feedparser, re
from datetime import datetime
from database import categorize, save_news_to_db

RSS = {
 "NYT Politics":"https://rss.nytimes.com/services/xml/rss/nyt/Upshot.xml",
 "Politico":"http://www.politico.com/rss/Top10Blogs.xml",
 "WP Politics":"http://feeds.washingtonpost.com/rss/politics",
 "Fox":"http://feeds.foxnews.com/foxnews/latest?format=xml",
 "BBC":"http://feeds.bbci.co.uk/news/politics/rss.xml",
 "РИА":"https://ria.ru/export/rss2/politics/index.xml",
 "ТАСС":"https://tass.ru/rss/v2.xml",
 "RT":"https://www.rt.com/rss/news/",
 "Xinhua":"http://www.xinhuanet.com/english/rss/worldrss.xml",
 "ChinaDaily":"https://www.chinadaily.com.cn/rss/china_rss.xml",
}

def parse(url,src):
    f=feedparser.parse(url); out=[]
    for e in f.entries:
        if not getattr(e,"published_parsed",None): continue
        dt=datetime(*e.published_parsed[:6]).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        out.append(dict(source=src,title=e.title, url=e.link, publishedAt=dt,
                        content=e.get("content",[{}])[0].get("value",""),
                        description=e.get("description",""),author=e.get("author")))
    return out

def main():
    all=[]
    for n,u in RSS.items(): all+=parse(u,n)
    kw=r"(trump|putin|xi\s+j(?:i|inping))"
    flt=[a for a in all if re.search(kw,(a["title"]+" "+a["content"]).lower())]
    t,p,x,m=categorize(flt)
    save_news_to_db(t,"Trump"); save_news_to_db(p,"Putin")
    save_news_to_db(x,"Xi");    save_news_to_db(m,"Mixed")

if __name__=="__main__": main()
