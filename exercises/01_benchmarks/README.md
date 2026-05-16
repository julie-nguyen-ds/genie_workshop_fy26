# Exercise 1 — Benchmarks: Run, Score, Grow

**Time:** ~15 minutes
**Goal:** Run the pre-loaded 6-question benchmark to establish a baseline, then **add a new benchmark question yourself** — including verifying the expected SQL is actually correct.

> Heads up: we are **not tuning anything** in this exercise. Some questions will fail — that's expected. The whole point of running a benchmark first is to **establish a baseline** before any tuning. Each later exercise will improve a different class of failure, and you can re-run the benchmark at the end of the workshop to see the score climb.

## Why this matters

Vibes-driven Genie tuning ("ask, tweak, ask again") doesn't scale past a few questions. **Benchmarks** let you measure every change. Each space supports up to 500 benchmark questions; each runs as an independent conversation and is scored against your expected SQL.

Two important properties:
- Benchmarks **evaluate**, they do not **inform**. Genie doesn't learn from them — they're a test set, not training data.
- The expected SQL is the **gold standard**. If it's wrong, you've codified a bug into your regression suite. Human verification of the SQL is non-negotiable (we'll do it in Part B).

## Prerequisites
- The base Genie space from setup (6 benchmark questions pre-loaded by `setup/01_create_base_space.py`).

> Note on the loader: Databricks Genie doesn't yet support a CSV import of benchmarks in the UI. The setup notebook attempts to load the 6 questions programmatically; if your workspace's API doesn't accept benchmark writes, setup prints the questions and the facilitator pastes them in via **Benchmark tab → Add question** before the session. The source-of-truth list lives in `benchmark_questions.csv`.

---

## Part A — Run the pre-loaded benchmark (~5 min)

1. Open the workshop Genie space → **Benchmark** tab (left nav).
2. Confirm you see **6 questions**. If not, see the loader note above.
3. Click **Run benchmark**.
4. Watch results stream in.

Don't worry about the score — whatever it is, it's the baseline. Take 30 seconds to look at each failure (click into it) and compare *generated SQL* vs *expected SQL*. The diff tells you what kind of fix would help.

We'll fix these failures across the next 4 exercises:

| Failure pattern | The lever that fixes it | Where you'll learn it |
|---|---|---|
| Genie writes `WHERE status = 'Paid'` (uppercase) against lowercase data → returns 0 → expected count mismatch | **Entity matching / Format assistance** (space settings) | **Exercise 2** |
| `text_instructions` blob is bloated; Genie can't pick the right rule | **Refactor instructions** | **Exercise 3** |
| Business term like "in-force" isn't defined — Genie ignores the date window | **Atomic text instructions + KPI glossary** | **Exercise 4** |
| Wrong join path or wrong query shape (e.g. claims → agents via a non-existent `agent_id`) | **SQL trusted asset** (example SQL or UC function) | **Exercise 5** |

The benchmark is your **regression suite** — at the end of the workshop, re-run it and most/all of the 6 should pass.

---

## Part B — Add your own benchmark question (~8 min)

This is the part that mirrors what you'll do in your own production spaces: **a benchmark is only as useful as the questions in it, and the expected SQL has to be human-verified.** Never trust auto-generated SQL as your gold standard without checking.

### Step 1. Pick a question (~1 min)

Use this one (good single-table aggregation, easy to verify):
> *What's our average paid claim amount for property fire losses in 2025?*

Or pick your own that:
- Targets your dataset
- Has a clear, unambiguous answer
- Doesn't already exist in the 6 pre-loaded benchmarks

### Step 2. Ask the question in chat first (~1 min)

In a **fresh chat thread** in the Genie space, paste your question. Wait for Genie to answer.

Expand the answer card → **Show generated SQL**. Copy that SQL to your clipboard. **Do not assume it's correct yet.**

### Step 3. Verify the SQL is actually correct (~4 min)

This is the critical step.

1. Open a new SQL editor tab (or use the Databricks SQL Editor).
2. Paste Genie's generated SQL exactly as-is.
3. Run it. Look at the result.

Now ask yourself:
- **Is the filter right?** For "2025", did Genie use `YEAR(loss_date)` or `YEAR(settle_date)` or `YEAR(report_date)`? For paid claims, did it filter on `status = 'paid'`?
- **Is the case right?** Did Genie write `'paid'` or `'Paid'`? Compare against `SELECT DISTINCT status FROM workspace.insurance_data.claims`.
- **Is the join right?** If multiple tables are joined, is it joining on the right keys? Are all joined tables actually needed?
- **Is the aggregation right?** For *"average"*, is it `AVG(claim_amount_thb)` over the right scope?
- **Is the population right?** Does the SQL filter to `product_subtype = 'property_fire'` (the actual value) or something else?
- **Sanity-check the number.** Roughly how many property fire claims do we have in 2025? Does an average of "5,000,000 THB" make sense, or is the number suspiciously big/small?

Cross-check with a second query if you're unsure. If Genie's SQL is **wrong**, rewrite it — that's your expected SQL. If it's **right**, use it as-is.

### Step 4. Add the question to the benchmark (~1 min)

1. Go back to the **Benchmark** tab.
2. **Add question**.
3. Paste:
   - **Question**: your natural-language prompt
   - **Expected SQL**: the verified SQL from Step 3
4. Save.

### Step 5. Re-run the benchmark (~1 min)

You should now see **7 questions** in the benchmark. Click **Run benchmark**. Your new question will pass if Genie regenerates the same SQL you just verified — and may fail if Genie's runtime SQL differs from your stored expected SQL (e.g. case mismatch, alias difference). Either outcome is a teaching moment.

---

## Discussion (~2 min)

- **Why is human verification non-negotiable?** Genie generates SQL that's often *plausible* and *runs successfully* but is wrong (filter on wrong date column, wrong join path, wrong currency framing). Without human review your benchmark codifies the same bugs the LLM produces — you'd be grading the test taker against their own answer key.
- **Growing a benchmark over time.** Treat the benchmark like a regression suite: every time a user reports a wrong answer, add the question (with the right SQL) as a benchmark, then later add the appropriate trusted asset / instruction (next exercises). Now that failure mode is locked in.
- **When NOT to add a question to the benchmark.** Questions whose "correct" answer depends on judgement (e.g. *"who's our best agent?"*) — those need a clarification instruction, not a benchmark entry.

---

## Done when
- [ ] Pre-loaded benchmark ran; you noted the baseline pass count and what kinds of failures appeared.
- [ ] You've added at least one new benchmark question yourself, with verified expected SQL.
- [ ] You can explain why human SQL verification is non-negotiable.

## If you finish early
- Try a question that you suspect will fail because of a case-mismatch issue (e.g. *"how many policies are motor product line?"*) and predict the failure pattern. We'll fix it for real in Exercise 2.
- Add 2 more benchmarks covering edge cases — last-30-days windows, fraud filter on `fraud_flag = true`, percentage calculations.

See `tuning_walkthrough.md` for the facilitator's reference on what each of the 6 pre-loaded questions targets and which later exercise fixes it.
