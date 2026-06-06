# Quantitative underwriting methodology

Status: review_required.

This negative fixture proves that an artifact cannot leave quantitative work empty by marking every Preview-dependent field as skipped without a scenario fallback.

## Required S6 quantitative fields
| Field | Value state | Reason |
| --- | --- | --- |
| Gross ROI | skipped_due_to_missing_input | due to missing position size, target leverage, hold horizon, and user risk policy |
| Simple annualized return | skipped_due_to_missing_input | due to missing hold horizon |
| Compound annualized return | skipped_due_to_missing_input | due to missing hold horizon |
| Points EV | skipped_due_to_missing_input | due to missing position size |
| Points ROI | skipped_due_to_missing_input | due to missing position size and target leverage |
| Points annualized return | skipped_due_to_missing_input | due to missing hold horizon |
| Expected loss | skipped_due_to_missing_input | due to missing user risk policy and Health Factor floor |
| Exit cost | skipped_due_to_missing_input | due to missing position size |
| Risk-adjusted ROI | skipped_due_to_missing_input | due to missing user risk policy |
| Risk-adjusted annualized return | skipped_due_to_missing_input | due to missing hold horizon and user risk policy |
| Break-even points ROI | skipped_due_to_missing_input | due to missing target leverage |
| Break-even terminal drawdown | skipped_due_to_missing_input | due to missing user risk policy |
| Price-stability certainty score | skipped_due_to_missing_input | due to missing user risk budget |

## Missing scenario fallback
No scenario band, sensitivity band, or analyze-only scenario matrix is present in this fixture.
