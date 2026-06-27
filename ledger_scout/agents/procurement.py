"""Procurement — allocates the EUR budget across premium needs and arbitrates overspend.

Free/open datasets cost nothing, so the budget is spread only across the premium
(paid) needs. When a chosen dataset exceeds its slice, Procurement first tries to
reallocate slack from other premium needs (agent-to-agent, no human); only a true
total-budget overflow escalates to the human.
"""
from .base import Agent

# Relative importance of premium needs when splitting the budget.
WEIGHTS = {
    "lca_impact": 0.55,        # claim-defending evidence is worth the most
    "market_benchmark": 0.45,
}


def _expected_spend(need):
    if need.status == "acquired":
        return need.paid_eur
    if need.chosen:
        return need.chosen.get("price_eur", 0)
    return 0


class Procurement(Agent):
    role = "procurement"

    def allocate(self, ledger):
        premium = ledger.premium_needs()
        if not premium:
            self.emit("budget", text="No premium datasets needed — budget held in reserve")
            return
        names = [n.name for n in premium]
        total_weight = sum(WEIGHTS.get(name, 1.0) for name in names)
        for need in premium:
            w = WEIGHTS.get(need.name, 1.0)
            need.allocation = round(ledger.total_budget * w / total_weight, 2)
        self.emit(
            "budget",
            text="Budget split across premium datasets: "
                 + ", ".join(f"{n.name} €{n.allocation:.0f}" for n in premium)
                 + f" (free datasets €0)",
        )

    def slack(self, ledger, exclude):
        """Unused EUR across other premium needs' slices."""
        total = 0.0
        for n in ledger.premium_needs():
            if n.name == exclude:
                continue
            total += max(0, n.allocation - _expected_spend(n))
        return round(total, 2)

    def reallocate(self, ledger, need, needed):
        """Trim slack from other premium needs into `need`. Returns EUR freed."""
        freed = 0.0
        for n in ledger.premium_needs():
            if n.name == need.name or freed >= needed:
                continue
            avail = max(0, n.allocation - _expected_spend(n))
            take = min(avail, needed - freed)
            if take > 0:
                n.allocation = round(n.allocation - take, 2)
                freed = round(freed + take, 2)
        need.allocation = round(need.allocation + freed, 2)
        if freed > 0:
            self.emit("budget", text=f"Reallocated €{freed:.0f} of slack → {need.name}")
        return freed
