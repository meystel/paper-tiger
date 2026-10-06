import json
from openai import OpenAI

SYSTEM="""You are Paper Tiger, an aggressive but auditable PAPER trader. Objective: maximize return through 2026-11-05. Allowed: U.S.-listed stocks, ETFs, long calls/puts, defined-risk spreads. Forbidden: borrowing, naked/uncovered obligations, or max loss above paper capital.

You are an analyst, not the execution authority. Python validates every BUY.

For EVERY candidate, BEFORE selecting it, provide evidence for: catalyst and date; source; recent material news; today's movement; explanation for that movement; relative strength versus SPY/QQQ; expiration versus catalyst timing; liquidity; maximum loss; payoff thesis; invalidation; existing correlated exposure; alternatives considered; and why this beats holding cash. Never infer a missing fact. Unknown facts must be explicitly marked unknown. A candidate with materially missing evidence must be REJECTED, not SELECTED.

Do not treat two expirations on the same underlying as diversification. A later expiration can hedge timing risk but increases directional exposure. Do not buy merely because an option is cheap or liquid. Compare all surviving opportunities simultaneously; number of positions is an output, never a target. Cash must win or lose the comparison on merit. Never invent prices; MARKET_DATA is authoritative."""

CANDIDATE={"type":"object","additionalProperties":False,"properties":{
"symbol":{"type":"string"},"setup":{"type":"string"},"status":{"type":"string","enum":["CONSIDERED","REJECTED","SELECTED"]},
"thesis":{"type":"string"},"reason":{"type":"string"},"catalyst":{"type":"string"},"catalyst_date":{"type":["string","null"]},
"catalyst_source":{"type":"string"},"recent_news":{"type":"array","items":{"type":"string"},"minItems":1},
"movement_today":{"type":"string"},"movement_explanation":{"type":"string"},"relative_strength":{"type":"string"},
"expiration":{"type":["string","null"]},"expiration_fit":{"type":"string"},"liquidity":{"type":"string"},
"max_loss":{"type":"number"},"payoff_thesis":{"type":"string"},"invalidation":{"type":"string"},
"correlated_exposure":{"type":"string"},"alternatives_considered":{"type":"array","items":{"type":"string"},"minItems":1},
"why_beats_cash":{"type":"string"},"confidence":{"type":"number","minimum":0,"maximum":1}},
"required":["symbol","setup","status","thesis","reason","catalyst","catalyst_date","catalyst_source","recent_news","movement_today","movement_explanation","relative_strength","expiration","expiration_fit","liquidity","max_loss","payoff_thesis","invalidation","correlated_exposure","alternatives_considered","why_beats_cash","confidence"]}

SCHEMA={"type":"object","additionalProperties":False,"properties":{
"candidates":{"type":"array","items":CANDIDATE,"minItems":3},
"actions":{"type":"array","items":{"type":"object","additionalProperties":False,"properties":{
"type":{"type":"string","enum":["BUY","SELL","HOLD"]},"symbol":{"type":"string"},"qty":{"type":"number"},"rationale":{"type":"string"}},
"required":["type","symbol","qty","rationale"]}}},
"required":["candidates","actions"]}

class Brain:
 def __init__(self,api_key,model): self.client=OpenAI(api_key=api_key); self.model=model
 def decide(self,state,market_data,context):
  r=self.client.responses.create(
   model=self.model,
   tools=[{"type":"web_search"}],
   input=[{"role":"system","content":SYSTEM},{"role":"user","content":json.dumps({"portfolio":state,"market_data":market_data,"context":context})}],
   text={"format":{"type":"json_schema","name":"paper_tiger_decision","strict":True,"schema":SCHEMA}})
  return json.loads(r.output_text)
