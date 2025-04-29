<!-- ───────────────────────── README.md ───────────────────────── -->

# 📰 RSS / NewsAPI Media-Monitor  
*Monitoring headline dynamics for **Trump**, **Putin** & **Xi Jinping**  
from September 2024 → today (demo dataset — April 2025).*

---

## 1 Что делает проект
| Этап | Описание |
|------|----------|
| **Сбор** | • качает новости за последние 30 дней из **NewsAPI**<br>• парсит ±40 RSS-лент крупнейших мировых СМИ |
| **Хранение** | сохраняет статьи в SQLite-базу **`news.db`**<br>формат 💾 `source · title · url · published_at · content · politician · sentiment` |
| **Аналитика** | • классификация по политикам (Trump / Putin / Xi / Mixed)<br>• анализ тональности `positive/neutral/negative` (NLTK VADER)<br>• 12 информативных графиков — тайм-серии, heatmap, pie/bar/stack |
| **Вывод** | в `/MyDrive/test` остаются ровно **3 единицы**:<br>`news.db`, `news.csv`, папка `graphs/` с PNG-картинками |

💡 **Фокус демо-набора** — **апрель 2025 г.** На графиках диапазон ограничен  
`2024-09-01 … (today + 3 days)`, поэтому в репрезентативной выгрузке
видны пики, приуроченные к апрельским событиям 2025 года.

---

## 2 Структура репозитория `RSS_Project/files`

| Файл | Что делает |
|------|------------|
| `api_fetcher.py` | выгрузка статей из **NewsAPI** |
| `rss_feeds.py`   | 💡 список RSS-источников (расширяйте при желании) |
| `rss.py`         | парсинг всех лент из `rss_feeds.py` |
| `database.py`    | единый слой работы c SQLite; путь к базе — переменная **`DB_PATH`** |
| `sentiment_analysis.py` | оценка тональности NLTK-VADER |
| `analyze.py`     | формирует `news.csv` и **12 графиков** |
| `requirements.txt` | минимальный stack, совместимый с Google Colab |
| `schedule_parsing.py` | (опционально) бесконечный цикл «раз в 24 ч» |
| **`main.py`**    | *не нужен — заменён `database.create()`* |

<img src="https://img.shields.io/badge/python-3.11%2B-blue?logo=python" alt="Python 3.11"> 
<img src="https://img.shields.io/badge/Colab-compatible-yellow?logo=googlecolab">

---

## 3 Быстрый старт в Google Colab

> **✂️ Скопируйте** ячейку ниже в Colab → введите ваш NewsAPI key → `▶︎ Run all`.

```python
# 🗝️  вставьте собственный ключ
NEWSAPI_KEY = "YOUR_NEWSAPI_KEY_HERE"

# ───────────── пуск ─────────────
from google.colab import drive
import pathlib, shutil, os, glob, subprocess, sys

drive.mount("/content/drive", force_remount=False)

DRIVE_DIR = pathlib.Path("/content/drive/MyDrive/test")      # итоговые файлы
TMP_DIR   = pathlib.Path("/content/RSS_tmp")                 # клон репо (RAM)

os.chdir("/content")
if TMP_DIR.exists(): shutil.rmtree(TMP_DIR)
!git clone --depth 1 https://github.com/vkalinovski/RSS_Project.git {TMP_DIR}

CODE = next((p.parent for p in TMP_DIR.rglob("api_fetcher.py")), TMP_DIR)
print("📂  scripts:", CODE)

!pip install -q feedparser requests python-dotenv pandas==2.2.2 matplotlib==3.8.4 nltk tqdm

DB_FILE = DRIVE_DIR / "news.db"
os.environ["DB_PATH"] = str(DB_FILE)
(CODE/".env").write_text(f"NEWSAPI_KEY={NEWSAPI_KEY}\n")

%cd {CODE}
!python api_fetcher.py
!python rss.py
!python sentiment_analysis.py

if not DB_FILE.exists() and pathlib.Path("news.db").exists():
    DRIVE_DIR.mkdir(parents=True, exist_ok=True)
    shutil.move("news.db", DB_FILE)

!python analyze.py        # пишет news.csv + graphs рядом с news.db

for f in glob.glob("news.csv"): shutil.move(f, DRIVE_DIR/"news.csv")
if (CODE/"graphs").is_dir():
    shutil.move(str(CODE/"graphs"), DRIVE_DIR/"graphs")

print("\n✅  Всё готово!  news.db, news.csv, graphs/ →", DRIVE_DIR)
