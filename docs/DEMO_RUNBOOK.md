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
3. **Terminal A** running the **stream server** (from project root), browser open on the ① Knitwear tab:
   ```bash
   python3 scripts/serve.py      # open http://localhost:8000/frontend/canvas.html
   ```
   (Plain `http.server` works for the recorded tabs, but the ▶ Run button needs `serve.py`.)
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

## Per-scenario narration (~1 min each, plain English)

Use these if you have time to walk through scenarios individually instead of the tight 1:40 story.

### ① Knitwear — *"the agent asks permission to spend"*

> We started with a real buying question: **should we make more recycled-cotton knitwear next autumn in
> the Benelux — and if we label it "recycled cotton," can we defend that if a regulator asks?**
>
> The agents broke that into five things we needed to know — our variables: is there genuine
> second-hand demand, is search interest rising, how much recycled content do similar garments actually
> have, what's the real environmental benefit, and is the market big enough with shoppers willing to pay
> more.
>
> The first three we got **for free** — resale listings, Google Trends, an open garment dataset — and
> they showed demand is real: a trend score of **88 out of 100**. The risky part is the green claim. On
> free data alone we could only stand behind it about **58%** — legally shaky. So the agent **paid €40**
> for a proper life-cycle dataset, which lifted the claim to **92% verifiable, low risk**, and **€30**
> for market data showing **11% growth** and a real price premium.
>
> Verdict: **go, and the claim is defensible.** The thing to watch: the agent paid on its own, but when
> the final purchase would break the budget, it **stopped and asked a human to approve €15 more.**

### ② Sustainable denim — *"the agents negotiate the budget themselves"*

> Same engine, different question: **can we launch a premium sustainable-denim line, around €79–99, in
> Germany next spring?**
>
> Same variables: the environmental evidence to back the "sustainable" label, the market size and price
> tolerance, plus second-hand demand and search interest as reality checks. The two **free** signals
> confirmed real pull. The environmental claim and the market sizing are worth paying for, so the agents
> bought the **life-cycle dataset (€40)** and the **market report (€30)**.
>
> The twist here: the life-cycle dataset cost a bit **more than the slice of budget it had been given.**
> Instead of bothering a human, the agents noticed **unused budget** in the market-data slice, quietly
> **moved it across**, and stayed within the total — no approval needed.
>
> The answer lands the same — strong demand, a **defensible claim at 92%**, a clear price band — but
> this scenario shows the agents **reallocating money among themselves** to get the job done.

### ③ Recycled activewear — *"the honest one: it won't fake confidence"*

> The third question is deliberately tight on money: **can we claim "recycled polyester" on a new
> activewear line in France — on a small budget?**
>
> The agents wanted solid environmental evidence first, which costs **€40**. But that purchase wouldn't
> fit the budget, so the agent **stopped and asked the human — and this time the human said no.**
>
> Rather than give up or pretend, the agent **fell back to a free, rough life-cycle estimate.** The
> honest consequence: the claim is only about **58% verifiable — high regulatory risk.** So the answer
> isn't a clean yes. It's: **"demand is there, go ahead with the product, but do not publish the
> recycled-polyester claim until you fund proper evidence."** It still spent **€30** on market data,
> which was affordable.
>
> The lesson: the system **never fakes confidence it didn't pay for.** Skip the evidence, and it tells
> you the claim is at risk.

**One-line thread:** *"In every case we turn a vague business question into a checklist of variables,
find a real dataset for each, get the cheap signals free, and pay only when free data can't make the
claim defensible — with a human always in the loop on the money."*

### If asked: "how do you know it's 92% if you didn't buy the data?"

> "The numbers are **representative** — we encode each source's known rigor rather than parsing the
> licensed file in the demo. ecoinvent is a peer-reviewed, jurisdiction-specific LCA, so it scores high
> and low-risk; the free literature-average proxy scores low and high-risk. What's **real** is the
> decision logic and the payment: a peer-reviewed LCA is what makes the claim defensible under the EU
> Green Claims rules, and that's the gap we pay to close. Swap the encoded score for one parsed from the
> downloaded dataset and the same code computes it for real."

---

## Live run (the proof) — streamed step by step in the canvas

This is the Lupo-style step-by-step reveal, but the steps are a **real run** with **real charges**.

**On the canvas:** pick the scenario in the **▶ Run live** row, keep **real Stripe charges** ticked,
and click **▶ Run**. A "Running…" panel appears and each agent step streams in live — breakdown →
shopping → the €40 payment → the human gate → the answer — while the sections below fill in.

> Alternative one-click: open `http://localhost:8000/frontend/canvas.html?run=knitwear&live=1`.
> CLI equivalent (no canvas streaming): `LEDGERSCOUT_STRIPE_LIVE=1 python3 scripts/run_research.py`.

**Stripe dashboard:** refresh `https://dashboard.stripe.com/test/payments` → two new **succeeded**
PaymentIntents (€40 ecoinvent, €30 Statista) whose `pi_…` ids **match the ids in the canvas's Governed
catalog**.

> Talk track during the run: *"These steps are happening right now — and as the payment step lands, a
> real PaymentIntent is created. Same ids appear in the Stripe dashboard. Test mode, so no real money,
> but the payment rail is genuinely live. Swap the test key and a real provider checkout, and the
> agents are buying data for real."*

---

## Safety net

- **Live run hiccups (network / Stripe down):** click the pre-baked **③ Recycled activewear** tab and
  narrate the "human declines → honest claim-at-risk" beat — same story, zero network.
- **Canvas can't load logs:** you served from the wrong folder. Serve from the **project root** and
  open `/frontend/canvas.html` (the canvas reads `../data/`).
- **`verify_stripe` refuses to run:** your key is `sk_live_…`. Use `sk_test_…` for the demo.
