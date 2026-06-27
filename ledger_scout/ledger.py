"""Research ledger — shared structured state for the coordinated research org.

Budget is in EUR. Free/open datasets cost 0; premium datasets are paid for with
real Stripe charges. Each need records its rationale (the agentic breakdown), the
chosen dataset, what was actually paid, and the Stripe payment id (when live).
"""
from dataclasses import dataclass, field


@dataclass
class DataNeed:
    name: str                 # marketplace family key (e.g. "lca_impact")
    rationale: str            # WHY we need it — the agentic breakdown
    tags: list = field(default_factory=list)
    allocation: float = 0.0   # EUR slice assigned by Procurement (premium needs only)
    chosen: dict | None = None
    paid_eur: float = 0.0
    payment_id: str | None = None
    quality_score: float | None = None
    status: str = "open"      # open|proposed|acquired|escalated|downgraded

    @property
    def is_premium(self):
        return bool(self.chosen and self.chosen.get("price_eur", 0) > 0)


@dataclass
class ResearchLedger:
    brief: str
    total_budget: float
    market: str = "Benelux"
    needs: list = field(default_factory=list)
    catalog_assets: list = field(default_factory=list)
    metrics: list = field(default_factory=list)
    budget_raised: float = 0.0

    def spent(self):
        return round(sum(n.paid_eur for n in self.needs if n.status == "acquired"), 2)

    def remaining(self):
        return round(self.total_budget - self.spent(), 2)

    def premium_needs(self):
        return [n for n in self.needs if n.chosen and n.chosen.get("price_eur", 0) > 0]

    def by_name(self, name):
        return next((n for n in self.needs if n.name == name), None)

    def coverage(self):
        return {n.name: n.status for n in self.needs}
