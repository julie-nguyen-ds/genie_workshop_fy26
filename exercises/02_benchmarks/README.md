# Exercise 2 — Benchmarks: Run, Score, Tune

**Time:** 25 minutes
**Goal:** Load a 10-question benchmark, run it, watch some questions fail, and tune Genie with the three levers — *text instruction*, *example SQL*, *join hint*.

## Why this matters
Vibes-driven Genie tuning is how most people start: ask a question, see it fail, tweak something, ask again. That doesn't scale. **Benchmarks** are how you measure progress. Each space supports up to 500 benchmark questions; each runs as an independent conversation, scored against your expected SQL.

Critically: benchmarks **evaluate**, they do not **inform**. Genie won't learn from benchmark questions — they're a test set, not training data.

## Prerequisites
- The base Genie space from Exercise 1 (with the trusted assets you added — they help).
- `benchmark_questions.csv` from this folder.

---

## Part A — Load and run (~5 min)

1. Open the space → **Benchmark** tab (left nav).
2. **Import questions** → upload `benchmark_questions.csv`. Maps `question` → question, `expected_sql` → SQL answer.
3. Click **Run benchmark**.
4. Watch results stream in. Expect ~6–8 of 10 to pass.

While it runs, talk through the three tuning levers:

| Lever | When to use |
|---|---|
| **Text instruction** | Genie doesn't know a *business term* or rule (e.g. "in-force = active and within effective/expiry"). |
| **Example SQL** | Genie consistently picks the wrong query shape (wrong joins, wrong aggregation pattern). |
| **Join spec** | Two tables can be joined multiple ways and Genie picks the wrong one. |

---

## Part B — Tune the failures (~15 min)

Two questions are *engineered* to fail. We'll fix them.

### Failure #1: "Which branch has the most active in-force policies right now?"

**What Genie gets wrong:** Without context, Genie interprets "active" as `status = 'active'` and ignores the date window. It returns the branch with the most rows where `status = 'active'`, even if most of those have already expired.

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
3. Re-run the benchmark question. Pass.

### Failure #2: "Top 10 agents by total claims filed by their policies, including the agent's branch"

**What Genie gets wrong:** Genie doesn't realize `claims` has no `agent_id` — the join must traverse `claims → policies → agents`. It may try `claims.agent_id` (doesn't exist) and fail, or it may invent a join.

**Fix it with an example SQL:**
1. Right rail → **Example SQL** → **Add**.
2. Paste the canonical join:
   ```sql
   -- Top N agents by claim count, with their branch
   SELECT a.agent_name, b.branch_name, COUNT(cl.claim_id) AS claim_count
   FROM main.insurance_data.agents a
   JOIN main.insurance_data.policies p ON p.agent_id = a.agent_id
   JOIN main.insurance_data.claims cl  ON cl.policy_id = p.policy_id
   JOIN main.insurance_data.branches b ON b.branch_id = a.branch_id
   GROUP BY a.agent_name, b.branch_name
   ORDER BY claim_count DESC
   LIMIT 10;
   ```
3. Re-run. Pass.

### (Optional, time permitting) Failure #3 — try the third lever

If the property-fire question fails, fix it with a **join spec** (right rail → Join relationships) by declaring `claims.policy_id → policies.policy_id` explicitly. This is the lever to reach for when you have ambiguous joins across many tables.

---

## Part C — Discuss (~5 min)

Look at the benchmark dashboard:
- Pass rate before and after tuning.
- Which questions are still marked "for review"? (Ones where you didn't provide expected SQL.)
- How would you build out the full benchmark for a production space? (≥ 20 questions, covering top user questions, refreshed when schema changes.)

## Done when
- [ ] Imported all 10 questions.
- [ ] Two engineered failures now pass after adding the text instruction and example SQL.
- [ ] You can explain when to use each of the three tuning levers.

## If you finish early
Add three more benchmark questions covering edge cases your customer asks (e.g. last-30-days windows, currency conversions). Run, fix any failures.

See `tuning_walkthrough.md` for the full step-by-step with screenshots placeholders.
