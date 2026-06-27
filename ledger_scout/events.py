"""Event stream — every coordination action emits an event for the canvas."""
import json
from datetime import datetime, timezone
from pathlib import Path

EVENT_LOG = Path(__file__).resolve().parent.parent / "data" / "events.jsonl"


class EventStream:
    def __init__(self, path=EVENT_LOG, echo=True):
        self.path = Path(path)
        self.echo = echo
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("")
        self.seq = 0

    def emit(self, kind, actor, **data):
        """kind: task|message|escalation|human_reply|budget|decision|deal|plan|payment|
               utilization|answer|candidates|catalog_register|metric|synthesis."""
        self.seq += 1
        ev = {
            "seq": self.seq,
            "ts": datetime.now(timezone.utc).isoformat(),
            "kind": kind,
            "actor": actor,
            **data,
        }
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(ev) + "\n")
        if self.echo:
            self._print(ev)
        return ev

    @staticmethod
    def _print(ev):
        icon = {
            "task": "→",
            "plan": "🧩",
            "message": "💬",
            "escalation": "⚠ ",
            "human_reply": "🙋",
            "budget": "📊",
            "decision": "✓",
            "payment": "💳",
            "utilization": "🧮",
            "answer": "🎯",
            "deal": "📦",
            "candidates": "🔍",
            "catalog_register": "📚",
            "metric": "📈",
            "synthesis": "📋",
        }.get(ev["kind"], "·")
        detail = ev.get("text") or ev.get("summary") or ""
        print(f"  {icon} [{ev['actor']:<14}] {ev['kind']:<16} {detail}")
