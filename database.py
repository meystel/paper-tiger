import json,sqlite3
from datetime import datetime,timezone
SCHEMA="""CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT,ts_utc TEXT NOT NULL,kind TEXT NOT NULL,payload TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS trades(id INTEGER PRIMARY KEY AUTOINCREMENT,ts_utc TEXT NOT NULL,symbol TEXT NOT NULL,side TEXT NOT NULL,qty REAL NOT NULL,fill REAL NOT NULL,quote_bid REAL,quote_ask REAL,quote_ts INTEGER,rationale TEXT);
CREATE TABLE IF NOT EXISTS state(key TEXT PRIMARY KEY,value TEXT NOT NULL);"""
class Ledger:
 def __init__(self,path):
  self.db=sqlite3.connect(path); self.db.executescript(SCHEMA); self.db.commit()
  if self.get("cash") is None:
   self.set("cash",100.0); self.set("contributed",100.0); self.set("positions",{})
 def close(self): self.db.close()
 def event(self,kind,payload):
  self.db.execute("INSERT INTO events(ts_utc,kind,payload) VALUES(?,?,?)",(datetime.now(timezone.utc).isoformat(),kind,json.dumps(payload,sort_keys=True))); self.db.commit()
 def trade(self,symbol,side,qty,fill,quote,rationale):
  self.db.execute("INSERT INTO trades(ts_utc,symbol,side,qty,fill,quote_bid,quote_ask,quote_ts,rationale) VALUES(?,?,?,?,?,?,?,?,?)",(datetime.now(timezone.utc).isoformat(),symbol,side,qty,fill,quote.get("bid"),quote.get("ask"),quote.get("bid_date") or quote.get("trade_date"),rationale)); self.db.commit()
 def get(self,key):
  r=self.db.execute("SELECT value FROM state WHERE key=?",(key,)).fetchone(); return json.loads(r[0]) if r else None
 def set(self,key,value):
  self.db.execute("INSERT INTO state(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",(key,json.dumps(value))); self.db.commit()
 def snapshot(self): return {"cash":self.get("cash"),"contributed":self.get("contributed"),"positions":self.get("positions") or {}}
