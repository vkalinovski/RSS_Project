import os
from pathlib import Path
from database_utils import create_database, remove_duplicates, update_database
from rss import fetch_rss_news
from api_fetcher import update_news
from sentiment_analysis import update_news_sentiment
from analyze import plot_all


def main():
    # Директория Google Drive для сохранения всех файлов
    drive_path = os.getenv('GDRIVE_PATH', '/content/gdrive/MyDrive/test')
    OUT = Path(drive_path)
    OUT.mkdir(exist_ok=True, parents=True)

    create_database()
    remove_duplicates()
    update_database()              # добавит колонку sentiment, если её нет

    fetch_rss_news(max_items=50)   # RSS → news.db
    update_news(keywords=["Trump", "Xi Jinping", "Putin"], max_items=100)

    update_news_sentiment(batch_size=16)  # проставит sentiment

    # Сохраняем все графики и CSV в Google Drive
    plot_all(OUT)

    print(f"🎉 Готово — все выходные файлы сохранены в {OUT}")

if __name__ == "__main__":
    main()
