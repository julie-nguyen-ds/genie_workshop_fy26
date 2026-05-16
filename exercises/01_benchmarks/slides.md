# Exercise 1 — Benchmarks (slides)

---

## Slide 1 — Title
**Exercise 1: Benchmarks — Run, Score, Grow**
*~15 minutes — set the baseline before any tuning*

---

## Slide 2 — Why start here
- Vibes tuning ("ask, tweak, ask again") doesn't scale past a few questions.
- Benchmarks **measure** every change you make.
- Up to **500 questions per space**, scored against your expected SQL.
- Critical: benchmarks **evaluate**, they do not **inform**. They're test data, not training data.

---

## Slide 3 — What you'll do
1. Run the **5 pre-loaded benchmark questions** to set a baseline.
2. **Look at the failures** — they preview every tuning lever we'll touch.
3. **Add a specific 6th question yourself** end-to-end: ask Genie, verify the SQL, save it. We'll close the loop on this one in Ex 3.

We do **not tune anything** in this exercise. Each next exercise targets a different class of failure you'll see.

---

## Slide 4 — Failure ↔ Exercise mapping
| Failure | Fixed in |
|---|---|
| `WHERE status = 'Paid'` (uppercase mismatch) → 0 rows | **Ex 2 — Entity matching** |
| Wrong join path (e.g. `claims.agent_id` doesn't exist); inconsistent answer to "claims by loss type" | **Ex 3 — Trusted assets** |
| Bloated `text_instructions` blob → wrong rules win; business term ("in-force") not defined | **Ex 4 — Fix oversized instructions** |

The benchmark = your regression suite. Re-run at end of workshop to see the score climb.

---

## Slide 5 — Add the 6th benchmark question
Ask Genie *"Show me total paid claims by loss type for 2025"* in a fresh chat thread. Then:
1. Expand → **Show generated SQL**, copy it.
2. Run that SQL in a SQL editor. **Verify** the date column (`loss_date`, not `settle_date`), the `status = 'paid'` filter, the case, the grouping, and **sanity-check** each loss_type's total.
3. Fix anything wrong; that corrected SQL is your expected SQL.
4. Add the verified Q+SQL pair via **Benchmark tab → Add question**.
5. Re-run — this question is the one Ex 3's Example SQL will pin later (both a hardcoded-2025 version and a parametrized `:start_date / :end_date` version), closing the loop.

**Never accept Genie's SQL as the expected SQL without checking it yourself** — you'd be grading the test taker against their own answer key.

---

## Slide 6 — Production rule of thumb
- ≥ 20 benchmark questions covering your top user prompts.
- Re-run on every change to instructions / tables / SQL functions.
- Refresh the benchmark when the schema evolves.
- Treat the benchmark as a regression suite: every user-reported wrong answer → add as a benchmark, then add the fix.
- A benchmark score isn't a SLO — it's a *trend you're trying to move*.
