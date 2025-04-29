# -*- coding: utf-8 -*-
"""
Один модуль — все операции с SQLite.

▪ путь к базе задаётся env DB_PATH  
▪ если переменная не задана — news.db рядом со скриптом
"""

import os, re, sqlite3
from datetime import datetime
from pathlib import Path

DB = Path(os.getenv("DB_PATH", Path(__file__).parent / "news.db"))

# ─── создание таблицы (если ещё нет) ───────────────────────
def create() -> None:
    DB.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB) as c:
        c.execute(
            """CREATE TABLE IF NOT EXISTS news (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   source TEXT,
                   title TEXT,
                   url TEXT UNIQUE,
                   published_at TEXT,
                   content TEXT,
                   politician TEXT,
                   sentiment TEXT
               )"""
        )

# ─── унификация дат ────────────────────────────────────────
def fix_date(raw: str | None) -> str:
    """ISO → 'YYYY-MM-DD HH:MM:SS' или текущий момент, если что-то пошло не так."""
    if not raw:
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    raw = raw.rstrip("Z")
    if "+" in raw: raw = raw.split("+")[0]
    if "." in raw: raw = raw.split(".")[0]
    try:
        return datetime.strptime(raw, "%Y-%m-%dT%H:%M:%S") \
                       .strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

# ─── вставка статей ─────────────────────────────────────────
def save(rows: list[dict]) -> None:
    if not rows: return
    create()
    with sqlite3.connect(DB) as c:
        cur = c.cursor()
        n = 0
        for a in rows:
            cur.execute(
                """INSERT OR IGNORE INTO news
                   (source, title, url, published_at, content, politician)
                   VALUES (?,?,?,?,?,?)""",
                (
                    a["source"],
                    a["title"],
                    a["url"],
                    fix_date(a["publishedAt"]),
                    a["content"],
                    a["politician"],
                ),
            )
            n += cur.rowcount
        if n:
            print(f"✓ сохранено новых статей: {n}")

# ─── детект имен в тексте ──────────────────────────────────
PATTERNS = {
    "Trump": re.compile(r"\btrump\b", re.I),
    "Putin": re.compile(r"\bputin\b", re.I),
    "Xi":    re.compile(r"\bxi\s+j(?:i|inping)\b|\bxi\bjinping\b", re.I),
}

def categorize(rows: list[dict]) -> dict[str, list[dict]]:
    """
    Разбивает список статей на 4 корзины:
    Trump / Putin / Xi / Mixed (если упоминается ≥2 имён).
    """
    outs = {k: [] for k in ["Trump", "Putin", "Xi", "Mixed"]}
    for a in rows:
        text = " ".join((a.get("title", ""), a.get("content", ""))).lower()
        hit = {p for p, pat in PATTERNS.items() if pat.search(text)}
        if   hit == {"Trump"}: outs["Trump"].append(a)
        elif hit == {"Putin"}: outs["Putin"].append(a)
        elif hit == {"Xi"}:    outs["Xi"].append(a)
        elif hit:              outs["Mixed"].append(a)
    return outs
