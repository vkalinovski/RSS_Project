import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Фильтр по дате: только с 1 января 2025 и до текущей даты
START_DATE = pd.to_datetime("2025-01-01")
END_DATE   = pd.to_datetime(pd.Timestamp.now().date())


def build_timeseries(df: pd.DataFrame) -> pd.DataFrame:
    """
    Строит DataFrame временных рядов: строки — даты (published_at),
    столбцы — политики, значение — число упоминаний.
    """
    df = df.copy()
    # приводим даты публикации к datetime и объединяем оба возможных поля
    if 'published_at' not in df.columns and 'published' in df.columns:
        df['published_at'] = df['published']
    df['published_at'] = pd.to_datetime(df['published_at'], errors='coerce')

    # Фильтруем период
    mask = (df['published_at'] >= START_DATE) & (df['published_at'] <= END_DATE)
    df = df.loc[mask]

    ts = (
        df
        .groupby(['published_at', 'politician'])
        .size()
        .unstack(fill_value=0)
    )
    ts.index = pd.to_datetime(ts.index)
    return ts.sort_index()


def plot_overall_timeseries(ts: pd.DataFrame, out_dir: str):
    """Ежедневные упоминания (с 2025-01-01 до сегодня)."""
    out_dir = Path(out_dir)
    ts = ts[(ts.index >= START_DATE) & (ts.index <= END_DATE)]

    plt.figure(figsize=(10, 5))
    for col in ts.columns:
        plt.plot(ts.index, ts[col], label=col)
    plt.title("Ежедневные упоминания (2025-01-01 — сегодня)")
    plt.xlabel("Дата")
    plt.ylabel("Частота упоминаний")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "overall_daily.png")
    plt.close()


def plot_weekly_aggregation(ts: pd.DataFrame, out_dir: str):
    """Недельные суммарные упоминания (с 2025-01-01 до сегодня)."""
    out_dir = Path(out_dir)
    subset = ts[(ts.index >= START_DATE) & (ts.index <= END_DATE)]
    weekly = subset.resample('W-MON').sum()

    plt.figure(figsize=(10, 5))
    for col in weekly.columns:
        plt.plot(weekly.index, weekly[col], marker='o', label=col)
    plt.title("Недельные упоминания (2025-01-01 — сегодня)")
    plt.xlabel("Неделя")
    plt.ylabel("Сумма упоминаний")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "weekly.png")
    plt.close()


def plot_monthly_aggregation(ts: pd.DataFrame, out_dir: str):
    """Месячные суммарные упоминания (с 2025-01-01 до сегодня)."""
    out_dir = Path(out_dir)
    subset = ts[(ts.index >= START_DATE) & (ts.index <= END_DATE)]
    monthly = subset.resample('MS').sum()

    plt.figure(figsize=(8, 5))
    monthly.plot(kind='bar')
    plt.title("Месячные упоминания (2025-01-01 — сегодня)")
    plt.xlabel("Месяц")
    plt.ylabel("Суммарное число упоминаний")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(out_dir / "monthly.png")
    plt.close()


def plot_cumulative(ts: pd.DataFrame, out_dir: str):
    """Кумулятивная кривая упоминаний (с 2025-01-01 до сегодня)."""
    out_dir = Path(out_dir)
    subset = ts[(ts.index >= START_DATE) & (ts.index <= END_DATE)]
    cum = subset.cumsum()

    plt.figure(figsize=(10, 5))
    for col in cum.columns:
        plt.plot(cum.index, cum[col], label=col)
    plt.title("Кумулятивные упоминания (2025-01-01 — сегодня)")
    plt.xlabel("Дата")
    plt.ylabel("Кумулятивное число")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "cumulative.png")
    plt.close()


def plot_top20_sources_bar(df: pd.DataFrame, out_dir: str):
    """Бар-чарт ТОП-20 источников за период (с 2025-01-01 до сегодня)."""
    out_dir = Path(out_dir)
    df = df.copy()
    if 'published_at' not in df.columns and 'published' in df.columns:
        df['published_at'] = df['published']
    df['published_at'] = pd.to_datetime(df['published_at'], errors='coerce')
    mask = (df['published_at'] >= START_DATE) & (df['published_at'] <= END_DATE)
    df = df.loc[mask]

    counts = df['source'].value_counts().head(20)
    plt.figure(figsize=(12, 6))
    counts.plot(kind='bar')
    plt.title("ТОП-20 источников (2025-01-01 — сегодня)")
    plt.xlabel("Источник")
    plt.ylabel("Количество упоминаний")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(out_dir / "top20_sources.png")
    plt.close()

