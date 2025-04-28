import sqlite3
from pathlib import Path
from datetime import datetime
import re   #  ← добавили

# Путь к базе данных
db_path = Path(__file__).parent / "news.db"


def create_database():
    """
    Создаёт таблицу news, если её ещё нет.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
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
    """
    )

    conn.commit()
    conn.close()
    print("Таблица news создана (если она ещё не существовала)!")


def get_last_saved_date():
    """
    Возвращает дату самой свежей статьи в базе данных (в формате "YYYY-MM-DD").
    Если записей нет, возвращает None.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(published_at) FROM news")
    last_date = cursor.fetchone()[0]

    conn.close()
    return None if not last_date else last_date.split(" ")[0]  # убираем время


def clean_value(value):
    return value if value and value.strip() else None


def fix_date_format(date_str: str | None) -> str:
    """
    Преобразует дату вида 2024-12-02T05:21:57+00:00 к
    виду 2024-12-02 05:21:57 (SQLite).
    """
    if not date_str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        date_str = date_str.split("+")[0]  # убираем смещение
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S").strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    except ValueError:
        print(f"⚠️  Неверный формат даты: {date_str}")
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def save_news_to_db(news: list[dict], category: str):
    """
    Сохраняет список статей в БД, игнорируя уже существующие по URL.
    """
    if not news:
        return

    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()

    saved = 0
    for art in news:
        url = art["url"]

        source = art.get("source")
        if isinstance(source, dict):
            source = source.get("name")

        published_at = fix_date_format(art.get("publishedAt"))

        try:
            cursor.execute(
                """
                INSERT OR IGNORE INTO news
                (source, title, url, published_at, content, author, politician)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    source,
                    clean_value(art.get("title")),
                    url,
                    published_at,
                    clean_value(art.get("content")),
                    clean_value(art.get("author")),
                    category,
                ),
            )
            saved += cursor.rowcount
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")

    conn.commit()
    conn.close()
    print(f"Сохранено {saved} новых статей в категорию {category!r}")


# ---------- НОВАЯ КАТЕГОРИЗАЦИЯ ---------- #
KEYWORDS = {
    "Trump": [r"\btrump\b"],
    "Putin": [r"\bputin\b"],
    "Xi": [r"\bxi\s+j(i|inping)\b", r"\bxi\bjinping\b"],
}


def categorize_news(news: list[dict]):
    """
    Делит статьи на списки Trump / Putin / Xi / Mixed.
    Возвращает кортеж из четырёх списков.
    """
    trump, putin, xi, mixed = [], [], [], []

    for art in news:
        text = (
            (art.get("title") or "")
            + " "
            + (art.get("description") or "")
            + " "
            + (art.get("content") or "")
        ).lower()

        hits = {
            name
            for name, patterns in KEYWORDS.items()
            if any(re.search(p, text) for p in patterns)
        }

        if hits == {"Trump"}:
            trump.append(art)
        elif hits == {"Putin"}:
            putin.append(art)
        elif hits == {"Xi"}:
            xi.append(art)
        elif hits:  # упомянуты 2+
            mixed.append(art)

    return trump, putin, xi, mixed
# ----------------------------------------- #


def remove_duplicates():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        DELETE FROM news
        WHERE id NOT IN (SELECT MIN(id) FROM news GROUP BY title, url)
    """
    )
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM news")
    print(f"После удаления дубликатов осталось {cursor.fetchone()[0]} записей")
    conn.close()


if __name__ == "__main__":
    create_database()
