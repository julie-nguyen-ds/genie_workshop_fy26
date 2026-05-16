-- Ground truth for the mandated 6th benchmark question (Ex 1 Part B):
--
--   "Show me total paid claims by loss type for 2025."
--
-- Attendees ask Genie this question in a fresh thread, copy the generated
-- SQL, and verify it against this file before saving as the expected SQL
-- in the Benchmark tab.

-- ============================================================================
-- Things to look out for when comparing Genie's generated SQL to this ground
-- truth (these are the typical differences you'll see):
--
--   1. Genie uses settle_date for filtering; ground truth uses loss_date.
--   2. Genie does not filter for paid claims; ground truth filters for
--      status = 'paid'.
--   3. Genie omits claim_count and only returns total_paid_claims_thb.
--   4. Genie does not use COALESCE or CASE for paid claims sum.
--   5. Genie orders by total_paid_claims_thb; ground truth orders by
--      claim_count.
-- ============================================================================

SELECT
  loss_type,
  COUNT(*) AS claim_count,
  COALESCE(
    SUM(
      CASE
        WHEN status = 'paid' THEN claim_amount_thb
      END
    ),
    0
  ) AS total_paid_thb
FROM
  workspace.insurance_data.claims
WHERE
  loss_date BETWEEN DATE '2025-01-01' AND DATE '2025-12-31'
GROUP BY
  loss_type
ORDER BY
  claim_count DESC;
