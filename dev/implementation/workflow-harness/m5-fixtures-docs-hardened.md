# M5 hardened execution brief — fixtures, runbooks, and external-agent handoff instructions

Purpose: revise `m5-fixtures-docs-plan.md` into an implementation-ready brief that resolves the M5 review blockers. This brief is for a future implementation worker; it does not implement fixtures, validator code, tests, or workflow prose changes.

This slice is formal workflow-compliance only. It must not assess token economic quality, oracle correctness, allocation suitability, or live execution quality.

## Inputs to treat as source

- `CLAUDE.md`.
- `dev/implementation/workflow-harness/m5-fixtures-docs-plan.md`.
- `dev/implementation/workflow-harness/m5-fixtures-docs-review.md`.
- `dev/implementation/workflow-harness/m1-validator-core-plan.md`.
- `dev/implementation/workflow-harness/m2-asset-checks-plan.md`.
- `dev/implementation/workflow-harness/m3-oracle-checks-plan.md`.
- `dev/implementation/workflow-harness/m4-agentic-flow-plan.md`.
- `dev/implementation/workflow-harness/hardened-plan.md`.
- `user/references/workflows/asset-investment-diligence/runbook.md`.
- `user/references/workflows/asset-investment-diligence/output-structure.md`.
- `user/references/workflows/oracle-analysis/runbook.md`.
- `user/references/workflows/oracle-analysis/output-structure.md`.

## Review blockers incorporated

| Review finding | Hardened decision |
| --- | --- |
| P1-1 fixture matrix was not runnable from README-only fixtures | Every fixture below has an explicit minimal physical artifact tree. README files are documentation only; they are not the runnable fixture content. |
| P1-2 report filenames conflicted with the M1 validator contract | Runtime docs must use `--report-dir <run_artifact_root>/verification` and the M1 deterministic names: `workflow-harness-report.json` and `workflow-harness-verification.md`. Do not introduce `workflow-harness-report.md`. |
| P1-3 parent-return artifacts were under-specified | The good combined fixture must pass an explicit valid `agentic-flow/parent-return.json`. The malformed parent-return fixture must pass an explicit invalid parent-return artifact. A separate absence fixture covers `parent_return.needs_parent_verification`. |
| P2-1 prerequisite gate was implicit | The implementation slice starts with the exact preflight command below and blocks before editing if it fails. |
| P2-2 fixture location conflicted with earlier tool fixtures | `dev/implementation/workflow-harness/fixtures/fixture-matrix.json` is the canonical external-agent docs/data fixture matrix for this slice. The existing `dev/tools/workflow_harness/tests/test_fixtures.py` must consume this matrix; if it does not, block or split a test-wiring slice instead of creating a second fixture source of truth. |

## Preflight gate before any implementation edits

Run from `/Users/ilya/Documents/Codex/front-knowledge-base`:

```bash
test -f dev/tools/validate_workflow_run.py
test -f dev/tools/workflow_harness/tests/test_fixtures.py
python3 dev/tools/validate_workflow_run.py --help >/dev/null
python3 - <<'PY'
from pathlib import Path
test_file = Path('dev/tools/workflow_harness/tests/test_fixtures.py')
text = test_file.read_text()
required = 'dev/implementation/workflow-harness/fixtures/fixture-matrix.json'
assert required in text, f'{test_file} must consume {required}; split or block before M5 docs/fixtures implementation'
print('M5_PREFLIGHT_PASS')
PY
```

If any command fails, block the implementation task with the missing prerequisite. Do not edit runbooks, output structures, or fixture docs around a validator that cannot execute this slice.

## Scope and edit boundary

In scope:

1. Create a compact runnable fixture battery under `dev/implementation/workflow-harness/fixtures/`.
2. Update the asset and oracle runbooks so external agents run the harness before final handoff.
3. Update the asset and oracle output structures so harness outputs are preserved under each run's `verification/` directory.
4. Require external agents to fix P0 findings, either fix or surface P1 findings, and include harness command evidence in final verification.

Allowed paths:

