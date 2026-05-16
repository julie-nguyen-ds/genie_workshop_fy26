-- Exercise 3 — reference solution.
--
-- Both queries below are intended to be pasted into the Genie space via
-- Right rail → "Example SQL queries" → Add. They are NOT meant to be run
-- standalone (the parametrized one uses :start_date / :end_date placeholders
-- that Genie substitutes at runtime).
--
-- Why Example SQL and not a UC SQL function for this exercise?
-- Genie's "Add functions" dialog currently rejects functions with DATE or
-- TIMESTAMP parameters ("Parameter start_date has an unsupported type: date").
-- Example SQL has no such limitation — DATE params work fine in the
-- parametrized form below.

-- ============================================================================
-- Part A — Non-parametrized Example SQL
-- ============================================================================
-- Question (paste into the "Question" field of the Example SQL dialog):
--   Show me total paid claims by loss type for 2025
SELECT
  loss_type,
  COUNT(*) AS claim_count,
  COALESCE(SUM(CASE WHEN status = 'paid' THEN claim_amount_thb END), 0) AS total_paid_thb
FROM workspace.insurance_data.claims
WHERE loss_date BETWEEN DATE'2025-01-01' AND DATE'2025-12-31'
GROUP BY loss_type
ORDER BY claim_count DESC;


-- ============================================================================
-- Part B — Parametrized Example SQL
-- ============================================================================
-- Question:  Total paid claims by loss type between two dates
-- Parameters:
--   :start_date — DATE, sample 2025-01-01, "Inclusive start of the loss date window. ISO format YYYY-MM-DD."
--   :end_date   — DATE, sample 2025-12-31, "Inclusive end of the loss date window. ISO format YYYY-MM-DD."
SELECT
  loss_type,
  COUNT(*) AS claim_count,
  COALESCE(SUM(CASE WHEN status = 'paid' THEN claim_amount_thb END), 0) AS total_paid_thb
FROM workspace.insurance_data.claims
WHERE loss_date BETWEEN :start_date AND :end_date
GROUP BY loss_type
ORDER BY claim_count DESC;


-- ============================================================================
-- "If you finish early" — parametrized example for top agents by province
-- ============================================================================
-- Question:  Top N agents by claim count in :province
-- Parameters:
--   :province — STRING, sample "Phuket", "Province name to filter branches by."
SELECT
  a.agent_id,
  a.agent_name,
  COUNT(cl.claim_id) AS claim_count
FROM workspace.insurance_data.agents a
JOIN workspace.insurance_data.policies p ON p.agent_id = a.agent_id
JOIN workspace.insurance_data.claims cl  ON cl.policy_id = p.policy_id
JOIN workspace.insurance_data.branches b ON b.branch_id = a.branch_id
WHERE b.province = :province
GROUP BY a.agent_id, a.agent_name
ORDER BY claim_count DESC
LIMIT 5;
