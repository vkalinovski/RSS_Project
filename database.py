import sqlite3, re
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path("/content/drive/MyDrive/etst/RSS_Project")
ROOT_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH  = ROOT_DIR / "news.db"

def create_database():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS news(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              source TEXT, title TEXT, url TEXT UNIQUE,
              published_at TEXT, content TEXT, author TEXT,
              politician TEXT, sentiment TEXT
            )
        """)
    print("✓ таблица news OK")

def clean(x):  # "" → None
    return x if x and x.strip() else None

def fix_date(ds: str | None) -> str:
    if not ds:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ds = ds.rstrip("Z")
    if "+" in ds:
        ds = ds.split("+")[0]
    if "." in ds:
        ds = ds.split(".")[0]
    try:
        return datetime.strptime(ds, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        print("⚠ bad date:", ds)
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def save_news_to_db(rows: list[dict], cat: str):
    create_database()                          # <─- страховка
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        n = 0
        for a in rows:
            cur.execute("""
                INSERT OR IGNORE INTO news
                 (source,title,url,published_at,content,author,politician)
                 VALUES (?,?,?,?,?,?,?)
            """, (
                (a.get("source") or {}).get("name") if isinstance(a.get("source"), dict) else a.get("source"),
                clean(a.get("title")), a["url"], fix_date(a.get("publishedAt")),
                clean(a.get("content")), clean(a.get("author")), cat,
            ))
            n += cur.rowcount
        conn.commit()
    print(f"✓ {cat}: +{n}")

KEYS = {
    "Trump": [r"\btrump\b"],
    "Putin": [r"\bputin\b"],
    "Xi":    [r"\bxi\s+j(?:i|inping)\b", r"\bxi\bjinping\b"],
}
def categorize(rows):
    trump, putin, xi, mixed = [], [], [], []
    for a in rows:
        txt = ((a.get("title") or "")+" "+(a.get("description") or "")+" "+(a.get("content") or "")).lower()
        hit = {k for k,pats in KEYS.items() if any(re.search(p, txt) for p in pats)}
        (trump if hit=={"Trump"} else putin if hit=={"Putin"} else xi if hit=={"Xi"} else mixed if hit else None).append(a)
    return trump, putin, xi, mixed


