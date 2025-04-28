# File: RSS_Project/main.py

import os
from pathlib import Path

# Импортируем из database_utils, а не database
from database_utils import create_database, remove_duplicates, update_database
from rss import fetch_rss_news
from api_fetcher import update_news
from sentiment_analysis import update_news_sentiment
from analyze import plot_all

def main():
    # Папка на Google Drive
    drive_path = os.getenv('GDRIVE_PATH', '/content/gdrive/MyDrive/test')
    OUT = Path(drive_path)
    OUT.mkdir(exist_ok=True, parents=True)

    # Инициализация БД
    create_database()
    remove_duplicates()
    update_database()              # добавит колонку sentiment, если её нет

    # Сбор новостей
    fetch_rss_news(max_items=50)
    update_news(keywords=["Trump", "Xi Jinping", "Putin"], max_items=100)

    # Анализ тональности
    update_news_sentiment(batch_size=16)

    # Генерация графиков и CSV
    plot_all(OUT)

    print(f"🎉 Готово — все выходные файлы сохранены в {OUT}")

if __name__ == "__main__":
    main()
