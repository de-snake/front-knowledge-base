# P6 final board handoff — workflow entrypoint readiness

Task: `t_78a6803e`

Verdict: READY for bounded scaffold and validation use by Codex, Claude Code, and Hermes.

This is not a Preview, Execute, live-research, economic-underwriting, oracle-quality, or Credit Account opening readiness harness. It is ready only for the P1–P5 acceptance scope: one compact input file creates deterministic Analyze → Propose run folders, agent packets, skeleton artifacts, and validation status without moving long workflow prompts into the launcher prompt.

## One entrypoint command

```bash
python3 dev/tools/run_workflow.py analyze-propose \
  --input dev/implementation/workflow-harness/fixtures/entrypoint-inputs/sample-assets-minimal.json \
  --mode scaffold \
  --agent <generic|codex|claude-code|hermes> \
  --format <json|markdown>
```

Operational notes:

- `--mode scaffold` creates the parent run root and child workflow roots.
- `--mode validate --resume --run-root <run-root-under-dev/implementation>` imports validator results back into `.workflow/validation/` and `.workflow/next-action.*`.
- `--run-root` is optional; the default root is deterministic: `dev/implementation/analyze-propose-<primary-scope>-<input-sha8>/`.
- The runner is standard-library-only and does not launch subagents.

## Input schema and sample

- Real user-requested asset inputs should be temporary repo-local files under `dev/implementation/workflow-harness/tmp/inputs/`.
- Do not use `dev/inputs/` for one-off asset runs or promote scratch inputs into permanent fixtures unless explicitly requested.
- Schema constant: `dev/tools/workflow_entrypoint_contracts.py` → `SCHEMA_VERSION = "workflow-entrypoint-input-v1"`.
- Minimal stable fixture input: `dev/implementation/workflow-harness/fixtures/entrypoint-inputs/sample-assets-minimal.json`.
- Additional stable fixtures:
  - `dev/implementation/workflow-harness/fixtures/entrypoint-inputs/missing-live-fields.json`
  - `dev/implementation/workflow-harness/fixtures/entrypoint-inputs/malformed-missing-assets.json`
  - `dev/implementation/workflow-harness/fixtures/entrypoint-inputs/path-escape-artifact-root.json`

The minimal sample is 78 lines / 2,930 bytes in P5 evidence. Missing live values remain `null` or `not_available` and are surfaced as blocking unknowns; the runner must not invent addresses, prices, APRs, feed verdicts, or suitability conclusions.

## File management, substeps, sections, and verification behavior

File management:

- `--input` must resolve inside the vault.
- `--run-root` must resolve under `dev/implementation/`.
- All writes are guarded to remain under the selected run root.
- Existing run roots require `--resume`, and resume is allowed only when `.workflow/input.normalized.json` matches the current input hash.
- Path-escape inputs fail with stable P0 ID `WE_PATH_ESCAPE`.

Generated root shape:

- Parent files include `README.md`, `index.md`, `run-manifest.json`, `agentic-flow/analyze-and-propose.md`, `.workflow/input.normalized.json`, `.workflow/plan.json`, `.workflow/tasks.json`, `.workflow/registry.json`, `.workflow/next-action.json`, and `.workflow/next-action.md`.
- Child roots are `asset-investment-diligence/` and `oracle-analysis/`.
- Packets are written as both JSON and Markdown under `.workflow/packets/<workflow>/`.

Substeps:

- Asset diligence stages: `S1_general_asset_mining`, `S2_asset_risk_analyst_report`, `S6_quantitative_underwriting`, `S7_final_verification`.
- Asset PT and social stages are explicitly skipped when `pt_markets` and `social_scopes` are empty.
- Oracle stages: `S0_scope_and_acceptance` through `S6_final_verification` for each oracle scope.

Packet section contract:

- Every Markdown packet includes `## Scope`, `## Known inputs`, `## Blocking unknowns`, `## Work to perform`, `## Required outputs`, `## Validation command`, and `## Return envelope`.
- JSON packets use `packet_schema = workflow-stage-packet-v1`.
- The canonical `task_payload` is byte-identical across `generic`, `codex`, `claude-code`, and `hermes`; only the sibling `launcher` object changes.

Validation behavior:

