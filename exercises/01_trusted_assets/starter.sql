-- Exercise 1, Part A — your turn.
-- Fill in the function body. The function should:
--   * Accept start_date and end_date (DATE).
--   * Return one row per loss_type with: claim_count, total_paid_thb.
--   * Only consider claims whose loss_date falls inside the window.
--   * Total paid should sum claim_amount_thb only for status = 'paid'.

CREATE OR REPLACE FUNCTION
  main.insurance_data.claims_by_loss_type(
    start_date DATE COMMENT '?',
    end_date DATE COMMENT '?'
  )
  RETURNS TABLE (loss_type STRING, claim_count BIGINT, total_paid_thb BIGINT)
  COMMENT 'TODO: describe what this function does'
  RETURN
    -- TODO: write the SELECT here
    ;

-- Smoke test:
-- SELECT * FROM main.insurance_data.claims_by_loss_type(DATE'2025-01-01', DATE'2025-12-31');
