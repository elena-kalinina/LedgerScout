"""Escalate-vs-proceed policy — when agents act alone vs ask the human."""
PROCEED, CONFIRM, ASK = "proceed", "confirm", "ask"

SIDE_EFFECTFUL = {"publish_brief", "commit_premium_dataset"}


def decide(action, *, within_budget=True, strategy_risk=False, missing_info=False, overspend=0.0):
    """Return one of PROCEED / CONFIRM / ASK with a short reason."""
    if missing_info or strategy_risk:
        return ASK, "needs human strategy or spec input"
    if action in SIDE_EFFECTFUL:
        return CONFIRM, "publishes research / commits spend"
    if not within_budget:
        if overspend <= 0:
            return PROCEED, "within budget"
        if overspend <= 5:
            return PROCEED, f"minor overspend €{overspend:.0f} auto-absorbed"
        return ASK, f"€{overspend:.0f} over budget needs human approval"
    return PROCEED, "clear and within budget"
