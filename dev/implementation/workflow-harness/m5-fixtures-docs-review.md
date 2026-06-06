# M5 review — fixtures, runbooks, and external-agent handoff instructions

Scope: review `dev/implementation/workflow-harness/m5-fixtures-docs-plan.md` for formal workflow-compliance only. This review checks missing checks, unsafe scope, and acceptance gaps. It does not assess token economic quality, oracle correctness, allocation suitability, or live execution quality.

## Checked inputs

- `CLAUDE.md`.
- `dev/implementation/workflow-harness/m5-fixtures-docs-plan.md`.
- `dev/implementation/workflow-harness/m1-validator-core-plan.md`.
- `dev/implementation/workflow-harness/m2-asset-checks-plan.md`.
- `dev/implementation/workflow-harness/m3-oracle-checks-plan.md`.
- `dev/implementation/workflow-harness/m4-agentic-flow-plan.md`.
- `dev/implementation/workflow-harness/hardened-plan.md`.
- `dev/implementation/workflow-harness/plan-review.md`.
- `user/references/workflows/asset-investment-diligence/runbook.md`.
- `user/references/workflows/asset-investment-diligence/output-structure.md`.
- `user/references/workflows/oracle-analysis/runbook.md`.
- `user/references/workflows/oracle-analysis/output-structure.md`.
- Gearbox front-knowledge-base formal workflow critic and runtime workflow placement references.

## Executive verdict

Not approved for implementation as written.

The plan has the right formal direction: it keeps economic and oracle-quality judgments out of scope, promotes the prior negative fixture classes into required acceptance, and adds an external-agent completion rule near final verification. The blocking issues are fixture executability and report-contract precision. As written, an implementation worker could create only README/matrix files, update runbooks, and still be unable to satisfy the plan's own validator acceptance commands.

## P1 findings

### P1-1 — Fixture file list is not sufficient to make the fixture matrix runnable

Evidence:

- The plan's required create list names only the fixture root README, `fixture-matrix.json`, and one README per fixture (`m5-fixtures-docs-plan.md:39-50`).
- The same plan later requires the matrix wrapper to run `dev/tools/validate_workflow_run.py` against every fixture `run_root`, assert each fixture's expected exit code/status, and assert expected finding ids (`m5-fixtures-docs-plan.md:224-240`).
- The happy-path fixture is expected to exit `0` with status `pass` (`m5-fixtures-docs-plan.md:97`). A README-only fixture cannot satisfy the asset, oracle, combined-flow, final-verification, local-link, and parent-handoff contracts.
- The fallback sentence, "If a fixture needs sample run content, keep it minimal and local to that fixture directory" (`m5-fixtures-docs-plan.md:115`), is too vague for an implementation slice whose acceptance depends on deterministic fixture content.

Risk:

The implementation can follow the exact file list and produce fixtures that are descriptive but not executable. The acceptance wrapper would then fail on unintended missing-file findings, or the good fixture would fail before it reaches the checks the fixture is supposed to protect.

Blocking fix:

Expand the M5 plan with a minimal physical fixture tree for each required fixture. At minimum, specify the required `run-manifest.json`, `index.md`/`README.md`, canonical `verification/*` files, child asset/oracle roots for the combined fixture, `agentic-flow/analyze-and-propose.md`, and any per-token/per-scope stub files needed to reach the intended finding id. Keep the content tiny, but make every fixture runnable from the matrix.

### P1-2 — Harness report filenames in output-structure updates conflict with the validator/report contract

Evidence:

- M5 tells both output-structure files to add `verification/workflow-harness-report.json` and `verification/workflow-harness-report.md` (`m5-fixtures-docs-plan.md:160-176`).
- The M5 runbook command uses `--format json,markdown --write-verification` but does not pass `--report-dir` (`m5-fixtures-docs-plan.md:126-132`, `m5-fixtures-docs-plan.md:145-150`).
- The M1 validator core plan defines report filenames differently: `--report-dir` writes `workflow-harness-report.json` and `workflow-harness-verification.md`, while `--write-verification` writes Markdown under `verification/workflow-harness-verification.md` for asset/oracle runs and `verification/combined-analyze-propose-verification.md` for combined runs (`m1-validator-core-plan.md:86-91`). It also says JSON is printed to stdout for `--format json` / `json,markdown`, not necessarily persisted under `verification/` unless report writing is requested.

Risk:

The runtime workflow docs would require files that the planned CLI does not write in the command shape shown to agents. Future agents could be told to link `workflow-harness-report.md` while the actual harness creates `workflow-harness-verification.md`, or to preserve a JSON report under `verification/` when the command only printed JSON to stdout.

Blocking fix:

Choose one contract and make the plan internally consistent. Either:

1. change the runbook command to pass `--report-dir <run_artifact_root>/verification` and use the validator's deterministic `workflow-harness-report.json` plus `workflow-harness-verification.md` names; or
2. revise the validator/report contract before this slice so `--write-verification` actually emits `workflow-harness-report.json` and `workflow-harness-report.md` under `verification/`.

Do not update runtime output structures until the command, generated filenames, and final-verification link text all agree.

### P1-3 — Parent-return fixture requirements are under-specified for the good combined fixture and parent-return negative fixture

