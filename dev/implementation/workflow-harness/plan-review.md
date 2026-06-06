# Formal review — workflow harness plan

Scope: review `dev/implementation/workflow-harness/plan.md` as a formal verifier. This review only checks workflow contract coverage, fixture adequacy, path/link validation, final-verification false-pass risk, implementation scope, and acceptance commands. It does not assess token economic quality, oracle correctness, investment conclusions, or user suitability.

## Checked inputs

- `CLAUDE.md` project contract, especially the `user/` versus `dev/` split and linking conventions.
- `dev/implementation/workflow-harness/plan.md`.
- `dev/implementation/workflow-harness/internal-audit.md`.
- `dev/implementation/workflow-harness/external-harness-research.md`.
- `user/references/workflows/asset-investment-diligence/output-structure.md` and `stage-contracts.md`.
- `user/references/workflows/oracle-analysis/output-structure.md` and `stage-contracts.md`.
- Gearbox front-knowledge-base formal workflow critic and agentic token/oracle workflow run references.

## Executive verdict

Not approved for implementation as written.

The plan has the right high-level direction: deterministic local validation, separate asset/oracle/combined modes, canonical final-verification protection, and a small fixture tree. The remaining gaps are formal harness issues rather than economic or oracle-quality issues. They can cause a false pass for manifest drift, parent-return drift, root status mismatch, or untested stage-gate failures.

## P1 findings

### P1-1 — Manifest entry schema and path reconciliation are under-specified

Evidence:

- The asset workflow `run-manifest.json` contract requires not only top-level fields but per-token entries with `token_id`, `chain`, `symbol`, `address`, `artifact_dir`, and `status` (`asset-investment-diligence/output-structure.md:83-103`).
- The oracle workflow has the same pattern for per-scope entries, including `artifact_dir` and `status` (`oracle-analysis/output-structure.md:88-111`).
- The plan only names top-level manifest required fields for asset runs (`plan.md:223-225`) and oracle runs (`plan.md:256-260`). It then checks that token/scope files exist (`plan.md:229`, `plan.md:264`) and that local paths resolve (`plan.md:232`, `plan.md:266`).

Risk:

A run can pass with a malformed manifest entry, stale `artifact_dir`, wrong token address/scope mapping, or `run_artifact_root` that does not normalize to the supplied `--run-root`. That is exactly the manifest/path-drift class the harness is meant to catch.

Required plan change:

Add explicit P0/P1 checks for:

- per-token/per-scope manifest entry schemas;
- `artifact_dir` resolution under the run root;
- `run_artifact_root` normalization against `--run-root`;
- manifest entry identity reconciliation against `scope.json` and folder slug;
- no absolute, parent-escaping, or sibling-run paths unless explicitly allowed by the workflow contract.

### P1-2 — Parent-agent return contract and root status reconciliation are not covered

Evidence:

- Both workflow contracts define a parent-agent return contract with `status`, `run_artifact_root`, manifest/index/scope paths, final verification path, and summary counts such as `blocked_scopes`, `review_required_scopes`, and `dominant_blockers` (`asset-investment-diligence/output-structure.md:151-171`; `oracle-analysis/output-structure.md:159-177`).
- The plan checks per-scope status value names only as P2 (`plan.md:248-250`, `plan.md:288-289`).
- The combined flow checks the parent root, child roots, and handoff existence (`plan.md:297-321`), but it does not define a local artifact or declared limitation for checking the parent-agent return contract.

Risk:

The harness can pass a run whose artifacts exist but whose final user-facing handoff returns loose report paths, omits blockers, or reports `pass` while a token/scope remains `review_required` or `blocked`. This is a formal workflow-compliance miss, not a reasoning-quality issue.

Required plan change:

Either add a machine-checkable parent-return artifact for harnessed runs, or state that parent-response validation is `needs parent verification` and cannot be claimed by the local harness. In either case, add status reconciliation checks so root index, final verification, manifest entries, and parent-return status cannot disagree silently.

### P1-3 — Negative fixtures and acceptance commands do not prove the important gates

Evidence:

- The only required negative fixture is `bad/missing-final-oracle-verification/` (`plan.md:341-347`).
- The highest-risk negatives are only recommended: asset heading overclaim, broken relative link, oracle side-specific omission, missing Propose handoff, and incorrectly ready-for-preview (`plan.md:355-358`).
- The acceptance commands exercise the good asset, good oracle, good combined, and missing-final-oracle fixtures only (`plan.md:396-416`).
- The negative fixture command is listed in a block that the implementation task should pass (`plan.md:393-416`), while the plan also says that command should exit `2` (`plan.md:434`).

Risk:

The implementation can satisfy acceptance with only the easiest P0 missing-file failure tested. It would not prove final-verification credibility checks, path/link checks, side-specific oracle conclusion checks, or combined-stage gate checks. The raw negative command also makes the acceptance block non-runnable as a normal shell block unless the expected nonzero exit is wrapped and asserted.

Required plan change:

