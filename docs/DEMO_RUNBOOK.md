# Demo runbook — 5 minutes

Structure: **(1)** architecture + **(2)** two pre-baked scenarios as a 1:40 story, then **(3)** a
live run that proves the Stripe charges are real. Safety net at the bottom.

---

## Pre-flight checklist (before the clock starts)

1. `.env` has `STRIPE_SECRET_KEY=sk_test_...` (the live-key guard refuses `sk_live_`).
2. Connectivity smoke test prints `status: succeeded`:
   ```bash
   python3 -m ledger_scout.payments.verify_stripe --amount 1
   ```
3. **Terminal A** running the server (from project root), browser open on the ① Knitwear tab:
   ```bash
   python3 -m http.server 8000   # open http://localhost:8000/frontend/canvas.html
   ```
4. Stripe dashboard open in a second browser tab, in **test mode**, Payments view.
5. Keep `USE_REAL_GEMINI=0` for a fast, deterministic breakdown.

---

## The story (1:40) — narration with stage directions

**[0:00–0:15 · Hook]** *(Canvas on ① Knitwear, hero visible)*
> "Merch teams don't need another chatbot — they need an answer they can defend to a regulator.
> Ledger Scout is a team of agents that **shops for real data**, pays for premium datasets **with
> Stripe**, and stays under a budget a human controls. One question in; an audit-ready brief out."

**[0:15–0:45 · Architecture]** *(Point at THE AGENT ORG strip)*
> "Five agents, four human gates. The **Analyst** breaks the question into data needs. The **Scout**
> shops real sources — HuggingFace, Eurostat, Google Trends for free; ecoinvent and Statista for
> money. **Procurement** splits the euro budget. The **Coordinator** pays and negotiates. The
> **Synthesizer** turns datasets into the answer, with full lineage in a governed catalog. Money
> moves only through human-approved gates."

**[0:45–1:05 · Scenario 1 — human approves]** *(Point at PAY & NEGOTIATE)*
> "Knitwear: the agent pays ecoinvent €40 on its own — then Statista would blow the €55 budget, so it
> **stops and asks me** to approve €15 more. I approve; it buys."

**[1:05–1:25 · Scenario 2 — autonomous]** *(Click the ② Denim tab)*
> "Same engine, sustainable denim. Here the LCA over-runs its slice, but instead of asking, the agents
> **reallocate budget between datasets autonomously** and stay in bounds. Approve, or self-balance —
> same orchestration."

**[1:25–1:40 · Payoff + handoff]** *(Scroll to THE ANSWER)*
> "And here's why the spend matters: with free data alone, the recycled-cotton claim is **58%
> verifiable — high risk**. The €40 LCA buy makes it **92% and defensible**. That gap is the ROI.
> Now let's run it **for real** and watch the euros hit Stripe."

*(Optional third beat if asked: ③ Recycled activewear — human **declines** the spend, agent downgrades
to the free tier, brief is honest: "GO, claim at risk — do not publish the claim.")*

---

## Live run (the proof)

**Terminal B — run the mission with real test-mode charges:**
```bash
LEDGERSCOUT_STRIPE_LIVE=1 LEDGERSCOUT_SCENARIO=knitwear python3 scripts/run_research.py
```
Writes real PaymentIntents to Stripe and streams to `data/events.jsonl` (~3 seconds).

**Browser:** click the **"Live run"** tab → the fresh run renders.

**Stripe dashboard:** refresh `https://dashboard.stripe.com/test/payments` → two new **succeeded**
PaymentIntents (€40 ecoinvent, €30 Statista) whose `pi_…` ids **match the ids in the canvas's Governed
catalog**.

> Talk track during the run: *"Real PaymentIntents, real succeeded charges — the same ids appear in
> the Stripe dashboard. Test mode, so no real money, but the payment rail is genuinely live. Swap the
> test key for a live key and a real provider checkout, and the agents are buying data for real."*

---

## Safety net

- **Live run hiccups (network / Stripe down):** click the pre-baked **③ Recycled activewear** tab and
  narrate the "human declines → honest claim-at-risk" beat — same story, zero network.
- **Canvas can't load logs:** you served from the wrong folder. Serve from the **project root** and
  open `/frontend/canvas.html` (the canvas reads `../data/`).
- **`verify_stripe` refuses to run:** your key is `sk_live_…`. Use `sk_test_…` for the demo.
