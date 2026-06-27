"""The Coordinator — routes agents, holds the ledger, runs escalate-vs-proceed policy.

It does not analyse, shop, or pay. It COORDINATES: sequences the human gates, lets
Procurement arbitrate the budget, and decides — per premium dataset — whether the
org can pay autonomously, self-heal by reallocating slack, or must ask the human to
approve a budget increase. Premium datasets are paid for with real Stripe charges.
"""
from . import policy
from .ledger import ResearchLedger
from .payments import get_wallet, live_enabled
from .sources.marketplace import USE_MAP


class Coordinator:
    def __init__(self, events, human, analyst, scout, procurement, synthesizer):
        self.events = events
        self.human = human
        self.analyst = analyst
        self.scout = scout
        self.procurement = procurement
        self.synthesizer = synthesizer

    def run(self, brief, budget, market="Benelux", scenario="knitwear"):
        ev = self.events
        ev.emit("task", "coordinator", text=f"Mission: '{brief}' — budget €{budget:.0f}")

        # 1) Agentic breakdown of the question + human approval of the plan.
        market, needs = self.analyst.propose_plan(brief, budget, market, scenario)
        ledger = ResearchLedger(brief=brief, total_budget=budget, market=market, needs=needs)

        _, why = policy.decide("approve_plan", strategy_risk=True)
        ev.emit("escalation", "coordinator", text=f"ASK human: approve research plan? ({why})")
        reply = self.human.ask("Approve this research plan? Any amendments?",
                               options=["approve", "amend"])
        ev.emit("human_reply", "human", text=reply)
        if any(k in reply.lower() for k in ["amend", "resale", "compliance", "regulatory", "claim"]):
            self.analyst.amend(needs, reply)

        # 2) Scout shops every need so we know which are premium, then split the budget.
        for need in needs:
            need.chosen = self.scout.shop(need)
            need.status = "proposed" if need.chosen else "escalated"

        self.procurement.allocate(ledger)
        ev.emit("escalation", "coordinator", text="ASK human: approve the budget split?")
        reply = self.human.ask("Approve this budget split?", options=["approve", "adjust"])
        ev.emit("human_reply", "human", text=reply)

        # 3) Open the agent's wallet (real Stripe card or offline simulator).
        self.wallet = get_wallet(budget)
        ev.emit("budget", "coordinator",
                text=f"Wallet ready: €{budget:.0f} limit "
                     f"({'REAL Stripe payments' if live_enabled() else 'offline simulator'})")

        # 4) Acquire each dataset: free instantly, premium via paid arbitration.
        for need in needs:
            if need.chosen:
                self._settle_need(ledger, need)

        # 5) Synthesize the brief + final publish gate.
        report = self.synthesizer.synthesize(ledger, ev)
        self._finalize(ledger, report)
        return ledger

    def _settle_need(self, ledger, need):
        ev = self.events
        best = need.chosen
        price = best.get("price_eur", 0)

        if price <= 0:
            self._acquire(ledger, need, 0.0, None, free=True)
            return

        available = self.wallet.available_eur

        if price <= available + 1e-9:
            # Within total budget. Over its own slice? Self-heal by reallocating slack.
            if price > need.allocation + 1e-9:
                over = round(price - need.allocation, 2)
                slack = self.procurement.slack(ledger, need.name)
                if slack >= over:
                    self.procurement.reallocate(ledger, need, over)
                    ev.emit("decision", "coordinator",
                            text=f"{need.name}: €{over:.0f} over its slice — resolved by "
                                 f"reallocating slack, no human needed")
                else:
                    ev.emit("decision", "coordinator",
                            text=f"{need.name}: €{over:.0f} over its slice but within total "
                                 f"budget — proceeding")
            self._pay(ledger, need, price)
            return

        # Over the TOTAL budget — escalate the arbitration to the human.
        needed = round(price - available, 2)
        _, why = policy.decide("overspend", within_budget=False, overspend=needed)
        ev.emit("escalation", "coordinator",
                text=f"{need.name} '{best['title']}' costs €{price:.0f} — €{needed:.0f} over "
                     f"the remaining €{available:.0f}. Premium evidence or a free fallback? ({why})")
        reply = self.human.ask(
            f"'{best['title']}' is €{price:.0f}, €{needed:.0f} over budget. "
            f"Approve a budget increase, or drop to the free tier?",
            options=["stretch", "cheaper"],
        )
        ev.emit("human_reply", "human", text=reply)

        if "stretch" in reply.lower() or "approve" in reply.lower() or "increase" in reply.lower():
            new_budget = round(ledger.total_budget + needed, 2)
            self.wallet.raise_limit_to(new_budget)
            ledger.total_budget = new_budget
            ledger.budget_raised = round(ledger.budget_raised + needed, 2)
            need.allocation = round(need.allocation + needed, 2)
            ev.emit("budget", "coordinator",
                    text=f"Human approved +€{needed:.0f}; budget now €{new_budget:.0f}")
            self._pay(ledger, need, price)
        elif "cheap" in reply.lower() or "free" in reply.lower() or "drop" in reply.lower():
            self._downgrade(ledger, need)
        else:
            need.status = "escalated"
            ev.emit("escalation", "coordinator", text=f"{need.name}: left unresolved")

    def _pay(self, ledger, need, price):
        ev = self.events
        result = self.wallet.authorize(price, need.chosen["title"])
        if not result.approved:
            need.status = "escalated"
            ev.emit("escalation", "coordinator", text=f"{need.name}: payment declined — {result.reason}")
            return
        self._acquire(ledger, need, result.amount_eur, result.payment_id)
        ev.emit("payment", "procurement",
                text=f"Paid €{result.amount_eur:.0f} for '{need.chosen['title']}' — {result.reason}",
                payment={"need": need.name, "amount_eur": result.amount_eur,
                         "payment_id": result.payment_id, "live": live_enabled()})

    def _downgrade(self, ledger, need):
        alt = need.chosen.get("cheaper_alternative")
        if not alt:
            need.status = "escalated"
            self.events.emit("escalation", "coordinator", text=f"{need.name}: no free fallback")
            return
        need.chosen = alt
        self.events.emit("decision", "coordinator",
                         text=f"Downgraded {need.name} to free tier: '{alt['title']}' "
                              f"(higher regulatory risk, lower verifiability)")
        self._acquire(ledger, need, 0.0, None, status="downgraded")

    def _acquire(self, ledger, need, paid_eur, payment_id, free=False, status="acquired"):
        need.paid_eur = paid_eur
        need.payment_id = payment_id
        need.quality_score = need.chosen.get("quality_score")
        need.status = status
        tag = "free" if (free or paid_eur == 0) else f"€{paid_eur:.0f}"
        self.events.emit("decision", "coordinator",
                         text=f"Acquired {need.name}: '{need.chosen['title']}' ({tag}) "
                              f"| budget left €{ledger.remaining():.0f}")
        self._emit_utilization(need, paid_eur)

    def _emit_utilization(self, need, paid_eur):
        """Show what the dataset delivers and how it answers the question — esp. for paid data."""
        use = USE_MAP.get(need.name, {})
        fields = need.chosen.get("schema_fields", [])[:4]
        stats = need.chosen.get("stats", {})
        key = use.get("key_stat")
        key_val = stats.get(key) if key else None
        verb = f"Paid €{paid_eur:.0f} →" if paid_eur > 0 else "Free →"
        self.events.emit(
            "utilization", "synthesizer",
            text=f"{verb} '{need.chosen['title']}' gives {', '.join(fields) or 'aggregates'} "
                 f"→ feeds {use.get('feeds', 'analysis')} → answers: {use.get('answers', need.rationale)}",
            utilization={
                "need": need.name,
                "dataset": need.chosen["title"],
                "tier": need.chosen.get("tier", "free"),
                "paid_eur": paid_eur,
                "provides": fields,
                "feeds": use.get("feeds", "analysis"),
                "answers": use.get("answers", need.rationale),
                "key_stat": key,
                "key_value": key_val,
            },
        )

    def _finalize(self, ledger, report):
        ev = self.events
        acquired = [n for n in ledger.needs if n.status in ("acquired", "downgraded")]
        paid = [n for n in acquired if n.paid_eur > 0]
        ev.emit("decision", "coordinator",
                text=f"Research pack: {len(acquired)}/{len(ledger.needs)} datasets, "
                     f"{len(paid)} paid, €{ledger.spent():.0f} / €{ledger.total_budget:.0f} spent")

        _, why = policy.decide("publish_brief")
        ev.emit("escalation", "coordinator", text=f"CONFIRM publish brief ({why})")
        reply = self.human.ask(
            f"Publish research brief ({report.get('trend_score', '?')}/100 trend score)?",
            options=["confirm", "cancel"],
        )
        ev.emit("human_reply", "human", text=reply)
        if "confirm" in reply.lower():
            ev.emit("deal", "coordinator", text="Research brief published")
