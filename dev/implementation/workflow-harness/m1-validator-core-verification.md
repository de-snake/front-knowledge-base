# M1 validator core verification

Task: verify validator core CLI and machine-readable report schema for `dev/tools/validate_workflow_run.py`.

Scope: formal workflow-compliance verification only. This review does not assess token economics, oracle correctness, allocation suitability, or execution merit.

Result: pass.

## Context inspected

- `CLAUDE.md`.
- `dev/tools/validate_workflow_run.py`.
- `dev/tools/workflow_harness/tests/test_fixtures.py`.
- `dev/implementation/workflow-harness/fixtures/fixture-matrix.json`.
- `dev/implementation/workflow-harness/m1-validator-core-hardened.md`.

`m1-validator-core-hardened.md` defines `id` as the canonical finding-code field. This verification therefore checks `id`, `severity`, `path`, and `message` for finding shape rather than requiring a separate `code` alias.

## Commands and results

### 1. CLI help exits 0

Command:

```bash
python3 dev/tools/validate_workflow_run.py --help >/tmp/fkb-validator-help.out 2>/tmp/fkb-validator-help.err
```

Observed result:

- exit code: `0`
- stdout bytes: `991`
- stderr bytes: `0`
- traceback present: `False`
- first stdout line: `usage: validate_workflow_run.py [-h] --workflow`

Acceptance: pass.

### 2. Missing run-root emits deterministic fail JSON, not a traceback

Command:

```bash
rm -rf /tmp/fkb-validator-missing-run-root
python3 dev/tools/validate_workflow_run.py \
  --workflow asset-investment-diligence \
  --run-root /tmp/fkb-validator-missing-run-root \
  --format json \
  >/tmp/fkb-validator-missing.json \
  2>/tmp/fkb-validator-missing.err
```

Observed result:

- exit code: `2`
- stdout bytes: `1091`
- stderr bytes: `0`
- traceback present: `False`
- JSON parsed successfully.
- `workflow`: `asset-investment-diligence-v1`
- `run_root`: `/private/tmp/fkb-validator-missing-run-root`
- `status`: `fail`
- report `exit_code`: `2`
- findings count: `1`
- first finding keys: `actual`, `expected`, `fix_hint`, `id`, `message`, `path`, `severity`, `workflow`
- first finding ID: `run_root.exists`
- first finding severity/path/message: `P0` / `.` / `run root does not exist or is not a directory`

Acceptance: pass.

### 3. Empty run-root emits fail JSON, not a traceback

Command:

```bash
rm -rf /tmp/fkb-validator-empty-run-root
mkdir -p /tmp/fkb-validator-empty-run-root
python3 dev/tools/validate_workflow_run.py \
  --workflow asset-investment-diligence \
  --run-root /tmp/fkb-validator-empty-run-root \
  --format json \
  >/tmp/fkb-validator-empty.json \
  2>/tmp/fkb-validator-empty.err
```

Observed result:

- exit code: `2`
- stdout bytes: `21667`
- stderr bytes: `0`
- traceback present: `False`
- JSON parsed successfully.
- `workflow`: `asset-investment-diligence-v1`
- `run_root`: `/private/tmp/fkb-validator-empty-run-root`
- `status`: `fail`
- report `exit_code`: `2`
- findings count: `37`
- first finding keys: `actual`, `expected`, `fix_hint`, `id`, `message`, `path`, `severity`, `workflow`
- first finding ID: `manifest.file_exists`
- first finding severity/path/message: `P0` / `run-manifest.json` / `run-manifest.json is missing`

Acceptance: pass.

### 4. JSON schema contains required machine-readable fields

Command:

```bash
python3 - <<'PY'
import json, pathlib
required_top = {'workflow','run_root','status','findings'}
required_finding = {'id','severity','path','message'}
reports = {
    'missing': json.loads(pathlib.Path('/tmp/fkb-validator-missing.json').read_text()),
    'empty': json.loads(pathlib.Path('/tmp/fkb-validator-empty.json').read_text()),
    'broken_relative_link': json.loads(pathlib.Path('/tmp/fkb-validator-link.json').read_text()),
}
for name, report in reports.items():
    missing_top = required_top - set(report)
    assert not missing_top, (name, missing_top)
    assert isinstance(report['findings'], list), name
    assert report['findings'], name
    for finding in report['findings']:
        missing_finding = required_finding - set(finding)
        assert not missing_finding, (name, finding, missing_finding)
print('schema_check=pass')
print('finding_code_field=id')
print('reports_checked=' + ','.join(reports))
PY
```

Observed result:

```text
schema_check=pass
finding_code_field=id
reports_checked=missing,empty,broken_relative_link
```

Acceptance: pass. The canonical finding code is `id`, matching `m1-validator-core-hardened.md`.

### 5. Link/path checker handles relative paths from nested markdown files

Positive fixture command:

```bash
python3 dev/tools/validate_workflow_run.py \
  --workflow combined-analyze-propose \
  --run-root dev/implementation/workflow-harness/fixtures/good/good-agentic-sample-assets \
  --parent-return agentic-flow/analyze-and-propose.md \
  --format json \
  >/tmp/fkb-validator-good-link.json \
  2>/tmp/fkb-validator-good-link.err
```

Observed result:

- exit code: `0`
- stderr bytes: `0`
- traceback present: `False`
- `workflow`: `combined-analyze-propose-v1`
- `run_root`: `dev/implementation/workflow-harness/fixtures/good/good-agentic-sample-assets`
- `status`: `pass`
- findings count: `0`
- `links.local_paths_resolve`: `pass`, message `run-local artifact links resolve (8 checked)`

Negative nested-link fixture command:

```bash
python3 dev/tools/validate_workflow_run.py \
  --workflow combined-analyze-propose \
  --run-root dev/implementation/workflow-harness/fixtures/bad/broken-relative-link \
  --parent-return agentic-flow/analyze-and-propose.md \
  --format json \
  >/tmp/fkb-validator-link.json \
  2>/tmp/fkb-validator-link.err
```

Observed result:

- exit code: `2`
- stderr bytes: `0`
- traceback present: `False`
- `workflow`: `combined-analyze-propose-v1`
- `run_root`: `dev/implementation/workflow-harness/fixtures/bad/broken-relative-link`
- `status`: `fail`
- findings count: `1`
- finding ID: `links.local_paths_resolve`
- finding message: `agentic-flow/analyze-and-propose.md -> agentic-flow/missing-local-artifact.md: target does not exist`
- check result: `fail`

Acceptance: pass. The positive fixture proves nested relative links resolve when valid. The negative fixture proves a broken link inside `agentic-flow/analyze-and-propose.md` is attributed to that nested source file instead of being treated as a root-level path.

### 6. Fixture regression suite

Command:

```bash
python3 -m pytest dev/tools/workflow_harness/tests/test_fixtures.py -q
```

Observed result:

```text
.....                                                                    [100%]
5 passed in 0.58s
```

Acceptance: pass.

## Verification conclusion

All M1 verification requirements are satisfied:

1. `python3 dev/tools/validate_workflow_run.py --help` exits `0`.
2. Missing and empty run roots produce parseable `fail` JSON with no traceback.
3. JSON output contains `workflow`, `run_root`, `status`, and `findings`; findings carry canonical code field `id` plus `severity`, `path`, and `message`.
4. The link/path checker resolves valid nested relative links and reports invalid nested relative links against the nested markdown source file.
5. The regression fixture suite passes.

No validator implementation changes were made by this verification task.
