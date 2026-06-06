# M1 review — validator core CLI and machine-readable report schema

Scope: review `dev/implementation/workflow-harness/m1-validator-core-plan.md` as a formal workflow-compliance plan. This review checks schema stability, CLI/output safety, slice boundary, and acceptance coverage only. It does not assess token economic quality, oracle correctness, investment conclusions, or allocation suitability.

## Checked inputs

- `CLAUDE.md` project contract.
- `dev/implementation/workflow-harness/m1-validator-core-plan.md`.
- `dev/implementation/workflow-harness/hardened-plan.md`.
- `dev/implementation/workflow-harness/plan-review.md`.
- Downstream slice briefs for compatibility spot-checks:
  - `dev/implementation/workflow-harness/m2-asset-checks-plan.md`.
  - `dev/implementation/workflow-harness/m3-oracle-checks-plan.md`.
  - `dev/implementation/workflow-harness/m4-agentic-flow-plan.md`.
  - `dev/implementation/workflow-harness/m5-fixtures-docs-plan.md`.
- Gearbox/front-knowledge-base formal workflow critic and runtime workflow placement references.

## Executive verdict

Not approved for implementation as written.

The M1 brief has the right direction: it keeps the implementation slice narrow, avoids workflow prose changes, defines a deferred-check guard so the core CLI cannot return a false production `pass`, and specifies a compact report schema. The blockers are acceptance and contract-stability gaps. They can let the first implementation create an apparently stable validator interface while leaving output modes, path safety, canonical verification protection, and downstream schema compatibility unproven.

## P1 findings

### P1-1 — Stable report schema is not protected against downstream drift

Evidence:

- M1 defines `workflow-harness-report-v1` with stable top-level keys, canonical workflow IDs, `status` values `pass | review_required | fail`, finding `id`, and severity values `P0 | P1 | P2` (`m1-validator-core-plan.md:115-163`).
- M1 explicitly positions itself as the stable validator entry point before M2-M6 add real workflow checks (`m1-validator-core-plan.md:111`).
- The current M2 brief shows a different shape: `status: pass | warning | fail`, severities `blocker | error | warning`, and finding field `check_id` (`m2-asset-checks-plan.md:50-63`).
- The current M3 brief also uses `check_id` in its example and fixture assertions, while M1 uses `id` (`m3-oracle-checks-plan.md:69-75`, `m3-oracle-checks-plan.md:365-368`).

Risk:

The first implementation can satisfy M1 but leave later workers with incompatible report contracts. That breaks the purpose of M1 as a stable machine-readable schema and can make fixture matrix checks accept mixed `id` / `check_id`, mixed severity vocabularies, or status values that do not reconcile with the M1 exit-code model.

Required plan change:

Add a non-negotiable schema compatibility section to M1:

- `schema_version` remains `workflow-harness-report-v1` until explicitly versioned.
- Findings use `id` as the canonical machine field. If a compatibility alias is intentionally allowed, define it explicitly and require the canonical `id` in every finding.
- Severity values remain `P0`, `P1`, and `P2`.
- Status values remain `pass`, `review_required`, and `fail`.
- Downstream slices must extend the `summary`, `findings`, and `checks` arrays without changing existing top-level semantics.

Acceptance should include a schema self-check that asserts these fields on at least one P1 report and one P0 report, including every finding key required by the M1 shape.

### P1-2 — Output-mode and generated-file behavior is specified but under-tested

Evidence:

- The CLI contract includes `--format json`, `--format markdown`, `--format json,markdown`, `--report-dir`, `--write-verification`, and `--strict-warnings` (`m1-validator-core-plan.md:62-67`).
- The output contract requires JSON stdout, Markdown stdout, JSON-with-embedded-Markdown when `json,markdown` has no destination, deterministic `--report-dir` files, and generated verification files (`m1-validator-core-plan.md:83-94`).
- The report schema includes `rendered_outputs` (`m1-validator-core-plan.md:145-146`), but the M1 JSON acceptance required-key set omits it (`m1-validator-core-plan.md:355-356`).
- The acceptance commands cover JSON stdout and `--write-verification`; they do not cover Markdown-only stdout, `json,markdown` without a destination, or `--report-dir` JSON plus Markdown output.

Risk:

A future implementation can pass M1 while violating one of the user-facing and machine-facing output contracts. The highest-risk false pass is mixed stdout for `json,markdown`, because parent agents and fixture wrappers need stdout to stay parseable JSON.

Required plan change:

Promote output-mode assertions into M1 acceptance:

1. `--format markdown` prints Markdown, not JSON.
2. `--format json,markdown` with no destination prints parseable JSON to stdout and includes `rendered_outputs.markdown` with the required Markdown markers.
3. `--report-dir <tmp>` writes `workflow-harness-report.json` and `workflow-harness-verification.md`, records both in `generated_files`, and keeps stdout parseable JSON.
4. The top-level required-key set includes `rendered_outputs`.
5. A generated JSON file and stdout JSON have the same `schema_version`, `status`, `exit_code`, `summary`, and finding IDs.

### P1-3 — Path-safety helpers are part of M1 but not proven by acceptance

Evidence:

- M1 requires `resolve_under_root(...)` to reject absolute paths, parent-escaping paths, and malformed values, and to resolve source-relative paths correctly (`m1-validator-core-plan.md:213-217`).
- M1 also defines `run_root.exists` as a P0 check for missing or non-directory run roots (`m1-validator-core-plan.md:192-194`).
- Current acceptance tests missing and invalid manifests, but not a missing/non-directory `--run-root`, not absolute/parent-escaping path helper behavior, and not source-relative path resolution.

