# Investment analysis layer — asset-risk reports MVP

This directory contains the decision-grade layer built on top of the source dossiers and X evidence logs.

## Files

- [Quantitative underwriting methodology](quantitative-underwriting-methodology.md)
  - Defines how to calculate PT ROI/APR, points expected value, expected loss, price-stability certainty, and decision status.

- [Investment analyst report — points and PT risk-adjusted returns](investment-analyst-report-points-pt-risk-return.md)
  - Applies the methodology to apyUSD, apxUSD, USDat, sUSDat, and the four scoped Pendle PT markets.
  - Includes gross returns, points scenarios, expected-loss priors, price-stability scores, risk-adjusted APR, and break-even points ROI.

## Relationship to source artifacts

- `../x-research/` contains social-source evidence and X claim extraction.
- `../reports/` contains underlying token and PT risk reports.
- `../technical-reports/` contains technical evidence and source-grounding detail.
- This directory converts those inputs into investment-decision variables.
