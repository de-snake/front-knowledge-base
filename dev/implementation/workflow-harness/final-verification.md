# Final verification: workflow harness battery

Generated: 2026-06-05 21:28:46 UTC
Workspace: `/Users/ilya/Documents/Codex/front-knowledge-base`
Kanban task: `t_4f0b136b`

## Executive verdict

PASS for the formal workflow-harness battery.

The validator help path works, malformed and empty run roots fail mechanically, the known-bad external asset and oracle runs are rejected, the known-good/current combined parent fixture passes, the fixture matrix catches all expected false-pass cases, repository diff whitespace checks pass, and the ai-assistant monorepo workspace policy checks pass.

No token economic quality, oracle correctness, allocation suitability, or live execution merit was assessed.

## Scope and parent-run availability

- Parent milestone verification artifacts were available in the Kanban parent handoff for M1 through M5.
- `dev/implementation/workflow-harness/fixtures/fixture-matrix.json` identifies `good/good-agentic-sample-assets` as the known-good/current combined parent fixture.
- A file search for `analyze-and-propose.md` under `dev/implementation/` returned fixture parent-return files only, so the combined-flow check used the known-good/current fixture from the matrix.

## Command evidence

### 1. Validator syntax check

Command:

```bash
python3 -m py_compile dev/tools/validate_workflow_run.py
```

Workdir: `/Users/ilya/Documents/Codex/front-knowledge-base`
Exit code: `0`
Validation output: no output.

### 2. Validator help

Command:

```bash
python3 dev/tools/validate_workflow_run.py --help
```

Workdir: `/Users/ilya/Documents/Codex/front-knowledge-base`
Exit code: `0`
Validation output excerpt:

```text
usage: validate_workflow_run.py [-h] --workflow
                                {asset-investment-diligence,combined-analyze-propose,oracle-analysis}
                                --run-root RUN_ROOT
                                [--format {json,json,markdown,markdown}]
                                [--parent-return PARENT_RETURN]
                                [--report-dir REPORT_DIR]
                                [--write-verification] [--strict-warnings]
```

### 3. Failure-mode smoke: missing run root

Command:

```bash
rm -rf /tmp/fkb-final-missing-run-root && python3 dev/tools/validate_workflow_run.py --workflow asset-investment-diligence --run-root /tmp/fkb-final-missing-run-root --format json
```

Workdir: `/Users/ilya/Documents/Codex/front-knowledge-base`
Exit code: `2`
Validation output:

- status: `fail`
- checks failed: `1`
- finding ids: `run_root.exists`

This confirms the validator rejects a missing run root instead of passing silently.

### 4. Failure-mode smoke: empty run root

Command:

```bash
rm -rf /tmp/fkb-final-empty-run-root && mkdir -p /tmp/fkb-final-empty-run-root && python3 dev/tools/validate_workflow_run.py --workflow asset-investment-diligence --run-root /tmp/fkb-final-empty-run-root --format json
```

Workdir: `/Users/ilya/Documents/Codex/front-knowledge-base`
Exit code: `2`
Validation output:

- status: `fail`
- checks failed: `37`
- severity counts: `P0=10`, `P1=27`, `P2=0`
- finding ids included:
  - `manifest.file_exists`
  - `asset.manifest.token_entries_present`
  - `asset.root.required_file_exists`
  - `asset.skipped_pt.index_exists`
  - `asset.skipped_pt.marker_present`
  - `asset.skipped_pt.reason_present`
  - `asset.skipped_social.index_exists`
  - `asset.skipped_social.marker_present`
  - `asset.skipped_social.reason_present`
  - `asset.s6.required_field_present`
  - `asset.final_verification.file_exists`
  - `asset.final_verification.status_present`
  - `asset.final_verification.required_file_checks_present`
  - `asset.final_verification.required_field_checks_present`
  - `asset.final_verification.skipped_stage_checks_present`
  - `asset.final_verification.cross_links_checked`
  - `asset.final_verification.workspace_validation_present`
  - `asset.readme_handoff_sections`
  - `asset.index_contract_sections`

This confirms empty-folder false positives are caught mechanically.

### 5. Asset harness against known-bad external asset run

Command:

