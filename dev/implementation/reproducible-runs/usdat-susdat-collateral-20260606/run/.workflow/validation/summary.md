# Workflow entrypoint validation

Status: pass

## Commands
- asset: exit 0 — `python3 dev/tools/validate_workflow_run.py --workflow asset-investment-diligence --run-root dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/run/asset-investment-diligence --format json,markdown --report-dir dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/run/asset-investment-diligence/verification --write-verification`
- oracle: exit 0 — `python3 dev/tools/validate_workflow_run.py --workflow oracle-analysis --run-root dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/run/oracle-analysis --format json,markdown --report-dir dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/run/oracle-analysis/verification --write-verification`
- combined: exit 0 — `python3 dev/tools/validate_workflow_run.py --workflow combined-analyze-propose --run-root dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/run --parent-return agentic-flow/analyze-and-propose.md --format json,markdown --report-dir dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/run/verification`

## Semantic review

- Enabled: no

## Execution graph

- Status: absent_legacy
- Checked: no
- Path: `dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/run/.workflow/execution-graph.json`
- Schema: absent
- Skipped reason: execution graph file absent; legacy validation path preserved
- Findings: P0=0, P1=0, P2=0, total=0

## Finding counts

- P0: 0
- P1: 0
- P2: 0
- Total: 0
