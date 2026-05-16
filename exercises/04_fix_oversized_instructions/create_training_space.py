# Databricks notebook source
# MAGIC %md
# MAGIC # Create the Instruction-Fix Training Genie Space — Exercise 4
# MAGIC
# MAGIC Creates a Genie space whose `text_instructions` is one oversized blob
# MAGIC — glossary + table descriptions + SQL fragments + FAQ all crammed
# MAGIC into a single entry, well past the per-instruction character cap.
# MAGIC Attendees refactor it into atomic, right-typed assets during Exercise 4.
# MAGIC
# MAGIC **Facilitator: run this BEFORE the session and share the resulting
# MAGIC `space_id` with attendees just before Exercise 4.**
# MAGIC
# MAGIC **Auth:** picked up from the notebook context — no env vars or PAT.
# MAGIC
# MAGIC **Warehouse:** leave the widget blank to auto-pick (or auto-create)
# MAGIC a Pro / Serverless warehouse. Paste an ID to override.

# COMMAND ----------

dbutils.widgets.text("warehouse_id", "", "SQL Warehouse ID (blank = auto-pick)")
warehouse_id_override = dbutils.widgets.get("warehouse_id").strip()

CATALOG = "workspace"
SCHEMA = "insurance_data"
TABLES = ["customers", "branches", "agents", "policies", "claims"]

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
# MAGIC ## Load the bloated blob from `bloated_instructions.md`
# MAGIC
# MAGIC Pulls the content from the fenced code block in the markdown file
# MAGIC sitting next to this notebook.

# COMMAND ----------

import os

notebook_path = ctx.notebookPath().get()
bloated_md_path = os.path.normpath(
    f"/Workspace{os.path.dirname(notebook_path)}/bloated_instructions.md"
)
raw = open(bloated_md_path, encoding="utf-8").read()

# Extract the fenced block.
start = raw.find("```")
end = raw.rfind("```")
blob = raw[start + 3:end]
if "\n" in blob:
    first, rest = blob.split("\n", 1)
    if first.strip().isalpha() or first.strip() == "":
        blob = rest
bloated = blob.strip()

print(f"Bloated instruction size: {len(bloated):,} characters")
print("(Per-instruction caps are typically a few thousand characters — this is well over.)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Build the serialized space with the oversized instruction blob

# COMMAND ----------

serialized_space = json.dumps({
    "version": 2,
    "config": {
        "sample_questions": [
            {"id": "00000000000000000000000000000001", "question": ["What is our loss ratio for motor in 2025?"]},
            {"id": "00000000000000000000000000000002", "question": ["How many in-force policies do we have right now?"]},
        ],
    },
    "data_sources": {
        "tables": [
            {"identifier": f"{CATALOG}.{SCHEMA}.{t}"} for t in TABLES
        ],
    },
    "instructions": {
        # The monster: a single instruction containing everything.
        "text_instructions": [
            {"id": "00000000000000000000000000000010", "content": [bloated]},
        ],
        "example_question_sqls": [],
        "join_specs": [],
        "sql_snippets": {"filters": [], "expressions": [], "measures": []},
    },
})

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create the training space

# COMMAND ----------

result = api("POST", "/api/2.0/genie/spaces", {
    "description": "Thai P&C — Genie Workshop Exercise 4 — instruction-size fix training space",
    "title": "Thai P&C — Ex 4 Instruction Fix",
    "parent_path": PARENT_PATH,
    "warehouse_id": warehouse_id,
    "serialized_space": serialized_space,
})

space_id = result.get("space_id") or result.get("id")
print(f"space_id: {space_id}")
print(f"open:     {HOST.rstrip('/')}/genie/rooms/{space_id}")

# COMMAND ----------

# MAGIC %md
# MAGIC Share the `space_id` printed above with attendees at the start of Exercise 4.
