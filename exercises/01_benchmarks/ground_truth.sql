-- Ground truth for the mandated 6th benchmark question (Ex 1 Part B):
--
--   "Show me total paid claims by loss type for 2024."
--
-- Attendees ask Genie this question in a fresh thread, copy the generated
-- SQL, and verify it against this file before saving as the expected SQL
-- in the Benchmark tab.

-- ============================================================================
-- Things to look out for when comparing Genie's generated SQL to this ground
-- truth (these are the typical differences you'll see):
--
--   1. Genie often uses settle_date for filtering; ground truth uses loss_date.
--   2. Genie often omits the status = 'paid' filter; ground truth filters in
--      the WHERE clause so claim_count AND total_paid_thb both describe paid
--      claims only.
--   3. Genie often returns only total_paid_claims_thb; ground truth also
--      returns claim_count.
--   4. Genie often skips COALESCE(..., 0) on the sum; ground truth wraps it
--      defensively.
--   5. Genie orders by total_paid_claims_thb; ground truth orders by
--      claim_count DESC.
-- ============================================================================

SELECT
  loss_type,
  COUNT(*) AS claim_count,
  COALESCE(SUM(claim_amount_thb), 0) AS total_paid_thb
FROM workspace.insurance_data.claims
WHERE loss_date BETWEEN '2024-01-01' AND '2024-12-31'
  AND status = 'paid'
GROUP BY loss_type
ORDER BY claim_count DESC;
