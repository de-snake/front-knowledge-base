"""Regression tests for workflow-harness fixtures.

These tests intentionally validate formal workflow compliance only. They do not
judge token quality, oracle quality, allocation suitability, or execution merit.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
MATRIX_PATH = REPO_ROOT / "dev/implementation/workflow-harness/fixtures/fixture-matrix.json"
VALIDATOR = REPO_ROOT / "dev/tools/validate_workflow_run.py"


def load_validator_module():
    tools_dir = REPO_ROOT / "dev/tools"
    if str(tools_dir) not in sys.path:
        sys.path.insert(0, str(tools_dir))
    spec = importlib.util.spec_from_file_location("validate_workflow_run_under_test", VALIDATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_matrix() -> list[dict]:
    return json.loads(MATRIX_PATH.read_text())


def run_row(row: dict) -> tuple[subprocess.CompletedProcess[str], dict]:
    cmd = [
        "python3",
        str(VALIDATOR),
        "--workflow",
        row["workflow"],
        "--run-root",
        row["run_root"],
        "--format",
        "json",
    ]
    if row.get("parent_return"):
        cmd.extend(["--parent-return", row["parent_return"]])
    proc = subprocess.run(cmd, cwd=REPO_ROOT, text=True, capture_output=True)
    assert proc.stdout, (row["id"], proc.returncode, proc.stderr)
    return proc, json.loads(proc.stdout)


def test_fixture_matrix_has_exact_required_rows() -> None:
    rows = load_matrix()
    required = {
        "good/good-agentic-sample-assets",
        "bad/missing-final-oracle-verification",
        "bad/asset-heading-overclaim",
        "bad/broken-relative-link",
        "bad/oracle-side-specific-omission",
        "bad/ready-for-preview-incorrectly",
        "bad/missing-propose-handoff",
        "bad/missing-parent-return-status",
        "bad/no-parent-return-artifact",
        "bad/oracle-no-result-proof-missing",
        "bad/oracle-not-investigated-as-no-result",
        "oracle-valid-no-market-no-route",
        "asset-good-scenario-fallback",
        "asset-bad-empty-calculations",
    }
    seen = {row["id"] for row in rows}
    assert seen == required


def test_fixture_rows_are_physical_trees() -> None:
    for row in load_matrix():
        root = REPO_ROOT / row["run_root"]
        assert root.exists() and root.is_dir(), row["id"]
        if row["workflow"] == "combined-analyze-propose":
            assert (root / "asset-investment-diligence/verification/workflow-harness-report.json").is_file()
            assert (root / "oracle-analysis/verification/workflow-harness-report.json").is_file()


def test_oracle_adapter_fixtures_cover_result_and_failures() -> None:
    fixtures = REPO_ROOT / "dev/implementation/workflow-harness/fixtures"
    good_memo = (fixtures / "oracle-good-minimal/tokens/sample-token-a-11111111/oracle/protocol-fit-memo.md").read_text()
    valid_no_result_memo = (fixtures / "oracle-valid-no-market-no-route/tokens/sample-token-a-11111111/oracle/protocol-fit-memo.md").read_text()
    no_result_memo = (fixtures / "oracle-bad-no-result-proof-missing/tokens/sample-token-a-11111111/oracle/protocol-fit-memo.md").read_text()
    not_investigated_memo = (fixtures / "oracle-bad-not-investigated-as-no-result/tokens/sample-token-a-11111111/oracle/protocol-fit-memo.md").read_text()
    assert "Market or Credit Manager: found" in good_memo
    assert "Market or Credit Manager: state=investigated_no_result" in valid_no_result_memo
    assert "Route availability: state=investigated_no_result" in valid_no_result_memo
    assert "registry checked" in valid_no_result_memo and "contract query attempted" in valid_no_result_memo
    assert "state=investigated_no_result" in no_result_memo and "proof bundle intentionally omitted" in no_result_memo
    assert "state=investigated_no_result" in not_investigated_memo and "not_investigated" in not_investigated_memo


def test_oracle_fact_state_summary_covers_all_taxonomy_states() -> None:
    validator = load_validator_module()
    adapter = validator.protocol_adapters.get_protocol_adapter("Gearbox")
    states = tuple(validator.protocol_adapters.FACT_STATES)
    assert len(adapter.required_facts) >= len(states)

    expected_by_state = {}
    lines = []
    for fact, state in zip(adapter.required_facts, states):
        expected_name = f"{fact.fact_id} ({fact.label})"
        expected_by_state[state] = expected_name
        value = "fixture source-grounded value; state=found"
        if state != "found":
            value = f"unknown marker recorded; state={state}; decision effect: review_required"
        lines.append(f"- {fact.label}: {value}.")

    observations = validator._oracle_fact_state_observations(
        "\n".join(lines),
        adapter,
        Path("protocol-fit-memo.md"),
    )
    summary = validator._oracle_state_summary(observations)

    assert set(states) <= set(summary["by_state"])
    for state, expected_name in expected_by_state.items():
        assert expected_name in summary["by_state"][state]
    assert summary["facts_investigated_no_result"] == [expected_by_state["investigated_no_result"]]
    assert expected_by_state["input_missing"] in summary["facts_needing_investigation"]
    assert expected_by_state["not_investigated"] in summary["facts_needing_investigation"]
    assert summary["facts_with_unproven_unknowns"] == []


def test_oracle_unproven_unknowns_are_named_as_needing_investigation() -> None:
    validator = load_validator_module()
    adapter = validator.protocol_adapters.get_protocol_adapter("Gearbox")
    fact = adapter.required_facts[0]
    fact_name = f"{fact.fact_id} ({fact.label})"
    observations = validator._oracle_fact_state_observations(
        f"- {fact.label}: unknown placeholder recorded without a value state.",
        adapter,
        Path("protocol-fit-memo.md"),
    )
    summary = validator._oracle_state_summary(observations)

    assert fact_name in summary["facts_with_unproven_unknowns"]
    assert fact_name in summary["facts_needing_investigation"]
    assert summary["facts_investigated_no_result"] == []


def test_oracle_run_report_names_investigation_needs_separately_from_no_result() -> None:
    source = REPO_ROOT / "dev/implementation/workflow-harness/fixtures/oracle-good-minimal"
    with tempfile.TemporaryDirectory(prefix="oracle-unproven-unknown-report-") as temp_dir:
        run_root = Path(temp_dir) / "oracle-unproven-unknown-report"
        shutil.copytree(source, run_root)
        memo_path = run_root / "tokens/sample-token-a-11111111/oracle/protocol-fit-memo.md"
        memo = memo_path.read_text()
        memo = memo.replace(
            "- Market or Credit Manager: found — fixture Gearbox Credit Manager context `sample-credit-manager` is named and used for parameter lookup; no live token address is inferred.",
            "- Market or Credit Manager: unknown placeholder recorded without a value state.",
        )
        memo_path.write_text(memo)
        proc = subprocess.run(
            ["python3", str(VALIDATOR), "--workflow", "oracle-analysis", "--run-root", str(run_root), "--format", "json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        report = json.loads(proc.stdout)
        decision = report["workflow_decision"]

    assert proc.returncode == 1
    assert report["status"] == "review_required"
    assert report["formal_validation_status"] == "review_required"
    assert report["workflow_decision_status"] == "review_required"
    assert report["proposal_gate"]["type"] == "request_more_inputs"
    assert decision["status"] == "review_required"
    assert decision["facts_needing_investigation"]
    assert decision["facts_investigated_no_result"] == []


def test_combined_run_preserves_formal_pass_separate_from_workflow_review() -> None:
    proc = subprocess.run(
        [
            "python3",
            str(VALIDATOR),
            "--workflow",
            "combined-analyze-propose",
            "--run-root",
            "dev/implementation/workflow-harness/fixtures/good/good-agentic-sample-assets",
            "--parent-return",
            "agentic-flow/analyze-and-propose.md",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )
    report = json.loads(proc.stdout)

    assert proc.returncode == 0
    assert report["formal_validation"]["status"] == "pass"
    assert report["formal_validation_status"] == "pass"
    assert report["semantic_review_status"] == "not_run"
    assert report["workflow_decision"]["status"] == "review_required"
    assert report["workflow_decision_status"] == "review_required"
    assert report["proposal_gate"]["type"] == "request_more_inputs"
    assert report["status_block"]["formal_validation_status"] == "pass"
    assert report["status_block"]["semantic_review_status"] == "not_run"
    assert report["status_block"]["workflow_decision_status"] == "review_required"
    assert report["status_block"]["proposal_gate"]["type"] == "request_more_inputs"
    assert report["status"] == "pass"


def test_oracle_not_investigated_requires_status_blocker_propagation() -> None:
    source = REPO_ROOT / "dev/implementation/workflow-harness/fixtures/oracle-good-minimal"
    with tempfile.TemporaryDirectory(prefix="oracle-not-investigated-no-blocker-") as temp_dir:
        run_root = Path(temp_dir) / "oracle-not-investigated-no-blocker"
        shutil.copytree(source, run_root)
        memo_path = run_root / "tokens/sample-token-a-11111111/oracle/protocol-fit-memo.md"
        memo = memo_path.read_text()
        memo = memo.replace(
            "- Market or Credit Manager: found — fixture Gearbox Credit Manager context `sample-credit-manager` is named and used for parameter lookup; no live token address is inferred.",
            "- Market or Credit Manager: state=not_investigated; not checked; decision effect is not propagated.",
        )
        memo_path.write_text(memo)
        proc = subprocess.run(
            ["python3", str(VALIDATOR), "--workflow", "oracle-analysis", "--run-root", str(run_root), "--format", "json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        report = json.loads(proc.stdout)
        finding_ids = {finding["id"] for finding in report.get("findings", [])}

        assert proc.returncode == 1
        assert "oracle.protocol_adapter_not_investigated_requires_blocker" in finding_ids


def test_oracle_final_verification_rejects_stale_pending_validation_text() -> None:
    source = REPO_ROOT / "dev/implementation/workflow-harness/fixtures/oracle-good-minimal"
    with tempfile.TemporaryDirectory(prefix="oracle-stale-pending-validation-") as temp_dir:
        run_root = Path(temp_dir) / "oracle-stale-pending-validation"
        shutil.copytree(source, run_root)
        final_path = run_root / "verification/final-oracle-analysis-verification.md"
        final_path.write_text("# Final oracle verification\n\nStatus: pass. Validator checks are pending and not yet run.\n")
        proc = subprocess.run(
            ["python3", str(VALIDATOR), "--workflow", "oracle-analysis", "--run-root", str(run_root), "--format", "json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        report = json.loads(proc.stdout)
        finding_ids = {finding["id"] for finding in report.get("findings", [])}

        assert proc.returncode == 1
        assert "oracle.final_verification.not_pending" in finding_ids


def test_all_fixture_rows_validate_as_expected() -> None:
    for row in load_matrix():
        proc, report = run_row(row)
        assert proc.returncode == row["expected_exit_code"], (row["id"], proc.returncode, proc.stdout, proc.stderr)
        assert report["status"] == row["expected_status"], row["id"]
        found = {finding.get("id") or finding.get("check_id") for finding in report.get("findings", [])}
        assert set(row.get("expected_findings", [])) <= found, (row["id"], row.get("expected_findings", []), found)


def test_asset_validator_rejects_s6_skipped_calculations_without_allowed_scenario_bands() -> None:
    source = REPO_ROOT / "dev/implementation/workflow-harness/fixtures/asset-bad-missing-s6-calculation-fields"
    with tempfile.TemporaryDirectory(prefix="asset-s6-skip-without-scenario-") as temp_dir:
        run_root = Path(temp_dir) / "asset-s6-skip-without-scenario"
        shutil.copytree(source, run_root)
        table = """# Quantitative underwriting methodology

