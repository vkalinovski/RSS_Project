import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# ————————————————————————————————————————————————
# Путь к базе данных: берем из переменной окружения OUT_DIR
OUT_DIR = os.environ.get('OUT_DIR', '.')
DB_PATH = os.path.join(OUT_DIR, 'news.db')
# ————————————————————————————————————————————————


def load_data(start_date_str: str = "2024-09-01") -> pd.DataFrame:
    """
    Загружает из SQLite все поля source, published_at, politician, sentiment,
    приводит published_at к дате и отсекает всё до start_date_str (в формате YYYY-MM-DD).
    Оставляет только наши три политики.
    """
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(
        "SELECT source, published_at, politician, sentiment FROM news",
        conn
    )
    conn.close()

    df["published_at"] = pd.to_datetime(df["published_at"]).dt.date
    start_date = datetime.fromisoformat(start_date_str).date()
    df = df[df["published_at"] >= start_date]

    # Оставляем только наши три категории
    df = df[df["politician"].isin([
        "Xi Jinping", "Donald Trump", "Vladimir Putin"
    ])]
    return df


def filter_sources_by_mentions(df: pd.DataFrame, threshold: int = 100) -> pd.DataFrame:
    """
    Оставляет из DataFrame только те записи, где источник
    имеет более threshold упоминаний.
    """
    counts = df["source"].value_counts()
    valid = counts[counts > threshold].index
    return df[df["source"].isin(valid)]


def analyze_mentions_scaled(df: pd.DataFrame):
    """Временной ряд частоты упоминаний (с сглаживанием)"""
    ts = df.groupby(["published_at", "politician"]).size().unstack(fill_value=0)
    plt.figure(figsize=(12, 6))
    y_max = ts.stack().quantile(0.95) * 1.1
    for pol in ts.columns:
        plt.plot(
            ts.index,
            ts[pol].rolling(window=3).mean(),
            label=pol, linewidth=2, alpha=0.7
        )
    plt.title("Частота упоминаний (с сентября 2024, сглажено)")
    plt.ylim(0, y_max)
    plt.xlabel("Дата"); plt.ylabel("Упоминания")
    plt.legend(title="Политик"); plt.grid(); plt.xticks(rotation=45)
    plt.show()


def analyze_mentions(df: pd.DataFrame):
    """Временной ряд частоты упоминаний (без дополнительной фильтрации)"""
    ts = df.groupby(["published_at", "politician"]).size().unstack(fill_value=0)
    plt.figure(figsize=(12, 6))
    for pol in ts.columns:
        plt.plot(
            ts.index,
            ts[pol].rolling(window=3).mean(),
            label=pol, linewidth=2, alpha=0.7
        )
    plt.title("Частота упоминаний (с сентября 2024, сглажено)")
    plt.xlabel("Дата"); plt.ylabel("Упоминания")
    plt.legend(title="Политик"); plt.grid(); plt.xticks(rotation=45)
    plt.show()


def analyze_sources_bar(df: pd.DataFrame):
    """Бар-чарт упоминаний по источникам (ТОП-20 с >100 упоминаниями)"""
    df2 = filter_sources_by_mentions(df, 100)
    cnt = df2.groupby(["source", "politician"]).size().unstack(fill_value=0)
    top20 = cnt.sum(axis=1).nlargest(20).index
    cnt = cnt.loc[top20]
    plt.figure(figsize=(14, 7))
    cnt.plot(kind="bar", stacked=True, width=0.8, ax=plt.gca())
    plt.title("Упоминания по источникам (ТОП-20, >100)")
    plt.xlabel("Источник"); plt.ylabel("Число упоминаний")
    plt.legend(title="Политик"); plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.xticks(rotation=45, ha="right"); plt.show()


