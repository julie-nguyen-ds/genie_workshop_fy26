# Exercise 4 — Business Glossary (slides)

---

## Slide 1 — Title
**Exercise 4: Make Genie Speak Insurance**
*25 minutes — encode your domain vocabulary*

---

## Slide 2 — The translation problem
Business users say:
- "loss ratio"
- "in-force"
- "claim severity"
- "earned premium"

The LLM sees:
- *some fuzzy averages of those phrases from training data*

Result: subtly wrong answers. Your job is to anchor the translation.

---

## Slide 3 — Two asset types do the work
| Asset | Use for |
|---|---|
| **`text_instructions`** | Definitions, rules, disambiguations. *"In-force means X."* |
| **`sql_snippets`** | Reusable measure formulas. *`SUM(claims) / SUM(premium)`.* |

Rule of thumb:
- If it's a *fact or rule*, it's an instruction.
- If it's a *calculation you'd plug into many queries*, it's a snippet.

---

## Slide 4 — What you'll encode (4 KPIs)
1. `loss_ratio` → **snippet**
2. `earned_premium_as_of` → **snippet** (parameterized)
3. "in-force" definition → **instruction**
4. "severity vs frequency" disambiguation → **instruction**

---

## Slide 5 — Test it with end-user voice
| Prompt (their language) | Should produce SQL using… |
|---|---|
| "Motor loss ratio in 2025?" | `loss_ratio` snippet |
| "In-force policies by region right now?" | 3-condition in-force filter |
| "Claim severity for property fire?" | AVG(claim_amount) on the right subtype |
| "Earned premium across portfolio today?" | `earned_premium_as_of` snippet |

---

## Slide 6 — Granularity rule
- One concept per instruction. Don't bundle "in-force" with "lapsed" into one entry.
- One formula per snippet. Don't put a query template in there — that's example SQL.
- If you have to write "and another thing" in an instruction, **split it**.
