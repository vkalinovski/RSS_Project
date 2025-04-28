import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

DB_PATH = "news.db"

def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT source, published_at, politician, sentiment FROM news", conn)
    conn.close()
    df["published_at"] = pd.to_datetime(df["published_at"]).dt.date
    df = df[df["published_at"] >= datetime(2024,11,1).date()]
    df = df[~df["politician"].isin(["Multiple"])]
    return df

def analyze_mentions(df, smooth=True):
    grp = df.groupby(["published_at","politician"]).size().unstack(fill_value=0)
    plt.figure(figsize=(12,6))
    ymax = grp.stack().quantile(0.95)*1.1
    for col in grp:
        series = grp[col].rolling(window=3).mean() if smooth else grp[col]
        plt.plot(grp.index, series, label=col)
    plt.title("Упоминания политиков в СМИ с ноября 2024")
    plt.xlabel("Дата"); plt.ylabel("Количество")
    plt.ylim(0,ymax)
    plt.legend(); plt.grid(); plt.xticks(rotation=45)
    plt.show()

def analyze_sources_bar(df):
    counts = df.groupby(["source","politician"]).size().unstack(fill_value=0)
    top = counts.sum(axis=1).nlargest(20).index
    counts = counts.loc[top]
    counts.plot.bar(stacked=True, figsize=(14,6))
    plt.title("ТОП-20 источников по упоминаниям"); plt.ylabel("Количество"); plt.xticks(rotation=45,ha="right")
    plt.show()

def sentiment_pie(df, pol):
    sub = df[df["politician"]==pol]
    cnt = sub["sentiment"].value_counts()
    cnt.plot.pie(autopct="%1.1f%%", startangle=140, wedgeprops={"edgecolor":"black"}, figsize=(6,6))
    plt.title(f"Тональность для {pol}")
    plt.ylabel(""); plt.show()

def compare_sentiments(df):
    cnt = df.groupby(["politician","sentiment"]).size().unstack(fill_value=0)
    cnt.plot.bar(figsize=(8,6))
    plt.title("Сравнение тональностей"); plt.ylabel("Количество"); plt.xticks(rotation=0); plt.grid(axis="y"); plt.show()

def main():
    df = load_data()
    if df.empty:
        print("Нет данных для анализа.")
        return
    analyze_mentions(df, smooth=True)
    analyze_mentions(df, smooth=False)
    analyze_sources_bar(df)
    for pol in ["Trump","Putin","Xi Jinping"]:
        sentiment_pie(df, pol)
    compare_sentiments(df)

if __name__ == "__main__":
    main()

