# Exercise 2 — Entity Matching & Format Assistance

**Time:** ~12 minutes
**Goal:** Make Genie match user-spoken values (e.g. `"Paid"`) to actual column values (`paid`, lowercase) without having to write SQL trusted assets first. This fixes the case-mismatch failures you saw in the Exercise 1 benchmark.

## Why this matters

Genie writes SQL by translating natural language into filters. Users say things like *"how many claims have been **paid** in 2025?"* — Genie writes `WHERE status = 'Paid'`. The SQL is syntactically perfect. It executes successfully. It returns **zero rows**, because the actual values in the column are lowercase `'paid'`.

This is the worst class of bug: **silent**. The query runs. No error appears. A non-technical user sees "0 claims paid in 2025" and walks away with a wrong answer.

Two settings on the Genie space fix this without any SQL:
- **Entity matching** — Genie samples distinct values from low-cardinality columns and learns to map user-spoken entities (`"Paid"`, `"PAID"`, `"paid claims"`) to the actual values.
- **Format assistance** — guides Genie on how values are formatted (case, spelling, special characters), so generated filter predicates respect the column's actual format.

## Prerequisites
- The base Genie space (`space_id` from facilitator).
- `workspace.insurance_data` schema loaded.

---

## Step 1. See the problem (~3 min)

Open your workshop Genie space. **With both settings still OFF**, ask:

> *How many claims have been paid in 2025?*

When Genie answers, click **Show generated code** (or expand the SQL panel). You'll likely see something like:

```sql
SELECT COUNT(*) AS paid_claims_2025
FROM workspace.insurance_data.claims
WHERE status = 'Paid'       -- ← capitalised!
  AND YEAR(settle_date) = 2025;
```

The result: **0 rows**.

Now run this in a separate SQL editor to see what's actually in the column:
```sql
SELECT DISTINCT status FROM workspace.insurance_data.claims;
```
Result: `denied`, `open`, `paid`, `pending` — **all lowercase**.

So Genie's SQL is technically correct but semantically wrong: a value that doesn't exist in the data. The query ran, returned zero, and no warning was emitted. Imagine this in a board report.

Try a second variant to confirm the pattern:
> *How many motor policies are active?*

Likely SQL: `WHERE product_line = 'Motor' AND status = 'Active'` — but the data has `motor` and `active` (both lowercase). Same silent zero.

---

## Step 2. Enable Entity matching (~3 min)

1. Open the Genie space's **Settings** (gear icon, top right of the space).
2. Find **Entity matching** and toggle it **ON**.
3. Genie will now scan low-cardinality columns (`status`, `product_line`, `product_subtype`, `commission_tier`, `region`, …) and index the distinct values it finds.
4. Save / Apply.

What this buys you: when a user prompt mentions a value (e.g. *"paid"*, *"Paid"*, *"PAID"*), Genie compares it against the indexed values and substitutes the actual canonical value into the SQL.

---

## Step 3. Enable Format assistance (~2 min)

1. Same Settings panel.
2. Toggle **Format assistance** **ON**.
3. Save / Apply.

What this buys you: stronger guidance to the planner that generated filter predicates must match the column's exact formatting — case, whitespace, accents. It complements Entity matching by also covering values it hasn't seen sampled (e.g. high-cardinality columns) and by enforcing the format on values you bring in from the user prompt verbatim.

---

## Step 4. Re-ask and compare (~2 min)

In a fresh thread, ask the same question as Step 1:

> *How many claims have been paid in 2025?*

Expand the generated SQL. You should now see:

```sql
WHERE status = 'paid'       -- ← lowercase, matches the data
```

…and a non-zero count.

Try the second one too:
> *How many motor policies are active?*

Now `WHERE product_line = 'motor' AND status = 'active'` — both lowercase, real result.

---

## Discussion (~2 min)

- **Why isn't this on by default?** Sampling values has a context-token cost. On a 5-table schema with low-cardinality enums it's cheap. On a warehouse with hundreds of tables and high-cardinality columns (millions of customer IDs), indexing every distinct value would blow up the planner's context. Picking when to enable it is a per-space decision.
- **Entity matching ≠ synonyms.** It maps spelling/case variants of the *same* word to the canonical value. It will **not** equate `"motor"` with `"auto"` or `"vehicle"` — those are domain synonyms and live in text instructions (Exercise 4) or as example SQL queries.
- **Where else does this break in our dataset?**
  - Province names (`"Phuket"` vs `"phuket"` — actually mixed-case in our data, watch for this)
  - Adjuster names with Thai diacritics
  - Product subtypes with underscores (`motor_voluntary` vs *"voluntary motor"* phrasing)
- **Diagnose silent failures:** when Genie returns `0` and the user expected a real number, always click **Show generated code** first. The case-mismatch pattern is one of the top three failure modes in production Genie spaces.

---

## Done when
- [ ] Entity matching enabled on the workshop Genie space.
- [ ] Format assistance enabled on the workshop Genie space.
- [ ] *"How many claims have been paid in 2025?"* returns a non-zero count and the SQL shows `status = 'paid'`.
- [ ] You can explain why the original query returned 0 even though it executed.

## If you finish early
Find another silent-zero in the schema. Try *"how many open claims do we have for property fire losses?"* — `loss_type` casing? `product_subtype` underscores? Document the failure, then verify entity matching catches it.
