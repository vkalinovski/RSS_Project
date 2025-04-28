# File: RSS_Project/analyze.py

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
from database_utils import DB_PATH
from datetime import datetime

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
    # Оставляем только интересующие категории
    df = df[df["politician"].isin(["Trump", "Biden", "Trump/Biden"])]
    return df

def build_timeseries(df: pd.DataFrame) -> pd.DataFrame:
    """Собирает DataFrame с датами и упоминаниями каждого политика."""
    ts = (
        df
        .groupby(["published_at","politician"])
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
    ax.set_xlabel("Дата"); ax.set_ylabel("Число упоминаний")
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
    ax.legend(title="Политик"); ax.grid(True)
    fig.tight_layout()
    fig.savefig(out_dir/"overall_daily.png")
    plt.close(fig)

# (Остальные функции plot_weekly_aggregation, plot_monthly_aggregation, plot_cumulative,
#  plot_sentiment_trends, plot_top_sources остаются без изменений)

def plot_all(out_dir: Path):
    """Вызывает все графики и сохраняет CSV."""
    df = load_data()
    ts = build_timeseries(df)
    out_dir.mkdir(exist_ok=True, parents=True)
    (out_dir/"timeseries.csv").write_text(ts.to_csv())
    plot_overall_timeseries(ts, out_dir)
    # … вызываем остальные plot_* аналогично …

