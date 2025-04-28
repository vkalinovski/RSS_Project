# -*- coding: utf-8 -*-
import sqlite3
from database_utils import DB_PATH
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from typing import List, Dict

# Загружаем модель один раз
_tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
_model     = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
_sentiment = pipeline(
    "sentiment-analysis",
    model=_model,
    tokenizer=_tokenizer,
    device=0 if "CUDA_VISIBLE_DEVICES" in __import__("os").environ else -1,
)

def analyze_sentiment(articles: List[Dict]) -> List[Dict]:
    """
    Добавляет к каждой статье поля 'sentiment' и 'score'.
    """
    texts = [(art.get('title') or '') + ' ' + (art.get('content') or '') for art in articles]
    results = []
    for i in range(0, len(texts), 8):
        batch = texts[i:i+8]
        try:
            res = _sentiment(batch, truncation=True, max_length=512)
        except Exception:
            res = [{'label': None, 'score': 0.0} for _ in batch]
        results.extend(res)
    out = []
    for art, r in zip(articles, results):
        art2 = art.copy()
        art2['sentiment'] = r.get('label')
        art2['score']     = r.get('score')
        out.append(art2)
    return out

def update_news_sentiment(batch_size: int = 16):
    """
    Обновляет поле sentiment в базе для нерелевантных записей.
    """
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, content FROM news WHERE sentiment IS NULL")
    rows = cursor.fetchall()
    if not rows:
        print("✅ Все новости уже обработаны!")
        conn.close()
        return

    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        texts = [(title or "") + " " + (content or "") for _, title, content in batch]
        results = _sentiment(texts, truncation=True, max_length=512)
        for (news_id, _, _), r in zip(batch, results):
            sentiment = r.get("label", "").lower()
            if sentiment not in ("positive", "negative"):
                sentiment = "neutral"
            cursor.execute("UPDATE news SET sentiment = ? WHERE id = ?", (sentiment, news_id))
        conn.commit()
    conn.close()
    print(f"✅ Обновлено тональность для {len(rows)} статей!")