- `dev/implementation/workflow-harness/fixtures/**`.
- `user/references/workflows/asset-investment-diligence/runbook.md`.
- `user/references/workflows/asset-investment-diligence/output-structure.md`.
- `user/references/workflows/oracle-analysis/runbook.md`.
- `user/references/workflows/oracle-analysis/output-structure.md`.

Do not edit in this slice:

- `dev/tools/validate_workflow_run.py`.
- `dev/tools/workflow_harness/tests/**`.
- any other file under `dev/tools/**`.
- `README.md`.
- `CLAUDE.md`.
- `user/references/workflows/*/workflow.json`.
- `user/references/workflows/*/stage-contracts.md`.
- `user/references/workflows/*/subagent-prompts.md`.

If the implementation worker discovers that a forbidden path must change for acceptance, stop and block with the exact missing prerequisite or create a follow-up implementation-plan card. Do not widen this slice silently.

## Fixture source of truth

`dev/implementation/workflow-harness/fixtures/fixture-matrix.json` is the machine-readable source for the fixture battery. The pytest regression must read this matrix; the fixture directories under `dev/implementation/` are not copies of `dev/tools/workflow_harness/fixtures/**`.

The root `fixtures/README.md` should state:

- these fixtures are the canonical docs/data battery for external-agent workflow compliance;
- fixture content is intentionally tiny, deterministic, and local-only;
- each row is runnable by `dev/tools/validate_workflow_run.py` from the vault root;
- the fixtures are not economic, oracle-quality, allocation, or live-execution benchmarks.

## Required fixture matrix rows

Each row in `fixture-matrix.json` must include:

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
  "source_basis": "m5-fixtures-docs-review.md P1-1 / internal audit missing final oracle verification class"
}
```

Required rows:

| Fixture id | Workflow | Parent return | Expected result | Required finding ids | Protects |
| --- | --- | --- | ---: | --- | --- |
| `good/good-agentic-sample-assets` | `combined-analyze-propose` | `dev/implementation/workflow-harness/fixtures/good/good-agentic-sample-assets/agentic-flow/parent-return.json` | exit `0`, status `pass` | none | happy-path parsing, child imports, parent handoff, parent return, final verification references |
| `bad/missing-final-oracle-verification` | `oracle-analysis` | null | exit `2`, status `fail` | `paths.final_verification_exists` | missing canonical run-level final verification |
| `bad/asset-heading-overclaim` | `asset-investment-diligence` | null | exit `1`, status `review_required` | `asset.s6_quantitative_fields`, `asset.verification_credibility` | heading-only final verification and missing exact quantitative fields |
| `bad/broken-relative-link` | `asset-investment-diligence` | null | exit `2`, status `fail` | `links.local_paths_resolve` or `paths.no_absolute_parent_escape` | broken nested local path or sibling-run path drift |
| `bad/oracle-side-specific-omission` | `oracle-analysis` | null | exit `1`, status `review_required` | `oracle.conclusion_quad_present` | oracle verdict missing position side, token role, stress direction, or loss bearer |
| `bad/ready-for-preview-incorrectly` | `combined-analyze-propose` | `dev/implementation/workflow-harness/fixtures/bad/ready-for-preview-incorrectly/agentic-flow/parent-return.json` | exit `1`, status `review_required` | `flow.unresolved_gates_request_more_inputs`, `flow.preview_execute_blocked_when_unresolved` | Analyze → Propose gate integrity while support, eligibility, feed, route, wallet, or user-policy gates remain unresolved |
| `bad/missing-propose-handoff` | `combined-analyze-propose` | null | exit `2`, status `fail` | `flow.propose_handoff_exists` | combined run cannot skip `agentic-flow/analyze-and-propose.md` |
| `bad/missing-parent-return-status` | `combined-analyze-propose` | `dev/implementation/workflow-harness/fixtures/bad/missing-parent-return-status/agentic-flow/parent-return.json` | exit `1`, status `review_required` | `parent_return.contract_fields_present`, `parent_return.status_reconciles_children` | malformed or inconsistent parent-agent return contract |
| `bad/no-parent-return-artifact` | `combined-analyze-propose` | null | exit `1`, status `review_required` | `parent_return.needs_parent_verification` | explicit absence path: parent response was not validated and cannot be reported as pass |

## Minimal runnable fixture trees

Keep fixture content short. Use obvious synthetic symbols such as SAMPLE_BASE_TOKEN and SampleVaultToken, but do not claim live market correctness. Every fixture README should document expected exit code, expected status, expected finding ids, source basis, and the non-benchmark note.

### Shared minimal asset run tree

Use this as the base for asset fixtures and for the asset child inside combined fixtures:

```text
<asset-run-root>/
  README.md
  run-manifest.json
  index.md
  tokens/
    ethereum-sample-base-token-00000000/
      scope.json
      research/
        onchain-admin.md
        issuer-backing-security.md
        transfer-liquidity-oracle-governance.md
      technical-report.md
      analyst-report.md
      verification.md
  pt-markets/
    index.md
  x-research/
    index.md
  investment-analysis/
    quantitative-underwriting-methodology.md
    investment-analyst-report-points-pt-risk-return.md
    index.md
  verification/
    final-investment-analysis-verification.md
