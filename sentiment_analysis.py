import sqlite3, nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from pathlib import Path
from tqdm import tqdm

DB = Path(__file__).parent / "news.db"
nltk.download("vader_lexicon", quiet=True)
vader = SentimentIntensityAnalyzer()

def main():
    with sqlite3.connect(DB) as c:
        rows = c.execute(
            "SELECT id,title,content FROM news WHERE sentiment IS NULL"
        ).fetchall()
        if not rows:
            print("✓ sentiment: всё готово"); return

        upd=[]
        for _id,title,cont in tqdm(rows, desc="sentiment"):
            txt = (title or "")+" "+(cont or "")
            score = vader.polarity_scores(txt)["compound"]
            sent = "positive" if score>0.2 else "negative" if score<-0.2 else "neutral"
            upd.append((sent,_id))
        c.executemany("UPDATE news SET sentiment=? WHERE id=?", upd)
        c.commit()
    print("✓ sentiment: обновлено", len(upd))

if __name__=="__main__":
    main()
