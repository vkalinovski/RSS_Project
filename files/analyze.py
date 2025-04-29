# -*- coding: utf-8 -*-
"""
Анализ базы news.db и генерация 12 PNG-графиков + news.csv.
Файлы пишутся в ту же папку, где лежит news.db.

Путь к базе задаётся переменной окружения DB_PATH
(если не указана — news.db рядом со скриптом).

Тайм-диапазон на графиках:
    1 января 2025  …  (сегодня)
"""

import os, sqlite3, pandas as pd, numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pathlib import Path

# ─────────────────── 1. Пути и константы ───────────────────
DB   = Path(os.getenv("DB_PATH", Path(__file__).parent / "news.db"))
ROOT = DB.parent
CSV  = ROOT / "news.csv"
GR   = ROOT / "graphs"
GR.mkdir(exist_ok=True)

POL   = ["Trump", "Putin", "Xi"]
START = pd.Timestamp("2025-01-01")
END   = pd.Timestamp(datetime.utcnow())

# ─────────────────── 2. Загрузка данных ────────────────────
if not DB.exists():
    raise FileNotFoundError(f"news.db не найден по пути {DB}")

with sqlite3.connect(DB) as c:
    df = pd.read_sql("SELECT * FROM news", c)

df["published_at"] = (
    pd.to_datetime(df["published_at"], utc=True).dt.tz_localize(None)
)
df = df[(df["published_at"] >= START) & (df["published_at"] <= END)]
df.to_csv(CSV, index=False)

if df.empty:
    print("⚠️  Нет данных в указанном диапазоне."); exit()

# ─────────────────── 3. Графические функции ────────────────
def timeline_mentions():
    g = (
        df.groupby([df["published_at"].dt.date, "politician"])
          .size().unstack(fill_value=0).rolling(3).mean()
    )
    plt.figure(figsize=(12,4))
    for p in POL: plt.plot(g.index, g[p], lw=2, label=p)
    plt.title("Упоминания (скользящее 3 дня)")
    plt.grid(); plt.legend(); plt.tight_layout()
    plt.savefig(GR/"mentions_timeline.png"); plt.close()

def stacked_mentions():
    g = (
        df.groupby([df["published_at"].dt.date,"politician"])
          .size().unstack(fill_value=0).reindex(columns=POL)
          .rolling(3).mean()
    )
    plt.figure(figsize=(12,5))
    plt.stackplot(g.index, g.T, labels=POL)
    plt.title("Stacked-area упоминаний (3-дн. сглаживание)")
    plt.xlabel("Дата"); plt.ylabel("Статей")
    plt.legend(loc="upper left"); plt.tight_layout()
    plt.savefig(GR/"stacked_mentions.png"); plt.close()

def sentiment_timeline():
    sub = df[df["sentiment"].isin(["positive","negative"])]
    g = (
        sub.groupby([sub["published_at"].dt.date,"sentiment"])
            .size().unstack(fill_value=0)[["positive","negative"]]
            .rolling(3).mean()
    )
    plt.figure(figsize=(12,4))
    plt.plot(g.index, g["positive"], label="positive", color="green")
    plt.plot(g.index, g["negative"], label="negative", color="red")
    plt.title("Позитив / негатив (3-дн. сглаживание)")
    plt.grid(); plt.legend(); plt.tight_layout()
    plt.savefig(GR/"sentiment_timeline.png"); plt.close()

def pie_sentiments():
    for p in POL:
        counts = df[df["politician"]==p]["sentiment"].value_counts()
        if counts.empty: continue
        plt.figure(figsize=(4,4))
        plt.pie(counts, labels=counts.index,
                autopct="%1.1f%%", startangle=140)
        plt.title(f"Тональность: {p}")
        plt.tight_layout()
        plt.savefig(GR/f"pie_sentiment_{p}.png"); plt.close()

def monthly_mentions():
    g = (
        df.groupby([df["published_at"].dt.to_period("M"),"politician"])
          .size().unstack(fill_value=0).reindex(columns=POL)
    )
    g.index = g.index.astype(str)
    g.plot(kind="bar", stacked=True, figsize=(12,6))
    plt.title("Статьи по месяцам")
    plt.xlabel("Месяц"); plt.ylabel("Статей")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(GR/"monthly_mentions.png"); plt.close()