```

Required content markers:

- `run-manifest.json` uses `workflow_id: asset-investment-diligence-v1`, a `run_artifact_root` that normalizes to the fixture root, one token entry whose `artifact_dir` is `tokens/ethereum-sample-base-token-00000000`, empty `pt_markets`, empty `x_research_scopes`, `final_index: index.md`, and `final_verification: verification/final-investment-analysis-verification.md`.
- `scope.json` reconciles with the manifest token symbol, address, chain, slug, and status.
- `pt-markets/index.md` includes an explicit skipped marker and reason for `S3_pt_market_economics`.
- `x-research/index.md` includes explicit skipped markers and reasons for `S4_x_social_mining` and `S5_x_social_synthesis`.
- The good/base final verification names concrete files checked, manifest/path reconciliation, local-link checks, terminology/diff evidence, and the final harness command once generated.
- The good/base S6 files include the exact quantitative field labels required by the asset harness: gross ROI, simple annualized return, points EV, points ROI, expected loss, exit cost, risk-adjusted ROI, break-even points requirement, and decision status. Tiny placeholder values are acceptable when clearly marked as fixture-only values.

### Shared minimal oracle run tree

Use this as the base for oracle fixtures and for the oracle child inside combined fixtures:

```text
<oracle-run-root>/
  README.md
  run-manifest.json
  index.md
  tokens/
    ethereum-sample-base-token-00000000/
      scope.json
      oracle/
        scope.md
        feed-graph.md
        node-classification.md
        source-primitive-audit.md
        stress-tradeoff-analysis.md
        protocol-fit-memo.md
      raw/
        feed-probes.json
        source-evidence/
          README.md
      verification/
        oracle-analysis-verification.md
  verification/
    final-oracle-analysis-verification.md
```

Required content markers:

- `run-manifest.json` uses `workflow_id: oracle-analysis-v1`, a `run_artifact_root` that normalizes to the fixture root, one token scope whose `artifact_dir` is `tokens/ethereum-sample-base-token-00000000`, and `final_verification: verification/final-oracle-analysis-verification.md`.
- `scope.json` reconciles with the manifest scope id, slug, chain, protocol, asset symbol, asset address, position sides, token roles, and status.
- `oracle/feed-graph.md` names a top-level feed, a formula, and leaf sources.
- `oracle/node-classification.md` classifies each node as market, fundamental, NAV, hardcoded, or hybrid.
- `oracle/source-primitive-audit.md` covers every leaf source and points to `raw/source-evidence/README.md`.
- `oracle/stress-tradeoff-analysis.md` explicitly includes liquidity-cascade and liquidity-trap framing.
- `oracle/protocol-fit-memo.md` includes verdict rows with position side, token role, stress direction, and loss bearer.
- `verification/final-oracle-analysis-verification.md` names concrete files checked, recursive graph coverage, source primitive audit coverage, side-specific conclusion fields, and the final harness command once generated.

### Good combined fixture tree

`good/good-agentic-sample-assets` must be runnable as a parent combined run:

```text
good/good-agentic-sample-assets/
  README.md
  index.md
  asset-investment-diligence/
    <shared minimal asset run tree>
  oracle-analysis/
    <shared minimal oracle run tree>
  agentic-flow/
    analyze-and-propose.md
    parent-return.json
