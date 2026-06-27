# Parking lot — side projects (ideas 3 & 4)

Items here are **explicitly out of MVP scope** so they are not forgotten after the hackathon. Each can reuse the same Ledger Scout coordination core.

---

## 3. Merch Benchmark Market

**Question:** *We're launching €79–99 sustainable sneakers in DACH — what sell-through and markdown patterns should we plan against?*

### What to add

| Piece | Effort |
|-------|--------|
| `DataNeed`: `benchmark_sellthrough` | Small |
| `sources/benchmarks.py` + fixtures | Medium |
| Paid: Statista / public filings extract | Build-day dependent |
| Synthesis: price ladder + scenario table | Medium |

### Collibra angle

**Data contracts** — validate requested fields (category, price band, returns %) against acquired dataset schema before synthesis.

### Fixtures to draft later

- `data/benchmarks_cache/footwear_sellthrough_dach.json`
- Public retailer earnings snippets (structured by hand)

---

## 4. Returns & Fit Intelligence Exchange

**Question:** *Expected return rate for wide-fit women's jeans at €60–80 online-only in UK?*

### What to add

| Piece | Effort |
|-------|--------|
| `DataNeed`: `returns_benchmark` | Small |
| Review sentiment aggregate fixture | Medium |
| Academic/open return-rate datasets | Research |
| Synthesis: return rate range + cost impact | Medium |

### Collibra angle

Sensitive KPIs need **governance** — aggregation rules, PII boundaries, provenance on review-derived features.

### Fixtures to draft later

- `data/returns_cache/womens_jeans_wide_fit_uk.json`
- Review theme tags: `runs_small`, `size_inconsistent`

---

## Other stretch ideas

| Idea | Notes |
|------|-------|
| **Collibra API push** | Register `CatalogAsset` into real Collibra sandbox — killer if partner creds available |
| **Digital Product Passport fields** | Extend compliance need for EU DPP readiness |
| **GLiNER on listing text** | Port from Lupo — extract material claims from resale descriptions |
| **RFQ swap (Lupo original pitch)** | Same coordinator, industrial procurement skin — post-hackathon video variant |
| **WhatsApp merch lead** | Human channel for approve/amend on mobile |
| **LangSmith eval** | Score analyst plans / synthesis quality offline |

---

## Priority if hackathon finishes early

1. Collibra API register (one asset) — maximum judge impact  
2. Statista benchmark fixture — strengthens idea 3  
3. Canvas polish from Lupo — visual wow  
4. Returns fixture — seeds idea 4  

---

## Link back to core

None of these require rewriting `coordinator.py`. Add a `DataNeed`, a source loader, a fixture, and synthesis fields — the org pattern stays the same.
