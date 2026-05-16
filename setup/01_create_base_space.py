"""Create the workshop's clean starter Genie space via the Management API.

Used by Exercises 1, 2, and 4. Exercise 3 has its own seed script with
intentionally bloated instructions.

Env vars:
    DATABRICKS_HOST     e.g. https://<workspace>.cloud.databricks.com
    DATABRICKS_TOKEN    a PAT for a user with Genie + warehouse permissions
    DATABRICKS_WAREHOUSE_ID   the SQL warehouse to attach to the space
    DATABRICKS_USERNAME (optional)   defaults to extracting from /api/2.0/preview/scim/v2/Me

Run:
    python setup/01_create_base_space.py
"""

import json
import os
import sys
import urllib.request
import urllib.error

CATALOG = "genie_workshop"
SCHEMA = "insurance_data"
TABLES = ["customers", "branches", "agents", "policies", "claims"]


def env(key: str) -> str:
    val = os.environ.get(key)
    if not val:
        sys.exit(f"Missing env var: {key}")
    return val


def request(method: str, path: str, host: str, token: str, body: dict | None = None) -> dict:
    url = host.rstrip("/") + path
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} {path} failed: {e.code} {e.read().decode('utf-8')}")


def parent_path(host: str, token: str) -> str:
    me = request("GET", "/api/2.0/preview/scim/v2/Me", host, token)
    username = me.get("userName") or os.environ.get("DATABRICKS_USERNAME")
    if not username:
        sys.exit("Could not determine username; set DATABRICKS_USERNAME")
    return f"/Workspace/Users/{username}"


def serialized_space() -> str:
    """A deliberately minimal space: just the 5 tables + the absolute bare minimum
    of instructions. Attendees will add trusted assets / instructions during exercises."""
    config = {
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
    }
    return json.dumps(config)


def main() -> None:
    host = env("DATABRICKS_HOST")
    token = env("DATABRICKS_TOKEN")
    warehouse_id = env("DATABRICKS_WAREHOUSE_ID")

    body = {
        "description": "Thai P&C Insurance — Genie Workshop (base space)",
        "title": "Thai P&C Insurance Workshop",
        "parent_path": parent_path(host, token),
        "warehouse_id": warehouse_id,
        "serialized_space": serialized_space(),
    }

    print(f"Creating base Genie space in {host} ...")
    resp = request("POST", "/api/2.0/genie/spaces", host, token, body)
    space_id = resp.get("space_id") or resp.get("id")
    print(f"  ✓ space_id: {space_id}")
    print(f"  open: {host.rstrip('/')}/genie/rooms/{space_id}")
    print("\nShare this space_id with attendees for Exercises 1, 2, and 4.")


if __name__ == "__main__":
    main()
