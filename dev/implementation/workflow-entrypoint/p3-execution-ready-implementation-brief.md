# P3 implementation brief — surgical workflow entrypoint

Task: `t_445ffbb8`

## Goal

Build the smallest permanent runner slice that lets an agent start one `analyze-propose` workflow from one compact input file and receive deterministic run folders, child workflow scaffolds, stage packets, and validation status for:

- `asset-investment-diligence`
- `oracle-analysis`

This brief replaces the broad P1 plan as the implementation target. P1 remains useful background; implement from this file.

## Decision

Implement a standard-library-only scaffold and validation bridge around the existing workflow packages and `dev/tools/validate_workflow_run.py`.

The first slice exposes exactly one user-facing command:

```bash
python3 dev/tools/run_workflow.py analyze-propose --input <scope.json> --mode scaffold --agent <generic|codex|claude-code|hermes> --format <json|markdown>
```

It does not launch subagents, perform live research, judge token economics, judge oracle correctness, or introduce state-changing stages. It only materializes a deterministic parent run root, child run roots, packet files, skeleton artifact files, and the next action packet that a separate agent can execute.

Use JSON input for this slice. YAML support is a non-goal until the repo accepts a dependency or a restricted parser contract; the P2 review found the test environment must stay reproducible without undeclared packages.

## P2 review findings addressed

| P2 finding | Resolution in this brief |
| --- | --- |
| RC1 — mandatory `must_read` docs can shift prompt bloat into child packets | Stage packets must be self-contained for execution. They include exact task summary, inputs, write paths, required headings, output files, return envelope, validation command, and blocker rules. Long workflow docs are listed only under `optional_reference_paths`. If a future implementation adds `mandatory_reference_paths`, prompt-budget tests must count those bytes. |
| RC2 — runner contracts/templates must be deterministic and not prose-parsed | Add a static Python contract file for workflow IDs, child run layout, selected stages, skip rules, skeleton headings, packet templates, validation commands, stable error IDs, and status mapping. Do not parse `runbook.md`, `stage-contracts.md`, or `subagent-prompts.md` at runtime. |
| RC3 — cross-agent packet invariance is under-specified | Packet JSON contains a canonical `task_payload` that is byte-identical for `--agent codex`, `--agent claude-code`, and `--agent hermes` when serialized with sorted keys. Agent differences live only in a sibling `launcher` object. Tests compare the canonical payload bytes across all agents. |
| RC4 — live data gaps need explicit fixtures | Add a missing-live-fields fixture. Normalization preserves missing addresses, feed addresses, position sides, token roles, and position size as `null` or `not_available`; generated packets and skeletons list them in `blocking_unknowns`; tests assert no synthetic address, price, APR, methodology verdict, or suitability claim is generated. |
| RC5 — pytest is unavailable in this checkout | New acceptance tests run through standard-library Python entrypoints. Keep pytest compatibility optional, but do not require pytest for the implementation gate. |

## Allowed implementation scope

Create these files:

1. `dev/tools/run_workflow.py`
   - Thin CLI wrapper.
   - `argparse` subcommand: `analyze-propose` only.
   - Arguments:
     - `--input` required, repo-relative or absolute path that must resolve inside the vault.
     - `--mode` choices: `scaffold`, `validate`; default `scaffold`.
     - `--agent` choices: `generic`, `codex`, `claude-code`, `hermes`; default `generic`.
     - `--format` choices: `json`, `markdown`; default `markdown`.
     - `--run-root` optional override; must resolve under `dev/implementation/`.
     - `--resume` optional; only allowed when existing `.workflow/input.normalized.json` hash matches the current input.
     - `--strict-warnings` optional; forwarded to validation only, making warning-only/P2 findings return review-required instead of pass.
   - Exit codes:
     - `0` for successful scaffold, pass validation, or warning-only validation without `--strict-warnings`.
     - `1` for review-required validation, including warning-only validation with `--strict-warnings`.
     - `2` for blocked/P0/input/path errors.

2. `dev/tools/workflow_entrypoint.py`
   - Core runner implementation.
   - Functions to implement:
     - `load_input(path: Path) -> dict`
     - `normalize_input(raw: dict) -> dict`
     - `validate_input(normalized: dict) -> list[Finding]`
     - `resolve_under_vault(path: Path) -> Path`
     - `resolve_run_root(normalized: dict, explicit_run_root: str | None) -> Path`
     - `build_plan(normalized: dict, run_root: Path) -> dict`
     - `scaffold(plan: dict, agent: str) -> RunnerResult`
     - `validate_run(plan: dict) -> RunnerResult`
     - `write_next_action(result: RunnerResult) -> None`
   - All writes must happen under the selected run root.
   - Use subprocess calls for `dev/tools/validate_workflow_run.py`; do not refactor the validator in this slice.

