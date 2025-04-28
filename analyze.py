"""
Строит графики по базе и сохраняет PNG в папку graphs (создаётся авто-).
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

DB_PATH = Path(__file__).parent / "news.db"
OUT_DIR = Path(__file__).parent / "graphs"
OUT_DIR.mkdir(exist_ok=True)

POLITICIANS = ["Trump", "Putin", "Xi"]
START_DATE = datetime(2024, 9, 1).date()

def load_df():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(
        "SELECT published_at, politician, sentiment FROM news", conn
    )
    conn.close()
    df["published_at"] = pd.to_datetime(df["published_at"]).dt.date
    df = df[df["published_at"] >= START_DATE]
    df = df[df["politician"] != "Mixed"]
    return df

def timeline(df):
    grp = df.groupby(["published_at", "politician"]).size().unstack(fill_value=0)
    plt.figure(figsize=(12, 6))
    for name in POLITICIANS:
        if name in grp.columns:
            plt.plot(
                grp.index,
                grp[name].rolling(3).mean(),
                label=name,
                linewidth=2,
            )
    plt.title("Частота упоминаний (с 01-09-2024)")
    plt.xlabel("Дата")
    plt.ylabel("Кол-во упоминаний")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "mentions_timeline.png")
    plt.show()

def pie(df, politician):
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
    plt.title(f"Тональность: {politician}")
    plt.savefig(OUT_DIR / f"sentiment_{politician}.png")
    plt.show()

def main():
    df = load_df()
    if df.empty:
        print("Нет данных — соберите новости")
        return
    timeline(df)
    for p in POLITICIANS:
        pie(df, p)
    print("✅  Графики сохранены в", OUT_DIR)

if __name__ == "__main__":
    main()
