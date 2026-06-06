# M4 hardened implementation brief — combined post-Discover Analyze → Propose harness

Purpose: provide the final execution brief for M4 after formal review of `m4-agentic-flow-plan.md`. This slice implements deterministic workflow-compliance checks for a parent run where Discover has already happened and the parent agent performs Analyze → Propose before any Preview or Execute action.

This brief does not implement the harness. It defines the implementation contract, edit boundary, blocker fixes, acceptance command, and definition of done for the future M4 implementation worker.

## Scope

M4 is formal workflow compliance only.

It must not assess token economic quality, oracle correctness, allocation suitability, investment conclusions, route quality, or whether a candidate asset should be used. It must only detect whether the combined parent run obeys the canonical `Discover → Analyze → Propose → Preview → Execute → Monitor` contract and carries machine-checkable child status/blocker evidence forward.

## Inputs incorporated

- `CLAUDE.md` — canonical loop, `user/` versus `dev/` split, Preview / Execute boundary, validation expectations, and Gearbox terminology.
- `dev/implementation/workflow-harness/m4-agentic-flow-plan.md`.
- `dev/implementation/workflow-harness/m4-agentic-flow-review.md`.
- `dev/implementation/workflow-harness/plan-review.md`.
- `dev/implementation/workflow-harness/hardened-plan.md`.
- `dev/implementation/workflow-harness/m1-validator-core-plan.md`.
- `dev/implementation/workflow-harness/m5-fixtures-docs-plan.md`.
- `user/references/workflows/asset-investment-diligence/output-structure.md`.
- `user/references/workflows/oracle-analysis/output-structure.md`.
- Gearbox `front-knowledge-base` formal workflow critic and runtime workflow placement references.

## Implementation edit boundary

Allowed implementation edits for M4:

1. `dev/tools/validate_workflow_run.py`
2. `user/references/workflows/asset-investment-diligence/subagent-prompts.md`
3. `user/references/workflows/oracle-analysis/subagent-prompts.md`

No persistent fixture files are required in M4. M4 acceptance uses temporary synthetic combined roots created inside subprocess assertions. The persistent fixture battery remains M5 scope.

Do not edit:

- `CLAUDE.md`
- `README.md`
- `user/references/workflows/*/runbook.md`
- `user/references/workflows/*/output-structure.md`
- `user/references/workflows/*/workflow.json`
- `user/references/workflows/*/stage-contracts.md`
- `dev/implementation/asset-diligence-2026-06-05-sample-base-token-sample-vault-token/**`
- `dev/implementation/oracle-analysis-2026-06-05-sample-base-token-sample-vault-token/**`
- persistent fixture directories under `dev/implementation/workflow-harness/fixtures/**` or `dev/tools/workflow_harness/fixtures/**`

If implementation needs any excluded file, stop and block with the exact missing dependency instead of expanding scope silently.

## Required parent run shape

For `--workflow combined-analyze-propose`, `--run-root` points to a parent run root with this minimum shape:

```text
<run-root>/
  README.md or index.md
  asset-investment-diligence/
    verification/
      workflow-harness-report.json
  oracle-analysis/
    verification/
      workflow-harness-report.json
  agentic-flow/
    analyze-and-propose.md
```

The combined validator must treat child validation reports as required input evidence for this slice. It does not need to run child validators recursively in M4. Recursive child validator execution can be added later, but M4 must not pass a combined run unless the child report JSON files exist, parse, match the expected child workflow IDs, and reconcile with the parent handoff.

Expected child report paths:

- Asset child report: `asset-investment-diligence/verification/workflow-harness-report.json`
- Oracle child report: `oracle-analysis/verification/workflow-harness-report.json`

Expected child report contract:

```json
{
  "schema_version": "workflow-harness-report-v1",
  "workflow": "asset-investment-diligence-v1 | oracle-analysis-v1",
  "run_root": "<path matching the child root>",
  "status": "pass | review_required | fail",
  "exit_code": 0,
  "summary": {"P0": 0, "P1": 0, "P2": 0},
  "findings": [],
  "checks": []
}
```

The implementation may accept additional report keys from M1-M3, but these fields are mandatory for combined status reconciliation.

## Parent handoff contract

`agentic-flow/analyze-and-propose.md` must be parsed deterministically. Accept either the existing markdown bullet format or a fenced JSON block. The semantic contract matters more than the serialization format.

Minimum markdown shape:

