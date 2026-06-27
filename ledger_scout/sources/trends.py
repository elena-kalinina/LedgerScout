"""Google Trends — live (best-effort) search-interest enrichment via pytrends.

Enriches a free trends candidate in place with a real interest index and YoY delta
when LEDGERSCOUT_TRENDS_LIVE=1 and pytrends is installed; falls back to the fixture.
"""
from .. import config


def enrich(candidate):
    if not config.USE_REAL_TRENDS:
        return candidate
    query = candidate.get("trends_query")
    geo = candidate.get("trends_geo", "")
    if not query:
        return candidate

    from pytrends.request import TrendReq

    pytrends = TrendReq(hl="en-US", tz=0)
    pytrends.build_payload([query], geo=geo, timeframe="today 12-m")
    frame = pytrends.interest_over_time()
    if frame is None or frame.empty:
        return candidate
    series = frame[query]
    latest = int(series.iloc[-1])
    first = int(series.iloc[0]) or 1
    candidate.setdefault("stats", {})
    candidate["stats"]["interest_index"] = latest
    candidate["stats"]["yoy_delta_pct"] = round((latest - first) / first * 100)
    candidate["freshness_days"] = 1
    candidate["live"] = True
    return candidate
