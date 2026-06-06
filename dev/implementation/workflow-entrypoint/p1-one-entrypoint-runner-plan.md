# P1 plan — one-entrypoint workflow runner contract

Task: `t_ae46c4a4`

## Goal

Build a thin workflow entrypoint on top of the existing `front-knowledge-base` workflow packages so an agent starts a token/oracle diligence run with one command plus one small YAML or JSON input file.

The runner must not replace the existing workflow docs or compliance validator. It should compile them into deterministic run folders, stage packets, skeleton artifacts, and validation gates.

## Sources inspected

- Parent R1 audit: `dev/implementation/workflow-entrypoint/r1-internal-research-audit.md`.
- Local operating contract: `CLAUDE.md`.
- Asset diligence workflow package:
  - `user/references/workflows/asset-investment-diligence/workflow.json`
  - `user/references/workflows/asset-investment-diligence/runbook.md`
  - `user/references/workflows/asset-investment-diligence/output-structure.md`
  - `user/references/workflows/asset-investment-diligence/stage-contracts.md`
  - `user/references/workflows/asset-investment-diligence/subagent-prompts.md`
- Oracle workflow package:
  - `user/references/workflows/oracle-analysis/workflow.json`
  - `user/references/workflows/oracle-analysis/runbook.md`
  - `user/references/workflows/oracle-analysis/output-structure.md`
  - `user/references/workflows/oracle-analysis/stage-contracts.md`
  - `user/references/workflows/oracle-analysis/subagent-prompts.md`
  - `user/references/workflows/oracle-analysis/gearbox-price-feed-parsing.md` when protocol is Gearbox.
- Existing validator: `dev/tools/validate_workflow_run.py`.

## Non-goals

- Do not assess token economics, oracle correctness, allocation suitability, or live execution merit.
- Do not embed long workflow docs in parent prompts.
- Do not make Preview or Execute recommendations while P0/P1 blockers remain.
- Do not mutate reusable workflow docs in this planning card.

## Proposed CLI contract

Add one canonical entrypoint:

```bash
python3 dev/tools/run_workflow.py analyze-propose --input <scope.yaml|scope.json>
```

Supported subcommands:

```bash
python3 dev/tools/run_workflow.py analyze-propose --input <file> [--mode plan|scaffold|next|validate|execute] [--agent codex|claude-code|hermes|generic] [--format markdown|json] [--resume]
python3 dev/tools/run_workflow.py asset-diligence --input <file> [same options]
python3 dev/tools/run_workflow.py oracle-analysis --input <file> [same options]
```

Default mode should be `scaffold` for the first implementation slice: validate the input, create the deterministic run root, write manifests/indexes/skeletons/stage packets, and return the next-action packet. `execute` can be reserved for a later slice that launches subagents; the P1 implementation can still make the execution contract explicit without implementing remote agent orchestration.

Mode semantics:

| Mode | Side effects | Output |
| --- | --- | --- |
| `plan` | None | Deterministic plan, selected workflows, run root, child roots, stage graph, validation gates. |
| `scaffold` | Creates run folders, manifests, indexes, skeletons, packet files. | Same as `plan` plus paths created and first next-action packet. |
| `next` | Reads existing run root. | One compact packet for the next unblocked stage/batch. |
| `validate` | Runs `dev/tools/validate_workflow_run.py`. | P0/P1/P2 summary, report paths, next blocker packet. |
| `execute` | Later slice only. | Runs or delegates packets according to `--agent`; not required for the first implementation. |

The CLI should accept relative paths only under the vault root and should resolve all output paths through `Path.resolve()` with a containment check. Any path that escapes the vault or the selected run root is a P0 input error.

## Minimal input schema

The input file must be intentionally small. It should identify the candidate, objective, workflows, and known live fields; the runner derives folders, manifests, skipped stages, and worker packet context.

### Schema fields

