"""
Формирует news.csv и 12 информативных графиков в папке graphs/.

Тайм-интервал: 1 сентября 2024 — (сегодня + 3 дня).
"""

import sqlite3, pandas as pd, numpy as np, matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime, timedelta

# ────────── пути и диапазон ──────────
ROOT   = Path(__file__).parent
DB     = ROOT / "news.db"
OUT    = ROOT / "graphs"
OUT.mkdir(exist_ok=True)

POLITS = ["Trump", "Putin", "Xi"]
START  = pd.Timestamp("2024-09-01")
END    = pd.Timestamp(datetime.utcnow() + timedelta(days=3))

# ────────── данные ──────────
def load() -> pd.DataFrame:
    with sqlite3.connect(DB) as c:
        df = pd.read_sql("SELECT * FROM news", c)
    df["published_at"] = pd.to_datetime(df["published_at"], utc=True)
    mask = (df["published_at"] >= START) & (df["published_at"] <= END)
    df = df.loc[mask]
    df.to_csv(ROOT / "news.csv", index=False)
    return df

# ────────── графики ──────────
def timeline_mentions(df):
    g = (
        df.groupby([df["published_at"].dt.date, "politician"])
          .size().unstack(fill_value=0)
          .rolling(3).mean()
    )
    plt.figure(figsize=(12,5))
    for p in POLITS:
        if p in g.columns:
            plt.plot(g.index, g[p], label=p, lw=2)
    plt.title("Упоминания (3-дневное скользящее среднее)")
    plt.xlabel("Дата"); plt.ylabel("Статей")
    plt.grid(); plt.legend(); plt.tight_layout()
    plt.savefig(OUT/"mentions_timeline.png"); plt.close()

def stacked_mentions(df):
    g = (
        df.groupby([df["published_at"].dt.date,"politician"])
          .size().unstack(fill_value=0).reindex(columns=POLITS)
          .rolling(3).mean()
    )
    plt.figure(figsize=(12,5))
    plt.stackplot(g.index, g.T, labels=POLITS)
    plt.title("Stacked-area упоминаний (3-дн. сглаживание)")
    plt.xlabel("Дата"); plt.ylabel("Статей")
    plt.legend(loc="upper left"); plt.tight_layout()
    plt.savefig(OUT/"stacked_mentions.png"); plt.close()

def sentiment_timeline(df):
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
    plt.savefig(OUT/"sentiment_timeline.png"); plt.close()

def pie_sentiments(df):
    for p in POLITS:
        counts = df[df["politician"]==p]["sentiment"].value_counts()
        if counts.empty: continue
        plt.figure(figsize=(4,4))
        plt.pie(counts, labels=counts.index, autopct="%1.1f%%", startangle=140)
        plt.title(f"Тональность: {p}")
        plt.tight_layout(); plt.savefig(OUT/f"pie_sentiment_{p}.png"); plt.close()

def monthly_mentions(df):
    g = (
        df.groupby([df["published_at"].dt.to_period("M"),"politician"])
          .size().unstack(fill_value=0).reindex(columns=POLITS)
    )
    g.index = g.index.astype(str)
    g.plot(kind="bar", stacked=True, figsize=(12,6))
    plt.title("Статьи по месяцам"); plt.xlabel("Месяц"); plt.ylabel("Статей")
    plt.xticks(rotation=45, ha="right"); plt.tight_layout()
    plt.savefig(OUT/"monthly_mentions.png"); plt.close()

def cumulative_mentions(df):
    g = (
        df.groupby([df["published_at"].dt.date,"politician"])
          .size().unstack(fill_value=0).reindex(columns=POLITS)
          .cumsum()
    )
    plt.figure(figsize=(12,5))
    for p in POLITS: plt.plot(g.index, g[p], label=p, lw=2)
    plt.title("Накопленные упоминания"); plt.grid()
    plt.xlabel("Дата"); plt.ylabel("Всего статей")
    plt.legend(); plt.tight_layout()
    plt.savefig(OUT/"cumulative_mentions.png"); plt.close()

def source_top20(df):
    g = (
        df.groupby(["source","politician"]).size()
          .unstack(fill_value=0).assign(total=lambda x: x.sum(1))
          .sort_values("total", ascending=False).head(20).drop(columns="total")
    )
    g.plot(kind="barh", stacked=True, figsize=(10,8))
    plt.title("ТОП-20 источников"); plt.xlabel("Статей"); plt.ylabel("Источник")
    plt.legend(title="Политик"); plt.tight_layout()
    plt.savefig(OUT/"source_top20.png"); plt.close()

def source_sent_bar(df):
    g = (
        df[df["sentiment"].isin(["positive","negative"])]
          .groupby(["source","sentiment"]).size()
          .unstack(fill_value=0).assign(total=lambda x:x.sum(1))
          .sort_values("total", ascending=False).head(15).drop(columns="total")
    )
    g.plot(kind="bar", figsize=(12,6))
    plt.title("Позитив / негатив • ТОП-15 источников")
    plt.xticks(rotation=45, ha="right"); plt.tight_layout()
    plt.savefig(OUT/"source_sentiment_bar.png"); plt.close()

def heatmap_month(df):
    cutoff = END - timedelta(days=30)
    last = df[df["published_at"] >= cutoff]
    last["day"] = last["published_at"].dt.strftime("%m-%d")
    pivot = (
        last.groupby(["politician","day"]).size()
             .unstack(fill_value=0).reindex(index=POLITS)
    )
    plt.figure(figsize=(14,3))
    plt.imshow(pivot, aspect="auto", cmap="viridis")
    plt.yticks(range(len(POLITS)), POLITS)
    plt.xticks(range(len(pivot.columns)), pivot.columns,
               rotation=90, fontsize=6)
    plt.colorbar(label="Статей")
    plt.title("Тепловая карта: последние 30 дней")
    plt.tight_layout(); plt.savefig(OUT/"heatmap_month.png"); plt.close()

def weekday_pattern(df):
    df["weekday"] = df["published_at"].dt.day_name()
    order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    g = (
        df.groupby(["weekday","politician"]).size()
          .unstack(fill_value=0).reindex(order)
    )
    g.plot(kind="bar", stacked=True, figsize=(10,5))
    plt.title("Распределение по дням недели")
    plt.xlabel("День"); plt.ylabel("Статей"); plt.tight_layout()
    plt.savefig(OUT/"weekday_pattern.png"); plt.close()

def hourly_pattern(df):
    df["hour"] = df["published_at"].dt.hour
    g = (
        df.groupby(["hour","politician"]).size()
          .unstack(fill_value=0).reindex(columns=POLITS).sort_index()
    )
    g.plot(kind="bar", stacked=True, figsize=(10,5))
    plt.title("Распределение по часам суток (UTC)")
    plt.xlabel("Час"); plt.ylabel("Статей"); plt.tight_layout()
    plt.savefig(OUT/"hourly_pattern.png"); plt.close()

# ────────── main ──────────
def main():
    df = load()
    if df.empty:
        print("⚠️  Нет данных"); return
    timeline_mentions(df)
    stacked_mentions(df)
    sentiment_timeline(df)
    pie_sentiments(df)
    monthly_mentions(df)
    cumulative_mentions(df)
    source_top20(df)
    source_sent_bar(df)
    heatmap_month(df)
    weekday_pattern(df)
    hourly_pattern(df)
    print("✓ всё сохранено в graphs/ и news.csv")

if __name__ == "__main__":
    main()


