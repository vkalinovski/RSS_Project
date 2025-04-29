# -*- coding: utf-8 -*-
"""
Добавляет колонку sentiment в news.db с помощью NLTK-VADER.
"""

import sqlite3, os, nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from tqdm import tqdm
from pathlib import Path
from database import create

DB = Path(os.getenv("DB_PATH", Path(__file__).parent / "news.db"))
create()

nltk.download("vader_lexicon", quiet=True)
vader = SentimentIntensityAnalyzer()

def main():
    with sqlite3.connect(DB) as c:
        rows = c.execute(
            "SELECT id,title,content FROM news WHERE sentiment IS NULL"
        ).fetchall()
        if not rows:
            print("✓ sentiment: nothing to do"); return

        upd = []
        for _id, title, cont in tqdm(rows, desc="sentiment"):
            txt = (title or "") + " " + (cont or "")
            sc = vader.polarity_scores(txt)["compound"]
            sent = "positive" if sc > 0.2 else "negative" if sc < -0.2 else "neutral"
            upd.append((sent, _id))
        c.executemany("UPDATE news SET sentiment=? WHERE id=?", upd)
        c.commit()
    print("✓ sentiment обновлён:", len(upd))

if __name__ == "__main__":
    main()