```markdown
## Stage status

- Discover: complete by user premise | complete by agent | blocked
- Analyze: complete | review_required | blocked
- Propose: `ready_for_preview` | `request_more_inputs` | `blocked`
- Preview: blocked | ready | complete
- Execute: blocked | ready | complete
- Monitor: not started | active | blocked
```

Minimum structured block shape, if present:

```json
{
  "schema_version": "agentic-analyze-propose-v1",
  "stage_status": {
    "Discover": "complete_by_user_premise",
    "Analyze": "complete",
    "Propose": "request_more_inputs",
    "Preview": "blocked",
    "Execute": "blocked",
    "Monitor": "not_started"
  },
  "analyze_artifacts": {
    "asset_child_report": "asset-investment-diligence/verification/workflow-harness-report.json",
    "oracle_child_report": "oracle-analysis/verification/workflow-harness-report.json"
  },
  "unresolved_gates": [
    {"gate": "feed_support", "status": "missing_input", "requested_input": "Identify active Gearbox PFS/feed support for the candidate collateral."}
  ],
  "preview_gate": {"status": "blocked", "reason": "unresolved feed/support and wallet eligibility gates"},
  "execute_gate": {"status": "blocked", "reason": "Preview is blocked and no signed execution package exists"}
}
```

Parser precedence:

1. If a valid fenced JSON block with `schema_version="agentic-analyze-propose-v1"` exists, validate it strictly.
2. If markdown stage bullets also exist, they must not conflict with the JSON statuses. A conflict is P1 `flow.stage_status_conflict`.
3. If no structured JSON block exists, parse normalized markdown bullets.
4. Do not infer missing stages from prose. If any canonical stage is absent, emit P1 `flow.stage_status_table_present`.

## M4 check catalog

### P0 structural checks

| Check ID | Rule |
| --- | --- |
| `flow.parent_root_exists` | Supplied parent root exists and is a directory. |
| `flow.child_asset_root_exists` | `asset-investment-diligence/` exists under the parent root. |
| `flow.child_oracle_root_exists` | `oracle-analysis/` exists under the parent root. |
| `flow.propose_handoff_exists` | `agentic-flow/analyze-and-propose.md` exists. |
| `flow.child_asset_report_json_valid` | Asset child `workflow-harness-report.json` exists and parses as JSON. |
| `flow.child_oracle_report_json_valid` | Oracle child `workflow-harness-report.json` exists and parses as JSON. |
| `links.local_paths_resolve` | Parent run-local links and code-spanned artifact paths resolve from their actual nesting level and stay under the parent run root. |

Missing child report JSON is P0 for JSON validity when the report file is absent or unreadable. This avoids a false pass where the parent run contains child folders but no machine-checkable child validation evidence.

### P1 contract checks

| Check ID | Rule |
| --- | --- |
| `flow.child_asset_validation_runs` | Asset child report workflow is `asset-investment-diligence-v1`, has the required report fields, and its `run_root` matches the asset child root. |
| `flow.child_oracle_validation_runs` | Oracle child report workflow is `oracle-analysis-v1`, has the required report fields, and its `run_root` matches the oracle child root. |
| `flow.child_findings_imported` | Child P0/P1 findings are imported into the combined report with child workflow, child path, original severity, and original finding ID. |
| `flow.status_reconciles_children` | Parent Analyze/Propose/Preview statuses are not more permissive than imported child status and blockers allow. |
| `flow.stage_status_table_present` | The handoff names all six stages: Discover, Analyze, Propose, Preview, Execute, Monitor. |
| `flow.discover_state_declared` | Discover says whether it was supplied by premise, completed by the agent, or blocked. |
| `flow.analyze_artifacts_declared` | The handoff links the asset and oracle child harness reports or final verification artifacts used for Analyze. |
| `flow.propose_status_declared` | Propose is one of `ready_for_preview`, `request_more_inputs`, or `blocked`. |
| `flow.unresolved_gates_request_more_inputs` | If unresolved gates are present, Propose is `request_more_inputs` or `blocked`. |
| `flow.preview_execute_blocked_when_unresolved` | Preview and Execute are blocked while unresolved gates remain. |
| `flow.no_unsupported_execution_recommendation` | The handoff does not recommend opening a Credit Account, allocating funds, signing transactions, or moving to Execute from Analyze-only evidence. |
| `flow.monitor_not_started_before_execute` | Monitor is `not started` or `blocked` unless Execute is complete. |
| `flow.requested_next_checks_named` | When Propose is `request_more_inputs`, the handoff lists concrete next checks. |
| `flow.stage_status_conflict` | JSON and markdown stage statuses do not conflict when both are present. |

