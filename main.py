# File: main.py

import os
import sys
import subprocess
from datetime import datetime
import pandas as pd

# ----------------------------------------------------------------------------
# 0️⃣ Клонирование репозитория (если ещё не загружен)
# ----------------------------------------------------------------------------
REPO_URL  = "https://github.com/vkalinovski/RSS_Project.git"
LOCAL_DIR = "RSS_Project"
if not os.path.isdir(LOCAL_DIR):
    print("Cloning repository…")
    subprocess.run(["git", "clone", REPO_URL, LOCAL_DIR], check=True)

# Добавляем папку проекта в PYTHONPATH
sys.path.insert(0, os.path.abspath(LOCAL_DIR))

# ----------------------------------------------------------------------------
# 1️⃣ Импорт модулей проекта
# ----------------------------------------------------------------------------
from rss_feeds            import RSS_FEEDS
from rss                  import fetch_rss_articles
from api_fetcher         import fetch_newsapi_articles
from database_utils      import create_database, save_news_to_db
from sentiment_analysis  import analyze_sentiment
from analyze             import (
    build_timeseries,
    plot1_timeseries, plot2_bar_total, plot3_rolling, plot4_monthly,
    plot5_pie_sources, plot6_weekday, plot7_top_days, plot8_cumulative,
    plot9_sentiment_dist, plot10_top_sources_per_politician
)
from utils               import now_utc

# ----------------------------------------------------------------------------
# 2️⃣ Конфигурация
# ----------------------------------------------------------------------------
KEYWORDS      = ["Xi Jinping", "Donald Trump"]
MAX_ITEMS     = 100                 # лимит free-тарифа NewsAPI
API_LANGUAGES = ["en"]              # запрашиваем только англоязычные
OUT_DIR       = "/content/gdrive/MyDrive/test"  # папка на Google Drive

# ----------------------------------------------------------------------------
# 3️⃣ Основная функция: Сбор → Фильтрация → Сохранение → Анализ → Визуализация
# ----------------------------------------------------------------------------
def one_cycle():
    print(f"[{now_utc()}] Запуск цикла…")

    # — Создание / проверка БД
    create_database()

    # — Сбор RSS и API
    rss_news = fetch_rss_articles(MAX_ITEMS)
    api_news = []
    for lang in API_LANGUAGES:
        api_news += fetch_newsapi_articles(KEYWORDS, MAX_ITEMS, language=lang)
    all_news = rss_news + api_news

    # — Фильтр по дате (только с 1 янв. 2024)
    all_news = [
        n for n in all_news
        if datetime.strptime(n["published"], "%Y-%m-%d") >= datetime(2024, 1, 1)
    ]
    if not all_news:
        print(f"[{now_utc()}] Нет статей с 2024-01-01 и позже.")
        return

    # — Категоризация: для каждого артила помечаем «Xi Jinping» или «Donald Trump»
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

    # — Сохранение в базу
    save_news_to_db(xi,    "Xi Jinping")
    save_news_to_db(trump, "Donald Trump")

    # — Сентимент-анализ
    combined    = xi + trump
    sentimented = analyze_sentiment(combined)

    # — Временной ряд + CSV
    df = pd.DataFrame(sentimented)
    ts = build_timeseries(df)
    os.makedirs(OUT_DIR, exist_ok=True)
    ts.to_csv(os.path.join(OUT_DIR, "timeseries.csv"), index=True)

    # — Генерация 10 графиков
    # после построения ts и df:
    plot_overall_timeseries(ts, OUT_DIR)
    plot_monthly_aggregation(ts, OUT_DIR)
    plot_weekly_aggregation(ts, OUT_DIR)
    plot_cumulative(ts, OUT_DIR)
    plot_sentiment_trends(df, OUT_DIR)
    plot_top_sources(ts, df, OUT_DIR)

    print(f"[{now_utc()}] Цикл завершён. Результаты — в {OUT_DIR}")

# ----------------------------------------------------------------------------
# 4️⃣ Точка входа
# ----------------------------------------------------------------------------
if __name__ == '__main__':
    one_cycle()
