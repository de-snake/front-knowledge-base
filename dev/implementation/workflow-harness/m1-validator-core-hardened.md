# M1 hardened execution brief — validator core CLI and machine-readable report schema

Purpose: final implementation brief for M1 after review. This replaces the weaker acceptance surface in `m1-validator-core-plan.md` by incorporating every blocker from `m1-validator-core-review.md` while preserving the same narrow implementation boundary.

This is a plan only. Do not implement validator code in this task.

## Inputs read

- `CLAUDE.md`
- `dev/implementation/workflow-harness/m1-validator-core-plan.md`
- `dev/implementation/workflow-harness/m1-validator-core-review.md`
- `dev/implementation/workflow-harness/hardened-plan.md`
- `dev/implementation/workflow-harness/plan-review.md`

## Review blockers incorporated

| Review blocker | Hardened change in this brief |
| --- | --- |
| P1-1 stable schema drift | Adds non-negotiable schema compatibility rules and acceptance checks for canonical `id`, `P0` / `P1` / `P2`, `pass` / `review_required` / `fail`, stable top-level keys, and explicit versioning. |
| P1-2 output modes under-tested | Adds acceptance for Markdown stdout, `json,markdown` without destination, `--report-dir`, `rendered_outputs`, `generated_files`, and stdout/file JSON consistency. |
| P1-3 path-safety helpers under-tested | Adds acceptance for missing/file-valued `run_root.exists`, absolute-path rejection, parent-escape rejection, source-relative resolution, and `repo_relative`. |
| P1-4 canonical final-verification protection under-tested | Adds sentinel-file acceptance proving canonical final verification is not overwritten and is not listed as a generated file. |
| P1-5 combined-run deferred behavior unproven | Adds combined-run acceptance proving manifest and child validation stay deferred in M1 and do not become P0 failures or false passes. |

## Scope and edit boundary

M1 may edit exactly one implementation file:

- `dev/tools/validate_workflow_run.py`

M1 must not edit:

- `CLAUDE.md`
- `README.md`
- `user/references/workflows/**`
- `dev/tools/workflow_harness/**`
- historical run artifacts under `dev/implementation/asset-diligence-2026-06-05-sample-base-token-sample-vault-token/**`
- historical run artifacts under `dev/implementation/oracle-analysis-2026-06-05-sample-base-token-sample-vault-token/**`
- fixture directories

The single-file shape is temporary architecture for M1 only. Helper functions should be pure, typed where practical, and importable so later milestones can extract them into a package after a reviewed refactor slice. Do not add a package tree or pytest suite in M1.

No fixture files are required for M1. All M1 acceptance cases use temporary directories created by the acceptance command.

## M1 goal

Implement the reusable validator core in `dev/tools/validate_workflow_run.py` as an import-safe Python script using only the standard library.

M1 establishes:

1. CLI parsing and validation.
2. Stable severity, status, and exit-code policy.
3. Stable JSON report schema.
4. Markdown verification rendering.
5. Safe path normalization helpers.
6. Manifest loading helpers.
7. Markdown section and local-link extraction helpers.
8. Code-spanned path extraction helpers.
9. Explicit skipped-stage marker helpers.
10. A deferred-check finding that prevents false production green reports until later milestones implement workflow-specific checks.

M1 must not implement:

- full asset workflow validation;
- full oracle workflow validation;
- combined Analyze -> Propose state-machine validation;
- parent-return reconciliation;
- fixture matrix or pytest tests;
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
- `--run-root` is resolved from the current working directory.
- Reports should display `run_root` as repository-relative when possible; otherwise use a stable resolved path string.
- `--format` accepts only `json`, `markdown`, or `json,markdown`.
- Invalid argparse input exits `2` through `argparse` and does not need to construct a JSON report.
- Default mode is read-only. The script writes nothing unless `--report-dir` or `--write-verification` is supplied.

## Output contract

- `--format json` prints compact JSON to stdout.
- `--format markdown` prints Markdown to stdout and must not print a JSON-only document.
- `--format json,markdown` prints parseable JSON to stdout.
- If `--format json,markdown` has no destination, the stdout JSON must include `rendered_outputs.markdown` with the rendered Markdown string. Do not mix Markdown prose into stdout outside the JSON object.
- `--report-dir <path>` writes deterministic files:
  - `workflow-harness-report.json`
  - `workflow-harness-verification.md`
