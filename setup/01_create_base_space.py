# Databricks notebook source
# MAGIC %md
# MAGIC # Create the Workshop's Base Genie Space
# MAGIC
# MAGIC Creates a minimal starter Genie space wired to the 5 tables in
# MAGIC `main.insurance_data`. Attendees will iterate on this space across
# MAGIC Exercises 1, 2, and 4. Exercise 3 has its own seed notebook with
# MAGIC intentionally bloated instructions.
# MAGIC
# MAGIC **Run order:** Run `00_load_data` first.
# MAGIC
# MAGIC **Prereq:** a SQL warehouse you can attach to the space — paste its ID
# MAGIC into the `warehouse_id` widget below.

# COMMAND ----------

dbutils.widgets.text("warehouse_id", "", "SQL Warehouse ID")
warehouse_id = dbutils.widgets.get("warehouse_id").strip()
assert warehouse_id, "Set the warehouse_id widget before running."

CATALOG = "main"
SCHEMA = "insurance_data"
TABLES = ["customers", "branches", "agents", "policies", "claims"]

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pull host + token from the notebook context (no PAT required)

# COMMAND ----------

ctx = dbutils.notebook.entry_point.getDbutils().notebook().getContext()
HOST = ctx.apiUrl().get()
TOKEN = ctx.apiToken().get()
USERNAME = ctx.userName().get()
PARENT_PATH = f"/Workspace/Users/{USERNAME}"

print(f"Host:        {HOST}")
print(f"Parent path: {PARENT_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Build the serialized space
# MAGIC
# MAGIC Deliberately minimal: the 5 tables + just the absolute bare-minimum
# MAGIC instructions. Attendees add trusted assets / instructions during exercises.

# COMMAND ----------

import json

serialized_space = json.dumps({
    "version": 1,
    "config": {
        "sample_questions": [
            {"id": "q1", "question": ["What was our total premium written last month?"]},
            {"id": "q2", "question": ["How many claims do we have in motor by loss type this year?"]},
            {"id": "q3", "question": ["Which branch had the highest claims paid in Q1 2026?"]},
            {"id": "q4", "question": ["Show me the top 10 agents by policies sold."]},
        ],
    },
    "data_sources": {
        "tables": [
            {
                "identifier": f"{CATALOG}.{SCHEMA}.{t}",
                "description": [f"See table comment in Unity Catalog for {t}."],
            }
            for t in TABLES
        ],
    },
    "instructions": {
        "text_instructions": [
            {
                "id": "ti_currency",
                "content": ["All monetary amounts are in Thai Baht (THB). Columns ending in _thb are amounts in THB."],
            },
            {
                "id": "ti_today",
                "content": ["Use current_date() when the user says 'today', 'now', or 'current'."],
            },
        ],
        "example_question_sqls": [],
        "sql_snippets": [],
        "join_specs": [],
    },
})

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create the space

# COMMAND ----------

import urllib.request, urllib.error

body = {
    "description": "Thai P&C Insurance — Genie Workshop (base space)",
    "title": "Thai P&C Insurance Workshop",
    "parent_path": PARENT_PATH,
    "warehouse_id": warehouse_id,
    "serialized_space": serialized_space,
}

req = urllib.request.Request(
    f"{HOST.rstrip('/')}/api/2.0/genie/spaces",
    data=json.dumps(body).encode("utf-8"),
    method="POST",
    headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
)
try:
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))
except urllib.error.HTTPError as e:
    raise SystemExit(f"POST /api/2.0/genie/spaces failed: {e.code} {e.read().decode('utf-8')}")

space_id = result.get("space_id") or result.get("id")
space_url = f"{HOST.rstrip('/')}/genie/rooms/{space_id}"

print(f"space_id: {space_id}")
print(f"open:     {space_url}")

# COMMAND ----------

# MAGIC %md
# MAGIC Share the `space_id` printed above with attendees for Exercises 1, 2, and 4.
