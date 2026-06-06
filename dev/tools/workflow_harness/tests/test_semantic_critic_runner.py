"""Regression tests for workflow semantic critic gates."""

from __future__ import annotations

import json
import shutil
import subprocess
import textwrap
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
CRITIC_RUNNER = REPO_ROOT / "dev/tools/semantic_critic_runner.py"
WORKFLOW_RUNNER = REPO_ROOT / "dev/tools/run_workflow.py"
COMPLETE_FIXTURE = "dev/implementation/workflow-harness/fixtures/entrypoint-inputs/sample-assets-complete.json"
TMP_ROOT = REPO_ROOT / "dev/implementation/workflow-harness/tmp/semantic-critic-tests"


def run_json(cmd: list[str]) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    proc = subprocess.run(cmd, cwd=REPO_ROOT, text=True, capture_output=True)
    assert proc.stdout, (proc.returncode, proc.stderr)
    return proc, json.loads(proc.stdout)


def write_stage_bundle(root: Path) -> tuple[Path, Path, Path]:
    root.mkdir(parents=True, exist_ok=True)
    packet = root / "packet.json"
    output = root / "stage-output.md"
    validator = root / "validator-summary.json"
    packet.write_text(json.dumps({
        "task_payload": {
            "workflow_id": "asset-investment-diligence-v1",
            "stage_id": "Analyze",
            "stage_title": "Analyze evidence",
            "scope_id": "sample-token",
            "objective": {"requested_decision": "Decide whether the evidence supports a proposal."},
            "input_paths": ["raw/source-evidence/README.md"],
            "required_outputs": ["stage-output.md"],
            "blocking_unknowns": [],
            "do_not": ["No Preview/Execute recommendation."],
        }
    }))
    output.write_text("# Analyze\n\n## Decision\nTBD\n\n## Evidence\nSource list exists, but no mapped decision.\n")
    validator.write_text(json.dumps({"status": "pass", "finding_counts": {"P0": 0, "P1": 0, "P2": 0, "total": 0}}))
    return packet, output, validator


def setup_function() -> None:
    shutil.rmtree(TMP_ROOT, ignore_errors=True)


def teardown_function() -> None:
    shutil.rmtree(TMP_ROOT, ignore_errors=True)


def test_semantic_runner_without_command_reports_unavailable_instead_of_pass() -> None:
    packet, output, validator = write_stage_bundle(TMP_ROOT / "unavailable")
    proc, report = run_json([
        "python3",
        str(CRITIC_RUNNER),
        "--packet",
        str(packet),
        "--output",
        str(output),
        "--validator-summary",
        str(validator),
    ])

    assert proc.returncode == 1
    assert report["schema_version"] == "workflow-semantic-critic-report-v1"
    assert report["rubric_version"] == "workflow-semantic-critic-rubric-v1"
    assert report["status"] == "semantic_review_unavailable"
    finding = report["findings"][0]
    assert finding["id"] == "semantic.semantic_review_unavailable"
    assert finding["status"] == "review_required"
    assert finding["severity"] == "P1"
    assert finding["violated_requirement"]
    assert finding["evidence"]["path"].endswith("packet.json")
    assert finding["required_remediation"]


def test_semantic_runner_normalizes_command_critic_findings() -> None:
    packet, output, validator = write_stage_bundle(TMP_ROOT / "command")
    stub = TMP_ROOT / "critic_stub.py"
    request_out = TMP_ROOT / "request.json"
    stub.write_text(textwrap.dedent(
        """
        import json
        import sys

        request = json.loads(open(sys.argv[-1]).read())
        assert request["stage_contract"]["stage_id"] == "Analyze"
        assert request["output_artifacts"][0]["content"]
        print(json.dumps({
            "status": "review_required",
            "findings": [{
                "id": "semantic.low_utility_decision",
                "severity": "P1",
                "violated_requirement": "Analyze stage must produce a supported decision, not a placeholder.",
                "evidence": {"path": "stage-output.md", "quote": "## Decision\\nTBD"},
                "required_remediation": "Replace TBD with a source-grounded decision and the evidence path used."
            }]
        }))
        """
    ).strip() + "\n")

    proc, report = run_json([
        "python3",
        str(CRITIC_RUNNER),
        "--packet",
        str(packet),
        "--output",
        str(output),
        "--validator-summary",
        str(validator),
        "--request-out",
        str(request_out),
        "--critic-command",
        f"python3 {stub}",
    ])

    assert proc.returncode == 1
    assert request_out.is_file()
    assert report["status"] == "review_required"
    finding = report["findings"][0]
    assert finding["id"] == "semantic.low_utility_decision"
    assert finding["status"] == "review_required"
    assert finding["severity"] == "P1"
    assert finding["violated_requirement"].startswith("Analyze stage")
    assert finding["evidence"] == {"path": "stage-output.md", "quote": "## Decision\nTBD"}
    assert finding["required_remediation"].startswith("Replace TBD")


def test_workflow_validate_semantic_review_is_opt_in_and_safe_on_unavailable() -> None:
    run_root = "dev/implementation/workflow-harness/tmp/semantic-critic-tests/entrypoint"
    scaffold_proc, scaffold = run_json([
        "python3",
        str(WORKFLOW_RUNNER),
        "analyze-propose",
        "--input",
        COMPLETE_FIXTURE,
        "--run-root",
        run_root,
        "--mode",
        "scaffold",
    ])
    assert scaffold_proc.returncode == 0
    assert scaffold["status"] == "scaffolded"

    default_proc, default = run_json([
        "python3",
        str(WORKFLOW_RUNNER),
        "analyze-propose",
        "--input",
        COMPLETE_FIXTURE,
        "--run-root",
        run_root,
        "--mode",
        "validate",
        "--resume",
    ])
    assert default_proc.returncode == 2
    assert default["validation"]["semantic_review"] == {"enabled": False}
    assert not (REPO_ROOT / run_root / ".workflow/semantic-review").exists()

    semantic_proc, semantic = run_json([
        "python3",
        str(WORKFLOW_RUNNER),
        "analyze-propose",
        "--input",
        COMPLETE_FIXTURE,
        "--run-root",
        run_root,
        "--mode",
        "validate",
        "--resume",
        "--semantic-review",
    ])
    assert semantic_proc.returncode == 2
    semantic_review = semantic["validation"]["semantic_review"]
    assert semantic_review["enabled"] is True
    assert semantic_review["command_configured"] is False
    assert semantic_review["reviews"]
    assert {review["status"] for review in semantic_review["reviews"]} == {"semantic_review_unavailable"}
    finding_ids = {finding["id"] for finding in semantic["findings"]}
    assert "semantic.semantic_review_unavailable" in finding_ids
    assert (REPO_ROOT / semantic_review["reviews"][0]["request_path"]).is_file()
