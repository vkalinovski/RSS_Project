import os, requests, json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from database import categorize, save_news_to_db

load_dotenv()
KEY = os.getenv("NEWSAPI_KEY")

POLITICIANS = {"Trump":"Trump","Putin":"Putin","Xi":'"Xi Jinping"'}
URL  = "https://newsapi.org/v2/everything"
HEAD = {"Authorization": KEY}
DATE_FROM = (datetime.utcnow()-timedelta(days=30)).strftime("%Y-%m-%d")
DATE_TO   =  datetime.utcnow().strftime("%Y-%m-%d")

def fetch(q):
    params = dict(q=q,from_param=DATE_FROM,to=DATE_TO,
                  language="en",sortBy="publishedAt",pageSize=100,page=1)
    arts=[]
    for p in range(1,6):
        params["page"]=p
        r=requests.get(URL,headers=HEAD,params=params,timeout=30)
        if r.status_code!=200: break
        chunk=r.json().get("articles",[])
        if not chunk: break
        arts+=chunk
        if len(chunk)<100: break
    return [{"source":a["source"],"title":a["title"],"url":a["url"],
             "publishedAt":a["publishedAt"],
             "content":a.get("content") or a.get("description",""),
             "author":a.get("author")} for a in arts]

def main():
    all=[]
    for name,q in POLITICIANS.items():
        rows=fetch(q); print(name,len(rows))
        all+=rows
    trump,putin,xi,mixed=categorize(all)
    save_news_to_db(trump,"Trump")
    save_news_to_db(putin,"Putin")
    save_news_to_db(xi,"Xi")
    save_news_to_db(mixed,"Mixed")

if __name__=="__main__": main()