```yaml
schema_version: workflow-entrypoint-input-v1
command: analyze-propose
run:
  # Optional. If omitted, runner derives a stable slug from command + primary scope + input fingerprint.
  slug: sample-assets-gearbox
  artifact_root: null  # optional override; must stay under dev/implementation/
  overwrite_policy: fail_if_exists  # fail_if_exists | resume_if_manifest_matches

objective:
  question: Is the SampleBaseToken/SampleVaultToken setup acceptable for Gearbox Credit Account opening analysis?
  canonical_loop_stage: Analyze
  requested_outputs:
    - asset_investment_diligence
    - oracle_analysis
    - combined_analyze_propose_handoff

portfolio_context:
  position_size_usd: null
  base_net_apr_hurdle: null
  opportunistic_net_apr_hurdle: null
  horizon_days: null

assets:
  - scope_id: eth-mainnet-sample-base-token
    chain_id: 1
    chain: Ethereum mainnet
    symbol: SampleBaseToken
    address: null
    asset_type: underlying_token
    intended_use: RWA backing / underlying exposure
    issuer_or_protocol: null

  - scope_id: eth-mainnet-sample-vault-token
    chain_id: 1
    chain: Ethereum mainnet
    symbol: SampleVaultToken
    address: "0x2222222222222222222222222222222222222222"
    asset_type: vault_share
    underlying_scope_id: eth-mainnet-sample-base-token
    intended_use: Gearbox collateral candidate
    issuer_or_protocol: null

gearbox_context:
  protocol: Gearbox
  market_context:
    credit_manager: null
    lt: null
    position_size_usd: null
    target_leverage: null
  oracle_scopes:
    - scope_id: eth-mainnet-sample-vault-token-gearbox
      asset_scope_id: eth-mainnet-sample-vault-token
      scope_type: token
      position_sides:
        - credit_account_borrower
        - pool_lp
        - liquidator
        - curator_operator
      token_roles:
        - collateral
      known_feeds:
        - role: main
          address: "0x4444444444444444444444444444444444444444"
      accepted_oracle_methodologies: null

pt_markets: []
social_scopes: []
policy:
  preserve_unknown_fields_as_null: true
  max_concurrent_subagents: 3
  allow_preview_execute_when_blocked: false
```

Required for future token cases:

- `schema_version`.
- `command`.
- `objective.question`.
- At least one `assets[]` item with `scope_id`, `chain_id`, `chain`, `symbol`, `address` as value or `null`, `asset_type`, and `intended_use`.
- At least one requested output under `objective.requested_outputs`.
- For oracle analysis, at least one `gearbox_context.oracle_scopes[]` or generic `oracle_scopes[]` item with `scope_id`, `asset_scope_id`, `scope_type`, `position_sides`, `token_roles`, and `known_feeds` as an array that may be empty but must exist.
- For asset diligence, `portfolio_context` fields must exist and may be `null`.
- For PT analysis, `pt_markets[]` entries add `scope_id`, `underlying_scope_id`, `target_maturity`, `chain_id`, and optional `market_address`.
- For X/social analysis, `social_scopes[]` entries add `scope_id`, `token_scope_id`, optional `pt_scope_id`, `programs`, and `time_window`.

Unknown values are retained as `null`; the runner never deletes unknown fields. This preserves blocker visibility for the Analyze → Propose handoff.

## Deterministic run-root creation

Default run root:

```text
dev/implementation/<command>-<primary-scope-slug>-<input-sha8>/
```

For the SampleBaseToken/SampleVaultToken input above, the default shape is:

```text
dev/implementation/analyze-propose-ethereum-sample-vault-token-22222222-<input-sha8>/
  README.md
  index.md
  run-manifest.json
  agentic-flow/
    analyze-and-propose.md
  asset-investment-diligence/
    README.md
    run-manifest.json
    index.md
    tokens/
      ethereum-sample-base-token-unknown/
      ethereum-sample-vault-token-22222222/
    verification/
  oracle-analysis/
    README.md
    run-manifest.json
    index.md
    tokens/
      ethereum-sample-vault-token-22222222/
    verification/
  .workflow/
    input.normalized.json
    plan.json
    tasks.json
    registry.json
    packets/
    templates/
    validation/
```

