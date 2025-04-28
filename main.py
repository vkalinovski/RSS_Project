# -*- coding: utf-8 -*-
import os, sys, subprocess
from datetime import datetime
import pandas as pd

# 0️⃣ Клонирование репозитория (если нужно)
REPO_URL  = "https://github.com/vkalinovski/RSS_Project.git"
LOCAL_DIR = "RSS_Project"
if not os.path.isdir(LOCAL_DIR):
    subprocess.run(["git","clone",REPO_URL,LOCAL_DIR], check=True)
sys.path.insert(0, os.path.abspath(LOCAL_DIR))

# 1️⃣ Импорты
from rss                import fetch_rss_articles
from api_fetcher        import fetch_newsapi_articles
from database_utils     import create_database, save_news_to_db
from sentiment_analysis import analyze_sentiment
from analyze            import (
    build_timeseries, plot_overall_timeseries, plot_weekly_aggregation,
    plot_monthly_aggregation, plot_cumulative, plot_sentiment_trends,
    plot_top_sources, plot_top20_sources_bar, plot_top5_sources_timeseries
)
from utils              import now_utc

# 2️⃣ Настройки
KEYWORDS      = ["Xi Jinping", "Donald Trump", "Vladimir Putin"]
MAX_ITEMS     = 100
API_LANGUAGES = ["en"]
OUT_DIR       = "/content/gdrive/MyDrive/test"
CUTOFF_DATE   = datetime(2024, 9, 1)

def one_cycle():
    print(f"[{now_utc()}] Старт цикла…")
    create_database()

    rss_news = fetch_rss_articles(MAX_ITEMS)
    api_news = []
    for lang in API_LANGUAGES:
        api_news += fetch_newsapi_articles(KEYWORDS, MAX_ITEMS, language=lang)
    all_news = rss_news + api_news

    # Фильтрация по дате
    filtered = []
    for art in all_news:
        try:
            dt = datetime.strptime(art["published"], "%Y-%m-%d")
        except:
            continue
        if dt >= CUTOFF_DATE:
            filtered.append(art)
    if not filtered:
        print(f"[{now_utc()}] Нет статей с {CUTOFF_DATE.date()}."); return

    # Категории по политикам
    lists = {"Xi Jinping":[], "Donald Trump":[], "Vladimir Putin":[]}
    for art in filtered:
        txt = (art.get("title") or "") + " " + (art.get("content") or "")
        for pol in lists:
            if pol in txt:
                lists[pol].append({**art, "politician": pol})
    for pol, lst in lists.items():
        save_news_to_db(lst, pol)

    # Сентимент
    combined    = sum(lists.values(), [])
    sentimented = analyze_sentiment(combined)

    # DataFrame и временной ряд
    df = pd.DataFrame(sentimented)
    df["published_at"] = pd.to_datetime(df["published"]).dt.strftime("%Y-%m-%d")
    ts = build_timeseries(df)

    # Сохранение CSV + графиков
    os.makedirs(OUT_DIR, exist_ok=True)
    ts.to_csv(os.path.join(OUT_DIR, "timeseries.csv"), index=True)

    plot_overall_timeseries(ts, OUT_DIR)
    plot_weekly_aggregation(ts, OUT_DIR)
    plot_monthly_aggregation(ts, OUT_DIR)
    plot_cumulative(ts, OUT_DIR)
    plot_sentiment_trends(df, OUT_DIR)
    plot_top_sources(df, OUT_DIR)
    plot_top20_sources_bar(df, OUT_DIR)
    plot_top5_sources_timeseries(df, OUT_DIR)

    print(f"[{now_utc()}] Графики и CSV сохранены в {OUT_DIR}")

if __name__ == "__main__":
    one_cycle()
