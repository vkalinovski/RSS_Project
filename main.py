# File: RSS_Project/main.py

from pathlib import Path
from database_utils import create_database, remove_duplicates, update_database
from rss import fetch_rss_news
from api_fetcher import update_news
from sentiment_analysis import update_news_sentiment
from analyze import plot_all

def main():
    BASE = Path(__file__).parent
    OUT  = BASE / "output"
    OUT.mkdir(exist_ok=True)

    create_database()
    remove_duplicates()
    update_database()              # добавит колонку sentiment, если её нет

    fetch_rss_news()               # RSS → news.db
    update_news()                  # Mediastack → news.db

    update_news_sentiment(batch_size=16)  # проставит sentiment

    plot_all(OUT)                  # все графики + timeseries.csv

    print(f"🎉 Готово — всё в {OUT}")

if __name__ == "__main__":
    main()
