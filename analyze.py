import sqlite3
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd

DB_PATH = "news.db"
POLITICIANS = ["Trump", "Putin", "Xi"]  # актуальный список


def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(
        "SELECT source, published_at, politician, sentiment FROM news", conn
    )
    conn.close()

    df["published_at"] = pd.to_datetime(df["published_at"]).dt.date
    df = df[df["published_at"] >= datetime(2024, 9, 1).date()]  # новая отсечка
    df = df[df["politician"] != "Mixed"]  # исключаем «смешанные» статьи
    return df


def filter_sources_by_mentions(df, threshold=100):
    counts = df["source"].value_counts()
    good = counts[counts > threshold].index
    return df[df["source"].isin(good)]


# ---------- Временной ряд по политикам ---------- #
def plot_mentions(df):
    g = df.groupby(["published_at", "politician"]).size().unstack(fill_value=0)

    plt.figure(figsize=(12, 6))
    for name in POLITICIANS:
        if name in g.columns:
            plt.plot(
                g.index,
                g[name].rolling(window=3).mean(),
                label=name,
                linewidth=2,
                alpha=0.8,
            )

    plt.title("Частота упоминаний (с 01-09-2024)")
    plt.xlabel("Дата")
    plt.ylabel("Количество упоминаний")
    plt.grid(True)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


# ---------- Тональность ---------- #
def sentiment_pie(df, politician):
    sub = df[df["politician"] == politician]
    if sub.empty:
        return
    counts = sub["sentiment"].value_counts()
    plt.figure(figsize=(5, 5))
    plt.pie(
        counts,
        labels=counts.index,
        autopct="%1.1f%%",
        startangle=140,
        wedgeprops={"edgecolor": "black"},
    )
    plt.title(f"Тональность новостей о {politician}")
    plt.show()


# ---------- Main ---------- #
if __name__ == "__main__":
    data = load_data()
    if data.empty:
        print("Нет данных после 01-09-2024, сначала соберите новости.")
    else:
        plot_mentions(data)
        for p in POLITICIANS:
            sentiment_pie(data, p)
