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


































# Проект анализа новостей о политиках (с сентября 2024 года)

## Описание проекта

Проект собирает и анализирует новостные статьи о мировых политиках: **Xi Jinping**, **Donald Trump** и **Vladimir Putin** с 1 сентября 2024 года. Новости извлекаются из RSS-лент ведущих мировых СМИ и через NewsAPI. Данные хранятся в SQLite и экспортируются в CSV. Выполняется анализ частоты упоминаний и тональности новостей, результаты визуализируются.

## Структура проекта

```
project/
├── main.py                    # Основной модуль запуска проекта
├── rss_feeds.py               # Список RSS-источников
├── rss.py                     # Функции для парсинга RSS
├── api_fetcher.py             # Сбор данных через NewsAPI
├── database_utils.py          # Работа с SQLite
├── sentiment_analysis.py      # Анализ тональности (DistilBERT)
├── analyze.py                 # Построение графиков и анализ
├── requirements.txt           # Зависимости проекта
├── news.db                    # БД SQLite (создаётся автоматически)
├── timeseries.csv             # CSV с результатами (создаётся автоматически)
└── graphs/                    # Папка для графиков (создаётся автоматически)
```

## Файлы и их назначение
- **`main.py`** – основной запускаемый скрипт.
- **`rss_feeds.py`** – словарь RSS-источников.
- **`rss.py`** – загрузка новостей из RSS.
- **`api_fetcher.py`** – взаимодействие с NewsAPI.
- **`database_utils.py`** – работа с базой SQLite.
- **`sentiment_analysis.py`** – анализ тональности новостей.
- **`analyze.py`** – генерация и сохранение графиков.

## Как запустить проект в Google Colab

### 1. Клонируйте репозиторий
```bash
!git clone https://github.com/yourusername/your-repo.git
%cd your-repo
```

### 2. Установите зависимости
```python
!pip install -r requirements.txt
```

### 3. Настройка параметров
- Установите API-ключ от [NewsAPI.org](https://newsapi.org/):
```python
import os
os.environ['NEWSAPI_KEY'] = "ВАШ_API_КЛЮЧ"
```
- Измените переменную `OUT_DIR` в `main.py` на нужный путь (например, Google Drive).
- Проверьте дату начала сбора новостей (`CUTOFF_DATE = datetime(2024, 9, 1)`).

### 4. Запустите сбор и анализ
```python
from main import one_cycle
one_cycle()
```

## Просмотр результатов
После выполнения в указанной папке вы найдёте:
- Файл `news.db` с новостями (SQLite)
- Файл `timeseries.csv` (количество упоминаний)
- Графики (`*.png`) в папке `graphs`

## Визуализации
- **Ежедневный, недельный и месячный тренды** упоминаний политиков.
- **Тренды тональности новостей** (позитивные и негативные).
- **Топ-источники** по количеству публикаций для каждого политика.

Для просмотра графиков используйте любой просмотрщик изображений или добавьте в код блок:
```python
from IPython.display import Image, display
import os

graphs_path = 'graphs/'
for graph in os.listdir(graphs_path):
    display(Image(filename=os.path.join(graphs_path, graph)))
```



