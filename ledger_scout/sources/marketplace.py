"""The data marketplace — real datasets the Scout can shop, free and premium.

Each candidate references a REAL dataset (title, provider, URL, license). Free/open
datasets cost nothing; premium datasets carry a real EUR price the agent pays via
Stripe. Fixtures make the demo deterministic offline; live fetchers (Eurostat,
HuggingFace, Google Trends) enrich the free candidates with fresh numbers when their
toggles are on, then fall back to the fixture on any error.

Candidate schema:
    id, title, summary, provider, url, license, tier ("free"|"premium"),
    price_eur, quality_score, freshness_days, schema_fields, stats,
    live (bool), cheaper_alternative (optional dict for the downgrade beat)
"""
import copy

from . import eurostat, huggingface, trends

# How each need is used to answer the brief — the sub-question it resolves and the
# metric it feeds. Drives the "what we bought → how it's used" utilization trace.
USE_MAP = {
    "resale_demand": {"answers": "Is there real resale/circular demand (not runway hype)?",
                      "feeds": "trend_score", "key_stat": "reuse_share"},
    "search_interest": {"answers": "Is consumer search interest rising?",
                        "feeds": "trend_score", "key_stat": "interest_index"},
    "material_composition": {"answers": "What recycled content do comparable garments carry?",
                             "feeds": "claim grounding", "key_stat": "recycled_cotton_variant_share"},
    "lca_impact": {"answers": "Can we defend the environmental claim? (EU Green Claims)",
                   "feeds": "gwp_reduction_pct + claim_verifiability", "key_stat": "gwp_reduction_pct"},
    "market_benchmark": {"answers": "What price band / willingness-to-pay supports the buy?",
                         "feeds": "market_cagr + wtp_premium", "key_stat": "wtp_premium_pct"},
}