Child status reconciliation is P1, not P2. A child `review_required` status, child P1 finding, deferred workflow check, or imported unresolved blocker means the parent cannot be `ready_for_preview`. A child `fail` status or child P0 finding means the combined report status is `fail` with exit code `2`.

Imported child finding IDs should be namespaced without losing the original ID. Example:

```json
{
  "id": "child.asset.validator.workflow_checks_deferred",
  "severity": "P1",
  "workflow": "combined-analyze-propose-v1",
  "path": "asset-investment-diligence/verification/workflow-harness-report.json",
  "field": "findings[validator.workflow_checks_deferred]",
  "message": "Imported asset child P1 finding: workflow-specific checks are deferred.",
  "source": {
    "child_workflow": "asset-investment-diligence-v1",
    "child_finding_id": "validator.workflow_checks_deferred"
  }
}
```

### P2 hardening checks

| Check ID | Rule |
| --- | --- |
| `flow.command_evidence_present` | Combined verification output includes validator command, exit code, and generated report path when `--write-verification` is used. |
| `flow.raw_dump_absent` | Parent index and handoff cite child artifact paths instead of pasting raw evidence dumps. |
| `flow.parent_index_maps_children` | Parent `README.md` or `index.md` links to child report/final verification artifacts and `agentic-flow/analyze-and-propose.md`, not only child directories. |

## Unresolved gate detection

Use deterministic markers and conservative keyword families. A false positive is acceptable because the safe output is `request_more_inputs` or blocked Preview/Execute. A false pass is not acceptable.

Treat these gate families as unresolved when they appear near a blocking marker:

- `support`, `Gearbox support`, `PFS`, `Credit Manager envelope`, `no Credit Manager`, `not enabled`, `unsupported`, `unavailable`
- `eligibility`, `KYC`, `wallet`, `issuer`, `transfer`, `redeem`, `not eligible`, `not verified`
- `feed`, `oracle`, `safe pricing`, `LT`, `LLTV`, `no active market`, `to be confirmed`, `TBD`
- `route`, `route depth`, `liquidity`, `exit`, `quote`, `no route`, `no quote`
- `user policy`, `mandate`, `position size`, `target leverage`, `cannot determine`, `insufficient data`
- `live input`, `current state`, `fresh data`, `not supplied`, `missing`, `unknown`, `unresolved`, `requires`, `must check`, `blocked`, `review_required`

The detector does not need broad natural-language understanding. It must catch common formal blocker wording such as `Gearbox support unsupported`, `wallet eligibility not verified`, `no route`, `no quote`, `TBD`, and `insufficient data`.

## Human override handling

M4 removes the previous human-override bypass.

For this slice, Preview and Execute must stay blocked while unresolved gates remain. A linked human override artifact, an approval note, or a claim of manual sign-off must not make Preview or Execute ready inside the M4 combined-run validator.

Reason: M4 validates post-Discover Analyze → Propose handoff integrity before any Preview or Execute action. Human override schema and signed execution package semantics are outside this slice. If a future task adds override support, it must define the artifact schema, permitted gate scope, approval source, timestamp, reason, and signed execution-package boundary in a separate brief with its own negative and positive acceptance cases.

## Prompt-doc implementation requirements

Update only the parent-handoff/final-verification areas of the two prompt files.

In `user/references/workflows/asset-investment-diligence/subagent-prompts.md`, require the final compressed handoff to return:

```text
- status: pass | review_required | blocked
- run_artifact_root
- final_verification
- workflow_harness_report
- blocked_scopes
- review_required_scopes
- dominant_blockers
- live_input_blockers
- preview_execute_relevance
```

Asset-specific blocker examples must include missing Gearbox support, issuer eligibility, wallet/KYC, route/depth, Credit Manager envelope, user policy, position size, and live-input gates. These blockers must be returned as machine-checkable fields, not buried in prose.

In `user/references/workflows/oracle-analysis/subagent-prompts.md`, add the same fields and oracle-specific blocker examples: missing feed support, recursive feed uncertainty, source-primitive gaps, side-specific loss-bearer omissions, Gearbox protocol-fit gaps, safe-pricing/LT status, and live market/feed state.

Do not change stage order, output folder names, workflow meaning, or run artifact semantics.

## Acceptance command for M4 implementation

