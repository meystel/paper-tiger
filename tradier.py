import requests
from datetime import datetime,timezone
class Tradier:
 def __init__(self,token,base_url):
  self.base=base_url.rstrip("/"); self.s=requests.Session(); self.s.headers.update({"Authorization":"Bearer "+token,"Accept":"application/json"})
 def _get(self,path,params):
  r=self.s.get(self.base+path,params=params,timeout=15); r.raise_for_status(); return r.json()
 def quote(self,symbol):
  q=self._get("/markets/quotes",{"symbols":symbol,"greeks":"true"}).get("quotes",{}).get("quote")
  if not q: raise RuntimeError("No Tradier quote for "+symbol)
  return q[0] if isinstance(q,list) else q
 def quotes(self,symbols):
  if not symbols:return []
  q=self._get("/markets/quotes",{"symbols":",".join(symbols),"greeks":"true"}).get("quotes",{}).get("quote") or []
  return q if isinstance(q,list) else [q]
 def expirations(self,underlying):
  d=self._get("/markets/options/expirations",{"symbol":underlying,"includeAllRoots":"true","strikes":"false"}).get("expirations",{}).get("date") or []
  return d if isinstance(d,list) else [d]
 def chain(self,underlying,expiration):
  o=self._get("/markets/options/chains",{"symbol":underlying,"expiration":expiration,"greeks":"true"}).get("options",{}).get("option") or []
  return o if isinstance(o,list) else [o]
 @staticmethod
 def observed_quote(q):
  keys=("symbol","description","underlying","root_symbol","type","bid","ask","last","bidsize","asksize",
        "bid_date","ask_date","trade_date","strike","expiration_date","option_type","open_interest","volume","greeks")
  out={k:q.get(k) for k in keys}
  out["captured_utc"]=datetime.now(timezone.utc).isoformat()
  out["source"]="Tradier"
  return out
