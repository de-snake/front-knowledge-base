# Asset scenario fallback fixture

## What was analyzed
This synthetic fixture analyzes a GOOD sample asset and demonstrates Analyze-only scenario bands when Preview-specific inputs are missing.

## Manifest
The manifest is `run-manifest.json`.

## Scope folders
- `tokens/ethereum-good-1111`

## Files to read first
Read `index.md`, `investment-analysis/quantitative-underwriting-methodology.md`, `investment-analysis/investment-analyst-report-points-pt-risk-return.md`, and `verification/final-investment-analysis-verification.md` first.

## Final validation status
Status: pass. Required S6 fields are present as `skipped_due_to_missing_input` with a non-executable Analyze-only scenario band, so the fixture must not emit `asset.s6.skipped_calculation_requires_analyze_only_scenario_band`.