Run this exact command from `/Users/ilya/Documents/Codex/front-knowledge-base` after implementing M4. It builds temporary combined roots, imports synthetic child reports, mutates handoffs, checks schema compatibility, verifies prompt fields, and checks diff hygiene for the allowed files.

```bash
python3 - <<'PY'
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

REQUIRED_REPORT_KEYS = {
    'schema_version', 'generated_at', 'workflow', 'run_root', 'status',
    'exit_code', 'summary', 'inputs', 'findings', 'checks', 'generated_files'
}
REQUIRED_PROMPT_FIELDS = {
    'status', 'run_artifact_root', 'final_verification', 'workflow_harness_report',
    'blocked_scopes', 'review_required_scopes', 'dominant_blockers',
    'live_input_blockers', 'preview_execute_relevance'
}


def run_validator(run_root, *extra):
    proc = subprocess.run([
        'python3', 'dev/tools/validate_workflow_run.py',
        '--workflow', 'combined-analyze-propose',
        '--run-root', str(run_root),
        '--format', 'json,markdown',
        *extra,
    ], text=True, capture_output=True)
    try:
        report = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(f'validator did not emit JSON stdout: rc={proc.returncode}\nSTDOUT={proc.stdout}\nSTDERR={proc.stderr}') from exc
    return proc, report


def finding_ids(report):
    return {finding.get('id') or finding.get('check_id') for finding in report.get('findings', [])}


def assert_report_shape(report):
    missing = REQUIRED_REPORT_KEYS - set(report)
    assert not missing, missing
    assert report['schema_version'] == 'workflow-harness-report-v1', report
    assert report['workflow'] == 'combined-analyze-propose-v1', report
    assert report['status'] in {'pass', 'review_required', 'fail'}, report
    assert isinstance(report['findings'], list), report
    assert isinstance(report['checks'], list), report
    if report.get('rendered_outputs'):
        md = report['rendered_outputs'].get('markdown')
        assert md is None or '# Workflow harness verification' in md, report['rendered_outputs']


def child_report(workflow, child_root, status='pass', exit_code=0, findings=None):
    findings = findings or []
    counts = {'P0': 0, 'P1': 0, 'P2': 0}
    for finding in findings:
        counts[finding['severity']] += 1
    return {
        'schema_version': 'workflow-harness-report-v1',
        'generated_at': '2026-06-05T00:00:00Z',
        'workflow': workflow,
        'run_root': str(child_root),
        'status': status,
        'exit_code': exit_code,
        'summary': {
            **counts,
            'checks_passed': 1,
            'checks_failed': len(findings),
            'checks_skipped': 0,
            'files_checked': 1,
            'json_files_parsed': 1,
            'links_checked': 0,
            'declared_paths_checked': 0,
        },
        'inputs': {'manifest': None, 'final_index': None, 'final_verification': None, 'parent_return': None},
        'findings': findings,
        'checks': [{'id': 'synthetic.child_report_loaded', 'severity': 'P0', 'result': 'pass', 'path': '.', 'message': 'synthetic child report for M4 acceptance'}],
        'generated_files': [],
        'rendered_outputs': {},
    }


def write_good_root(root):
    asset = root / 'asset-investment-diligence'
    oracle = root / 'oracle-analysis'
    for child in [asset, oracle]:
        (child / 'verification').mkdir(parents=True)
    (root / 'agentic-flow').mkdir(parents=True)
    (root / 'README.md').write_text(
        '# Synthetic combined run\n\n'
        '- Asset child report: [asset](asset-investment-diligence/verification/workflow-harness-report.json)\n'
        '- Oracle child report: [oracle](oracle-analysis/verification/workflow-harness-report.json)\n'
        '- Parent handoff: [handoff](agentic-flow/analyze-and-propose.md)\n',
        encoding='utf-8',
    )
    (asset / 'verification' / 'workflow-harness-report.json').write_text(
        json.dumps(child_report('asset-investment-diligence-v1', asset)), encoding='utf-8')
    (oracle / 'verification' / 'workflow-harness-report.json').write_text(
        json.dumps(child_report('oracle-analysis-v1', oracle)), encoding='utf-8')
    (root / 'agentic-flow' / 'analyze-and-propose.md').write_text(
        '# Analyze and Propose\n\n'
        '## Stage status\n\n'
        '- Discover: complete by user premise.\n'
        '- Analyze: complete.\n'
        '- Propose: `request_more_inputs`.\n'
        '- Preview: blocked.\n'
        '- Execute: blocked.\n'
        '- Monitor: not started.\n\n'
        '## Analyze artifacts\n\n'
        '- Asset child report: `asset-investment-diligence/verification/workflow-harness-report.json`.\n'
        '- Oracle child report: `oracle-analysis/verification/workflow-harness-report.json`.\n\n'
        '## Unresolved gates\n\n'
        '- Gearbox support requires confirmation before Preview.\n'
        '- Wallet eligibility not verified for execution.\n\n'
        '## Requested next checks\n\n'
        '- Confirm Gearbox PFS/feed support.\n'
        '- Confirm wallet eligibility and user policy.\n',
        encoding='utf-8',
    )


with tempfile.TemporaryDirectory() as td:
    base = Path(td)
    good = base / 'good-combined'
    write_good_root(good)

    proc, report = run_validator(good)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert_report_shape(report)
    assert report['status'] == 'pass', report
    ids = finding_ids(report)
    assert not {'flow.unresolved_gates_request_more_inputs', 'flow.preview_execute_blocked_when_unresolved'} & ids, ids

    missing_handoff = base / 'missing-handoff'
    shutil.copytree(good, missing_handoff)
    (missing_handoff / 'agentic-flow' / 'analyze-and-propose.md').unlink()
    proc, report = run_validator(missing_handoff)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert_report_shape(report)
    assert 'flow.propose_handoff_exists' in finding_ids(report), finding_ids(report)

    child_p1 = base / 'child-p1-ready-parent'
    shutil.copytree(good, child_p1)
    asset = child_p1 / 'asset-investment-diligence'
    finding = {
        'id': 'validator.workflow_checks_deferred',
        'severity': 'P1',
        'workflow': 'asset-investment-diligence-v1',
        'path': '.',
        'field': None,
        'expected': 'workflow checks complete',
        'actual': 'deferred',
        'message': 'child validator deferred checks',
        'fix_hint': 'complete child checks',
    }
    (asset / 'verification' / 'workflow-harness-report.json').write_text(
        json.dumps(child_report('asset-investment-diligence-v1', asset, status='review_required', exit_code=1, findings=[finding])),
        encoding='utf-8',
    )
    handoff = child_p1 / 'agentic-flow' / 'analyze-and-propose.md'
    text = handoff.read_text(encoding='utf-8')
    assert 'Propose: `request_more_inputs`.' in text
    mutated = text.replace('Propose: `request_more_inputs`.', 'Propose: `ready_for_preview`.')
    assert mutated != text
    handoff.write_text(mutated, encoding='utf-8')
    proc, report = run_validator(child_p1)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    ids = finding_ids(report)
    assert 'flow.status_reconciles_children' in ids, ids
    assert any(i and i.endswith('validator.workflow_checks_deferred') for i in ids), ids

    unresolved_ready = base / 'unresolved-ready'
    shutil.copytree(good, unresolved_ready)
    handoff = unresolved_ready / 'agentic-flow' / 'analyze-and-propose.md'
    text = handoff.read_text(encoding='utf-8')
    replacements = {
        'Propose: `request_more_inputs`.': 'Propose: `ready_for_preview`.',
        'Preview: blocked.': 'Preview: ready.',
        'Execute: blocked.': 'Execute: ready.',
        'Gearbox support requires confirmation before Preview.': 'Gearbox support unsupported for this Credit Manager envelope.',
        'Wallet eligibility not verified for execution.': 'Wallet eligibility not verified for execution.',
    }
    mutated = text
    for old, new in replacements.items():
        assert old in mutated, old
        mutated = mutated.replace(old, new)
    assert mutated != text
    handoff.write_text(mutated, encoding='utf-8')
    proc, report = run_validator(unresolved_ready)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    ids = finding_ids(report)
    assert 'flow.unresolved_gates_request_more_inputs' in ids, ids
    assert 'flow.preview_execute_blocked_when_unresolved' in ids, ids

    override_claim = base / 'override-claim'
    shutil.copytree(good, override_claim)
    handoff = override_claim / 'agentic-flow' / 'analyze-and-propose.md'
    text = handoff.read_text(encoding='utf-8')
    assert 'Preview: blocked.' in text and 'Execute: blocked.' in text
    mutated = text.replace('Preview: blocked.', 'Preview: ready by linked human override.').replace('Execute: blocked.', 'Execute: ready by linked human override.')
    assert mutated != text
    handoff.write_text(mutated, encoding='utf-8')
    proc, report = run_validator(override_claim)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    ids = finding_ids(report)
    assert 'flow.preview_execute_blocked_when_unresolved' in ids, ids

for path in [
    Path('user/references/workflows/asset-investment-diligence/subagent-prompts.md'),
    Path('user/references/workflows/oracle-analysis/subagent-prompts.md'),
]:
    text = path.read_text(encoding='utf-8')
    missing = sorted(term for term in REQUIRED_PROMPT_FIELDS if term not in text)
    assert not missing, f'{path}: missing {missing}'

for cmd in [
    ['python3', '-m', 'py_compile', 'dev/tools/validate_workflow_run.py'],
    ['git', 'diff', '--check', '--',
     'dev/tools/validate_workflow_run.py',
     'user/references/workflows/asset-investment-diligence/subagent-prompts.md',
     'user/references/workflows/oracle-analysis/subagent-prompts.md'],
    ['git', 'status', '--short', '--',
     'dev/tools/validate_workflow_run.py',
     'user/references/workflows/asset-investment-diligence/subagent-prompts.md',
     'user/references/workflows/oracle-analysis/subagent-prompts.md'],
]:
    proc = subprocess.run(cmd, text=True, capture_output=True)
    assert proc.returncode == 0, (cmd, proc.returncode, proc.stdout, proc.stderr)
    if cmd[:3] == ['git', 'status', '--short']:
        allowed = {
            'dev/tools/validate_workflow_run.py',
            'user/references/workflows/asset-investment-diligence/subagent-prompts.md',
            'user/references/workflows/oracle-analysis/subagent-prompts.md',
        }
        touched = []
        for line in proc.stdout.splitlines():
            if line.strip():
                touched.append(line[3:])
        unexpected = [p for p in touched if p not in allowed]
        assert not unexpected, unexpected

print('M4_COMBINED_ANALYZE_PROPOSE_ACCEPTANCE_PASS')
PY
```

