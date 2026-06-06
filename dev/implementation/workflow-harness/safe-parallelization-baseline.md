# Safe parallelization baseline

M0 objective: freeze the currently working `Analyze -> Propose` verification flow before any safe-parallelization work changes generated metadata, packet routing, validator behavior, or rollout gates.

This is a baseline and non-regression contract only. It does not implement an execution graph, ready-packet waves, scheduling, delegation, or subagent launch.

## Grounded source files

Baseline source of truth:

- `dev/tools/workflow_entrypoint.py`
- `dev/tools/workflow_entrypoint_contracts.py`
- `dev/tools/validate_workflow_run.py`
- `dev/tools/run_workflow.py`
- `dev/implementation/workflow-entrypoint/run-workflow-usage.md`
- `dev/tools/workflow_harness/tests/*`
- `dev/implementation/workflow-harness/fixtures/fixture-matrix.json`
- `dev/implementation/workflow-harness/fixtures/regression-evals/quality-gate-regression-suite.json`
- `dev/implementation/workflow-harness/contracts/evidence-ledger.schema.json`

A sample scaffold of `dev/implementation/workflow-harness/fixtures/entrypoint-inputs/sample-assets-complete.json` currently creates 20 serial stage packets. The generated plan task keys are limited to:

```text
artifact_dir, blocking_unknowns, child_run_root, input_paths, packet_json,
packet_markdown, required_outputs, scenario_analysis_forbidden, scope_id,
scope_slug, scope_type, stage_id, stage_title, task_id, validation_command,
workflow_id, workflow_key
```

There are no current plan task keys for `depends_on_task_ids`, `parallel_group_id`, `parallel_unit`, `delegate_to_subagent`, `recommended_max_concurrent`, `subagent_prompt_path`, or `artifact_write_scope`.

## Current generated artifact contract

The supported entrypoint remains:

```bash
python3 dev/tools/run_workflow.py analyze-propose \
  --input <repo-local-input.json> \
  --mode scaffold \
  --agent generic \
  --format markdown
```

The command may receive `--run-root` under `dev/implementation/`; otherwise it creates a deterministic parent run root under `dev/implementation/`. The runner is a scaffold and validation bridge only. It does not perform live research, infer suitability, infer oracle correctness, unlock Preview, unlock Execute, launch agents, or launch subagents.

The parent run root currently includes these baseline files:

```text
README.md
index.md
run-manifest.json
agentic-flow/analyze-and-propose.md
.workflow/input.normalized.json
.workflow/plan.json
.workflow/tasks.json
.workflow/registry.json
.workflow/agent-handoff.md
.workflow/next-action.json
.workflow/next-action.md
```

The parent run root also includes `.workflow/packets/<workflow>/<task>.json` and `.workflow/packets/<workflow>/<task>.md` for each generated stage packet.

The scaffold creates two child run roots:

```text
asset-investment-diligence/
oracle-analysis/
```

Each child root has its own `run-manifest.json`, `scope.json` files where applicable, stage output placeholders, final index/verification placeholders, and a validator command pointing back to `dev/tools/validate_workflow_run.py`.

Validate mode writes the bridge outputs under:

```text
.workflow/validation/summary.json
.workflow/validation/summary.md
.workflow/next-action.json
.workflow/next-action.md
asset-investment-diligence/verification/workflow-harness-report.json
asset-investment-diligence/verification/workflow-harness-verification.md
oracle-analysis/verification/workflow-harness-report.json
oracle-analysis/verification/workflow-harness-verification.md
verification/workflow-harness-report.json
verification/workflow-harness-verification.md
```

The generated packet JSON currently has this top-level envelope:

```text
agent
launcher
packet_schema
schema_version
task_payload
task_payload_sha256
```

The `task_payload` currently contains:

```text
artifact_dir
blocking_unknowns
command
do_not
input_paths
known_inputs
mandatory_reference_paths
objective
optional_reference_paths
protocol_adapter
required_outputs
required_packet_headings
return_envelope
run_root
scope_id
scope_type
stage_contract
stage_id
stage_title
validation_command
workflow_id
```

The return envelope inside `task_payload` currently requires the agent to report artifact paths, status, blockers, validation status, fact-state summary, blocking fact ids, fact-result artifact paths, and no-result proof paths.

## Current status and exit semantics

`dev/tools/run_workflow.py` is only a wrapper around `workflow_entrypoint.main()`.

Entrypoint status-to-exit mapping in `workflow_entrypoint_contracts.py` is:

