# -*- coding: utf-8 -*-
import sqlite3
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from database_utils import DB_PATH

# Выбираем GPU, если он доступен, иначе CPU
_device = 0 if torch.cuda.is_available() else -1

# Загружаем токенизатор и модель один раз
_tokenizer = AutoTokenizer.from_pretrained(
    "distilbert-base-uncased-finetuned-sst-2-english"
)
_model = AutoModelForSequenceClassification.from_pretrained(
    "distilbert-base-uncased-finetuned-sst-2-english"
)

# Создаём пайплайн с PyTorch на нужном устройстве
_sentiment = pipeline(
    "sentiment-analysis",
    model=_model,
    tokenizer=_tokenizer,
    framework="pt",
    device=_device,
)

def update_news_sentiment(batch_size: int = 16):
    """
    Обновляет в БД поле sentiment для всех записей, где оно ещё не проставлено.
    """
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Выбираем необработанные статьи
    cursor.execute("SELECT id, title, content FROM news WHERE sentiment IS NULL")
    rows = cursor.fetchall()
    if not rows:
        print("✅ Все новости уже обработаны!")
        conn.close()
        return

    # Обрабатываем пакетами
    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        texts = [(title or "") + " " + (content or "") for _, title, content in batch]
        results = _sentiment(texts, truncation=True, max_length=512)

        # Записываем результат
        for (news_id, _, _), res in zip(batch, results):
            label = (res.get("label") or "").lower()
            if label not in ("positive", "negative"):
                label = "neutral"
            cursor.execute(
                "UPDATE news SET sentiment = ? WHERE id = ?",
                (label, news_id)
            )
        conn.commit()

    conn.close()
    print(f"✅ Проставлено sentiment для {len(rows)} статей!")

