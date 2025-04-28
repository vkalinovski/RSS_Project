import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Диапазон дат: с 1 января 2025 до сегодня
START_DATE = pd.to_datetime("2025-01-01")
END_DATE = pd.to_datetime("today")


def build_timeseries(df: pd.DataFrame) -> pd.DataFrame:
    """
    Строит DataFrame ежедневных упоминаний по политикам
    из df, содержащего столбцы 'published' или 'published_at'.
    Индекс — даты, колонки — политики, значение — число упоминаний.
    """
    df = df.copy()
    # Переименовываем колонку 'published', если она есть
    if 'published' in df.columns:
        df = df.rename(columns={'published': 'published_at'})
    # Парсим даты
    df['published_at'] = pd.to_datetime(df['published_at'])
    # Фильтруем по диапазону
    mask = (df['published_at'] >= START_DATE) & (df['published_at'] <= END_DATE)
    df = df.loc[mask]
    # Группируем по дате и политику
    daily = (
        df.groupby([df['published_at'].dt.date, 'politician'])
          .size()
          .unstack(fill_value=0)
    )
    daily.index = pd.to_datetime(daily.index)
    return daily


def plot_overall_daily(ts: pd.DataFrame, out_dir: str):
    """Ежедневные упоминания с 2025-01-01 до сегодня"""
    out_dir = Path(out_dir)
    plt.figure(figsize=(12, 6))
    for col in ts.columns:
        plt.plot(ts.index, ts[col], label=col)
    plt.title("Ежедневные упоминания (2025-01-01 – сегодня)")
    plt.xlabel("Дата")
    plt.ylabel("Частота упоминаний")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "overall_daily.png")
    plt.close()


def plot_weekly(ts: pd.DataFrame, out_dir: str):
    """Недельные суммарные упоминания"""
    out_dir = Path(out_dir)
    weekly = ts.resample('W').sum()
    plt.figure(figsize=(12, 6))
    for col in weekly.columns:
        plt.plot(weekly.index, weekly[col], marker='o', label=col)
    plt.title("Недельные упоминания (2025)")
    plt.xlabel("Начало недели")
    plt.ylabel("Сумма упоминаний")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "weekly.png")
    plt.close()


def plot_monthly(ts: pd.DataFrame, out_dir: str):
    """Месячные суммарные упоминания"""
    out_dir = Path(out_dir)
    monthly = ts.resample('MS').sum()
    plt.figure(figsize=(10, 6))
    monthly.plot(kind='bar')
    plt.title("Месячные упоминания (2025)")
    plt.xlabel("Месяц")
    plt.ylabel("Сумма упоминаний")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(out_dir / "monthly.png")
    plt.close()


def plot_cumulative(ts: pd.DataFrame, out_dir: str):
    """Кумулятивный график упоминаний"""
    out_dir = Path(out_dir)
    cum = ts.cumsum()
    plt.figure(figsize=(12, 6))
    for col in cum.columns:
        plt.plot(cum.index, cum[col], label=col)
    plt.title("Кумулятивные упоминания (2025)")
    plt.xlabel("Дата")
    plt.ylabel("Накопленное кол-во упоминаний")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "cumulative.png")
    plt.close()


def plot_top20_sources(df: pd.DataFrame, out_dir: str):
    """ТОП-20 источников по числу упоминаний"""
    out_dir = Path(out_dir)
    d = df.copy()
    if 'published' in d.columns:
        d = d.rename(columns={'published': 'published_at'})
    d['published_at'] = pd.to_datetime(d['published_at'])
    d = d[(d['published_at'] >= START_DATE) & (d['published_at'] <= END_DATE)]
    top20 = d['source'].value_counts().head(20)
    plt.figure(figsize=(12, 6))
    top20.plot(kind='bar')
    plt.title("ТОП-20 источников (2025)")
    plt.xlabel("Источник")
    plt.ylabel("Количество упоминаний")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(out_dir / "top20_sources.png")
    plt.close()
