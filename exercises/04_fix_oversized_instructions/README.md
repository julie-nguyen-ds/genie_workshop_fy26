# Exercise 4 — Fix Oversized Instructions

**Time:** 25 minutes
**Goal:** Open a Genie space whose instructions are a single oversized blob, and re-home each piece in the *right* asset type — not by chopping the blob into smaller blobs, but by moving each rule to the destination Genie was designed to read it from.

## Why this matters
Every customer hits this wall. They start by putting "everything Genie needs to know" into one giant instructions textarea — glossary, rules, SQL fragments, FAQs. Then they hit the per-instruction character cap, or Genie just gets worse because instructions are competing for attention. The fix is **not** "make text_instructions shorter" or "split it into 9 atomic instructions" — Databricks Genie doesn't have a per-rule atomic-instruction feature; all `text_instructions` entries get concatenated into the planner's context the same way. The actual lever is **putting each piece in the right asset type** so Genie reads it from the slot designed for that kind of content.

### The rule of thumb
| If the rule… | …goes in |
|---|---|
| Applies to **every** query Genie writes (currency, "today" semantics, schema-wide conventions) | **General instructions** (`text_instructions`) — kept short |
| Is a **reusable WHERE clause** (e.g. "in-force" filter) | **SQL filter** (`sql_snippets.filters`) |
| Is a **reusable formula / measure** (loss ratio, earned premium) | **SQL expression / measure** (`sql_snippets.expressions` / `.measures`) |
| Is about **one specific table or column** (`claims` has no `agent_id`, status enum values) | **Per-table description** (`data_sources.tables[].description`) |
| Is a **canonical query shape** for a specific question | **Example SQL** (`example_question_sqls`) |
| Is a **sample question** or **conversational clarification** | Space's *Sample questions* panel, not instructions |

If you find yourself adding the same content to two slots, it probably belongs in only one — pick by which one Genie *uses* for that kind of work.

