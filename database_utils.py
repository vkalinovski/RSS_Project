# -*- coding: utf-8 -*-
import os
import sqlite3
from pathlib import Path
from typing import List, Dict
from utils import now_utc

DRIVE   = "/content/gdrive/MyDrive/test"
DB_PATH = Path(DRIVE) / "news.db"

def create_database():
    """
    Создаёт таблицу news, если её нет.
    """
    os.makedirs(DRIVE, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            title TEXT,
            url TEXT UNIQUE NOT NULL,
            published_at TEXT,
            content TEXT,
            author TEXT,
            politician TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print(f"[{now_utc()}] БД готова: {DB_PATH}")

def clean_value(val: str) -> str:
    """Преобразует пустые строки в None"""
    return val.strip() if isinstance(val, str) and val.strip() else None

def fix_date_format(date_str: str) -> str:
    """
    Преобразует ISO8601 к 'YYYY-MM-DD HH:MM:SS'
    """
    from datetime import datetime
    if not date_str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        core   = date_str.split("+")[0]
        dt_obj = datetime.fromisoformat(core)
        return dt_obj.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        print(f"[{now_utc()}] Неправильный формат даты: {date_str}")
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def save_news_to_db(news: List[Dict], politician: str):
    """
    Сохраняет список новостей в БД с категорией politician.
    """
    conn  = sqlite3.connect(DB_PATH, check_same_thread=False)
    cur   = conn.cursor()
    saved = 0
    for art in news:
        src     = clean_value(art.get("source"))
        title   = clean_value(art.get("title"))
        url     = art.get("url")
        pub     = fix_date_format(art.get("published"))
        content = clean_value(art.get("content"))
        author  = clean_value(art.get("author"))
        try:
            cur.execute(
                "INSERT OR IGNORE INTO news "
                "(source,title,url,published_at,content,author,politician) "
                "VALUES (?,?,?,?,?,?,?)",
                (src, title, url, pub, content, author, politician)
            )
            if cur.rowcount:
                saved += 1
        except sqlite3.Error as e:
            print(f"[{now_utc()}] Ошибка вставки в БД: {e}")
    conn.commit()
    conn.close()
    print(f"[{now_utc()}] Сохранено {saved} статей для «{politician}»")

