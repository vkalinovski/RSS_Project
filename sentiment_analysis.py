import sqlite3
from pathlib import Path
from transformers import pipeline
from tqdm import tqdm

DB_PATH = Path(__file__).parent / "news.db"
BATCH = 8

sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    device_map="auto",
)

def fetch_rows():
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute(
            "SELECT id, title, content FROM news WHERE sentiment IS NULL"
        ).fetchall()

def save(upd):
    with sqlite3.connect(DB_PATH) as conn:
        conn.executemany("UPDATE news SET sentiment=? WHERE id=?", upd)
        conn.commit()

def main():
    rows = fetch_rows()
    if not rows:
        print("✅  Все новости уже размечены")
        return

    updates = []
    for i in tqdm(range(0, len(rows), BATCH), desc="Sentiment"):
        batch = rows[i : i+BATCH]
        texts = [( (t or "") + " " + (c or "") ) for _,t,c in batch]
        preds = sentiment_analyzer(texts, truncation=True)

        for (news_id, _, _), pr in zip(batch, preds):
            label = pr["label"].lower()
            sent = "positive" if "positive" in label else "negative" if "negative" in label else "neutral"
            updates.append((sent, news_id))

    save(updates)
    print("✅  Обновлено", len(updates), "статей")

if __name__ == "__main__":
    main()
