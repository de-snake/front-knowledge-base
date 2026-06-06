# Safe parallelization dry-run report

Verdict: compatible. The graph-enabled scaffold/validate path preserves the baseline verification outcome for both sample entrypoint fixtures. Rollout is not blocked by these dry runs.

The expected validation result for newly scaffolded, unfilled runs is still `blocked` / exit `2`: the deterministic validators correctly fail because stage artifacts are placeholders or absent. The important compatibility check is that graph metadata does not change scaffold exit codes, validation exit codes, validation status, validator status tuple, or finding counts.

## Scope and baseline method

- Summary artifact: `dev/implementation/workflow-harness/tmp/safe-parallelization-dry-runs/20260606T162440Z-2/dry-run-summary.json`.
- Dry-run root directory: `dev/implementation/workflow-harness/tmp/safe-parallelization-dry-runs/20260606T162440Z-2`.
- Baseline source of truth: `dev/implementation/workflow-harness/safe-parallelization-baseline.md`.
- Baseline replay method: scaffold with the current runner, then remove persisted `plan.execution_graph` and `.workflow/execution-graph.json` before validation. This exercises the legacy graph-absent verification path with the same deterministic validators and run-root layout. It is not claimed to be an old-code checkout.
- Graph-enabled method: scaffold and validate with the current `dev/tools/run_workflow.py` runner and persisted execution graph metadata intact.

## Result matrix

| Fixture | Variant | Run root | Scaffold exit | Validate exit | Validation status | Finding counts | Validator statuses | Graph/next-action surface | Worker-like commands |
| --- | --- | --- | ---: | ---: | --- | --- | --- | --- | ---: |
| minimal | baseline / legacy graph-absent | `dev/implementation/workflow-harness/tmp/safe-parallelization-dry-runs/20260606T162440Z-2/minimal-baseline_legacy_graph_absent` | 0 | 2 | blocked | P0=28, P1=152, P2=1, total=181 | asset=fail (exit 2); oracle=fail (exit 2); combined=fail (exit 2) | graph_tasks=0; ready=0; blocked=0; waves=0 | 0 |
| minimal | graph-enabled | `dev/implementation/workflow-harness/tmp/safe-parallelization-dry-runs/20260606T162440Z-2/minimal-graph_enabled` | 0 | 2 | blocked | P0=28, P1=152, P2=1, total=181 | asset=fail (exit 2); oracle=fail (exit 2); combined=fail (exit 2) | graph_tasks=20; ready=1; blocked=19; waves=1 | 0 |
| complete | baseline / legacy graph-absent | `dev/implementation/workflow-harness/tmp/safe-parallelization-dry-runs/20260606T162440Z-2/complete-baseline_legacy_graph_absent` | 0 | 2 | blocked | P0=28, P1=152, P2=1, total=181 | asset=fail (exit 2); oracle=fail (exit 2); combined=fail (exit 2) | graph_tasks=0; ready=0; blocked=0; waves=0 | 0 |
| complete | graph-enabled | `dev/implementation/workflow-harness/tmp/safe-parallelization-dry-runs/20260606T162440Z-2/complete-graph_enabled` | 0 | 2 | blocked | P0=28, P1=152, P2=1, total=181 | asset=fail (exit 2); oracle=fail (exit 2); combined=fail (exit 2) | graph_tasks=20; ready=2; blocked=18; waves=1 | 0 |

Compatibility notes:

- Minimal fixture: scaffold exits match (`0`), validate exits match (`2`), validation status matches (`blocked`), finding counts match (`P0=28, P1=152, P2=1, total=181`), and validator status tuple matches (`asset/oracle/combined = fail exit 2`).
- Complete fixture: scaffold exits match (`0`), validate exits match (`2`), validation status matches (`blocked`), finding counts match (`P0=28, P1=152, P2=1, total=181`), and validator status tuple matches (`asset/oracle/combined = fail exit 2`).
- Report paths differ only because each variant uses a distinct run root.

