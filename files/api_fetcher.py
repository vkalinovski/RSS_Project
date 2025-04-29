# -*- coding: utf-8 -*-
"""
Загрузка статей из NewsAPI (последние 30 дней).
NEWSAPI_KEY берётся из .env (или переменной окружения).
news.db сохраняется по пути DB_PATH (см. database.py).
"""

import os, sys, requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from database import create, categorize, save

load_dotenv()
KEY = os.getenv("NEWSAPI_KEY")
if not KEY:
    sys.exit("❌ NEWSAPI_KEY не найден в .env")

URL = "https://newsapi.org/v2/everything"
HEAD = {"Authorization": KEY}

POLIT = {"Trump": "Trump", "Putin": "Putin", "Xi": '"Xi Jinping"'}
SPAN_DAYS = 30
PAGE_SIZE = 100
MAX_PAGES = 5          # 5×100 = 500 статей на персона

def to_std(a: dict, who: str) -> dict:
    return {
        "source": a["source"]["name"],
        "title": a.get("title") or "",
        "url": a.get("url"),
        "publishedAt": a.get("publishedAt"),
        "content": a.get("content") or a.get("description", ""),
        "politician": who,
    }

def fetch(query: str):
    fr = (datetime.utcnow() - timedelta(days=SPAN_DAYS)).strftime("%Y-%m-%d")
    to = datetime.utcnow().strftime("%Y-%m-%d")
    params = dict(q=query, from_param=fr, to=to,
                  language="en", sortBy="publishedAt", pageSize=PAGE_SIZE)
    arts = []
    for page in range(1, MAX_PAGES+1):
        params["page"] = page
        r = requests.get(URL, headers=HEAD, params=params, timeout=30)
        if r.status_code != 200:
            print("NewsAPI error:", r.text); break
        chunk = r.json().get("articles", [])
        if not chunk: break
        arts.extend(chunk)
        if len(chunk) < PAGE_SIZE: break
    return arts

def main():
    create()
    rows = []
    for who, q in POLIT.items():
        raw = fetch(q)
        print(f"{who}: {len(raw)} статей")
        rows.extend(to_std(a, who) for a in raw)
    for bucket in categorize(rows).values():
        save(bucket)

if __name__ == "__main__":
    main()
