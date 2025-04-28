# -*- coding: utf-8 -*-
import os
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from typing import List, Dict

_tokenizer = AutoTokenizer.from_pretrained(
    "distilbert-base-uncased-finetuned-sst-2-english"
)
_model = AutoModelForSequenceClassification.from_pretrained(
    "distilbert-base-uncased-finetuned-sst-2-english"
)
_sentiment = pipeline(
    "sentiment-analysis",
    model=_model,
    tokenizer=_tokenizer,
    device=0 if "CUDA_VISIBLE_DEVICES" in os.environ else -1,
)

def analyze_sentiment(articles: List[Dict]) -> List[Dict]:
    """
    Добавляет к каждой статье поля 'sentiment' и 'score'.
    """
    texts = []
    for art in articles:
        texts.append((art.get('title') or '') + ' ' + (art.get('content') or ''))

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


