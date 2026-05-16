# Exercise 2 — Benchmarks: Run, Score, Tune, Grow

**Time:** 25 minutes
**Goal:** Run the pre-loaded 5-question benchmark, tune the engineered failures with the three levers (text instruction / example SQL / join spec), then **add a brand-new benchmark question yourself** — including verifying the expected SQL is actually correct.

## Why this matters
Vibes-driven Genie tuning is how most people start: ask a question, see it fail, tweak something, ask again. That doesn't scale. **Benchmarks** are how you measure progress. Each space supports up to 500 benchmark questions; each runs as an independent conversation, scored against your expected SQL.

Critically: benchmarks **evaluate**, they do not **inform**. Genie won't learn from benchmark questions — they're a test set, not training data.

## Prerequisites
- The base Genie space from the setup (5 benchmark questions pre-loaded by `setup/01_create_base_space.py`).
- Entity matching + Format assistance **ON** (you turned these on in Exercise 1).

> Note on the loader: Databricks Genie does not yet support a CSV import of benchmarks in the UI. The setup notebook attempts to load the 5 questions programmatically; if your workspace's API doesn't accept benchmark writes, setup prints the questions and you (the facilitator) paste them in via **Benchmark tab → Add question** before the session. The source-of-truth list lives in `benchmark_questions.csv`.

---

## Part A — Run the pre-loaded benchmark (~5 min)

1. Open the workshop Genie space → **Benchmark** tab (left nav).
2. Confirm you see **5 questions**. If not, see the loader note above.
3. Click **Run benchmark**.
4. Watch results stream in. Expect **3 of 5 to pass** — two are engineered to fail.

While it runs, talk through the three tuning levers:

| Lever | When to use |
|---|---|
| **Text instruction** | Genie doesn't know a *business term* or rule (e.g. "in-force = active and within effective/expiry"). |
| **Example SQL** | Genie consistently picks the wrong query shape (wrong joins, wrong aggregation pattern). |
| **Join spec** | Two tables can be joined multiple ways and Genie picks the wrong one. |

---

## Part B — Tune the two engineered failures (~8 min)

### Failure #1: "Which branch has the most active in-force policies right now?"

**What Genie gets wrong:** Without context, Genie treats "in-force" as `status = 'active'` only — it ignores the date window. Branches that have lots of `active` policies with already-expired `expiry_date` win incorrectly.

**Fix it with a text instruction:**
1. Right rail → **General instructions** → **Add**.
2. Paste:
   ```
   "In-force" policies are policies where status = 'active'
   AND effective_date <= current_date()
   AND expiry_date >= current_date(). Always apply all three
   conditions when the user asks about in-force, active right now,
   or currently in force.
   ```
3. Re-run this benchmark question. Pass.

### Failure #2: "Top 10 agents by total claims filed by their policies, including the agent's branch"

**What Genie gets wrong:** The `claims` table has no `agent_id` — the join must traverse `claims → policies → agents`. Genie often tries `claims.agent_id` (errors) or invents a wrong path.

**Fix it with an example SQL:**
1. Right rail → **Example SQL** → **Add**.
2. Paste the canonical join:
   ```sql
   -- Top N agents by claim count, with their branch
   SELECT a.agent_name, b.branch_name, COUNT(cl.claim_id) AS claim_count
   FROM workspace.insurance_data.agents a
   JOIN workspace.insurance_data.policies p ON p.agent_id = a.agent_id
   JOIN workspace.insurance_data.claims cl  ON cl.policy_id = p.policy_id
   JOIN workspace.insurance_data.branches b ON b.branch_id = a.branch_id
   GROUP BY a.agent_name, b.branch_name
   ORDER BY claim_count DESC
   LIMIT 10;
   ```
3. Re-run. Pass.

---

## Part C — Add your own benchmark question (~10 min)

This is the part that mirrors what you'll do in your own production spaces: **a benchmark is only as useful as the questions in it, and the expected SQL has to be human-verified.** Never trust auto-generated SQL as your gold standard without checking.

### Step 1. Pick a question (~1 min)

Use this one (good single-table aggregation, easy to verify):
> *What's our average paid claim amount for property fire losses in 2025?*

Or pick your own that:
- Targets your dataset
- Has a clear, unambiguous answer
- Doesn't already exist in the 5 pre-loaded benchmarks

### Step 2. Ask the question in chat first (~2 min)

In a **fresh chat thread** in the Genie space, paste your question. Wait for Genie to answer.

Expand the answer card → **Show generated SQL**. Copy that SQL to your clipboard. **Do not assume it's correct yet.**

### Step 3. Verify the SQL is actually correct (~4 min)

This is the critical step.

1. Open a new SQL editor tab (or use the Databricks SQL Editor).
2. Paste Genie's generated SQL exactly as-is.
3. Run it. Look at the result.

Now ask yourself:
- **Is the filter right?** For "2025", did Genie use `YEAR(loss_date)` or `YEAR(settle_date)` or `YEAR(report_date)`? For paid claims, did it filter on `status = 'paid'`?
- **Is the join right?** If multiple tables are joined, is it joining on the right keys? Are all joined tables actually needed?
- **Is the aggregation right?** For *"average"*, is it `AVG(claim_amount_thb)` over the right scope?
- **Is the population right?** Does the SQL filter to `product_subtype = 'property_fire'` (the actual value) or something else?
- **Sanity-check the number.** Roughly how many property fire claims do we have in 2026? Does an average of "5,000,000 THB" make sense, or is the number suspiciously big/small?

Cross-check with a second query if you're unsure — for example, write your own version and compare row count or aggregate to Genie's. If they disagree, dig in.

If Genie's SQL is **wrong**, rewrite it. Save the corrected version — that's your expected SQL.
If Genie's SQL is **right**, use it as-is.

### Step 4. Add the question to the benchmark (~2 min)

1. Go back to the **Benchmark** tab.
2. **Add question**.
3. Paste:
   - **Question**: your natural-language prompt
   - **Expected SQL**: the verified SQL from Step 3
4. Save.

### Step 5. Re-run the benchmark (~1 min)

You should now see **6 questions** in the benchmark. Click **Run benchmark**. Your new question should pass (since Genie just generated this exact SQL minutes ago — at most it'll fail on a column-order or alias mismatch, which is a teaching moment about why scoring is strict).

---

## Part D — Discuss (~2 min)

- **Why is human verification non-negotiable?** Genie generates SQL that's often *plausible* and *runs successfully* but is wrong (filter on wrong date column, wrong join path, wrong currency framing). Without human review your benchmark codifies the same bugs the LLM produces — you'd be grading the test taker against their own answer key.
- **Growing a benchmark over time.** Treat the benchmark like a regression suite: every time a user reports a wrong answer, add the question (with the right SQL) as a benchmark, then add the appropriate trusted asset / instruction. Now that failure mode is locked in.
- **When NOT to add a question to the benchmark.** Questions whose "correct" answer depends on judgement (e.g. *"who's our best agent?"*) — those need a clarification instruction, not a benchmark entry.

---

## Done when
- [ ] Pre-loaded benchmark ran; 3 of 5 passed first time.
- [ ] Two engineered failures now pass after adding the text instruction and example SQL.
- [ ] You've added at least one new benchmark question yourself, with verified expected SQL.
- [ ] You can explain when to use each of the three tuning levers and why human SQL verification is non-negotiable.

## If you finish early
Add two more benchmarks covering edge cases — last-30-days windows, fraud filter on `fraud_flag = true`, percentage calculations — and run, fix any failures.

See `tuning_walkthrough.md` for the full step-by-step.