## Exact command lines

### minimal

#### baseline / legacy graph-absent

```bash
python3 dev/tools/run_workflow.py analyze-propose --input dev/implementation/workflow-harness/fixtures/entrypoint-inputs/sample-assets-minimal.json --run-root dev/implementation/workflow-harness/tmp/safe-parallelization-dry-runs/20260606T162440Z-2/minimal-baseline_legacy_graph_absent --mode scaffold --agent generic --format json
# exit 0
python3 dev/tools/run_workflow.py analyze-propose --input dev/implementation/workflow-harness/fixtures/entrypoint-inputs/sample-assets-minimal.json --run-root dev/implementation/workflow-harness/tmp/safe-parallelization-dry-runs/20260606T162440Z-2/minimal-baseline_legacy_graph_absent --mode validate --resume --format json
# exit 2
```

#### graph-enabled

```bash
python3 dev/tools/run_workflow.py analyze-propose --input dev/implementation/workflow-harness/fixtures/entrypoint-inputs/sample-assets-minimal.json --run-root dev/implementation/workflow-harness/tmp/safe-parallelization-dry-runs/20260606T162440Z-2/minimal-graph_enabled --mode scaffold --agent generic --format json
# exit 0
python3 dev/tools/run_workflow.py analyze-propose --input dev/implementation/workflow-harness/fixtures/entrypoint-inputs/sample-assets-minimal.json --run-root dev/implementation/workflow-harness/tmp/safe-parallelization-dry-runs/20260606T162440Z-2/minimal-graph_enabled --mode validate --resume --format json
# exit 2
```

### complete

#### baseline / legacy graph-absent

```bash
python3 dev/tools/run_workflow.py analyze-propose --input dev/implementation/workflow-harness/fixtures/entrypoint-inputs/sample-assets-complete.json --run-root dev/implementation/workflow-harness/tmp/safe-parallelization-dry-runs/20260606T162440Z-2/complete-baseline_legacy_graph_absent --mode scaffold --agent generic --format json
# exit 0
python3 dev/tools/run_workflow.py analyze-propose --input dev/implementation/workflow-harness/fixtures/entrypoint-inputs/sample-assets-complete.json --run-root dev/implementation/workflow-harness/tmp/safe-parallelization-dry-runs/20260606T162440Z-2/complete-baseline_legacy_graph_absent --mode validate --resume --format json
# exit 2
```

#### graph-enabled

```bash
python3 dev/tools/run_workflow.py analyze-propose --input dev/implementation/workflow-harness/fixtures/entrypoint-inputs/sample-assets-complete.json --run-root dev/implementation/workflow-harness/tmp/safe-parallelization-dry-runs/20260606T162440Z-2/complete-graph_enabled --mode scaffold --agent generic --format json
# exit 0
python3 dev/tools/run_workflow.py analyze-propose --input dev/implementation/workflow-harness/fixtures/entrypoint-inputs/sample-assets-complete.json --run-root dev/implementation/workflow-harness/tmp/safe-parallelization-dry-runs/20260606T162440Z-2/complete-graph_enabled --mode validate --resume --format json
# exit 2
```

## Validator command records and no worker launch evidence

Each validate run recorded exactly three child commands, all deterministic validator invocations:

- `python3 dev/tools/validate_workflow_run.py --workflow asset-investment-diligence ...`
- `python3 dev/tools/validate_workflow_run.py --workflow oracle-analysis ...`
- `python3 dev/tools/validate_workflow_run.py --workflow combined-analyze-propose ...`

No recorded command contains `delegate_task`, `kanban`, `worker`, `subagent`, or `hermes`; `worker_like_command_records` is empty for all four dry runs. The scaffold runs do not record validator commands and the graph-enabled next-action text remains advisory-only: ready packets may be worked by a graph-aware agent, but the harness itself performs no scheduling, worker launch, subagent call, or orchestration.

## Next-action surface diffs

