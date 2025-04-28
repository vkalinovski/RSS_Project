import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Анализ с сентября 2024
START_DATE = pd.to_datetime("2024-09-01")

def build_timeseries(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['published_at'] = pd.to_datetime(df['published_at'])
    df = df[df['published_at'] >= START_DATE]
    ts = df.groupby(['published_at','politician']).size().unstack(fill_value=0)
    ts.index = pd.to_datetime(ts.index)
    return ts.sort_index()

def plot_overall_timeseries(ts: pd.DataFrame, out_dir: str):
    out_dir = Path(out_dir); ts = ts[ts.index>=START_DATE]
    plt.figure(figsize=(10,5))
    for col in ts.columns:
        plt.plot(ts.index, ts[col], label=col)
    plt.title("Ежедневные упоминания (с 2024-09-01)"); plt.xlabel("Дата"); plt.ylabel("Частота")
    plt.legend(); plt.tight_layout(); plt.savefig(out_dir/"overall_daily.png"); plt.close()

def plot_weekly_aggregation(ts: pd.DataFrame, out_dir: str):
    out_dir = Path(out_dir); ts = ts[ts.index>=START_DATE]
    weekly = ts.resample('W-MON').sum()
    plt.figure(figsize=(10,5))
    for col in weekly.columns:
        plt.plot(weekly.index, weekly[col], marker='o', label=col)
    plt.title("Недельные упоминания (с 2024-09-01)"); plt.xlabel("Неделя"); plt.ylabel("Сумма")
    plt.legend(); plt.tight_layout(); plt.savefig(out_dir/"weekly.png"); plt.close()

def plot_monthly_aggregation(ts: pd.DataFrame, out_dir: str):
    out_dir = Path(out_dir); ts = ts[ts.index>=START_DATE]
    monthly = ts.resample('MS').sum()
    plt.figure(figsize=(8,5)); monthly.plot(kind='bar')
    plt.title("Месячные упоминания (с 2024-09-01)"); plt.xlabel("Месяц"); plt.ylabel("Сумма")
    plt.xticks(rotation=45, ha='right'); plt.tight_layout()
    plt.savefig(out_dir/"monthly.png"); plt.close()

def plot_cumulative(ts: pd.DataFrame, out_dir: str):
    out_dir = Path(out_dir); ts = ts[ts.index>=START_DATE]
    cum = ts.cumsum()
    plt.figure(figsize=(10,5))
    for col in cum.columns:
        plt.plot(cum.index, cum[col], label=col)
    plt.title("Кумулятивные упоминания (с 2024-09-01)"); plt.xlabel("Дата"); plt.ylabel("Кумулятивное")
    plt.legend(); plt.tight_layout(); plt.savefig(out_dir/"cumulative.png"); plt.close()

def plot_sentiment_trends(df: pd.DataFrame, out_dir: str):
    out_dir = Path(out_dir)
    df = df.copy(); df['published_at']=pd.to_datetime(df['published_at'])
    df = df[df['published_at']>=START_DATE]
    df['week'] = df['published_at'].dt.to_period('W-MON').apply(lambda r: r.start_time)
    plt.figure(figsize=(10,5))
    for pol in df['politician'].unique():
        pivot = df[df['politician']==pol].groupby(['week','sentiment']).size().unstack(fill_value=0)
        for s in pivot.columns:
            plt.plot(pivot.index, pivot[s], marker='o', label=f"{pol} – {s}")
    plt.title("Тональность по неделям (с 2024-09-01)")
    plt.xlabel("Неделя"); plt.ylabel("Число статей")
    plt.legend(); plt.tight_layout(); plt.savefig(out_dir/"sentiment_trends.png"); plt.close()

def plot_top_sources(df: pd.DataFrame, out_dir: str):
    out_dir = Path(out_dir)
    df = df.copy(); df['published_at']=pd.to_datetime(df['published_at'])
    df = df[df['published_at']>=START_DATE]
    for pol in df['politician'].unique():
        counts = df[df['politician']==pol]['source'].value_counts().head(5)
        plt.figure(figsize=(6,4)); counts.plot(kind='bar')
        plt.title(f"Топ-5 источников: {pol}")
        plt.xlabel("Источник"); plt.ylabel("Упоминаний")
        plt.xticks(rotation=45, ha='right'); plt.tight_layout()
        plt.savefig(out_dir/f"top_sources_{pol.replace(' ','_')}.png"); plt.close()

def plot_top20_sources_bar(df: pd.DataFrame, out_dir: str):
    out_dir = Path(out_dir)
    df = df.copy(); df['published_at']=pd.to_datetime(df['published_at'])
    df = df[df['published_at']>=START_DATE]
    counts = df['source'].value_counts()
    top20 = counts[counts>100].head(20)
    if top20.empty:
        print("plot_top20_sources_bar: нет источников с >100 упоминаниями.")
        return
    plt.figure(figsize=(12,6)); top20.plot(kind='bar')
    plt.title("ТОП-20 источников (>100 упоминаний)")
    plt.xlabel("Источник"); plt.ylabel("Число упоминаний")
    plt.xticks(rotation=45, ha='right'); plt.tight_layout()
    plt.savefig(out_dir/"top20_sources.png"); plt.close()

def plot_top5_sources_timeseries(df: pd.DataFrame, out_dir: str):
    out_dir = Path(out_dir)
    df = df.copy(); df['published_at']=pd.to_datetime(df['published_at'])
    df = df[df['published_at']>=START_DATE]
    top5 = df['source'].value_counts().head(5).index
    ts = df.groupby(['source','published_at']).size().unstack(fill_value=0).loc[top5].T
    plt.figure(figsize=(10,5))
    for src in ts.columns:
        plt.plot(ts.index, ts[src], label=src)
    plt.title("Топ-5 источников: временные ряды")
    plt.xlabel("Дата"); plt.ylabel("Упоминаний")
    plt.legend(); plt.tight_layout()
    plt.savefig(out_dir/"top5_sources_timeseries.png"); plt.close()
