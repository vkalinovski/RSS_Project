"""
Оценивает тональность статей в news.db.
— pipeline вызывается с truncation=True, поэтому >512 токенов автоматически обрежутся;
— батч = 8, что ускоряет работу и экономит память.
"""

import sqlite3
from pathlib import Path
from transformers import pipeline
from tqdm import tqdm

DB_PATH = Path(__file__).parent / "news.db"
BATCH = 8

sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    tokenizer="distilbert-base-uncased-finetuned-sst-2-english",
    device_map="auto",
)

def fetch_unprocessed():
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute(
            "SELECT id, title, content FROM news WHERE sentiment IS NULL"
        ).fetchall()

def save_sentiments(updates):
    with sqlite3.connect(DB_PATH) as conn:
        conn.executemany(
            "UPDATE news SET sentiment = ? WHERE id = ?", updates
        )
        conn.commit()

def main():
    rows = fetch_unprocessed()
    if not rows:
        print("✅  Все новости уже размечены")
        return

    print(f"📊  Нужно разметить {len(rows)} статей")
    updates = []
    for i in tqdm(range(0, len(rows), BATCH), desc="Sentiment"):
        batch = rows[i : i + BATCH]
        texts = [
            ((t or "") + " " + (c or "")) for _, t, c in batch
        ]
        preds = sentiment_analyzer(texts, truncation=True)  # ← ключевой момент!

        for (news_id, _, _), pred in zip(batch, preds):
            label = pred["label"].lower()
            sentiment = (
                "positive" if "positive" in label else
                "negative" if "negative" in label else
                "neutral"
            )
            updates.append((sentiment, news_id))

    save_sentiments(updates)
    print("✅  Готово! Обновлено:", len(updates))

if __name__ == "__main__":
    main()
