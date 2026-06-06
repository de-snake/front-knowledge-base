# M5 fixtures, runbooks, and external-agent handoff plan

Purpose: give the next implementation worker a narrow, executable brief for adding the workflow-harness fixture battery and the minimal workflow documentation updates that force agents to run the harness, fix failures, and carry harness output into final verification.

This slice is formal workflow-compliance only. It must not assess token economic quality, oracle correctness, allocation suitability, or live execution quality.

## Inputs read

- `CLAUDE.md`
- `dev/implementation/workflow-harness/hardened-plan.md`
- `dev/implementation/workflow-harness/internal-audit.md`
- `dev/implementation/workflow-harness/external-harness-research.md`
- `dev/implementation/workflow-harness/plan-review.md`
- `user/references/workflows/asset-investment-diligence/runbook.md`
- `user/references/workflows/asset-investment-diligence/output-structure.md`
- `user/references/workflows/oracle-analysis/runbook.md`
- `user/references/workflows/oracle-analysis/output-structure.md`

## Scope boundary

In scope:

1. Add a compact fixture battery under `dev/implementation/workflow-harness/fixtures/`.
2. Add the minimum runbook instructions that make asset and oracle workflow agents run the harness before final user handoff.
3. Add the minimum output-structure wording needed to preserve harness reports under each run's `verification/` directory.
4. Require external agents to fix P0 failures, either fix or explicitly surface P1 findings, and include harness output in canonical final verification.

Out of scope:

- Validator implementation or refactor.
- New economic, oracle-quality, investment, or allocation judgment checks.
- Rewriting workflow stage order, folder semantics, stage meanings, or parent-agent responsibilities.
- README or `CLAUDE.md` navigation changes unless a later worker proves a discoverability gap. This plan does not require them.

Prerequisite: the validator CLI from the harness implementation slices must exist before this slice is implemented. If `dev/tools/validate_workflow_run.py` or the relevant `dev/tools/workflow_harness/tests/` files are absent, block the implementation task instead of writing runbook claims around a non-existent harness.

## Exact files to edit or create in the implementation slice

Create fixture docs/data:

- `dev/implementation/workflow-harness/fixtures/README.md`
- `dev/implementation/workflow-harness/fixtures/fixture-matrix.json`
- `dev/implementation/workflow-harness/fixtures/good/good-agentic-sample-assets/README.md`
- `dev/implementation/workflow-harness/fixtures/bad/missing-final-oracle-verification/README.md`
- `dev/implementation/workflow-harness/fixtures/bad/asset-heading-overclaim/README.md`
- `dev/implementation/workflow-harness/fixtures/bad/broken-relative-link/README.md`
- `dev/implementation/workflow-harness/fixtures/bad/oracle-side-specific-omission/README.md`
- `dev/implementation/workflow-harness/fixtures/bad/ready-for-preview-incorrectly/README.md`
- `dev/implementation/workflow-harness/fixtures/bad/missing-propose-handoff/README.md`
- `dev/implementation/workflow-harness/fixtures/bad/missing-parent-return-status/README.md`

Edit workflow runbooks:

- `user/references/workflows/asset-investment-diligence/runbook.md`
- `user/references/workflows/oracle-analysis/runbook.md`

Edit output contracts:

- `user/references/workflows/asset-investment-diligence/output-structure.md`
- `user/references/workflows/oracle-analysis/output-structure.md`

Do not edit in this slice:

- `README.md`
- `CLAUDE.md`
- `user/references/workflows/*/workflow.json`
- `user/references/workflows/*/stage-contracts.md`
- `user/references/workflows/*/subagent-prompts.md`
- validator code under `dev/tools/`

If the implementation worker discovers a real need to edit one of the excluded files, it should stop and create a follow-up plan or block with the exact reason.

## Fixture battery contract

`dev/implementation/workflow-harness/fixtures/README.md` should explain that these fixtures are the canonical docs/data battery for external-agent workflow compliance. It should point to `fixture-matrix.json` as the machine-readable source and state that fixture content is intentionally small, deterministic, and local-only.

`fixture-matrix.json` should contain one object per fixture with these fields:

```json
{
  "id": "bad/missing-final-oracle-verification",
  "workflow": "oracle-analysis",
  "run_root": "dev/implementation/workflow-harness/fixtures/bad/missing-final-oracle-verification",
  "parent_return": null,
  "expected_exit_code": 2,
  "expected_status": "fail",
  "expected_findings": ["paths.final_verification_exists"],
  "protects": "canonical final-verification existence",
  "source_basis": "internal-audit.md missing final oracle verification class"
}
```

Required fixture rows:

