# Demo scenarios, pitches & Collibra hook

## Collibra hook (say this in the close)

> **The agent shops and pays; the catalog makes it enterprise-safe.**  
> Every external dataset — free or a real Stripe purchase — is registered with license, freshness, quality score, tier, payment id, and business-glossary links before it touches a merchandising decision. That is governed data acquisition — the problem Collibra solves at scale.

Two things judges should remember:

1. **Agentic breakdown** — the Analyst decomposes one question into named data needs, each with a rationale, a real source, and a free/paid tier.
2. **Budget negotiation** — agents pay autonomously within budget, **reallocate slack** between datasets, and **ask the human to approve a budget increase** when premium data would blow the total — paid for real with Stripe.

Differentiators to name explicitly:

- **Real datasets + real payments** — HuggingFace / Eurostat / Zenodo / Google Trends (free) + ecoinvent / Statista (paid via Stripe)
- **Lineage** — metric → dataset → agent → human decision → payment id
- **Data quality dimensions** — freshness, quality score, tier (free vs premium)

---

## Suggested one-liners

| Audience | Line |
|----------|------|
| **Track 2 (general)** | *Send agents to the data market with a budget; they come back with trends you can defend in a board meeting.* |
| **Collibra** | *Agentic data shopping with PEPPOL-grade provenance — for fashion claims and trend intelligence.* |
| **Fashion retail** | *One question for your AW26 knitwear line — quantitative signals plus compliance gaps, sourced and governed.* |
| **Technical** | *Lupo's coordination layer, swapped from Vinted listings to governed research datasets.* |

---

## Scenario A — Knitwear (primary demo, ~3 min) · *human approves spend*

**Brief:**  
*Should we increase recycled-cotton knitwear for AW26 in the Benelux, and can we defend the "recycled cotton" claim?*

| Setting | Value |
|---------|--------|
| Scenario key | `knitwear` |
| Market | Benelux |
| Budget | €55 |
| Human script | amend resale + claim focus → approve split → **stretch** (approve budget increase) → confirm publish |

### Story beats

| Time | Beat |
|------|------|
| 0:00 | Hook + open canvas |
| 0:20 | Analyst **breaks the question down** into 5 data needs, each with a rationale + source + free/paid tier |
| 0:45 | Human amends: *prioritize resale demand and claim evidence* |
| 1:00 | Scouts shop the marketplace; Procurement splits the budget across the two premium datasets |
| 1:15 | Agent pays **€40 to ecoinvent** for LCA evidence autonomously (real Stripe charge) |
| 1:35 | **Peak:** Statista (€30) would blow the €55 budget → agent **asks the human to approve +€15** → approved → pays €30 |
| 2:00 | Catalog registers all 5 assets (with payment ids); Synthesizer: trend 88/100, claim 92% verifiable |
| 2:20 | Lineage table — every number traceable to a dataset + payment |
| 2:35 | Collibra close |

### Expected output

- Trend score 88/100, confidence 0.89
- GWP reduction 64%, claim verifiability 92%, regulatory risk: low
- 2 premium datasets paid (€40 + €30), budget raised €15, €70 spent
- **Answer: GO** — publish the recycled-cotton claim, it's defensible
- **Free-only would say: "GO, claim at risk"** (58% verifiable, high regulatory risk, no WTP) — so the
  €70 spend is what unlocks the defensible claim (+0.18 confidence, flips the verdict)

### "Good use of what we bought"

- Each acquisition emits a **utilization** trace: `dataset → fields it provides → metric it feeds →
  sub-question it answers`. At payment time you see exactly what the €40 ecoinvent buy delivers and why.
- The Synthesizer answers the brief **twice** (full vs free-only) and itemizes the *value of paid* —
  the canvas renders this as a side-by-side verdict comparison.

```bash
python3 scripts/run_research.py                              # offline simulator
LEDGERSCOUT_STRIPE_LIVE=1 python3 scripts/run_research.py    # real Stripe charges
```

---

## Scenario B — Sustainable denim (backup, ~90 sec) · *agent reallocates*

