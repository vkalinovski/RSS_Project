"""
Определяет тональность новостей и записывает в колонку sentiment.
Приводит текст к 512 символам, чтобы избежать ошибки размера тензора.
"""

import sqlite3
from pathlib import Path
from transformers import pipeline
from tqdm import tqdm

DB_PATH = Path(__file__).parent / "news.db"
MAX_LEN = 512         # не больше 512 символов
BATCH = 8             # пакет для инференса

sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
    device_map="auto",
)

def load_unprocessed():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, title, content FROM news WHERE sentiment IS NULL")
    rows = cur.fetchall()
    conn.close()
    return rows

def update_sentiment(rows):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    for i in tqdm(range(0, len(rows), BATCH), desc="Sentiment"):
        batch = rows[i : i + BATCH]
        texts = [
            ((t or "") + " " + (c or ""))[:MAX_LEN]  # обрезаем
            for _, t, c in batch
        ]
        preds = sentiment_analyzer(texts)

        for (news_id, _, _), pred in zip(batch, preds):
            label = pred["label"].lower()
            sentiment = (
                "positive"
                if "positive" in label
                else "negative"
                if "negative" in label
                else "neutral"
            )
            cur.execute(
                "UPDATE news SET sentiment = ? WHERE id = ?",
                (sentiment, news_id),
            )
        conn.commit()
    conn.close()

def main():
    rows = load_unprocessed()
    if not rows:
        print("✅  Все новости уже имеют тональность")
        return
    print(f"📊  Обработаем {len(rows)} статей")
    update_sentiment(rows)
    print("✅  Тональность сохранена")

if __name__ == "__main__":
    main()