```bash
python3 dev/tools/validate_workflow_run.py --workflow asset-investment-diligence --run-root dev/implementation/asset-diligence-2026-06-05-sample-base-token-sample-vault-token --format json
```

Workdir: `/Users/ilya/Documents/Codex/front-knowledge-base`
Exit code: `2`
Validation output:

- status: `fail`
- checks failed: `26`
- checks passed: `105`
- severity counts: `P0=1`, `P1=25`, `P2=0`
- files checked: `27`
- JSON files parsed: `3`
- links checked: `1`
- finding ids:
  - `asset.s2.technical_appendix_pointer_present`
  - `asset.s1.required_fact_slot_present`
  - `asset.skipped_pt.reason_present`
  - `asset.s6.required_field_present`
  - `asset.s6.required_field_has_value_state`
  - `asset.s6.heading_only_false_pass`
  - `asset.final_verification.status_present`
  - `asset.final_verification.required_file_checks_present`
  - `asset.final_verification.required_field_checks_present`
  - `asset.final_verification.skipped_stage_checks_present`
  - `asset.final_verification.cross_links_checked`
  - `asset.final_verification.workspace_validation_present`
  - `asset.readme_handoff_sections`
  - `asset.index_contract_sections`
  - `links.local_paths_resolve`

Result: the external asset run does not false-pass; the validator rejects missing formal fields, heading-only overclaim, weak final verification, missing handoff/index sections, and a broken local path.

### 6. Oracle harness against known-bad external oracle run

Command:

```bash
python3 dev/tools/validate_workflow_run.py --workflow oracle-analysis --run-root dev/implementation/oracle-analysis-2026-06-05-sample-base-token-sample-vault-token --format json
```

Workdir: `/Users/ilya/Documents/Codex/front-knowledge-base`
Exit code: `2`
Validation output:

- status: `fail`
- checks failed: `22`
- checks passed: `29`
- severity counts: `P0=2`, `P1=20`, `P2=0`
- files checked: `27`
- JSON files parsed: `1`
- finding ids:
  - `oracle.manifest_schema`
  - `oracle.required_files_present`
  - `oracle.readme_handoff_sections`
  - `oracle.source_primitive_audit_present`
  - `oracle.run_status_reconciles`
  - `oracle.pricing_formula_present`
  - `oracle.stress_tradeoff_fields`
  - `oracle.conclusion_quad_present`
  - `oracle.gearbox_fields_present`
  - `oracle.node_classification_present`
  - `oracle.no_top_level_only_verdict`

Result: the external oracle run does not false-pass; the validator rejects missing schema fields, missing final verification, weak source-primitive audits, missing formulas, missing side-specific conclusion fields, missing Gearbox fields, and top-level-label-only verdicts.

### 7. Combined-flow harness against known-good/current parent fixture

Command:

```bash
python3 dev/tools/validate_workflow_run.py --workflow combined-analyze-propose --run-root dev/implementation/workflow-harness/fixtures/good/good-agentic-sample-assets --parent-return agentic-flow/analyze-and-propose.md --format json
```

Workdir: `/Users/ilya/Documents/Codex/front-knowledge-base`
Exit code: `0`
Validation output:

- status: `pass`
- checks failed: `0`
- checks passed: `22`
- checks skipped: `1`
- files checked: `8`
- JSON files parsed: `2`
- links checked: `1`
- finding count: `0`

Result: the known-good/current combined parent fixture passes.

### 8. Fixture matrix false-pass probe

Command:

