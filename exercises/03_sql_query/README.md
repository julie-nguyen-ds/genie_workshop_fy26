# Exercise 3 — Use SQL Query (Parametrized and Non-Parametrized)

**Time:** ~22 minutes
**Goal:** Pin Genie's answer to a pre-vetted SQL query by adding two flavors of **SQL Query** asset to your space: a *non-parametrized* one for a single specific question, and a *parametrized* one that covers a whole family of questions.

> Note on UC SQL functions: UC functions are another way to ship pre-vetted SQL, but the Genie "Add functions" attach dialog currently rejects `DATE` (and `TIMESTAMP`) parameters with *"Parameter start_date has an unsupported type: date"*. We stay with SQL Query (Example SQL) throughout this exercise — `DATE` parameters work fine in the parametrized form.

## Why this matters

By default, Genie writes the SQL itself. That's flexible but it's also where hallucinations and subtle aggregation bugs live. A **SQL Query asset** is pre-vetted SQL you save on the space — when a user prompt matches it semantically, Genie reuses your SQL verbatim instead of generating new SQL each time. You verify Genie reused it by expanding the generated-SQL panel on the answer card and comparing it against the SQL you saved.

Two flavors today:
1. **Non-parametrized** — a fixed canonical query for one specific question. Trivial to author; matches one prompt shape only.
2. **Parametrized** — same idea, but with `:param` placeholders Genie fills in from the user's prompt. Slightly more authoring effort; covers a whole family of questions.

## Prerequisites
- The base Genie space.
- `workspace.insurance_data` schema loaded.
- Entity matching + Format assistance **ON** (you turned these on in Exercise 2).

---

## Part A — Non-parametrized SQL Query (~10 min)

We'll add a SQL Query for the **6th benchmark question you added in Ex 1**: *"Show me total paid claims by loss type for 2024"*. Right now this question fails in your benchmark because Genie generates inconsistent SQL each run. We'll pin it.

### Step 1. See the problem (~2 min)

In a fresh chat thread, ask:

> *Show me total paid claims by loss type for 2024.*

Expand the generated SQL. You'll likely see at least one of:
- `WHERE settle_date BETWEEN ...` instead of `loss_date`
- Missing `status = 'paid'` filter (sums denied/pending too)
- Output column renamed across runs (`total_amount` → `paid_total_thb` → `sum_claims`)
- `ORDER BY` swung between count and amount

This is exactly the gap Ex 1 told us Ex 3 would close.

### Step 2. Author the non-parametrized SQL Query (~5 min)

Open `solution.sql` for the verified version, or compose your own. Either way it should match the `ground_truth.sql` we agreed on in Ex 1 Part B Step 2:

```sql
-- Question: Show me total paid claims by loss type for 2024
SELECT
  loss_type,
  COUNT(*) AS claim_count,
  COALESCE(SUM(claim_amount_thb), 0) AS total_paid_thb
FROM workspace.insurance_data.claims
WHERE loss_date BETWEEN '2024-01-01' AND '2024-12-31'
  AND status = 'paid'
GROUP BY loss_type
ORDER BY claim_count DESC;
```

Notice this query bakes in every fix from Ex 1's ground truth: `loss_date` (not `settle_date`) for the date window, an explicit `status = 'paid'` filter in the WHERE clause (so `claim_count` and `total_paid_thb` both describe paid claims only), stable column names, and `_thb` suffix on the currency column.

### Step 3. Attach it on the Genie space (~2 min)

