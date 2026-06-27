"""Research mission — assembles the org and runs a data-shopping mission."""
from ..events import EventStream
from ..human.channel import get_channel
from ..coordinator import Coordinator
from ..agents.analyst import Analyst
from ..agents.scout import Scout
from ..agents.procurement import Procurement
from ..agents.synthesizer import Synthesizer


SCENARIOS = {
    "knitwear": {
        "brief": "Should we increase recycled-cotton knitwear for AW26 in the Benelux, "
                 "and can we defend the 'recycled cotton' claim?",
        "budget": 55.0,
        "market": "Benelux",
        # Budget is tight: the agent pays for the LCA evidence autonomously, then must
        # ASK the human to approve a budget increase for the market benchmark.
        "script": [
            ("research plan", "amend: prioritize resale demand and claim evidence"),
            ("budget split", "approve"),
            ("over budget", "stretch"),
            ("Publish research brief", "confirm"),
        ],
    },
    "sustainable_denim": {
        "brief": "Can we launch €79–99 sustainable denim in Germany for SS27?",
        "budget": 70.0,
        "market": "Germany",
        # Budget covers both premium datasets, but the LCA over-runs its slice — the
        # agents REALLOCATE slack autonomously (no human) and pay within budget.
        "script": [
            ("research plan", "amend: prioritize claim evidence"),
            ("budget split", "approve"),
            ("over budget", "cheaper"),
            ("Publish research brief", "confirm"),
        ],
    },
    "recycled_activewear": {
        "brief": "Can we claim 'recycled polyester' for SS27 activewear in France on a tight budget?",
        "budget": 35.0,
        "market": "France",
        # Tight budget: the agent asks to buy €40 LCA evidence, the human DECLINES and
        # tells it to drop to the free tier. The brief then honestly downgrades the
        # claim to "at risk" — but the €30 market benchmark is still bought.
        "script": [
            ("research plan", "amend: prioritize claim evidence"),
            ("budget split", "approve"),
            ("over budget", "cheaper"),
            ("Publish research brief", "confirm"),
        ],
    },
}


def run(scenario="knitwear", human=None):
    cfg = SCENARIOS[scenario]
    events = EventStream()
    human = human or get_channel(cfg["script"])

    analyst = Analyst("analyst", events)
    scout = Scout("scout", events)
    procurement = Procurement("procurement", events)
    synthesizer = Synthesizer("synthesizer", events)

    coord = Coordinator(events, human, analyst, scout, procurement, synthesizer)
    ledger = coord.run(cfg["brief"], cfg["budget"], cfg["market"], scenario)
    return ledger, events


def traceability(ledger):
    lines = [
        "# Research Traceability",
        f"Brief: {ledger.brief}",
        f"Market: {ledger.market}",
        f"Budget: €{ledger.total_budget:.0f} (raised €{ledger.budget_raised:.0f}) | "
        f"Spent: €{ledger.spent():.0f} | Remaining: €{ledger.remaining():.0f}",
        "",
        "| Need | Status | Dataset | Tier | Paid | Quality | Payment |",
        "|------|--------|---------|------|------|---------|---------|",
    ]
    for n in ledger.needs:
        title = n.chosen["title"] if n.chosen else "—"
        tier = n.chosen.get("tier", "—") if n.chosen else "—"
        paid = f"€{n.paid_eur:.0f}" if n.paid_eur else "free"
        quality = f"{n.quality_score:.0%}" if n.quality_score else "—"
        pay = n.payment_id or "—"
        lines.append(f"| {n.name} | {n.status} | {title} | {tier} | {paid} | {quality} | {pay} |")

    if ledger.metrics:
        lines += ["", "## Metrics (with lineage)", ""]
        for m in ledger.metrics:
            lines.append(f"- **{m['name']}** = {m['value']} ({m['unit']}) ← {m['sources']}")

    if ledger.catalog_assets:
        lines += ["", "## Catalog assets", ""]
        for a in ledger.catalog_assets:
            lines.append(
                f"- {a.name} | {a.provider} | Q={a.quality_score:.0%} | {a.freshness_days}d | "
                f"{a.tier} | {a.license}"
            )
    return "\n".join(lines)
