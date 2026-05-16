# Exercise 2 — Entity Matching & Format Assistance (slides)

---

## Slide 1 — Title
**Exercise 2: Entity Matching & Format Assistance**
*~12 minutes — fix the silent-zero failures from the Ex 1 benchmark*

---

## Slide 2 — The silent-zero failure mode
- User asks: *"how many claims have been **paid** in 2025?"*
- Genie writes: `WHERE status = 'Paid'`
- Actual values in column: `paid`, `open`, `denied`, `pending` (all lowercase)
- Result: query runs, no error, returns **0**.
- Business user reads "0 paid claims" and walks away with the wrong answer.

This is the worst class of Genie bug because nothing flags it. The fix isn't SQL — it's two settings.

---

## Slide 3 — Two settings on the space
- **Entity matching** — Genie samples distinct values from low-cardinality columns; maps user-spoken variants (`"Paid"`, `"PAID"`, `"paid"`) to the canonical value.
- **Format assistance** — guides the planner to respect the column's actual casing / format when emitting filter predicates.

Together: user can say it however they want, Genie writes SQL that matches the data.

---

## Slide 4 — What you'll do
1. Ask Genie *"How many claims have been paid in 2025?"* — observe `status = 'Paid'` and a 0 result.
2. Confirm the data is lowercase via `SELECT DISTINCT status FROM claims`.
3. Enable **Entity matching** in space Settings.
4. Enable **Format assistance** in space Settings.
5. Re-ask — `status = 'paid'`, non-zero count.

---

## Slide 5 — Why not on by default
- Sampling values costs context tokens.
- Cheap on 5-table schemas with enums. Expensive on warehouses with high-cardinality columns (millions of distinct IDs).
- **Per-space decision**: enable it when your filter columns are low-cardinality categoricals.

Entity matching ≠ synonyms. `"paid"` → `"paid"` works; `"motor"` → `"auto"` needs a text instruction (Ex 4) or example SQL (Ex 5).

---

## Slide 6 — Done when
- [ ] Entity matching ON
- [ ] Format assistance ON
- [ ] *"How many claims have been paid in 2025?"* returns a non-zero number, SQL shows `status = 'paid'`

**Diagnostic habit:** when Genie returns `0` and you expected a real number, *always* expand the generated SQL first. Case-mismatch is one of the top three silent-failure modes in production spaces.