```text
pass -> 0
ready -> 0
scaffolded -> 0
review_required -> 1
blocked -> 2
input_error -> 2
```

Scaffold success returns `status: scaffolded` and exit code `0`. Missing live fields are not fatal input errors; they are represented as blocking unknowns in packets and `next-action`, with Preview/Execute still blocked.

Fatal input errors remain stable and exit `2`: schema/command/objective/assets/oracle-scope errors, path escape, existing run root without compatible resume, and input hash mismatch. `WE_LIVE_FIELD_MISSING` is a stable non-fatal error id used for blockers.

`dev/tools/validate_workflow_run.py` keeps deterministic formal validator semantics:

```text
any P0 finding -> status fail, exit 2
any P1 finding -> status review_required, exit 1
P2 findings only -> status pass, exit 0
--strict-warnings with P2 findings -> status review_required, exit 1
no P0/P1 findings -> status pass, exit 0
```

The validator returns `report.exit_code` from `main()`. It does not decide token economics, oracle quality, investment suitability, or execution merit.

Entrypoint validate mode imports child validator reports into `.workflow/validation/summary.*`, updates `.workflow/next-action.*`, and then applies the same runner status-to-exit mapping. Current tests expect a scaffold-only sample validate run with unfinished artifacts to return `status: blocked` and exit `2`.

Semantic review is opt-in for entrypoint validate mode. By default `.workflow/validation/summary.json` records `semantic_review: {"enabled": false}` and no `.workflow/semantic-review/` directory is created. When enabled without a configured critic command, semantic review reports `semantic_review_unavailable` findings instead of silently passing.

`python3 dev/tools/run_fixture_checks.py` is the smoke wrapper. It runs the fixture matrix, evidence-ledger schema tests, semantic critic runner tests, regression eval suite, and workflow entrypoint unittest module. It exits `0` only when every included check passes; otherwise it exits `2`.

## Non-regression invariants for safe parallelization

### 1. Registry compatibility remains stable

`.workflow/registry.json` must remain valid and backward compatible.

The registry must continue to expose the generated packet list in the legacy serial order. Existing agents that only know how to read `registry.json` and execute packets in registry order must continue to work.

Adding graph metadata later must be additive. Graph-absent legacy runs must continue to validate through the current path.

### 2. `next-action.first_packet` remains

`.workflow/next-action.json.first_packet` must remain present whenever at least one task exists.

The current first-packet shape is:

```json
{
  "task_id": "<task id>",
  "json": ".workflow/packets/<workflow>/<task>.json",
  "markdown": ".workflow/packets/<workflow>/<task>.md",
  "blocking_unknowns": []
}
```

Future `ready_packets`, `blocked_packets`, waves, or execution graph metadata must not replace or rename `first_packet`.

### 3. Packet payload stays stable across agents except launcher text

For the same run root regenerated with `--resume`, supported agent launchers (`generic`, `codex`, `claude-code`, `hermes`) must not change `task_payload` or `task_payload_sha256`.

The only intended agent-specific difference is the top-level `launcher` text. Do not compare payload hashes across different run roots, because `run_root` and validator commands are part of `task_payload`.

### 4. Validator exit semantics do not drift

The validator mapping `P0 -> fail/2`, `P1 -> review_required/1`, `P2-only -> pass/0`, and `strict P2 -> review_required/1` is part of the baseline contract.

Entrypoint validate mode may aggregate reports, but it must not reinterpret formal validation pass as workflow-decision pass when child artifacts, parent return artifacts, semantic review, or unresolved gates still require review.

### 5. Preview and Execute remain blocked

The harness is post-Discover `Analyze -> Propose` only. Preview and Execute remain blocked until a separate human-gated flow exists.

Packets and handoff text must continue to say not to claim execution readiness, not to perform state-changing on-chain actions, and not to make Preview/Execute recommendations.

The parent proposal status block must keep unresolved inputs or validation findings as `request_more_inputs`, `review_required`, `blocked`, or `fail`; it must not mark a run ready for Preview/Execute when blockers remain.

### 6. Harness does not launch subagents

The harness must remain deterministic local file generation plus validator subprocesses only.

It may later emit advisory metadata for human/agent routing, but it must not call `delegate_task`, start worker processes, schedule background agents, or orchestrate subagents. Any future subagent prompt paths must be inert metadata unless a separate reviewed execution system consumes them.

### 7. Parallelization metadata is additive and safe by default

The current baseline has no execution graph, no dependency metadata, no ready-packet sets, no write-scope metadata, and no delegation metadata.

