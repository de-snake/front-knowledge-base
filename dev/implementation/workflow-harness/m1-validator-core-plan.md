# M1 validator core implementation brief

Purpose: implement only the base workflow-harness CLI and machine-readable report contract for `front-knowledge-base` workflow runs. This is the first implementation slice from `hardened-plan.md`; it must not implement asset, oracle, or combined-flow semantic checks yet, and it must not report a production `pass` while those checks remain deferred.

This brief is an implementation handoff. It does not change workflow meaning, does not assess token economics or oracle correctness, and does not edit runtime workflow prose.

## Inputs read

- `CLAUDE.md`
- `dev/implementation/workflow-harness/plan.md`
- `dev/implementation/workflow-harness/plan-review.md`
- `dev/implementation/workflow-harness/hardened-plan.md`

## Edit boundary for the M1 implementation

M1 may edit exactly one implementation file:

- `dev/tools/validate_workflow_run.py`

M1 must not edit these files or directories:

- `CLAUDE.md`
- `README.md`
- `user/references/workflows/**`
- `dev/tools/workflow_harness/**`
- historical run artifacts under `dev/implementation/asset-diligence-2026-06-05-sample-base-token-sample-vault-token/**`
- historical run artifacts under `dev/implementation/oracle-analysis-2026-06-05-sample-base-token-sample-vault-token/**`

No fixture files are required for M1. If the implementer finds fixture files necessary, stop and split that work into a later fixture slice rather than expanding this one.

## M1 scope

Implement the reusable core inside `dev/tools/validate_workflow_run.py` as a single importable Python script:

1. CLI argument parsing and validation.
2. Severity model, status model, and exit-code policy.
3. JSON report schema.
4. Markdown verification rendering.
5. Safe path normalization helpers.
6. Manifest loading helpers.
7. Markdown section and local-link extraction helpers.
8. Explicit skipped-stage marker helpers.
9. A deferred-check finding that prevents false green reports until later milestones implement workflow-specific checks.

Out of scope for M1:

- full asset workflow validation;
- full oracle workflow validation;
- combined Analyze -> Propose state-machine validation;
- parent-return reconciliation;
- pytest fixture matrix;
- workflow documentation or prompt updates;
- live RPC, explorer, web, X, Dune, or LLM calls;
- automatic repair of run artifacts.

## CLI contract

Required command shape:

```bash
python3 dev/tools/validate_workflow_run.py \
  --workflow <asset-investment-diligence|oracle-analysis|combined-analyze-propose> \
  --run-root <path> \
  --format <json|markdown|json,markdown> \
  [--report-dir <path>] \
  [--write-verification] \
  [--strict-warnings]
```

Argument behavior:

- `--workflow` maps to canonical report workflow IDs:
  - `asset-investment-diligence` -> `asset-investment-diligence-v1`
  - `oracle-analysis` -> `oracle-analysis-v1`
  - `combined-analyze-propose` -> `combined-analyze-propose-v1`
- `--run-root` is resolved from the current working directory but reported as a stable path relative to the repository root when possible.
- `--format` accepts only `json`, `markdown`, or `json,markdown`.
- invalid CLI input exits `2` through `argparse`.
- default mode is read-only and writes nothing unless `--report-dir` or `--write-verification` is supplied.

Output behavior:

- `--format json` prints compact JSON to stdout.
- `--format markdown` prints Markdown to stdout.
- `--format json,markdown` prints JSON to stdout and writes Markdown only when `--report-dir` or `--write-verification` supplies a destination. If no destination is supplied, include the rendered Markdown string under `rendered_outputs.markdown` in the JSON report rather than printing mixed machine-readable and prose output.
- `--report-dir` writes generated reports there with deterministic names:
  - `workflow-harness-report.json`
  - `workflow-harness-verification.md`
- `--write-verification` writes generated harness Markdown under the run root:
  - asset and oracle runs: `verification/workflow-harness-verification.md`
  - combined runs: `verification/combined-analyze-propose-verification.md`
- The script must never create or overwrite canonical workflow final verification files:
  - `verification/final-investment-analysis-verification.md`
  - `verification/final-oracle-analysis-verification.md`

## Exit-code and status policy

Severity semantics:

- `P0`: structural failure. Report `status="fail"`; exit `2`.
- `P1`: contract failure or false-pass risk. Report `status="review_required"` when no P0 exists; exit `1`.
- `P2`: hardening warning. Report can stay `status="pass"`; exit `0` unless `--strict-warnings` is set, then exit `1`.

Status calculation:

