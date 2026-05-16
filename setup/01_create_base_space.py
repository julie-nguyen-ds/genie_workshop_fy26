# Databricks notebook source
# MAGIC %md
# MAGIC # Create the Workshop's Base Genie Space
# MAGIC
# MAGIC Creates a minimal starter Genie space wired to the 5 tables in
# MAGIC `workspace.insurance_data`. Attendees iterate on this space across
# MAGIC Exercises 1, 2, and 4. Exercise 3 has its own seed notebook with
# MAGIC intentionally bloated instructions.
# MAGIC
# MAGIC **Run order:** Run `00_load_data` first.
# MAGIC
# MAGIC **Auth:** picked up from the notebook context — no env vars or PAT.
# MAGIC
# MAGIC **Warehouse:** leave the widget blank to auto-pick the first
# MAGIC eligible Pro / Serverless warehouse in the workspace (and create a
# MAGIC small Serverless Pro one if none exists). Paste an ID to override.

# COMMAND ----------

dbutils.widgets.text("warehouse_id", "", "SQL Warehouse ID (blank = auto-pick)")
warehouse_id_override = dbutils.widgets.get("warehouse_id").strip()


CATALOG = "workspace"
SCHEMA = "insurance_data"
TABLES = ["customers", "branches", "agents", "policies", "claims"]

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pull host + token from the notebook context

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
# MAGIC ## Shared API helper

# COMMAND ----------

import json, urllib.request, urllib.error

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
# MAGIC Picks the first eligible Pro / Serverless warehouse already in the
# MAGIC workspace. If none exist, creates a small Serverless Pro warehouse
# MAGIC called "Genie Workshop Starter".

# COMMAND ----------

def is_genie_eligible(w: dict) -> bool:
    if w.get("state") == "DELETED":
        return False
    return bool(w.get("enable_serverless_compute")) or w.get("warehouse_type") == "PRO"

def find_or_create_warehouse() -> str:
    listing = api("GET", "/api/2.0/sql/warehouses")
    warehouses = listing.get("warehouses", [])
    eligible = [w for w in warehouses if is_genie_eligible(w)]
    # Prefer serverless + already running
    eligible.sort(key=lambda w: (
        0 if w.get("enable_serverless_compute") else 1,
        0 if w.get("state") == "RUNNING" else 1,
    ))
    if eligible:
        chosen = eligible[0]
        print(
            f"Using existing warehouse: {chosen['name']} ({chosen['id']}) — "
            f"serverless={chosen.get('enable_serverless_compute')} "
            f"state={chosen.get('state')}"
        )
        return chosen["id"]

    print("No eligible Pro/Serverless warehouse found — creating one.")
    created = api("POST", "/api/2.0/sql/warehouses", {
        "name": "Genie Workshop Starter",
        "cluster_size": "2X-Small",
        "min_num_clusters": 1,
        "max_num_clusters": 1,
        "auto_stop_mins": 10,
        "enable_serverless_compute": True,
        "warehouse_type": "PRO",
    })
    new_id = created.get("id") or created.get("warehouse_id")
    print(f"Created warehouse: {new_id}")
    return new_id

if warehouse_id_override:
    warehouse_id = warehouse_id_override
    print(f"Using warehouse from widget: {warehouse_id}")
else:
    warehouse_id = find_or_create_warehouse()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Build the serialized space
# MAGIC
# MAGIC Deliberately minimal: the 5 tables + the absolute bare-minimum text
# MAGIC instructions. Attendees add trusted assets / instructions during the exercises.

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
        "tables": sorted([
            {
                "identifier": f"{CATALOG}.{SCHEMA}.{t}",
                "description": [f"See table comment in Unity Catalog for {t}."],
            }
            for t in TABLES
        ], key=lambda x: x["identifier"]),
    },
    "instructions": {
        "text_instructions": [
            {"id": "00000000000000000000000000000010", "content": ["All monetary amounts are in Thai Baht (THB). Columns ending in _thb are amounts in THB. Use current_date() when the user says 'today', 'now', or 'current'."]},
        ],
        "example_question_sqls": [
            {
                "id": "00000000000000000000000000000020",
                "question": ["What was our total premium written last month?"],
                "sql": [
                    "SELECT SUM(annual_premium_thb) AS total_premium_written_thb\n",
                    "FROM workspace.insurance_data.policies\n",
                    "WHERE effective_date >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL 1 MONTH)\n",
                    "  AND effective_date < DATE_TRUNC('month', CURRENT_DATE)",
                ],
            },
            {
                "id": "00000000000000000000000000000021",
                "question": ["How many claims do we have in motor by loss type this year?"],
                "sql": [
                    "SELECT c.loss_type, COUNT(*) AS num_claims\n",
                    "FROM workspace.insurance_data.claims c\n",
                    "JOIN workspace.insurance_data.policies p ON c.policy_id = p.policy_id\n",
                    "WHERE p.product_line = 'Motor'\n",
                    "  AND c.loss_date >= DATE_TRUNC('year', CURRENT_DATE)\n",
                    "GROUP BY c.loss_type\n",
                    "ORDER BY num_claims DESC",
                ],
            },
            {
                "id": "00000000000000000000000000000022",
                "question": ["Which branch had the highest claims paid in Q1 2026?"],
                "sql": [
                    "SELECT b.branch_name, SUM(c.claim_amount_thb) AS total_claims_paid_thb\n",
                    "FROM workspace.insurance_data.claims c\n",
                    "JOIN workspace.insurance_data.policies p ON c.policy_id = p.policy_id\n",
                    "JOIN workspace.insurance_data.agents a ON p.agent_id = a.agent_id\n",
                    "JOIN workspace.insurance_data.branches b ON a.branch_id = b.branch_id\n",
                    "WHERE c.status = 'Paid'\n",
                    "  AND c.settle_date >= '2026-01-01'\n",
                    "  AND c.settle_date < '2026-04-01'\n",
                    "GROUP BY b.branch_name\n",
                    "ORDER BY total_claims_paid_thb DESC\n",
                    "LIMIT 1",
                ],
            },
            {
                "id": "00000000000000000000000000000023",
                "question": ["Show me the top 10 agents by policies sold."],
                "sql": [
                    "SELECT a.agent_name, COUNT(*) AS policies_sold\n",
                    "FROM workspace.insurance_data.policies p\n",
                    "JOIN workspace.insurance_data.agents a ON p.agent_id = a.agent_id\n",
                    "GROUP BY a.agent_name\n",
                    "ORDER BY policies_sold DESC\n",
                    "LIMIT 10",
                ],
            },
        ],
        "join_specs": [],
        "sql_snippets": {"filters": [], "expressions": [], "measures": []},
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
print(f"space_id:    {space_id}")
print(f"warehouse:   {warehouse_id}")
print(f"open:        {HOST.rstrip('/')}/genie/rooms/{space_id}")

# COMMAND ----------

# MAGIC %md
# MAGIC Share the `space_id` printed above with attendees for Exercises 1, 2, and 4.

