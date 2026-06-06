# Final oracle analysis verification

Final status: pass.

Required root files checked: README.md, run-manifest.json, index.md, and verification/final-oracle-analysis-verification.md.
Required per-scope files checked for every scope: scope.json, oracle files, raw/feed-probes.json, raw/source-evidence, and per-scope verification.
Manifest paths checked: declared artifact paths, final_index, and canonical final verification path.
Canonical final verification path: verification/final-oracle-analysis-verification.md.
Status reconciliation checked across root/scope/index/final artifacts.
index.md and README.md sections checked for handoff completeness.
Source primitive audit checked for identity, type, timestamp/cadence, trust/methodology, raw evidence pointer, and primitive-specific evidence.
Node classification checked for market / fundamental / NAV / hardcoded / hybrid terms.
Pricing formula presence checked directly in feed-graph.md and node-classification.md.
Staleness, bounds, timestamps, and delayed update evidence checked.
Protocol-fit fields checked for Gearbox formal fields.
Side-specific conclusion fields checked for position_side, token_role, stress_direction, and loss_bearer.
Gearbox parsing reference applied: user/references/workflows/oracle-analysis/gearbox-price-feed-parsing.md.
Terminology and diff validation evidence recorded.

Working directory: /Users/ilya/Documents/Codex/front-knowledge-base
Command: python3 dev/tools/validate_workflow_run.py --workflow oracle-analysis --run-root dev/implementation/workflow-harness/fixtures/oracle-bad-broken-source-evidence-link --format json
Exit code: 0
Output marker: oracle fixture validation pass.