- When `--report-dir` is supplied, stdout must remain parseable JSON and `generated_files` must list both written files.
- `--write-verification` writes generated harness Markdown under the run root:
  - asset and oracle runs: `verification/workflow-harness-verification.md`
  - combined runs: `verification/combined-analyze-propose-verification.md`
- The script must never create or overwrite canonical workflow final verification files:
  - `verification/final-investment-analysis-verification.md`
  - `verification/final-oracle-analysis-verification.md`

## Stable schema compatibility rules

M1 is the schema anchor for later milestones. Downstream slices may extend the report, but they must not silently change existing machine semantics.

Non-negotiable rules:

1. `schema_version` remains `workflow-harness-report-v1` unless a future reviewed slice introduces explicit versioning and compatibility tests.
2. Top-level keys remain stable and include at minimum:
   - `schema_version`
   - `generated_at`
   - `workflow`
   - `run_root`
   - `status`
   - `exit_code`
   - `summary`
   - `inputs`
   - `findings`
   - `checks`
   - `generated_files`
   - `rendered_outputs`
3. Workflow IDs remain canonical:
   - `asset-investment-diligence-v1`
   - `oracle-analysis-v1`
   - `combined-analyze-propose-v1`
4. Status values remain:
   - `pass`
   - `review_required`
   - `fail`
5. Severity values remain:
   - `P0`
   - `P1`
   - `P2`
6. Findings use `id` as the canonical machine field. If a compatibility alias such as `check_id` is ever added, it must not replace `id`, and it must equal the canonical `id` for the same finding.
7. Later milestones extend `summary`, `findings`, and `checks` without renaming the existing top-level keys or changing exit-code semantics.
8. JSON should not include raw evidence dumps. Raw command evidence belongs in Markdown verification or implementation handoff prose.

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

M1 must add P1 finding `validator.workflow_checks_deferred` for otherwise valid runs. This prevents the core CLI from returning a false production `pass` before M2-M6 add real workflow checks. Later milestones may remove this finding only after the relevant check catalog is implemented and covered by fixture tests.

`--strict-warnings` does not require a synthetic P2 finding in M1. The flag becomes acceptance-testable in the first later slice that emits P2 findings.

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
- Keep check IDs stable.
- Include all generated report paths in `generated_files`.
- Include rendered Markdown only under `rendered_outputs.markdown` when JSON stdout must carry both JSON and Markdown.
- Do not include raw run artifacts or source dumps in findings.

## Core checks required in M1

M1 implements only common checks that do not depend on final asset, oracle, or combined-flow contracts.

| Check ID | Severity | Required behavior |
| --- | --- | --- |
| `cli.input_valid` | P0 | Pass after argparse accepts workflow, run root, and format. Invalid argparse input exits `2` before report construction. |
| `run_root.exists` | P0 | Fail with JSON report if `--run-root` does not exist or is not a directory. |
| `manifest.file_exists` | P0 | Fail if `<run-root>/run-manifest.json` is missing for asset or oracle runs. For combined runs, skip with message `combined manifest deferred until M5`. |
| `manifest.json_valid` | P0 | Parse `<run-root>/run-manifest.json` when present; fail on invalid JSON. |
| `validator.workflow_checks_deferred` | P1 | Always emit as a finding in M1 after common checks complete. |

Combined-run M1 behavior:

- Do not require `run-manifest.json` for `combined-analyze-propose` in M1.
- Do not attempt child asset or oracle validation in M1.
- Emit skipped checks for deferred combined manifest and child validation.
- Still emit P1 `validator.workflow_checks_deferred`, so combined runs exit `1`, not `0`.

## Required importable helpers

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
  - returns no path and an error message for absolute paths, parent-escaping paths, malformed values, or symlink traversal outside `root`;
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

