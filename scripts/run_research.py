#!/usr/bin/env python3
"""Run a Ledger Scout research mission (offline by default)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ledger_scout.missions import research


def main():
    scenario = os.getenv("LEDGERSCOUT_SCENARIO", "knitwear")
    ledger, events = research.run(scenario=scenario)
    print()
    print(research.traceability(ledger))
    print()
    print(f"Event stream: {events.path} ({events.seq} events)")


if __name__ == "__main__":
    main()
