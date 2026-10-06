from __future__ import annotations
from datetime import date, datetime, timezone

REQUIRED = (
    "catalyst","catalyst_source","recent_news","movement_today",
    "movement_explanation","relative_strength","expiration_fit","liquidity",
    "max_loss","payoff_thesis","invalidation","correlated_exposure",
    "alternatives_considered","why_beats_cash"
)

def validate_candidate(c: dict, cash: float, existing_underlyings: set[str], today: date) -> list[str]:
    errors=[]
    for key in REQUIRED:
        v=c.get(key)
        if v is None or v=="" or v==[]:
            errors.append("REJECTED_INCOMPLETE_ANALYSIS:"+key)

    exp=c.get("expiration")
    catalyst_date=c.get("catalyst_date")
    if exp:
        e=date.fromisoformat(exp)
        if e <= today:
            errors.append("BAD_EXPIRATION")
        if catalyst_date and date.fromisoformat(catalyst_date)>e:
            fit=(c.get("expiration_fit") or "").lower()
            if "pre-catalyst" not in fit and "before catalyst" not in fit:
                errors.append("CATALYST_AFTER_EXPIRATION")

    if float(c.get("max_loss") or 0)>cash:
        errors.append("CAPITAL_LIMIT")

    if c.get("symbol") in existing_underlyings:
        corr=(c.get("correlated_exposure") or "").lower()
        if "hedge" not in corr and "timing" not in corr:
            errors.append("DUPLICATE_EXPOSURE")

    if float(c.get("confidence") or 0)<0.55:
        errors.append("THESIS_WEAK")
    return errors

def quote_age_seconds(q: dict, now: datetime | None=None) -> float | None:
    now=now or datetime.now(timezone.utc)
    stamps=[q.get("ask_date"),q.get("bid_date"),q.get("trade_date")]
    stamps=[x for x in stamps if x]
    if not stamps:return None
    # Tradier quote timestamps are Unix milliseconds.
    ts=max(float(x) for x in stamps)/1000.0
    return max(0.0,now.timestamp()-ts)

def validate_quote(q: dict, max_age_seconds: int=1200) -> list[str]:
    errors=[]
    age=quote_age_seconds(q)
    if age is None: errors.append("QUOTE_TIMESTAMP_MISSING")
    elif age>max_age_seconds: errors.append("STALE_QUOTE")
    bid=q.get("bid"); ask=q.get("ask")
    if not bid or not ask or float(bid)<=0 or float(ask)<=0: errors.append("NO_TWO_SIDED_MARKET")
    elif float(ask)<float(bid): errors.append("CROSSED_MARKET")
    return errors