### minimal

- Baseline graph-absent counts: ready=0, blocked=0, waves=0.
- Graph-enabled counts: ready=1, blocked=19, waves=1.
- Reduced diff, omitting run-root-specific fields and truncating long blocked packet lists:

```diff
--- baseline
+++ graph
@@ -1,17 +1,75 @@
 {
-  "blocked_packets": [],
+  "blocked_packets": [
+    "asset-S1_general_asset_mining-eth-mainnet-sample-base-token",
+    "asset-S2_asset_risk_analyst_report-eth-mainnet-sample-base-token",
+    "asset-S2_asset_risk_analyst_report-eth-mainnet-sample-vault-token",
+    "asset-S6_quantitative_underwriting-run",
+    "asset-S7_final_verification-run",
+    "... 14 more"
+  ],
   "first_packet": {
-    "artifact_write_scope": {},
-    "delegate_to_subagent": false,
+    "artifact_write_scope": {
+      "mode": "exclusive_prefixes",
+      "read_roots": [
+        "asset-investment-diligence/tokens/eth-mainnet-sample-base-token/scope.json"
+      ],
+      "required_outputs": [
+        "asset-investment-diligence/tokens/eth-mainnet-sample-base-token/research/onchain-admin.md",
+        "asset-investment-diligence/tokens/eth-mainnet-sample-base-token/research/issuer-backing-security.md",
+        "asset-investment-diligence/tokens/eth-mainnet-sample-base-token/research/transfer-liquidity-oracle-governance.md",
+        "asset-investment-diligence/tokens/eth-mainnet-sample-base-token/technical-report.md"
+      ],
+      "shared_write_roots": [],
+      "write_roots": [
+        "asset-investment-diligence/tokens/eth-mainnet-sample-base-token"
+      ]
+    },
+    "delegate_to_subagent": true,
     "json": ".workflow/packets/asset/asset-S1_general_asset_mining-eth-mainnet-sample-base-token.json",
     "markdown": ".workflow/packets/asset/asset-S1_general_asset_mining-eth-mainnet-sample-base-token.md",
-    "recommended_max_concurrent": 1,
-    "return_contract": null,
-    "subagent_prompt_reference": null,
+    "recommended_max_concurrent": 3,
+    "return_contract": {
+      "artifact_layout_return_contract": "Return run_artifact_root, run-manifest.json, index.md, per-token directories, per-PT directories, and final verification path. Do not return loose report paths or raw evidence dumps.",
+      "artifact_paths": [
+        "tokens/eth-mainnet-sample-base-token/research/onchain-admin.md",
+        "tokens/eth-mainnet-sample-base-token/research/issuer-backing-security.md",
+        "tokens/eth-mainnet-sample-base-token/research/transfer-liquidity-oracle-governance.md",
+        "tokens/eth-mainnet-sample-base-token/technical-report.md"
+      ],
+      "contract_id": "stage-worker-compressed-handoff-v1",
+      "parent_verification_required": true,
+      "reference": {
+        "path": "user/references/workflows/asset-investment-diligence/subagent-prompts.md",
+        "section": "Shared stage-worker return contract"
+      },
+      "required_fields": [
+        "status",
+        "artifact_paths",
+        "validation_status",
+        "blockers",
+        "commands_run"
+      ],
+      "worker_self_report_is_advisory": true
+    },
+    "subagent_prompt_reference": {
+      "path": "user/references/workflows/asset-investment-diligence/subagent-prompts.md",
+      "return_contract_section": "Shared stage-worker return contract",
+      "section": "S1 prompt \u2014 General asset mining"
+    },
     "task_id": "asset-S1_general_asset_mining-eth-mainnet-sample-base-token"
   },
-  "parallel_waves": [],
-  "ready_packets": [],
+  "parallel_waves": [
+    {
+      "packet_task_ids": [
+        "asset-S1_general_asset_mining-eth-mainnet-sample-vault-token"
+      ],
+      "recommended_max_concurrent": 1,
+      "wave_id": "ready-wave-1"
+    }
+  ],
+  "ready_packets": [
+    "asset-S1_general_asset_mining-eth-mainnet-sample-vault-token"
+  ],
   "reason": "Validation found blocking findings; fill the listed artifacts or missing inputs before proceeding.",
   "schema_version": "workflow-entrypoint-next-action-v1",
   "status": "blocked"
```

