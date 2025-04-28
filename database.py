import sqlite3
from pathlib import Path
from datetime import datetime
import re

DB_PATH = Path(__file__).parent / "news.db"

# ---------- создание таблицы ----------
def create_database():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source      TEXT,
                title       TEXT,
                url         TEXT UNIQUE NOT NULL,
                published_at TEXT,
                content     TEXT,
                author      TEXT,
                politician  TEXT NOT NULL,
                sentiment   TEXT
            )
        """
        )
    print("Таблица news создана (если не была)")

# ---------- helpers ----------
def clean(val):  # заменяем "" на None
    return val if val and val.strip() else None

def fix_date_format(ds: str | None) -> str:
    """
    Приводит ISO-8601 к  'YYYY-MM-DD HH:MM:SS'.
    Поддержка суффиксов Z, +00:00, +0300 и долей секунд.
    """
    if not ds:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        ds = ds.rstrip("Z")
        if "+" in ds:
            ds = ds.split("+")[0]
        if "." in ds:
            ds = ds.split(".")[0]
        return datetime.strptime(ds, "%Y-%m-%dT%H:%M:%S").strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    except ValueError:
        print(f"⚠️  Неверный формат даты: {ds}")
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ---------- сохранение ----------
def save_news_to_db(arts: list[dict], category: str):
    if not arts:
        return
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        saved = 0
        for a in arts:
            cur.execute(
                """
                INSERT OR IGNORE INTO news
                (source,title,url,published_at,content,author,politician)
                VALUES (?,?,?,?,?,?,?)
                """,
                (
                    a.get("source", {}).get("name") if isinstance(a.get("source"), dict) else a.get("source"),
                    clean(a.get("title")),
                    a["url"],
                    fix_date_format(a.get("publishedAt")),
                    clean(a.get("content")),
                    clean(a.get("author")),
                    category,
                ),
            )
            saved += cur.rowcount
        conn.commit()
    print(f"Сохранено {saved} новых статей в категорию '{category}'")

# ---------- дубликаты ----------
def remove_duplicates():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            DELETE FROM news
            WHERE id NOT IN (
                SELECT MIN(id) FROM news GROUP BY title, url
            )
        """
        )
        n = conn.execute("SELECT COUNT(*) FROM news").fetchone()[0]
    print("После удаления дубликатов осталось", n, "записей")

# ---------- категоризация ----------
KEYWORDS = {
    "Trump": [r"\btrump\b"],
    "Putin": [r"\bputin\b"],
    "Xi":    [r"\bxi\s+j(?:i|inping)\b", r"\bxi\bjinping\b"],
}

def categorize_news(rows: list[dict]):
    trump, putin, xi, mixed = [], [], [], []
    for a in rows:
        text = (
            (a.get("title") or "")
            + " "
            + (a.get("description") or "")
            + " "
            + (a.get("content") or "")
        ).lower()
        hits = {
            name
            for name, pats in KEYWORDS.items()
            if any(re.search(pat, text) for pat in pats)
        }
        if hits == {"Trump"}:
            trump.append(a)
        elif hits == {"Putin"}:
            putin.append(a)
        elif hits == {"Xi"}:
            xi.append(a)
        elif hits:
            mixed.append(a)
    return trump, putin, xi, mixed

if __name__ == "__main__":
    create_database()

