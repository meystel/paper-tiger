import argparse,json
from datetime import date
from config import Settings
from database import Ledger
from tradier import Tradier
from trader import Brain
from validator import validate_candidate,validate_quote

WATCH=["SPY","QQQ","TQQQ","AMD","NVDA","AVGO","MSFT","META","GOOGL","AMZN","TSLA","RIVN","SOFI"]

def underlying(symbol,q):
 return q.get("underlying") or q.get("root_symbol") or symbol

def fill(side,q):
 errors=validate_quote(q)
 if errors: raise RuntimeError("Quote rejected: "+",".join(errors))
 p=q.get("ask") if side=="BUY" else q.get("bid")
 if p is None or float(p)<=0: raise RuntimeError("No defensible quote")
 return float(p)

def validate_actions(ledger,decision,qm):
 cash=float(ledger.get("cash")); positions=ledger.get("positions") or {}
 existing={underlying(sym,qm.get(sym,{})) for sym,qty in positions.items() if float(qty)>0}
 candidates={c["symbol"]:c for c in decision["candidates"]}
 accepted=[]
 for a in decision["actions"]:
  if a["type"]=="HOLD": accepted.append(a); continue
  sym=a["symbol"]
  if sym not in qm:
   ledger.event("VALIDATOR_REJECT",{"action":a,"codes":["UNQUOTED_INSTRUMENT"]}); continue
  if a["type"]=="BUY":
   c=candidates.get(sym)
   if not c:
    ledger.event("VALIDATOR_REJECT",{"action":a,"codes":["NO_PRETRADE_RECORD"]}); continue
   codes=validate_candidate(c,cash,existing,date.today())+validate_quote(qm[sym])
   if codes:
    ledger.event("VALIDATOR_REJECT",{"action":a,"candidate":c,"codes":codes}); continue
  accepted.append(a)
 return accepted

def apply(l,a,qm):
 side=a["type"]
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
 l.set("cash",round(cash,8)); l.set("positions",pos)
 l.trade(sym,side,qty,px,q,a["rationale"]); l.event("ACTION",{**a,"fill":px,"raw_quote":q})

def run(_):
 s=Settings(); s.validate(); l=Ledger(s.db_path); md=Tradier(s.tradier_token,s.tradier_base_url)
 try:
  syms=list(dict.fromkeys(WATCH+list((l.get("positions") or {}).keys())))
  obs=[md.observed_quote(q) for q in md.quotes(syms)]
  qm={q["symbol"]:q for q in obs}; l.event("MARKET_SNAPSHOT",obs)
  context=("Research current catalysts/news with web search before proposing a trade. "
           "Compare relative performance to SPY/QQQ. Every selected instrument must already "
           "exist in MARKET_DATA; otherwise reject it for this run. The validator will reject "
           "incomplete analysis, stale quotes, capital violations, and unjustified duplicate exposure.")
  d=Brain(s.openai_api_key,s.openai_model).decide(l.snapshot(),obs,context)
  l.event("DECISION",d)
  actions=validate_actions(l,d,qm)
  for a in actions: apply(l,a,qm)
  print(json.dumps({"decision":d,"executed_actions":actions,"state":l.snapshot()},indent=2))
 finally:l.close()

def quote(a):
 s=Settings(); s.validate(); md=Tradier(s.tradier_token,s.tradier_base_url)
 print(json.dumps(md.observed_quote(md.quote(a.symbol)),indent=2))

def status(_):
 s=Settings(); l=Ledger(s.db_path)
 try:print(json.dumps(l.snapshot(),indent=2))
 finally:l.close()

if __name__=="__main__":
 p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="cmd",required=True)
 sub.add_parser("run").set_defaults(fn=run)
 q=sub.add_parser("quote"); q.add_argument("symbol"); q.set_defaults(fn=quote)
 sub.add_parser("status").set_defaults(fn=status)
 a=p.parse_args(); a.fn(a)