Rules:

1. If `run.slug` is supplied, use `dev/implementation/<slug>/` after slug normalization unless `run.artifact_root` supplies a stricter path.
2. If `run.slug` is absent, derive `primary-scope-slug` from the first asset or oracle scope: `<chain>-<symbol>-<address-prefix>`, with `unknown` for a null address.
3. Compute `input-sha8` from canonical JSON: sorted keys, no insignificant whitespace, null fields preserved.
4. Refuse to overwrite an existing run root unless `--resume` is passed and the existing `.workflow/input.normalized.json` hash matches.
5. Parent `analyze-propose` always places child run roots as siblings under the parent run root: `asset-investment-diligence/` and `oracle-analysis/`.
6. Child manifests declare their `run_artifact_root` relative to the vault root, matching the existing validator expectation.
7. Every generated path is recorded in `.workflow/plan.json` and in the relevant run manifest before any subagent packet is emitted.

## Workflow-doc compiler contract

The runner should compile from workflow package files instead of copying those files into prompts.

Source priority:

1. `workflow.json` is the stage graph source of truth: workflow ID, stage IDs, dependencies, parallelization, delegate policy, inputs, outputs, validation fields, and global rules.
2. `output-structure.md` provides canonical folder/file layout until the layout is promoted into machine-readable `workflow.json.artifact_layout` fields.
3. `stage-contracts.md` provides stage input/output envelopes and required fields.
4. `subagent-prompts.md` provides reusable worker prompt templates by stage ID.
5. `gearbox-price-feed-parsing.md` is cited in oracle packets when `protocol: Gearbox`.

P1 implementation should add only the smallest machine-readable metadata needed to avoid brittle markdown parsing:

```json
{
  "runner_contract": {
    "input_schema_ref": "workflow-entrypoint-input-v1",
    "stage_prompt_template_ids": {
      "S1_general_asset_mining": "asset.S1",
      "S1_feed_inventory_and_graph": "oracle.S1"
    },
    "artifact_templates": {
      "run_readme": "templates/run-readme.md",
      "run_index": "templates/run-index.md",
      "stage_packet": "templates/stage-packet.md"
    },
    "validator": {
      "command": "python3 dev/tools/validate_workflow_run.py",
      "workflow_arg": "asset-investment-diligence"
    }
  }
}
```

If reusable workflow docs are not mutated in the first implementation slice, the runner can keep this metadata in `dev/tools/workflow_entrypoint_contracts.py` as a transitional adapter. The long-term target is `workflow.json` owning the machine-readable contract.

## Generated artifacts

The runner writes these artifacts before any worker execution:

```text
.workflow/input.normalized.json       # canonicalized user input
.workflow/plan.json                   # command, run root, child roots, stage graph, selected/skipped stages
.workflow/tasks.json                  # task DAG with statuses, dependencies, packet paths, artifact paths
.workflow/registry.json               # compact parent registry; updated after each handoff
.workflow/packets/<stage>/<scope>.md  # compact agent packet
.workflow/packets/<stage>/<scope>.json
.workflow/validation/latest.json      # latest validator summary, if validation ran
```

Each child run root receives existing workflow-compatible skeletons:

- `README.md` with read-first paths and validation status placeholders.
- `index.md` with artifact map, open blockers, and status table placeholders.
- `run-manifest.json` with workflow ID, run root, scope entries, expected directories, status `blocked` or `review_required` until artifacts exist.
- Per-token/per-scope `scope.json` files derived from the normalized input.
- Required directories from `output-structure.md`.
- Verification directories.

Skeleton markdown should include headings required by the validator, but not invented conclusions. Unknown evidence sections must say `not_run` or `not_available` and point to the relevant packet/stage.

## Stage packet contract

Every generated packet must be short enough for Codex, Claude Code, or Hermes to consume without loading the full workflow package.