1. If any P0 finding exists, `status="fail"`, `exit_code=2`.
2. Else if any P1 finding exists, `status="review_required"`, `exit_code=1`.
3. Else if `--strict-warnings` and any P2 finding exists, `status="review_required"`, `exit_code=1`.
4. Else `status="pass"`, `exit_code=0`.

M1 must add a P1 finding with ID `validator.workflow_checks_deferred` for otherwise valid runs. This prevents the core CLI from returning a false `pass` before M2-M6 add the real workflow checks. Later milestones may remove this finding only after the relevant check catalog is implemented and covered by acceptance tests.

## JSON report schema

The report must be a single JSON object with stable top-level keys:

```json
{
  "schema_version": "workflow-harness-report-v1",
  "generated_at": "2026-06-05T00:00:00Z",
  "workflow": "asset-investment-diligence-v1",
  "run_root": "dev/implementation/example-run",
  "status": "pass | review_required | fail",
  "exit_code": 0,
  "summary": {
    "P0": 0,
    "P1": 0,
    "P2": 0,
    "checks_passed": 0,
    "checks_failed": 0,
    "checks_skipped": 0,
    "files_checked": 0,
    "json_files_parsed": 0,
    "links_checked": 0,
    "declared_paths_checked": 0
  },
  "inputs": {
    "manifest": "run-manifest.json",
    "final_index": null,
    "final_verification": null,
    "parent_return": null
  },
  "findings": [],
  "checks": [],
  "generated_files": [],
  "rendered_outputs": {}
}
```

Finding shape:

```json
{
  "id": "validator.workflow_checks_deferred",
  "severity": "P1",
  "workflow": "asset-investment-diligence-v1",
  "path": ".",
  "field": null,
  "expected": "workflow-specific checks implemented before production pass",
  "actual": "M1 core only",
  "message": "Workflow-specific checks are deferred in M1, so this report cannot be treated as a production pass.",
  "fix_hint": "Complete the later validator milestones and remove this deferred-check finding only when covered by fixture tests."
}
```

Check result shape:

```json
{
  "id": "manifest.json_valid",
  "severity": "P0",
  "result": "pass | fail | skipped",
  "path": "run-manifest.json",
  "message": "run-manifest.json parsed successfully"
}
```

Report rules:

- Keep paths relative to the repository root or run root when possible.
- Do not include raw evidence dumps in findings.
- Keep check IDs stable.
- Include all generated report paths in `generated_files`.
- Include command evidence in Markdown, not raw command transcripts in JSON.

## Core checks required in M1

M1 should implement only common checks that do not depend on the final asset/oracle/combined contracts:

| Check ID | Severity | Required behavior |
| --- | --- | --- |
| `cli.input_valid` | P0 | Pass after argparse accepts workflow, run root, and format. Invalid argparse input exits `2` before report construction. |
| `run_root.exists` | P0 | Fail if `--run-root` does not exist or is not a directory. |
| `manifest.file_exists` | P0 | Fail if `<run-root>/run-manifest.json` is missing for asset or oracle runs. For combined runs, skip with message `combined manifest deferred until M5`. |
| `manifest.json_valid` | P0 | Parse `<run-root>/run-manifest.json` when present; fail on invalid JSON. |
| `validator.workflow_checks_deferred` | P1 | Always fail as a finding in M1 after common checks complete. |

For combined runs in M1, the script should not attempt child validation. It should emit `validator.workflow_checks_deferred` and skipped check entries for child validation so the report is honest about the missing implementation.

## Reusable helper requirements

Even though M1 is a single-file implementation, write helper functions as if they will be extracted later. Use Python standard library only.

Required dataclasses or equivalent typed structures:

- `Finding`
- `CheckResult`
- `Report`
- `ValidationContext`

Required helper functions:

- `repo_relative(path: Path, repo_root: Path) -> str`
- `resolve_under_root(value: str, *, root: Path, source_file: Path | None = None) -> tuple[Path | None, str | None]`
  - returns a resolved path and no error when the value stays under `root`;
  - returns no path and an error message for absolute paths, parent-escaping paths, or malformed values;
  - treats paths as relative to `source_file.parent` when `source_file` is supplied, otherwise relative to `root`.
- `load_json(path: Path) -> tuple[dict | None, str | None]`
- `load_manifest(run_root: Path) -> tuple[dict | None, list[Finding], list[CheckResult]]`
- `extract_markdown_sections(text: str) -> dict[str, str]`
  - keys should be normalized heading text;
  - section bodies should exclude the heading line.
- `extract_local_markdown_links(text: str) -> list[str]`
  - include Markdown links with local targets;
  - include Obsidian-style `[[Note#Anchor|label]]` values as raw local targets;
  - ignore `http://`, `https://`, `mailto:`, and fragment-only links.