Risk:

Path normalization is the common helper that later M2-M5 checks depend on for manifest paths, local links, code-spanned artifact paths, and sibling-run drift. If M1 accepts a weak helper, later semantic checks may look correct while still allowing parent escapes or resolving nested links from the wrong base.

Required plan change:

Add an import-level helper acceptance block that directly exercises `resolve_under_root(...)` and `repo_relative(...)`:

- in-root relative path succeeds;
- `../escape.md` fails;
- `/absolute/path.md` fails;
- `source_file=run_root / "tokens/t/analyst-report.md"` resolves `verification.md` against `tokens/t/`, not the run root;
- missing or file-valued `--run-root` emits P0 `run_root.exists` and exits `2`.

If symlink traversal is intentionally out of scope for M1, the brief should state that boundary and leave a later check ID for it.

### P1-4 — Canonical final-verification protection is not fully accepted

Evidence:

- M1 instructs output handling to include canonical-final-verification protection (`m1-validator-core-plan.md:303`).
- The `--write-verification` acceptance asserts that `verification/workflow-harness-verification.md` is created and that a missing canonical final verification file is not created (`m1-validator-core-plan.md:431-441`).
- The acceptance does not pre-create `verification/final-oracle-analysis-verification.md` or `verification/final-investment-analysis-verification.md` with sentinel content and then prove it was not overwritten.

Risk:

A validator implementation can pass the current acceptance while still overwriting an existing canonical final verification file in real runs. That is a destructive artifact risk in a documentation vault and conflicts with the requirement that the harness write its own report rather than mutate canonical final verification.

Required plan change:

Add one acceptance case that pre-creates the canonical final verification file with sentinel content, runs `--write-verification`, and asserts:

- sentinel content is unchanged;
- only `verification/workflow-harness-verification.md` is created or modified;
- `generated_files` lists the harness report path and does not list the canonical final verification path.

### P1-5 — Combined-run M1 behavior needs an explicit acceptance case

Evidence:

- M1 says `manifest.file_exists` is skipped for combined runs with message `combined manifest deferred until M5` (`m1-validator-core-plan.md:194`).
- M1 says combined runs should not attempt child validation and should emit deferred child-validation checks honestly (`m1-validator-core-plan.md:198`).
- Current acceptance only covers asset/oracle common-core runs and an oracle `--write-verification` path. It does not run `--workflow combined-analyze-propose`.

Risk:

A future implementation can incorrectly require `run-manifest.json` for combined runs, attempt child validation before M4/M5 exists, or return a misleading pass/skipped state. That would make M1 incompatible with the combined post-Discover flow it is supposed to support later.

Required plan change:

Add a combined-run acceptance case using a temporary run root with no manifest:

- command uses `--workflow combined-analyze-propose --format json`;
- exit code is `1` because `validator.workflow_checks_deferred` is present;
- no P0 `manifest.file_exists` finding is emitted;
- `checks` contains a skipped `manifest.file_exists` or child-validation check with the M1 deferred message.

## P2 observations

### P2-1 — The single-file M1 scope is acceptable but should be named as temporary architecture

The M1 plan narrows implementation to `dev/tools/validate_workflow_run.py`, while the hardened plan originally allowed a package and test files. The single-file scope is not a blocker because M2 also expects the validator to remain self-contained for now. The plan should still state that helper functions are intentionally colocated only until a later refactor task authorizes a package tree. That prevents implementers from treating the single-file shape as the long-term design.

### P2-2 — `--strict-warnings` has no proving case in M1

M1 may not emit any P2 findings yet, so this is not a blocker. If the flag remains in the M1 CLI, the plan should either add a tiny synthetic P2 check for acceptance or state that `--strict-warnings` behavior becomes testable in the first slice that emits P2 findings.

## Slice-scope assessment

Safe scope:

- M1 does not modify runtime workflow prose.
- M1 does not assess economic, oracle, investment, or allocation quality.
- M1 keeps real asset/oracle/combined semantic checks deferred and visible through `validator.workflow_checks_deferred`.

Unsafe or under-accepted scope:

- Output generation writes files but lacks enough acceptance around all write modes.
- Path helper behavior becomes shared infrastructure before it is tested.
- The schema is declared stable but not protected against already-visible downstream drift.

## Blocking fixes before approval

1. Add schema compatibility acceptance and make M2-M5 extension rules explicit: canonical `id`, `P0/P1/P2`, `pass/review_required/fail`, stable top-level keys, and versioning rules.
2. Add output-mode acceptance for `markdown`, `json,markdown` without destination, and `--report-dir`, including `rendered_outputs` and `generated_files` assertions.
3. Add path-safety/helper acceptance for `run_root.exists`, absolute paths, parent escapes, and source-relative resolution.
4. Add canonical final-verification non-overwrite acceptance with sentinel content.
5. Add a combined-run M1 acceptance case proving manifest and child validation remain deferred, not failed or falsely passed.

## Final review decision

approved: false

Reason: the M1 plan is directionally sound, but it does not yet prove the machine-readable schema and CLI/output contracts that later slices must build on. The listed blocking fixes are acceptance-level and contract-wording changes; they should be small enough to add without expanding implementation beyond the core CLI/report slice.
