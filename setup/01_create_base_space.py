# Databricks notebook source
# MAGIC %md
# MAGIC # Create the Workshop's Base Genie Space
# MAGIC
# MAGIC Creates a deliberately minimal Genie space wired to the 5 tables in
# MAGIC `workspace.insurance_data`. Attendees add the trusted assets, example
# MAGIC SQL, and additional instructions themselves during Exercises 1, 2, and 4.
# MAGIC
# MAGIC **Run order:** Run `00_load_data` first.
# MAGIC
# MAGIC **Auth:** picked up from the notebook context — no env vars or PAT.
# MAGIC
# MAGIC **Warehouse:** leave the widget blank to auto-pick (or auto-create) a
# MAGIC Pro / Serverless warehouse. Paste an ID to override.

# COMMAND ----------

dbutils.widgets.text("warehouse_id", "", "SQL Warehouse ID (blank = auto-pick)")
warehouse_id_override = dbutils.widgets.get("warehouse_id").strip()

CATALOG = "workspace"
SCHEMA = "insurance_data"
TABLES = ["agents", "branches", "claims", "customers", "policies"]

# COMMAND ----------

# MAGIC %md
# MAGIC ## Auth + API helper

# COMMAND ----------

import json, urllib.request, urllib.error

ctx = dbutils.notebook.entry_point.getDbutils().notebook().getContext()
HOST = ctx.apiUrl().get()
TOKEN = ctx.apiToken().get()
PARENT_PATH = f"/Workspace/Users/{ctx.userName().get()}"

def api(method: str, path: str, body: dict | None = None) -> dict:
    req = urllib.request.Request(
        f"{HOST.rstrip('/')}{path}",
        data=json.dumps(body).encode("utf-8") if body is not None else None,
        method=method,
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{method} {path} failed: {e.code} {e.read().decode('utf-8')}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Resolve the warehouse
# MAGIC
# MAGIC Picks the first eligible Pro / Serverless warehouse in the workspace,
# MAGIC or creates a small Serverless Pro one if none exist.

# COMMAND ----------

def find_or_create_warehouse() -> str:
    eligible = [
        w for w in api("GET", "/api/2.0/sql/warehouses").get("warehouses", [])
        if w.get("state") != "DELETED"
        and (w.get("enable_serverless_compute") or w.get("warehouse_type") == "PRO")
    ]
    eligible.sort(key=lambda w: (
        0 if w.get("enable_serverless_compute") else 1,
        0 if w.get("state") == "RUNNING" else 1,
    ))
    if eligible:
        chosen = eligible[0]
        print(f"Using existing warehouse: {chosen['name']} ({chosen['id']})")
        return chosen["id"]
    print("No eligible warehouse — creating one.")
    created = api("POST", "/api/2.0/sql/warehouses", {
        "name": "Genie Workshop Starter",
        "cluster_size": "2X-Small",
        "min_num_clusters": 1,
        "max_num_clusters": 1,
        "auto_stop_mins": 10,
        "enable_serverless_compute": True,
        "warehouse_type": "PRO",
    })
    return created.get("id") or created.get("warehouse_id")

warehouse_id = warehouse_id_override or find_or_create_warehouse()
print(f"warehouse_id: {warehouse_id}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Build the serialized space (minimal)
# MAGIC
# MAGIC 5 tables + four sample-question starter prompts + one bare-minimum text
# MAGIC instruction. No example SQL, no SQL snippets — those are added by
# MAGIC attendees in Exercises 1 and 4.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load the 5 starter benchmark questions for Exercise 1
# MAGIC
# MAGIC Attendees will add a 6th question themselves during Part B of Ex 1.
# MAGIC
# MAGIC Reads `exercises/01_benchmarks/benchmark_questions.csv` (sits next to this
# MAGIC notebook in workspace files) and builds the `benchmarks.questions` block
# MAGIC that we'll inline into the `serialized_space` JSON below — so the space
# MAGIC ships with the benchmark already populated, no post-creation API call.

# COMMAND ----------

import os, csv

notebook_path = ctx.notebookPath().get()
csv_path = os.path.normpath(
    f"/Workspace{os.path.dirname(notebook_path)}/../exercises/01_benchmarks/benchmark_questions.csv"
)

with open(csv_path, encoding="utf-8") as f:
    benchmark_rows = list(csv.DictReader(f))

benchmark_questions = [
    {
        "id": f"{50 + i:032d}",
        "question": [row["question"]],
        "answer": [
            {
                "format": "SQL",
                "content": [row["expected_sql"]],
            }
        ],
    }
    for i, row in enumerate(benchmark_rows)
]

print(f"Loaded {len(benchmark_questions)} benchmark questions from {csv_path}")

# COMMAND ----------

serialized_space = json.dumps({
    "version": 2,
    "config": {
        "sample_questions": [
            {"id": "00000000000000000000000000000001", "question": ["What was our total premium written last month?"]},
            {"id": "00000000000000000000000000000002", "question": ["How many claims do we have in motor by loss type this year?"]},
            {"id": "00000000000000000000000000000003", "question": ["Which branch had the highest claims paid in Q1 2026?"]},
            {"id": "00000000000000000000000000000004", "question": ["Show me the top 10 agents by policies sold."]},
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
                "id": "00000000000000000000000000000010",
                "content": ["All monetary amounts are in Thai Baht (THB). Columns ending in _thb are amounts in THB. Use current_date() when the user says 'today', 'now', or 'current'."],
            },
        ],
        "example_question_sqls": [],
        "join_specs": [],
        "sql_snippets": {"filters": [], "expressions": [], "measures": []},
    },
    "benchmarks": {
        "questions": benchmark_questions,
    },
})

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create the space

# COMMAND ----------

result = api("POST", "/api/2.0/genie/spaces", {
    "description": "Thai P&C Insurance — Genie Workshop (base space)",
    "title": "Thai P&C Insurance Workshop",
    "parent_path": PARENT_PATH,
    "warehouse_id": warehouse_id,
    "serialized_space": serialized_space,
})

space_id = result.get("space_id") or result.get("id")
print(f"space_id:        {space_id}")
print(f"benchmarks:      {len(benchmark_questions)} question(s) baked in")
print(f"open:            {HOST.rstrip('/')}/genie/rooms/{space_id}")

# COMMAND ----------

# MAGIC %md
# MAGIC Share the `space_id` printed above with attendees for Exercises 1, 2, 4, and 5.
