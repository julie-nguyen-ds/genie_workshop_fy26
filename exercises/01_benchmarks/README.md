# Exercise 1 — Benchmarks: Run, Score, Grow

**Time:** ~15 minutes
**Goal:** Run the pre-loaded **5-question** benchmark to establish a baseline, then **add a 6th benchmark question yourself** — generating the SQL with Genie, verifying it, then saving it. The 6th question is intentionally one that Exercise 5 will fix (closing the loop on the workshop's regression test).

> Heads up: we are **not tuning anything** in this exercise. Some questions will fail — that's expected. The whole point of running a benchmark first is to **establish a baseline** before any tuning. Each later exercise will improve a different class of failure, and you can re-run the benchmark at the end of the workshop to see the score climb.

## Why this matters

Vibes-driven Genie tuning ("ask, tweak, ask again") doesn't scale past a few questions. **Benchmarks** let you measure every change. Each space supports up to 500 benchmark questions; each runs as an independent conversation and is scored against your expected SQL.

Two important properties:
- Benchmarks **evaluate**, they do not **inform**. Genie doesn't learn from them — they're a test set, not training data.
- The expected SQL is the **gold standard**. If it's wrong, you've codified a bug into your regression suite. Human verification of the SQL is non-negotiable (we'll do it in Part B).

## Prerequisites
- The base Genie space from setup (5 benchmark questions pre-loaded by `setup/01_create_base_space.py`).

> Note on the loader: Databricks Genie doesn't yet have a CSV import for benchmarks in the UI. The setup notebook bakes the 5 questions directly into the space's `serialized_space.benchmarks.questions` block at creation time — so they're already there when you open the Benchmark tab. The source-of-truth list lives in `benchmark_questions.csv`; if you need to re-seed, re-run `setup/01_create_base_space.py` and it creates a fresh space with benchmarks pre-loaded.

---

## Part A — Run the pre-loaded benchmark (~5 min)

1. Open the workshop Genie space → **Benchmark** tab (left nav).
2. Confirm you see **5 questions**. If not, see the loader note above.
3. Click **Run benchmark**.
4. Watch results stream in.

Don't worry about the score — whatever it is, it's the baseline. Take 30 seconds to look at each failure (click into it) and compare *generated SQL* vs *expected SQL*. The diff tells you what kind of fix would help.

We'll fix these failures across the next 4 exercises:

| Failure pattern | The lever that fixes it | Where you'll learn it |
|---|---|---|
| Genie writes `WHERE status = 'Paid'` (uppercase) against lowercase data → returns 0 → expected count mismatch | **Entity matching / Format assistance** (space settings) | **Exercise 2** |
| `text_instructions` blob is bloated; Genie can't pick the right rule | **Refactor instructions** | **Exercise 3** |
| Business term like "in-force" isn't defined — Genie ignores the date window | **Atomic text instructions + KPI glossary** | **Exercise 4** |
| Wrong join path or wrong query shape (e.g. claims → agents via a non-existent `agent_id`); inconsistent answer to "claims by loss type" | **SQL trusted asset** (example SQL or UC function) | **Exercise 5** |

The benchmark is your **regression suite** — at the end of the workshop, re-run it and most/all of the 5 pre-loaded questions plus the 6th you'll add in Part B should pass.

---

## Part B — Add the 6th benchmark question yourself (~8 min)

This is the part that mirrors what you'll do in your own production spaces: **a benchmark is only as useful as the questions in it, and the expected SQL has to be human-verified.** Never trust auto-generated SQL as your gold standard without checking.

### The question you'll add

> *Show me total paid claims by loss type for 2025.*

We chose this one on purpose: it's the natural-language counterpart for the SQL function you'll build in Exercise 5 (`claims_by_loss_type`). Right now Genie has no trusted asset for it, so it'll likely get the SQL subtly wrong. Once Ex 5 attaches the function, re-running this benchmark should pass — that's the regression-test loop closing.

### Step 1. Ask Genie to generate the SQL (~1 min)

In a **fresh chat thread** in the Genie space, paste the question above. Wait for Genie to answer.

Expand the answer card → **Show generated SQL**. Copy that SQL to your clipboard. **Do not assume it's correct yet.**

### Step 2. Verify the SQL is actually correct (~5 min)

This is the critical step. Open a SQL editor tab (or the Databricks SQL Editor), paste Genie's SQL, run it, and look at the result.

The **ground truth** for this question lives in [`ground_truth.sql`](ground_truth.sql) — open it side-by-side with Genie's output. Diff the two and walk through the five things Genie typically gets wrong on this question:

1. **Date column** — Genie usually filters on `settle_date`. The ground truth filters on `loss_date` (claims that *occurred* in 2025, not ones *settled* in 2025).
2. **Paid filter** — Genie doesn't filter for paid claims. The ground truth filters `status = 'paid'`, so unpaid/denied/pending claims don't inflate the total.
3. **Missing `claim_count`** — Genie typically only returns `total_paid_claims_thb`. The ground truth returns both `claim_count` and `total_paid_thb` per loss type.
4. **No `COALESCE` + `CASE`** — Genie aggregates with a plain `SUM`. The ground truth wraps the paid-only sum in `CASE WHEN status = 'paid' THEN claim_amount_thb END` and `COALESCE(..., 0)` so loss types with zero paid claims still show a row with `0` instead of `NULL`.
5. **Order** — Genie orders by `total_paid_claims_thb DESC`. The ground truth orders by `claim_count DESC` (most-frequent loss types first, regardless of THB magnitude).

Also sanity-check the casing (`'paid'` lowercase vs `'Paid'`) and eyeball the per-loss_type numbers — if "fire" comes out to 23 THB or 10^12 THB, something is broken.

If Genie's SQL differs from the ground truth, **use the ground truth** as your expected SQL. **You ran it and verified the number yourself** before promoting it to the benchmark.

### Step 3. Add the question to the benchmark (~1 min)

1. Go back to the **Benchmark** tab.
2. **Add question**.
3. Paste:
   - **Question**: *Show me total paid claims by loss type for 2025.*
   - **Expected SQL**: the verified SQL from Step 2
4. Save.

### Step 4. Re-run the benchmark (~1 min)

You should now see **6 questions** in the benchmark. Click **Run benchmark**. Your new question may pass or fail depending on whether Genie regenerates the same SQL you stored — and that's exactly the gap that Exercise 5 will close by pinning the SQL via a UC function.

---

## Discussion (~2 min)

- **Why is human verification non-negotiable?** Genie generates SQL that's often *plausible* and *runs successfully* but is wrong (filter on wrong date column, wrong join path, wrong currency framing). Without human review your benchmark codifies the same bugs the LLM produces — you'd be grading the test taker against their own answer key.
- **Growing a benchmark over time.** Treat the benchmark like a regression suite: every time a user reports a wrong answer, add the question (with the right SQL) as a benchmark, then later add the appropriate trusted asset / instruction (next exercises). Now that failure mode is locked in.
- **When NOT to add a question to the benchmark.** Questions whose "correct" answer depends on judgement (e.g. *"who's our best agent?"*) — those need a clarification instruction, not a benchmark entry.

---

## Done when
- [ ] Pre-loaded 5-question benchmark ran; you noted the baseline pass count and what kinds of failures appeared.
- [ ] You added the *"Show me total paid claims by loss type for 2025"* question to the benchmark, with verified expected SQL.
- [ ] You can explain why human SQL verification is non-negotiable.

## If you finish early
- Try a question that you suspect will fail because of a case-mismatch issue (e.g. *"how many policies are motor product line?"*) and predict the failure pattern. We'll fix it for real in Exercise 2.
- Add another benchmark covering an edge case — last-30-days windows, fraud filter on `fraud_flag = true`, percentage calculations.

See `tuning_walkthrough.md` for the facilitator's reference on what each of the 5 pre-loaded questions targets and which later exercise fixes it.
