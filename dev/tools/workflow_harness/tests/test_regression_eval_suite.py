"""Regression eval manifest tests for workflow quality gates."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
SUITE_PATH = REPO_ROOT / "dev/implementation/workflow-harness/fixtures/regression-evals/quality-gate-regression-suite.json"
SEED_PATH = REPO_ROOT / "dev/implementation/workflow-harness/fixtures/regression-evals/latest-quality-gate-seed.json"
VALIDATOR = REPO_ROOT / "dev/tools/validate_workflow_run.py"
CRITIC_RUNNER = REPO_ROOT / "dev/tools/semantic_critic_runner.py"
CRITIC_STUB = REPO_ROOT / "dev/tools/workflow_harness/tests/semantic_fixture_critic_stub.py"
FORBIDDEN_SEED_TERMS = {
    "usdat",
    "susdat",
    "sUSDaT",
    "USDaT",
    "0x00",
    "0x11",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def run_json(cmd: list[str]) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    proc = subprocess.run(cmd, cwd=REPO_ROOT, text=True, capture_output=True)
    assert proc.stdout, (cmd, proc.returncode, proc.stderr)
    return proc, json.loads(proc.stdout)


def test_quality_gate_regression_suite_covers_required_generalized_modes() -> None:
    suite = load_json(SUITE_PATH)
    deterministic_ids = {case["id"] for case in suite["deterministic_cases"]}
    critic_ids = {case["id"] for case in suite["critic_cases"]}

    assert suite["schema_version"] == "workflow-quality-gate-regression-suite-v1"
    assert {
        "fact.well_investigated_positive",
        "fact.investigated_no_result_with_negative_evidence",
        "fact.not_investigated_masquerading_as_unknown",
        "adapter.valid_no_market_no_route_after_search",
        "quantitative.scenario_fallback",
        "quantitative.empty_calculations",
        "parent.request_more_inputs_actionable_acceptance",
    } <= deterministic_ids
    assert {"semantic.low_quality_form_fill"} <= critic_ids
    assert suite["seed_policy"]["latest_run_seed"].endswith("latest-quality-gate-seed.json")
    assert "token-specific" in suite["seed_policy"]["generalization_rule"]


def test_deterministic_regression_cases_replay_expected_validator_findings() -> None:
    suite = load_json(SUITE_PATH)
    cases = [case for case in suite["deterministic_cases"] if case.get("workflow") and case.get("run_root")]
    assert cases

    for case in cases:
        cmd = [
            "python3",
            str(VALIDATOR),
            "--workflow",
            case["workflow"],
            "--run-root",
            case["run_root"],
            "--format",
            "json",
        ]
        if case.get("parent_return"):
            cmd.extend(["--parent-return", case["parent_return"]])
        proc, report = run_json(cmd)
        finding_ids = {finding.get("id") or finding.get("check_id") for finding in report.get("findings", [])}

        assert proc.returncode == case["expected_exit_code"], (case["id"], proc.returncode, report)
        assert report["exit_code"] == case["expected_exit_code"], case["id"]
        if "expected_status" in case:
            assert report["status"] == case["expected_status"], case["id"]
        assert set(case.get("expected_findings", [])) <= finding_ids, (case["id"], finding_ids)
        assert set(case.get("expected_absent_findings", [])).isdisjoint(finding_ids), (case["id"], finding_ids)
        if expected_gate := case.get("expected_proposal_gate"):
            proposal_gate = report.get("proposal_gate") or {}
            assert proposal_gate.get("type") == expected_gate, case["id"]
            if expected_gate == "request_more_inputs":
                blockers = proposal_gate.get("blockers") or []
                assert blockers, case["id"]
                assert all(blocker.get("acceptance_criteria") for blocker in blockers), case["id"]
        if expected_facts := case.get("expected_investigated_no_result_facts"):
            actual = report.get("workflow_decision", {}).get("facts_investigated_no_result", [])
            for fact_id in expected_facts:
                assert any(str(item).startswith(fact_id) for item in actual), (case["id"], fact_id, actual)


def test_semantic_low_quality_form_fill_fixture_replays_critic_finding() -> None:
    case = load_json(SUITE_PATH)["critic_cases"][0]
    with tempfile.TemporaryDirectory(prefix="semantic-low-quality-form-fill-") as temp_dir:
        request_out = Path(temp_dir) / "request.json"
        cmd = [
            "python3",
            str(CRITIC_RUNNER),
            "--packet",
            case["packet"],
            "--output",
            case["output"],
            "--validator-summary",
            case["validator_summary"],
            "--request-out",
            str(request_out),
            "--critic-command",
            f"python3 {CRITIC_STUB} {case['critic_response']}",
        ]
        proc, report = run_json(cmd)
        finding_ids = {finding["id"] for finding in report.get("findings", [])}

        assert proc.returncode == case["expected_exit_code"]
        assert report["status"] == case["expected_status"]
        assert set(case["expected_findings"]) <= finding_ids
        assert request_out.is_file()
        request = load_json(request_out)
        assert request["stage_contract"]["stage_id"] == "Analyze"
        assert request["output_artifacts"][0]["path"].endswith("stage-output.md")


def test_latest_quality_gate_seed_is_replayable_and_generalized() -> None:
    suite = load_json(SUITE_PATH)
    seed = load_json(SEED_PATH)
    serialized_seed = json.dumps(seed, sort_keys=True)

    assert seed["schema_version"] == "workflow-quality-gate-latest-seed-v1"
    assert seed["source_suite"] == SUITE_PATH.relative_to(REPO_ROOT).as_posix()
    assert seed["replay_commands"] == suite["local_commands"]
    assert seed["seed_policy"] == suite["seed_policy"]["generalization_rule"]
    assert seed["generalized_case_ids"] == [
        case["id"] for case in suite["deterministic_cases"] + suite["critic_cases"]
    ]
    assert "sample-token" in serialized_seed
    for forbidden in FORBIDDEN_SEED_TERMS:
        assert forbidden not in serialized_seed, forbidden
