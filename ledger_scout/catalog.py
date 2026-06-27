"""Collibra-shaped catalog — governed metadata for every acquired dataset."""
from dataclasses import asdict, dataclass


@dataclass
class CatalogAsset:
    id: str
    name: str
    provider: str
    tier: str
    price_eur: float
    license: str
    freshness_days: int
    quality_score: float
    url: str
    schema_fields: list[str]
    glossary_terms: list[str]
    lineage_parent: str | None = None
    payment_id: str | None = None

    def to_dict(self):
        return asdict(self)


def register(events, *, need_name, candidate, glossary_terms, payment_id=None):
    """Register an acquired dataset in the catalog and emit a canvas event."""
    asset = CatalogAsset(
        id=candidate.get("id", need_name),
        name=candidate.get("title", need_name),
        provider=candidate.get("provider", "unknown"),
        tier=candidate.get("tier", "free"),
        price_eur=candidate.get("price_eur", 0),
        license=candidate.get("license", "unknown"),
        freshness_days=candidate.get("freshness_days", 999),
        quality_score=candidate.get("quality_score", 0.5),
        url=candidate.get("url", ""),
        schema_fields=candidate.get("schema_fields", []),
        glossary_terms=glossary_terms,
        lineage_parent=need_name,
        payment_id=payment_id,
    )
    events.emit(
        "catalog_register",
        "catalog",
        text=f"Registered: {asset.name} "
             f"(Q={asset.quality_score:.0%}, {asset.freshness_days}d, {asset.tier})",
        asset=asset.to_dict(),
    )
    return asset
