# M5 verification — fixtures, runbooks, and external-agent handoff instructions

Scope: formal workflow-compliance verification only. This check does not assess token economic quality, oracle correctness, allocation suitability, or live execution quality.

## Verdict

PASS. The M5 acceptance criteria are satisfied.

No implementation changes were made besides writing this verification artifact.

## Artifacts checked

- `CLAUDE.md`
- `dev/tools/validate_workflow_run.py`
- `dev/tools/workflow_harness/tests/test_fixtures.py`
- `dev/implementation/workflow-harness/fixtures/fixture-matrix.json`
- `dev/implementation/workflow-harness/fixtures/good/good-agentic-sample-assets/README.fixture.md`
- `dev/implementation/workflow-harness/fixtures/bad/missing-final-oracle-verification/README.fixture.md`
- `user/references/workflows/asset-investment-diligence/runbook.md`
- `user/references/workflows/oracle-analysis/runbook.md`
- `user/references/workflows/asset-investment-diligence/output-structure.md`
- `user/references/workflows/oracle-analysis/output-structure.md`
- `user/references/workflows/asset-investment-diligence/subagent-prompts.md`
- `user/references/workflows/oracle-analysis/subagent-prompts.md`

## Acceptance checks

| Requirement | Result | Evidence |
| --- | --- | --- |
| At least one known-bad fixture and one known-good/current fixture are documented. | PASS | `fixture-matrix.json` contains 9 documented rows: 1 good/current row with `expected_status: pass` (`good/good-agentic-sample-assets`) and 8 known-bad rows with expected non-pass statuses and `expected_findings`. Representative fixture docs exist at `fixtures/good/good-agentic-sample-assets/README.fixture.md` and `fixtures/bad/missing-final-oracle-verification/README.fixture.md`. |
| Runbooks include exact validator commands. | PASS | Both runbooks include `python3 dev/tools/validate_workflow_run.py`, `--workflow`, `--run-root <run_artifact_root>`, `--format json,markdown`, `--report-dir <run_artifact_root>/verification`, and `--write-verification`. Asset command appears in `asset-investment-diligence/runbook.md`; oracle command appears in `oracle-analysis/runbook.md`. |
| Final verification template is harness-backed, not hand-written pass tables. | PASS | Both `output-structure.md` files require deterministic `workflow-harness-report.json` and `workflow-harness-verification.md` outputs. The runbooks require `--write-verification` and say unresolved `review_required` findings must include the harness command, exit code, report path, and finding ids in the final parent-agent handoff. |
| External-agent instruction snippet exists and is paste-ready. | PASS | `asset-investment-diligence/subagent-prompts.md` explicitly says the prompts are paste-ready and requires `workflow_harness_report` and `commands_run` in worker returns. `oracle-analysis/subagent-prompts.md` provides fenced `text` prompt snippets for workers/reviewer and requires the same machine-checkable return fields. |

## Commands run and results

### Validator syntax and help

Command:

```bash
python3 -m py_compile dev/tools/validate_workflow_run.py && \
python3 dev/tools/validate_workflow_run.py --help >/tmp/m5-validator-help.txt && \
printf 'PY_COMPILE_PASS\nVALIDATOR_HELP_PASS\n'
```

Result:

```text
exit_code=0
PY_COMPILE_PASS
VALIDATOR_HELP_PASS
```

### Fixture regression suite

Command:

```bash
python3 -m pytest dev/tools/workflow_harness/tests/test_fixtures.py -q
```

Result:

```text
exit_code=0
.....                                                                    [100%]
5 passed in 0.54s
```

This suite verifies the exact fixture matrix rows, physical fixture trees, expected good/bad statuses, expected findings, and parent-return edge cases.

### Known-good fixture direct run

Command:

```bash
python3 dev/tools/validate_workflow_run.py \
  --workflow combined-analyze-propose \
  --run-root dev/implementation/workflow-harness/fixtures/good/good-agentic-sample-assets \
  --parent-return agentic-flow/analyze-and-propose.md \
  --format json
```

Result summary:

```text
exit_code=0
status=pass
checks_passed=22
checks_skipped=1
findings=[]
```

### Known-bad fixture direct run

Command:

```bash
set +e
python3 dev/tools/validate_workflow_run.py \
  --workflow combined-analyze-propose \
  --run-root dev/implementation/workflow-harness/fixtures/bad/missing-final-oracle-verification \
  --parent-return agentic-flow/analyze-and-propose.md \
  --format json
rc=$?
printf '\nBAD_FIXTURE_EXIT_CODE=%s\n' "$rc"
exit 0
```

