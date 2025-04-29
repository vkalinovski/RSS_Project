# -*- coding: utf-8 -*-
"""
Скачивает статьи c 1-го сентября 2024 до сегодня (UTC) из Mediastack,
классифицирует по политикам (Trump, Putin, Xi), сохраняет в news.db.

◼️  Переменная окружения / .env:  MEDIASTACK_KEY
◼️  news.db-путь берётся из env DB_PATH либо располагается рядом с файлом
"""

import os, sys, requests, calendar
from datetime import datetime, date
from pathlib import Path
from dotenv import load_dotenv
from database import create, categorize, save

# ─────────────────── 0. API-key ───────────────────
load_dotenv()
KEY = os.getenv("MEDIASTACK_KEY")
if not KEY:
    sys.exit("❌ MEDIASTACK_KEY не найден в .env")

# ─────────────────── 1. Константы ─────────────────
POLIT = {
    "Trump": "Trump",
    "Putin": "Putin",
    "Xi":    '"Xi Jinping"',
}
START = date(2024, 9, 1)
TODAY = date.today()

URL  = "http://api.mediastack.com/v1/news"
BASE = dict(
    access_key = KEY,
    languages  = "en,ru",
    sort       = "published_desc",
    limit      = 100,          # максимум free-плана
)

# ─────────────────── 2. Хелперы ───────────────────
def month_pairs():
    y, m = START.year, START.month
    while date(y, m, 1) <= TODAY:
        last = calendar.monthrange(y, m)[1]
        yield date(y, m, 1), date(y, m, last)
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)

def fetch(q: str, since: date, until: date):
    params = BASE | {
        "keywords": q,
        "date":     f"{since},{until}",
        "offset":   0,
    }
    arts = []
    while True:
        r = requests.get(URL, params=params, timeout=25)
        if r.status_code != 200:
            print("Mediastack error:", r.text); break
        chunk = r.json().get("data", [])
        if not chunk: break
        arts.extend(chunk)
        if len(chunk) < 100: break
        params["offset"] += 100
    return arts

def std(a: dict, who: str) -> dict:
    return {
        "source": a.get("source") or "",
        "title":  a.get("title")  or "",
        "url":    a.get("url"),
        "publishedAt": a.get("published_at"),
        "content": a.get("description") or "",
        "politician": who,
    }

# ─────────────────── 3. Main ──────────────────────
def main():
    create()
    rows = []
    for who, q in POLIT.items():
        for fr, to in month_pairs():
            chunk = fetch(q, fr, to)
            print(f"{who}  {fr:%Y-%m}: {len(chunk)}")
            rows.extend(std(a, who) for a in chunk)
    for bunch in categorize(rows).values():
        save(bunch)

if __name__ == "__main__":
    main()
