# 📰 RSS / Media-Monitor  
Tracking global coverage of **Putin**, **Trump** & **Xi Jinping**

<p align="center">
  <img src="docs/img/banner.png"
       alt="Banner · Putin · Trump · Xi"
       width="820">
</p>

> “A thought not supported by data is just an opinion.”

---

## 1 Pipeline — Step by Step

| Step | Action | Script |
|------|--------|--------|
| **01. Collection** | • 30-day extraction from **NewsAPI**<br>• parsing ≈ 40 RSS feeds (see `rss_feeds.py`) | `api_fetcher.py` / `rss.py` |
| **02. Cleaning**   | normalize dates to ISO, remove duplicate URLs | `database.py` |
| **03. Classification** | RegExp → `Trump` / `Putin` / `Xi` / `Mixed` | `database.py` |
| **04. Storage**    | everything is saved into **SQLite** `db/news.db` | `database.py` |
| **05. Sentiment Analysis** | NLTK-VADER → `positive / neutral / negative` | `sentiment_analysis.py` |
| **06. Analytics**  | generate `news.csv` + **13 PNG charts** | `analyze.py` |
| **07. Output**     | Only the following remain in Google Drive:<br>`db/news.db`, `db/news.csv`, `graphs/*.png` | — |

> All charts cover the date range `2025-01-01 → today`

---

## 2 Repository Structure `RSS_Project/files`

| File | Purpose |
|------|---------|
| `api_fetcher.py`         | fetch articles from NewsAPI |
| `rss_feeds.py`           | list of RSS sources (easily extendable) |
| `rss.py`                 | read all feeds, initial filtering |
| `database.py`            | work with SQLite; database path → env `DB_PATH` |
| `sentiment_analysis.py`  | conduct VADER sentiment analysis |
| `analyze.py`             | produce `db/news.csv` and 13 charts |
| `requirements.txt`       | minimal stack (Colab-friendly) |
| `schedule_parsing.py`    | optional “cron” — every 24 hours |

<img src="https://img.shields.io/badge/Python-3.11+-blue?logo=python"> 
<img src="https://img.shields.io/badge/Google Colab-compatible-yellow?logo=googlecolab">

---

## 3 Contents of Output Folders

**What’s inside?**

| File/Folder | Description |
|-------------|-------------|
| `db/news.db`   | Main SQLite database. Contains all articles with fields:<br>`source`, `title`, `url`, `published_at`, `content`, `politician`, `sentiment`. |
| `db/news.csv`  | The same dataset exported as CSV — open in Excel, Apache Superset, pandas. |
| `graphs/`      | 13 PNG charts:<br>• time series of mentions (stacked area, cumulative)<br>• positive vs negative over time and by source<br>• pie charts, heatmap of last 30 days<br>• distributions by day of week and hour of day. |

> We keep only these artifacts in Google Drive to avoid cluttering storage with intermediate `.py` files.

---

## 4 One-Click Launch in Google Colab

> Copy this block, paste into Colab,  
> replace `YOUR_NEWSAPI_KEY`, then click **Run all**.

```python
# 🗝️ insert your NEWSAPI KEY
NEWSAPI_KEY = "YOUR_NEWSAPI_KEY"

from google.colab import drive
import os, pathlib, shutil, glob, subprocess, sys

drive.mount("/content/drive", force_remount=False)

DRIVE = pathlib.Path("/content/drive/MyDrive/test")   # final files
TMP   = pathlib.Path("/content/RSS_tmp")              # repo clone

os.chdir("/content")
if TMP.exists(): shutil.rmtree(TMP)
!git clone -q --depth 1 https://github.com/vkalinovski/RSS_Project.git {TMP}

CODE = next((p.parent for p in TMP.rglob("api_fetcher.py")), TMP)
print("scripts:", CODE)

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


