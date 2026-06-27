"""Smoke tests — research coordination arc must hold end-to-end (offline simulator)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ledger_scout.missions import research


def test_knitwear_completes_within_budget():
    ledger, _ = research.run(scenario="knitwear")
    assert ledger.spent() <= ledger.total_budget + 1e-6, "must not overspend the (possibly raised) budget"
    acquired = [n for n in ledger.needs if n.status in ("acquired", "downgraded")]
    assert len(acquired) >= 4, "most data needs should be acquired"


def test_knitwear_pays_for_premium_datasets():
    ledger, _ = research.run(scenario="knitwear")
    paid = [n for n in ledger.needs if n.paid_eur > 0]
    assert len(paid) >= 2, "premium datasets should be paid for"
    assert all(n.payment_id for n in paid), "each paid dataset gets a payment id"


def test_knitwear_human_approves_budget_increase():
    ledger, _ = research.run(scenario="knitwear")
    assert ledger.budget_raised > 0, "knitwear should require a human-approved budget increase"


def test_denim_reallocates_without_human():
    ledger, events = research.run(scenario="sustainable_denim")
    assert ledger.budget_raised == 0, "denim should resolve within budget (no increase)"
    reallocated = any(e.get("kind") == "budget" and "Reallocated" in e.get("text", "")
                      for e in _events(events))
    assert reallocated, "denim should show autonomous slack reallocation"


def test_agentic_breakdown_emitted():
    _, events = research.run(scenario="knitwear")
    plans = [e for e in _events(events) if e.get("kind") == "plan"]
    assert plans and plans[0].get("plan"), "analyst must emit a structured decomposition"


def test_catalog_and_metrics():
    ledger, _ = research.run(scenario="knitwear")
    assert len(ledger.catalog_assets) >= 4, "catalog should register acquired datasets"
    assert any(m["name"] == "trend_score" for m in ledger.metrics)
    assert any(m["name"] == "claim_verifiability" for m in ledger.metrics)


def test_utilization_trace_per_dataset():
    _, events = research.run(scenario="knitwear")
    util = [e for e in _events(events) if e.get("kind") == "utilization"]
    assert len(util) >= 4, "each acquired dataset should explain how it's used"
    paid = [u for u in util if u["utilization"]["paid_eur"] > 0]
    assert paid and all(u["utilization"]["answers"] for u in paid), "paid data must state what it answers"


def test_answer_with_free_only_approximation():
    _, events = research.run(scenario="knitwear")
    ans = next(e for e in _events(events) if e.get("kind") == "answer")["answer"]
    assert ans["full"]["verdict"] and ans["free_only"]["verdict"], "both answers computed"
    # Paid LCA must make the claim defensible where free-only data cannot.
    assert ans["full"]["claim_defensible"] is True
    assert ans["free_only"]["claim_defensible"] is False
    assert ans["value_of_paid"]["confidence_delta"] > 0, "paid data should raise confidence"
    assert ans["value_of_paid"]["unlocks"], "value of paid should be itemized"


def _events(stream):
    import json
    return [json.loads(line) for line in stream.path.read_text().splitlines() if line.strip()]


if __name__ == "__main__":
    test_knitwear_completes_within_budget()
    test_knitwear_pays_for_premium_datasets()
    test_knitwear_human_approves_budget_increase()
    test_denim_reallocates_without_human()
    test_agentic_breakdown_emitted()
    test_catalog_and_metrics()
    test_utilization_trace_per_dataset()
    test_answer_with_free_only_approximation()
    print("All research smoke tests passed.")
