# Exercise 3 — Fix Oversized Instructions (slides)

---

## Slide 1 — Title
**Exercise 3: The Instruction Junk Drawer**
*25 minutes — refactor a real-world mess*

---

## Slide 2 — The problem you'll inherit
Every customer eventually has *one* instruction entry like this:

```
GLOSSARY: ...
TABLES: ...
SQL PATTERNS: ...
FAQ: ...
REMEMBER: don't forget the rules above ...
```

3,800 characters. Past the cap. Genie gets *worse*, not better.

---

## Slide 3 — The fix isn't "shorten it"
The fix is **routing each piece to the right asset type**:

| Asset | What goes here |
|---|---|
| `text_instructions` | Atomic facts (1 fact, 1 entry, <500 chars) |
| `sql_snippets` | Reusable measures (loss ratio, earned premium) |
| `example_question_sqls` | Canonical query shapes |
| Per-table `description` | What each table is and how to join it |
| Sample questions on the space | "How many X do we have?" |
| Just delete it | FAQs that don't change query behavior |

---

## Slide 4 — The refactor (live)
You'll open the broken space, then:
1. Split the monster into **9 atomic `text_instructions`**.
2. Promote loss ratio + earned premium to **`sql_snippets`**.
3. Promote canonical joins to **`example_question_sqls`**.
4. Move table notes to the **table description**.
5. Delete the FAQ section.

---

## Slide 5 — Why this works
- One instruction does **one** job → no competition for Genie's attention.
- Reusable formulas live where they can be reused → `sql_snippets`.
- Query shapes live where they show up as Trusted answers → example SQL.
- Table notes live on the tables → they apply *automatically* to any question about that table.

---

## Slide 6 — Takeaway
> *"My instructions are too long" is rarely the real problem.*
> *The real problem is that my instructions are doing five jobs and three of them belong elsewhere.*

Audit your space's instructions before every release. If any entry mentions more than one concept, split it.