| Field | Value state | Reason |
| --- | --- | --- |
| Gross ROI | skipped_due_to_missing_input | due to missing position size, target leverage, hold horizon, and user risk policy |
| Simple annualized return | skipped_due_to_missing_input | due to missing hold horizon |
| Compound annualized return | skipped_due_to_missing_input | due to missing hold horizon |
| Points EV | skipped_due_to_missing_input | due to missing position size |
| Points ROI | skipped_due_to_missing_input | due to missing position size and target leverage |
| Points annualized return | skipped_due_to_missing_input | due to missing hold horizon |
| Expected loss | skipped_due_to_missing_input | due to missing user risk policy and HF floor |
| Exit cost | skipped_due_to_missing_input | due to missing position size |
| Risk-adjusted ROI | skipped_due_to_missing_input | due to missing user risk policy |
| Risk-adjusted annualized return | skipped_due_to_missing_input | due to missing hold horizon and risk policy |
| Break-even points ROI | skipped_due_to_missing_input | due to missing target leverage |
| Break-even terminal drawdown | skipped_due_to_missing_input | due to missing user risk policy |
| Price-stability certainty score | skipped_due_to_missing_input | due to missing risk policy |
"""
        for rel in (
            "investment-analysis/quantitative-underwriting-methodology.md",
            "investment-analysis/investment-analyst-report-points-pt-risk-return.md",
            "investment-analysis/index.md",
        ):
            (run_root / rel).write_text(table)

        proc = subprocess.run(
            ["python3", str(VALIDATOR), "--workflow", "asset-investment-diligence", "--run-root", str(run_root), "--format", "json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        assert proc.stdout, proc.stderr
        report = json.loads(proc.stdout)
        found = {finding.get("id") or finding.get("check_id") for finding in report.get("findings", [])}
        assert proc.returncode == 2
        assert report["formal_validation_status"] == "fail"
        assert report["workflow_decision_status"] == "fail"
        assert report["proposal_gate"]["type"] == "request_more_inputs"
        assert "asset.s6.skipped_calculation_requires_analyze_only_scenario_band" in found


def test_good_combined_fixture_requires_explicit_parent_return() -> None:
    row = next(row for row in load_matrix() if row["id"] == "good/good-agentic-sample-assets")
    explicit_proc, explicit_report = run_row(row)
    assert explicit_proc.returncode == 0
    assert explicit_report["status"] == "pass"

    implicit = dict(row)
    implicit.pop("parent_return", None)
    implicit_proc, implicit_report = run_row(implicit)
    assert implicit_proc.returncode == 0
    assert implicit_report["status"] == "pass"


def test_malformed_and_missing_parent_returns_are_distinct() -> None:
    rows = {row["id"]: row for row in load_matrix()}
    malformed_proc, malformed_report = run_row(rows["bad/missing-parent-return-status"])
    missing_proc, missing_report = run_row(rows["bad/no-parent-return-artifact"])

    malformed_ids = {finding.get("id") for finding in malformed_report.get("findings", [])}
    missing_ids = {finding.get("id") for finding in missing_report.get("findings", [])}

    assert malformed_proc.returncode == 1
    assert "flow.stage_status_table_present" in malformed_ids
    assert missing_proc.returncode == 2
    assert "flow.propose_handoff_exists" in missing_ids
