# Exercise 3 — Use SQL Query (slides)

---

## Slide 1 — Title
**Exercise 3: Use SQL Query (Parametrized and Non-Parametrized)**
*~22 minutes — pin Genie's SQL to a pre-vetted query using two flavors of SQL Query asset*

---

## Slide 2 — Why pin the SQL
- Default Genie writes SQL on the fly → flexible, but can hallucinate or get aggregations subtly wrong.
- A **SQL Query** asset saves pre-vetted SQL on the space. When a user prompt matches it semantically, Genie reuses your SQL **verbatim** instead of generating new SQL.
- You confirm reuse by expanding the generated-SQL panel on the answer card and diffing against the SQL you saved.

Today's vehicle: **Example SQL queries** (the space's "Example SQL queries" right-rail panel). UC SQL functions are another valid option, but their Add-Function dialog currently rejects DATE parameters — we stick to Example SQL where DATE works.

---

## Slide 3 — What you'll do
Part A (~10 min) — **non-parametrized SQL Query**:
1. Ask Genie *"Show me total paid claims by loss type for 2025"* — observe what it generates wrong (wrong date column, missing paid filter, drifting column names).
2. Paste the verified SQL from Ex 1's `ground_truth.sql` as a SQL Query on the space, with question text + usage guidance.
3. Ask again — the SQL panel now matches your saved query exactly.

Part B (~10 min) — **parametrized SQL Query**:
1. Same query, but with `:start_date` / `:end_date` placeholders (DATE type).
2. Now Genie can answer the same shape for *any* year, not just 2025.
3. Ask for Q1 2026 → reuse with params filled.

Discussion (~2 min): when to choose each flavor.

---

## Slide 4 — Non-parametrized vs parametrized
| | Non-parametrized | Parametrized |
|---|---|---|
| Authoring effort | Minimal — paste SQL, name the question | A bit more — declare each param's type, sample, description |
| Coverage | One specific prompt shape only | A whole family of prompts with one SQL shape |
| Genie matching | Easy — semantic match on the question text | Slightly harder — Genie has to extract param values from the prompt |
| Reach for it when | Marquee question execs ask verbatim; absolute zero drift required | Common question shape with varying filters (dates, regions, product lines) |

**Heuristic:** if you'd write *"for $year"* / *"in $branch"* in the question, parametrize. If the question always uses the exact literal value, non-parametrize.

---

## Slide 5 — They coexist
Both flavors live on the same space. Genie picks whichever matches better:
- Non-parametrized "for 2025" wins on the exact 2025 phrasing.
- Parametrized variant wins on every other year / quarter / month.

In a production space you'll typically have *both* — a tight non-param for the executive-favorite version of a recurring query, plus a parametrized version that covers everything else.

---

## Slide 6 — Done when
- [ ] Non-parametrized SQL Query for "total paid claims by loss type for 2025" attached; expand-SQL panel matches what you saved
- [ ] Parametrized SQL Query with `:start_date` / `:end_date` attached; non-2025 date question runs with the params filled in
- [ ] Re-run Ex 1 benchmark → your user-added 6th question now passes

*Finished early?* Parametrize *"top 5 agents by claim count in `:province`"* and try Phuket / Bangkok / Chiang Mai. Bonus: add a non-parametrized SQL Query for the 4-way join in Ex 1 benchmark #5 (top agents + branch).
