# Genie Space Workshop — Thai P&C Insurance

*Consolidated deck source. One section = one slide. Will be converted to a Databricks-branded Google Slides deck.*

---

## 1. Title slide
**Building Production-Grade Genie Spaces**
A hands-on workshop for [Customer Name] — Thailand
Facilitated by Julie Nguyen, Databricks Field Engineering
2026 · 2 hours · 4 exercises

---

## 2. What you'll leave with
- A working Genie space backed by real P&C data
- Concrete patterns for **trusted assets**, **benchmarks**, and **instruction hygiene**
- A short list of mistakes you don't have to make
- A production-readiness checklist you can take back to your team

---

## 3. The mental model
A Genie space has four kinds of context:

| Asset | Job |
|---|---|
| Table descriptions | Tell Genie what each table is |
| Text instructions | Atomic facts and rules |
| SQL snippets | Reusable measure formulas |
| Example SQL | Canonical query shapes (Trusted answers) |
| SQL functions (UC) | Reusable measures, callable from anywhere |

The rest of the workshop is learning when to reach for which.

---

## 4. Agenda
| 0:00 | Intro (you are here) |
| 0:10 | Ex 1 — Trusted assets |
| 0:35 | Ex 2 — Benchmarks: run, score, tune |
| 1:00 | Ex 3 — Fix oversized instructions |
| 1:25 | Ex 4 — Business glossary |
| 1:50 | Wrap & production checklist |

---

## 5. The dataset
Synthetic Thai P&C insurer:
- `customers` (~3,000) — Thai policyholders, provinces, occupations
- `branches` (~10) — across major Thai regions
- `agents` (~50) — licensed agents, commission tiers
- `policies` (~10,000) — motor + property
- `claims` (~5,000) — with ~3% fraud-flagged

All in `workspace.insurance_data`. Sample data is already loaded for you.

---

## (Section break) 6. Exercise 1 — Trusted Assets
*See `exercises/01_trusted_assets/slides.md` for the per-exercise slide block.*

---

## (Section break) 7. Exercise 2 — Benchmarks
*See `exercises/02_benchmarks/slides.md` for the per-exercise slide block.*

---

## (Section break) 8. Exercise 3 — Fix Oversized Instructions
*See `exercises/03_fix_oversized_instructions/slides.md` for the per-exercise slide block.*

---

## (Section break) 9. Exercise 4 — Business Glossary
*See `exercises/04_glossary_general_instructions/slides.md` for the per-exercise slide block.*

---

## 10. Production readiness checklist
Before you ship a Genie space to real users:

- [ ] ≥ 5 tested **example SQL queries** covering top user questions
- [ ] A **benchmark** of ≥ 20 questions with expected SQL
- [ ] **Per-table descriptions** (one short paragraph each)
- [ ] **Atomic `text_instructions`** — one fact each, < 500 chars
- [ ] A **glossary** of KPIs as `sql_snippets`
- [ ] A **starter prompt** set on the space (6–10 examples for first-time users)
- [ ] Owners and a review cadence (who maintains, how often)

---

## 11. What's next for [Customer Name]
- Run this workshop's pattern on one real internal use case (suggested: motor claims operations).
- Set up the benchmark *before* you start tuning — not after.
- Audit your existing spaces' instructions for the "junk drawer" pattern.
- Schedule a 4-week check-in: bring your benchmark scores.

---

## 12. Questions
**Julie Nguyen** — julie.nguyen@databricks.com
Workshop materials repo: `~/claude_research/genie-workshop-thai-pc-insurance/`
Official docs: docs.databricks.com → AI/BI Genie
