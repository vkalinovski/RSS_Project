import pandas as pd
import matplotlib.pyplot as plt


def build_timeseries(df: pd.DataFrame) -> pd.DataFrame:
    """
    Строит DataFrame с ежедневными счётчиками упоминаний каждого политика.
    Ожидает в df колонки 'published_at' (YYYY-MM-DD) и 'politician'.
    """
    # Если нужно, переименовываем
    if "published" in df.columns and "published_at" not in df.columns:
        df = df.rename(columns={"published": "published_at"})
    # Упорядочиваем даты
    df["published_at"] = pd.to_datetime(df["published_at"]).dt.strftime("%Y-%m-%d")

    # Группируем по дате и политику
    ts = df.groupby(["published_at", "politician"]).size().unstack(fill_value=0)
    ts.index = pd.to_datetime(ts.index)
    return ts.sort_index()


def plot_overall_timeseries(ts: pd.DataFrame, out_dir: str):
    """Ежедневные упоминания (с 2025-01-01 по сегодня)."""
    sub = ts[ts.index >= "2025-01-01"]
    plt.figure(figsize=(10, 5))
    for col in sub.columns:
        plt.plot(sub.index, sub[col], label=col)
    plt.title("Ежедневные упоминания (с 2025-01-01)")
    plt.xlabel("Дата")
    plt.ylabel("Частота")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{out_dir}/overall_daily.png")
    plt.close()


def plot_monthly_aggregation(ts: pd.DataFrame, out_dir: str):
    """Месячная агрегация упоминаний (начало каждого месяца)."""
    monthly = ts.resample("MS").sum()
    plt.figure(figsize=(10, 5))
    monthly.plot(kind="bar")
    plt.title("Месячные упоминания (с января 2025)")
    plt.xlabel("Месяц")
    plt.ylabel("Суммарное число упоминаний")
    plt.tight_layout()
    plt.savefig(f"{out_dir}/monthly.png")
    plt.close()


def plot_weekly_aggregation(ts: pd.DataFrame, out_dir: str):
    """Недельная агрегация упоминаний (понедельник)."""
    weekly = ts.resample("W-MON").sum()
    plt.figure(figsize=(10, 5))
    for col in weekly.columns:
        plt.plot(weekly.index, weekly[col], marker="o", label=col)
    plt.title("Недельные упоминания (с января 2025)")
    plt.xlabel("Неделя (Понедельник)")
    plt.ylabel("Сумма упоминаний")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{out_dir}/weekly.png")
    plt.close()


def plot_cumulative(ts: pd.DataFrame, out_dir: str):
    """Кумулятивное число упоминаний (с 2025-01-01)."""
    cum = ts.cumsum()
    cum = cum[cum.index >= "2025-01-01"]
    plt.figure(figsize=(10, 5))
    for col in cum.columns:
        plt.plot(cum.index, cum[col], label=col)
    plt.title("Кумулятивные упоминания (с 2025-01-01)")
    plt.xlabel("Дата")
    plt.ylabel("Кумулятивно")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{out_dir}/cumulative.png")
    plt.close()


def plot_sentiment_trends(df: pd.DataFrame, out_dir: str):
    """
    Тренд тональности по неделям для каждого политика.
    Ожидает столбцы 'published_at', 'politician', 'sentiment'.
    """
    # Определяем начало недели
    df["week_start"] = pd.to_datetime(df["published_at"]).dt.to_period("W").apply(lambda r: r.start_time)
    plt.figure(figsize=(10, 6))
    for pol in df["politician"].unique():
        sub = df[df["politician"] == pol]
        grouped = sub.groupby(["week_start", "sentiment"]).size().unstack(fill_value=0)
        for sentiment_label in grouped.columns:
            plt.plot(grouped.index, grouped[sentiment_label], marker="o", label=f"{pol} – {sentiment_label}")
    plt.title("Тональность по неделям (с 2025-01-01)")
    plt.xlabel("Неделя")
    plt.ylabel("Число статей")
    plt.legend(ncol=2, fontsize="small")
    plt.tight_layout()
    plt.savefig(f"{out_dir}/sentiment_trends.png")
    plt.close()


def plot_top_sources(df: pd.DataFrame, out_dir: str):
    """Топ-5 источников за весь период для каждого политика."""
    plt.figure(figsize=(12, 6))
    pols = df["politician"].unique()
    for i, pol in enumerate(pols, 1):
        plt.subplot(1, len(pols), i)
        top5 = df[df["politician"] == pol]["source"].value_counts().head(5)
        top5.plot(kind="bar")
        plt.title(pol)
        plt.xlabel("")
        plt.ylabel("Упоминаний")
    plt.suptitle("Топ-5 источников по политику (с 2025-01-01)")
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(f"{out_dir}/top_sources.png")
    plt.close()


def plot_top20_sources_bar(df: pd.DataFrame, out_dir: str):
    """ТОП-20 источников (>100 упоминаний) с января 2025."""
    mask = pd.to_datetime(df["published_at"]) >= pd.to_datetime("2025-01-01")
    counts = df[mask]["source"].value_counts()
    top20 = counts[counts > 100].head(20)
    plt.figure(figsize=(12, 6))
    top20.plot(kind="bar")
    plt.title("ТОП-20 источников (>100 упоминаний) с 2025-01-01")
    plt.xlabel("Источник")
    plt.ylabel("Упоминания")
    plt.tight_layout()
    plt.savefig(f"{out_dir}/top20_sources.png")
    plt.close()


def plot_top5_sources_timeseries(df: pd.DataFrame, out_dir: str):
    """Недельный тренд упоминаний топ-5 источников (с начала 2025)."""
    # Определяем топ-5 по общему количеству
    top5 = df["source"].value_counts().head(5).index
    df["date"] = pd.to_datetime(df["published_at"])  # для ресемплинга
    weekly_src = (
        df[df["source"].isin(top5)]
        .groupby([pd.Grouper(key="date", freq="W-MON"), "source"])  
        .size().unstack(fill_value=0)
    )
    plt.figure(figsize=(10, 5))
    for src in weekly_src.columns:
        plt.plot(weekly_src.index, weekly_src[src], marker="o", label=src)
    plt.title("Недельный тренд упоминаний топ-5 источников (с 2025-01-01)")
    plt.xlabel("Неделя")
    plt.ylabel("Упоминания")
    plt.legend(fontsize="small")
    plt.tight_layout()
    plt.savefig(f"{out_dir}/top5_sources_timeseries.png")
    plt.close()

