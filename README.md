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
- Write access to a Unity Catalog catalog where the workshop schema will be created (default: `main.insurance_data`).
- A Databricks PAT (personal access token) for Exercise 3's API-driven space creation.

For the facilitator:
- All of the above, plus you'll run `setup/01_create_base_space.py` and `exercises/03_fix_oversized_instructions/seed_broken_space.py` ahead of time and share the resulting `space_id`s.

## Setup (do this once, before the session)

1. **Load the sample data**
   - Open `setup/00_load_data.py` as a Databricks notebook (Workspace → Repos / Git folder, then "Open as notebook"), attach to a cluster, and Run All.
   - The notebook reads CSVs from `../data/` directly out of workspace files — no Volume upload required.
   - Creates `main.insurance_data.{customers, policies, claims, agents, branches}`.

2. **Create the base Genie space** (used by Exercises 1, 2, 4)
   - Open `setup/01_create_base_space.py` as a Databricks notebook and Run All.
   - Auth (host + token) is picked up from the notebook context — no env vars or PAT.
   - The `warehouse_id` widget can be left blank: the notebook auto-picks the first Pro/Serverless warehouse in the workspace, or creates a small Serverless Pro one if none exists.
   - Output prints the new `space_id` and a direct URL — share with attendees.

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
