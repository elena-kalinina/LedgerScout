"""HuggingFace Hub — live dataset metadata for free candidates.

Uses the public Hub API (no key). Enriches a marketplace candidate in place with
real download counts and last-modified freshness when LEDGERSCOUT_HF_LIVE=1.
"""
from datetime import datetime, timezone

import requests

from .. import config

API = "https://huggingface.co/api/datasets"


def enrich(candidate):
    if not config.USE_REAL_HF:
        return candidate
    repo = candidate.get("hf_repo")
    if not repo:
        return candidate
    resp = requests.get(f"{API}/{repo}", timeout=15)
    resp.raise_for_status()
    info = resp.json()
    candidate.setdefault("stats", {})
    candidate["stats"]["hf_downloads"] = info.get("downloads")
    candidate["stats"]["hf_likes"] = info.get("likes")
    last_modified = info.get("lastModified")
    if last_modified:
        try:
            dt = datetime.fromisoformat(last_modified.replace("Z", "+00:00"))
            candidate["freshness_days"] = max(0, (datetime.now(timezone.utc) - dt).days)
        except ValueError:
            pass
    candidate["live"] = True
    return candidate