Packet fields:

```json
{
  "packet_schema": "workflow-stage-packet-v1",
  "agent": "generic",
  "run_root": "dev/implementation/.../oracle-analysis",
  "workflow_id": "oracle-analysis-v1",
  "stage_id": "S1_feed_inventory_and_graph",
  "scope_id": "eth-mainnet-sample-vault-token-gearbox",
  "artifact_dir": "tokens/ethereum-sample-vault-token-22222222",
  "must_read": [
    "user/references/workflows/oracle-analysis/stage-contracts.md#S1",
    "user/references/workflows/oracle-analysis/gearbox-price-feed-parsing.md"
  ],
  "inputs": {
    "scope_json": "tokens/ethereum-sample-vault-token-22222222/scope.json",
    "known_feeds": [{"role": "main", "address": "0x4444444444444444444444444444444444444444"}]
  },
  "expected_outputs": [
    "tokens/ethereum-sample-vault-token-22222222/oracle/feed-graph.md",
    "tokens/ethereum-sample-vault-token-22222222/raw/feed-probes.json"
  ],
  "return_envelope": {
    "stage_id": "S1_feed_inventory_and_graph",
    "scope_id": "eth-mainnet-sample-vault-token-gearbox",
    "status": "pass | review_required | blocked",
    "artifact_paths": [],
    "key_numbers": [],
    "blocking_unknowns": [],
    "validation": {"result": "pass | fail", "checks": []}
  },
  "do_not": [
    "Do not paste raw RPC dumps into the handoff.",
    "Do not make Preview or Execute recommendations.",
    "Do not write outside the run root."
  ]
}
```

The Markdown packet can wrap the same data in plain instructions for terminal agents. Agent-specific differences are limited to launch hints:

- Codex: command-line task text plus packet path; no Kanban or Hermes assumptions.
- Claude Code: `claude`/`claude-code` prompt that says to read the packet and write outputs under the run root.
- Hermes: `delegate_task`-ready prompt, with explicit instruction not to call Kanban tools unless the parent packet was itself a board task.
- Generic: plain terminal/LLM prompt.

## Stage selection and skip logic

The runner selects stages from `workflow.json` and input arrays:

Asset diligence:

- Always select S1, S2, S6, S7 when `asset_investment_diligence` is requested.
- Select S3 only when `pt_markets[]` is non-empty.
- Select S4/S5 only when `social_scopes[]` is non-empty or input policy asks for social/points research.
- Create explicit skipped-stage markers for S3, S4, and S5 when skipped so the validator can distinguish an intentional skip from a missing artifact.

Oracle analysis:

- Always select S0 through S6 when `oracle_analysis` is requested and `position_sides` and `token_roles` are present.
- Permit S0/S1-only inventory mode only when `position_sides` and `token_roles` are explicitly `null`; block protocol-fit packets in that mode.
- Add `gearbox-price-feed-parsing.md` to `must_read` when protocol is Gearbox.

Analyze → Propose parent:

- Create both child roots when both child workflows are requested.
- Create `agentic-flow/analyze-and-propose.md` only after child validator reports exist or as a skeleton with status `not_ready`.
- Keep Preview, Execute, and Monitor stages blocked until child P0/P1 findings are reconciled and live gates are named.

## Validator integration and P0/P1 surfacing

Keep `dev/tools/validate_workflow_run.py` as the compliance layer. The runner should call it rather than duplicating validation logic:

```bash
python3 dev/tools/validate_workflow_run.py \
  --workflow asset-investment-diligence \
  --run-root <parent>/asset-investment-diligence \
  --format json,markdown \
  --report-dir <parent>/asset-investment-diligence/verification \
  --write-verification

python3 dev/tools/validate_workflow_run.py \
  --workflow oracle-analysis \
  --run-root <parent>/oracle-analysis \
  --format json,markdown \
  --report-dir <parent>/oracle-analysis/verification \
  --write-verification

python3 dev/tools/validate_workflow_run.py \
  --workflow combined-analyze-propose \
  --run-root <parent> \
  --parent-return agentic-flow/analyze-and-propose.md \
  --format json,markdown \
  --report-dir <parent>/verification
```

