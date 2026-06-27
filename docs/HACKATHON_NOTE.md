# Hackathon note (strategic)

**Project:** Ledger Scout  
**Track:** 2 — Agentic data shopping (Collibra)  
**Blend:** Compliance Data Bazaar + Trend Ledger (fashion retail)

## Problem

Fashion merchandisers need **quantitative, sourced** answers for assortment and compliance:

- *Is knitwear trending in Benelux for AW26?*
- *Can we claim "recycled cotton" without regulatory risk in DE?*

Today: spreadsheets, consultants, and vibes — not governed external data.

## Solution

Ledger Scout coordinates a **research org**:

| Agent | Role |
|-------|------|
| **Analyst** | Brief → structured data needs |
| **Scout** | Shops sources, ranks datasets |
| **Procurement** | Allocates & arbitrates research credits |
| **Synthesizer** | Quant brief + lineage |
| **Catalog** | Collibra-shaped metadata on every asset |

The human (merch lead) approves plan, credit split, and publish — same coordination pattern as **Lupo** (personal shopper org), reskinned for data shopping.

## Why Lupo as foundation

Lupo already implements the hard part the track asks for:

- Multi-agent coordination **with humans in the loop**
- Shared ledger + budget arbitration
- Escalate vs proceed policy
- Event stream for visible coordination
- Offline-first fixtures + live toggles

We swap the domain layer: Vinted listings → research datasets.

## Why Collibra cares

Not "more data" — **trusted, governed, discoverable data**:

- External data catalog with license & freshness
- Lineage from metric → dataset → decision
- Business glossary (`data/glossary.yaml`)
- Quality-driven budget tradeoffs (premium vs free tier)

## Hackathon constraints

- ~9 hours build time
- No confirmed paid APIs — credits are metaphorical; fixtures ship the demo
- Single senior builder + AI tooling

## Success criteria

3-minute demo: one fashion question → agents shop within budget → conflict resolved → governed quantitative brief with lineage.

## Non-goals

See `docs/MVP_SCOPE.md`. Ideas 3–4 in `docs/PARKING_LOT.md`.