3. `dev/tools/workflow_entrypoint_contracts.py`
   - Static declarative contracts, not runtime Markdown parsing.
   - Include:
     - workflow IDs: `asset-investment-diligence-v1`, `oracle-analysis-v1`, `combined-analyze-propose`.
     - child directories: `asset-investment-diligence/`, `oracle-analysis/`.
     - generated parent files: `README.md`, `index.md`, `run-manifest.json`, `agentic-flow/analyze-and-propose.md`, `.workflow/input.normalized.json`, `.workflow/plan.json`, `.workflow/tasks.json`, `.workflow/registry.json`, `.workflow/next-action.json`, `.workflow/next-action.md`.
     - child files: `README.md`, `index.md`, `run-manifest.json`, per-scope `scope.json`, `verification/` directories, skipped-stage markers.
     - selected stages for this first slice:
       - asset: `S1_general_asset_mining`, `S2_asset_risk_analyst_report`, `S6_quantitative_underwriting`, `S7_final_verification`; mark `S3`, `S4`, `S5` skipped when `pt_markets` and `social_scopes` are empty.
       - oracle: `S0_scope_and_acceptance` through `S6_final_verification` when oracle scopes are present.
     - required skeleton headings per generated Markdown artifact.
     - packet schema `workflow-stage-packet-v1`.
     - stable error IDs: `WE_SCHEMA_VERSION`, `WE_COMMAND`, `WE_OBJECTIVE_QUESTION`, `WE_ASSETS`, `WE_ORACLE_SCOPE`, `WE_PATH_ESCAPE`, `WE_RUN_ROOT_EXISTS`, `WE_INPUT_HASH_MISMATCH`, `WE_LIVE_FIELD_MISSING`.
     - validator command templates for asset and oracle child roots.
     - status mapping: validator exit `2 -> blocked`, exit `1 -> review_required`, exit `0 -> pass`; warning-only/P2 findings stay pass unless `--strict-warnings` is set.

4. `dev/tools/workflow_harness/tests/test_workflow_entrypoint.py`
   - Standard-library executable test file with `unittest.main()`.
   - Must not require pytest.
   - Test cases:
     - CLI help returns exit code `0` for the root command and `analyze-propose --help`.
     - minimal input scaffolds parent and child run roots in a temporary directory under `dev/implementation/workflow-harness/tmp/`.
     - deterministic scaffold: two isolated run roots produce identical normalized input, plan, tasks, packet task payloads, and next-action files after stripping the explicit run-root string.
     - path escape input fails with exit code `2`, stable ID `WE_PATH_ESCAPE`, and no write outside the selected run root.
     - malformed input fails with stable schema IDs before scaffold.
     - prompt budget: baseline bytes and deterministic token proxy equal hand-written scope plus `runbook.md`, `workflow.json`, `stage-contracts.md`, `subagent-prompts.md`, and `output-structure.md` for both child workflows; new bytes and token proxy equal input plus `.workflow/next-action.md` plus one packet plus any `mandatory_reference_paths`; assert new surface is below 25% and raw `subagent-prompts.md` content is absent.
     - cross-agent invariance: generate packets for `generic`, `codex`, `claude-code`, and `hermes`; assert canonical `task_payload` bytes match and only `launcher` differs.
     - live-data gaps: omitted feed address, position side, token role, and position size remain `null` or `not_available`, appear in `blocking_unknowns`, and do not produce invented addresses, prices, APRs, or suitability language.
     - validation bridge: known child validation P0/P1/P2 results are imported into `.workflow/validation/`, `.workflow/next-action.json`, and process exit codes.

5. `dev/tools/workflow_harness/tests/run_fixture_checks.py`
   - Standard-library wrapper around the existing fixture matrix so the current validator regression can run without pytest.
   - It should execute the same checks currently expressed in `test_fixtures.py`:
     - exact required fixture rows;
     - physical run trees;
     - expected exit codes/statuses/findings;
     - distinct malformed versus missing parent-return failures.

6. Fixture inputs under `dev/implementation/workflow-harness/fixtures/entrypoint-inputs/`:
   - `sample-assets-minimal.json`
   - `malformed-missing-assets.json`
   - `path-escape-artifact-root.json`
   - `missing-live-fields.json`

