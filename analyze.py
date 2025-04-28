# File: RSS_Project/analyze.py

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

def build_timeseries(df: pd.DataFrame) -> pd.DataFrame:
    """
    Строит DataFrame временных рядов: строки — даты (published_at),
    столбцы — политики, значение — число упоминаний.
    """
    # Группируем по дате и политику
    ts = (
        df
        .groupby(['published_at', 'politician'])
        .size()
        .unstack(fill_value=0)
    )
    # Индекс в datetime для корректного сортирования и работы matplotlib
    ts.index = pd.to_datetime(ts.index)
    return ts.sort_index()

def plot_overall_timeseries(ts: pd.DataFrame, out_dir: str):
    """Ежедневные упоминания с 2025-01-01."""
    out_dir = Path(out_dir)
    plt.figure(figsize=(10, 5))
    for col in ts.columns:
        plt.plot(ts.index, ts[col], label=col)
    plt.title("Ежедневные упоминания (с 2025-01-01)")
    plt.xlabel("Дата")
    plt.ylabel("Частота упоминаний")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "overall_daily.png")
    plt.close()

def plot_weekly_aggregation(ts: pd.DataFrame, out_dir: str):
    """Недельные суммарные упоминания."""
    out_dir = Path(out_dir)
    weekly = ts.resample('W-MON').sum()   # неделя по понедельникам
    plt.figure(figsize=(10, 5))
    for col in weekly.columns:
        plt.plot(weekly.index, weekly[col], marker='o', label=col)
    plt.title("Недельные упоминания (с 2025-01-01)")
    plt.xlabel("Неделя")
    plt.ylabel("Сумма упоминаний")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "weekly.png")
    plt.close()

def plot_monthly_aggregation(ts: pd.DataFrame, out_dir: str):
    """Месячные суммарные упоминания."""
    out_dir = Path(out_dir)
    monthly = ts.resample('MS').sum()    # начало каждого месяца
    monthly.plot(
        kind='bar',
        figsize=(8, 5)
    )
    plt.title("Месячные упоминания (с 2025-01-01)")
    plt.xlabel("Месяц")
    plt.ylabel("Суммарное число упоминаний")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(out_dir / "monthly.png")
    plt.close()

def plot_cumulative(ts: pd.DataFrame, out_dir: str):
    """Кумулятивная кривая упоминаний."""
    out_dir = Path(out_dir)
    cum = ts.cumsum()
    plt.figure(figsize=(10, 5))
    for col in cum.columns:
        plt.plot(cum.index, cum[col], label=col)
    plt.title("Кумулятивные упоминания (с 2025-01-01)")
    plt.xlabel("Дата")
    plt.ylabel("Кумулятивное число")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "cumulative.png")
    plt.close()

def plot_sentiment_trends(df: pd.DataFrame, out_dir: str):
    """
    Тренд тональности по неделям для каждой пары (политик, sentiment).
    """
    out_dir = Path(out_dir)
    df = df.copy()
    # неделя по понедельникам
    df['week'] = pd.to_datetime(df['published_at']).dt.to_period('W-MON').apply(lambda r: r.start_time)
    for pol in df['politician'].unique():
        sub = df[df['politician'] == pol]
        # свод: строки — week, столбцы — sentiment, значения — count
        pivot = sub.groupby(['week', 'sentiment']).size().unstack(fill_value=0)
        plt.figure(figsize=(10,5))
        for sentiment in pivot.columns:
            plt.plot(pivot.index, pivot[sentiment], marker='o', label=f"{pol} – {sentiment}")
    plt.title("Тональность по неделям (с 2025-01-01)")
    plt.xlabel("Неделя")
    plt.ylabel("Число статей")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "sentiment_trends.png")
    plt.close()

def plot_top_sources(df: pd.DataFrame, out_dir: str):
    """Топ-5 источников для каждого политика."""
    out_dir = Path(out_dir)
    for pol in df['politician'].unique():
        counts = df[df['politician'] == pol]['source'].value_counts().head(5)
        plt.figure(figsize=(6,4))
        counts.plot(kind='bar')
        plt.title(f"Топ-5 источников: {pol}")
        plt.xlabel("Источник")
        plt.ylabel("Упоминаний")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(out_dir / f"top_sources_{pol.replace(' ', '_')}.png")
        plt.close()

def plot_top20_sources_bar(df: pd.DataFrame, out_dir: str):
    """
    Бар-чарт ТОП-20 источников, у которых >100 упоминаний
    (с января 2025).
    """
    out_dir = Path(out_dir)
    counts = df['source'].value_counts()
    top20 = counts[counts > 100].head(20)
    if top20.empty:
        print("plot_top20_sources_bar: нет источников с более чем 100 упоминаниями.")
        return
    plt.figure(figsize=(12,6))
    top20.plot(kind='bar')
    plt.title("ТОП-20 источников (>100 упоминаний с 2025-01-01)")
    plt.xlabel("Источник")
    plt.ylabel("Количество упоминаний")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(out_dir / "top20_sources.png")
    plt.close()

def plot_top5_sources_timeseries(df: pd.DataFrame, out_dir: str):
    """
    Временные ряды по 5 самым активным источникам.
    """
    out_dir = Path(out_dir)
    # считаем общее число упоминаний источника
    top5 = df['source'].value_counts().head(5).index
    ts = (
        pd.to_datetime(df['published_at'])
        .groupby([df['source'], df['published_at']])
        .size()
        .unstack(fill_value=0)
        .loc[top5]
        .T
    )
    plt.figure(figsize=(10,5))
    for src in ts.columns:
        plt.plot(ts.index, ts[src], label=src)
    plt.title("Временные ряды по ТОП-5 источникам")
    plt.xlabel("Дата")
    plt.ylabel("Упоминаний")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "top5_sources_timeseries.png")
    plt.close()