Evidence:

- The fixture matrix schema allows `parent_return` but only conditionally adds `--parent-return` when the row supplies it (`m5-fixtures-docs-plan.md:77-90`, `m5-fixtures-docs-plan.md:231-232`).
- The required good combined fixture row expects exit `0`, status `pass`, and protects parent handoff/final verification references (`m5-fixtures-docs-plan.md:97`).
- The hardened combined-flow contract says that if no parent-return artifact is supplied, the report must include P1 `parent_return.needs_parent_verification` and must not claim the parent response was validated (`hardened-plan.md:211`). That behavior is incompatible with an exit `0` good combined fixture unless the fixture row supplies a valid parent-return artifact.
- The `bad/missing-parent-return-status` row expects both `parent_return.contract_fields_present` and `parent_return.status_reconciles_children` (`m5-fixtures-docs-plan.md:104`), but the plan does not say whether the row omits `parent_return`, points to a malformed JSON artifact, or points to a semantically inconsistent artifact.

Risk:

The good combined fixture may fail with `parent_return.needs_parent_verification`, or the bad parent-return fixture may exercise absence rather than contract-field/status reconciliation. Either outcome weakens the main false-pass guard the slice is meant to prove.

Blocking fix:

Specify exact parent-return artifacts in the matrix:

- `good/good-agentic-sample-assets` must include a valid `parent_return` path, for example `agentic-flow/parent-return.json`, and that artifact must reconcile with child statuses and final verification paths.
- `bad/missing-parent-return-status` must include a concrete malformed or inconsistent `parent_return` artifact when the expected finding ids are `parent_return.contract_fields_present` and `parent_return.status_reconciles_children`.
- If the intended absence case should also be covered, add a separate fixture expecting `parent_return.needs_parent_verification` and `review_required`, not `pass`.

## P2 findings

### P2-1 — The prerequisite gate is directionally right but should be an explicit preflight command

Evidence:

- The plan correctly says implementation should block if `dev/tools/validate_workflow_run.py` or relevant harness tests are absent (`m5-fixtures-docs-plan.md:35`).
- Current workspace preflight during this review found these files/directories absent: `dev/tools/validate_workflow_run.py`, `dev/tools/workflow_harness/tests/test_fixtures.py`, `dev/tools/workflow_harness/tests`, and `dev/tools/workflow_harness/fixtures`.

Risk:

A future worker may start the docs/runbook changes before the harness exists, creating runtime docs that claim validator behavior before it is executable.

Recommended fix:

Add a short preflight command to the M5 plan before any file edits:

```bash
test -f dev/tools/validate_workflow_run.py
test -f dev/tools/workflow_harness/tests/test_fixtures.py
python3 dev/tools/validate_workflow_run.py --help >/dev/null
```

If any command fails, the implementation task should block with the missing prerequisite instead of editing runbooks or output structures.

### P2-2 — Fixture location should be reconciled with earlier harness paths before implementation

Evidence:

- M5 places the docs/data fixture battery under `dev/implementation/workflow-harness/fixtures/` (`m5-fixtures-docs-plan.md:23`, `m5-fixtures-docs-plan.md:41-50`).
- Earlier hardened implementation milestones place validator fixtures under `dev/tools/workflow_harness/fixtures/**` and tests under `dev/tools/workflow_harness/tests/**` (`hardened-plan.md:221-228`).
- The M2/M3 slice plans also allow optional fixture metadata under `dev/implementation/workflow-harness/fixtures/**`, so this may be intentional, but the plan does not explain whether the test suite consumes implementation fixtures, tool fixtures, or both.

Risk:

The repository can end up with two fixture surfaces whose expectations drift: implementation-review fixtures under `dev/implementation/` and validator-regression fixtures under `dev/tools/`.

Recommended fix:

Add one sentence defining the source of truth: either `dev/implementation/workflow-harness/fixtures/fixture-matrix.json` is the canonical external-agent fixture matrix consumed by `test_fixtures.py`, or M5 should create/mirror the runnable fixtures under `dev/tools/workflow_harness/fixtures/` and keep `dev/implementation/` as planning lineage only.

## Positive notes

- The scope boundary is safe: it explicitly excludes validator implementation, economic judgment, oracle-quality judgment, and broad workflow rewrites (`m5-fixtures-docs-plan.md:19-35`).
- The acceptance wrapper correctly asserts expected nonzero exit codes instead of putting raw failing validator commands in a shell block (`m5-fixtures-docs-plan.md:203-241`). This resolves the earlier plan-review acceptance concern.
- The external-agent completion rule is placed near final verification and requires P0 fixes, P1 visibility, command/cwd/exit-code evidence, and unresolved finding ids (`m5-fixtures-docs-plan.md:180-188`). That is the right behavior change once the report filename and fixture executability blockers are fixed.

## Blocking fixes required before approval

1. Specify the minimal runnable artifact tree for every required fixture, not only README/matrix files.
2. Align runbook/output-structure report filenames with the actual validator command and generated outputs.
3. Require explicit parent-return artifacts for the good combined fixture and parent-return negative fixture, with expected findings matched to the chosen absence/malformed/inconsistent case.

approved: false
