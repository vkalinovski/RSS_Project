import sqlite3
from transformers import pipeline
from tqdm import tqdm

db_path = "news.db"  # путь внутри DATA_DIR

sentiment_analyzer = pipeline("sentiment-analysis")

def analyze_sentiment(text):
    res = sentiment_analyzer(text[:512])[0]
    lbl = res["label"].lower()
    return "positive" if "positive" in lbl else "negative" if "negative" in lbl else "neutral"

def update_news_sentiment(batch_size=8):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, title, content FROM news WHERE sentiment IS NULL")
    rows = cur.fetchall()
    if not rows:
        print("Все тональности проставлены.")
        return
    for i in tqdm(range(0, len(rows), batch_size)):
        batch = rows[i:i+batch_size]
        texts = [(t or "") + " " + (c or "") for _,t,c in batch]
        results = sentiment_analyzer(texts)
        for (nid,_,_),r in zip(batch, results):
            s = r["label"].lower()
            s = "positive" if "positive" in s else "negative" if "negative" in s else "neutral"
            cur.execute("UPDATE news SET sentiment=? WHERE id=?", (s, nid))
        conn.commit()
    conn.close()
    print("Тональности обновлены.")

if __name__ == "__main__":
    update_news_sentiment()