- `extract_code_spanned_paths(text: str) -> list[str]`
  - return code-spanned values that look like local artifact paths.
- `has_skipped_marker(text: str, topic: str) -> bool`
  - return true for explicit markers such as `skipped`, `not_in_scope`, `not in scope`, `not applicable`, or `no <topic> in scope`.
- `make_report(context, findings, checks, generated_files) -> Report`
- `render_json(report: Report) -> str`
- `render_markdown(report: Report, command: list[str]) -> str`

Path helper guardrails:

- Do not silently normalize parent-escaping paths.
- Do not treat sibling run directories as local valid paths in M1.
- Do not follow symlinks outside the run root when resolving declared artifact paths.
- Keep returned error messages specific enough for future findings.

Markdown helper guardrails:

- Do not claim full CommonMark parsing.
- Use deterministic regex-based extraction that is good enough for local workflow artifacts.
- Keep helper functions pure and importable for later tests.

## Markdown verification output

Generated Markdown must use this section shape:

````markdown
# Workflow harness verification

- Workflow: <workflow id>
- Run root: <path>
- Status: <pass|review_required|fail>
- Generated at: <UTC ISO timestamp>
- Validator command: `<exact command>`
- Exit code: <exit code>

## Summary

| Severity | Count |
| --- | ---: |
| P0 | 0 |
| P1 | 1 |
| P2 | 0 |

## Findings

| Severity | Check ID | Path | Message | Fix hint |
| --- | --- | --- | --- | --- |

## Checks run

| Check ID | Result | Path | Message |
| --- | --- | --- | --- |

## JSON report

```json
{...compact report...}
```
````

Markdown rules:

- Escape pipe characters in table cells.
- Keep JSON compact and deterministic enough for review.
- Do not include raw run artifacts or raw source dumps.
- If there are no findings, put a single row saying no findings.

## Implementation sequence

1. Create `dev/tools/validate_workflow_run.py` with an import-safe `main(argv=None)` and `if __name__ == "__main__": raise SystemExit(main())`.
2. Add constants for schema version, workflow ID mapping, valid formats, generated verification filenames, canonical final-verification filenames, and severity order.
3. Add dataclasses and serialization helpers.
4. Add CLI parsing.
5. Add context construction and common M1 checks.
6. Add JSON rendering.
7. Add Markdown rendering.
8. Add `--report-dir` and `--write-verification` output handling with canonical-final-verification protection.
9. Add helper functions for paths, manifests, Markdown sections, local links, code-spanned paths, and skipped markers.
10. Run the acceptance commands below from `/Users/ilya/Documents/Codex/front-knowledge-base`.

## Acceptance commands

Run all commands from `/Users/ilya/Documents/Codex/front-knowledge-base` after implementing M1.

### 1. CLI help and invalid input

```bash
python3 dev/tools/validate_workflow_run.py --help

python3 - <<'PY'
import subprocess
proc = subprocess.run([
    "python3", "dev/tools/validate_workflow_run.py",
    "--workflow", "bad",
    "--run-root", ".",
    "--format", "json",
], text=True, capture_output=True)
assert proc.returncode == 2, proc.stdout + proc.stderr
PY
```

### 2. JSON schema and deferred-check safety

```bash
python3 - <<'PY'
import json
import subprocess
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as td:
    root = Path(td) / "asset-run"
    root.mkdir()
    (root / "run-manifest.json").write_text(json.dumps({
        "workflow_id": "asset-investment-diligence-v1",
        "run_id": "m1-smoke",
        "run_artifact_root": str(root),
        "final_index": "index.md",
        "final_verification": "verification/final-investment-analysis-verification.md",
    }), encoding="utf-8")
    proc = subprocess.run([
        "python3", "dev/tools/validate_workflow_run.py",
        "--workflow", "asset-investment-diligence",
        "--run-root", str(root),
        "--format", "json",
    ], text=True, capture_output=True)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    report = json.loads(proc.stdout)
    required = {"schema_version", "generated_at", "workflow", "run_root", "status", "exit_code", "summary", "inputs", "findings", "checks", "generated_files"}
    assert required <= set(report), report
    assert report["schema_version"] == "workflow-harness-report-v1"
    assert report["workflow"] == "asset-investment-diligence-v1"
    assert report["status"] == "review_required"
    assert report["exit_code"] == 1
    assert report["summary"]["P1"] >= 1
    ids = {finding["id"] for finding in report["findings"]}
    assert "validator.workflow_checks_deferred" in ids, ids
PY
```

### 3. Missing and invalid manifests return P0 reports

