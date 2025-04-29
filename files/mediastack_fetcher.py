# -*- coding: utf-8 -*-
"""
Исторический сборщик Mediastack (FREE-plan).

• диапазон: 01-09-2024 … today  
• 1 запрос на месяц × 3 персоны → 24 calls (<500/мес)  
• пауза 1 сек, чтобы не нарваться на rate-limit
"""

import calendar, os, sys, time, requests
from datetime import date
from dotenv import load_dotenv

from database import create, categorize, save

# ─── 1. ключ API ────────────────────────────────────────────
load_dotenv()
KEY = os.getenv("MEDIASTACK_KEY")
if not KEY:
    sys.exit("❌ MEDIASTACK_KEY не найден (.env или env-var)")

# ─── 2. константы ───────────────────────────────────────────
START = date(2024, 9, 1)
TODAY  = date.today()

PEOPLE = {
    "Trump": "Trump",
    "Putin": "Putin",
    "Xi":    '"Xi Jinping"',
}

URL  = "http://api.mediastack.com/v1/news"
BASE = dict(
    access_key=KEY,
    languages="en,ru",
    sort="published_desc",
    limit=100,
)

# ─── 3. вспомогательные функции ────────────────────────────
def month_range():
    """Генератор (first_day, last_day) для всех месяцев между START…TODAY"""
    y, m = START.year, START.month
    while date(y, m, 1) <= TODAY:
        last = calendar.monthrange(y, m)[1]
        yield date(y, m, 1), date(y, m, last)
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)

def fetch(q: str, frm: date, to: date):
    params = BASE | {"keywords": q, "date": f"{frm},{to}"}
    r = requests.get(URL, params=params, timeout=25)
    if r.status_code != 200:
        print("⚠️ Mediastack error", r.text[:120])
        return []
    return r.json().get("data", [])

def std(a: dict, person: str) -> dict:
    """Приводим ответ Mediastack к единому формату"""
    return dict(
        source=a.get("source") or "",
        title=a.get("title") or "",
        url=a.get("url"),
        publishedAt=a.get("published_at"),
        content=a.get("description") or "",
        politician=person,
    )

# ─── 4. main ETL ────────────────────────────────────────────
def main():
    create()
    rows = []
    for person, query in PEOPLE.items():
        for frm, to in month_range():
            data = fetch(query, frm, to)
            print(f"{person} {frm:%Y-%m}: {len(data)}")
            rows.extend(std(a, person) for a in data)
            time.sleep(1.1)       # 1 call/sec — безопасный запас
    for bunch in categorize(rows).values():
        save(bunch)

if __name__ == "__main__":
    main()
