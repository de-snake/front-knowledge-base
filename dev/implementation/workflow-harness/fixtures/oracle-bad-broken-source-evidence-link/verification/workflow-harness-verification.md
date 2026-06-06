# Workflow harness verification

- Workflow: oracle-analysis-v1
- Run root: dev/implementation/workflow-harness/fixtures/oracle-good-minimal
- Status: pass
- Generated at: 2026-06-05T20:21:43Z
- Validator command: `dev/tools/validate_workflow_run.py --workflow oracle-analysis --format markdown --run-root dev/implementation/workflow-harness/fixtures/oracle-good-minimal --report-dir /tmp/oracle-validator-reports --write-verification`
- Exit code: 0

## Summary

| Severity | Count |
| --- | ---: |
| P0 | 0 |
| P1 | 0 |
| P2 | 0 |

## Findings

| Severity | Check ID | Path | Message | Fix hint |
| --- | --- | --- | --- | --- |
| - | - | - | No findings. | - |

## Checks run

| Check ID | Result | Path | Message |
| --- | --- | --- | --- |
| cli.input_valid | pass | . | CLI arguments accepted |
| run_root.exists | pass | . | run root exists and is a directory |
| manifest.file_exists | pass | run-manifest.json | run-manifest.json exists |
| manifest.json_valid | pass | run-manifest.json | run-manifest.json parsed successfully |
| oracle.manifest_schema | pass | run-manifest.json | manifest includes required oracle-analysis fields |
| oracle.canonical_final_verification_path | pass | run-manifest.json | canonical final verification path declared |
| oracle.required_files_present | pass | README.md | required root file present: README.md |
| oracle.required_files_present | pass | index.md | required root file present: index.md |
| oracle.required_files_present | pass | verification/final-oracle-analysis-verification.md | required root file present: verification/final-oracle-analysis-verification.md |
| oracle.index_contract_sections | pass | index.md | index.md includes required oracle handoff sections |
| oracle.readme_handoff_sections | pass | README.md | README.md includes required handoff sections |
| oracle.required_files_present | pass | tokens/sample-token-a-11111111/scope.json | required per-scope file present: scope.json |
| oracle.required_files_present | pass | tokens/sample-token-a-11111111/oracle/scope.md | required per-scope file present: oracle/scope.md |
| oracle.required_files_present | pass | tokens/sample-token-a-11111111/oracle/feed-graph.md | required per-scope file present: oracle/feed-graph.md |
| oracle.required_files_present | pass | tokens/sample-token-a-11111111/oracle/node-classification.md | required per-scope file present: oracle/node-classification.md |
| oracle.required_files_present | pass | tokens/sample-token-a-11111111/oracle/source-primitive-audit.md | required per-scope file present: oracle/source-primitive-audit.md |
| oracle.required_files_present | pass | tokens/sample-token-a-11111111/oracle/stress-tradeoff-analysis.md | required per-scope file present: oracle/stress-tradeoff-analysis.md |
| oracle.required_files_present | pass | tokens/sample-token-a-11111111/oracle/protocol-fit-memo.md | required per-scope file present: oracle/protocol-fit-memo.md |
| oracle.required_files_present | pass | tokens/sample-token-a-11111111/raw/feed-probes.json | required per-scope file present: raw/feed-probes.json |
| oracle.required_files_present | pass | tokens/sample-token-a-11111111/verification/oracle-analysis-verification.md | required per-scope file present: verification/oracle-analysis-verification.md |
| oracle.pricing_formula_present | pass | tokens/sample-token-a-11111111 | pricing formula present in feed graph and node classification |
| oracle.source_primitive_audit_present | pass | tokens/sample-token-a-11111111/oracle/source-primitive-audit.md | source primitive audit includes required evidence fields |
| oracle.node_classification_present | pass | tokens/sample-token-a-11111111/oracle/node-classification.md | node classification taxonomy present |
| oracle.stress_tradeoff_fields | pass | tokens/sample-token-a-11111111/oracle/stress-tradeoff-analysis.md | cascade/trap stress branches present |
| oracle.conclusion_quad_present | pass | tokens/sample-token-a-11111111/oracle/protocol-fit-memo.md | side-specific conclusion fields present |
| oracle.gearbox_fields_present | pass | tokens/sample-token-a-11111111/oracle/protocol-fit-memo.md | Gearbox protocol-fit fields present |
| oracle.no_top_level_only_verdict | pass | tokens/sample-token-a-11111111/oracle/protocol-fit-memo.md | verdict reaches child/source primitives |
| oracle.run_status_reconciles | pass | . | oracle-analysis statuses reconcile |

## JSON report

