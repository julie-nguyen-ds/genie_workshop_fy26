# Exercise 2 — Tuning Walkthrough (facilitator reference)

This is the deep-dive cheat sheet for the live walk-through portion of Exercise 2.

## The 5 starter benchmark questions and why each one is there

| # | Question | Difficulty | Lever needed |
|---|---|---|---|
| 1 | How many policies are currently active? | Easy | none — passes by default |
| 2 | How many claims paid in 2025? | Easy | none |
| 3 | Total claim amount by loss type, motor only, 2025 | Moderate (filter through join) | usually passes; if not → example SQL |
| 4 | **Which branch has the most active in-force policies right now?** | Moderate | **text instruction for "in-force"** — engineered failure #1 |
| 5 | **Top 10 agents by claim count + branch** | Hard (3-way join) | **example SQL** — engineered failure #2 |

3 easy/moderate to set the baseline, 2 engineered failures each demonstrating a different lever. Attendees add a 6th of their own in Part C.

## Engineered failure #1 — "in-force"

**Symptom:** Genie returns the branch with the most `status = 'active'` policies, but several of those have `expiry_date < today`.

**Root cause:** "in-force" is insurance jargon. The LLM has a fuzzy notion of it that doesn't match your data's exact definition.

**Fix:** *text instruction*. Lever choice rationale: this is a definition / business rule, not a query shape.

```
"In-force" policies are policies where status = 'active'
AND effective_date <= current_date()
AND expiry_date >= current_date(). Always apply all three
conditions when the user asks about in-force, active right now,
or currently in force.
```

**Verify:** Re-run question #4. Should now produce the same result as the expected SQL.

## Engineered failure #2 — agent claims join

**Symptom:** Genie either errors ("column `claims.agent_id` does not exist") or invents a wrong path (e.g., joins `claims` to `branches` directly via... nothing sensible).

**Root cause:** the path `claims → policies → agents → branches` is not obvious from column names alone; `claims` has no `agent_id`.

**Fix:** *example SQL*. Lever choice rationale: this is a *query shape* problem. Once Genie has seen the canonical join pattern, it'll reuse for other "by agent" claim questions too.

```sql
-- Question: Top N agents by claim count, with their branch
SELECT a.agent_name, b.branch_name, COUNT(cl.claim_id) AS claim_count
FROM workspace.insurance_data.agents a
JOIN workspace.insurance_data.policies p ON p.agent_id = a.agent_id
JOIN workspace.insurance_data.claims cl  ON cl.policy_id = p.policy_id
JOIN workspace.insurance_data.branches b ON b.branch_id = a.branch_id
GROUP BY a.agent_name, b.branch_name
ORDER BY claim_count DESC
LIMIT 10;
```

**Verify:** Re-run question #5. Should pass.

## When to reach for the third lever — *join spec*

You'd reach for join specs when the same two tables can be joined multiple legitimate ways and you want to lock in the default. For our schema, the joins are mostly unambiguous, so we use text instructions and example SQL. Mention this in the discussion; don't force a third failure into the 25-min budget unless you have time.

## Part C — coaching the "add your own benchmark" step

Suggested question for attendees: *"What's our average paid claim amount for property fire losses in 2025?"*

**What you'll likely see Genie generate on a tuned space (Entity matching + Format assistance on):**

```sql
SELECT AVG(cl.claim_amount_thb) AS avg_paid_thb
FROM workspace.insurance_data.claims cl
JOIN workspace.insurance_data.policies p ON p.policy_id = cl.policy_id
WHERE p.product_subtype = 'property_fire'
  AND cl.status = 'paid'
  AND YEAR(cl.settle_date) = 2025;
```

**Things attendees should check (your coaching prompts):**

1. **Date column** — `YEAR(cl.settle_date) = 2025` or `YEAR(cl.loss_date) = 2025`? Both are defensible; the *insurance* convention is `loss_date` for occurrence-year reporting, `settle_date` for paid-in-year cash reporting. Genie may pick either. Ask attendees: *which would the business expect?*
2. **Status filter** — `'paid'` lowercase, present, single value? (Format assistance from Ex 1 should make this correct.)
3. **Population filter** — `product_subtype = 'property_fire'` matches the actual data? (Run `SELECT DISTINCT product_subtype FROM workspace.insurance_data.policies` to confirm.)
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
- **"How do I know which lever to reach for?"** Diagnose what Genie got wrong: wrong filter → instruction; wrong join → example SQL or join spec; wrong aggregation pattern → example SQL.
