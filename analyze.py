import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Все даты до этой отбрасываются
START_DATE = pd.to_datetime("2025-01-01")


def build_timeseries(df: pd.DataFrame) -> pd.DataFrame:
    """
    Переименовываем колонку и строим временной ряд:
    строки — даты (published_at), столбцы — политики, значение — число упоминаний.
    """
    df = df.rename(columns={'published': 'published_at'})
    df['published_at'] = pd.to_datetime(df['published_at'])
    df = df[df['published_at'] >= START_DATE]

    ts = (
        df
        .groupby(['published_at', 'politician'])
        .size()
        .unstack(fill_value=0)
    )
    ts.index = pd.to_datetime(ts.index)
    return ts.sort_index()


def plot_overall_timeseries(ts: pd.DataFrame, out_dir: str):
    """Ежедневные упоминания (с 2025-01-01)."""
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
    """Недельные суммарные упоминания (с 2025-01-01)."""
    out_dir = Path(out_dir)
    weekly = ts.resample('W-MON').sum()

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
    """Месячные суммарные упоминания (с 2025-01-01)."""
    out_dir = Path(out_dir)
    monthly = ts.resample('MS').sum()

    plt.figure(figsize=(8, 5))
    monthly.plot(kind='bar')
    plt.title("Месячные упоминания (с 2025-01-01)")
    plt.xlabel("Месяц")
    plt.ylabel("Суммарное число упоминаний")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(out_dir / "monthly.png")
    plt.close()


def plot_cumulative(ts: pd.DataFrame, out_dir: str):
    """Кумулятивная кривая упоминаний (с 2025-01-01)."""
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
    """Тренд тональности по неделям (с 2025-01-01)."""
    out_dir = Path(out_dir)
    df = df.rename(columns={'published': 'published_at'})
    df['published_at'] = pd.to_datetime(df['published_at'])
    df = df[df['published_at'] >= START_DATE]
    df['week'] = df['published_at'].dt.to_period('W-MON').apply(lambda r: r.start_time)

    plt.figure(figsize=(10, 5))
    for pol in df['politician'].unique():
        sub = df[df['politician'] == pol]
        pivot = sub.groupby(['week', 'sentiment']).size().unstack(fill_value=0)
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
    """Топ-5 источников для каждого политика (с 2025-01-01)."""
    out_dir = Path(out_dir)
    df = df.rename(columns={'published': 'published_at'})
    df['published_at'] = pd.to_datetime(df['published_at'])
    df = df[df['published_at'] >= START_DATE]

    for pol in df['politician'].unique():
        counts = df[df['politician'] == pol]['source'].value_counts().head(5)
        plt.figure(figsize=(6, 4))
        counts.plot(kind='bar')
        plt.title(f"Топ-5 источников: {pol}")
        plt.xlabel("Источник")
        plt.ylabel("Упоминаний")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(out_dir / f"top_sources_{pol.replace(' ', '_')}.png")
        plt.close()


def plot_top20_sources_bar(df: pd.DataFrame, out_dir: str):
    """Бар-чарт ТОП-20 источников (>100 упоминаний с 2025-01-01)."""
    out_dir = Path(out_dir)
    df = df.rename(columns={'published': 'published_at'})
    df['published_at'] = pd.to_datetime(df['published_at'])
    df = df[df['published_at'] >= START_DATE]

    counts = df['source'].value_counts()
    top20 = counts[counts > 100].head(20)
    if top20.empty:
        print("plot_top20_sources_bar: нет источников с более чем 100 упоминаниями.")
        return

    plt.figure(figsize=(12, 6))
    top20.plot(kind='bar')
    plt.title("ТОП-20 источников (>100 упоминаний с 2025-01-01)")
    plt.xlabel("Источник")
    plt.ylabel("Количество упоминаний")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(out_dir / "top20_sources.png")
    plt.close()


def plot_top5_sources_timeseries(df: pd.DataFrame, out_dir: str):
    """Временные ряды по ТОП-5 источникам (с 2025-01-01)."""
    out_dir = Path(out_dir)
    df = df.rename(columns={'published': 'published_at'})
    df['published_at'] = pd.to_datetime(df['published_at'])
    df = df[df['published_at'] >= START_DATE]

    top5 = df['source'].value_counts().head(5).index
    # группируем по source и дате, затем транспонируем
    ts = (
        df
        .groupby(['source', 'published_at'])
        .size()
        .unstack(fill_value=0)
        .loc[top5]
        .T
    )

    plt.figure(figsize=(10, 5))
    for src in ts.columns:
        plt.plot(ts.index, ts[src], label=src)
    plt.title("Упоминания ТОП-5 источников (с 2025-01-01)")
    plt.xlabel("Дата")
    plt.ylabel("Упоминаний")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "top5_sources_timeseries.png")
    plt.close()

