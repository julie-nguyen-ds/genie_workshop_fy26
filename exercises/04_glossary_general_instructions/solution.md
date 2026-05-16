# Exercise 4 — Reference Solution

The exact assets to add to your space.

## `sql_snippets`

```json
[
  {
    "id": "sn_loss_ratio",
    "name": "loss_ratio",
    "description": ["Loss ratio = total claims paid / total premium written, for a cohort of policies. Expects 'policies p' and 'claims cl' aliases in the outer query."],
    "sql": "SUM(cl.claim_amount_thb) / NULLIF(SUM(p.annual_premium_thb), 0)"
  },
  {
    "id": "sn_earned_premium",
    "name": "earned_premium_as_of",
    "description": ["Time-prorated earned premium for a single policy row as of date :as_of. Defaults to current_date()."],
    "sql": "annual_premium_thb * GREATEST(0, LEAST(DATEDIFF(:as_of, effective_date), DATEDIFF(expiry_date, effective_date))) / NULLIF(DATEDIFF(expiry_date, effective_date), 0)"
  }
]
```

## `text_instructions`

```json
[
  {
    "id": "ti_in_force",
    "content": ["A policy is 'in-force' when status = 'active' AND effective_date <= current_date() AND expiry_date >= current_date(). Always apply all three conditions when the user asks about in-force, active right now, or currently in force."]
  },
  {
    "id": "ti_severity_frequency",
    "content": ["Claim severity = AVG(claim_amount_thb), i.e. average paid per claim. Claim frequency = COUNT(claims) / COUNT(policies). Do not confuse the two. If the user says 'claims rate', ask whether they mean severity or frequency."]
  }
]
```

## Expected SQL Genie produces for the four test prompts

### "What was our motor loss ratio in 2025?"
```sql
SELECT SUM(cl.claim_amount_thb) / NULLIF(SUM(p.annual_premium_thb), 0) AS loss_ratio_2025
FROM genie_workshop.insurance_data.policies p
LEFT JOIN genie_workshop.insurance_data.claims cl ON cl.policy_id = p.policy_id
WHERE p.product_line = 'motor'
  AND YEAR(p.effective_date) = 2025;
```

### "How many policies are in-force right now by region?"
```sql
SELECT b.region, COUNT(*) AS in_force_count
FROM genie_workshop.insurance_data.policies p
JOIN genie_workshop.insurance_data.agents a ON a.agent_id = p.agent_id
JOIN genie_workshop.insurance_data.branches b ON b.branch_id = a.branch_id
WHERE p.status = 'active'
  AND p.effective_date <= current_date()
  AND p.expiry_date >= current_date()
GROUP BY b.region
ORDER BY in_force_count DESC;
```

### "What's our claim severity for property fire claims?"
```sql
SELECT AVG(cl.claim_amount_thb) AS claim_severity_thb
FROM genie_workshop.insurance_data.claims cl
JOIN genie_workshop.insurance_data.policies p ON p.policy_id = cl.policy_id
WHERE p.product_subtype = 'property_fire';
```

### "What's the earned premium across our portfolio as of today?"
```sql
SELECT SUM(
  annual_premium_thb
    * GREATEST(0, LEAST(DATEDIFF(current_date(), effective_date),
                        DATEDIFF(expiry_date, effective_date)))
    / NULLIF(DATEDIFF(expiry_date, effective_date), 0)
) AS total_earned_premium_thb
FROM genie_workshop.insurance_data.policies;
```
