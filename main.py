# File: RSS_Project/main.py

import os
import sys
import subprocess
from datetime import datetime
import pandas as pd

# ----------------------------------------------------------------------------
# 0️⃣ Клонирование репозитория (если не загружен)
# ----------------------------------------------------------------------------
REPO_URL  = "https://github.com/vkalinovski/RSS_Project.git"
LOCAL_DIR = "RSS_Project"
if not os.path.isdir(LOCAL_DIR):
    print("Cloning repository…")
    subprocess.run(["git", "clone", REPO_URL, LOCAL_DIR], check=True)

# Добавляем проект в PYTHONPATH
sys.path.insert(0, os.path.abspath(LOCAL_DIR))

# ----------------------------------------------------------------------------
# 1️⃣ Импорт модулей проекта
# ----------------------------------------------------------------------------
from rss               import fetch_rss_articles
from api_fetcher       import fetch_newsapi_articles
from database_utils    import create_database, save_news_to_db
from sentiment_analysis import analyze_sentiment
from analyze           import (
    build_timeseries,
    plot_overall_timeseries,
    plot_monthly_aggregation,
    plot_weekly_aggregation,
    plot_cumulative,
    plot_sentiment_trends,
    plot_top_sources
)
from utils             import now_utc

# ----------------------------------------------------------------------------
# 2️⃣ Конфигурация
# ----------------------------------------------------------------------------
KEYWORDS       = ["Xi Jinping", "Donald Trump"]
MAX_ITEMS      = 100                  # лимит free-тарифа NewsAPI
API_LANGUAGES  = ["en"]               # запрашиваем только англоязычные статьи
OUT_DIR        = "/content/gdrive/MyDrive/test"  # папка на Google Drive

# ----------------------------------------------------------------------------
# 3️⃣ Основная функция: сбор → фильтрация → сохранение → анализ → визуализация
# ----------------------------------------------------------------------------
def one_cycle():
    print(f"[{now_utc()}] Старт цикла…")

    # 1) Инициализация БД
    create_database()

    # 2) Сбор новостей из RSS и NewsAPI
    rss_news = fetch_rss_articles(MAX_ITEMS)
    api_news = []
    for lang in API_LANGUAGES:
        api_news += fetch_newsapi_articles(KEYWORDS, MAX_ITEMS, language=lang)
    all_news = rss_news + api_news

    # 3) Отбор статей не раньше 2025-01-01
    cutoff = datetime(2025, 1, 1)
    all_news = [
        art for art in all_news
        if datetime.strptime(art["published"], "%Y-%m-%d") >= cutoff
    ]
    if not all_news:
        print(f"[{now_utc()}] Нет статей с {cutoff.date()}.")
        return

    # 4) Категоризация по политикам
    xi     = []
    trump  = []
    for art in all_news:
        text = (art.get("title") or "") + " " + (art.get("content") or "")
        if "Xi Jinping" in text:
            xi.append({**art, "politician": "Xi Jinping"})
        if "Donald Trump" in text:
            trump.append({**art, "politician": "Donald Trump"})
    if not xi and not trump:
        print(f"[{now_utc()}] Не найдено упоминаний Xi Jinping или Donald Trump.")
        return

    # 5) Сохранение в базу данных
    save_news_to_db(xi,    "Xi Jinping")
    save_news_to_db(trump, "Donald Trump")

    # 6) Сентимент-анализ
    combined    = xi + trump
    sentimented = analyze_sentiment(combined)

    # 7) Построение DataFrame и временного ряда
    df = pd.DataFrame(sentimented)
    # Обеспечиваем наличие published_at для анализа тональности
    df["published_at"] = pd.to_datetime(df["published"]).dt.strftime("%Y-%m-%d")
    ts = build_timeseries(df)

    # 8) Сохранение CSV
    os.makedirs(OUT_DIR, exist_ok=True)
    ts.to_csv(os.path.join(OUT_DIR, "timeseries.csv"), index=True)

    # 9️⃣ Генерация шести ключевых графиков
    plot_overall_timeseries(ts, OUT_DIR)
    plot_monthly_aggregation(ts, OUT_DIR)
    plot_weekly_aggregation(ts, OUT_DIR)
    plot_cumulative(ts, OUT_DIR)
    plot_sentiment_trends(df, OUT_DIR)
    plot_top_sources(df, OUT_DIR)

    print(f"[{now_utc()}] Графики и CSV сохранены в {OUT_DIR}")

# ----------------------------------------------------------------------------
# 4️⃣ Запуск
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    one_cycle()
