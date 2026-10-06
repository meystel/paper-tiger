import argparse,json
from config import Settings
from database import Ledger
from tradier import Tradier
from trader import Brain
WATCH=["SPY","QQQ","TQQQ","AMD","NVDA","AVGO","MSFT","META","GOOGL","AMZN","TSLA"]
def fill(side,q):
 p=q.get("ask") if side=="BUY" else q.get("bid")
 if p is None or float(p)<=0: raise RuntimeError("No executable quote")
 return float(p)
def apply(l,d,qm):
 a=d["action"]; side=a["type"]
 if side=="HOLD": l.event("ACTION",a); return
 sym=a["symbol"]; qty=float(a["qty"])
 if qty<=0 or sym not in qm: raise RuntimeError("Invalid/unquoted order")
 q=qm[sym]; px=fill(side,q); mult=100 if q.get("type")=="option" else 1
 cash=float(l.get("cash")); pos=l.get("positions") or {}; cur=float(pos.get(sym,0))
 if side=="BUY":
  cost=px*qty*mult
  if cost>cash+1e-9: raise RuntimeError("Order exceeds paper cash")
  cash-=cost; pos[sym]=cur+qty
 else:
  if qty>cur+1e-9: raise RuntimeError("Cannot sell more than paper position")
  cash+=px*qty*mult; pos[sym]=cur-qty
  if abs(pos[sym])<1e-9: pos.pop(sym,None)
 l.set("cash",round(cash,8)); l.set("positions",pos); l.trade(sym,side,qty,px,q,a["rationale"]); l.event("ACTION",{**a,"fill":px,"raw_quote":q})
def run(_):
 s=Settings(); s.validate(); l=Ledger(s.db_path); md=Tradier(s.tradier_token,s.tradier_base_url)
 try:
  syms=list(dict.fromkeys(WATCH+list((l.get("positions") or {}).keys())))
  obs=[md.observed_quote(q) for q in md.quotes(syms)]; qm={q["symbol"]:q for q in obs}; l.event("MARKET_SNAPSHOT",obs)
  d=Brain(s.openai_api_key,s.openai_model).decide(l.snapshot(),obs,"Use only supplied quote observations. Reject weak or chased setups explicitly.")
  l.event("DECISION",d); apply(l,d,qm); print(json.dumps({"decision":d,"state":l.snapshot()},indent=2))
 finally:l.close()
def quote(a):
 s=Settings(); s.validate(); md=Tradier(s.tradier_token,s.tradier_base_url); print(json.dumps(md.observed_quote(md.quote(a.symbol)),indent=2))
def status(_):
 s=Settings(); l=Ledger(s.db_path)
 try:print(json.dumps(l.snapshot(),indent=2))
 finally:l.close()
if __name__=="__main__":
 p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="cmd",required=True); sub.add_parser("run").set_defaults(fn=run); q=sub.add_parser("quote"); q.add_argument("symbol"); q.set_defaults(fn=quote); sub.add_parser("status").set_defaults(fn=status); a=p.parse_args(); a.fn(a)