Promote at least one negative fixture per failure class into required acceptance:

- missing canonical final verification;
- heading-only final verification that omits required fields;
- broken run-local relative path or escaped sibling-run path;
- oracle verdict missing position side / token role / stress direction / loss bearer;
- combined run that marks Preview or Execute ready despite unresolved support, eligibility, feed, route, or user-policy gates;
- missing `agentic-flow/analyze-and-propose.md` or missing Propose `request_more_inputs` state.

Acceptance should assert expected nonzero exits explicitly, for example through pytest parametrization or a short subprocess wrapper that checks exit code, severity, and expected check IDs.

## P2 findings

### P2-1 — Link validation should include Obsidian wikilinks or declare them out of scope

Evidence:

- The project contract says body docs use Obsidian wikilinks and README files use standard Markdown links (`CLAUDE.md:299-303`).
- The plan describes link validation as local Markdown links and code-spanned run-local artifact paths (`plan.md:232`, `plan.md:266`).

Risk:

A workflow-doc update or final artifact can contain broken `[[Note#Anchor|label]]` references while the harness reports link validation as passed.

Recommended plan change:

Add an explicit parser for run-local and workflow-doc wikilinks, including anchor checks where practical. If repo-wide Obsidian link validation is too broad for this harness, state the boundary and keep a separate acceptance command for repository link policy.

### P2-2 — Workflow docs and prompt updates need a narrower implementation slice

Evidence:

- The plan includes workflow docs and prompt updates after the validator exists, with a guard not to change workflow meaning (`plan.md:363-389`).
- The acceptance diff scope includes both tool files and workflow docs (`plan.md:418-423`).

Risk:

A single implementation task can drift from building a formal validator into broad workflow rewriting. The repo constraint is to preserve existing workflow meaning and make surgical changes.

Recommended plan change:

Split the implementation into two explicit slices:

1. Validator, fixtures, and tests only.
2. Minimal documentation/prompt updates that merely require running the validator and pasting/linking the report summary.

The second slice should have its own diff check and should not modify workflow semantics, output folders, or stage meanings.

## Fixture adequacy checklist

Current plan coverage:

- Positive combined fixture: adequate as the first smoke fixture.
- Missing final oracle verification: adequate as the first P0 negative fixture.
- Field-level false-pass fixture: not required yet.
- Broken path/link fixture: not required yet.
- Oracle conclusion completeness fixture: not required yet.
- Combined flow gate fixture: not required yet.
- Parent-return/status reconciliation fixture: missing.

Minimum fixture matrix before implementation approval:

| Fixture | Expected result | Why required |
|---|---:|---|
| `good/good-agentic-sample-assets` | exit `0` | proves happy-path parsing and report shape |
| `bad/missing-final-oracle-verification` | exit `2`, P0 | protects canonical final-verification existence |
| `bad/asset-heading-overclaim` | exit `1` or `2` by severity policy | protects final-verification credibility |
| `bad/broken-relative-link` | exit `2` for missing declared path | protects path/link validation |
| `bad/oracle-side-specific-omission` | exit `1` or `2` by severity policy | protects side-specific oracle verdict contract |
| `bad/ready-for-preview-incorrectly` | exit `1` or `2` by severity policy | protects Analyze -> Propose gate integrity |
| `bad/missing-parent-return-status` | exit `1` or `2` by severity policy | protects parent-return/root-status reconciliation |

## Missing acceptance commands

Add runnable commands or pytest cases that prove expected failures. The current raw negative fixture command should be replaced with an asserted command such as:

```bash
python3 - <<'PY'
import json
import subprocess

cmd = [
    "python3",
    "dev/tools/validate_workflow_run.py",
    "--workflow",
    "oracle-analysis",
    "--run-root",
    "dev/tools/workflow_harness/fixtures/bad/missing-final-oracle-verification",
    "--format",
    "json",
]
proc = subprocess.run(cmd, text=True, capture_output=True)
assert proc.returncode == 2, proc.stdout + proc.stderr
report = json.loads(proc.stdout)
check_ids = {finding["check_id"] for finding in report["findings"]}
assert "oracle.final_verification_file_exists" in check_ids
PY
```

Add equivalent asserted commands or pytest fixture cases for the other required negative fixtures above.

## Approval blockers

Implementation should not start until these are resolved in the plan:

1. Manifest entry schema and path reconciliation checks are explicit.
2. Parent-return validation is either implemented as a local artifact check or explicitly marked `needs parent verification`.
3. Root status / blocker reconciliation is defined.
4. Required negative fixtures cover missing-file, field-credibility, path/link, oracle-side verdict, and combined-flow stage-gate failures.
5. Acceptance commands are runnable as written and assert expected nonzero exits.

## Final review decision

approved: false

Reason: the plan is directionally sound but still permits formal false passes in manifest/path drift, parent-return/status reconciliation, and untested P1/P2 gate classes. Fixing the listed P1 blockers should be enough for a revised plan to become implementation-ready.