1. Open the workshop Genie space.
2. Right rail → **Example SQL queries** → **Add**.
3. Paste the SQL above.
4. Fill in the metadata:
   - **Question:** *Show me total paid claims by loss type for 2024*
   - **Usage guidance:** list paraphrases that should hit this exact query (it only handles 2024 — don't widen the net beyond that year):
     ```
     Use this exact query for any 2024-scoped question about paid claims grouped
     by loss_type. Phrasings that should match:
       • "Show me total paid claims by loss type for 2024"
       • "Paid claims by loss_type in 2024"
       • "Breakdown of paid claims by type of loss for 2024"
       • "Loss type distribution of paid claims for 2024"

     Do NOT use this query for any year other than 2024 — use the parametrized
     version below instead.
     ```
5. Save.

### Step 4. Re-ask and verify (~1 min)

In a fresh thread, ask:
> *Show me total paid claims by loss type for 2024.*

Expand the generated-SQL panel. You should see **exactly** the SQL you saved in Step 2 — same WHERE clause, same aliases, same ordering. That's how you confirm Genie reused your query verbatim.

Re-run the Ex 1 benchmark — your 6th question (the one you added) should now pass deterministically.

> Note: Databricks Genie also surfaces a "Trusted" badge on the answer card when a saved query is reused. In some workspaces / UI versions the badge isn't rendered yet — don't rely on it visually. The SQL-diff check above is the definitive test.

---

## Part B — Parametrized SQL Query (~10 min)

The non-parametrized query above only works for 2024. As soon as a user asks about 2023 or *"last quarter"*, Genie has to generate its own SQL again. A **parametrized SQL Query** generalizes — same query shape, `:param` placeholders Genie fills in from the user's prompt.

### Step 1. Author the parametrized SQL Query (~5 min)

```sql
-- Question: Total paid claims by loss type between :start_date and :end_date
SELECT
  loss_type,
  COUNT(*) AS claim_count,
  COALESCE(SUM(claim_amount_thb), 0) AS total_paid_thb
FROM workspace.insurance_data.claims
WHERE loss_date BETWEEN :start_date AND :end_date
  AND status = 'paid'
GROUP BY loss_type
ORDER BY claim_count DESC;
```

Same body, but the literal date range is replaced with `:start_date` and `:end_date`.

### Step 2. Attach with parameter metadata (~3 min)

1. Right rail → **Example SQL queries** → **Add**.
2. Paste the SQL.
3. Fill in the metadata:
   - **Question:** *Total paid claims by loss type between two dates*
   - **Parameters:**
     - `:start_date` — type **DATE**, sample value `2024-01-01`, description: *"Inclusive start of the loss date window. ISO format YYYY-MM-DD."*
     - `:end_date` — type **DATE**, sample value `2024-12-31`, description: *"Inclusive end of the loss date window. ISO format YYYY-MM-DD."*
   - **Usage guidance:**
     ```
     Use this query whenever the user asks for paid claims grouped by loss_type
     over a date range OTHER than 2024 (the fixed 2024 version above handles that
     specific year). Phrasings that should match:
       • "Paid claims by loss type for 2023"
       • "Loss type breakdown of paid claims in Q1 2026"
       • "Paid claims by loss_type last month"
       • "What did we pay out by loss type from March to August 2023?"

     Map the user's time window to :start_date and :end_date:
       • "2023"           → '2023-01-01', '2023-12-31'
       • "Q1 2026"        → '2026-01-01', '2026-03-31'
       • "January 2025"   → '2025-01-01', '2025-01-31'
       • "last month"     → first and last day of the previous calendar month
       • "year-to-date"   → 'YYYY-01-01' through today

     Do NOT use this query for: claims grouped by something other than loss_type
     (status, branch, agent); open/pending/denied claims (filter is paid-only).
     ```
4. Save.

### Step 3. Test (~2 min)

Ask Genie:
> *Loss type breakdown of paid claims for Q1 2026.*

Expand the SQL — should be the parametrized template with `:start_date = '2026-01-01'`, `:end_date = '2026-03-31'`.

Try one more:
> *Paid claims by loss type in 2023.*

Should also use the parametrized version with `'2023-01-01'`, `'2023-12-31'`.

---

## Discussion (~2 min)

**Non-parametrized vs parametrized — when to use which?**

| | Non-parametrized | Parametrized |
|---|---|---|
| Authoring effort | Minimal — paste the SQL, name the question | Slightly more — define each param's type, sample, description |
| Question coverage | One specific prompt shape only | A whole family of prompts sharing one SQL shape |
| Genie matching | Easy — semantic match on the question text | Slightly harder — Genie has to extract values from the user's prompt |
| When to reach for it | Marquee questions executives ask verbatim every Monday; questions where you absolutely cannot afford SQL drift | Common question shapes with varying filters (date ranges, regions, product lines) |

**Heuristic:** if you'd write `"for $year"`/`"for $month"`/`"in $branch"` in the question, parametrize. If the question always uses the exact same literal value (and you want a bulletproof match on that one phrasing), non-parametrize.

**Combining them.** Both can coexist on the same space. Genie will pick whichever matches better. Use a non-param for the "executive favorite" version of a recurring query, plus a parametrized version that covers everything else.

---

## Done when
- [ ] Non-parametrized SQL Query for "total paid claims by loss type for 2024" exists on the space; the corresponding chat prompt returns the **same SQL you saved** (verify by expanding the SQL panel).
- [ ] Parametrized SQL Query with `:start_date` / `:end_date` exists on the space; a non-2024 date question runs with the params correctly filled in.
- [ ] Re-run the Ex 1 benchmark — your user-added 6th question (claims by loss type for 2024) now passes.
- [ ] You can explain when to choose each flavor.

## If you finish early
- Add a parametrized SQL Query for *"Top N agents by claim count in `:province`"* with `:province` as a STRING parameter. Ask Genie *"who are the top 5 agents by claim count in Phuket?"*.
- Add a non-parametrized SQL Query that pins the join shape from Ex 1 benchmark #5 (top 10 agents by claim count + branch — the question `claims` has no `agent_id` problem). After adding it, re-run that benchmark — should pass.

See `solution.sql` for paste-ready versions of both flavors.
