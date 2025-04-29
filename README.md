<!-- ───────────────────────── README.md ───────────────────────── -->

# 📰 RSS / NewsAPI Media-Monitor  
*Tracking global media coverage of **Trump**, **Putin** & **Xi Jinping**  
from **April 2025** up to **today**  
---

## 0 Зачем нужен этот проект?

> «Мысль, не подкреплённая данными, — просто мнение».  
> Сервис собирает сырые новости **из двух независимых каналов**  
> (NewsAPI + прямые RSS-ленты), приводит к единому формату,  
> размечает, считает тональность, выводит 12 готовых графиков —  
> чтобы спор на кухне можно было проверять цифрами.

---

## 1 Пайплайн — шаг за шагом

| Шаг | Что происходит | Скрипт |
|-----|----------------|--------|
| **01. Сбор** | • 30-дневная выгрузка из **NewsAPI**<br>• парсинг ≈ 40 RSS-лент (см. `rss_feeds.py`) | `api_fetcher.py` / `rss.py` |
| **02. Очистка** | нормализация дат ISO, удаление дублей URL | `database.py` |
| **03. Классификация** | RegExp → `Trump` / `Putin` / `Xi` / `Mixed` | `database.py` |
| **04. Хранение** | всё складывается в **SQLite** `db/news.db` | `database.py` |
| **05. Тональность** | NLTK-VADER → `positive / neutral / negative` | `sentiment_analysis.py` |
| **06. Аналитика** | Генерация `news.csv` + **12 PNG-графиков** | `analyze.py` |
| **07. Вывод** | В Google Drive остаётся **только**<br>`db/news.db`, `db/news.csv`, `graphs/*.png` | — |

> На графиках диапазон принудительно обрезан  
> `2024-09-01 → (today + 3 days)`, поэтому в демо видны всплески,
> связанные с событиями **апреля 2025**.

---

## 2 Структура репозитория `RSS_Project/files`

| Файл | Назначение |
|------|-----------|
| `api_fetcher.py` | выгрузка статей из NewsAPI |
| `rss_feeds.py`   | список RSS-источников (легко расширяется) |
| `rss.py`         | чтение всех лент, первичная фильтрация |
| `database.py`    | работа с SQLite; путь к базе → env `DB_PATH` |
| `sentiment_analysis.py` | тональность VADER |
| `analyze.py`     | формирует `db/news.csv` и 12 графиков |
| `requirements.txt` | минимальный stack (Colab-friendly) |
| `schedule_parsing.py` | опциональный «cron» — каждые 24 ч |

<img src="https://img.shields.io/badge/Python-3.11+-blue?logo=python"> 
<img src="https://img.shields.io/badge/Google Colab-compatible-yellow?logo=googlecolab">

---

## 3 Содержимое результирующих папок

**Что внутри?**

| Файл/папка | Смысл |
|------------|-------|
| `db/news.db` | Главная база данных (SQLite). Содержит все статьи с полями:<br>`source`, `title`, `url`, `published_at`, `content`, `politician`, `sentiment`. |
| `db/news.csv` | Тот же набор данных, но в CSV-виде — откройте в Excel, Apache Superset, pandas. |
| `graphs/` | 12 PNG-графиков:<br>• тайм-серии упоминаний, stacked-area, cumulative<br>• позитив vs негатив во времени и по источникам<br>• pie-диаграммы, heatmap последних 30 дней<br>• распределения по дням недели и по часам суток. |

> Оставляем только эти артефакты в Google Drive,  
> чтобы не захламлять хранилище промежуточными .py-файлами.


---

## 4 One-click launch в Google Colab

> Скопируйте блок, вставьте в Colab,  
> замените `YOUR_NEWSAPI_KEY`, жмите **Run all**.

```python
# 🗝️ вставьте свой NEWSAPI KEY
NEWSAPI_KEY = "YOUR_NEWSAPI_KEY"

from google.colab import drive
import os, pathlib, shutil, glob, subprocess, sys

drive.mount("/content/drive", force_remount=False)

DRIVE = pathlib.Path("/content/drive/MyDrive/test")   # финальные файлы
TMP   = pathlib.Path("/content/RSS_tmp")              # клон репо

os.chdir("/content")
if TMP.exists(): shutil.rmtree(TMP)
!git clone -q --depth 1 https://github.com/vkalinovski/RSS_Project.git {TMP}

CODE = next((p.parent for p in TMP.rglob("api_fetcher.py")), TMP)
print("📂 scripts:", CODE)

!pip install -q feedparser requests python-dotenv pandas==2.2.2 matplotlib==3.8.4 nltk tqdm

os.environ["DB_PATH"] = str(DRIVE/"news.db")
(CODE/".env").write_text(f"NEWSAPI_KEY={NEWSAPI_KEY}\n")

%cd {CODE}
!python api_fetcher.py          || echo "NewsAPI step failed"
!python rss.py                  || echo "RSS step failed"
!python sentiment_analysis.py   || echo "Sentiment step failed"

if not pathlib.Path(os.environ["DB_PATH"]).exists() and pathlib.Path("news.db").exists():
    DRIVE.mkdir(parents=True, exist_ok=True)
    shutil.move("news.db", os.environ["DB_PATH"])

!python analyze.py              || echo "Analyze failed"

for f in glob.glob("news.csv"):
    shutil.move(f, DRIVE/"news.csv")
if (CODE/"graphs").is_dir():
    if (DRIVE/"graphs").exists(): shutil.rmtree(DRIVE/"graphs")
    shutil.move(str(CODE/"graphs"), DRIVE/"graphs")

print("\n✅ Готово! Смотрите db/ и graphs/ в", DRIVE)