## Prerequisites
- The **instruction-fix training space** `space_id` shared by your facilitator (they ran `create_training_space.py` ahead of time — this space has its `text_instructions` set to a single oversized blob, which is what you'll refactor).
- 25 minutes of patience.

---

## Step 1 — Open the training space and see what's wrong (~5 min)

1. Open the instruction-fix training Genie space.
2. Click **Instructions** in the right rail.
3. You'll see **one** `text_instructions` entry containing a ~3,800-character blob. Read it. Resist the urge to fix it in place.
4. Try asking Genie:
   > *What's our motor loss ratio in 2025?*

   Observe: response is slow, sometimes wrong, and definitely not consistent across runs. The instruction is past the cap and getting truncated / weighted poorly.

See `bloated_instructions.md` if you want to read the blob outside the UI.

---

## Step 2 — Refactor by destination (~15 min)

Make **five** moves. Each one points to a different asset type. After all five are done, the giant text_instructions blob should be a short paragraph of truly universal rules — everything else has been re-homed.

### Move 1 — Universal facts → **General instructions** (`text_instructions`)

Keep one short entry for things that apply to **every** query. Replace the bloated blob with:

```
All monetary columns end in _thb and are Thai Baht; do not convert to USD
unless asked. Use current_date() for "today", "now", "currently". "Last
month" = the previous calendar month, not trailing 30 days. "This year"
= the current calendar year.
```

That's ~280 chars covering currency + date semantics. Everything else from the original blob moves to one of the slots below.

### Move 2 — In-force filter → **SQL filter** (`sql_snippets.filters`)

The "in-force" rule is a WHERE clause Genie will plug into many queries. Right rail → **SQL snippets** → **Filters** → **Add**:

```json
{
  "name": "in_force",
  "description": ["A policy is in-force when status = 'active' AND the policy window contains today. Use whenever the user asks about in-force, active right now, or currently in force."],
  "sql": "status = 'active' AND effective_date <= current_date() AND expiry_date >= current_date()"
}
```

Now `in-force` is a named filter Genie can drop into the WHERE of any policy-scoped query — no more "did the LLM remember all three conditions this time?" drift.

### Move 3 — Loss ratio formula → **SQL measure** (`sql_snippets.measures`)

Right rail → **SQL snippets** → **Measures** (or **Expressions** depending on the UI version):

```json
{
  "name": "loss_ratio",
  "description": ["Loss ratio = total claims paid / total premium written, for a cohort of policies. Expects 'policies p' and 'claims cl' aliases in the outer query."],
  "sql": "SUM(cl.claim_amount_thb) / NULLIF(SUM(p.annual_premium_thb), 0)"
}
```

Genie can now plug `loss_ratio` into any aggregation that joins `policies p` and `claims cl`. (If you want the earned-premium formula too, add it the same way — same destination, distinct snippet.)

### Move 4 — Table-specific gotchas → **Per-table description**

The "claims has no `agent_id`, join through policies first" note is about *one specific table*. It belongs on the `claims` table's description, not in general instructions. Right rail → **Tables** → **claims** → edit description:

```
One row per filed claim. Joins to policies via policy_id. NOTE: there is
no agent_id on claims — to filter/group claims by agent, traverse
claims → policies → agents. loss_date = when loss occurred;
report_date = when reported; settle_date = paid/denied date (NULL if
open/pending). status in (open, paid, denied, pending). fraud_flag is
boolean.
```

Do the same kind of one-paragraph description for the other 4 tables (briefly — their gotchas are smaller).

### Move 5 — Canonical query shape → **Example SQL**

The original blob had the "top N agents by claim count with branch" SQL fragment as a reference snippet. That's a query shape — it belongs as Example SQL on the space, not buried inside instructions. Right rail → **Example SQL queries** → **Add**:

```sql
-- Question: Top N agents by claim count, with their branch
SELECT a.agent_name, b.branch_name, COUNT(cl.claim_id) AS claim_count
FROM workspace.insurance_data.agents a
JOIN workspace.insurance_data.policies p ON p.agent_id = a.agent_id
JOIN workspace.insurance_data.claims cl  ON cl.policy_id = p.policy_id
JOIN workspace.insurance_data.branches b ON b.branch_id = a.branch_id
GROUP BY a.agent_name, b.branch_name
ORDER BY claim_count DESC
LIMIT 10;
```

This is the same kind of asset you authored in Ex 3 — pinning a canonical join shape so Genie doesn't reinvent it. It also fixes Ex 1 benchmark question #5.

### What about the FAQ section in the original blob?

The blob's FAQ is a mix of three different things — each goes somewhere different (none of them belong in `text_instructions`):
- *"How many customers do we have?"* → **Sample question** on the space (not an instruction at all)
- *"Who is the best-performing agent?"* → **Clarification rule** that genuinely is universal, so keep it in the short general instructions: *"When the user asks for the 'best' or 'top' agent, ask which metric (policies sold, premium written, loss ratio, claim count) before answering."*
- *"How is fraud detected?"* → **Drop it.** It's product trivia, not query context.

---

## Step 3 — Validate (~5 min)

1. Re-run the same prompt as Step 1:
   > *What's our motor loss ratio in 2025?*

   Should now be faster and reference the `loss_ratio` snippet you added.

2. Check the in-force filter:
   > *List in-force policies as of today.*

   Should use the `in_force` SQL snippet — all three conditions applied, consistently.

3. Compare side-by-side with the base space from Exercises 1–2 — your refactored space should answer at least as well, with the general instructions field down to a short paragraph instead of a wall.

4. Re-run the **Ex 1 benchmark** — question #4 ("which branch has the most active in-force policies") should now pass thanks to the in-force filter snippet.

---

## Done when
- [ ] The `text_instructions` field is a short paragraph of universal rules only (~300 chars or less).
- [ ] `in_force` exists as a SQL filter snippet.
- [ ] `loss_ratio` (and optionally `earned_premium`) exists as a SQL measure/expression snippet.
- [ ] The `claims` table description includes the "no agent_id, join through policies" note.
- [ ] At least one canonical join lives as Example SQL.
- [ ] You can articulate, for any new piece of context, which asset type it belongs in.

## Key takeaway
**"My instructions are too long" is rarely the real problem. The real problem is "my instructions are doing five jobs and four of them belong elsewhere."** The instructions field is the path of least resistance, and that's why it becomes a junk drawer. The fix isn't shorter text_instructions — it's *less* in text_instructions and *more* in the asset types Genie's planner reads for each specific job.
