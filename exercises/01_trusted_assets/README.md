# Exercise 1 — Create SQL Trusted Assets

**Time:** 25 minutes
**Goal:** Make Genie's answer render the **Trusted** badge by adding a SQL function and a parameterized example SQL.

## Why this matters
By default, Genie writes the SQL itself. That's flexible but it's also where hallucinations and subtle aggregation bugs live. **Trusted assets** are pre-vetted SQL that Genie reuses verbatim — when an answer uses one, it gets a *Trusted* badge, signalling to your business users that the math was reviewed by a human.

Two flavors of trusted asset:
1. **SQL function** — a UC function. Genie can call it; the result is marked Trusted.
2. **Parameterized example SQL** — a saved query template with `:param` placeholders. Genie substitutes values and runs it verbatim.

You'll add one of each.

## Prerequisites
- The base Genie space (`space_id` shared by facilitator).
- `main.thai_pc_insurance_workshop` schema loaded.

---

## Part A — SQL function (~10 min)

We'll add a function that aggregates claims by loss type over a date range.

### Step 1. Author the function in UC
Open a new SQL query (or use a notebook). Use `starter.sql` as your template, or write your own.

```sql
CREATE OR REPLACE FUNCTION
  main.thai_pc_insurance_workshop.claims_by_loss_type(
    start_date DATE COMMENT 'Inclusive start of the loss date window',
    end_date DATE COMMENT 'Inclusive end of the loss date window'
  )
  RETURNS TABLE (loss_type STRING, claim_count BIGINT, total_paid_thb BIGINT)
  COMMENT 'Aggregate claims by loss_type for losses occurring between start_date and end_date.'
  RETURN
    SELECT
      loss_type,
      COUNT(*) AS claim_count,
      COALESCE(SUM(CASE WHEN status = 'paid' THEN claim_amount_thb END), 0) AS total_paid_thb
    FROM main.thai_pc_insurance_workshop.claims
    WHERE loss_date BETWEEN start_date AND end_date
    GROUP BY loss_type
    ORDER BY claim_count DESC;
```

Run it. Test it standalone:
```sql
SELECT * FROM main.thai_pc_insurance_workshop.claims_by_loss_type(DATE'2025-01-01', DATE'2025-12-31');
```

### Step 2. Attach the function to the Genie space
1. Open the workshop Genie space.
2. Right rail → **Functions** → **Add functions**.
3. Search for `claims_by_loss_type` and add it.

### Step 3. Ask Genie a matching question
Type into the space:
> *Show me claims by loss type for 2025.*

Expected: Genie calls your function. The response card shows the **Trusted** badge. 🎉

---

## Part B — Parameterized example SQL (~10 min)

Now the second flavor: an example SQL with a `:province` parameter.

### Step 1. Add the example SQL
In the space, right rail → **Example SQL queries** → **Add**.

```sql
-- Question: Top 5 agents by claim count in :province
SELECT
  a.agent_id,
  a.agent_name,
  COUNT(cl.claim_id) AS claim_count
FROM main.thai_pc_insurance_workshop.agents a
JOIN main.thai_pc_insurance_workshop.policies p ON p.agent_id = a.agent_id
JOIN main.thai_pc_insurance_workshop.claims cl ON cl.policy_id = p.policy_id
JOIN main.thai_pc_insurance_workshop.branches b ON b.branch_id = a.branch_id
WHERE b.province = :province
GROUP BY a.agent_id, a.agent_name
ORDER BY claim_count DESC
LIMIT 5;
```

Mark `:province` as a parameter; sample value `Bangkok`.

### Step 2. Ask Genie
> *Who are the top 5 agents by claim count in Phuket?*

Expected: Genie reuses your example SQL with `:province = 'Phuket'`. **Trusted** badge.

---

## Discussion (~5 min)
- **When SQL function vs example SQL?** Function = reusable across many questions, lives in UC, callable from anywhere. Example SQL = scoped to this space, more flexible (joins, CTEs, parameters), faster to author.
- **What if the user asks something slightly different?** Genie may decide your trusted asset doesn't fit and write its own SQL — then the badge won't appear. That's expected; trusted assets aren't a guarantee they'll always be used.
- **Discoverability for users.** Show attendees how to see the function/example SQL in the right rail of the space.

## Done when
- [ ] Function `claims_by_loss_type` exists in UC and is attached to the space.
- [ ] Example SQL "Top 5 agents by claim count in :province" is saved on the space.
- [ ] At least one of your test prompts produces an answer with the **Trusted** badge.

## If you finish early
Add a second SQL function: `premium_by_branch(year INT)` returning total premium written by branch for a given year. Attach it. Ask Genie for "total premium by branch in 2025".
