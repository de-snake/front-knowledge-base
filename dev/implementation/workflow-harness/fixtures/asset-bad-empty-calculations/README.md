# Asset empty calculations fixture

## What was analyzed
This synthetic negative fixture analyzes a GOOD sample asset and demonstrates that skipped quantitative fields still require an Analyze-only scenario fallback.

## Manifest
The manifest is `run-manifest.json`.

## Scope folders
- `tokens/ethereum-good-1111`

## Files to read first
Read `index.md`, `investment-analysis/quantitative-underwriting-methodology.md`, `investment-analysis/investment-analyst-report-points-pt-risk-return.md`, and `verification/final-investment-analysis-verification.md` first.

## Final validation status
Status: review_required. This fixture should emit `asset.s6.skipped_calculation_requires_analyze_only_scenario_band`.