# --------------------------------------------------------------------------- #
# Real dataset catalog, keyed by data need.
# --------------------------------------------------------------------------- #
CATALOG = {
    "resale_demand": [
        {
            "id": "hf-wargon-secondhand",
            "title": "Second-Hand Clothing Dataset (Wargön Innovation / RISE)",
            "summary": "43,132 sorted second-hand garments with reuse/recycle/repair labels and condition grades.",
            "provider": "Hugging Face · wargoninnovation/clothingdatasetsecondhand",
            "url": "https://huggingface.co/datasets/wargoninnovation/clothingdatasetsecondhand",
            "license": "Research use (CISUTAC / Vinnova project)",
            "tier": "free",
            "price_eur": 0,
            "quality_score": 0.82,
            "freshness_days": 60,
            "schema_fields": ["item_id", "category", "usage", "condition", "station"],
            "stats": {"items": 43132, "reuse_share": 0.71, "recycle_share": 0.21},
            "hf_repo": "wargoninnovation/clothingdatasetsecondhand",
        },
        {
            "id": "eurostat-worn-clothing",
            "title": "Used/worn textiles trade (Eurostat Comext, CN 6309)",
            "summary": "EU import/export volumes of worn clothing — a proxy for resale/circular supply.",
            "provider": "Eurostat Comext",
            "url": "https://ec.europa.eu/eurostat/databrowser/product/view/DS-045409",
            "license": "Eurostat — free reuse with attribution",
            "tier": "free",
            "price_eur": 0,
            "quality_score": 0.7,
            "freshness_days": 120,
            "schema_fields": ["reporter", "partner", "product", "flow", "value_eur", "period"],
            "stats": {"eu_worn_textile_trade_index": 112, "yoy_delta_pct": 9},
            "eurostat_ref": "DS-045409",  # Comext (not on the JSON-stat live API) — static reference
        },
    ],
    "search_interest": [
        {
            "id": "google-trends-recycled-knit",
            "title": "Google Trends — recycled cotton knitwear (Benelux)",
            "summary": "Search-interest index and YoY momentum for recycled/sustainable knitwear terms.",
            "provider": "Google Trends (pytrends)",
            "url": "https://trends.google.com/trends/explore?q=recycled%20cotton%20knitwear&geo=BE",
            "license": "Google Trends — free, rate-limited",
            "tier": "free",
            "price_eur": 0,
            "quality_score": 0.62,
            "freshness_days": 2,
            "schema_fields": ["term", "geo", "interest_index", "period"],
            "stats": {"interest_index": 68, "yoy_delta_pct": 14},
            "trends_query": "recycled cotton knitwear",
            "trends_geo": "BE",
        },
    ],
    "material_composition": [
        {
            "id": "zenodo-garment-variant",
            "title": "Fast-fashion Garment-Variant Dataset (H&M + Uniqlo)",
            "summary": "47,522 colour-specific garment variants with normalized material composition for circularity analysis.",
            "provider": "Zenodo · Li & Walther (2026)",
            "url": "https://doi.org/10.5281/zenodo.20006389",
            "license": "CC-BY (curated release materials)",
            "tier": "free",
            "price_eur": 0,
            "quality_score": 0.78,
            "freshness_days": 90,
            "schema_fields": ["variant_id", "brand", "category", "material", "share_pct", "country"],
            "stats": {"records": 47522, "recycled_cotton_variant_share": 0.12, "cotton_share": 0.46},
        },
    ],
    "lca_impact": [
        {
            "id": "ecoinvent-textiles-312",
            "title": "ecoinvent v3.12 — textiles LCA (recycled vs conventional cotton)",
            "summary": "Peer-reviewed cradle-to-gate impact factors (GWP, water, energy) for ~230 textile activities — the evidence to defend a 'recycled cotton' claim.",
            "provider": "ecoinvent Association",
            "url": "https://ecoinvent.org/database/",
            "license": "ecoinvent commercial license (single-user)",
            "tier": "premium",
            "price_eur": 40,
            "quality_score": 0.95,
            "freshness_days": 30,
            "schema_fields": ["activity", "geography", "gwp_kg_co2e", "water_m3", "energy_mj", "system_model"],
            "stats": {
                "gwp_recycled_cotton_kg": 2.1,
                "gwp_conventional_cotton_kg": 5.9,
                "gwp_reduction_pct": 64,
                "verifiability": 0.92,
                "regulatory_risk": "low",
            },
            "cheaper_alternative": {
                "id": "open-lca-proxy",
                "title": "Open LCA proxy factors (literature average)",
                "summary": "Free aggregated literature estimates — directional only, not jurisdiction-specific.",
                "provider": "Open literature / OpenLCA Nexus",
                "url": "https://nexus.openlca.org/",
                "license": "Mixed open licenses",
                "tier": "free",
                "price_eur": 0,
                "quality_score": 0.55,
                "freshness_days": 365,
                "schema_fields": ["material", "gwp_estimate_kg"],
                "stats": {
                    "gwp_recycled_cotton_kg": 2.6,
                    "gwp_conventional_cotton_kg": 5.2,
                    "gwp_reduction_pct": 50,
                    "verifiability": 0.58,
                    "regulatory_risk": "high",
                },
            },
        },
    ],
    "market_benchmark": [
        {
            "id": "statista-sustainable-apparel-eu",
            "title": "Statista — Sustainable apparel market, Europe",
            "summary": "Market size, growth, price bands and consumer willingness-to-pay for sustainable clothing.",
            "provider": "Statista",
            "url": "https://www.statista.com/markets/415/topic/466/apparel/",
            "license": "Statista single-account license",
            "tier": "premium",
            "price_eur": 30,
            "quality_score": 0.88,
            "freshness_days": 45,
            "schema_fields": ["segment", "market_size_eur", "cagr_pct", "price_band", "wtp_premium_pct"],
            "stats": {"cagr_pct": 11, "wtp_premium_pct": 27, "price_band_eur": "60-95"},
            "cheaper_alternative": {
                "id": "eurostat-apparel-cpi",
                "title": "Eurostat apparel HICP + PRODCOM (free benchmark)",
                "summary": "Official apparel price index and production volumes — coarse, no segment detail.",
                "provider": "Eurostat",
                "url": "https://ec.europa.eu/eurostat/databrowser/product/view/prc_hicp_midx",
                "license": "Eurostat — free reuse with attribution",
                "tier": "free",
                "price_eur": 0,
                "quality_score": 0.6,
                "freshness_days": 90,
                "schema_fields": ["coicop", "geo", "index", "period"],
                "stats": {"cagr_pct": 7, "wtp_premium_pct": None, "price_band_eur": "n/a"},
                "eurostat_dataset": "prc_hicp_midx",
                # Pin one cell: EU27 garments (CP0312) HICP index, latest month only.
                "eurostat_params": {"geo": "EU27_2020", "coicop": "CP0312", "unit": "I15"},
            },
        },
    ],
}


def _enrich_one(candidate):
    """Dispatch a single candidate to its live fetcher (no-op without the right marker)."""
    if candidate.get("hf_repo"):
        huggingface.enrich(candidate)
    elif candidate.get("eurostat_dataset"):
        eurostat.enrich(candidate)
    elif candidate.get("trends_query"):
        trends.enrich(candidate)


def _augment_live(candidate):
    """Best-effort live enrichment of a candidate AND its free fallback proxy.

    Enriching the nested `cheaper_alternative` means the *free-only* answer is also
    computed from real fetched numbers (e.g. Eurostat HICP) when toggles are on.
    Silent fallback to the fixture on any error — fixtures are valid real references.
    """
    try:
        _enrich_one(candidate)
    except Exception:
        pass
    alt = candidate.get("cheaper_alternative")
    if alt:
        try:
            _enrich_one(alt)
        except Exception:
            pass
    return candidate


def search(need_name, tags=None, live=False):
    """Return ranked dataset candidates for a need (deep-copied so callers can mutate)."""
    candidates = [copy.deepcopy(c) for c in CATALOG.get(need_name, [])]
    if live:
        for c in candidates:
            _augment_live(c)
    candidates.sort(key=lambda c: (-c.get("quality_score", 0), c.get("price_eur", 0)))
    return candidates
