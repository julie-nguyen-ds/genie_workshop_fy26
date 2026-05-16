# Exercise 3 — Trusted Assets (slides)

---

## Slide 1 — Title
**Exercise 3: SQL Trusted Assets via Example SQL**
*~22 minutes — make Genie show the Trusted badge using two flavors of Example SQL*

---

## Slide 2 — Why trusted assets
- Default Genie writes SQL on the fly → flexible, but can hallucinate or get aggregations subtly wrong.
- **Trusted assets** = pre-vetted SQL Genie reuses *verbatim*.
- When Genie's answer uses one, the response card shows a **Trusted** badge — signal to your business users that a human reviewed the math.

Today's flavor: **Example SQL** queries (live on the space). UC SQL functions are another valid option, but their Add-Function dialog currently rejects DATE parameters — we'll stick to Example SQL where DATE works.

---

## Slide 3 — What you'll do
Part A (~10 min) — **non-parametrized Example SQL**:
1. Ask Genie *"Show me total paid claims by loss type for 2025"* — observe what it generates wrong (wrong date column, missing paid filter, drifting column names).
2. Paste the verified SQL from Ex 1's `ground_truth.sql` as an Example SQL on the space, with question text + usage guidance.
3. Ask again — Trusted badge.

Part B (~10 min) — **parametrized Example SQL**:
1. Same query, but with `:start_date` / `:end_date` placeholders (DATE type).
2. Now Genie can answer the same shape for *any* year, not just 2025.
3. Ask for Q1 2026 → Trusted badge with params filled.

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
- [ ] Non-parametrized Example SQL for "total paid claims by loss type for 2025" → Trusted badge
- [ ] Parametrized Example SQL with `:start_date` / `:end_date` → Trusted badge on a non-2025 prompt
- [ ] Re-run Ex 1 benchmark → your user-added 6th question now passes

*Finished early?* Parametrize *"top 5 agents by claim count in `:province`"* and try Phuket / Bangkok / Chiang Mai. Bonus: add a non-parametrized example SQL for the 4-way join in Ex 1 benchmark #5 (top agents + branch).
