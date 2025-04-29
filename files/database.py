# -*- coding: utf-8 -*-
"""
Общие функции работы с базой SQLite.
Путь к базе задаётся переменной окружения DB_PATH.
Если переменная не задана — берётся news.db в каталоге скрипта.
"""

import sqlite3, re, os
from pathlib import Path
from datetime import datetime

DB = Path(os.getenv("DB_PATH", Path(__file__).parent / "news.db"))

def create() -> None:
    """Создать таблицу news, если её ещё нет."""
    DB.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB) as c:
        c.execute(
            """CREATE TABLE IF NOT EXISTS news (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   source TEXT, title TEXT, url TEXT UNIQUE,
                   published_at TEXT, content TEXT,
                   politician TEXT, sentiment TEXT
               )"""
        )

# ─────────── дата ISO-8601 → YYYY-MM-DD HH:MM:SS ───────────
def fix_date(s: str | None) -> str:
    if not s:
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    s = s.rstrip("Z")
    if "+" in s: s = s.split("+")[0]
    if "." in s: s = s.split(".")[0]
    try:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S").strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    except ValueError:
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

# ─────────── сохранение статей ───────────
def save(rows: list[dict]) -> None:
    if not rows: return
    create()                          # гарантия, что таблица есть
    with sqlite3.connect(DB) as c:
        n = 0
        for a in rows:
            c.execute(
                """INSERT OR IGNORE INTO news
                   (source,title,url,published_at,content,politician)
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
            n += c.total_changes
        print(f"✓ {n} новых статей сохранено")

# ─────────── категоризация ───────────
PATTERNS = {
    "Trump": re.compile(r"\btrump\b", re.I),
    "Putin": re.compile(r"\bputin\b", re.I),
    "Xi":    re.compile(r"\bxi\s+j(?:i|inping)\b|\bxi\bjinping\b", re.I),
}

def categorize(rows: list[dict]):
    outs = {k: [] for k in ["Trump", "Putin", "Xi", "Mixed"]}
    for a in rows:
        text = " ".join((a.get("title", ""), a.get("content", ""))).lower()
        hit = {p for p, pat in PATTERNS.items() if pat.search(text)}
        if   hit == {"Trump"}: outs["Trump"].append(a)
        elif hit == {"Putin"}: outs["Putin"].append(a)
        elif hit == {"Xi"}:    outs["Xi"].append(a)
        elif hit:              outs["Mixed"].append(a)
    return outs
