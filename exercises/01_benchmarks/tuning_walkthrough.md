# Exercise 1 — Benchmark Walkthrough (facilitator reference)

This is the deep-dive cheat sheet for the live walk-through portion of Exercise 1.

**Reminder:** Ex 1 does not tune anything. The point is to **see the baseline** and look at each failure long enough to understand what kind of fix it needs — then come back to it in the appropriate later exercise.

## The 6 starter benchmark questions and where each one gets fixed

| # | Question | Why it might fail | Where we fix it |
|---|---|---|---|
| 1 | How many policies are currently active? | Genie may write `status = 'Active'` (uppercase) → 0 rows | **Ex 2** Entity matching |
| 2 | How many claims paid in 2025? | Genie may write `status = 'Paid'` (uppercase) → 0 rows | **Ex 2** Entity matching |
| 3 | Total claim amount by loss type, motor only, 2025 | Similar — `product_line = 'Motor'` case mismatch; sometimes wrong date column | **Ex 2** Entity matching (and good sample values discipline in Ex 4) |
| 4 | **Which branch has the most active in-force policies right now?** | Genie reads "active" as `status = 'active'` only — ignores the date window. "In-force" is insurance jargon Genie doesn't know. | **Ex 4** — atomic text instruction defining `in-force = status='active' AND effective_date <= current_date() AND expiry_date >= current_date()` |
| 5 | **Top 10 agents by claim count + branch** | `claims` table has no `agent_id` — the join must traverse `claims → policies → agents`. Genie often errors or invents a wrong path. | **Ex 5** — parameterised example SQL pinning the canonical 4-way join |
| 6 | **Show me total paid claims by loss type for 2025** | Without a trusted asset, Genie picks `report_date`/`settle_date`, omits the `status='paid'` filter, or renames columns each run | **Ex 5** — UC SQL function `claims_by_loss_type(start_date, end_date)` returns `loss_type`, `claim_count`, `total_paid_thb` deterministically |

3 easy/moderate to set the baseline (#1-3), 3 engineered failures previewing different fixes (#4-6). Attendees add a 7th of their own in Part B.

## What each later exercise fixes (live re-run guidance)

After each later exercise, you *could* re-run the benchmark to demonstrate the score improving. We don't budget for this inside the exercises (it adds 2-3 min each), but the very end of the workshop is a great moment to re-run all 6 and show the difference vs the baseline.

- After **Ex 2** (Entity matching ON): #1, #2, #3 should pass — case mismatch fixed.
- After **Ex 4** (in-force instruction added): #4 should pass.
- After **Ex 5** (trusted assets added): #5 and #6 should pass.

If a question still fails after the "right" exercise, it's a coaching moment: dig into the generated SQL and figure out the residual gap.

## Coaching the "add your own benchmark" step (Part B)

Suggested question for attendees: *"What's our average paid claim amount for property fire losses in 2025?"*

**What you'll likely see Genie generate (varies by whether Entity matching is on yet — it isn't, in Ex 1):**

```sql
SELECT AVG(cl.claim_amount_thb) AS avg_paid_thb
FROM workspace.insurance_data.claims cl
JOIN workspace.insurance_data.policies p ON p.policy_id = cl.policy_id
WHERE p.product_subtype = 'property_fire'
  AND cl.status = 'paid'
  AND YEAR(cl.settle_date) = 2025;
```

…but Genie might generate `'Property_fire'` or `'Paid'` (uppercase) since Entity matching is OFF in Ex 1. **That's the point**: attendees see the raw failure mode and learn to verify the SQL themselves.

**Things attendees should check (your coaching prompts):**

1. **Case** — is `'paid'` actually `'paid'` in the column? Run `SELECT DISTINCT status FROM workspace.insurance_data.claims`. (Genie WILL likely get this wrong in Ex 1.)
2. **Date column** — `YEAR(cl.settle_date) = 2025` or `YEAR(cl.loss_date) = 2025`? Both are defensible; the *insurance* convention is `loss_date` for occurrence-year reporting, `settle_date` for paid-in-year cash reporting. Ask attendees: *which would the business expect?*
3. **Population filter** — `product_subtype = 'property_fire'` matches the actual data? Confirm with `SELECT DISTINCT product_subtype FROM workspace.insurance_data.policies`.
4. **Aggregation** — `AVG(claim_amount_thb)`, not `SUM`, not over the wrong table.
5. **Currency framing** — output column called `avg_paid_thb` makes the unit explicit. If it's just `avg_amount` that's a minor nit.
6. **Sanity check the number** — eyeball the result. If you got "23 THB" something is broken; if "5,000,000 THB" it's plausible.

**Common attendee mistakes to catch:**
- Pasting Genie's SQL into the benchmark without running it themselves.
- Skipping the sanity check on the result number.
- Assuming `settle_date` and `loss_date` are interchangeable (they're not — a 2024 loss can be settled in 2025).

If an attendee's question is too judgement-laden (*"who's our best agent?"*), redirect them to a more concrete formulation (*"top 5 agents by paid claim count in 2025"*) — the lesson is that benchmark questions need a deterministic right answer.

## Common attendee questions

- **"My expected SQL returns different column order — does that fail?"** Yes, the scorer compares result sets including column names. Use consistent aliasing in expected SQL.
- **"Can I run a subset of the benchmark?"** Yes — re-running individual questions is the normal tuning loop.
- **"How do I know which lever to reach for?"** Each later exercise covers one: Ex 2 settings → case/format; Ex 3 → instruction hygiene; Ex 4 → business term definitions; Ex 5 → query shape (trusted assets).
