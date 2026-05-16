"""Facilitator-only: seed a deliberately broken Genie space for Exercise 3.

This creates a Genie space whose `text_instructions` is a single monster blob —
glossary + table descriptions + SQL fragments + FAQ all crammed together,
well past the per-instruction character cap. Attendees will refactor it.

Run BEFORE the workshop and share the resulting space_id with attendees just
before Exercise 3.

Env vars:
    DATABRICKS_HOST
    DATABRICKS_TOKEN
    DATABRICKS_WAREHOUSE_ID
"""

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

CATALOG = "workspace"
SCHEMA = "insurance_data"
TABLES = ["customers", "branches", "agents", "policies", "claims"]

BLOATED_PATH = Path(__file__).parent / "bloated_instructions.md"


def env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        sys.exit(f"Missing env var: {key}")
    return v


def request(method: str, path: str, host: str, token: str, body: dict | None = None) -> dict:
    url = host.rstrip("/") + path
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
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


def extract_bloated_blob() -> str:
    """Read the bloated text from bloated_instructions.md (everything inside the ``` fence)."""
    text = BLOATED_PATH.read_text(encoding="utf-8")
    start = text.find("```")
    end = text.rfind("```")
    if start == -1 or end == -1 or start == end:
        sys.exit(f"Could not find fenced block in {BLOATED_PATH}")
    blob = text[start + 3:end]
    # Drop optional language tag on first line.
    if "\n" in blob:
        first, rest = blob.split("\n", 1)
        if first.strip().isalpha() or first.strip() == "":
            blob = rest
    return blob.strip()


def serialized_space(bloated: str) -> str:
    config = {
        "version": 1,
        "config": {
            "sample_questions": [
                {"id": "q1", "question": ["What is our loss ratio for motor in 2025?"]},
                {"id": "q2", "question": ["How many in-force policies do we have right now?"]},
            ],
        },
        "data_sources": {
            "tables": [
                {"identifier": f"{CATALOG}.{SCHEMA}.{t}"} for t in TABLES
            ],
        },
        "instructions": {
            "text_instructions": [
                # The monster: a single instruction containing everything.
                {"id": "ti_everything", "content": [bloated]},
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

    bloated = extract_bloated_blob()
    print(f"Bloated instruction size: {len(bloated):,} characters")
    print("(Per-instruction caps are typically a few thousand characters — this is well over.)")

    body = {
        "description": "Thai P&C — Genie Workshop Exercise 3 (BROKEN: oversized instructions, do not use as a reference)",
        "title": "Thai P&C — Ex 3 BROKEN",
        "parent_path": parent_path(host, token),
        "warehouse_id": warehouse_id,
        "serialized_space": serialized_space(bloated),
    }

    print(f"\nCreating broken Genie space in {host} ...")
    resp = request("POST", "/api/2.0/genie/spaces", host, token, body)
    space_id = resp.get("space_id") or resp.get("id")
    print(f"  ✓ space_id: {space_id}")
    print(f"  open: {host.rstrip('/')}/genie/rooms/{space_id}")
    print("\nShare this space_id with attendees at the start of Exercise 3.")


if __name__ == "__main__":
    main()
