-- Exercise 1 — reference solution.

-- Part A: SQL function
CREATE OR REPLACE FUNCTION
  workspace.insurance_data.claims_by_loss_type(
    start_date DATE COMMENT 'Inclusive start of the loss date window',
    end_date DATE COMMENT 'Inclusive end of the loss date window'
  )
  RETURNS TABLE (loss_type STRING, claim_count BIGINT, total_paid_thb BIGINT)
  COMMENT 'Aggregate claims by loss_type for losses occurring between start_date and end_date.'
  RETURN
    SELECT
      loss_type,
      COUNT(*) AS claim_count,
      COALESCE(SUM(CASE WHEN status = 'paid' THEN claim_amount_thb END), 0) AS total_paid_thb
    FROM workspace.insurance_data.claims
    WHERE loss_date BETWEEN start_date AND end_date
    GROUP BY loss_type
    ORDER BY claim_count DESC;

-- Smoke test
SELECT * FROM workspace.insurance_data.claims_by_loss_type(DATE'2025-01-01', DATE'2025-12-31');


-- Part B: parameterized example SQL (paste into the Example SQL panel of the space)
/*
-- Question: Top 5 agents by claim count in :province
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
*/