| Fixture id | Workflow | Expected result | Required finding ids | Protects |
|---|---|---:|---|---|
| `good/good-agentic-sample-assets` | `combined-analyze-propose` | exit `0`, status `pass` | none | happy-path parsing, child run imports, parent handoff, final verification references |
| `bad/missing-final-oracle-verification` | `oracle-analysis` | exit `2`, status `fail` | `paths.final_verification_exists` | missing canonical run-level final verification |
| `bad/asset-heading-overclaim` | `asset-investment-diligence` | exit `1`, status `review_required` | `asset.s6_quantitative_fields`, `asset.verification_credibility` | heading-only final verification and missing exact quantitative fields |
| `bad/broken-relative-link` | `asset-investment-diligence` | exit `2`, status `fail` | `links.local_paths_resolve` or `paths.no_absolute_parent_escape` | broken nested local path or sibling-run path drift |
| `bad/oracle-side-specific-omission` | `oracle-analysis` | exit `1`, status `review_required` | `oracle.conclusion_quad_present` | oracle verdict missing position side, token role, stress direction, or loss bearer |
| `bad/ready-for-preview-incorrectly` | `combined-analyze-propose` | exit `1`, status `review_required` | `flow.unresolved_gates_request_more_inputs`, `flow.preview_execute_blocked_when_unresolved` | Analyze -> Propose gate integrity when support, eligibility, feed, route, or user-policy gates remain unresolved |
| `bad/missing-propose-handoff` | `combined-analyze-propose` | exit `2`, status `fail` | `flow.propose_handoff_exists` | combined run cannot skip `agentic-flow/analyze-and-propose.md` |
| `bad/missing-parent-return-status` | `combined-analyze-propose` | exit `1`, status `review_required` | `parent_return.contract_fields_present`, `parent_return.status_reconciles_children` | parent-agent return contract and root status reconciliation |

Fixture README files should include only:

- what failure or success the fixture represents;
- the workflow mode to run;
- the expected exit code and status;
- expected finding ids;
- source basis from `internal-audit.md`, `plan-review.md`, or `hardened-plan.md`;
- a note that the fixture is not an economic or oracle-quality benchmark.

Do not copy raw research dumps into fixture README files. If a fixture needs sample run content, keep it minimal and local to that fixture directory.

## Asset runbook update

In `user/references/workflows/asset-investment-diligence/runbook.md`, add a short harness gate after the existing final verification step and before completion standard language.

Required content:

- Run from vault root.
- Command shape:

```bash
python3 dev/tools/validate_workflow_run.py \
  --workflow asset-investment-diligence \
  --run-root <run_artifact_root> \
  --format json,markdown \
  --write-verification
```

- If the command exits `2`, the run is structurally failed. Fix the artifacts and rerun before final handoff.
- If the command exits `1`, the run is `review_required`. Fix findings where possible; if findings remain because inputs are missing, keep the final status as `review_required` and list the finding ids and blockers in final verification.
- The final user summary must include `run_artifact_root`, final index path, final verification path, harness report path or embedded harness section, exit code, and unresolved P1/P2 finding ids.
- The agent must not claim `pass` if the harness report status is `fail` or `review_required`.

## Oracle runbook update

In `user/references/workflows/oracle-analysis/runbook.md`, add the same harness gate after the verification stage and before final answer shape.

Required command shape:

```bash
python3 dev/tools/validate_workflow_run.py \
  --workflow oracle-analysis \
  --run-root <run_artifact_root> \
  --format json,markdown \
  --write-verification
```

Required wording mirrors the asset runbook, with oracle-specific examples of non-negotiable findings:

- missing `verification/final-oracle-analysis-verification.md` is structural failure;
- missing side-specific conclusion fields is at least `review_required`;
- conclusions must not stop at top-level feed type;
- unresolved live inputs must be reflected as blockers, not hidden behind a `pass` status.

## Output-structure updates

In both output-structure files, extend the existing `verification/` folder description with the harness report files:

```text
verification/
  final-...-verification.md
  workflow-harness-report.json
  workflow-harness-report.md
```

Add one paragraph near the parent-agent return contract:

- `workflow-harness-report.json` is the machine-readable validator result.
- `workflow-harness-report.md` is the human-readable report summary.
- The canonical final verification file must either embed the harness summary or link to both report files.
- Parent-agent return `status` must reconcile with harness status: `fail` cannot be returned as `pass`; `review_required` cannot be returned as `pass` unless a human explicitly overrides outside the workflow artifact.

Do not change token, PT, scope, or stage folder meanings.

## External-agent handoff instruction

Add this rule to both runbooks in concise form:

```text
External-agent completion rule: before returning to the parent agent or user, run the workflow harness, fix all P0 findings, rerun it, and include the final harness command, cwd, exit code, status, report path, and unresolved finding ids in the final verification file. If P1 findings remain, return `review_required` with blockers; do not call the run `pass`.
```

