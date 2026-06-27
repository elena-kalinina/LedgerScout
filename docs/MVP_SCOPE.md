# MVP scope

Hackathon constraints: **24h total**, **~9h building**, team = senior builder + AI tools. No confirmed paid APIs — budget is a **research-credits metaphor**, not literal spend.

## In scope (must ship)

| # | Deliverable | Notes |
|---|-------------|--------|
| 1 | **Research mission** | `ledger_scout/missions/research.py` — two scenarios, scripted human |
| 2 | **Coordinator flow** | Plan → credit split → scout sources → conflict → synthesize → publish |
| 3 | **Agent roster** | Analyst, Scout, Procurement, Synthesizer (+ Catalog on acquire) |
| 4 | **Two data families** | Trend (resale + search interest) + Compliance (claims + LCA) |
| 5 | **Fixture-first sources** | All demos run offline from `data/*_cache/` |
| 6 | **Collibra-shaped catalog** | License, freshness, quality score, glossary terms per asset |
| 7 | **Quant output** | `trend_score`, `confidence`, `claim_verifiability`, `regulatory_risk` + lineage |
| 8 | **Event stream + canvas stub** | `data/events.jsonl` → `frontend/canvas.html` |
| 9 | **Smoke tests** | `tests/test_research_mission.py` green offline |
| 10 | **Architecture diagram** | `frontend/architecture.svg` |

## Human gates (3 — same pattern as Lupo)

1. Approve / amend **research plan**
2. Approve **credit allocation**
3. **Publish** research brief (side-effectful)

## Conflict beat (required for demo drama)

Premium compliance dataset **8 credits over slice** → human chooses:

- **Knitwear scenario:** `stretch` (reallocate credits)
- **Denim scenario:** `cheaper` (downgrade to free/stale tier)

## Out of scope (explicit — do not build on hackathon day)

| Item | Why out | Where it lives |
|------|---------|----------------|
| Collibra API / real catalog integration | Mock metadata is enough for pitch | Parking lot |
| Paid APIs (Statista, etc.) | Not confirmed; check build day only | `docs/DATA_SOURCES.md` |
| Merch benchmark market (idea 3) | Side project | `docs/PARKING_LOT.md` |
| Returns & fit intelligence (idea 4) | Side project | `docs/PARKING_LOT.md` |
| Full canvas redesign | Stub replay is enough | Polish only if time |
| Voice / WhatsApp human channel | Scripted channel suffices | Lupo has reference |
| Live web scraping at scale | Legal + demo risk | Fixture + optional single live cache |
| Multi-tenant auth, persistence | Not needed for 3-min demo | — |
| Negotiator / seller agents | Wrong metaphor for data shopping | — |

## Cut order (if behind schedule)

Drop from bottom up:

1. Gemini live toggle  
2. Denim scenario (keep knitwear only)  
3. Canvas polish (keep CLI + jsonl)  
4. Third compliance source  
5. Synthesis prose (keep numbers + lineage)

**Never cut:** coordinator flow, credit conflict, catalog register, ≥1 quant metric with lineage, offline demo path.

## Definition of done

```bash
python3 tests/test_research_mission.py          # all pass
python3 scripts/run_research.py                 # knitwear → traceability table
LEDGERSCOUT_SCENARIO=sustainable_denim python3 scripts/run_research.py
```

Demo can explain in 3 minutes: question → agents shop → budget conflict → governed datasets → quantitative brief.
