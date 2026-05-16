# Exercise 1 — Benchmark Walkthrough (facilitator reference)

This is the deep-dive cheat sheet for the live walk-through portion of Exercise 1.

**Reminder:** Ex 1 does not tune anything. The point is to **see the baseline** and look at each failure long enough to understand what kind of fix it needs — then come back to it in the appropriate later exercise.

## The 5 starter benchmark questions and where each one gets fixed

| # | Question | Why it might fail | Where we fix it |
|---|---|---|---|
| 1 | How many policies are currently active? | Genie may write `status = 'Active'` (uppercase) → 0 rows | **Ex 2** Entity matching |
| 2 | How many claims paid in 2025? | Genie may write `status = 'Paid'` (uppercase) → 0 rows | **Ex 2** Entity matching |
| 3 | Total claim amount by loss type, motor only, 2025 | Similar — `product_line = 'Motor'` case mismatch; sometimes wrong date column | **Ex 2** Entity matching |
| 4 | **Which branch has the most active in-force policies right now?** | Genie reads "active" as `status = 'active'` only — ignores the date window. "In-force" is insurance jargon Genie doesn't know. | **Ex 4** — when attendees refactor the oversized instruction blob, the "in-force" atomic text instruction gets extracted (the bloated blob already contains the definition) |
| 5 | **Top 10 agents by claim count + branch** | `claims` table has no `agent_id` — the join must traverse `claims → policies → agents`. Genie often errors or invents a wrong path. | **Ex 3** — parameterised example SQL pinning the canonical 4-way join |

3 easy/moderate to set the baseline (#1-3) + 2 engineered failures previewing different fixes (#4-5).

**Attendees add a 6th question themselves in Part B** — and that 6th is mandated, not free choice: *"Show me total paid claims by loss type for 2025"*. This is the natural-language counterpart for the UC SQL function (`claims_by_loss_type`) attendees will build in Ex 3. Adding it here closes the loop: Ex 3's function pins the SQL, the benchmark then passes consistently on re-run.

## What each later exercise fixes (live re-run guidance)

After each later exercise, you *could* re-run the benchmark to demonstrate the score improving. We don't budget for this inside the exercises (it adds 2-3 min each), but the very end of the workshop is a great moment to re-run all 6 and show the difference vs the baseline.

- After **Ex 2** (Entity matching ON): #1, #2, #3 should pass — case mismatch fixed.
- After **Ex 3** (trusted assets added): #5 should pass, and the **user-added 6th question** ("total paid claims by loss type for 2025") should also pass since the new UC function pins its SQL.
- After **Ex 4** (instruction refactor — atomic in-force instruction extracted from the bloated blob): #4 should pass.

If a question still fails after the "right" exercise, it's a coaching moment: dig into the generated SQL and figure out the residual gap.

## Coaching the "add the 6th benchmark" step (Part B)

The question is mandated: *"Show me total paid claims by loss type for 2025."*

**What Genie will likely generate (Entity matching is OFF in Ex 1):**

Common variants you'll see:
```sql
-- Variant A — wrong date column, wrong status case
SELECT loss_type, SUM(claim_amount_thb) AS total
FROM workspace.insurance_data.claims
WHERE status = 'Paid' AND YEAR(settle_date) = 2025
GROUP BY loss_type;
```
```sql
-- Variant B — no status filter at all
SELECT loss_type, SUM(claim_amount_thb)
FROM workspace.insurance_data.claims
WHERE YEAR(loss_date) = 2025
GROUP BY loss_type;
```
```sql
-- Variant C — right idea, drifting column names
SELECT loss_type, COUNT(*) AS num_claims, SUM(claim_amount_thb) AS sum_amount
FROM workspace.insurance_data.claims
WHERE status = 'paid' AND loss_date BETWEEN '2025-01-01' AND '2025-12-31'
GROUP BY loss_type;
```

The "verified expected SQL" we want attendees to land on is in [`ground_truth.sql`](ground_truth.sql), with the five typical Genie-vs-ground-truth differences listed inline in the SQL comment header. Open that file alongside Genie's generated SQL when coaching attendees through the diff.

Quick reference for the diff:
1. Genie filters on `settle_date`; ground truth filters on `loss_date`.
2. Genie omits the `status = 'paid'` filter; ground truth includes it.
3. Genie typically returns only `total_paid_claims_thb`; ground truth returns both `claim_count` and `total_paid_thb`.
4. Genie uses a plain `SUM`; ground truth wraps with `COALESCE(SUM(CASE WHEN status = 'paid' THEN claim_amount_thb END), 0)`.
5. Genie orders by the total amount; ground truth orders by `claim_count DESC`.

**Coaching prompts to walk attendees through:**

1. **Date column** — `loss_date` is the insurance convention for "claims in 2025" (date of loss occurrence). `settle_date` would answer "claims paid in 2025" — different semantics, different result.
2. **"Paid" filter** — the prompt says *total **paid** claims*. Did Genie include `status = 'paid'`? If not, the SUM includes denied/pending/open claims and is wrong.
3. **Case sensitivity** — is the literal `'paid'` (matching the data) or `'Paid'`? Run `SELECT DISTINCT status FROM workspace.insurance_data.claims` to confirm. Entity matching isn't on yet in Ex 1, so Genie WILL likely get this wrong.
4. **Grouping** — `GROUP BY loss_type`, one row per loss_type.
5. **Currency framing** — output column called `total_paid_thb` makes the unit explicit.
6. **Sanity check the number** — eyeball each loss_type total. For our 5K-claim dataset, plausible annual paid totals per loss_type are in the millions to tens-of-millions of THB. If anything is "23 THB" or "10^12 THB", something is broken.

**Common attendee mistakes to catch:**
- Pasting Genie's SQL into the benchmark without running it themselves.
- Skipping the sanity check on the loss_type totals.
- Confusing `settle_date` and `loss_date`.
- Counting unpaid claims in the "total paid" sum.

**The point of this question being mandated:** it's the natural-language counterpart for the `claims_by_loss_type` SQL function attendees will build in Ex 3. By the end of the workshop, when the function is attached, Genie should call it and produce exactly this SQL deterministically — the benchmark pass becomes proof that Ex 3's work landed.

## Common attendee questions

- **"My expected SQL returns different column order — does that fail?"** Yes, the scorer compares result sets including column names. Use consistent aliasing in expected SQL.
- **"Can I run a subset of the benchmark?"** Yes — re-running individual questions is the normal tuning loop.
- **"How do I know which lever to reach for?"** Each later exercise covers one: Ex 2 settings → case/format; Ex 3 → query shape (trusted assets); Ex 4 → instruction hygiene + business term definitions.