Current validator status semantics are:

- Any P0 finding: status `fail`, exit code `2`.
- Any P1 finding without P0: status `review_required`, exit code `1`.
- P2 warnings only: status `pass`, exit code `0`, unless `--strict-warnings` is used.

Runner surfacing rules:

1. Always write the raw report JSON and Markdown verification paths into `.workflow/validation/latest.json` and the parent `index.md`.
2. Print a compact summary grouped by P0, P1, P2 count, not the full report.
3. For P0, return the first unblock action as a packet with `status: blocked` and the failing check IDs.
4. For P1, return `review_required` with concrete artifact paths and check IDs; do not continue to Preview/Execute.
5. For P2, include warnings in the packet but allow the next stage unless `--strict-warnings` was requested.
6. Store all validator commands with exit codes in `.workflow/validation/commands.jsonl`.

## Compact next-action packet

After every mode, the runner prints and writes one packet that answers: what should the next agent do, which files should it read, where must it write, and what validator command will judge it.

Path:

```text
.workflow/next-action.md
.workflow/next-action.json
```

Required fields:

```json
{
  "status": "ready | review_required | blocked | pass",
  "next_action_type": "run_stage_batch | fix_findings | review | no_action",
  "agent_packet_paths": [".workflow/packets/S1_feed_inventory_and_graph/eth-mainnet-sample-vault-token-gearbox.md"],
  "read_first": [".workflow/plan.json", "oracle-analysis/run-manifest.json"],
  "write_scope": "dev/implementation/.../oracle-analysis/tokens/ethereum-sample-vault-token-22222222",
  "validator_command": "python3 dev/tools/validate_workflow_run.py ...",
  "blocking_findings": [],
  "review_findings": [],
  "prompt_budget_note": "Parent prompt contains input file + packet path only; workflow docs are referenced by path."
}
```

This is the handoff any agent type can use without the current chat context.

## Smoke and e2e test strategy proving prompt shrinkage

Add tests under a new runner-focused test module, for example:

```text
dev/tools/workflow_harness/tests/test_workflow_entrypoint.py
```

Test fixtures should live under the existing harness fixture tree or a sibling input fixture folder:

```text
dev/implementation/workflow-harness/fixtures/entrypoint-inputs/
  sample-assets-minimal.yaml
  malformed-missing-assets.yaml
  path-escape.yaml
  pt-and-social.yaml
```

Required checks:

1. CLI help:
   - `python3 dev/tools/run_workflow.py --help`
   - `python3 dev/tools/run_workflow.py analyze-propose --help`
2. Minimal scaffold:
   - Run `analyze-propose --input sample-assets-minimal.yaml --mode scaffold` into a temporary output root.
   - Assert parent root, child roots, manifests, indexes, scope files, packet files, and next-action files exist.
3. Determinism:
   - Run the same input twice in isolated temp dirs.
   - Assert normalized input, plan, task graph, packet content, and relative paths match byte-for-byte except for explicitly declared generated timestamps. Prefer no generated timestamps in deterministic files.
4. Path safety:
   - `artifact_root: ../../outside` fails with a P0-style input error and writes nothing outside the temp root.
5. Malformed input:
   - Missing `assets[]`, missing `objective.question`, or invalid `known_feeds` type fails before scaffold.
   - Error IDs are stable.
6. Stage skip logic:
   - Empty `pt_markets[]` and `social_scopes[]` produce explicit skipped markers and no S3/S4 worker packets.
7. Validator invocation:
   - `--mode validate` calls `validate_workflow_run.py` for child workflows and records report paths and exit codes.
8. P0/P1 surfacing:
   - Feed a known-bad fixture report and assert `next-action.json` groups P0 as `blocked` and P1 as `review_required`.
