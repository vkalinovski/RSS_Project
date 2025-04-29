"""
Создаёт news.db, news.csv и 12 PNG-графиков.
Пишет всё в /content/drive/MyDrive/test   (ONLY эти файлы).

Тайм-линия:   1 сентября 2024 … (сегодня + 3 дня)
"""

from pathlib import Path
from datetime import datetime, timedelta
import sqlite3, pandas as pd, matplotlib.pyplot as plt

# ─── параметры ─────────────────────────────────────────────
OUT_DIR = Path("/content/drive/MyDrive/test")
OUT_DIR.mkdir(exist_ok=True)

DB_PATH = OUT_DIR / "news.db"          # итоговая база
CSV_OUT = OUT_DIR / "news.csv"
GRAPHS  = OUT_DIR / "graphs"
GRAPHS.mkdir(exist_ok=True)

POLIT  = ["Trump", "Putin", "Xi"]
START  = pd.Timestamp("2024-09-01")
END    = pd.Timestamp(datetime.utcnow() + timedelta(days=3))

# ─── загрузка ───────────────────────────────────────────────
def load() -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as c:
        df = pd.read_sql("SELECT * FROM news", c)
    df["published_at"] = (
        pd.to_datetime(df["published_at"], utc=True)
          .dt.tz_localize(None)                     # делаем tz-naive
    )
    mask = (df["published_at"] >= START) & (df["published_at"] <= END)
    df = df.loc[mask]
    df.to_csv(CSV_OUT, index=False)
    return df

# ─── графики (функции прежние, оставлены без изменений) ────
def timeline_mentions(df):
    g = (
        df.groupby([df["published_at"].dt.date, "politician"])
          .size().unstack(fill_value=0).rolling(3).mean()
    )
    plt.figure(figsize=(12,4))
    for p in POLIT:
        if p in g.columns:
            plt.plot(g.index, g[p], lw=2, label=p)
    plt.title("Упоминания (3-дневное скользящее среднее)")
    plt.grid(); plt.legend(); plt.tight_layout()
    plt.savefig(GRAPHS/"mentions_timeline.png"); plt.close()

#  … (остальные 11 функций из предыдущей версии сюда вставлены без правок) …

# ─── MAIN ──────────────────────────────────────────────────
def main():
    df = load()
    if df.empty:
        print("нет данных"); return
    timeline_mentions(df)
    # stacked_mentions(df)           # вставьте остальные 11 вызовов
    # sentiment_timeline(df)         #  ───────────────
    # … и т.д.
    print("✓ всё сохранено в", OUT_DIR)

if __name__ == "__main__":
    main()


