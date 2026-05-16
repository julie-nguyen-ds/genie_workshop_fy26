# Genie Space Workshop — Thai P&C Insurance

A 2-hour hands-on workshop teaching analytics teams how to **build and operate** Genie Spaces on Databricks, using a synthetic Thai P&C insurance dataset.

## Audience
Analytics / BI engineers and SAs who will own a Genie space day-to-day. Attendees should already have a Databricks workspace with Genie enabled and a SQL warehouse they can attach to a space.

## Agenda (~1h45m)

| Time | Segment |
|---|---|
| 0:00 – 0:10 | Intro — what makes a good Genie space (3 asset types) |
| 0:10 – 0:25 | **Exercise 1** — Benchmarks: run + add your own (sets the baseline; no tuning here) |
| 0:25 – 0:37 | **Exercise 2** — Entity matching & format assistance (fix the silent-zero) |
| 0:37 – 1:05 | **Exercise 3** — Create SQL trusted assets |
| 1:05 – 1:30 | **Exercise 4** — Fix oversized instructions |
| 1:30 – 1:45 | Wrap — re-run the benchmark; checklist for shipping a production Genie space |

## Prereqs

Per attendee:
- A Databricks workspace with **Genie enabled** (AI/BI Genie entitlement on Premium+).
- A **SQL warehouse** (Serverless preferred) you can attach to a space.
- Write access to a Unity Catalog catalog where the workshop schema will be created (default: `workspace.insurance_data` — `workspace` is the default catalog in Databricks Free Edition).
- A Databricks PAT (personal access token) for Exercise 4's API-driven space creation.

For the facilitator:
- All of the above, plus you'll run `setup/01_create_base_space.py` and `exercises/04_fix_oversized_instructions/create_training_space.py` ahead of time and share the resulting `space_id`s.

## Setup (do this once, before the session)

1. **Load the sample data**
   - Open `setup/00_load_data.py` as a Databricks notebook (Workspace → Repos / Git folder, then "Open as notebook"), attach to a cluster, and Run All.
   - The notebook reads CSVs from `../data/` directly out of workspace files — no Volume upload required.
   - Creates `workspace.insurance_data.{customers, policies, claims, agents, branches}`.

2. **Create the base Genie space** (used by Exercises 1, 2, 4)
   - Open `setup/01_create_base_space.py` as a Databricks notebook and Run All.
   - Auth (host + token) is picked up from the notebook context — no env vars or PAT.
   - The `warehouse_id` widget can be left blank: the notebook auto-picks the first Pro/Serverless warehouse in the workspace, or creates a small Serverless Pro one if none exists.
   - Output prints the new `space_id` and a direct URL — share with attendees.

3. **Create the instruction-fix training space for Exercise 4** (separate space whose `text_instructions` is an intentionally oversized single blob)
   - Open `exercises/04_fix_oversized_instructions/create_training_space.py` as a Databricks notebook and Run All.
   - Same auth + warehouse auto-pick as `01_create_base_space` — no env vars needed.
   - Output prints the training `space_id` — share with attendees just before Ex 4.

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
