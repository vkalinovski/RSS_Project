# -*- coding: utf-8 -*-
"""
Исторический сборщик Mediastack (FREE-plan).

• Берёт данные с 01-09-2024 до today  (UTC)
• По 1 запросу на месяц × 3 политики  →  24 calls  (< 500/мес)
• Соблюдает лимит 1 call / second  (time.sleep).

.env  ─ MEDIASTACK_KEY
env   ─ DB_PATH    (опц.)
"""

import os, sys, requests, calendar, time
from datetime import datetime, date
from dotenv import load_dotenv
from database import create, categorize, save

load_dotenv()
KEY = os.getenv("MEDIASTACK_KEY")
if not KEY:
    sys.exit("❌ MEDIASTACK_KEY не найден")

START = date(2024, 9, 1)
TODAY  = date.today()

POLIT = {
    "Trump": "Trump",
    "Putin": "Putin",
    "Xi":    '"Xi Jinping"',
}

URL  = "http://api.mediastack.com/v1/news"
BASE = dict(
    access_key = KEY,
    languages  = "en,ru",
    sort       = "published_desc",
    limit      = 100,          # 1-shot, без пагинации
)

def month_pairs():
    y, m = START.year, START.month
    while date(y, m, 1) <= TODAY:
        yield date(y, m, 1), date(y, m, calendar.monthrange(y, m)[1])
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)

def fetch(q: str, since: date, until: date):
    params = BASE | {
        "keywords": q,
        "date": f"{since},{until}",
    }
    r = requests.get(URL, params=params, timeout=25)
    if r.status_code != 200:
        print("Mediastack error:", r.text)
        return []
    return r.json().get("data", [])

def std(a: dict, who: str) -> dict:
    return {
        "source": a.get("source") or "",
        "title":  a.get("title")  or "",
        "url":    a.get("url"),
        "publishedAt": a.get("published_at"),
        "content": a.get("description") or "",
        "politician": who,
    }

def main():
    create()
    rows = []
    for who, q in POLIT.items():
        for fr, to in month_pairs():
            data = fetch(q, fr, to)
            print(f"{who} {fr:%Y-%m}: {len(data)}")
            rows.extend(std(a, who) for a in data)
            time.sleep(1.2)          # соблюдаем 1 req/sec
    for bucket in categorize(rows).values():
        save(bucket)

if __name__ == "__main__":
    main()