Result summary:

```text
BAD_FIXTURE_EXIT_CODE=2
status=fail
findings:
- child.oracle.oracle.canonical_final_verification_path
- child.oracle.status_fail
- flow.status_reconciles_children
```

This proves the known-bad fixture is not only documented but actively rejected by the harness.

### M5 documentation contract probe

Command:

```bash
python3 - <<'PY'
import json
from pathlib import Path
root = Path('.')
matrix_path = root / 'dev/implementation/workflow-harness/fixtures/fixture-matrix.json'
rows = json.loads(matrix_path.read_text())
good = [r for r in rows if r['id'].startswith('good/') and r.get('expected_status') == 'pass']
bad = [r for r in rows if r['id'].startswith('bad/') and r.get('expected_status') in {'fail', 'review_required'}]
assert good, 'no documented known-good fixture with expected_status pass'
assert bad, 'no documented known-bad fixture with expected_status fail/review_required'
assert all('run_root' in r and 'workflow' in r and 'expected_exit_code' in r for r in rows), 'fixture row missing command contract fields'
assert any(r.get('expected_findings') for r in bad), 'known-bad fixtures need expected_findings'

for rel in [
    'user/references/workflows/asset-investment-diligence/runbook.md',
    'user/references/workflows/oracle-analysis/runbook.md',
]:
    text = (root / rel).read_text()
    assert 'python3 dev/tools/validate_workflow_run.py' in text, rel
    assert '--workflow ' in text, rel
    assert '--run-root <run_artifact_root>' in text, rel
    assert '--format json,markdown' in text, rel
    assert '--report-dir <run_artifact_root>/verification' in text, rel
    assert '--write-verification' in text, rel
    assert 'Completion rule: fix all P0 findings before returning the run as complete.' in text, rel

for rel in [
    'user/references/workflows/asset-investment-diligence/output-structure.md',
    'user/references/workflows/oracle-analysis/output-structure.md',
]:
    text = (root / rel).read_text()
    assert 'workflow-harness-report.json' in text, rel
    assert 'workflow-harness-verification.md' in text, rel
    assert 'workflow-harness-report.md' not in text, rel
    assert 'machine-readable report with status, exit code, checks, and findings' in text, rel

for rel in [
    'user/references/workflows/asset-investment-diligence/subagent-prompts.md',
    'user/references/workflows/oracle-analysis/subagent-prompts.md',
]:
    text = (root / rel).read_text()
    assert 'paste-ready' in text.lower() or '```text' in text, rel
    assert 'workflow_harness_report' in text, rel
    assert 'commands_run' in text, rel
    assert 'Do not handwave final verification' in text, rel
    assert 'return' in text.lower(), rel

print('M5_ACCEPTANCE_DOC_CONTRACT_PASS')
print(f'fixture_rows={len(rows)} good={len(good)} bad={len(bad)}')
print('runbook_commands=asset-investment-diligence,oracle-analysis')
print('harness_outputs=workflow-harness-report.json,workflow-harness-verification.md')
print('external_snippets=asset-investment-diligence/subagent-prompts.md,oracle-analysis/subagent-prompts.md')
PY
```

Result:

```text
exit_code=0
M5_ACCEPTANCE_DOC_CONTRACT_PASS
fixture_rows=9 good=1 bad=8
runbook_commands=asset-investment-diligence,oracle-analysis
harness_outputs=workflow-harness-report.json,workflow-harness-verification.md
external_snippets=asset-investment-diligence/subagent-prompts.md,oracle-analysis/subagent-prompts.md
```

### Diff whitespace check

Command:

```bash
git diff --check -- dev/implementation/workflow-harness/m5-fixtures-docs-verification.md dev/tools/validate_workflow_run.py dev/tools/workflow_harness/tests/test_fixtures.py user/references/workflows/asset-investment-diligence/runbook.md user/references/workflows/oracle-analysis/runbook.md user/references/workflows/asset-investment-diligence/output-structure.md user/references/workflows/oracle-analysis/output-structure.md user/references/workflows/asset-investment-diligence/subagent-prompts.md user/references/workflows/oracle-analysis/subagent-prompts.md
```

Result:

```text
exit_code=0
(no output)
```

## Notes

- The fixture battery is deterministic and regression-covered by `test_fixtures.py`.
- The final verification path is harness-backed through generated `workflow-harness-report.json` and `workflow-harness-verification.md` artifacts, not free-form human pass tables.
- The external-agent snippets require machine-checkable return fields, including `workflow_harness_report` and `commands_run`, so parent agents can verify downstream claims without relying on prose assurance.