1. Create `dev/tools/validate_workflow_run.py` with import-safe `main(argv=None)` and `if __name__ == "__main__": raise SystemExit(main())`.
2. Add constants for schema version, workflow ID mapping, valid formats, generated verification filenames, canonical final-verification filenames, and severity order.
3. Add dataclasses and serialization helpers.
4. Add CLI parsing.
5. Add context construction and common M1 checks.
6. Add JSON rendering.
7. Add Markdown rendering.
8. Add `--report-dir` and `--write-verification` output handling with canonical-final-verification protection.
9. Add path, manifest, Markdown section, local-link, code-spanned path, and skipped-marker helpers.
10. Run the exact acceptance command below from `/Users/ilya/Documents/Codex/front-knowledge-base`.

## Exact acceptance command

Run this full command from `/Users/ilya/Documents/Codex/front-knowledge-base` after implementing M1:

```bash
python3 - <<'PY'
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

REPO = Path.cwd()
SCRIPT = REPO / "dev/tools/validate_workflow_run.py"
REQUIRED_TOP_KEYS = {
    "schema_version",
    "generated_at",
    "workflow",
    "run_root",
    "status",
    "exit_code",
    "summary",
    "inputs",
    "findings",
    "checks",
    "generated_files",
    "rendered_outputs",
}
FINDING_KEYS = {
    "id",
    "severity",
    "workflow",
    "path",
    "field",
    "expected",
    "actual",
    "message",
    "fix_hint",
}
CHECK_KEYS = {"id", "severity", "result", "path", "message"}
WORKFLOWS = {
    "asset-investment-diligence-v1",
    "oracle-analysis-v1",
    "combined-analyze-propose-v1",
}
STATUSES = {"pass", "review_required", "fail"}
SEVERITIES = {"P0", "P1", "P2"}
RESULTS = {"pass", "fail", "skipped"}


def run_validator(*args):
    return subprocess.run(
        ["python3", str(SCRIPT), *map(str, args)],
        cwd=REPO,
        text=True,
        capture_output=True,
    )


def parse_json_stdout(proc):
    try:
        return json.loads(proc.stdout)
    except Exception as exc:
        raise AssertionError(
            f"stdout was not parseable JSON; rc={proc.returncode}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        ) from exc


def finding_ids(report):
    return {finding["id"] for finding in report.get("findings", [])}


def check_ids_by_result(report, result):
    return {check["id"] for check in report.get("checks", []) if check.get("result") == result}


def assert_report_schema(report):
    missing = REQUIRED_TOP_KEYS - set(report)
    assert not missing, ("missing top-level keys", missing, report)
    assert report["schema_version"] == "workflow-harness-report-v1", report
    assert report["workflow"] in WORKFLOWS, report
    assert report["status"] in STATUSES, report
    assert isinstance(report["exit_code"], int), report
    assert isinstance(report["summary"], dict), report
    for severity in SEVERITIES:
        assert severity in report["summary"], report["summary"]
    assert isinstance(report["inputs"], dict), report
    assert isinstance(report["findings"], list), report
    assert isinstance(report["checks"], list), report
    assert isinstance(report["generated_files"], list), report
    assert isinstance(report["rendered_outputs"], dict), report
    for finding in report["findings"]:
        missing = FINDING_KEYS - set(finding)
        assert not missing, ("missing finding keys", missing, finding)
        assert finding["id"], finding
        assert finding["severity"] in SEVERITIES, finding
        assert finding["workflow"] in WORKFLOWS, finding
        if "check_id" in finding:
            assert finding["check_id"] == finding["id"], finding
    for check in report["checks"]:
        missing = CHECK_KEYS - set(check)
        assert not missing, ("missing check keys", missing, check)
        assert check["id"], check
        assert check["severity"] in SEVERITIES, check
        assert check["result"] in RESULTS, check


def write_manifest(root, workflow_id):
    (root / "run-manifest.json").write_text(json.dumps({
        "workflow_id": workflow_id,
        "run_id": "m1-hardened-smoke",
        "run_artifact_root": str(root),
        "final_index": "index.md",
        "final_verification": "verification/final-investment-analysis-verification.md"
            if workflow_id == "asset-investment-diligence-v1"
            else "verification/final-oracle-analysis-verification.md",
    }), encoding="utf-8")


assert SCRIPT.exists(), SCRIPT

help_proc = run_validator("--help")
assert help_proc.returncode == 0, help_proc.stdout + help_proc.stderr
assert "--workflow" in help_proc.stdout, help_proc.stdout

bad_cli = run_validator("--workflow", "bad", "--run-root", ".", "--format", "json")
assert bad_cli.returncode == 2, bad_cli.stdout + bad_cli.stderr

with tempfile.TemporaryDirectory() as td:
    tmp = Path(td)

    asset = tmp / "asset-run"
    asset.mkdir()
    write_manifest(asset, "asset-investment-diligence-v1")

    oracle = tmp / "oracle-run"
    oracle.mkdir()
    write_manifest(oracle, "oracle-analysis-v1")

    # JSON schema and deferred-check safety.
    proc = run_validator(
        "--workflow", "asset-investment-diligence",
        "--run-root", asset,
        "--format", "json",
    )
    assert proc.returncode == 1, proc.stdout + proc.stderr
    report = parse_json_stdout(proc)
    assert_report_schema(report)
    assert report["workflow"] == "asset-investment-diligence-v1", report
    assert report["status"] == "review_required", report
    assert report["exit_code"] == 1, report
    assert "validator.workflow_checks_deferred" in finding_ids(report), report
    assert report["summary"]["P1"] >= 1, report

    # Markdown-only stdout is Markdown, not JSON.
    proc = run_validator(
        "--workflow", "asset-investment-diligence",
        "--run-root", asset,
        "--format", "markdown",
    )
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert proc.stdout.lstrip().startswith("# Workflow harness verification"), proc.stdout
    try:
        json.loads(proc.stdout)
    except json.JSONDecodeError:
        pass
    else:
        raise AssertionError("--format markdown printed a JSON-only document")

    # json,markdown without destination keeps stdout parseable JSON and embeds Markdown.
    proc = run_validator(
        "--workflow", "asset-investment-diligence",
        "--run-root", asset,
        "--format", "json,markdown",
    )
    assert proc.returncode == 1, proc.stdout + proc.stderr
    report = parse_json_stdout(proc)
    assert_report_schema(report)
    md = report["rendered_outputs"].get("markdown")
    assert md and "# Workflow harness verification" in md and "## JSON report" in md, report

    # --report-dir writes deterministic files, records generated_files, and keeps stdout JSON.
    report_dir = tmp / "reports"
    proc = run_validator(
        "--workflow", "asset-investment-diligence",
        "--run-root", asset,
        "--format", "json,markdown",
        "--report-dir", report_dir,
    )
    assert proc.returncode == 1, proc.stdout + proc.stderr
    stdout_report = parse_json_stdout(proc)
    assert_report_schema(stdout_report)
    json_path = report_dir / "workflow-harness-report.json"
    md_path = report_dir / "workflow-harness-verification.md"
    assert json_path.exists(), stdout_report
    assert md_path.exists(), stdout_report
    file_report = json.loads(json_path.read_text(encoding="utf-8"))
    assert_report_schema(file_report)
    for key in ["schema_version", "workflow", "status", "exit_code", "summary"]:
        assert file_report[key] == stdout_report[key], (key, file_report, stdout_report)
    assert finding_ids(file_report) == finding_ids(stdout_report), (file_report, stdout_report)
    generated = "\n".join(stdout_report["generated_files"])
    assert "workflow-harness-report.json" in generated, stdout_report
    assert "workflow-harness-verification.md" in generated, stdout_report

    # run_root.exists fails for missing and file-valued roots with P0 JSON reports.
    file_root = tmp / "not-a-directory"
    file_root.write_text("not a directory", encoding="utf-8")
    for bad_root in [tmp / "missing-root", file_root]:
        proc = run_validator(
            "--workflow", "asset-investment-diligence",
            "--run-root", bad_root,
            "--format", "json",
        )
        assert proc.returncode == 2, proc.stdout + proc.stderr
        report = parse_json_stdout(proc)
        assert_report_schema(report)
        assert report["status"] == "fail", report
        assert "run_root.exists" in finding_ids(report), report
        assert report["summary"]["P0"] >= 1, report

    # Missing and invalid manifests return P0 reports for asset/oracle runs.
    missing_manifest = tmp / "missing-manifest"
    missing_manifest.mkdir()
    proc = run_validator(
        "--workflow", "asset-investment-diligence",
        "--run-root", missing_manifest,
        "--format", "json",
    )
    assert proc.returncode == 2, proc.stdout + proc.stderr
    report = parse_json_stdout(proc)
    assert_report_schema(report)
    assert report["status"] == "fail", report
    assert "manifest.file_exists" in finding_ids(report), report

    invalid_manifest = tmp / "invalid-manifest"
    invalid_manifest.mkdir()
    (invalid_manifest / "run-manifest.json").write_text("{not json", encoding="utf-8")
    proc = run_validator(
        "--workflow", "oracle-analysis",
        "--run-root", invalid_manifest,
        "--format", "json",
    )
    assert proc.returncode == 2, proc.stdout + proc.stderr
    report = parse_json_stdout(proc)
    assert_report_schema(report)
    assert report["status"] == "fail", report
    assert "manifest.json_valid" in finding_ids(report), report

    # Canonical final-verification non-overwrite protection with sentinel content.
    verification_dir = oracle / "verification"
    verification_dir.mkdir(exist_ok=True)
    canonical = verification_dir / "final-oracle-analysis-verification.md"
    sentinel = "SENTINEL: canonical final verification must not be overwritten\n"
    canonical.write_text(sentinel, encoding="utf-8")
    proc = run_validator(
        "--workflow", "oracle-analysis",
        "--run-root", oracle,
        "--format", "json",
        "--write-verification",
    )
    assert proc.returncode == 1, proc.stdout + proc.stderr
    report = parse_json_stdout(proc)
    assert_report_schema(report)
    harness_md = verification_dir / "workflow-harness-verification.md"
    assert harness_md.exists(), report
    assert canonical.read_text(encoding="utf-8") == sentinel, canonical.read_text(encoding="utf-8")
    generated = "\n".join(report["generated_files"])
    assert "workflow-harness-verification.md" in generated, report
    assert "final-oracle-analysis-verification.md" not in generated, report

    # Combined M1 behavior: no manifest required, child validation deferred, no false pass.
    combined = tmp / "combined-run"
    combined.mkdir()
    proc = run_validator(
        "--workflow", "combined-analyze-propose",
        "--run-root", combined,
        "--format", "json",
    )
    assert proc.returncode == 1, proc.stdout + proc.stderr
    report = parse_json_stdout(proc)
    assert_report_schema(report)
    assert report["workflow"] == "combined-analyze-propose-v1", report
    assert report["status"] == "review_required", report
    assert "validator.workflow_checks_deferred" in finding_ids(report), report
    assert not any(
        finding["id"] == "manifest.file_exists" and finding["severity"] == "P0"
        for finding in report["findings"]
    ), report
    skipped = check_ids_by_result(report, "skipped")
    assert "manifest.file_exists" in skipped, report
    skipped_messages = "\n".join(check.get("message", "") for check in report.get("checks", []) if check.get("result") == "skipped")
    assert "combined manifest deferred until M5" in skipped_messages, report
    assert any("child" in check_id or "validation" in check_id for check_id in skipped), report

    # Import-level helper acceptance.
    spec = importlib.util.spec_from_file_location("validate_workflow_run", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    helper_root = tmp / "helper-root"
    helper_root.mkdir()
    (helper_root / "tokens" / "t").mkdir(parents=True)
    source_file = helper_root / "tokens" / "t" / "analyst-report.md"
    source_file.write_text("source", encoding="utf-8")

    rel = mod.repo_relative(REPO / "dev", REPO)
    assert rel == "dev", rel

    resolved, err = mod.resolve_under_root("tokens/t/scope.json", root=helper_root)
    assert err is None and resolved == (helper_root / "tokens" / "t" / "scope.json").resolve(), (resolved, err)

    resolved, err = mod.resolve_under_root("../escape.md", root=helper_root)
    assert resolved is None and err, (resolved, err)

    resolved, err = mod.resolve_under_root("/absolute/path.md", root=helper_root)
    assert resolved is None and err, (resolved, err)

    resolved, err = mod.resolve_under_root("verification.md", root=helper_root, source_file=source_file)
    assert err is None and resolved == (helper_root / "tokens" / "t" / "verification.md").resolve(), (resolved, err)

    sections = mod.extract_markdown_sections("# Title\nIntro\n\n## Alpha\nA\n\n## Beta\nB\n")
    assert "alpha" in sections and sections["alpha"].strip() == "A", sections

    links = mod.extract_local_markdown_links("[local](docs/a.md) [web](https://example.com) [frag](#x) [[Note#Anchor|label]]")
    assert "docs/a.md" in links, links
    assert "Note#Anchor" in links, links
    assert all("example.com" not in item for item in links), links
    assert all(item != "#x" for item in links), links

    paths = mod.extract_code_spanned_paths("See `tokens/sample-base-token/scope.json`, `verification/final.md`, and `not a path`.")
    assert "tokens/sample-base-token/scope.json" in paths, paths
    assert "verification/final.md" in paths, paths

    assert mod.has_skipped_marker("PT markets: not_in_scope because no PT markets were requested", "PT markets")

# Touched-file checks.
diff = subprocess.run(
    ["git", "diff", "--check", "--", "dev/tools/validate_workflow_run.py"],
    cwd=REPO,
    text=True,
    capture_output=True,
)
assert diff.returncode == 0, diff.stdout + diff.stderr

status = subprocess.run(
    ["git", "status", "--short", "--", "dev/tools/validate_workflow_run.py"],
    cwd=REPO,
    text=True,
    capture_output=True,
)
assert status.returncode == 0, status.stdout + status.stderr
print(status.stdout, end="")
print("M1_HARDENED_ACCEPTANCE: PASS")
PY
```

