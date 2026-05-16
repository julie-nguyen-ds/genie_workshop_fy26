# Exercise 3 — Refactored Solution

The bloated single-instruction blob from `bloated_instructions.md` gets split across
the **right** asset types. This is the destination state.

## Heuristic
- One **fact** per `text_instruction`. Atomic. < 500 chars.
- **Table descriptions** go on the table, not in instructions.
- **SQL patterns** are `example_question_sqls` (with the question they answer) or `sql_snippets` (reusable measures).
- **FAQs** that are really conditional logic should be encoded as instructions; FAQs that are just sample questions belong in the space's sample questions or as example SQL.

---

## 1. Move each glossary term to its own `text_instruction`

```json
[
  {"id": "ti_in_force", "content": ["A policy is 'in-force' when status = 'active' AND effective_date <= current_date() AND expiry_date >= current_date(). Apply all three conditions for any question about in-force, active right now, or currently active."]},
  {"id": "ti_lapsed", "content": ["'Lapsed' policies have status = 'lapsed', typically due to missed payments."]},
  {"id": "ti_cancelled", "content": ["'Cancelled' policies have status = 'cancelled', typically customer-initiated."]},
  {"id": "ti_severity", "content": ["Claim severity = AVG(claim_amount_thb) per claim. Frequency = COUNT(claims) / COUNT(policies)."]},
  {"id": "ti_renewal", "content": ["A 'renewal' is a policy whose effective_date is within 30 days of a prior policy's expiry_date for the same customer_id."]},
  {"id": "ti_currency", "content": ["All monetary columns end in _thb and are in Thai Baht. Do not convert to USD unless explicitly asked."]},
  {"id": "ti_dates", "content": ["Use current_date() for 'today', 'now', 'currently'. 'Last month' = the previous calendar month, not trailing 30 days. 'This year' = current calendar year."]},
  {"id": "ti_fraud", "content": ["'Fraud' refers to claims where fraud_flag = true."]},
  {"id": "ti_claims_no_agent", "content": ["The claims table has no agent_id. To filter or group claims by agent, join claims -> policies -> agents."]}
]
```

That's **9 atomic instructions** instead of one monster.

## 2. Move loss ratio + earned premium to `sql_snippets` (reusable measures)

```json
[
  {
    "id": "sn_loss_ratio",
    "name": "loss_ratio",
    "description": ["Loss ratio for a cohort of policies: total claims / total premium written"],
    "sql": "SUM(cl.claim_amount_thb) / NULLIF(SUM(p.annual_premium_thb), 0)"
  },
  {
    "id": "sn_earned_premium",
    "name": "earned_premium_as_of",
    "description": ["Time-prorated earned premium for a policy as of date :as_of"],
    "sql": "annual_premium_thb * GREATEST(0, LEAST(DATEDIFF(:as_of, effective_date), DATEDIFF(expiry_date, effective_date))) / NULLIF(DATEDIFF(expiry_date, effective_date), 0)"
  }
]
```

## 3. Move the canonical join patterns to `example_question_sqls`

```json
[
  {
    "id": "eq_top_agents_by_claims",
    "question": ["Top N agents by claim count, with branch"],
    "sql": "SELECT a.agent_name, b.branch_name, COUNT(cl.claim_id) AS claim_count FROM main.insurance_data.agents a JOIN main.insurance_data.policies p ON p.agent_id = a.agent_id JOIN main.insurance_data.claims cl ON cl.policy_id = p.policy_id JOIN main.insurance_data.branches b ON b.branch_id = a.branch_id GROUP BY a.agent_name, b.branch_name ORDER BY claim_count DESC LIMIT 10"
  },
  {
    "id": "eq_in_force_now",
    "question": ["List in-force policies as of today"],
    "sql": "SELECT * FROM main.insurance_data.policies WHERE status = 'active' AND effective_date <= current_date() AND expiry_date >= current_date()"
  }
]
```

## 4. Move table descriptions to the table identifier blocks

```json
{
  "identifier": "main.insurance_data.claims",
  "description": ["One row per filed claim. Joins to policies via policy_id (claims has no agent_id). loss_date = when loss occurred; report_date = when reported; settle_date = paid/denied date (NULL if open/pending). status in (open, paid, denied, pending). fraud_flag is boolean."]
}
```

…and similar one-paragraph descriptions per table.

## 5. Delete the FAQ section
- "How many customers do we have?" → just a sample question on the space, not an instruction.
- "Who is the best-performing agent?" → if you want Genie to ask for clarification, that's a separate dedicated instruction: `"When the user asks for 'best' or 'top' agents, ask them to specify the metric (policies sold, premium written, loss ratio, or claim count) before answering."` — atomic and short.
- "How is fraud detected?" → conversation context, not space context. Drop it.

## Result
**Before:** 1 instruction × ~3,800 characters → over the per-instruction cap, Genie may truncate or fail.
**After:** 9 instructions averaging ~200 chars + 2 `sql_snippets` + 2 `example_question_sqls` + 5 per-table descriptions. Each piece does one job; nothing competes for attention; everything is the right asset type.
