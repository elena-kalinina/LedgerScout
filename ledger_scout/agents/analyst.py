"""Analyst — turns one fashion question into a structured research plan.

This is the "agentic breakdown" showcase: *to answer this, we need A, B, C, D — and
here is why each matters and where we'll source it.* The plan is emitted as a single
rich `plan` event the canvas renders as a decomposition panel. Rule-based by default;
USE_REAL_GEMINI=1 swaps in a Gemini-authored decomposition (with safe fallback).
"""
from .base import Agent
from ..ledger import DataNeed
from ..sources import marketplace
from .. import config

# Per-scenario decomposition: (need family, rationale, tags).
PLANS = {
    "knitwear": [
        ("resale_demand", "Is there real second-hand demand for knitwear, or just runway hype? Resale pull is the honest demand signal.",
         ["knitwear", "wool", "secondhand"]),
        ("search_interest", "Is consumer search interest in recycled-cotton knitwear actually rising in the Benelux?",
         ["recycled", "cotton", "knitwear", "benelux"]),
        ("material_composition", "What recycled-cotton content do comparable garments really carry? Grounds the claim in product reality.",
         ["recycled", "cotton", "composition"]),
        ("lca_impact", "Can we defend the 'recycled cotton' environmental claim with peer-reviewed LCA factors? (EU Green Claims risk)",
         ["lca", "recycled", "cotton", "claim"]),
        ("market_benchmark", "What price band and willingness-to-pay supports an AW26 recycled-knitwear buy?",
         ["market", "price", "sustainable"]),
    ],
    "sustainable_denim": [
        ("lca_impact", "Sustainable denim lives or dies on a defensible environmental claim — start with the LCA evidence.",
         ["lca", "denim", "sustainable", "claim"]),
        ("market_benchmark", "Does a €79–99 sustainable denim price band hold in Germany? Need market size and WTP.",
         ["market", "denim", "germany", "price"]),
        ("resale_demand", "Is there resale/circular demand for sustainable denim, validating real pull?",
         ["denim", "sustainable", "secondhand"]),
        ("search_interest", "Is search interest for sustainable denim rising in Germany for SS27?",
         ["denim", "sustainable", "germany"]),
    ],
    "recycled_activewear": [
        ("lca_impact", "A 'recycled polyester' activewear claim must be defensible — get peer-reviewed LCA evidence first.",
         ["lca", "polyester", "recycled", "claim"]),
        ("search_interest", "Is search interest in recycled activewear rising in France?",
         ["activewear", "recycled", "france"]),
        ("resale_demand", "Is there resale/circular demand for activewear (real pull, not hype)?",
         ["activewear", "secondhand"]),
        ("market_benchmark", "What price band supports recycled activewear in France?",
         ["market", "activewear", "france", "price"]),
    ],
}


class Analyst(Agent):
    role = "analyst"

    def propose_plan(self, brief, budget, market="Benelux", scenario="knitwear"):
        spec = None
        if config.USE_REAL_GEMINI:
            try:
                spec = self._gemini_plan(brief, budget, market)
            except Exception as e:
                self.emit("decision", text=f"(Gemini plan failed, using built-in decomposition: {e})")

        rows = spec if spec else PLANS.get(scenario, PLANS["knitwear"])
        needs = [DataNeed(name=n, rationale=r, tags=list(t)) for (n, r, t) in rows]

        breakdown = []
        for need in needs:
            preview = marketplace.search(need.name)
            best = preview[0] if preview else {}
            breakdown.append({
                "need": need.name,
                "rationale": need.rationale,
                "source": best.get("provider", "—"),
                "tier": best.get("tier", "free"),
                "price_eur": best.get("price_eur", 0),
            })

        self.emit(
            "plan",
            text=f"To answer this within €{budget:.0f}, I need {len(needs)} datasets: "
                 + ", ".join(b["need"] for b in breakdown),
            plan=breakdown,
            market=market,
            budget=budget,
        )
        return market, needs

    def amend(self, needs, instruction):
        instr = instruction.lower()
        if "resale" in instr or "demand" in instr:
            for n in needs:
                if n.name == "resale_demand":
                    n.tags.append("priority")
            self.emit("decision", text="Amended: prioritize resale demand over runway signals")
        if "compliance" in instr or "regulatory" in instr or "claim" in instr:
            for n in needs:
                if n.name == "lca_impact":
                    n.tags.append("priority")
            self.emit("decision", text="Amended: elevated LCA / claim-evidence priority")
        return needs

    def _gemini_plan(self, brief, budget, market):
        from .. import llm

        spec = llm.gemini_research_plan(brief, budget, market)
        valid = set(marketplace.CATALOG.keys())
        rows = []
        for n in spec.get("needs", []):
            name = n.get("name") or n.get("source_type")
            if name in valid:
                rows.append((name, n.get("rationale", "(model rationale)"), n.get("tags", [])))
        return rows or None
