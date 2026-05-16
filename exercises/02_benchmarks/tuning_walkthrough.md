# Exercise 2 — Tuning Walkthrough (facilitator reference)

This is the deep-dive cheat sheet for the live walk-through portion of Exercise 2.

## The 10 benchmark questions and why each one is there

| # | Question | Difficulty | Lever needed |
|---|---|---|---|
| 1 | How many policies are currently active? | Easy | none — passes by default |
| 2 | Total premium written in 2025 for motor | Easy | none |
| 3 | How many claims paid in 2025? | Easy | none |
| 4 | Total claim amount by loss type, motor only, 2025 | Moderate (filter through join) | usually passes; if not → example SQL |
| 5 | Fraud-flagged claim count + total amount | Easy | none |
| 6 | **Branch with most in-force policies** | Moderate | **text instruction for "in-force"** — engineered failure #1 |
| 7 | **Top 10 agents by claim count + branch** | Hard (3-way join) | **example SQL** — engineered failure #2 |
| 8 | % of motor policies with at least one claim | Moderate | usually passes; uses LEFT JOIN |
| 9 | Avg paid for property fire losses 2025 | Moderate | usually passes |
| 10 | Total sum insured for in-force property by region | Hard (in-force + 3-way join) | will pass *after* fixes for 6+7 are in place |

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

**Verify:** Re-run question #6. Should now produce the same result as the expected SQL.

## Engineered failure #2 — agent claims join

**Symptom:** Genie either errors ("column `claims.agent_id` does not exist") or invents a wrong path (e.g., joins `claims` to `branches` directly via... nothing sensible).

**Root cause:** the path `claims → policies → agents → branches` is not obvious from column names alone; `claims` has no `agent_id`.

**Fix:** *example SQL*. Lever choice rationale: this is a *query shape* problem. Once Genie has seen the canonical join pattern, it'll reuse for other "by agent" claim questions too.

```sql
-- Question: Top N agents by claim count, with their branch
SELECT a.agent_name, b.branch_name, COUNT(cl.claim_id) AS claim_count
FROM genie_workshop.insurance_data.agents a
JOIN genie_workshop.insurance_data.policies p ON p.agent_id = a.agent_id
JOIN genie_workshop.insurance_data.claims cl  ON cl.policy_id = p.policy_id
JOIN genie_workshop.insurance_data.branches b ON b.branch_id = a.branch_id
GROUP BY a.agent_name, b.branch_name
ORDER BY claim_count DESC
LIMIT 10;
```

**Verify:** Re-run question #7. Should pass.

## When to reach for the third lever — *join spec*

You'd reach for join specs when the same two tables can be joined multiple legitimate ways and you want to lock in the default. For our schema, the joins are mostly unambiguous, so we use text instructions and example SQL. Mention this in the discussion; don't force a third failure into the 25-min budget unless you have time.

## Common attendee questions

- **"My expected SQL returns different column order — does that fail?"** Yes, the scorer compares result sets including column names. Use consistent aliasing in expected SQL.
- **"Can I run a subset of the benchmark?"** Yes — re-running individual questions is the normal tuning loop.
- **"How do I know which lever to reach for?"** Diagnose what Genie got wrong: wrong filter → instruction; wrong join → example SQL or join spec; wrong aggregation pattern → example SQL.
