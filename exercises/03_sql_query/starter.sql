-- Exercise 3 — your turn.
--
-- You'll paste two Example SQL queries into the Genie space's right rail.
-- Both filter on loss_date AND status = 'paid' in the WHERE clause.
-- Same query shape, two flavors: one with a hardcoded year, one parametrized.

-- ============================================================================
-- Part A — Non-parametrized Example SQL
-- ============================================================================
-- Question for the Genie dialog:
--   Show me total paid claims by loss type for 2024
--
-- Fill in the SELECT below. Expected shape:
--   - WHERE: loss_date in 2024 AND status = 'paid'
--   - GROUP BY loss_type
--   - claim_count = COUNT(*) of paid claims in window (status filter is in WHERE,
--     so the count and sum both describe paid claims only)
--   - total_paid_thb = COALESCE(SUM(claim_amount_thb), 0)
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
-- with ISO YYYY-MM-DD sample values (e.g. 2024-01-01).
-- Keep status = 'paid' in the WHERE clause.

-- TODO: write your parametrized SELECT here.
-- Hint: WHERE loss_date BETWEEN :start_date AND :end_date AND status = 'paid'
SELECT
  -- ...
;
