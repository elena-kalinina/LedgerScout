"""Eurostat — live (best-effort) enrichment for free trade/price candidates.

Eurostat's dissemination API returns JSON-stat 2.0 with no key. We do a light-touch
fetch (latest observation) when LEDGERSCOUT_EUROSTAT_LIVE=1 and mark the candidate
live; any failure falls back silently to the fixture reference.
"""
import requests

from .. import config

BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"


def _latest_value(jsonstat):
    """Pull the most recent numeric observation from a JSON-stat 2.0 payload."""
    values = jsonstat.get("value") or {}
    if not values:
        return None
    # value is a {index: number} map; take the highest index (latest in flattened order)
    last_key = max(values, key=lambda k: int(k))
    return values[last_key]


def enrich(candidate):
    if not config.USE_REAL_EUROSTAT:
        return candidate
    dataset = candidate.get("eurostat_dataset")
    if not dataset:
        return candidate
    # IMPORTANT: always filter by dimensions + latest period, or Eurostat returns the
    # ENTIRE dataset (100+ MB). Candidates carry `eurostat_params` to pin one cell.
    params = {"format": "JSON", "lang": "EN", "lastTimePeriod": "1"}
    params.update(candidate.get("eurostat_params", {}))
    resp = requests.get(f"{BASE}/{dataset}", params=params, timeout=15)
    resp.raise_for_status()
    payload = resp.json()
    value = _latest_value(payload)
    period = (((payload.get("dimension") or {}).get("time") or {})
              .get("category", {}).get("label", {}))
    candidate.setdefault("stats", {})
    if value is not None:
        candidate["stats"]["eurostat_latest_observation"] = value
    if period:
        candidate["stats"]["eurostat_period"] = list(period.values())[-1]
    candidate["live"] = True
    return candidate
