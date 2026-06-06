# Quantitative underwriting methodology

Status: pass.

This synthetic Analyze-only fixture uses non-executable scenario bands when Preview-specific inputs are missing. It proves that missing position size, target leverage, hold horizon, and user risk policy do not justify an empty calculation artifact.

## Required S6 quantitative fields
| Field | Value state | Reason |
| --- | --- | --- |
| Gross ROI | skipped_due_to_missing_input | missing position size and target leverage; see non-executable scenario band below |
| Simple annualized return | skipped_due_to_missing_input | missing hold horizon; see non-executable scenario band below |
| Compound annualized return | skipped_due_to_missing_input | missing hold horizon; see non-executable scenario band below |
| Points EV | skipped_due_to_missing_input | missing position size; see non-executable scenario band below |
| Points ROI | skipped_due_to_missing_input | missing position size and target leverage; see non-executable scenario band below |
| Points annualized return | skipped_due_to_missing_input | missing hold horizon; see non-executable scenario band below |
| Expected loss | skipped_due_to_missing_input | missing user risk policy and Health Factor floor; see non-executable scenario band below |
| Exit cost | skipped_due_to_missing_input | missing position size; see non-executable scenario band below |
| Risk-adjusted ROI | skipped_due_to_missing_input | missing user risk policy; see non-executable scenario band below |
| Risk-adjusted annualized return | skipped_due_to_missing_input | missing hold horizon and user risk policy; see non-executable scenario band below |
| Break-even points ROI | skipped_due_to_missing_input | missing target leverage; see non-executable scenario band below |
| Break-even terminal drawdown | skipped_due_to_missing_input | missing user risk policy; see non-executable scenario band below |
| Price-stability certainty score | skipped_due_to_missing_input | missing user risk budget; see non-executable scenario band below |

## Analyze-only scenario band
These scenario bands are non-executable and analysis-only. They preserve quantitative usefulness without pretending that Preview-specific sizing inputs exist.

| Scenario band | Notional | Target leverage | Hold horizon | Points ROI | Expected loss | Risk-adjusted ROI |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Conservative | $10,000 | 1.0x | 30 days | 0.40% | 0.20% | 0.20% |
| Base | $25,000 | 1.5x | 60 days | 0.75% | 0.30% | 0.45% |
| Upside | $50,000 | 2.0x | 90 days | 1.20% | 0.40% | 0.80% |

## Decision effect
Use these bands only to decide whether more user inputs are worth requesting. Do not treat any band as allocation sizing, Preview readiness, or execution approval.
