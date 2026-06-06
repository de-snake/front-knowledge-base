# Formal review — M2 asset-investment-diligence harness checks

Scope: review `dev/implementation/workflow-harness/m2-asset-checks-plan.md` for missing checks, unsafe scope, and acceptance gaps. This review is formal workflow-compliance only. It does not assess token economic quality, oracle correctness, allocation suitability, or whether any report conclusion is persuasive.

## Executive verdict

Not approved for implementation as written.

The plan targets the right asset-workflow surfaces: manifest/schema reconciliation, required token files, S1/S2 section coverage, S6 exact quantitative fields, skipped PT/social markers, and final-verification overclaim checks. However, it has two blocking implementation-safety gaps:

1. It defines a CLI/report/exit-code contract that conflicts with the M1 validator-core contract.
2. Its acceptance path can pass with only negative fixtures, so an always-failing validator or an uncleared M1 deferred-check finding would not be caught.

A third gap should be fixed or explicitly deferred: the plan does not fully cover S7 cross-link and workspace-validation requirements even though it validates the final verification file.

## Checked inputs

- `CLAUDE.md` — project contract and canonical `Discover → Analyze → Propose → Preview → Execute → Monitor` loop.
- `user/references/workflows/asset-investment-diligence/output-structure.md` — required run folder, manifest, index, token, PT, social, investment-analysis, and final-verification paths.
- `user/references/workflows/asset-investment-diligence/stage-contracts.md` — S1, S2, S6, and S7 contracts.
- `user/references/workflows/asset-investment-diligence/runbook.md` — run execution and artifact-return expectations.
- `dev/implementation/workflow-harness/m1-validator-core-plan.md` — CLI/report/status baseline for later slices.
- `dev/implementation/workflow-harness/hardened-plan.md` and `plan-review.md` — prior false-pass and path/link review context.
- Existing partial asset run: `dev/implementation/asset-diligence-2026-06-05-sample-base-token-sample-vault-token/`.
- Gearbox formal workflow critic and front-knowledge-base runtime workflow placement references.

## Blocking findings

### P0-1 — M2 report and exit-code contract drifts from M1

Evidence:

- M1 defines the reusable CLI/report contract with `schema_version`, `workflow`, `run_root`, `status`, `exit_code`, `summary`, `findings`, and `checks`; findings use `id` and severities `P0`, `P1`, `P2` (`m1-validator-core-plan.md:96-184`).
- M1 status policy is `fail` for P0 / exit `2`, `review_required` for P1 / exit `1`, and `pass` for clean or non-strict P2 (`m1-validator-core-plan.md:96-111`).
- M2 redefines the report shape with `status: pass | warning | fail`, `severity: blocker | error | warning`, and `check_id` (`m2-asset-checks-plan.md:50-71`).
- M2 acceptance examples also expect `finding["check_id"]` and exit `2` for contract/false-pass failures that are P1-class under M1.

Why this blocks implementation:

Following M2 literally would either break the M1 core schema/tests or force the implementer to maintain two incompatible report dialects in the same script. It also changes the meaning of contract failures from `review_required` / exit `1` to `fail` / exit `2`, which loses the distinction between structural invalidity and review-required false-pass risk.

Blocking fix:

- Align M2 to M1 before implementation:
  - use `id`, not `check_id`;
  - use `P0`, `P1`, `P2`, not `blocker`, `error`, `warning`;
  - use `status: pass | review_required | fail`, not `warning`;
  - keep `exit_code`, `summary`, and `checks` in the JSON report;
  - map malformed JSON, unsafe paths, and missing declared required files to P0 / exit `2`;
  - map missing required content fields, S6 heading-only overclaims, skipped-stage omissions, and final-verification overclaims to P1 / exit `1` unless the plan explicitly justifies P0.
- Update all M2 acceptance snippets and fixture metadata to inspect `finding["id"]`.
- State exactly when the M1 `validator.workflow_checks_deferred` finding is removed or scoped away for `asset-investment-diligence` after M2 passes.

### P0-2 — Negative-only acceptance can miss an always-failing validator

Evidence:

