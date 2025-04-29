# -*- coding: utf-8 -*-
"""
Читает news.db, формирует news.csv и 12 PNG-графиков.
Все файлы кладутся в ту же папку, где лежит news.db.

▪ путь к базе задаётся env-переменной DB_PATH  
▪ если DB_PATH нет — берётся news.db рядом со скриптом
"""

import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# ─── 1. пути и диапазон дат ────────────────────────────────────────────
DB   = Path(os.getenv("DB_PATH", Path(__file__).parent / "news.db"))
ROOT = DB.parent                         # здесь будут csv и графы
CSV  = ROOT / "news.csv"
GR   = ROOT / "graphs"
GR.mkdir(exist_ok=True)

POL   = ["Trump", "Putin", "Xi"]
START = pd.Timestamp("2024-09-01")
END   = pd.Timestamp(datetime.utcnow())      # «сегодня» UTC

# ─── 2. загрузка базы ───────────────────────────────────────────────────
if not DB.exists():
    raise FileNotFoundError(f"news.db не найден по пути {DB}")

with sqlite3.connect(DB) as c:
    df = pd.read_sql("SELECT * FROM news", c)

# привели published_at к tz-naive datetime
df["published_at"] = pd.to_datetime(df["published_at"], utc=True).dt.tz_localize(None)
df = df[(df["published_at"] >= START) & (df["published_at"] <= END)].copy()
df.to_csv(CSV, index=False)

if df.empty:
    print("⚠️  В базе нет данных в указанном диапазоне."); exit()

# ─── 3. функции построения графиков ─────────────────────────────────────
def timeline_mentions():
    """Сглаженная (3-дня) линия количества упоминаний по каждому политику"""
    g = df.groupby([df["published_at"].dt.date, "politician"]).size() \
          .unstack(fill_value=0).rolling(3).mean()
    plt.figure(figsize=(12, 4))
    for p in POL:
        plt.plot(g.index, g[p], lw=2, label=p)
    plt.title("Упоминания • скользящее 3 дня")
    plt.grid(); plt.legend(); plt.tight_layout()
    plt.savefig(GR / "mentions_timeline.png"); plt.close()

def stacked_mentions():
    """Stacked-area та же метрика"""
    g = df.groupby([df["published_at"].dt.date, "politician"]).size() \
          .unstack(fill_value=0).reindex(columns=POL).rolling(3).mean()
    plt.figure(figsize=(12, 5))
    plt.stackplot(g.index, g.T, labels=POL)
    plt.title("Stacked-area упоминаний (3 дн. сглаживание)")
    plt.xlabel("Дата"); plt.ylabel("Статей")
    plt.legend(loc="upper left"); plt.tight_layout()
    plt.savefig(GR / "stacked_mentions.png"); plt.close()

def sentiment_timeline():
    """Positive vs Negative в разрезе всей базы"""
    sub = df[df["sentiment"].isin(["positive", "negative"])]
    g = sub.groupby([sub["published_at"].dt.date, "sentiment"]).size() \
           .unstack(fill_value=0)[["positive", "negative"]].rolling(3).mean()
    plt.figure(figsize=(12, 4))
    plt.plot(g.index, g["positive"], label="positive", color="green")
    plt.plot(g.index, g["negative"], label="negative", color="red")
    plt.title("Позитив / негатив (скользящее 3 дня)")
    plt.grid(); plt.legend(); plt.tight_layout()
    plt.savefig(GR / "sentiment_timeline.png"); plt.close()

def pie_sentiments():
    """Круговые диаграммы по каждому политику"""
    for p in POL:
        counts = df[df["politician"] == p]["sentiment"].value_counts()
        if counts.empty: continue
        plt.figure(figsize=(4, 4))
        plt.pie(counts, labels=counts.index, autopct="%1.1f%%", startangle=140)
        plt.title(f"Тональность: {p}")
        plt.tight_layout()
        plt.savefig(GR / f"pie_sentiment_{p}.png"); plt.close()

