from datetime import date,datetime,timezone,timedelta
from validator import validate_candidate,validate_quote

def good():
 return {"symbol":"XYZ","catalyst":"product launch","catalyst_date":"2026-10-10","catalyst_source":"source",
 "recent_news":["news"],"movement_today":"up 1%","movement_explanation":"buyers responding to catalyst",
 "relative_strength":"outperforming SPY","expiration":"2026-10-16","expiration_fit":"captures catalyst",
 "liquidity":"tight spread","max_loss":35,"payoff_thesis":"convex upside","invalidation":"breaks support",
 "correlated_exposure":"none","alternatives_considered":["ABC"],"why_beats_cash":"positive expected payoff","confidence":0.7}

def test_missing_rejected():
 c=good(); c["catalyst_source"]=""
 assert any("REJECTED_INCOMPLETE_ANALYSIS" in x for x in validate_candidate(c,100,set(),date(2026,10,6)))

def test_catalyst_after_expiry_rejected():
 c=good(); c["catalyst_date"]="2026-10-29"
 assert "CATALYST_AFTER_EXPIRATION" in validate_candidate(c,100,set(),date(2026,10,6))

def test_duplicate_rejected():
 c=good(); assert "DUPLICATE_EXPOSURE" in validate_candidate(c,100,{"XYZ"},date(2026,10,6))

def test_timing_hedge_can_be_explicit():
 c=good(); c["correlated_exposure"]="timing hedge; directional exposure increases"
 assert "DUPLICATE_EXPOSURE" not in validate_candidate(c,100,{"XYZ"},date(2026,10,6))

def test_stale_quote_rejected():
 old=int((datetime.now(timezone.utc)-timedelta(hours=1)).timestamp()*1000)
 q={"bid":1.0,"ask":1.1,"bid_date":old,"ask_date":old}
 assert "STALE_QUOTE" in validate_quote(q)