Do not edit these files in this slice unless a failing test proves it is unavoidable:

- `dev/tools/validate_workflow_run.py`
- `user/references/workflows/asset-investment-diligence/workflow.json`
- `user/references/workflows/oracle-analysis/workflow.json`
- `user/references/workflows/*/runbook.md`
- `user/references/workflows/*/stage-contracts.md`
- `user/references/workflows/*/subagent-prompts.md`
- `user/references/workflows/*/output-structure.md`
- root `README.md`
- root `CLAUDE.md`

## Generated run-root contract

For `sample-assets-minimal.json`, the default scaffold should create:

```text
dev/implementation/analyze-propose-<primary-scope>-<input-sha8>/
  README.md
  index.md
  run-manifest.json
  agentic-flow/
    analyze-and-propose.md
  asset-investment-diligence/
    README.md
    index.md
    run-manifest.json
    tokens/
      <asset-scope-slug>/
        scope.json
        research/
        verification.md
    pt-markets/
      index.md
      skipped-S3_pt_market_economics.md
    x-research/
      index.md
      skipped-S4_x_social_mining.md
      skipped-S5_x_social_synthesis.md
    investment-analysis/
    verification/
  oracle-analysis/
    README.md
    index.md
    run-manifest.json
    tokens/
      <oracle-scope-slug>/
        scope.json
        oracle/
          scope.md
        raw/
    verification/
  .workflow/
    input.normalized.json
    plan.json
    tasks.json
    registry.json
    packets/
      <stage-id>/
        <scope-id>.json
        <scope-id>.md
    validation/
      commands.jsonl
    next-action.json
    next-action.md
```

Skeleton files may state `not_run`, `not_ready`, `not_available`, or `blocked_on_input`. They must not contain fabricated factual conclusions.

## Packet contract

Every packet JSON must use this top-level shape:

```json
{
  "packet_schema": "workflow-stage-packet-v1",
  "task_payload": {
    "command": "analyze-propose",
    "workflow_id": "oracle-analysis-v1",
    "stage_id": "S1_feed_inventory_and_graph",
    "scope_id": "eth-mainnet-sample-vault-token-gearbox",
    "run_root": "dev/implementation/.../oracle-analysis",
    "artifact_dir": "tokens/<oracle-scope-slug>",
    "input_paths": ["tokens/<oracle-scope-slug>/scope.json"],
    "required_outputs": ["tokens/<oracle-scope-slug>/oracle/feed-graph.md"],
    "required_headings": ["Scope", "Known inputs", "Blocking unknowns", "Work to perform", "Return envelope"],
    "blocking_unknowns": [],
    "optional_reference_paths": ["user/references/workflows/oracle-analysis/gearbox-price-feed-parsing.md"],
    "mandatory_reference_paths": [],
    "return_envelope": {
      "stage_id": "S1_feed_inventory_and_graph",
      "scope_id": "eth-mainnet-sample-vault-token-gearbox",
      "status": "pass | review_required | blocked",
      "artifact_paths": [],
      "key_numbers": [],
      "blocking_unknowns": [],
      "validation": {"result": "not_run", "checks": []}
    },
    "do_not": [
      "Do not write outside the run root.",
      "Do not invent missing addresses, prices, APRs, or oracle verdicts.",
      "Do not claim economic suitability or execution readiness."
    ]
  },
  "launcher": {
    "agent": "generic",
    "invocation_hint": "Read this packet and write only to the declared run root."
  }
}
```

The Markdown packet should be a rendering of the same `task_payload`, plus the `launcher.invocation_hint`.

## Validation bridge

`validate` mode runs child validators only; it does not create new downstream action semantics.

Commands generated by the runner:

```bash
python3 dev/tools/validate_workflow_run.py --workflow asset-investment-diligence --run-root <parent>/asset-investment-diligence --format json,markdown --report-dir <parent>/asset-investment-diligence/verification --write-verification
python3 dev/tools/validate_workflow_run.py --workflow oracle-analysis --run-root <parent>/oracle-analysis --format json,markdown --report-dir <parent>/oracle-analysis/verification --write-verification
```

The runner writes:

- `.workflow/validation/commands.jsonl` with command, exit code, stdout/stderr paths, and timestamp.
- `.workflow/validation/latest.json` with child statuses and grouped P0/P1/P2 counts.
- `.workflow/next-action.json` and `.workflow/next-action.md` with the first unblock/review action.

Do not call the combined Analyze → Propose validator until a real parent handoff exists. A scaffold placeholder is not a parent verdict.

