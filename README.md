# Genie Space Workshop — Thai P&C Insurance

A 2-hour hands-on workshop teaching analytics teams how to **build and operate** Genie Spaces on Databricks, using a synthetic Thai P&C insurance dataset.

## Audience
Analytics / BI engineers and SAs who will own a Genie space day-to-day. Attendees should already have a Databricks workspace with Genie enabled and a SQL warehouse they can attach to a space.

## Agenda (~2h10m)

| Time | Segment |
|---|---|
| 0:00 – 0:10 | Intro — what makes a good Genie space (3 asset types) |
| 0:10 – 0:35 | **Exercise 1** — Create SQL trusted assets |
| 0:35 – 1:00 | **Exercise 2** — Benchmarks: run, score, tune |
| 1:00 – 1:25 | **Exercise 3** — Fix oversized instructions |
| 1:25 – 1:50 | **Exercise 4** — Business glossary & general instructions |
| 1:50 – 2:00 | Wrap — checklist for shipping a production Genie space |

## Prereqs

Per attendee:
- A Databricks workspace with **Genie enabled** (AI/BI Genie entitlement on Premium+).
- A **SQL warehouse** (Serverless preferred) you can attach to a space.
- Write access to Unity Catalog with `CREATE CATALOG` (the setup creates a `genie_workshop` catalog with an `insurance_data` schema).
- A Databricks PAT (personal access token) for Exercise 3's API-driven space creation.

For the facilitator:
- All of the above, plus you'll run `setup/01_create_base_space.py` and `exercises/03_fix_oversized_instructions/seed_broken_space.py` ahead of time and share the resulting `space_id`s.

## Setup (do this once, before the session)

1. **Load the sample data**
   ```sql
   -- Open setup/00_load_data.sql in a notebook or SQL editor and run.
   -- Creates genie_workshop.insurance_data.{customers, policies, claims, agents, branches}
   ```

2. **Create the base Genie space** (used by Exercises 1, 2, 4)
   ```bash
   export DATABRICKS_HOST="https://<your-workspace>.cloud.databricks.com"
   export DATABRICKS_TOKEN="dapi..."
   python setup/01_create_base_space.py
   # → prints the new space_id; share it with attendees
   ```

3. **Create the broken space for Exercise 3** (separate space, intentionally over-sized instructions)
   ```bash
   python exercises/03_fix_oversized_instructions/seed_broken_space.py
   # → prints the broken space_id; share with attendees just before Ex 3
   ```

## Repo layout

```
data/                            synthetic CSVs + generator
setup/                           SQL + API to bootstrap the workshop
exercises/                       one folder per exercise (README + slides + assets)
slides/workshop_deck.md          consolidated markdown deck
facilitator_guide.md             timing, pitfalls, env checklist
CLAUDE.md                        project tracker
```

## License / re-use
Internal Databricks Field Engineering enablement material. Reuse welcome; please update the sample-data flavor for your customer's vertical.
