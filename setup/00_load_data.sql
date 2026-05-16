-- Bootstrap the Thai P&C Insurance workshop schema.
-- Run in a SQL editor or notebook attached to a Serverless SQL warehouse.
-- Idempotent: safe to re-run; tables are dropped and recreated.

-- 1. Create the workshop catalog and schema. Requires CREATE CATALOG on the metastore.
CREATE CATALOG IF NOT EXISTS genie_workshop
  COMMENT 'Catalog for Genie workshop assets';

USE CATALOG genie_workshop;

CREATE SCHEMA IF NOT EXISTS insurance_data
  COMMENT 'Sample Thai P&C insurance data for the Genie workshop';

USE SCHEMA insurance_data;

-- 2. Stage CSVs in a Volume so COPY INTO can read them.
-- Upload all 5 CSVs from data/ into this volume (UI: Catalog > Volumes > Upload).
-- Or use the CLI: `databricks fs cp data/*.csv dbfs:/Volumes/genie_workshop/insurance_data/raw/`
CREATE VOLUME IF NOT EXISTS raw;

-- 3. Define tables with explicit schemas (don't rely on inference for a workshop).
DROP TABLE IF EXISTS branches;
CREATE TABLE branches (
  branch_id     STRING,
  branch_name   STRING,
  province      STRING,
  region        STRING,
  opened_date   DATE
) COMMENT 'Branch offices across Thailand';

DROP TABLE IF EXISTS agents;
CREATE TABLE agents (
  agent_id          STRING,
  agent_name        STRING,
  license_no        STRING,
  branch_id         STRING,
  hire_date         DATE,
  commission_tier   STRING
) COMMENT 'Licensed agents assigned to branches';

DROP TABLE IF EXISTS customers;
CREATE TABLE customers (
  customer_id     STRING,
  first_name      STRING,
  last_name       STRING,
  dob             DATE,
  gender          STRING,
  occupation      STRING,
  province        STRING,
  phone           STRING,
  email           STRING,
  customer_since  DATE
) COMMENT 'Individual policyholders';

DROP TABLE IF EXISTS policies;
CREATE TABLE policies (
  policy_id            STRING,
  customer_id          STRING,
  agent_id             STRING,
  product_line         STRING COMMENT 'motor or property',
  product_subtype      STRING,
  effective_date       DATE,
  expiry_date          DATE,
  sum_insured_thb      BIGINT COMMENT 'Sum insured in Thai Baht',
  annual_premium_thb   BIGINT COMMENT 'Annual premium in Thai Baht',
  payment_frequency    STRING,
  status               STRING COMMENT 'active, lapsed, or cancelled'
) COMMENT 'Issued insurance policies (motor + property)';

DROP TABLE IF EXISTS claims;
CREATE TABLE claims (
  claim_id           STRING,
  policy_id          STRING,
  loss_date          DATE,
  report_date        DATE,
  settle_date        DATE,
  loss_type          STRING,
  claim_amount_thb   BIGINT COMMENT 'Claimed amount in Thai Baht',
  status             STRING COMMENT 'open, paid, denied, or pending',
  adjuster_name      STRING,
  fraud_flag         BOOLEAN
) COMMENT 'Claims filed against policies, including fraud flags';

-- 4. Load. Adjust the volume path to match where you uploaded the CSVs.
COPY INTO branches
  FROM '/Volumes/genie_workshop/insurance_data/raw/branches.csv'
  FILEFORMAT = CSV
  FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'false');

COPY INTO agents
  FROM '/Volumes/genie_workshop/insurance_data/raw/agents.csv'
  FILEFORMAT = CSV
  FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'false');

COPY INTO customers
  FROM '/Volumes/genie_workshop/insurance_data/raw/customers.csv'
  FILEFORMAT = CSV
  FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'false');

COPY INTO policies
  FROM '/Volumes/genie_workshop/insurance_data/raw/policies.csv'
  FILEFORMAT = CSV
  FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'false');

COPY INTO claims
  FROM '/Volumes/genie_workshop/insurance_data/raw/claims.csv'
  FILEFORMAT = CSV
  FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'false');

-- 5. Sanity check.
SELECT 'branches'  AS table_name, COUNT(*) AS row_count FROM branches
UNION ALL SELECT 'agents',    COUNT(*) FROM agents
UNION ALL SELECT 'customers', COUNT(*) FROM customers
UNION ALL SELECT 'policies',  COUNT(*) FROM policies
UNION ALL SELECT 'claims',    COUNT(*) FROM claims;
-- Expected: 10, 50, 3000, 10000, 5000
