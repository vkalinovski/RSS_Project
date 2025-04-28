"""
Сохраняет:
  • graphs/mentions_timeline.png
  • graphs/sentiment_<политик>.png
  • news.csv (полный дамп таблицы)
"""

import sqlite3, pandas as pd, matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

ROOT   = Path(__file__).parent
DB     = ROOT/"news.db"
GRAPH  = ROOT/"graphs"
GRAPH.mkdir(exist_ok=True)

POLIT = ["Trump","Putin","Xi"]
START = datetime(2024,9,1).date()

def load():
    with sqlite3.connect(DB) as c:
        df = pd.read_sql("SELECT * FROM news", c)
    df["published_at"] = pd.to_datetime(df["published_at"]).dt.date
    df = df[df["published_at"]>=START]
    df.to_csv(ROOT/"news.csv", index=False)
    return df

def timeline(df):
    g = df.groupby(["published_at","politician"]).size().unstack(fill_value=0)
    plt.figure(figsize=(12,5))
    for p in POLIT:
        if p in g.columns:
            plt.plot(g.index, g[p].rolling(3).mean(), label=p, linewidth=2)
    plt.title("Упоминания в новостях"); plt.grid(); plt.legend()
    plt.xticks(rotation=45); plt.tight_layout()
    plt.savefig(GRAPH/"mentions_timeline.png"); plt.show()

def pie(df,p):
    sub=df[df["politician"]==p]
    if sub.empty: return
    counts=sub["sentiment"].value_counts()
    plt.figure(figsize=(4,4))
    plt.pie(counts,labels=counts.index,autopct="%1.1f%%",startangle=140)
    plt.title(f"Тональность: {p}")
    plt.savefig(GRAPH/f"sentiment_{p}.png"); plt.show()

def main():
    df=load()
    if df.empty: return print("нет данных")
    timeline(df)
    for p in POLIT: pie(df,p)
    print("✓ графики и CSV сохранены")

if __name__=="__main__":
    main()