Safe parallelization work must degrade missing or ambiguous dependency information to serial/blocking behavior. Run-level synthesis, underwriting rollups, final verification, and parent proposal composition must remain serial unless a later validator proves otherwise.

## Minimum fixture set that must remain green before rollout

The minimum existing fixture set is the current smoke and pytest surface, not a smaller happy-path subset. Future graph/parallelization fixtures should be additive to this list.

### Entrypoint fixtures and tests

Keep `dev/tools/workflow_harness/tests/test_workflow_entrypoint.py` green. It is the direct baseline for generated artifacts and compatibility behavior.

Minimum covered entrypoint fixtures:

- `dev/implementation/workflow-harness/fixtures/entrypoint-inputs/sample-assets-minimal.json`
- `dev/implementation/workflow-harness/fixtures/entrypoint-inputs/sample-assets-complete.json`
- malformed input fixture coverage in the test module
- path escape fixture coverage in the test module

Minimum covered entrypoint invariants:

- help/no-arg CLI exits `0`;
- minimal input scaffolds parent root, child roots, packets, registry, handoff, and next-action;
- scaffold output is deterministic across isolated roots;
- supported agent launchers do not change same-run `task_payload`;
- prompt budget stays below the current bound;
- missing live fields become blockers, not fatal input errors;
- packets embed investigation contract and fact-state templates;
- asset blockers propagate into related oracle packets;
- S6 scenario fallback is allowed only for missing user sizing/risk inputs and forbidden when request inputs prevent scenarios;
- malformed input has stable error ids;
- path escape is rejected before writing;
- validate mode imports child validator findings into `next-action`.

### Formal fixture matrix

Keep every row in `dev/implementation/workflow-harness/fixtures/fixture-matrix.json` green with its expected status, exit code, and finding ids:

| Fixture id | Expected status | Expected exit |
| --- | ---: | ---: |
| `good/good-agentic-sample-assets` | `pass` | `0` |
| `bad/missing-final-oracle-verification` | `fail` | `2` |
| `bad/asset-heading-overclaim` | `fail` | `2` |
| `bad/broken-relative-link` | `fail` | `2` |
| `bad/oracle-side-specific-omission` | `fail` | `2` |
| `bad/ready-for-preview-incorrectly` | `review_required` | `1` |
| `bad/missing-propose-handoff` | `fail` | `2` |
| `bad/missing-parent-return-status` | `review_required` | `1` |
| `bad/no-parent-return-artifact` | `fail` | `2` |
| `bad/oracle-no-result-proof-missing` | `review_required` | `1` |
| `bad/oracle-not-investigated-as-no-result` | `review_required` | `1` |
| `oracle-valid-no-market-no-route` | `pass` | `0` |
| `asset-good-scenario-fallback` | `pass` | `0` |
| `asset-bad-empty-calculations` | `review_required` | `1` |

### Evidence-ledger contract fixture

Keep `dev/tools/workflow_harness/tests/test_evidence_ledger_schema.py` green.

Minimum fixture:

- `dev/implementation/workflow-harness/fixtures/evidence-ledger/positive-and-no-result/evidence-ledger.json`

This fixture protects the positive fact envelope, `investigated_no_result` evidence, raw output path resolution, RPC/HTTP/negative-search required fields, freshness, and decision effect metadata.

### Semantic critic and quality-gate regression fixtures

Keep `dev/tools/workflow_harness/tests/test_semantic_critic_runner.py` green.

Minimum semantic behavior:

- missing critic command reports `semantic_review_unavailable` instead of pass;
- critic-command findings normalize into the stable report schema;
- entrypoint validate mode keeps semantic review opt-in and safe on unavailable.

Keep `dev/tools/workflow_harness/tests/test_regression_eval_suite.py` green.

Minimum regression eval ids:

- `fact.well_investigated_positive`
- `fact.investigated_no_result_with_negative_evidence`
- `fact.not_investigated_masquerading_as_unknown`
- `adapter.valid_no_market_no_route_after_search`
- `quantitative.scenario_fallback`
- `quantitative.empty_calculations`
- `parent.request_more_inputs_actionable_acceptance`
- `semantic.low_quality_form_fill`

These ids protect generalized quality gates without encoding live token recommendations, token-specific addresses, or asset-specific remediation policy.

## Required verification commands

Run both commands from the repository root before any safe-parallelization rollout card proceeds:

```bash
python3 dev/tools/run_fixture_checks.py
python3 -m pytest dev/tools/workflow_harness/tests -q
```

Both commands must exit `0` against the current baseline. Any safe-parallelization change must preserve this baseline and add graph-specific tests on top.