This is the acceptance command for the future M4 implementation task. It is intentionally self-contained and does not require the M5 persistent fixture battery.

## Diff hygiene command for this planning brief

The hardening task that writes this file should run:

```bash
git diff --check -- dev/implementation/workflow-harness/m4-agentic-flow-hardened.md

git status --short -- \
  dev/implementation/workflow-harness/m4-agentic-flow-hardened.md \
  dev/implementation/workflow-harness/m4-agentic-flow-plan.md \
  dev/implementation/workflow-harness/m4-agentic-flow-review.md
```

## Definition of done for M4 implementation

The future M4 implementation is complete only when all conditions below are true:

1. `dev/tools/validate_workflow_run.py` supports `--workflow combined-analyze-propose` using the check catalog in this brief.
2. Child report JSON files are required, parsed, schema-checked, workflow-checked, and imported into the combined report.
3. Child P0/P1 findings and child `fail` / `review_required` statuses cannot be hidden by a permissive parent handoff.
4. `flow.status_reconciles_children` is P1 and is covered by acceptance.
5. Missing or invalid child report JSON produces a non-pass report.
6. Parent handoff parsing accepts normalized markdown bullets and optionally strict JSON, with conflict detection when both are present.
7. Unresolved support, eligibility, feed, route/depth, wallet, Credit Manager envelope, user-policy, and live-input gates force Propose to `request_more_inputs` or `blocked`.
8. Preview and Execute remain blocked while unresolved gates remain. M4 has no human-override bypass.
9. Gate keyword coverage catches `unsupported`, `not enabled`, `unavailable`, `not verified`, `to be confirmed`, `TBD`, `no route`, `no quote`, `no active market`, `no Credit Manager`, `not eligible`, `cannot determine`, and `insufficient data`.
10. Acceptance wrappers read finding IDs via `finding.get('id') or finding.get('check_id')` and assert each fixture mutation changed the source text.
11. `--format json,markdown` behavior matches M1: JSON on stdout; Markdown in `rendered_outputs.markdown` unless `--report-dir` or `--write-verification` writes it to a file.
12. The two prompt docs contain the required parent blocker handoff fields and do not change stage order or workflow meaning.
13. The exact acceptance command above prints `M4_COMBINED_ANALYZE_PROPOSE_ACCEPTANCE_PASS`.
14. Diff hygiene passes for the three implementation files, with unrelated pre-existing vault changes left untouched.

## Out of scope after hardening

- Persistent fixture battery and runbook updates remain M5 scope.
- Human override schema remains a separate future task.
- Recursive child validator execution is optional future hardening; M4 uses child report import as its concrete machine-checkable contract.
- Production economic, oracle-quality, route-quality, allocation, or suitability judgments remain out of scope.