```json
{"checks":[{"id":"cli.input_valid","message":"CLI arguments accepted","path":".","result":"pass","severity":"P0"},{"id":"run_root.exists","message":"run root exists and is a directory","path":".","result":"pass","severity":"P0"},{"id":"manifest.file_exists","message":"run-manifest.json exists","path":"run-manifest.json","result":"pass","severity":"P0"},{"id":"manifest.json_valid","message":"run-manifest.json parsed successfully","path":"run-manifest.json","result":"pass","severity":"P0"},{"id":"oracle.manifest_schema","message":"manifest includes required oracle-analysis fields","path":"run-manifest.json","result":"pass","severity":"P0"},{"id":"oracle.canonical_final_verification_path","message":"canonical final verification path declared","path":"run-manifest.json","result":"pass","severity":"P0"},{"id":"oracle.required_files_present","message":"required root file present: README.md","path":"README.md","result":"pass","severity":"P0"},{"id":"oracle.required_files_present","message":"required root file present: index.md","path":"index.md","result":"pass","severity":"P0"},{"id":"oracle.required_files_present","message":"required root file present: verification/final-oracle-analysis-verification.md","path":"verification/final-oracle-analysis-verification.md","result":"pass","severity":"P0"},{"id":"oracle.index_contract_sections","message":"index.md includes required oracle handoff sections","path":"index.md","result":"pass","severity":"P1"},{"id":"oracle.readme_handoff_sections","message":"README.md includes required handoff sections","path":"README.md","result":"pass","severity":"P1"},{"id":"oracle.required_files_present","message":"required per-scope file present: scope.json","path":"tokens/sample-token-a-11111111/scope.json","result":"pass","severity":"P0"},{"id":"oracle.required_files_present","message":"required per-scope file present: oracle/scope.md","path":"tokens/sample-token-a-11111111/oracle/scope.md","result":"pass","severity":"P0"},{"id":"oracle.required_files_present","message":"required per-scope file present: oracle/feed-graph.md","path":"tokens/sample-token-a-11111111/oracle/feed-graph.md","result":"pass","severity":"P0"},{"id":"oracle.required_files_present","message":"required per-scope file present: oracle/node-classification.md","path":"tokens/sample-token-a-11111111/oracle/node-classification.md","result":"pass","severity":"P0"},{"id":"oracle.required_files_present","message":"required per-scope file present: oracle/source-primitive-audit.md","path":"tokens/sample-token-a-11111111/oracle/source-primitive-audit.md","result":"pass","severity":"P0"},{"id":"oracle.required_files_present","message":"required per-scope file present: oracle/stress-tradeoff-analysis.md","path":"tokens/sample-token-a-11111111/oracle/stress-tradeoff-analysis.md","result":"pass","severity":"P0"},{"id":"oracle.required_files_present","message":"required per-scope file present: oracle/protocol-fit-memo.md","path":"tokens/sample-token-a-11111111/oracle/protocol-fit-memo.md","result":"pass","severity":"P0"},{"id":"oracle.required_files_present","message":"required per-scope file present: raw/feed-probes.json","path":"tokens/sample-token-a-11111111/raw/feed-probes.json","result":"pass","severity":"P0"},{"id":"oracle.required_files_present","message":"required per-scope file present: verification/oracle-analysis-verification.md","path":"tokens/sample-token-a-11111111/verification/oracle-analysis-verification.md","result":"pass","severity":"P0"},{"id":"oracle.pricing_formula_present","message":"pricing formula present in feed graph and node classification","path":"tokens/sample-token-a-11111111","result":"pass","severity":"P1"},{"id":"oracle.source_primitive_audit_present","message":"source primitive audit includes required evidence fields","path":"tokens/sample-token-a-11111111/oracle/source-primitive-audit.md","result":"pass","severity":"P1"},{"id":"oracle.node_classification_present","message":"node classification taxonomy present","path":"tokens/sample-token-a-11111111/oracle/node-classification.md","result":"pass","severity":"P1"},{"id":"oracle.stress_tradeoff_fields","message":"cascade/trap stress branches present","path":"tokens/sample-token-a-11111111/oracle/stress-tradeoff-analysis.md","result":"pass","severity":"P1"},{"id":"oracle.conclusion_quad_present","message":"side-specific conclusion fields present","path":"tokens/sample-token-a-11111111/oracle/protocol-fit-memo.md","result":"pass","severity":"P1"},{"id":"oracle.gearbox_fields_present","message":"Gearbox protocol-fit fields present","path":"tokens/sample-token-a-11111111/oracle/protocol-fit-memo.md","result":"pass","severity":"P1"},{"id":"oracle.no_top_level_only_verdict","message":"verdict reaches child/source primitives","path":"tokens/sample-token-a-11111111/oracle/protocol-fit-memo.md","result":"pass","severity":"P1"},{"id":"oracle.run_status_reconciles","message":"oracle-analysis statuses reconcile","path":".","result":"pass","severity":"P1"}],"exit_code":0,"findings":[],"generated_at":"2026-06-05T20:21:43Z","generated_files":["/private/tmp/oracle-validator-reports/workflow-harness-report.json","/private/tmp/oracle-validator-reports/workflow-harness-verification.md","dev/implementation/workflow-harness/fixtures/oracle-good-minimal/verification/workflow-harness-verification.md"],"inputs":{"final_index":"index.md","final_verification":"verification/final-oracle-analysis-verification.md","manifest":"run-manifest.json","parent_return":null},"rendered_outputs":{},"run_root":"dev/implementation/workflow-harness/fixtures/oracle-good-minimal","schema_version":"workflow-harness-report-v1","status":"pass","summary":{"P0":0,"P1":0,"P2":0,"checks_failed":0,"checks_passed":28,"checks_skipped":0,"declared_paths_checked":0,"files_checked":15,"json_files_parsed":1,"links_checked":0},"workflow":"oracle-analysis-v1"}
```
