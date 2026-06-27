"""Scout — shops the data marketplace for each need, ranks candidates, proposes the best."""
from .base import Agent
from ..sources import marketplace
from .. import config


class Scout(Agent):
    role = "scout"

    def shop(self, need):
        candidates = marketplace.search(need.name, need.tags, live=self._live())
        if not candidates:
            self.emit("escalation", text=f"No dataset found for {need.name}")
            return None

        best = candidates[0]
        self.events.emit(
            "candidates",
            self.name,
            category=need.name,
            text=f"{need.name}: ranked {len(candidates)} dataset(s)",
            candidates=[
                {
                    "id": c.get("id"),
                    "title": c["title"],
                    "provider": c.get("provider", ""),
                    "tier": c.get("tier", "free"),
                    "price_eur": c.get("price_eur", 0),
                    "quality_score": c.get("quality_score", 0),
                    "freshness_days": c.get("freshness_days", 0),
                    "license": c.get("license", ""),
                    "url": c.get("url", ""),
                    "live": c.get("live", False),
                    "best": c is best,
                }
                for c in candidates
            ],
        )
        tier = best.get("tier", "free")
        price = best.get("price_eur", 0)
        cost = "free" if price == 0 else f"€{price:.0f} ({tier})"
        self.emit(
            "message",
            text=f"{need.name}: best fit '{best['title']}' — {cost}, Q={best.get('quality_score', 0):.0%}",
        )
        return best

    @staticmethod
    def _live():
        return config.USE_REAL_TRENDS or config.USE_REAL_EUROSTAT or config.USE_REAL_HF
