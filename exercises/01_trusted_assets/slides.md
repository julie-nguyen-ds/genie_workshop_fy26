# Exercise 1 — Trusted Assets (slides)

---

## Slide 1 — Title
**Exercise 1: SQL Trusted Assets**
*25 minutes — make Genie show the Trusted badge*

---

## Slide 2 — Why trusted assets
- Default Genie writes SQL on the fly → flexible, but can hallucinate or get aggregations subtly wrong.
- **Trusted assets** = pre-vetted SQL Genie reuses *verbatim*.
- When Genie's answer uses one, the response card shows a **Trusted** badge — signal to your business users that a human reviewed the math.

Two flavors today:
1. **SQL function** (lives in Unity Catalog, callable everywhere).
2. **Parameterized example SQL** (lives on the space, more flexible).

---

## Slide 3 — What you'll do
Part A (10 min): write `claims_by_loss_type(start_date, end_date)` as a UC function, attach to the space, ask Genie a matching question → Trusted badge.

Part B (10 min): add a parameterized example SQL "Top 5 agents by claim count in `:province`", ask Genie → Trusted badge.

Discussion (5 min): when to use which.

---

## Slide 4 — Function vs example SQL
| | SQL function | Example SQL |
|---|---|---|
| Lives in | Unity Catalog (reusable) | This Genie space only |
| Granularity | Atomic aggregation / measure | Whole-question template, joins, CTEs |
| Parameters | Strongly typed | `:name` placeholders |
| Best for | Reusable measures (loss ratio, premium written) | Common question shapes (top-N, by-region) |

**Heuristic:** if 3+ spaces would use the same logic, make it a function. Otherwise, example SQL.

---

## Slide 5 — Done when
- [ ] Function `claims_by_loss_type` in UC and attached to the space
- [ ] Example SQL with `:province` parameter on the space
- [ ] At least one prompt returns an answer with the **Trusted** badge

*Finished early?* Add `premium_by_branch(year INT)` and try "total premium by branch in 2025".