9. Prompt shrinkage:
   - Compute bytes/tokens for the old manual parent prompt baseline by concatenating `runbook.md`, `workflow.json`, `stage-contracts.md`, `subagent-prompts.md`, `output-structure.md`, and the hand-written scope block.
   - Compute bytes/tokens for the new path by concatenating the small input file plus `.workflow/next-action.md` plus one stage packet.
   - Assert the new packet surface is less than 25% of the baseline for the SampleBaseToken/SampleVaultToken fixture and does not include raw `subagent-prompts.md` content.
10. Existing regression:
    - Keep current checks passing:
      `python3 -m py_compile dev/tools/validate_workflow_run.py dev/tools/workflow_harness/tests/test_fixtures.py`
      `python3 -m pytest dev/tools/workflow_harness/tests/test_fixtures.py -q`

## Implementation slices

### Slice 1 — plan/scaffold only

Files likely touched later:

- `dev/tools/run_workflow.py` or `dev/tools/workflow_entrypoint.py`.
- `dev/tools/workflow_harness/tests/test_workflow_entrypoint.py`.
- `dev/implementation/workflow-harness/fixtures/entrypoint-inputs/`.

Deliverables:

- CLI help and input loading.
- Input schema validation with stable error IDs.
- Deterministic run root and child root derivation.
- Manifest/index/README/scope skeleton generation.
- Stage plan and packet generation.
- Next-action packet.
- No subagent launching.

### Slice 2 — validator bridge

Deliverables:

- `--mode validate` invokes existing validator for child and combined workflows.
- Report paths and P0/P1 summaries are written into `.workflow/validation/` and `next-action.json`.
- P0/P1 behavior blocks Preview/Execute gates.

### Slice 3 — agent launch adapters

Deliverables:

- Agent-specific packet rendering for Codex, Claude Code, Hermes, and generic terminal agents.
- Optional execution adapter; still bounded by generated packets and write scopes.
- Parent registry update from returned stage envelopes.

### Slice 4 — promote machine-readable runner metadata

Deliverables:

- Move transitional runner contracts into `workflow.json.runner_contract` once scaffold behavior is stable.
- Keep Markdown docs as human explanations and compact packet references, not parser-critical data.

## Acceptance criteria

A future implementation of this plan is acceptable when all criteria below pass:

1. `python3 dev/tools/run_workflow.py --help` exposes one canonical entrypoint and documents `analyze-propose --input <yaml/json>`.
2. A minimal SampleBaseToken/SampleVaultToken Gearbox input file produces deterministic parent and child run roots without a long prompt.
3. The runner creates parent `README.md`, `index.md`, `run-manifest.json`, `agentic-flow/analyze-and-propose.md` skeleton, child run manifests/indexes, per-scope directories, per-scope `scope.json`, verification directories, `.workflow/plan.json`, `.workflow/tasks.json`, and `.workflow/next-action.*`.
4. Generated child roots match existing `output-structure.md` layouts for `asset-investment-diligence` and `oracle-analysis`.
5. Stage packets resolve placeholders for run root, artifact dir, scope paths, prior artifact paths, known feeds, and validator commands.
6. Parent prompts no longer need to include full runbooks, full stage contracts, or full subagent prompts; packets cite those files by path/anchor.
7. `--mode validate` runs `dev/tools/validate_workflow_run.py` and surfaces P0 as blocked, P1 as review required, and P2 as warnings.
8. P0/P1 findings are reflected in `next-action.json`, parent `index.md`, and the final Analyze → Propose handoff; Preview/Execute stays blocked while they exist.
9. Path escape and overwrite attempts fail safely before writing outside the selected run root.
10. Smoke/e2e tests prove deterministic output and prompt shrinkage below 25% of the manual baseline for the SampleBaseToken/SampleVaultToken fixture.
11. Existing validator fixture tests continue to pass.
12. The runner never claims economic suitability, oracle quality, or live execution readiness; it only orchestrates artifacts, packets, and deterministic compliance gates.