- Validate mode runs the asset, oracle, and combined Analyze → Propose validators.
- Results are written under `.workflow/validation/summary.json`, `.workflow/validation/summary.md`, and refreshed `.workflow/next-action.*` files.
- Exit semantics are `0 = pass`, `1 = review_required`, and `2 = blocked or input error`.
- P0 findings are intentionally surfaced; incomplete scaffold validation is expected to return exit `2` rather than hide missing artifacts.

## P5 evidence read for this handoff

P5 verdict: PASS after combined-validator repair.

Evidence paths:

- `/tmp/p5-verify-t_58c75224-retry-20260605T232852Z/verification-summary.md`
- `/tmp/p5-verify-t_58c75224-retry-20260605T232852Z/verification-summary.json`
- `/Users/ilya/Documents/Codex/front-knowledge-base/dev/implementation/workflow-harness/tmp/p5-verify-t_58c75224-retry-20260605T232852Z/.workflow/validation/summary.json`
- `/Users/ilya/Documents/Codex/front-knowledge-base/dev/implementation/workflow-harness/tmp/p5-verify-t_58c75224-retry-20260605T232852Z/verification/workflow-harness-report.json`

P5 commands and results supporting readiness:

- `python3 -m py_compile ...` → exit `0`.
- `python3 dev/tools/run_workflow.py --help` → exit `0`.
- `python3 dev/tools/run_workflow.py analyze-propose --help` → exit `0`.
- Fresh scaffold run with the minimal input and `--agent hermes --format json` → exit `0`, status `scaffolded`, 93 files written.
- Validate of the intentionally incomplete scaffold → exit `2`, status `blocked`, 14 P0 findings surfaced.
- `python3 dev/tools/run_fixture_checks.py` → exit `0`, fixture matrix 5/5 and workflow entrypoint 9/9.
- `python3 -m unittest dev.tools.workflow_harness.tests.test_workflow_entrypoint` → exit `0`, 9 tests passed.
- Known-bad combined fixture validation → exit `2`, status `fail`, first findings include `flow.propose_handoff_exists` and `links.local_paths_resolve`.
- Scoped `git diff --check` for the runner, docs, tests, and input fixture files → exit `0`.

P5 remaining gap: `pytest` is not installed for `/Library/Developer/CommandLineTools/usr/bin/python3`; the repository-provided pytest-free smoke checks and direct unittest checks passed.

## Current git-diff state observed in P6

The current worktree is not clean. P6 observed:

- Full `git status --short`: 197 entries total — 183 deleted, 7 modified, 7 untracked.
- Full tracked `git diff --name-status`: 190 files.
- Scoped workflow paths have no tracked diff yet: `workflow_tracked_diff_files = 0`.
- The entrypoint/harness/workflow package paths are currently untracked roots:
  - `dev/implementation/workflow-entrypoint/`
  - `dev/implementation/workflow-harness/`
  - `dev/tools/`
  - `user/references/mechanics/`
  - `user/references/workflows/`

This verdict is therefore scoped to the P1–P5 workflow-entrypoint harness evidence. It is not a claim that the full repository diff is reviewed or ready to merge.

## Readiness by agent

Codex: ready to receive a Markdown packet path from `.workflow/next-action.md`. The packet contains the full stage payload and Codex-specific launcher text.

Claude Code: ready to receive the same packet path. The canonical task payload is invariant; Claude Code-specific wording is limited to the launcher hint.

Hermes: ready to receive the same packet path. Hermes-specific wording is limited to the launcher hint and does not add separate workflow semantics.

Generic agents: supported through the same packet schema and `generic` launcher hint.

## Unresolved limitations and gates

- The runner does not execute live research, market-data retrieval, X research, RPC calls, or web discovery.
- The runner does not produce an economic suitability verdict, oracle-quality verdict, allocation recommendation, Preview package, Execute package, or Credit Account opening readiness verdict.
- The runner scaffolds child workflows and imports validator output; it does not manage long-running agent orchestration or board task creation.
- `pytest` remains unavailable in the system Python used by P5; keep the pytest-free checks as the acceptance gate unless the environment adds pytest intentionally.
- The broad repository worktree has unrelated uncommitted changes and deletions. Merge readiness requires a separate diff review.

## Final handoff

Use `dev/implementation/workflow-entrypoint/run-workflow-usage.md` as the operator-facing usage note and this file as the board-level readiness summary.

Final verdict: the harness is ready for the bounded scaffold-and-validate entrypoint contract verified in P5. It is not ready, and does not claim to be ready, for autonomous live underwriting, Preview, Execute, or state-changing operations.