```

`agentic-flow/analyze-and-propose.md` must include:

- all six canonical stages: Discover, Analyze, Propose, Preview, Execute, Monitor;
- Discover marked complete by user premise or complete by agent;
- Analyze complete;
- Propose marked `request_more_inputs` or `blocked` if any child blockers remain, otherwise a pass-compatible state accepted by the current validator;
- Preview and Execute blocked unless an explicit local human override artifact exists;
- links to both child final verification files;
- concrete next checks when Propose requests more inputs;
- no recommendation to open a Credit Account, allocate funds, sign transactions, or move to Execute from Analyze-only evidence.

`agentic-flow/parent-return.json` must include at least:

```json
{
  "status": "pass",
  "run_artifact_root": "dev/implementation/workflow-harness/fixtures/good/good-agentic-sample-assets",
  "index": "dev/implementation/workflow-harness/fixtures/good/good-agentic-sample-assets/index.md",
  "final_verification": "dev/implementation/workflow-harness/fixtures/good/good-agentic-sample-assets/agentic-flow/analyze-and-propose.md",
  "child_runs": {
    "asset-investment-diligence": {
      "status": "pass",
      "run_artifact_root": "dev/implementation/workflow-harness/fixtures/good/good-agentic-sample-assets/asset-investment-diligence",
      "final_verification": "dev/implementation/workflow-harness/fixtures/good/good-agentic-sample-assets/asset-investment-diligence/verification/final-investment-analysis-verification.md"
    },
    "oracle-analysis": {
      "status": "pass",
      "run_artifact_root": "dev/implementation/workflow-harness/fixtures/good/good-agentic-sample-assets/oracle-analysis",
      "final_verification": "dev/implementation/workflow-harness/fixtures/good/good-agentic-sample-assets/oracle-analysis/verification/final-oracle-analysis-verification.md"
    }
  },
  "blocked_scopes": [],
  "review_required_scopes": [],
  "dominant_blockers": [],
  "live_input_blockers": [],
  "unresolved_finding_ids": []
}
```

If the implemented validator uses a stricter parent-return schema, update this fixture within the same paths while preserving the required meaning: the parent status reconciles with children and all referenced final verification paths exist.

### Bad fixture mutations

Build each bad fixture by copying only the minimal base needed to reach the intended finding, then make the single mutation below. Avoid multiple accidental failures.

- `bad/missing-final-oracle-verification`: use the shared oracle tree, but omit `verification/final-oracle-analysis-verification.md` while leaving the manifest `final_verification` pointing to it.
- `bad/asset-heading-overclaim`: use the shared asset tree, but make S6 and final verification heading-only. Keep root files present, but omit the exact quantitative field labels and concrete verification evidence so the expected P1 ids are the first meaningful findings.
- `bad/broken-relative-link`: use the shared asset tree, but include one broken local Markdown link, code-spanned local path, or manifest-declared path that resolves outside the run root. Keep all required files present.
- `bad/oracle-side-specific-omission`: use the shared oracle tree, but make `oracle/protocol-fit-memo.md` omit at least one of: position side, token role, stress direction, loss bearer.
- `bad/ready-for-preview-incorrectly`: use a combined parent tree with child artifacts that name unresolved support, eligibility, feed, route, wallet, or user-policy gates. Set Propose to `ready_for_preview` and Preview/Execute to ready. Include a parent-return artifact whose status is not structurally malformed so this fixture targets the flow gate ids.
- `bad/missing-propose-handoff`: use a combined parent tree with child asset/oracle runs, but omit `agentic-flow/analyze-and-propose.md`. Do not pass `parent_return` in the matrix row.
- `bad/missing-parent-return-status`: use a combined parent tree with `agentic-flow/analyze-and-propose.md`, and pass `agentic-flow/parent-return.json` in the matrix. The JSON must be concrete but invalid: omit required contract fields such as `status`, and also include at least one inconsistency such as child status `review_required` while the parent status is `pass` if `status` is present. The fixture must exercise `parent_return.contract_fields_present` and `parent_return.status_reconciles_children`, not the absence path.
- `bad/no-parent-return-artifact`: use a combined parent tree with `agentic-flow/analyze-and-propose.md`, but set `parent_return` to null in the matrix. The expected finding is `parent_return.needs_parent_verification`, and the run must be `review_required`, not `pass`.

## Runbook updates

Add a short harness gate after each workflow's final verification step and before completion / final answer language.

### Asset command

```bash
python3 dev/tools/validate_workflow_run.py \
  --workflow asset-investment-diligence \
  --run-root <run_artifact_root> \
  --format json,markdown \
  --report-dir <run_artifact_root>/verification \
  --write-verification
