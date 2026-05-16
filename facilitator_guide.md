# Facilitator Guide

## Day-of timing (tight version)

| min | what you do | watch for |
|---|---|---|
| 0–10 | Intro slides: three asset types (text instructions, example SQL, SQL functions, sql_snippets), what each is for | Don't let intro slip past 10. The doing is the value. |
| 10–25 | **Ex 1 — Benchmarks (run + add the mandated 6th).** Walk through `exercises/01_benchmarks/README.md`. Attendees open the Benchmark tab, confirm 5 pre-loaded questions, click Run benchmark. Don't tune anything; just look at each failure and call out which later exercise fixes it (use the table in the README). Then attendees add the **mandated 6th question** — *"Show me total paid claims by loss type for 2025"* — by asking Genie for the SQL, verifying it themselves in a SQL editor, and saving the verified Q+SQL pair. | This is the *baseline* — keep it brisk. The 6th question is mandated (not free choice) because Ex 3's UC function pins exactly this SQL — when re-run at end of workshop, that question's pass becomes Ex 3's emotional payoff. Coach them through the verification checklist (`loss_date` not `settle_date`, `status='paid'` not `'Paid'`, sanity-check the per-loss_type totals). |
| 25–37 | **Ex 2 — Entity matching & format assistance.** Walk through `exercises/02_entity_matching/README.md`. **Do the silent-zero demo live** — ask "how many claims have been paid in 2025?", point at `WHERE status = 'Paid'` and the 0 result, then `SELECT DISTINCT status FROM claims` to reveal the lowercase values. Then have attendees enable Entity matching + Format assistance and re-ask. Optionally re-run the Ex 1 benchmark and observe questions 1-3 now pass. | The teaching moment is "the query ran, returned a number, and was still wrong." Don't move on until everyone has seen the 0 → real-count flip on their own space. |
| 37–65 | **Ex 3 — Trusted assets.** Walk through `exercises/03_trusted_assets/README.md`. **First do the "see the problem" step live** — ask "show me total paid claims by loss type for 2025" 2–3 times in fresh threads, expand the SQL, point at the inconsistencies (wrong date column, unpaid claims included, drifting column names, no THB framing). Then have attendees author the function + attach with sample question + usage guidance. After this, Ex 1 benchmark questions #5 and #6 should pass on re-run. | Some attendees will spend too long perfecting their SQL function. Time-box: if they don't have a working function at the 20-min mark, give them the `solution.sql`. |
| 65–90 | **Ex 4 — Fix oversized instructions.** Share the instruction-fix training `space_id` you created ahead of time. Attendees open it, hit the wall, refactor. The refactor extracts the in-force atomic instruction, sql_snippets for loss ratio / earned premium, and example SQL — directly fixing Ex 1 benchmark question #4 in the process. | This one frustrates people — that's the point. After 10 min if folks are stuck, do the refactor live and let them follow. Glossary content (loss_ratio, earned_premium, in-force, severity) lives inside the bloated blob — attendees encounter every KPI when they extract atomic instructions. |
| 90–105 | Wrap. **Re-run the Ex 1 benchmark together** — the score should be much higher than the baseline. Production checklist. Q&A. | The re-run is the workshop's emotional payoff — don't skip it. Show the baseline pass rate vs final pass rate. |

## Prereqs checklist (send to attendees 1 day before)

- [ ] Workspace URL + login confirmed
- [ ] Genie entitlement enabled on your user
- [ ] SQL warehouse you can attach to a space (Serverless OK)
- [ ] Write access to a UC catalog (default `workspace` — the Databricks Free Edition default — schema `insurance_data`)
- [ ] Personal Access Token generated (only needed for Ex 4 if you want to recreate the training space yourself)
- [ ] You've run `setup/00_load_data.py` (as a Databricks notebook) and can `SELECT * FROM workspace.insurance_data.policies LIMIT 5;`

## Pre-flight (you, the facilitator, the morning of)

1. Run `setup/00_load_data.py` (open as Databricks notebook, Run All) in your demo workspace — confirm 5 tables, expected row counts.
2. Run `setup/01_create_base_space.py` as a Databricks notebook (Run All — widget can be blank; auto-picks or creates a warehouse) — write down the `space_id`; open it; confirm all 5 tables show in the right rail.
3. Run `exercises/04_fix_oversized_instructions/create_training_space.py` as a Databricks notebook (Run All — same auth/warehouse pattern as `01_create_base_space`) — write down the training `space_id`; open it; confirm you see the oversized-instruction warning or that the space materially misbehaves.
4. Have `solution.sql`, `tuning_walkthrough.md`, `refactored_solution.md`, and `solution.md` open in tabs — for the moments when you need to unblock the room.

## Common pitfalls

- **"My Genie answer says 'Verified' not 'Trusted'."** Verified means a human reviewed it; Trusted means it used the *exact text* of a parameterized example SQL or SQL function. Different concept. Show the docs.
- **Ex 1 "before" step — Genie answers look correct.** Sometimes Genie *does* pick `loss_date` and filter `status = 'paid'` on the first run. The repeatability angle still holds: ask 2–3 times and point at column-name drift (`total_amount` → `paid_total_thb` → `sum_claims`). If even the column names are stable, fall back to the conceptual framing: *"you got lucky this time; on a different day or schema, the same prompt could quietly produce different SQL."*
- **"The benchmark scorer says my answer is wrong but it looks right."** Benchmark compares result *sets*. Order matters if you didn't `ORDER BY` consistently. Column aliases matter. This is a teaching moment.
- **"I made the instruction shorter and it still doesn't work."** Length isn't the only issue — Genie weights instructions; too many compete. Re-read Ex 4 takeaways.
- **THB currency in queries** — Genie may default to USD framing. Add an instruction: "All monetary columns are in THB."

## Production checklist (the wrap)

When attendees ship a Genie space to real users, they should have:

1. ≥ 5 tested **example SQL queries** covering their top user questions.
2. A **benchmark** of ≥ 20 questions with expected SQL, with a passing rate they're comfortable defending.
3. **Per-table descriptions** — one short paragraph per table, no marketing.
4. **Atomic text_instructions** — one fact per instruction, not paragraphs.
5. A **glossary** of domain KPIs encoded as `sql_snippets` (not pasted into a giant instruction blob).
6. A **starter prompt** set on the space (6–10 sample questions for first-time users).
7. **Owners and SLA** — who maintains this and how often is it reviewed?
