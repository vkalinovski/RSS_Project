import time
from datetime import datetime
from rss import fetch_rss_news
from api_fetcher import update_news

def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def run_daily():
    while True:
        log("Запуск сбора новостей")
        try:
            fetch_rss_news()
            update_news()
            log("Завершено, спим 24 ч.")
        except Exception as e:
            log("Ошибка: " + str(e))
        time.sleep(86400)

if __name__ == "__main__":
    run_daily()

