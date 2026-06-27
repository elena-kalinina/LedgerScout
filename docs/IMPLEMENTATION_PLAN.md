# Implementation plan — hackathon build day (~9 hours)

Golden rule: **offline demo must work at every hour.** All live paths behind env toggles; fall back to stubs on error.

Prep is done in this repo — build day is polish, canvas, and optional live integrations.

---

## Hour 0 — Baseline (30 min)

```bash
cd LedgerScout
python3 -m venv .venv && source .venv/bin/activate   # optional
pip install -r requirements.txt                        # optional for offline
python3 tests/test_research_mission.py
python3 scripts/run_research.py
LEDGERSCOUT_SCENARIO=sustainable_denim python3 scripts/run_research.py
```

- [ ] All tests green
- [ ] Traceability tables look sane
- [ ] `data/events.jsonl` written

---

## Hour 1 — Mission & scenarios (45 min)

- [ ] Verify scenario scripts match demo narration (`docs/DEMO_SCENARIOS.md`)
- [ ] Tune fixture `credit_cost` values so conflict beat triggers reliably (premium ~38, slice ~30)
- [ ] Snapshot golden logs:

```bash
LEDGERSCOUT_SCENARIO=knitwear python3 scripts/run_research.py
cp data/events.jsonl data/events_knitwear.jsonl
LEDGERSCOUT_SCENARIO=sustainable_denim python3 scripts/run_research.py
cp data/events.jsonl data/events_denim.jsonl
```

---

## Hour 2 — Canvas (60 min)

- [ ] Serve frontend: `cd frontend && python3 -m http.server 8000`
- [ ] Canvas replays `events_knitwear.jsonl` / `events_denim.jsonl`
- [ ] Add: credit ring, dataset cards from `candidates` events, catalog badges
- [ ] Borrow card renderer from Lupo `frontend/canvas.html` if time

**Cut:** keep stub feed if behind — CLI traceability is enough.

---

## Hour 3 — Scout & fixtures (60 min)

- [ ] Verify resale slug ↔ cache filename alignment (`_slug(query).json`)
- [ ] Refresh resale fixtures with real Vinted snapshot if `LEDGERSCOUT_RESALE_LIVE=1` works
- [ ] Add 1–2 more compliance fixture rows if demo feels thin

---

## Hour 4 — Synthesis & lineage (45 min)

- [ ] Tune `_trend_score` weights if scores look absurd (>100 clamped already)
- [ ] Ensure `traceability()` prints metrics + catalog section
- [ ] Optional: markdown export `outputs/brief.md` on publish

---

## Hour 5 — Optional Gemini (45 min)

```bash
export USE_REAL_GEMINI=1
export GEMINI_API_KEY=...
```

- [ ] Analyst plan via `ledger_scout/llm.py`
- [ ] Synthesis narrative paragraph (keep numbers from stub math)
- [ ] Verify fallback on API error

**Cut first if behind.**

---

## Hour 6 — Optional live trends (45 min)

```bash
pip install pytrends
export LEDGERSCOUT_TRENDS_LIVE=1
```

- [ ] Implement `_search_live` in `sources/trends.py`
- [ ] Cache to `data/trends_cache/`
- [ ] Re-run mission with live off for demo

---

## Hour 7 — Architecture & pitch (45 min)

- [ ] Update `frontend/architecture.svg` if roster changed
- [ ] Rehearse 3-minute script (`docs/DEMO_SCENARIOS.md`)
- [ ] Prepare 1-slide Collibra mapping (catalog, lineage, glossary, quality)

---

## Hour 8 — Harden (45 min)

- [ ] Run tests after any changes
- [ ] Record screen capture of canvas or terminal
- [ ] Pre-flight: turn OFF all live toggles for main demo

---

## Hour 9 — Buffer / submission

- [ ] Zip or push repo (when ready to commit)
- [ ] Video / slide deck if required
- [ ] Partner API attempts only if hours 1–7 done

---

## Cut order (reminder)

Gemini → denim scenario → canvas polish → live trends → live resale  
**Never cut:** coordinator, credit conflict, catalog, quant metrics, offline path.

---

## Pre-demo checklist

- [ ] `python3 tests/test_research_mission.py`
- [ ] Knitwear scenario end-to-end < 5 sec
- [ ] Canvas or terminal rehearsed
- [ ] Know env vars to disable live mode instantly
- [ ] `docs/HACKATHON_NOTE.md` talking points memorized
