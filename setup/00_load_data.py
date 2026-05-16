# Databricks notebook source
# MAGIC %md
# MAGIC # Bootstrap the Thai P&C Insurance Workshop Data
# MAGIC
# MAGIC Loads the 5 sample CSVs from `../data/` directly into Delta tables under
# MAGIC `workspace.insurance_data`. No Volume / UC external location required —
# MAGIC reads CSVs from the workspace files alongside this notebook.
# MAGIC
# MAGIC Idempotent: safe to re-run. Tables are overwritten.

# COMMAND ----------

CATALOG = "workspace"
SCHEMA = "insurance_data"

spark.sql(f"USE CATALOG {CATALOG}")
spark.sql(
    f"CREATE SCHEMA IF NOT EXISTS {SCHEMA} "
    "COMMENT 'Sample Thai P&C insurance data for the Genie workshop'"
)
spark.sql(f"USE SCHEMA {SCHEMA}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Locate the `data/` folder relative to this notebook

# COMMAND ----------

import os

notebook_path = (
    dbutils.notebook.entry_point.getDbutils()
    .notebook().getContext().notebookPath().get()
)
data_dir = os.path.normpath(f"/Workspace{os.path.dirname(notebook_path)}/../data")
assert os.path.isdir(data_dir), f"Data folder not found: {data_dir}"

print("Loading CSVs from:", data_dir)
print("Files present:   ", sorted(os.listdir(data_dir)))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Explicit schemas and table comments

# COMMAND ----------

from pyspark.sql.types import (
    StructType, StructField, StringType, DateType, LongType, BooleanType,
)

schemas = {
    "branches": StructType([
        StructField("branch_id",    StringType()),
        StructField("branch_name",  StringType()),
        StructField("province",     StringType()),
        StructField("region",       StringType()),
        StructField("opened_date",  DateType()),
    ]),
    "agents": StructType([
        StructField("agent_id",         StringType()),
        StructField("agent_name",       StringType()),
        StructField("license_no",       StringType()),
        StructField("branch_id",        StringType()),
        StructField("hire_date",        DateType()),
        StructField("commission_tier",  StringType()),
    ]),
    "customers": StructType([
        StructField("customer_id",     StringType()),
        StructField("first_name",      StringType()),
        StructField("last_name",       StringType()),
        StructField("dob",             DateType()),
        StructField("gender",          StringType()),
        StructField("occupation",      StringType()),
        StructField("province",        StringType()),
        StructField("phone",           StringType()),
        StructField("email",           StringType()),
        StructField("customer_since",  DateType()),
    ]),
    "policies": StructType([
        StructField("policy_id",           StringType()),
        StructField("customer_id",         StringType()),
        StructField("agent_id",            StringType()),
        StructField("product_line",        StringType()),
        StructField("product_subtype",     StringType()),
        StructField("effective_date",      DateType()),
        StructField("expiry_date",         DateType()),
        StructField("sum_insured_thb",     LongType()),
        StructField("annual_premium_thb",  LongType()),
        StructField("payment_frequency",   StringType()),
        StructField("status",              StringType()),
    ]),
    "claims": StructType([
        StructField("claim_id",          StringType()),
        StructField("policy_id",         StringType()),
        StructField("loss_date",         DateType()),
        StructField("report_date",       DateType()),
        StructField("settle_date",       DateType()),
        StructField("loss_type",         StringType()),
        StructField("claim_amount_thb", LongType()),
        StructField("status",            StringType()),
        StructField("adjuster_name",     StringType()),
        StructField("fraud_flag",        BooleanType()),
    ]),
}

table_comments = {
    "branches":  "Branch offices across Thailand",
    "agents":    "Licensed agents assigned to branches",
    "customers": "Individual policyholders",
    "policies":  "Issued insurance policies (motor + property)",
    "claims":    "Claims filed against policies, including fraud flags",
}

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load each CSV into a Delta table

# COMMAND ----------

for table, schema in schemas.items():
    csv_path = f"file:{data_dir}/{table}.csv"
    df = (
        spark.read
        .option("header", "true")
        .schema(schema)
        .csv(csv_path)
    )
    (
        df.write
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(f"{CATALOG}.{SCHEMA}.{table}")
    )
    comment = table_comments[table].replace("'", "''")
    spark.sql(
        f"COMMENT ON TABLE {CATALOG}.{SCHEMA}.{table} IS '{comment}'"
    )
    print(f"  loaded {table}: {df.count():>6} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Sanity check — expected counts: 10, 50, 3000, 10000, 5000

# COMMAND ----------

display(spark.sql(f"""
SELECT 'branches'  AS table_name, COUNT(*) AS row_count FROM {CATALOG}.{SCHEMA}.branches
UNION ALL SELECT 'agents',    COUNT(*) FROM {CATALOG}.{SCHEMA}.agents
UNION ALL SELECT 'customers', COUNT(*) FROM {CATALOG}.{SCHEMA}.customers
UNION ALL SELECT 'policies',  COUNT(*) FROM {CATALOG}.{SCHEMA}.policies
UNION ALL SELECT 'claims',    COUNT(*) FROM {CATALOG}.{SCHEMA}.claims
"""))