## Definition of done for M1 implementation

M1 is complete only when:

1. `dev/tools/validate_workflow_run.py` exists and is import-safe.
2. CLI help works.
3. Invalid CLI input exits `2`.
4. Valid common-core asset and oracle runs emit schema-valid JSON.
5. Top-level JSON includes `rendered_outputs` and `generated_files`.
6. Every finding uses canonical `id`, `P0` / `P1` / `P2`, and required finding keys.
7. M1 valid common-core reports include P1 `validator.workflow_checks_deferred` and exit `1`, not `0`.
8. Missing or file-valued run roots produce P0 `run_root.exists`, status `fail`, and exit `2`.
9. Missing asset/oracle manifest and invalid manifest produce P0 JSON reports and exit `2`.
10. `--format markdown` prints Markdown to stdout.
11. `--format json,markdown` without destination prints parseable JSON and embeds Markdown under `rendered_outputs.markdown`.
12. `--report-dir` writes `workflow-harness-report.json` and `workflow-harness-verification.md`, records both in `generated_files`, and keeps stdout JSON parseable.
13. `--write-verification` writes only the harness verification file and does not create or overwrite canonical final verification files.
14. Canonical final-verification sentinel content survives a `--write-verification` run unchanged.
15. Combined runs in M1 do not require a manifest, do not attempt child validation, include skipped deferred checks, and exit `1` because `validator.workflow_checks_deferred` is present.
16. Path, manifest, Markdown section, local-link, code-spanned path, and skipped-marker helpers are importable.
17. `resolve_under_root(...)` rejects absolute paths and parent escapes, resolves source-relative paths from `source_file.parent`, and does not silently follow symlinks outside the run root.
18. Only `dev/tools/validate_workflow_run.py` is edited for the implementation slice.
19. The implementer records command, cwd, exit code, and output marker `M1_HARDENED_ACCEPTANCE: PASS` in the kanban handoff.

## Notes for later milestones

- M2 should replace the broad deferred-check finding for asset/oracle runs with manifest schema and path reconciliation checks.
- M3 should add Markdown contract checks for exact fields and final-verification credibility.
- M4 should harden local Markdown links, Obsidian-style links, and code-spanned local paths.
- M5 should add combined-flow and parent-return validation.
- M6 should introduce the fixture matrix and pytest regression suite.
- M7 should update workflow docs only after validator tests pass.