def analyze_sources_pie(df: pd.DataFrame):
    """Круговая диаграмма: доли ТОП-10 источников + 'Другие'"""
    df2 = filter_sources_by_mentions(df, 100)
    counts = df2["source"].value_counts()
    top10 = counts.nlargest(10)
    other = counts.iloc[10:].sum()
    if other > 0:
        top10["Другие"] = other
    plt.figure(figsize=(10, 6))
    wedges, texts, autos = plt.pie(
        top10, labels=top10.index, autopct="%1.1f%%",
        startangle=140, wedgeprops={"edgecolor":"black"}, pctdistance=0.85
    )
    for t in texts + autos:
        t.set_fontsize(10)
    plt.title("Доли упоминаний по источникам (ТОП-10 + 'Другие')")
    plt.ylabel(""); plt.show()


def analyze_timeline_per_source(df: pd.DataFrame):
    """Временной ряд упоминаний по ТОП-10 источникам (с сглаживанием)"""
    df2 = filter_sources_by_mentions(df, 100)
    ts = df2.groupby(["published_at", "source"]).size().unstack(fill_value=0)
    top10 = ts.sum().nlargest(10).index
    ts = ts[top10]
    plt.figure(figsize=(14, 7))
    for src in ts.columns:
        plt.plot(
            ts.index, ts[src].rolling(window=3).mean(),
            label=src, linewidth=2, alpha=0.7
        )
    plt.title("Упоминания по источникам (ТОП-10, сглажено)")
    plt.xlabel("Дата"); plt.ylabel("Упоминания")
    plt.legend(title="Источник", bbox_to_anchor=(1.05,1), loc="upper left")
    plt.grid(axis="y", linestyle="--", alpha=0.7); plt.xticks(rotation=45)
    plt.show()


# —————————— SENTIMENT ——————————

def analyze_sentiment_pie(df: pd.DataFrame, politician: str):
    """Круговая диаграмма тональности для каждого политика"""
    sub = df[df["politician"] == politician]
    if sub.empty:
        print(f"Нет данных для {politician}")
        return
    cnt = sub["sentiment"].value_counts()
    plt.figure(figsize=(8, 6))
    plt.pie(cnt, labels=cnt.index, autopct="%1.1f%%",
            startangle=140, wedgeprops={"edgecolor":"black"})
    plt.title(f"Тональность новостей о {politician}"); plt.show()


def compare_sentiment_distribution(df: pd.DataFrame):
    """Сравнение тональности по политикам (bar-chart)"""
    pivot = df.groupby(["politician","sentiment"]).size().unstack(fill_value=0)
    plt.figure(figsize=(8, 6))
    pivot.plot(kind="bar", width=0.8)
    plt.title("Тональность по политикам")
    plt.xlabel("Политик"); plt.ylabel("Число упоминаний")
    plt.xticks(rotation=0); plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.show()


def plot_sentiment_over_time(df: pd.DataFrame):
    """Динамика тональности по неделям для всех политиков"""
    df2 = df.copy()
    df2["published_at"] = pd.to_datetime(df2["published_at"])
    df2["week"] = df2["published_at"].dt.to_period('W-MON').apply(lambda r: r.start_time)
    grp = df2.groupby(["week","politician","sentiment"]).size().reset_index(name="count")
    plt.figure(figsize=(12, 6))
    for pol in grp["politician"].unique():
        sub = grp[grp["politician"] == pol].pivot("week","sentiment","count").fillna(0)
        for sentiment in sub.columns:
            plt.plot(sub.index, sub[sentiment], marker='o', label=f"{pol} – {sentiment}")
    plt.title("Тональность по неделям")
    plt.xlabel("Неделя"); plt.ylabel("Число статей")
    plt.legend(); plt.xticks(rotation=45); plt.tight_layout(); plt.show()


# —————————— MAIN ——————————

if __name__ == "__main__":
    df = load_data("2024-09-01")
    if df.empty:
        print("⚠️ Нет данных с сентября 2024!")
    else:
        analyze_mentions_scaled(df)
        analyze_mentions(df)
        analyze_sources_bar(df)
        analyze_sources_pie(df)
        analyze_timeline_per_source(df)
        for pol in ["Xi Jinping", "Donald Trump", "Vladimir Putin"]:
            analyze_sentiment_pie(df, pol)
        compare_sentiment_distribution(df)
        plot_sentiment_over_time(df)
