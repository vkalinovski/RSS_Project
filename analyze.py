# File: RSS_Project/analyze.py

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
from database_utils import DB_PATH

# Стартовая дата
START_DATE = pd.to_datetime("2024-09-01").date()

def load_data():
    """
    Загружает из SQLite колонки source, published_at, politician, sentiment,
    приводит published_at к date и отсекает всё до START_DATE.
    """
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT source, published_at, politician, sentiment FROM news", conn)
    conn.close()

    df["published_at"] = pd.to_datetime(df["published_at"]).dt.date
    df = df[df["published_at"] >= START_DATE]
    # Оставляем только нужные категории
    df = df[df["politician"].isin(["Trump", "Xi Jinping", "Putin", "Multiple"])]
    return df

def build_timeseries(df: pd.DataFrame) -> pd.DataFrame:
    """Собирает DataFrame с датами и упоминаниями каждого политика."""
    ts = (
        df
        .groupby(["published_at", "politician"])
        .size()
        .unstack(fill_value=0)
        .sort_index()
    )
    ts.index = pd.to_datetime(ts.index)
    return ts

def plot_overall_timeseries(ts: pd.DataFrame, out_dir: Path):
    """Ежедневный временной ряд."""
    fig, ax = plt.subplots(figsize=(12, 6))
    for col in ts.columns:
        ax.plot(ts.index, ts[col], label=col, linewidth=2, alpha=0.8)
    ax.set_title("Ежедневные упоминания (с 2024-09-01)")
    ax.set_xlabel("Дата")
    ax.set_ylabel("Число упоминаний")
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
    ax.legend(title="Политик")
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(out_dir / "overall_daily.png")
    plt.close(fig)

def plot_weekly_aggregation(ts: pd.DataFrame, out_dir: Path):
    """Недельная агрегация (понедельник→понедельник)."""
    weekly = ts.resample("W-MON").sum()
    fig, ax = plt.subplots(figsize=(12, 6))
    for col in weekly.columns:
        ax.plot(weekly.index, weekly[col], marker="o", label=col)
    ax.set_title("Недельные упоминания (с 2024-09-01)")
    ax.set_xlabel("Неделя")
    ax.set_ylabel("Сумма упоминаний")
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
    ax.legend(title="Политик")
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(out_dir / "weekly.png")
    plt.close(fig)

def plot_monthly_aggregation(ts: pd.DataFrame, out_dir: Path):
    """Месячная агрегация."""
    monthly = ts.resample("MS").sum()
    fig, ax = plt.subplots(figsize=(10, 5))
    monthly.plot(kind="bar", ax=ax)
    ax.set_title("Месячные упоминания (с 2024-09-01)")
    ax.set_xlabel("Месяц")
    ax.set_ylabel("Сумма упоминаний")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    fig.tight_layout()
    fig.savefig(out_dir / "monthly.png")
    plt.close(fig)

def plot_cumulative(ts: pd.DataFrame, out_dir: Path):
    """Кумулятивный график."""
    cum = ts.cumsum()
    fig, ax = plt.subplots(figsize=(12, 6))
    for col in cum.columns:
        ax.plot(cum.index, cum[col], label=col, linewidth=2)
    ax.set_title("Кумулятивные упоминания (с 2024-09-01)")
    ax.set_xlabel("Дата")
    ax.set_ylabel("Накопленное число")
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
    ax.legend(title="Политик")
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(out_dir / "cumulative.png")
    plt.close(fig)

def plot_sentiment_trends(df: pd.DataFrame, out_dir: Path):
    """Тональность по неделям."""
    df2 = df.copy()
    df2["week"] = pd.to_datetime(df2["published_at"]).dt.to_period("W-MON").apply(lambda r: r.start_time)
    fig, ax = plt.subplots(figsize=(12, 6))
    for pol in df2["politician"].unique():
        pivot = df2[df2["politician"] == pol].groupby(["week", "sentiment"]).size().unstack(fill_value=0)
        for s in pivot.columns:
            ax.plot(pivot.index.to_timestamp(), pivot[s], marker="o", label=f"{pol} – {s}")
    ax.set_title("Тональность по неделям (с 2024-09-01)")
    ax.set_xlabel("Неделя")
    ax.set_ylabel("Кол-во статей")
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
    ax.legend()
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(out_dir / "sentiment_trends.png")
    plt.close(fig)

def plot_top_sources(df: pd.DataFrame, out_dir: Path):
    """Топ-5 источников для каждого политика."""
    df2 = df[df["politician"] != "Multiple"]
    for pol in ["Trump", "Xi Jinping", "Putin"]:
        cnt = df2[df2["politician"] == pol]["source"].value_counts().head(5)
        fig, ax = plt.subplots(figsize=(6, 4))
        cnt.plot(kind="bar", ax=ax)
        ax.set_title(f"Топ-5 источников: {pol}")
        ax.set_xlabel("Источник")
        ax.set_ylabel("Упоминания")
        ax.tick_params(axis="x", rotation=45)
        ax.grid(axis="y", linestyle="--", alpha=0.7)
        fig.tight_layout()
        fig.savefig(out_dir / f"top5_{pol.replace(' ', '_')}.png")
        plt.close(fig)

def plot_all(out_dir: Path):
    """Вызывает все графики и сохраняет CSV."""
    df = load_data()
    ts = build_timeseries(df)
    out_dir.mkdir(exist_ok=True, parents=True)
    (out_dir / "timeseries.csv").write_text(ts.to_csv())
    plot_overall_timeseries(ts, out_dir)
    plot_weekly_aggregation(ts, out_dir)
    plot_monthly_aggregation(ts, out_dir)
    plot_cumulative(ts, out_dir)
    plot_sentiment_trends(df, out_dir)
    plot_top_sources(df, out_dir)