### complete

- Baseline graph-absent counts: ready=0, blocked=0, waves=0.
- Graph-enabled counts: ready=2, blocked=18, waves=1.
- Reduced diff, omitting run-root-specific fields and truncating long blocked packet lists:

```diff
--- baseline
+++ graph
@@ -1,17 +1,77 @@
 {
-  "blocked_packets": [],
+  "blocked_packets": [
+    "asset-S2_asset_risk_analyst_report-eth-mainnet-sample-base-token",
+    "asset-S2_asset_risk_analyst_report-eth-mainnet-sample-vault-token",
+    "asset-S6_quantitative_underwriting-run",
+    "asset-S7_final_verification-run",
+    "oracle-S0_scope_and_acceptance-eth-mainnet-sample-base-token-gearbox-oracle",
+    "... 13 more"
+  ],
   "first_packet": {
-    "artifact_write_scope": {},
-    "delegate_to_subagent": false,
+    "artifact_write_scope": {
+      "mode": "exclusive_prefixes",
+      "read_roots": [
+        "asset-investment-diligence/tokens/eth-mainnet-sample-base-token/scope.json"
+      ],
+      "required_outputs": [
+        "asset-investment-diligence/tokens/eth-mainnet-sample-base-token/research/onchain-admin.md",
+        "asset-investment-diligence/tokens/eth-mainnet-sample-base-token/research/issuer-backing-security.md",
+        "asset-investment-diligence/tokens/eth-mainnet-sample-base-token/research/transfer-liquidity-oracle-governance.md",
+        "asset-investment-diligence/tokens/eth-mainnet-sample-base-token/technical-report.md"
+      ],
+      "shared_write_roots": [],
+      "write_roots": [
+        "asset-investment-diligence/tokens/eth-mainnet-sample-base-token"
+      ]
+    },
+    "delegate_to_subagent": true,
     "json": ".workflow/packets/asset/asset-S1_general_asset_mining-eth-mainnet-sample-base-token.json",
     "markdown": ".workflow/packets/asset/asset-S1_general_asset_mining-eth-mainnet-sample-base-token.md",
-    "recommended_max_concurrent": 1,
-    "return_contract": null,
-    "subagent_prompt_reference": null,
+    "recommended_max_concurrent": 3,
+    "return_contract": {
+      "artifact_layout_return_contract": "Return run_artifact_root, run-manifest.json, index.md, per-token directories, per-PT directories, and final verification path. Do not return loose report paths or raw evidence dumps.",
+      "artifact_paths": [
+        "tokens/eth-mainnet-sample-base-token/research/onchain-admin.md",
+        "tokens/eth-mainnet-sample-base-token/research/issuer-backing-security.md",
+        "tokens/eth-mainnet-sample-base-token/research/transfer-liquidity-oracle-governance.md",
+        "tokens/eth-mainnet-sample-base-token/technical-report.md"
+      ],
+      "contract_id": "stage-worker-compressed-handoff-v1",
+      "parent_verification_required": true,
+      "reference": {
+        "path": "user/references/workflows/asset-investment-diligence/subagent-prompts.md",
+        "section": "Shared stage-worker return contract"
+      },
+      "required_fields": [
+        "status",
+        "artifact_paths",
+        "validation_status",
+        "blockers",
+        "commands_run"
+      ],
+      "worker_self_report_is_advisory": true
+    },
+    "subagent_prompt_reference": {
+      "path": "user/references/workflows/asset-investment-diligence/subagent-prompts.md",
+      "return_contract_section": "Shared stage-worker return contract",
+      "section": "S1 prompt \u2014 General asset mining"
+    },
     "task_id": "asset-S1_general_asset_mining-eth-mainnet-sample-base-token"
   },
-  "parallel_waves": [],
-  "ready_packets": [],
+  "parallel_waves": [
+    {
+      "packet_task_ids": [
+        "asset-S1_general_asset_mining-eth-mainnet-sample-base-token",
+        "asset-S1_general_asset_mining-eth-mainnet-sample-vault-token"
+      ],
+      "recommended_max_concurrent": 2,
+      "wave_id": "ready-wave-1"
+    }
+  ],
+  "ready_packets": [
+    "asset-S1_general_asset_mining-eth-mainnet-sample-base-token",
+    "asset-S1_general_asset_mining-eth-mainnet-sample-vault-token"
+  ],
   "reason": "Validation found blocking findings; fill the listed artifacts or missing inputs before proceeding.",
   "schema_version": "workflow-entrypoint-next-action-v1",
   "status": "blocked"
```

