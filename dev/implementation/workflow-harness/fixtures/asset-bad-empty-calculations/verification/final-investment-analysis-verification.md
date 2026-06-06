# Final investment-analysis verification

Status: review_required.

## Required file checks
PASS — required root files, per-token files, and skipped PT/social index files exist.

## Per-token and per-PT folder structure
PASS — token folder `tokens/ethereum-good-1111` follows `output-structure.md`; no PT folders are in scope.

## Manifest paths and artifact paths
PASS — `run-manifest.json`, token `artifact_dir`, `final_index`, and `final_verification` resolve inside the run root.

## Cross-link resolution
PASS — local Markdown links in README.md, index.md, investment-analysis/index.md, and this verification file resolve inside the run root.

## Required sections and quantitative fields
REVIEW_REQUIRED — S1 fact slots, S2 sections, and all exact S6 quantitative fields are present, but the skipped fields do not include a non-executable Analyze-only scenario band.

## Skipped-stage checks
PASS — S3_pt_market_economics, S4_x_social_mining, and S5_x_social_synthesis are skipped with explicit reasons.

## Unsupported allocation conclusions
PASS — no source artifact gives an execution-ready or allocation-ready claim.

## Workspace validation
REVIEW_REQUIRED — expected regression finding: `asset.s6.skipped_calculation_requires_analyze_only_scenario_band`.
Command: python3 dev/tools/validate_workflow_run.py --workflow asset-investment-diligence --run-root /Users/ilya/Documents/Codex/front-knowledge-base/dev/implementation/workflow-harness/fixtures/asset-bad-empty-calculations --format json
Exit status: 1

## README and index handoff sections
PASS — README.md and index.md include manifest path, token folder, read-first paths, artifact map, blockers, and final validation status.
