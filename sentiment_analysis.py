import subprocess, importlib.util
# удаляем torchvision, чтобы не конфликтовала с torch 2.2
subprocess.run(["pip","uninstall","-y","torchvision"],stdout=subprocess.DEVNULL)

from transformers import pipeline
import sqlite3, tqdm, pathlib
from database import DB_PATH

pipe = pipeline("sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device_map="auto")

def fetch():
    with sqlite3.connect(DB_PATH) as c:
        return c.execute("SELECT id,title,content FROM news WHERE sentiment IS NULL").fetchall()

def save(upd):
    with sqlite3.connect(DB_PATH) as c:
        c.executemany("UPDATE news SET sentiment=? WHERE id=?", upd); c.commit()

def main():
    rows=fetch()
    if not rows: print("✓ sentiment OK"); return
    upd=[]
    for i in tqdm.tqdm(range(0,len(rows),8)):
        batch=rows[i:i+8]
        txt=[(t or "")+" "+(c or "") for _,t,c in batch]
        for (nid,_,_),pred in zip(batch,pipe(txt,truncation=True)):
            lab=pred["label"].lower()
            upd.append(("positive" if "pos" in lab else "negative" if "neg" in lab else "neutral",nid))
    save(upd); print("✓ sentiment updated",len(upd))

if __name__=="__main__": main()