```bash
python3 - <<'INNER'
import json
import subprocess
import sys
from pathlib import Path
root = Path.cwd()
rows = json.loads((root / 'dev/implementation/workflow-harness/fixtures/fixture-matrix.json').read_text())
summary = []
mismatches = []
false_passes = []
for row in rows:
    cmd = ['python3', 'dev/tools/validate_workflow_run.py', '--workflow', row['workflow'], '--run-root', row['run_root'], '--format', 'json']
    if row.get('parent_return'):
        cmd.extend(['--parent-return', row['parent_return']])
    proc = subprocess.run(cmd, cwd=root, text=True, capture_output=True)
    report = json.loads(proc.stdout)
    found = sorted({f.get('id') or f.get('check_id') for f in report.get('findings', []) if isinstance(f, dict)})
    expected_findings = set(row.get('expected_findings', []))
    missing_expected = sorted(expected_findings - set(found))
    row_summary = {
        'id': row['id'],
        'actual_exit_code': proc.returncode,
        'actual_status': report.get('status'),
        'expected_findings_present': not missing_expected,
    }
    summary.append(row_summary)
    if proc.returncode != row['expected_exit_code'] or report.get('status') != row['expected_status'] or missing_expected:
        mismatches.append(row_summary)
    if row['expected_status'] != 'pass' and proc.returncode == 0 and report.get('status') == 'pass':
        false_passes.append(row['id'])
result = {'rows_total': len(rows), 'false_passes': false_passes, 'mismatches': mismatches, 'rows': summary}
print(json.dumps(result, indent=2, sort_keys=True))
sys.exit(0 if not false_passes and not mismatches else 1)
INNER
```

Workdir: `/Users/ilya/Documents/Codex/front-knowledge-base`
Exit code: `0`
Validation output:

- rows total: `9`
- false passes: `[]`
- mismatches: `[]`
- row outcomes:
  - `good/good-agentic-sample-assets`: exit `0`, status `pass`, expected findings present `true`
  - `bad/missing-final-oracle-verification`: exit `2`, status `fail`, expected findings present `true`
  - `bad/asset-heading-overclaim`: exit `2`, status `fail`, expected findings present `true`
  - `bad/broken-relative-link`: exit `2`, status `fail`, expected findings present `true`
  - `bad/oracle-side-specific-omission`: exit `2`, status `fail`, expected findings present `true`
  - `bad/ready-for-preview-incorrectly`: exit `1`, status `review_required`, expected findings present `true`
  - `bad/missing-propose-handoff`: exit `2`, status `fail`, expected findings present `true`
  - `bad/missing-parent-return-status`: exit `1`, status `review_required`, expected findings present `true`
  - `bad/no-parent-return-artifact`: exit `2`, status `fail`, expected findings present `true`

Result: all fixture false-pass cases are caught mechanically.

### 9. Pytest fixture regression

Command:

```bash
python3 -m pytest dev/tools/workflow_harness/tests/test_fixtures.py -q
```

Workdir: `/Users/ilya/Documents/Codex/front-knowledge-base`
Exit code: `0`
Validation output:

```text
.....                                                                    [100%]
5 passed in 0.52s
```

### 10. Repository whitespace diff check before this report

Command:

```bash
git diff --check
```

Workdir: `/Users/ilya/Documents/Codex/front-knowledge-base`
Exit code: `0`
Validation output: no output.

### 11. Monorepo workspace sync check

Command:

```bash
python3 scripts/workspace_sync.py --check
```

Workdir: `/Users/ilya/ai-assistant`
Exit code: `0`
Validation output: no output.

### 12. Monorepo workspace policy check

Command:

```bash
python3 scripts/workspace_policy_check.py --all
```

Workdir: `/Users/ilya/ai-assistant`
Exit code: `0`
Validation output:

```text
Workspace policy check: PASS
```

### 13. Repository whitespace diff check after writing this report

Command:

```bash
git diff --check
```

Workdir: `/Users/ilya/Documents/Codex/front-knowledge-base`
Exit code: `0`
Validation output: no output.

### 14. Final report file sanity check

Command:

```bash
python3 - <<'PY'
from pathlib import Path
p = Path('dev/implementation/workflow-harness/final-verification.md')
text = p.read_text()
print({
    'exists': p.exists(),
    'bytes': p.stat().st_size,
    'ends_with_newline': text.endswith('\n'),
    'trailing_whitespace_lines': [i + 1 for i, line in enumerate(text.splitlines()) if line.rstrip() != line][:10],
    'line_count': len(text.splitlines()),
})
PY
```

Workdir: `/Users/ilya/Documents/Codex/front-knowledge-base`
Exit code: `0`
Validation output:

```text
{'exists': True, 'bytes': 12248, 'ends_with_newline': True, 'trailing_whitespace_lines': [], 'line_count': 368}
```

## Remaining blockers

None for the requested final verification.

The repository working tree had many pre-existing unrelated modifications and deletions before this report was written. This verification run intentionally changed only `dev/implementation/workflow-harness/final-verification.md`.
