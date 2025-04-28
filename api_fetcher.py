"""
Скачивает новости за последние 30 дней из NewsAPI.
Требуется переменная окружения NEWSAPI_KEY (файл .env).
"""

import os, requests, json, sys
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from database import create, categorize, save

load_dotenv()
KEY = os.getenv("NEWSAPI_KEY")
URL = "https://newsapi.org/v2/everything"
HEAD = {"Authorization": KEY}

POLITICIANS = {"Trump": "Trump", "Putin": "Putin", "Xi": '"Xi Jinping"'}
SPAN = 30                    # дней
PAGE = 100                   # макс. размер страницы
MAX_PAGES = 5                # 5×100=500 статей/персону

def std(a: dict, who: str) -> dict:
    return {
        "source": a["source"]["name"],
        "title":  a.get("title") or "",
        "url":    a.get("url"),
        "publishedAt": a.get("publishedAt"),
        "content": a.get("content") or a.get("description",""),
        "politician": who,
    }

def fetch(q: str):
    frm = (datetime.utcnow()-timedelta(days=SPAN)).strftime("%Y-%m-%d")
    to  =  datetime.utcnow().strftime("%Y-%m-%d")
    params = dict(q=q, from_param=frm, to=to,
                  language="en", sortBy="publishedAt",
                  pageSize=PAGE)
    arts=[]
    for p in range(1, MAX_PAGES+1):
        params["page"]=p
        r = requests.get(URL, headers=HEAD, params=params, timeout=30)
        if r.status_code!=200:
            print("NewsAPI error", r.json()); break
        chunk = r.json().get("articles",[])
        if not chunk: break
        arts.extend(chunk)
        if len(chunk)<PAGE: break
    return arts

def main():
    create()
    all_rows=[]
    for who,q in POLITICIANS.items():
        raw = fetch(q)
        print(who, len(raw))
        all_rows.extend(std(a,who) for a in raw)
    buckets = categorize(all_rows)
    for rows in buckets.values(): save(rows)

if __name__=="__main__":
    if not KEY: sys.exit("❌ NEWSAPI_KEY не найден в .env")
    main()
