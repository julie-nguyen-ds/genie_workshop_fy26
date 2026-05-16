# Exercise 4 — Fix Oversized Instructions

**Time:** 25 minutes
**Goal:** Open a Genie space whose instructions are a single oversized blob, and refactor it into the *right* asset types.

## Why this matters
Every customer hits this wall. They start by putting "everything Genie needs to know" into one giant instructions textarea — glossary, rules, SQL fragments, FAQs. Then they hit the per-instruction character cap, or Genie just gets worse because instructions are competing for attention. The fix isn't "make it shorter" — it's **putting each piece in the right place**.

The right places are:
- **`text_instructions`** → atomic facts, one per entry, < ~500 chars each
- **`sql_snippets`** → reusable measures (loss ratio, earned premium)
- **`example_question_sqls`** → canonical query shapes for common questions
- **Per-table descriptions** → what each table is for
- *Not in instructions at all* → sample questions on the space; conversation-time clarifications

## Prerequisites
- The **instruction-fix training space** `space_id` shared by your facilitator (they ran `create_training_space.py` ahead of time — this space has its `text_instructions` set to a single oversized blob, which is what you'll refactor).
- 25 minutes of patience.

---

## Step 1 — Open the training space and see what's wrong (~5 min)

1. Open the instruction-fix training Genie space.
2. Click **Instructions** in the right rail.
3. You'll see **one** `text_instructions` entry containing a 3,800-character blob. Read it. Resist the urge to fix it in place.
4. Try asking Genie:
   > *What's our motor loss ratio in 2025?*

   Observe: response is slow, sometimes wrong, and definitely not consistent across runs. The instruction is past the cap and getting truncated / weighted poorly.

See `bloated_instructions.md` if you want to read it outside the UI.

---

## Step 2 — Refactor (~15 min)

Open `refactored_solution.md` as your destination state. Walk through it section by section, applying each piece to the space:

### a. Replace the monster instruction with 9 atomic ones
Delete the single big entry. Add 9 new `text_instructions`, one per fact (in-force, lapsed, cancelled, severity, renewal, currency, dates, fraud, claims-have-no-agent). Each one under ~500 chars.

### b. Promote the two measure formulas to `sql_snippets`
- `loss_ratio` → `SUM(cl.claim_amount_thb) / NULLIF(SUM(p.annual_premium_thb), 0)`
- `earned_premium_as_of` → time-prorated formula with `:as_of` parameter

These are now reusable — Genie can plug them into any aggregation.

### c. Promote canonical joins to `example_question_sqls`
The "top agents by claims" and "in-force now" SQL fragments are query shapes — they belong as example SQL, not instructions.

### d. Move table descriptions to the table identifier blocks
The lines like "claims has no agent_id" go on the `claims` table description directly. Same for the others.

### e. Delete the FAQ section
- "How many customers do we have?" → make it a sample question on the space.
- "Best-performing agent?" → keep as a *one-line* clarification instruction.
- "How is fraud detected?" → drop it (irrelevant to data queries).

---

## Step 3 — Validate (~5 min)

1. Re-run the same prompt:
   > *What's our motor loss ratio in 2025?*

   Should now be faster, more consistent, and reference the `loss_ratio` snippet.

2. Quick sanity check:
   > *List in-force policies as of today.*

   Should use the canonical example SQL.

3. Compare side-by-side with the base space from Exercises 1–2 — your refactored space should answer about as well.

---

## Done when
- [ ] No single `text_instructions` entry is over ~500 chars.
- [ ] `loss_ratio` and `earned_premium_as_of` exist as `sql_snippets`.
- [ ] At least 2 canonical SQL patterns exist as `example_question_sqls`.
- [ ] Each table has a one-paragraph description.
- [ ] You can articulate, for any new piece of context, which asset type it belongs in.

## Key takeaway
**"My instructions are too long" is rarely the real problem. The real problem is "my instructions are doing five jobs and three of them belong elsewhere."** The instructions blob is the path of least resistance, and that's why it becomes a junk drawer. Resist it.