def monthly_mentions():
    """Статьи по месяцам (stacked bar)"""
    g = df.groupby([df["published_at"].dt.to_period("M"), "politician"]).size() \
          .unstack(fill_value=0).reindex(columns=POL)
    g.index = g.index.astype(str)
    g.plot(kind="bar", stacked=True, figsize=(12, 6))
    plt.title("Статьи по месяцам")
    plt.xlabel("Месяц"); plt.ylabel("Статей")
    plt.xticks(rotation=45, ha="right"); plt.tight_layout()
    plt.savefig(GR / "monthly_mentions.png"); plt.close()

def cumulative_mentions():
    """Накопительный счётчик упоминаний"""
    g = df.groupby([df["published_at"].dt.date, "politician"]).size() \
          .unstack(fill_value=0).reindex(columns=POL).cumsum()
    plt.figure(figsize=(12, 5))
    for p in POL: plt.plot(g.index, g[p], lw=2, label=p)
    plt.title("Накопленные упоминания"); plt.grid(); plt.legend()
    plt.tight_layout(); plt.savefig(GR / "cumulative_mentions.png"); plt.close()

def source_top20():
    """ТОП-20 медиа-источников (stacked bar)"""
    g = df.groupby(["source", "politician"]).size().unstack(fill_value=0)
    g["total"] = g.sum(1)
    g = g.sort_values("total", ascending=False).head(20).drop(columns="total")
    g.plot(kind="barh", stacked=True, figsize=(10, 8))
    plt.title("ТОП-20 источников"); plt.xlabel("Статей")
    plt.legend(title="Политик"); plt.tight_layout()
    plt.savefig(GR / "source_top20.png"); plt.close()

def source_sentiment_bar():
    """Positive vs Negative для ТОП-15 источников"""
    g = df[df["sentiment"].isin(["positive", "negative"])]
    g = g.groupby(["source", "sentiment"]).size().unstack(fill_value=0)
    g["total"] = g.sum(1)
    g = g.sort_values("total", ascending=False).head(15).drop(columns="total")
    g.plot(kind="bar", figsize=(12, 6))
    plt.title("Позитив / негатив • ТОП-15 источников")
    plt.xticks(rotation=45, ha="right"); plt.tight_layout()
    plt.savefig(GR / "source_sentiment_bar.png"); plt.close()

def heatmap_month():
    """Heatmap последних 30 дней"""
    cutoff = END - timedelta(days=30)
    recent = df[df["published_at"] >= cutoff].copy()
    recent["day"] = recent["published_at"].dt.strftime("%m-%d")
    pivot = recent.groupby(["politician", "day"]).size().unstack(fill_value=0) \
                  .reindex(index=POL)
    plt.figure(figsize=(14, 3))
    plt.imshow(pivot, aspect="auto", cmap="viridis")
    plt.yticks(range(len(POL)), POL)
    plt.xticks(range(len(pivot.columns)), pivot.columns, rotation=90, fontsize=6)
    plt.colorbar(label="Статей")
    plt.title("Тепловая карта: последние 30 дней")
    plt.tight_layout(); plt.savefig(GR / "heatmap_month.png"); plt.close()

def weekday_pattern():
    """Распределение публикаций по дням недели"""
    df["weekday"] = df["published_at"].dt.day_name()
    order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    g = df.groupby(["weekday", "politician"]).size().unstack(fill_value=0).reindex(order)
    g.plot(kind="bar", stacked=True, figsize=(10, 5))
    plt.title("По дням недели"); plt.xlabel("День"); plt.ylabel("Статей")
    plt.tight_layout(); plt.savefig(GR / "weekday_pattern.png"); plt.close()

def hourly_pattern():
    """Распределение публикаций по часам (UTC)"""
    df["hour"] = df["published_at"].dt.hour
    g = df.groupby(["hour", "politician"]).size().unstack(fill_value=0) \
          .reindex(columns=POL).sort_index()
    g.plot(kind="bar", stacked=True, figsize=(10, 5))
    plt.title("По часам суток (UTC)"); plt.xlabel("Час"); plt.ylabel("Статей")
    plt.tight_layout(); plt.savefig(GR / "hourly_pattern.png"); plt.close()

# ─── 4. генерируем все графики ──────────────────────────────────────────
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