## Acceptance commands

Run from `/Users/ilya/Documents/Codex/front-knowledge-base` after implementation:

```bash
python3 -m py_compile \
  dev/tools/run_workflow.py \
  dev/tools/workflow_entrypoint.py \
  dev/tools/workflow_entrypoint_contracts.py \
  dev/tools/validate_workflow_run.py \
  dev/tools/workflow_harness/tests/test_fixtures.py \
  dev/tools/workflow_harness/tests/test_workflow_entrypoint.py \
  dev/tools/workflow_harness/tests/run_fixture_checks.py
```

```bash
python3 dev/tools/workflow_harness/tests/run_fixture_checks.py
```

```bash
python3 dev/tools/workflow_harness/tests/test_workflow_entrypoint.py
```

```bash
python3 dev/tools/run_workflow.py analyze-propose --input dev/implementation/workflow-harness/fixtures/entrypoint-inputs/sample-assets-minimal.json --mode scaffold --agent generic --format json --run-root dev/implementation/workflow-harness/tmp/manual-entrypoint-smoke
```

Expected acceptance:

- all commands above return exit code `0` on a clean checkout;
- the scaffold command creates the generated run-root contract listed above;
- `.workflow/next-action.json` is `ready` or `blocked` with concrete packet paths and blockers, never a suitability or action-ready conclusion;
- generated packet `task_payload` bytes are identical across supported agents;
- prompt-budget test shows the generated prompt surface is below 25% of the manual baseline by bytes and by deterministic token proxy;
- missing live fields stay null/not_available and appear in `blocking_unknowns`;
- path-escape fixtures fail with exit code `2` and stable finding ID `WE_PATH_ESCAPE`;
- validator fixture regressions remain green through `run_fixture_checks.py` without pytest.

Before handing off, also run:

```bash
git diff --check -- dev/tools/run_workflow.py dev/tools/workflow_entrypoint.py dev/tools/workflow_entrypoint_contracts.py dev/tools/workflow_harness/tests/test_workflow_entrypoint.py dev/tools/workflow_harness/tests/run_fixture_checks.py dev/implementation/workflow-harness/fixtures/entrypoint-inputs

git status --short -- dev/tools/run_workflow.py dev/tools/workflow_entrypoint.py dev/tools/workflow_entrypoint_contracts.py dev/tools/workflow_harness/tests/test_workflow_entrypoint.py dev/tools/workflow_harness/tests/run_fixture_checks.py dev/implementation/workflow-harness/fixtures/entrypoint-inputs
```

## Rollback

Rollback is file-level and safe:

1. Delete the new runner files:
   - `dev/tools/run_workflow.py`
   - `dev/tools/workflow_entrypoint.py`
   - `dev/tools/workflow_entrypoint_contracts.py`
2. Delete the new test files:
   - `dev/tools/workflow_harness/tests/test_workflow_entrypoint.py`
   - `dev/tools/workflow_harness/tests/run_fixture_checks.py`
3. Delete the new input fixtures:
   - `dev/implementation/workflow-harness/fixtures/entrypoint-inputs/`
4. Delete any generated smoke roots under:
   - `dev/implementation/workflow-harness/tmp/`

No rollback of reusable workflow docs or the existing validator should be needed because this slice does not mutate them.

## Non-goals

- No subagent launching.
- No remote RPC, explorer, web, X, or market-data calls.
- No economic suitability, allocation, APR, price, oracle-quality, or execution-readiness verdicts.
- No new modes beyond `scaffold` and `validate`.
- No separate public `asset-diligence` or `oracle-analysis` command in this slice; they are child workflows under `analyze-propose` only.
- No runtime parsing of long Markdown workflow docs.
- No mutation of `user/references/workflows/*` in this slice.
- No YAML support until dependency policy is explicit.
- No Preview/Execute semantics, generated approvals, transaction previews, or action execution contracts.

## Implementation order

1. Add fixture JSON inputs.
2. Add `workflow_entrypoint_contracts.py` with static contracts and stable IDs.
3. Add `workflow_entrypoint.py` normalization, path safety, plan building, scaffold writing, and validation bridge.
4. Add `run_workflow.py` CLI wrapper.
5. Add `run_fixture_checks.py` for stdlib validator regression.
6. Add `test_workflow_entrypoint.py` and make it run all new acceptance cases.
7. Run the acceptance commands above.
8. If any test requires editing `validate_workflow_run.py` or workflow package docs, stop and update this brief first; do not expand scope ad hoc.