## Packet surface diffs

### minimal

- First packet top-level keys match: True.
- First packet packet_metadata keys match: True.
- First packet task_payload keys match: True.
- Raw first-packet JSON diffs:
  - `/task_payload/run_root` differs only by variant run root.
  - `/task_payload/validation_command` differs only by variant run root.
  - `/task_payload_sha256` changes because the run-root-specific payload changes.

### complete

- First packet top-level keys match: True.
- First packet packet_metadata keys match: True.
- First packet task_payload keys match: True.
- Raw first-packet JSON diffs:
  - `/task_payload/run_root` differs only by variant run root.
  - `/task_payload/validation_command` differs only by variant run root.
  - `/task_payload_sha256` changes because the run-root-specific payload changes.

Interpretation: the generated first packet JSON surface remains stable except for run-root-dependent paths and the derived payload hash. The graph-enabled next-action surface adds advisory graph metadata (`ready_packets`, `blocked_packets`, `parallel_waves`, first-packet delegation prompt/reference/scope), but does not change deterministic validation behavior.

## Regression suite replay

Quality-gates fixtures are present via `dev/implementation/workflow-harness/QUALITY_GATES_KANBAN.md` and `dev/implementation/workflow-harness/fixtures/regression-evals/quality-gate-regression-suite.json`. Replay results:

```bash
python3 dev/tools/run_fixture_checks.py
# exit 0
# Ran 20 tests in 3.001s; OK
# fixture matrix: ran 13, failures 0
# evidence ledger schema: ran 5, failures 0
# semantic critic runner: ran 3, failures 0
# regression eval suite: ran 4, failures 0
# workflow entrypoint: exit 0

python3 -m pytest dev/tools/workflow_harness/tests -q
# exit 1: /usr/bin/python3 has no module named pytest

/opt/anaconda3/bin/python -m pytest dev/tools/workflow_harness/tests -q
# exit 0
# 45 passed, 2 subtests passed in 6.58s
```

## Rollout decision

No concrete regression was found. The graph-enabled metadata is additive/advisory for the dry-run surfaces, the graph-absent validation path remains compatible, deterministic validator results match, old `first_packet` / registry-order consumers remain supported, and no subagent/worker launch was observed.

This report is rollout evidence, not an automatic production switch. Production enablement still requires the gated checklist in `dev/implementation/workflow-harness/SAFE_PARALLELIZATION_KANBAN.md`: all fixture and pytest checks pass in the implementation environment, this dry-run report is accepted, there are no validator regressions, no automatic subagent orchestration exists, and legacy `first_packet` consumers remain supported.

Rollback remains data-only. Ignore or delete `.workflow/execution-graph.json`, ignore graph-only next-action fields such as `ready_packets`, `blocked_packets`, and `parallel_waves`, and fall back to `.workflow/next-action.json.first_packet` plus `.workflow/registry.json` serial order.
