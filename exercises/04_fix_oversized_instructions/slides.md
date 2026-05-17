# Exercise 4 — Fix Oversized Instructions (slides)

---

## Slide 1 — Title
**Exercise 4: The Instruction Junk Drawer**
*25 minutes — refactor a real-world mess by re-homing each rule, not by chopping the blob*

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

~3,800 characters. Past the cap. Genie gets *worse*, not better.

---

## Slide 3 — The fix isn't "shorten it" or "split into atoms"
Genie's `text_instructions` field doesn't get richer when you turn one entry into nine — they all get concatenated into the planner's context the same way. The real lever is **routing each piece to the asset type Genie was designed to read it from**:

| If the rule… | …goes in |
|---|---|
| Applies to **every** query (currency, "today" semantics) | **General instructions** (`text_instructions`) — kept short |
| Is a reusable **WHERE clause** ("in-force") | **SQL filter** (`sql_snippets.filters`) |
| Is a reusable **formula** (loss ratio, earned premium) | **SQL expression / measure** (`sql_snippets.measures`) |
| Is about **one specific table/column** | **Per-table description** |
| Is a **canonical query shape** | **Example SQL** |
| Is a sample question / conversational clarification | *Sample questions* panel, not instructions |

---

## Slide 4 — The refactor (live, 5 moves)
You'll open the training space (oversized single-instruction blob), then make **five** moves — each one points to a different asset type:

1. **General instructions** → keep ONE short paragraph: currency + "today" semantics only.
2. **SQL filter** → `in_force` filter (status + date window).
3. **SQL measure** → `loss_ratio` formula.
4. **Per-table description** → "claims has no agent_id, join through policies" lives on the `claims` table.
5. **Example SQL** → the canonical top-agents-by-claims join.

FAQs in the blob get sorted: sample question / clarification rule / drop.

---

## Slide 5 — Why this works
- **General instructions stay short** → no competition for Genie's attention; the LLM actually reads them.
- **Reusable formulas live where they can be reused** → `sql_snippets`.
- **Query shapes live as Example SQL** → semantic match on the question, deterministic SQL on the answer (same lesson as Ex 3).
- **Table-specific notes live on the table** → they apply *automatically* to any question that touches that table.

---

## Slide 6 — Takeaway
> *"My instructions are too long" is rarely the real problem.*
> *The real problem is that my instructions are doing five jobs and four of them belong elsewhere.*

Audit your space's instructions before every release. If anything in `text_instructions` doesn't apply to **every** query, it's in the wrong slot.
