# -*- coding: utf-8 -*-
"""
Выгрузка статей из NewsAPI для трёх политиков.
Диапазон фиксированный: с 1 сентября 2024 года по today (+UTC).

NEWSAPI_KEY берётся из .env или переменной окружения.
news.db создаётся/обновляется по пути DB_PATH (см. database.py).
"""

import os, sys, requests
from datetime import datetime
from dotenv import load_dotenv
from database import create, categorize, save

# ─────────────────── константы ───────────────────
START_DATE = datetime(2024, 9, 1)                 # ← ваша «точка ноль»
POLIT = {
    "Trump": "Trump",
    "Putin": "Putin",
    "Xi":    '"Xi Jinping"',
}
PAGE_SIZE  = 100
MAX_PAGES  = 40                                   # 40×100 ≈ 4 000 статей/персону
URL  = "https://newsapi.org/v2/everything"

# ─────────────────── key & headers ───────────────
load_dotenv()
KEY = os.getenv("NEWSAPI_KEY")
if not KEY:
    sys.exit("❌ NEWSAPI_KEY не найден в .env")
HEAD = {"Authorization": KEY}

# ─────────────────── helpers ──────────────────────
def to_std(a: dict, who: str) -> dict:
    return {
        "source": a["source"]["name"],
        "title": a.get("title", "") or "",
        "url": a.get("url"),
        "publishedAt": a.get("publishedAt"),
        "content": a.get("content") or a.get("description", ""),
        "politician": who,
    }

def fetch(query: str):
    fr = START_DATE.strftime("%Y-%m-%d")
    to = datetime.utcnow().strftime("%Y-%m-%d")
    params = dict(q=query, from_param=fr, to=to,
                  language="en", sortBy="publishedAt",
                  pageSize=PAGE_SIZE)
    arts = []
    for pg in range(1, MAX_PAGES + 1):
        params["page"] = pg
        r = requests.get(URL, headers=HEAD, params=params, timeout=30)
        if r.status_code != 200:
            print("NewsAPI error:", r.text); break
        chunk = r.json().get("articles", [])
        if not chunk: break
        arts.extend(chunk)
        if len(chunk) < PAGE_SIZE: break
    return arts

# ─────────────────── main ─────────────────────────
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

