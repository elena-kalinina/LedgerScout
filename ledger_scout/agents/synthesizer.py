"""Synthesizer — merges acquired datasets into a quantitative brief, then actually
answers the question two ways:

  * full      — using everything we acquired (incl. paid premium datasets)
  * free_only — using only free datasets + the free `cheaper_alternative` proxies

The gap between them is the demonstrated *value of what we paid for* — typically a
legally defensible sustainability claim and a precise price band / willingness-to-pay.
"""
from .base import Agent
from .. import catalog

GLOSSARY = {
    "resale_demand": ["reuse_rate", "resale_demand_index"],
    "search_interest": ["search_interest_index", "yoy_delta"],
    "material_composition": ["recycled_content_share"],
    "lca_impact": ["gwp_reduction_pct", "claim_verifiability", "regulatory_risk"],
    "market_benchmark": ["market_cagr", "wtp_premium"],
}


class Synthesizer(Agent):
    role = "synthesizer"

    def synthesize(self, ledger, events):
        acquired = [n for n in ledger.needs if n.status in ("acquired", "downgraded")]
        if not acquired:
            self.emit("escalation", text="No datasets acquired — cannot synthesize")
            return {}

        for n in acquired:
            asset = catalog.register(
                events,
                need_name=n.name,
                candidate=n.chosen,
                glossary_terms=GLOSSARY.get(n.name, []),
                payment_id=n.payment_id,
            )
            ledger.catalog_assets.append(asset)

        full = self._compute(ledger, free_only=False)
        free = self._compute(ledger, free_only=True)

        for name, value, unit, sources in [
            ("trend_score", full["trend_score"], "0-100", "resale_demand+search_interest"),
            ("confidence", full["confidence"], "0-1", "source_agreement"),
            ("gwp_reduction_pct", full["gwp_reduction_pct"], "%", "lca_impact"),
            ("claim_verifiability", full["verifiability"], "0-1", "lca_impact"),
            ("regulatory_risk", full["risk"], "low|medium|high", "lca_impact"),
            ("market_cagr_pct", full["market_cagr"], "%", "market_benchmark"),
        ]:
            if value is None:
                continue
            record = {"name": name, "value": value, "unit": unit, "sources": sources}
            events.emit("metric", self.name, text=f"{name}={value} ({unit})", metric=record)
            ledger.metrics.append(record)

        value_of_paid = self._value_of_paid(full, free, ledger)
        answer = {
            "brief": ledger.brief,
            "full": full,
            "free_only": free,
            "value_of_paid": value_of_paid,
        }
        events.emit(
            "answer", self.name,
            text=f"ANSWER: {full['verdict']} — {full['headline']} "
                 f"(free-only would say: {free['verdict']})",
            answer=answer,
        )

        report = {
            "trend_score": full["trend_score"],
            "confidence": full["confidence"],
            "verdict": full["verdict"],
            "claim": {"gwp_reduction_pct": full["gwp_reduction_pct"],
                      "verifiability": full["verifiability"], "risk": full["risk"],
                      "gaps": full["gaps"]},
            "market": {"cagr_pct": full["market_cagr"], "wtp_premium_pct": full["wtp"]},
            "answer": answer,
            "datasets_acquired": len(acquired),
            "premium_paid": round(ledger.spent(), 2),
        }
        events.emit(
            "synthesis", self.name,
            text=f"Brief ready: {full['verdict']} | trend {full['trend_score']}/100, "
                 f"claim {full['verifiability']:.0%} verifiable (risk {full['risk']})",
            report=report,
        )
        return report

    # ------------------------------------------------------------------ #
    # Answer the question, optionally restricted to free data.
    # ------------------------------------------------------------------ #
    def _selected(self, need, free_only):
        """The candidate we'd rely on: the acquired one, or its free proxy in free-only mode."""
        if not need.chosen:
            return None
        c = need.chosen
        if free_only and c.get("price_eur", 0) > 0:
            return c.get("cheaper_alternative")  # may be None → that signal is absent for free
        return c

    NEED_NAMES = ["resale_demand", "search_interest", "material_composition",
                  "lca_impact", "market_benchmark"]

    def _compute(self, ledger, free_only):
        def cand(name):
            need = ledger.by_name(name)
            return self._selected(need, free_only) if need else None

        def stats(name):
            c = cand(name)
            return c.get("stats", {}) if c else {}

        live_sources = sorted({c.get("provider") for n in self.NEED_NAMES
                               if (c := cand(n)) and c.get("live")})

        resale, search = stats("resale_demand"), stats("search_interest")
        trend = 50.0
        if resale:
            trend += min(20, resale.get("reuse_share", 0) * 20) + min(10, resale.get("yoy_delta_pct", 0))
        if search:
            trend += min(15, search.get("interest_index", 0) / 5) + min(10, max(0, search.get("yoy_delta_pct", 0)))
        trend = round(min(100, trend))

        lca = stats("lca_impact")
        verifiability = lca.get("verifiability")
        risk = lca.get("regulatory_risk", "unknown" if not lca else "medium")
        gwp = lca.get("gwp_reduction_pct")

        mkt = stats("market_benchmark")
        market_quality = (cand("market_benchmark") or {}).get("quality_score", 0)
        cagr = mkt.get("cagr_pct")
        wtp = mkt.get("wtp_premium_pct")

        claim_defensible = bool(lca) and (verifiability or 0) >= 0.8 and risk == "low"
        demand_ok = trend >= 70
        confidence = round(0.4 * (trend / 100) + 0.35 * (verifiability or 0) + 0.25 * market_quality, 2)

        if demand_ok and claim_defensible:
            verdict = "GO"
            headline = "increase the buy and publish the sustainability claim — it's defensible"
        elif demand_ok and not claim_defensible:
            verdict = "GO, claim at risk"
            headline = ("increase the buy on demand, but do NOT publish the sustainability claim "
                        "without defensible LCA evidence (high regulatory risk)")
        else:
            verdict = "HOLD"
            headline = "demand signal too weak to commit"

        gaps = []
        if not claim_defensible and lca:
            gaps.append("claim evidence not legally defensible (verifiability < 80% or risk not low)")
        if wtp is None:
            gaps.append("no willingness-to-pay / price-band precision")

        return {"trend_score": trend, "confidence": confidence, "gwp_reduction_pct": gwp,
                "verifiability": verifiability if verifiability is not None else (0.0 if free_only else None),
                "risk": risk, "market_cagr": cagr, "wtp": wtp,
                "claim_defensible": claim_defensible, "verdict": verdict, "headline": headline,
                "gaps": gaps, "live_sources": live_sources}

    def _value_of_paid(self, full, free, ledger):
        unlocks = []
        if full["claim_defensible"] and not free["claim_defensible"]:
            fv = (free["verifiability"] or 0)
            unlocks.append(
                f"Defensible sustainability claim: {fv:.0%} (risk {free['risk']}) → "
                f"{full['verifiability']:.0%} verifiable (risk {full['risk']})")
        if full["wtp"] and not free["wtp"]:
            unlocks.append(f"Willingness-to-pay +{full['wtp']}% and a real price band")
        if full["market_cagr"] and free["market_cagr"] and full["market_cagr"] != free["market_cagr"]:
            unlocks.append(f"Market growth {free['market_cagr']}% → {full['market_cagr']}% (segment-level)")
        return {
            "spent_eur": round(ledger.spent(), 2),
            "confidence_delta": round(full["confidence"] - free["confidence"], 2),
            "verdict_changed": full["verdict"] != free["verdict"],
            "unlocks": unlocks,
        }