```

### Oracle command

```bash
python3 dev/tools/validate_workflow_run.py \
  --workflow oracle-analysis \
  --run-root <run_artifact_root> \
  --format json,markdown \
  --report-dir <run_artifact_root>/verification \
  --write-verification
```

Required wording for both runbooks:

- Run from vault root.
- If the command exits `2`, the run is structurally failed. Fix artifacts and rerun before final handoff.
- If the command exits `1`, the run is `review_required`. Fix findings where possible; if findings remain because inputs are missing, keep final status as `review_required` and list finding ids and blockers in final verification.
- The final user summary must include `run_artifact_root`, final index path, final verification path, harness JSON report path, harness Markdown verification path, command, cwd, exit code, status, and unresolved P1/P2 finding ids.
- The agent must not claim `pass` if the harness report status is `fail` or `review_required`.
- For oracle runs, missing `verification/final-oracle-analysis-verification.md` is structural failure; missing side-specific conclusion fields is at least `review_required`; conclusions must not stop at top-level feed type; unresolved live inputs must remain visible as blockers.

External-agent completion rule to add in concise form:

```text
Before returning to the parent agent or user, run the workflow harness, fix all P0 findings, rerun it, and include the final harness command, cwd, exit code, status, JSON report path, Markdown verification path, and unresolved finding ids in the final verification file. If P1 findings remain, return `review_required` with blockers; do not call the run `pass`.
```

## Output-structure updates

In both output-structure files, extend the `verification/` folder shape to use the M1 report contract:

Asset:

```text
verification/
  final-investment-analysis-verification.md
  workflow-harness-report.json
  workflow-harness-verification.md
```

Oracle:

```text
verification/
  final-oracle-analysis-verification.md
  workflow-harness-report.json
  workflow-harness-verification.md
```

Add one concise paragraph near each parent-agent return contract:

- `workflow-harness-report.json` is the machine-readable validator result written by `--report-dir <run_artifact_root>/verification`.
- `workflow-harness-verification.md` is the human-readable harness report written by the same command; `--write-verification` must not overwrite the canonical final verification file.
- The canonical final verification file must embed the harness summary or link to both harness files.
- Parent-agent return `status` must reconcile with harness status: `fail` cannot be returned as `pass`; `review_required` cannot be returned as `pass` unless a human explicitly overrides outside the workflow artifact.

Do not add `workflow-harness-report.md`; that filename is not part of the M1 validator contract.

## Exact acceptance command

Run this whole block from `/Users/ilya/Documents/Codex/front-knowledge-base` after implementing the slice:

```bash
set -euo pipefail

# 0. Preflight: harness and fixture test already exist and consume this slice's matrix.
test -f dev/tools/validate_workflow_run.py
test -f dev/tools/workflow_harness/tests/test_fixtures.py
python3 dev/tools/validate_workflow_run.py --help >/dev/null
python3 - <<'PY'
from pathlib import Path
test_file = Path('dev/tools/workflow_harness/tests/test_fixtures.py')
text = test_file.read_text()
required = 'dev/implementation/workflow-harness/fixtures/fixture-matrix.json'
assert required in text, f'{test_file} must consume {required}'
print('M5_PREFLIGHT_PASS')
PY