This is the core behavior change of the slice. Keep it near final verification so it is hard to miss during execution.

## Acceptance commands for the implementation slice

Run from `/Users/ilya/Documents/Codex/front-knowledge-base` unless a command states otherwise.

1. Fixture battery regression:

```bash
python3 -m pytest dev/tools/workflow_harness/tests/test_fixtures.py -q
```

2. Matrix command wrapper against all required fixture rows:

```bash
python3 - <<'PY'
import json
import subprocess
from pathlib import Path

matrix_path = Path('dev/implementation/workflow-harness/fixtures/fixture-matrix.json')
rows = json.loads(matrix_path.read_text())
required_ids = {
    'good/good-agentic-sample-assets',
    'bad/missing-final-oracle-verification',
    'bad/asset-heading-overclaim',
    'bad/broken-relative-link',
    'bad/oracle-side-specific-omission',
    'bad/ready-for-preview-incorrectly',
    'bad/missing-propose-handoff',
    'bad/missing-parent-return-status',
}
seen = {row['id'] for row in rows}
missing = required_ids - seen
assert not missing, missing

for row in rows:
    cmd = [
        'python3', 'dev/tools/validate_workflow_run.py',
        '--workflow', row['workflow'],
        '--run-root', row['run_root'],
        '--format', 'json',
    ]
    if row.get('parent_return'):
        cmd.extend(['--parent-return', row['parent_return']])
    proc = subprocess.run(cmd, text=True, capture_output=True)
    assert proc.returncode == row['expected_exit_code'], (row['id'], proc.returncode, proc.stdout, proc.stderr)
    report = json.loads(proc.stdout)
    assert report['status'] == row['expected_status'], (row['id'], report.get('status'))
    found = {finding.get('id') or finding.get('check_id') for finding in report.get('findings', [])}
    expected = set(row.get('expected_findings', []))
    assert expected <= found, (row['id'], expected, found)
print('M5_FIXTURE_MATRIX_PASS')
PY
```

3. Documentation contract check:

```bash
python3 - <<'PY'
from pathlib import Path

checks = {
    'user/references/workflows/asset-investment-diligence/runbook.md': [
        'dev/tools/validate_workflow_run.py',
        '--workflow asset-investment-diligence',
        '--write-verification',
        'fix all P0 findings',
        'review_required',
        'harness command',
        'unresolved finding ids',
    ],
    'user/references/workflows/oracle-analysis/runbook.md': [
        'dev/tools/validate_workflow_run.py',
        '--workflow oracle-analysis',
        '--write-verification',
        'fix all P0 findings',
        'review_required',
        'harness command',
        'unresolved finding ids',
    ],
    'user/references/workflows/asset-investment-diligence/output-structure.md': [
        'workflow-harness-report.json',
        'workflow-harness-report.md',
        'Parent-agent return',
    ],
    'user/references/workflows/oracle-analysis/output-structure.md': [
        'workflow-harness-report.json',
        'workflow-harness-report.md',
        'Parent-agent return',
    ],
}
for path, terms in checks.items():
    text = Path(path).read_text()
    missing = [term for term in terms if term not in text]
    assert not missing, (path, missing)
print('M5_RUNBOOK_OUTPUT_STRUCTURE_CHECK_PASS')
PY
```

4. Full harness tests:

```bash
python3 -m pytest dev/tools/workflow_harness/tests -q
```

5. Diff hygiene for the allowed files only:

```bash
git diff --check -- \
  dev/implementation/workflow-harness/fixtures \
  user/references/workflows/asset-investment-diligence/runbook.md \
  user/references/workflows/asset-investment-diligence/output-structure.md \
  user/references/workflows/oracle-analysis/runbook.md \
  user/references/workflows/oracle-analysis/output-structure.md

git status --short -- \
  dev/implementation/workflow-harness/fixtures \
  user/references/workflows/asset-investment-diligence/runbook.md \
  user/references/workflows/asset-investment-diligence/output-structure.md \
  user/references/workflows/oracle-analysis/runbook.md \
  user/references/workflows/oracle-analysis/output-structure.md
```

Do not run monorepo workspace sync for this slice unless the implementation worker edits navigation or workspace metadata, which this plan forbids by default.

## Definition of done for the implementation slice

- All exact files listed above are either created or edited, and no excluded files are touched.
- `fixture-matrix.json` includes all required good and bad fixture rows.
- Each bad fixture proves a distinct formal failure class with expected exit code, status, and finding ids.
- Asset and oracle runbooks require the harness before final handoff.
- Asset and oracle output structures preserve the harness report under `verification/` and require final verification to embed or link the result.
- Acceptance commands above pass, with command output recorded in the implementation handoff.
- Any remaining P1 findings are explicitly returned as `review_required`; no agent may convert them into `pass` without a human override outside the workflow artifact.