- M2 fixture metadata lists `asset-good-token-only/metadata.json`, but the recommended mapping makes the good fixture conditional: use a known-good root only “if available” (`m2-asset-checks-plan.md:326-337`).
- The plan says that if stable fixture roots are not available, the implementer may rely on targeted negative assertions and inline temporary-fixture assertions in the handoff (`m2-asset-checks-plan.md:335-337`).
- The mandatory acceptance sections exercise existing partial bad cases for missing exact S6 fields and skipped PT/social markers. They do not require a deterministic positive pass case.

Why this blocks implementation:

A validator that always emits one P1/P0 finding could satisfy the negative checks. The acceptance path would also miss the case where M2 correctly implements asset checks but leaves M1’s `validator.workflow_checks_deferred` finding active for asset runs, causing no compliant asset run to pass.

Blocking fix:

- Require one deterministic positive acceptance case in M2, not optional M5 work.
- The positive case can be generated inside a temporary directory by the acceptance script; it does not need to edit historical run artifacts. It must include:
  - one valid `run-manifest.json` with one token;
  - all required root files;
  - all required token files;
  - explicit skipped markers and reasons for S3, S4, and S5 when PT/social scopes are absent;
  - exact S6 fields with numeric values or allowed non-numeric value states plus reasons;
  - a final verification file that names required file checks, exact field checks, skipped-stage checks, command evidence, and non-execution-ready status where applicable.
- Assert `exit_code == 0`, `status == "pass"`, no M2 P1/P0 findings, and no remaining `validator.workflow_checks_deferred` for `asset-investment-diligence` once M2 is considered complete.

## Required fix or explicit deferral

### P1-1 — S7 final-verification coverage is incomplete

Evidence:

- S7 requires final verification to check required files, per-token/per-PT folder structure, cross-links, required sections, quantitative fields, unsupported allocation conclusions, and workspace validation (`stage-contracts.md:314-340`).
- M2 final-verification checks cover existence, status marker, required file checks, required field checks, skipped-stage checks, command evidence, overclaim detection, and unsupported execution-ready claims (`m2-asset-checks-plan.md:280-304`).
- M2 does not require final verification to record cross-link resolution or workspace-validation status, and it does not check the `README.md` / `index.md` content contract from `output-structure.md:107-127`.
- The existing partial asset run contains sibling-run links such as `../oracle-analysis-2026-06-05-sample-base-token-sample-vault-token/` from `investment-analysis/investment-analyst-report-points-pt-risk-return.md:85-90`; broken sibling-run paths are a known formal failure class.

Why this matters:

If M2 reports a clean asset-workflow pass while S7 link validation or workspace-validation evidence is absent, the harness can still false-pass the final verification layer that it claims to validate.

Required change:

Either:

1. Add deterministic M2 checks for these S7 fields:
   - final verification records cross-link resolution;
   - final verification records workspace-validation command status or an explicit unrelated-failure isolation;
   - `README.md` points to `run-manifest.json` and final validation status;
   - `index.md` includes artifact map and final verification status.

or:

2. Explicitly defer these checks to a later slice and make M2 emit a P1 deferred-check finding so M2 cannot return a production `pass` for a full asset run until S7 coverage is complete.

## Non-blocking hardening notes

- `Compound annualized return, when relevant` needs a deterministic rule. Prefer requiring the field always, with either a numeric value or an allowed state such as `not_in_scope` plus reason. Otherwise an implementer may silently skip it.
- `asset.pt_social.full_validation_out_of_scope` should be P2 when PT/social scopes are non-empty and full validation is deferred, unless the run or final verification claims those scopes passed. If a pass is claimed without validation, escalate to P1.
- The plan should state that M2 is intentionally re-slicing part of the hardened plan’s M3 content into an asset-only M2, or rename the slice to avoid confusion with `hardened-plan.md` where M2 is manifest/path only and Markdown contract checks are M3.

## Blocking fixes required before approval

1. Rewrite the CLI/report/exit-code section and all acceptance snippets to match the M1 report contract.
2. Add a mandatory positive fixture or temporary-good-run acceptance assertion.
3. Specify how M2 clears or scopes `validator.workflow_checks_deferred` for asset-investment-diligence.
4. Add S7 cross-link/workspace-validation/README/index checks or explicitly defer them with a non-pass finding.
5. Make the `Compound annualized return` relevance rule deterministic.

approved: false
