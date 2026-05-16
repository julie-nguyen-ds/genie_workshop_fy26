-- Exercise 3 — your turn.
--
-- You'll paste two Example SQL queries into the Genie space's right rail.
-- Both filter on loss_date and only sum claims where status = 'paid'.
-- Same query shape, two flavors: one with a hardcoded year, one parametrized.

-- ============================================================================
-- Part A — Non-parametrized Example SQL
-- ============================================================================
-- Question for the Genie dialog:
--   Show me total paid claims by loss type for 2025
--
-- Fill in the SELECT below. Expected shape:
--   - GROUP BY loss_type
--   - claim_count = COUNT(*) of claims in window
--   - total_paid_thb = SUM of claim_amount_thb only for status = 'paid'
--     (use CASE WHEN ... THEN ... and COALESCE so loss types with 0 paid
--      claims still appear with 0 instead of NULL)
--   - Window: loss_date in 2025
--   - ORDER BY claim_count DESC

-- TODO: write your non-parametrized SELECT here
SELECT
  -- ...
;


-- ============================================================================
-- Part B — Parametrized Example SQL
-- ============================================================================
-- Same query shape, but the date range becomes :start_date / :end_date.
-- When attaching, declare :start_date and :end_date as DATE parameters
-- with ISO YYYY-MM-DD sample values (e.g. 2025-01-01).

-- TODO: write your parametrized SELECT here.
-- Hint: WHERE loss_date BETWEEN :start_date AND :end_date
SELECT
  -- ...
;
