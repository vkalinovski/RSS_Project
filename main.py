# File: RSS_Project/main.py

from pathlib import Path
from database import create_database, remove_duplicates, update_database
from rss import fetch_rss_news
from api_fetcher import update_news
from sentiment_analysis import update_news_sentiment
from analyze import plot_all

def main():
    BASE_DIR = Path(__file__).parent
    OUT_DIR = BASE_DIR / "output"            # всё будет сохраняться сюда
    # 1) База и дубликаты
    create_database()
    remove_duplicates()
    update_database()                        # добавит колонку sentiment, если нужно
    # 2) Сбор новостей
    fetch_rss_news()                         # RSS → news.db
    update_news()                            # API MediaStack → news.db
    # 3) Анализ тональности
    update_news_sentiment(batch_size=16)     # запишет sentiment в news.db
    # 4) Построение и сохранение графиков + CSV
    plot_all(OUT_DIR)
    print(f"Графики и CSV сохранены в {OUT_DIR}")

if __name__ == "__main__":
    main()
