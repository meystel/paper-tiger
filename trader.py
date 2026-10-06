import json
from openai import OpenAI
SYSTEM="""You are Paper Tiger, an aggressive but auditable PAPER trader. Objective: maximize return through 2026-11-05. Starting capital is $100. Allowed: U.S.-listed stocks, ETFs, long calls/puts, and defined-risk option spreads. Forbidden: borrowing, naked/uncovered obligations, or maximum loss exceeding paper capital. Prefer asymmetric individual-company opportunities over index/ETF trades. Never invent a price. Prices in MARKET_DATA are observations supplied by the execution engine. HOLD is valid. Return only schema-valid JSON."""
SCHEMA={"type":"object","additionalProperties":False,"properties":{"candidates":{"type":"array","items":{"type":"object","additionalProperties":False,"properties":{"symbol":{"type":"string"},"setup":{"type":"string"},"status":{"type":"string","enum":["CONSIDERED","REJECTED","SELECTED"]},"thesis":{"type":"string"},"reason":{"type":"string"}},"required":["symbol","setup","status","thesis","reason"]}},"action":{"type":"object","additionalProperties":False,"properties":{"type":{"type":"string","enum":["BUY","SELL","HOLD"]},"symbol":{"type":"string"},"qty":{"type":"number"},"rationale":{"type":"string"}},"required":["type","symbol","qty","rationale"]}},"required":["candidates","action"]}
class Brain:
 def __init__(self,api_key,model): self.client=OpenAI(api_key=api_key); self.model=model
 def decide(self,state,market_data,context):
  r=self.client.responses.create(model=self.model,input=[{"role":"system","content":SYSTEM},{"role":"user","content":json.dumps({"portfolio":state,"market_data":market_data,"context":context})}],text={"format":{"type":"json_schema","name":"paper_tiger_decision","strict":True,"schema":SCHEMA}})
  return json.loads(r.output_text)