**Brief:**  
*Can we launch €79–99 sustainable denim in Germany for SS27?*

| Setting | Value |
|---------|--------|
| Scenario key | `sustainable_denim` |
| Market | Germany |
| Budget | €70 |
| Human script | prioritize claim evidence → approve split → (no human needed) → confirm |

### Why this scenario exists

Shows the **autonomous** coordination move: the LCA dataset over-runs its budget slice, so the agents
**reallocate slack** from the market-benchmark slice and stay within total budget — **no human needed**.
The complement to Scenario A's human-approval beat.

```bash
LEDGERSCOUT_SCENARIO=sustainable_denim python3 scripts/run_research.py
```

---

## Scenario C — Recycled activewear (~60 sec) · *human declines, graceful downgrade*

**Brief:**  
*Can we claim "recycled polyester" for SS27 activewear in France on a tight budget?*

| Setting | Value |
|---------|--------|
| Scenario key | `recycled_activewear` |
| Market | France |
| Budget | €35 (deliberately tight) |
| Human script | prioritize claim evidence → approve split → **cheaper** (decline the €40 LCA) → confirm |

### Why this scenario exists

The third negotiation move: the agent asks to buy the €40 LCA evidence, but it **exceeds the tight
budget**, so it escalates — and the human **declines the spend**. The agent **gracefully downgrades**
to the free Open-LCA proxy, and the brief is **honest about the cost**: claim verifiability drops to
58% (high regulatory risk), so the verdict is **"GO, claim at risk — do NOT publish the claim."** It
still pays €30 for the market benchmark within budget. Demonstrates that the system won't fabricate
confidence it didn't pay for.

Together the three scenarios cover the full arbitration space: **approve more budget** (knitwear),
**reallocate autonomously** (denim), **decline → downgrade** (activewear).

```bash
LEDGERSCOUT_SCENARIO=recycled_activewear python3 scripts/run_research.py
```

---

## Demo script (narration)

The canvas is built to be read top-to-bottom as a 6-act story. Talk to the sections.

**Cold open (10s)** — *"One merchandising question. Instead of a chatbot guessing, watch a team of
agents shop real data — including paid datasets — and pay for it with Stripe, with a human holding
the purse strings."* Point at the **hero**: GO verdict, and the headline number — *"€70 of paid data
flipped the answer from 'claim at risk' to a defensible GO."*

1. **The agent org** — five agents, four human gates. *"This is an org, not a prompt."*
2. **① Breakdown** — *"The Analyst decomposes the question: to answer it we need resale demand,
   search interest, material composition, LCA evidence, and a market benchmark — three free, two paid."*
3. **② Datasets shopped** — *"It shops real sources: HuggingFace, Eurostat, Zenodo, Google Trends for
   free; ecoinvent and Statista for money."*
4. **③ Pay & negotiate** (the peak) — *"It pays €40 to ecoinvent on its own. Then Statista would blow
   the €55 budget, so it stops and asks the human to approve €15 more."* Show the **real charge in the
   Stripe dashboard.** *"On the denim run, it instead reallocates budget between datasets — no human
   needed."*
5. **④ From data → answer** — *"Every purchase is accounted for: what fields it bought, which metric it
   feeds, which sub-question it answers. No black box."*
6. **⑤ The answer** — *"Here's the honest part: with free data alone, the recycled-cotton claim is only
   58% verifiable — high regulatory risk. The €40 ecoinvent buy is what makes it 92% and defensible.
   That gap is the ROI of the spend."*

**Close** — *"Agentic data shopping with real payments — and a governed catalog with lineage that makes
every number audit-ready. Swap our marketplace for yours; the coordination layer stays."*

---

## Pre-demo checklist

- [ ] `python3 tests/test_research_mission.py` passes
- [ ] `python3 -m ledger_scout.payments.verify_stripe` shows a succeeded charge
- [ ] Golden `data/events_knitwear.jsonl` / `events_denim.jsonl` regenerated for the canvas
- [ ] Stripe dashboard (test mode) open on a second screen to show real charges
- [ ] Architecture SVG open; know how to disable live toggles instantly
