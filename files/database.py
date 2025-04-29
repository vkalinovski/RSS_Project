import sqlite3, re
from pathlib import Path
from datetime import datetime

DB = Path(__file__).parent / "news.db"

def create():
    with sqlite3.connect(DB) as c:
        c.execute(
            """CREATE TABLE IF NOT EXISTS news (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   source TEXT, title TEXT, url TEXT UNIQUE,
                   published_at TEXT, content TEXT,
                   politician TEXT, sentiment TEXT
               )"""
        )

# ---------- дата ISO-8601 → YYYY-MM-DD HH:MM:SS ----------
def fix_date(s: str | None) -> str:
    if not s:
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    s = s.rstrip("Z")
    if "+" in s:
        s = s.split("+")[0]
    if "." in s:
        s = s.split(".")[0]
    try:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S").strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    except ValueError:
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

# ---------- сохранение ----------
def save(rows: list[dict]):
    if not rows:
        return
    with sqlite3.connect(DB) as c:
        cur = c.cursor()
        n = 0
        for a in rows:
            cur.execute(
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
            n += cur.rowcount
        print(f"✓ {n} новых статей сохранено")

# ---------- категоризация ----------
PATTERNS = {
    "Trump": re.compile(r"\btrump\b", re.I),
    "Putin": re.compile(r"\bputin\b", re.I),
    "Xi":    re.compile(r"\bxi\s+j(?:i|inping)\b|\bxi\bjinping\b", re.I),
}

def categorize(rows: list[dict]):
    outs = {k: [] for k in ["Trump", "Putin", "Xi", "Mixed"]}
    for a in rows:
        text = " ".join((a.get("title",""), a.get("content",""))).lower()
        hit = {p for p,pat in PATTERNS.items() if pat.search(text)}
        if   hit=={"Trump"}: outs["Trump"].append(a)
        elif hit=={"Putin"}: outs["Putin"].append(a)
        elif hit=={"Xi"}:    outs["Xi"].append(a)
        elif hit:            outs["Mixed"].append(a)
    return outs


