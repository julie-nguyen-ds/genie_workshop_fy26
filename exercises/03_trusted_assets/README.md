# Exercise 3 — Create SQL Trusted Assets

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
- `workspace.insurance_data` schema loaded.

---

## Part A — SQL function (~13 min)

We'll add a function that aggregates claims by loss type over a date range. Before we add anything, let's see *why* we need it.

### Step 1. See the problem first (~3 min)

Open your workshop Genie space. **Without any trusted assets yet**, ask:

> *Show me total paid claims by loss type for 2025.*

When Genie answers, **click "Show SQL"** (or expand the card) to see what it actually wrote. Then ask the **same question 2 more times** in fresh threads.

You'll likely see at least one of these, varying between runs:

| Problem | What goes wrong | Why it matters |
|---|---|---|
| **Wrong date column** | Filters on `report_date` or `settle_date` instead of `loss_date` | A claim reported in 2025 for a 2024 loss gets counted in the wrong year |
| **Counts unpaid claims as "paid"** | `SUM(claim_amount_thb)` with no `status = 'paid'` filter | Reserves and denied claims inflate the "paid" total |
| **Drifting column names** | One run says `total_amount`, the next `sum_claims`, the next `claim_total_thb` | Downstream dashboards / exports break; users lose trust |
| **No currency framing** | Numbers shown with no "THB" anywhere | Business users assume USD |

**The point:** even a "correct-looking" answer is the wrong primitive when the definition shifts every time someone asks. That's the gap trusted assets close.

### Step 2. Author the function in UC (~5 min)

Open a new SQL query (or use a notebook). Use `starter.sql` as your template, or write your own.

```sql
CREATE OR REPLACE FUNCTION
  workspace.insurance_data.claims_by_loss_type(
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
    FROM workspace.insurance_data.claims
    WHERE loss_date BETWEEN start_date AND end_date
    GROUP BY loss_type
    ORDER BY claim_count DESC;
```

Notice the function bakes in every fix from the table above: `loss_date` (not `report_date`), `status = 'paid'` filter, stable column names (`claim_count`, `total_paid_thb`), `_thb` suffix making the currency unambiguous.

Run it. Test it standalone:
```sql
SELECT * FROM workspace.insurance_data.claims_by_loss_type(DATE'2025-01-01', DATE'2025-12-31');
```

### Step 3. Attach the function to the Genie space (~2 min)
1. Open the workshop Genie space.
2. Right rail → **Functions** → **Add functions**.
3. Search for `claims_by_loss_type` and add it.
4. When prompted, fill in the two fields shown in the attach dialog:

   - **Sample question:**
     > *Show me total paid claims by loss type for 2025.*

   - **Usage guidance** (list the *phrasings* that should hit this function, not just what it does — Genie matches user prompts against these examples semantically):
     ```
     Call this function whenever the user asks for claims grouped by loss_type
     over a date range. The function filters on loss_date and only sums claims
     where status = 'paid'.

     Phrasings that should all trigger this function:
       • "Show me total paid claims by loss type for 2025"
       • "Paid claims by loss_type in 2025"
       • "Claims broken down by loss type, January 2025"
       • "Loss type distribution of paid claims this year"
       • "What's our paid claim total per loss type for Q1 2026?"
       • "How much have we paid out by loss type last month?"
       • "Top loss types by paid claim amount in 2025"
       • "Breakdown of claims by type of loss for 2025"

     Map the user's time window to start_date / end_date:
       • "2025"           → DATE'2025-01-01', DATE'2025-12-31'
       • "January 2025"   → DATE'2025-01-01', DATE'2025-01-31'
       • "Q1 2026"        → DATE'2026-01-01', DATE'2026-03-31'
       • "last month"     → first and last day of the previous calendar month
       • "year-to-date"   → DATE'YYYY-01-01' through current_date()

     Do NOT call this function for:
       • Claims grouped by something other than loss_type (status, branch, agent)
       • Questions about open / pending / denied claims (function only sums paid)
       • Filtered further by product_line or product_subtype (write a custom query)
     ```

**Why both fields, and why list phrasings?** The function's UC `COMMENT` is for humans browsing the catalog — Genie's planner doesn't lean on it much. The **sample question** and **usage guidance** are what Genie actually reads when deciding *whether* to call the function for a user prompt:

- The sample question pins a single canonical phrasing.
- The usage guidance widens the net. Users won't say the canonical phrase verbatim — they'll say *"breakdown of claims by type of loss"*, *"paid loss-type totals last month"*, *"how much have we paid per loss type"*. By listing those paraphrases explicitly, you give Genie's semantic matcher concrete anchors to score against — and you also list **what NOT to do** so Genie doesn't mis-fire on adjacent-but-different questions (e.g. *"claims by status"* — wrong grouping; *"open claims by loss type"* — wrong status filter).

Skip these two fields and Genie sees only the signature + return type. It'll still work *sometimes*, but you'll lose the Trusted badge any time a user phrases their question even slightly differently.

### Step 4. Re-ask and compare (~3 min)

In a fresh thread, ask the **same question** as Step 1:

> *Show me total paid claims by loss type for 2025.*

Now check, and compare against your Step 1 runs:
- ✅ **Trusted** badge appears on the response card — Genie called your function instead of writing its own SQL.
- ✅ Columns are `loss_type`, `claim_count`, `total_paid_thb` — same every time.
- ✅ `total_paid_thb` only includes `status = 'paid'` claims.
- ✅ The `_thb` suffix makes the currency unambiguous.

Ask it 2 more times. The answer is now identical across runs. **That repeatability is what trusted assets buy you.**

---

## Part B — Parameterized example SQL (~10 min)

> Optional warm-up: before adding the example SQL below, try asking Genie *"Who are the top 5 agents by claim count in Phuket?"* and look at the SQL it generates. The `claims` table has no `agent_id`, so Genie often errors out or invents the wrong join path. Same lesson as Part A — query shapes also need to be pinned.

Now the second flavor: an example SQL with a `:province` parameter.

### Step 1. Add the example SQL
In the space, right rail → **Example SQL queries** → **Add**.

```sql
-- Question: Top 5 agents by claim count in :province
SELECT
  a.agent_id,
  a.agent_name,
  COUNT(cl.claim_id) AS claim_count
FROM workspace.insurance_data.agents a
JOIN workspace.insurance_data.policies p ON p.agent_id = a.agent_id
JOIN workspace.insurance_data.claims cl ON cl.policy_id = p.policy_id
JOIN workspace.insurance_data.branches b ON b.branch_id = a.branch_id
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

## Discussion (~3 min)
- **What you saw in Step 1 of Part A** is the default Genie behavior at scale — the same business question gets a slightly different answer every time because the underlying SQL is regenerated. Trusted assets pin the answer.
- **When SQL function vs example SQL?** Function = reusable across many questions, lives in UC, callable from anywhere. Example SQL = scoped to this space, more flexible (joins, CTEs, parameters), faster to author.
- **What if the user asks something slightly different?** Genie may decide your trusted asset doesn't fit and write its own SQL — then the badge won't appear. That's expected; trusted assets aren't a guarantee they'll always be used.
- **Discoverability for users.** Show attendees how to see the function/example SQL in the right rail of the space.

## Done when
- [ ] Function `claims_by_loss_type` exists in UC and is attached to the space.
- [ ] Example SQL "Top 5 agents by claim count in :province" is saved on the space.
- [ ] At least one of your test prompts produces an answer with the **Trusted** badge.

## If you finish early
Add a second SQL function: `premium_by_branch(year INT)` returning total premium written by branch for a given year. Attach it. Ask Genie for "total premium by branch in 2025".
