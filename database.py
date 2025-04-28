import sqlite3
from pathlib import Path
import os
from datetime import datetime

# Путь к папке с данными на Google Drive
DATA_DIR = Path(os.getenv("DATA_PATH", "/content/drive/MyDrive/test"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
db_path = DATA_DIR / "news.db"

def create_database():
    """Создаёт таблицу news, если её ещё нет."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            title TEXT,
            url TEXT UNIQUE NOT NULL,
            published_at TEXT,
            content TEXT,
            author TEXT,
            politician TEXT NOT NULL,
            sentiment TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("Таблица news готова.")

def get_last_saved_date():
    """
    Возвращает дату самой свежей статьи в базе (YYYY-MM-DD),
    или None, если записей нет.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(published_at) FROM news")
    last_date = cursor.fetchone()[0]
    conn.close()
    if not last_date:
        return None
    return last_date.split(" ")[0]

def clean_value(value):
    return value if value and value.strip() else None

def fix_date_format(date_str):
    """Преобразует ISO-строку в формат SQLite."""
    if not date_str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        # Убираем смещение часового пояса
        base = date_str.split("+")[0].replace("Z", "")
        dt = datetime.fromisoformat(base)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def save_news_to_db(news, category):
    """Сохраняет список статей с категорией (Trump/Putin/Xi Jinping/Multiple)."""
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()
    saved = 0
    for art in news:
        src = art.get("source")
        if isinstance(src, dict):
            src = src.get("name")
        published = fix_date_format(art.get("publishedAt"))
        title = clean_value(art.get("title"))
        content = clean_value(art.get("content"))
        author = clean_value(art.get("author"))

        try:
            cursor.execute('''
                INSERT OR IGNORE INTO news 
                  (source, title, url, published_at, content, author, politician)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (src, title, art["url"], published, content, author, category))
            if cursor.rowcount > 0:
                saved += 1
        except sqlite3.Error as e:
            print("DB Error:", e)

    conn.commit()
    conn.close()
    print(f"  → Сохранено {saved} статей для {category}")

def categorize_news(news):
    """
    Разбивает список статей на четыре категории:
    Trump, Putin, Xi Jinping, Multiple (если упоминаются ≥2).
    """
    trump, putin, xi, multi = [], [], [], []
    for art in news:
        text = (
            (art.get("title") or "") + " " +
            (art.get("description") or "") + " " +
            (art.get("content") or "")
        ).lower()
        m_tr = "trump" in text
        m_pt = "putin" in text
        m_xj = "xi jinping" in text
        count = sum([m_tr, m_pt, m_xj])
        if count == 1:
            if m_tr:   trump.append(art)
            if m_pt:   putin.append(art)
            if m_xj:   xi.append(art)
        elif count > 1:
            multi.append(art)
    return trump, putin, xi, multi

def remove_duplicates():
    """Удаляет дубликаты по title+url."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM news
        WHERE id NOT IN (
            SELECT MIN(id) FROM news GROUP BY title, url
        )
    """)
    conn.commit()
    conn.close()
    print("Дубликаты удалены.")