def cumulative_mentions():
    g = (
        df.groupby([df["published_at"].dt.date,"politician"])
          .size().unstack(fill_value=0).reindex(columns=POL).cumsum()
    )
    plt.figure(figsize=(12,5))
    for p in POL: plt.plot(g.index, g[p], lw=2, label=p)
    plt.title("Накопленные упоминания")
    plt.xlabel("Дата"); plt.ylabel("Всего статей")
    plt.grid(); plt.legend(); plt.tight_layout()
    plt.savefig(GR/"cumulative_mentions.png"); plt.close()

def source_top20():
    g = (
        df.groupby(["source","politician"]).size()
          .unstack(fill_value=0).assign(total=lambda x: x.sum(1))
          .sort_values("total", ascending=False).head(20)
          .drop(columns="total")
    )
    g.plot(kind="barh", stacked=True, figsize=(10,8))
    plt.title("ТОП-20 источников")
    plt.xlabel("Статей"); plt.ylabel("Источник")
    plt.legend(title="Политик"); plt.tight_layout()
    plt.savefig(GR/"source_top20.png"); plt.close()

def source_sentiment_bar():
    g = (
        df[df["sentiment"].isin(["positive","negative"])]
          .groupby(["source","sentiment"]).size()
          .unstack(fill_value=0).assign(total=lambda x:x.sum(1))
          .sort_values("total", ascending=False).head(15)
          .drop(columns="total")
    )
    g.plot(kind="bar", figsize=(12,6))
    plt.title("Позитив / негатив • ТОП-15 источников")
    plt.xticks(rotation=45, ha="right"); plt.tight_layout()
    plt.savefig(GR/"source_sentiment_bar.png"); plt.close()

def heatmap_month():
    cutoff = END - timedelta(days=30)
    last = df[df["published_at"] >= cutoff]
    last["day"] = last["published_at"].dt.strftime("%m-%d")
    pivot = (
        last.groupby(["politician","day"]).size()
             .unstack(fill_value=0).reindex(index=POL)
    )
    plt.figure(figsize=(14,3))
    plt.imshow(pivot, aspect="auto", cmap="viridis")
    plt.yticks(range(len(POL)), POL)
    plt.xticks(range(len(pivot.columns)), pivot.columns,
               rotation=90, fontsize=6)
    plt.colorbar(label="Статей")
    plt.title("Тепловая карта: последние 30 дней")
    plt.tight_layout()
    plt.savefig(GR/"heatmap_month.png"); plt.close()

def weekday_pattern():
    df["weekday"] = df["published_at"].dt.day_name()
    order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    g = (
        df.groupby(["weekday","politician"]).size()
          .unstack(fill_value=0).reindex(order)
    )
    g.plot(kind="bar", stacked=True, figsize=(10,5))
    plt.title("Распределение по дням недели")
    plt.xlabel("День"); plt.ylabel("Статей")
    plt.tight_layout()
    plt.savefig(GR/"weekday_pattern.png"); plt.close()

def hourly_pattern():
    df["hour"] = df["published_at"].dt.hour
    g = (
        df.groupby(["hour","politician"]).size()
          .unstack(fill_value=0).reindex(columns=POL).sort_index()
    )
    g.plot(kind="bar", stacked=True, figsize=(10,5))
    plt.title("Распределение по часам суток (UTC)")
    plt.xlabel("Час"); plt.ylabel("Статей")
    plt.tight_layout()
    plt.savefig(GR/"hourly_pattern.png"); plt.close()

# ─────────────────── 4. Запуск всех графиков ───────────────
timeline_mentions()
stacked_mentions()
sentiment_timeline()
pie_sentiments()
monthly_mentions()
cumulative_mentions()
source_top20()
source_sentiment_bar()
heatmap_month()
weekday_pattern()
hourly_pattern()

print("✓ news.csv и 12 графиков сохранены в", ROOT)

