# Data sources

Fixture-first for demo reliability; every fixture references a **real dataset** (title, provider,
URL, license). Live fetchers are **optional toggles**. Premium datasets carry a real **EUR price**
the agent pays with Stripe.

## Budget model

The research budget is **real EUR**. Free/open datasets cost €0; premium datasets are paid for with
**Stripe PaymentIntents** (test mode → genuine succeeded charges, no funding needed). With
`LEDGERSCOUT_STRIPE_LIVE=0` a deterministic local simulator mirrors the same accept/decline logic.

| Tier | Price | Quality | Freshness | Pays via |
|------|-------|---------|-----------|----------|
| Free / open | €0 | 0.55–0.82 | 1–120 days | — |
| Premium | €30–40 | 0.88–0.95 | 30–45 days | Stripe |

---

## Datasets in the demo

| Need | Dataset | Provider | Tier | Live toggle |
|------|---------|----------|------|-------------|
| `resale_demand` | Second-Hand Clothing Dataset (43k items) | HuggingFace · wargoninnovation/clothingdatasetsecondhand | free | `LEDGERSCOUT_HF_LIVE=1` |
| `resale_demand` | Worn textiles trade (CN 6309) | Eurostat Comext | free | `LEDGERSCOUT_EUROSTAT_LIVE=1` |
| `search_interest` | Recycled-cotton knitwear search interest | Google Trends (pytrends) | free | `LEDGERSCOUT_TRENDS_LIVE=1` |
| `material_composition` | Fast-fashion garment-variant (H&M+Uniqlo, 47k) | Zenodo | free | — |
| `lca_impact` | **ecoinvent v3.12 textiles LCA** (recycled vs conventional cotton) | ecoinvent Association | **premium €40** | paid (Stripe) |
| `market_benchmark` | **Statista** sustainable apparel market, Europe | Statista | **premium €30** | paid (Stripe) |

Premium needs carry a `cheaper_alternative` (a free Open-LCA / Eurostat proxy) used in the
"drop to free tier" human-decline beat.

### Live fetchers (free datasets)

- **HuggingFace** (`sources/huggingface.py`) — public Hub API, no key; enriches with live download
  counts + last-modified freshness.
- **Eurostat** (`sources/eurostat.py`) — dissemination API (JSON-stat), no key; best-effort latest
  observation, silent fallback to fixture.
- **Google Trends** (`sources/trends.py`) — pytrends; real interest index + YoY for the query/geo.

These fetchers enrich both the primary candidate **and its free `cheaper_alternative`**, so the
**free-only answer is computed from real fetched numbers** (e.g. live EU-garments HICP) when toggles
are on — not just fixtures. The answer event records `live_sources` per mode.

> ⚠️ Eurostat gotcha: a query with no dimension filters returns the **entire dataset (100+ MB)** and
> hangs. Candidates therefore carry `eurostat_params` (geo / coicop / unit) and the fetcher always
> adds `lastTimePeriod=1` to pin a single cell (sub-second response).

---

## Stripe payment rail (why PaymentIntents, not Issuing)

We first wired **Stripe Issuing** (the budget = a virtual card's spending limit, with real-time
authorization webhooks approving/declining). It works conceptually, but **EU sandbox accounts can't
fund the test Issuing balance** (EUR top-ups via `sepa_credit_transfer` are rejected; GBP funds but
cards must be EUR), so authorizations only ever returned `insufficient_funds`. Creating a new
sandbox to switch currency re-triggers the "verify your activity" KYC gate.

**PaymentIntents** sidestep all of it: a charge brings money *in*, so no balance is required — test
cards succeed immediately. The budget and the approve/reallocate/escalate decisions live in the
agent orchestration (Procurement + Coordinator + human gates), which is where the multi-agent
showcase belongs anyway. The real Stripe artifact is a **succeeded charge per approved dataset**.

```bash
python3 -m ledger_scout.payments.verify_stripe --amount 40    # one real test charge
```

---

## Candidate dict contract (marketplace)

```python
{
  "id": "ecoinvent-textiles-312",
  "title": "ecoinvent v3.12 — textiles LCA ...",
  "summary": "One-line description",
  "provider": "ecoinvent Association",
  "url": "https://ecoinvent.org/database/",
  "license": "ecoinvent commercial license (single-user)",
  "tier": "free" | "premium",
  "price_eur": 40,
  "quality_score": 0.95,
  "freshness_days": 30,
  "schema_fields": ["activity", "gwp_kg_co2e", ...],
  "stats": {},                    # source-specific aggregates the synthesizer reads
  "live": False,                  # set True when a live fetcher enriched it
  "cheaper_alternative": { ... }  # optional free fallback for the downgrade beat
}
```

---

## Legal / demo hygiene

- Document **license** on every candidate (done in `sources/marketplace.py`).
- Premium dataset *access* is represented by a real payment; we ship only aggregate stats, never
  redistribute the licensed data.
- Treat any live listing/text as **untrusted** if you add LLM extraction later.