```bash
python3 - <<'PY'
import json
import subprocess
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as td:
    missing = Path(td) / "missing-manifest"
    missing.mkdir()
    proc = subprocess.run([
        "python3", "dev/tools/validate_workflow_run.py",
        "--workflow", "asset-investment-diligence",
        "--run-root", str(missing),
        "--format", "json",
    ], text=True, capture_output=True)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    report = json.loads(proc.stdout)
    assert report["status"] == "fail"
    assert any(f["id"] == "manifest.file_exists" and f["severity"] == "P0" for f in report["findings"]), report

    invalid = Path(td) / "invalid-manifest"
    invalid.mkdir()
    (invalid / "run-manifest.json").write_text("{not json", encoding="utf-8")
    proc = subprocess.run([
        "python3", "dev/tools/validate_workflow_run.py",
        "--workflow", "oracle-analysis",
        "--run-root", str(invalid),
        "--format", "json",
    ], text=True, capture_output=True)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    report = json.loads(proc.stdout)
    assert report["status"] == "fail"
    assert any(f["id"] == "manifest.json_valid" and f["severity"] == "P0" for f in report["findings"]), report
PY
```

### 4. Markdown verification generation and canonical-file protection

```bash
python3 - <<'PY'
import json
import subprocess
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as td:
    root = Path(td) / "oracle-run"
    root.mkdir()
    (root / "run-manifest.json").write_text(json.dumps({
        "workflow_id": "oracle-analysis-v1",
        "run_id": "m1-markdown-smoke",
        "run_artifact_root": str(root),
        "final_index": "index.md",
        "final_verification": "verification/final-oracle-analysis-verification.md",
    }), encoding="utf-8")
    proc = subprocess.run([
        "python3", "dev/tools/validate_workflow_run.py",
        "--workflow", "oracle-analysis",
        "--run-root", str(root),
        "--format", "json",
        "--write-verification",
    ], text=True, capture_output=True)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    report = json.loads(proc.stdout)
    harness_md = root / "verification" / "workflow-harness-verification.md"
    canonical_md = root / "verification" / "final-oracle-analysis-verification.md"
    assert harness_md.exists(), report
    assert not canonical_md.exists(), "validator must not create canonical final verification"
    md = harness_md.read_text(encoding="utf-8")
    for marker in ["# Workflow harness verification", "## Summary", "## Findings", "## Checks run", "## JSON report"]:
        assert marker in md, marker
    assert "validator.workflow_checks_deferred" in md
PY
```

### 5. Helper import smoke test

```bash
python3 - <<'PY'
import importlib.util
from pathlib import Path

path = Path("dev/tools/validate_workflow_run.py")
spec = importlib.util.spec_from_file_location("validate_workflow_run", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

sections = mod.extract_markdown_sections("# Title\nIntro\n\n## Alpha\nA\n\n## Beta\nB\n")
assert "alpha" in sections and sections["alpha"].strip() == "A"
links = mod.extract_local_markdown_links("[local](docs/a.md) [web](https://example.com) [[Note#Anchor|label]]")
assert "docs/a.md" in links and "Note#Anchor" in links and all("example.com" not in item for item in links)
paths = mod.extract_code_spanned_paths("See `tokens/sample-base-token/scope.json` and `not a path`.")
assert "tokens/sample-base-token/scope.json" in paths
assert mod.has_skipped_marker("PT markets: not_in_scope because no PT markets were requested", "PT markets")
PY
```

### 6. Touched-file diff check

```bash
git diff --check -- dev/tools/validate_workflow_run.py
git status --short -- dev/tools/validate_workflow_run.py
```

## Definition of done for M1 implementation

M1 is complete only when:

1. `dev/tools/validate_workflow_run.py` exists and is import-safe.
2. CLI help works.
3. Invalid CLI input exits `2`.
4. Valid common-core runs emit schema-valid JSON.
5. M1 valid common-core reports include P1 `validator.workflow_checks_deferred` and exit `1`, not `0`.
6. Missing manifest and invalid manifest produce P0 JSON reports and exit `2`.
7. Markdown verification output is generated when explicitly requested.
8. Canonical final verification files are never created or overwritten by the harness.
9. Path, manifest, Markdown section, local-link, code-spanned path, and skipped-marker helpers are importable.
10. Only `dev/tools/validate_workflow_run.py` is edited for the implementation slice.
11. The implementer records command, cwd, exit code, and output markers in the kanban handoff.

## Notes for later milestones

- M2 should replace the broad deferred-check finding for asset/oracle runs with manifest schema and path reconciliation checks.
- M3 should add Markdown contract checks for exact fields and final-verification credibility.
- M4 should harden local links and Obsidian-style links.
- M5 should add combined-flow and parent-return validation.
- M6 should introduce the fixture matrix and pytest regression suite.
- M7 should update workflow docs only after validator tests pass.
