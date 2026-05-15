# Exercise 2 — Benchmarks (slides)

---

## Slide 1 — Title
**Exercise 2: Benchmarks — Run, Score, Tune**
*25 minutes — go from vibes-driven tuning to measurable improvement*

---

## Slide 2 — Why benchmarks
- Vibes tuning ("ask, tweak, ask again") doesn't scale past a few questions.
- Benchmarks let you **measure** every change you make.
- Up to **500 questions per space**, scored automatically against your expected SQL.
- Critical: benchmarks **evaluate**, they do not **inform**. They're test data, not training data.

---

## Slide 3 — The 3 tuning levers
| Lever | When to reach for it |
|---|---|
| **Text instruction** | Business term / rule (e.g. "in-force") |
| **Example SQL** | Wrong query shape (joins, aggregation) |
| **Join spec** | Ambiguous join paths between tables |

Today you'll use the first two. (Join spec is the lever for messy multi-fact schemas.)

---

## Slide 4 — What you'll do
1. Import `benchmark_questions.csv` (10 Q+SQL pairs).
2. Run benchmark, watch the score.
3. Two questions are engineered to fail:
   - **"In-force policies"** → fix with a text instruction.
   - **"Top agents with branch"** → fix with example SQL.
4. Re-run, watch score climb.

---

## Slide 5 — Failure #1: "in-force"
**Symptom:** Genie ignores the date window — counts expired policies too.
**Lever:** text instruction.
```
"In-force" = status='active' AND effective_date <= current_date()
AND expiry_date >= current_date(). Apply all three.
```

---

## Slide 6 — Failure #2: agent claims join
**Symptom:** Genie can't traverse claims → policies → agents → branches.
**Lever:** example SQL.
```sql
SELECT a.agent_name, b.branch_name, COUNT(*) ...
FROM agents a
JOIN policies p ON p.agent_id = a.agent_id
JOIN claims  cl ON cl.policy_id = p.policy_id
JOIN branches b ON b.branch_id = a.branch_id
GROUP BY a.agent_name, b.branch_name ORDER BY count DESC LIMIT 10;
```

---

## Slide 7 — Production rule of thumb
- ≥ 20 benchmark questions covering your top user prompts.
- Re-run on every change to instructions / tables / SQL functions.
- Refresh the benchmark when the schema evolves.
- A benchmark score isn't a SLO — it's a *trend you're trying to move*.
