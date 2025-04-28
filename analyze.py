import pandas as pd, matplotlib.pyplot as plt, sqlite3, pathlib, csv
from datetime import datetime
from database import DB_PATH, ROOT_DIR

OUT = ROOT_DIR
OUT.mkdir(exist_ok=True)

POL=["Trump","Putin","Xi"]

def load():
    with sqlite3.connect(DB_PATH) as c:
        df=pd.read_sql("SELECT published_at,politician,sentiment FROM news",c)
    df["published_at"]=pd.to_datetime(df["published_at"]).dt.date
    return df[df["published_at"]>=datetime(2024,9,1).date()]

def timeline(df):
    g=df.groupby(["published_at","politician"]).size().unstack(fill_value=0)
    plt.figure(figsize=(12,6))
    for p in POL:
        if p in g: plt.plot(g.index,g[p].rolling(3).mean(),label=p)
    plt.legend(); plt.grid(); plt.xticks(rotation=45); plt.tight_layout()
    plt.savefig(OUT/"mentions.png"); plt.close()

def to_csv(df):
    df.to_csv(OUT/"news_dump.csv",index=False)

def main():
    d=load(); timeline(d); to_csv(d); print("✓ графики и CSV сохранены")

if __name__=="__main__": main()