# 1. Fixture battery regression.
python3 -m pytest dev/tools/workflow_harness/tests/test_fixtures.py -q

# 2. Matrix command wrapper against all required fixture rows.
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
    'bad/no-parent-return-artifact',
}
seen = {row['id'] for row in rows}
missing = required_ids - seen
extra = seen - required_ids
assert not missing, missing
assert not extra, extra

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

# 3. Documentation contract check.
python3 - <<'PY'
from pathlib import Path

checks = {
    'user/references/workflows/asset-investment-diligence/runbook.md': [
        'dev/tools/validate_workflow_run.py',
        '--workflow asset-investment-diligence',
        '--report-dir <run_artifact_root>/verification',
        '--write-verification',
        'fix all P0 findings',
        'review_required',
        'harness command',
        'unresolved finding ids',
    ],
    'user/references/workflows/oracle-analysis/runbook.md': [
        'dev/tools/validate_workflow_run.py',
        '--workflow oracle-analysis',
        '--report-dir <run_artifact_root>/verification',
        '--write-verification',
        'fix all P0 findings',
        'review_required',
        'harness command',
        'unresolved finding ids',
    ],
    'user/references/workflows/asset-investment-diligence/output-structure.md': [
        'workflow-harness-report.json',
        'workflow-harness-verification.md',
        'Parent-agent return',
    ],
    'user/references/workflows/oracle-analysis/output-structure.md': [
        'workflow-harness-report.json',
        'workflow-harness-verification.md',
        'Parent-agent return',
    ],
}
for path, terms in checks.items():
    text = Path(path).read_text()
    missing = [term for term in terms if term not in text]
    assert not missing, (path, missing)
    assert 'workflow-harness-report.md' not in text, path
print('M5_RUNBOOK_OUTPUT_STRUCTURE_CHECK_PASS')
PY

# 4. Full harness tests.
python3 -m pytest dev/tools/workflow_harness/tests -q

# 5. Diff hygiene and scoped status for allowed paths, including untracked fixture files.
python3 - <<'PY'
from pathlib import Path
roots = [
    Path('dev/implementation/workflow-harness/fixtures'),
    Path('user/references/workflows/asset-investment-diligence/runbook.md'),
    Path('user/references/workflows/asset-investment-diligence/output-structure.md'),
    Path('user/references/workflows/oracle-analysis/runbook.md'),
    Path('user/references/workflows/oracle-analysis/output-structure.md'),
]
files = []
for root in roots:
    if root.is_file():
        files.append(root)
    elif root.exists():
        files.extend(p for p in root.rglob('*') if p.is_file())
for path in files:
    text = path.read_text()
    for idx, line in enumerate(text.splitlines(), 1):
        assert not line.rstrip() != line, f'trailing whitespace: {path}:{idx}'
    assert text.endswith('\n'), f'missing final newline: {path}'
print('M5_ALLOWED_PATH_TEXT_HYGIENE_PASS')
PY

git status --short -- \
  dev/implementation/workflow-harness/fixtures \
  user/references/workflows/asset-investment-diligence/runbook.md \
  user/references/workflows/asset-investment-diligence/output-structure.md \
  user/references/workflows/oracle-analysis/runbook.md \
  user/references/workflows/oracle-analysis/output-structure.md
```

Do not run monorepo workspace sync for this slice unless the implementation worker edits navigation or workspace metadata, which this brief forbids by default.

## Definition of done for the future implementation slice

- Preflight passes before edits.
- Only allowed paths are changed.
- `fixture-matrix.json` includes exactly the required rows above.
- Every fixture has a runnable physical tree, not only README prose.
- The good combined fixture passes only when an explicit valid parent-return artifact is supplied.
- The malformed parent-return fixture and no-parent-return fixture exercise different findings.
- Runbooks use `--report-dir <run_artifact_root>/verification` and preserve command/cwd/exit-code evidence.
- Output structures name `workflow-harness-report.json` and `workflow-harness-verification.md`, and do not name `workflow-harness-report.md`.
- The exact acceptance command above passes and its output is recorded in the implementation handoff.
