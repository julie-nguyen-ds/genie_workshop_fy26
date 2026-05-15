# Exercise 4 — Business Glossary & General Instructions

**Time:** 25 minutes
**Goal:** Teach Genie your insurance KPIs by encoding them as `text_instructions` and `sql_snippets`. Then test with prompts using end-user language.

## Why this matters
Your business users don't say `SUM(claim_amount_thb) / SUM(annual_premium_thb)`. They say "loss ratio". They don't say `effective_date <= current_date() AND expiry_date >= current_date()`. They say "in-force". The job of a Genie space is to translate business language → SQL semantics. That translation lives in two asset types:

- **`text_instructions`** for definitions, rules, and disambiguations.
- **`sql_snippets`** for reusable calculations the LLM can plug into bigger queries.

You'll encode four insurance KPIs and then ask Genie questions in your business team's natural language.

## Prerequisites
- The base Genie space from Exercise 1 (or your refactored space from Exercise 3 — either works).

---

## Step 1 — Encode the four KPIs (~15 min)

Add the following to your space. Numbers correspond to the asset type.

### 1.1 (`sql_snippet`) `loss_ratio`
Description: *Loss ratio for a cohort of policies — total claims paid divided by total premium written.*
SQL:
```sql
SUM(cl.claim_amount_thb) / NULLIF(SUM(p.annual_premium_thb), 0)
```
Notes: the snippet expects `policies p` and `claims cl` to already be aliased in the outer query. That's intentional — `sql_snippets` are fragments, not full queries.

### 1.2 (`sql_snippet`) `earned_premium_as_of`
Description: *Time-prorated portion of annual premium that has been earned as of date `:as_of`.*
SQL:
```sql
annual_premium_thb
  * GREATEST(0, LEAST(DATEDIFF(:as_of, effective_date),
                      DATEDIFF(expiry_date, effective_date)))
  / NULLIF(DATEDIFF(expiry_date, effective_date), 0)
```
Notes: parameter `:as_of` defaults to `current_date()`.

### 1.3 (`text_instruction`) "in-force"
```
A policy is "in-force" when status = 'active' AND effective_date <= current_date()
AND expiry_date >= current_date(). Always apply all three when the user asks about
in-force, active right now, or currently in force.
```

### 1.4 (`text_instruction`) severity vs frequency
```
Claim severity = AVG(claim_amount_thb), i.e. average paid per claim.
Claim frequency = COUNT(claims) / COUNT(policies), i.e. claims per policy in the cohort.
Never confuse the two. If the user just says "claims rate", ask which they mean.
```

---

## Step 2 — Test with end-user language (~8 min)

Ask Genie these in order. They use *business* phrasing, not SQL phrasing:

| # | Prompt | What Genie should do |
|---|---|---|
| 1 | "What was our motor loss ratio in 2025?" | Use the `loss_ratio` snippet, filter on `product_line='motor'`, year filter on either effective_date or loss_date (call out the ambiguity if it asks). |
| 2 | "How many policies are in-force right now by region?" | Apply all three in-force conditions, join through agents+branches for region. |
| 3 | "What's our claim severity for property fire claims?" | Use AVG(claim_amount_thb), filter on `product_subtype='property_fire'`. |
| 4 | "What's the earned premium across our portfolio as of today?" | Sum the `earned_premium_as_of` snippet with `:as_of = current_date()` across all policies. |

For each, check: did Genie use the snippet/instruction you added? (Look at the SQL it ran.)

---

## Step 3 — Discuss (~2 min)
- **Granularity of instructions.** One concept per instruction. If your "loss ratio" instruction also says "by the way, in-force means…", split it.
- **When snippet vs instruction?** Snippet if the formula is reusable in many query contexts; instruction if it's a *rule* or *disambiguation* the LLM needs to apply.
- **Iteration loop.** Add → ask → check SQL → refine. Benchmarks are how you make this systematic (Exercise 2).

---

## Done when
- [ ] `loss_ratio` and `earned_premium_as_of` exist as `sql_snippets`.
- [ ] "in-force" definition and "severity vs frequency" disambiguation exist as atomic `text_instructions`.
- [ ] All four test prompts use the snippet/instruction you added (verify in the SQL Genie ran).

See `solution.md` for the full JSON payload of what your space should look like.

## If you finish early
Add a `combined_ratio` snippet. (We don't track expense ratio yet, so it's the same as loss ratio for now — *that* is a useful instruction in itself: "Combined ratio = loss ratio + expense ratio. We don't currently track expense_ratio, so combined ratio equals loss ratio.")
