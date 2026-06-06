"""Regression tests for the workflow entrypoint runner."""

from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
TOOLS_DIR = REPO_ROOT / "dev/tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))
import workflow_entrypoint as entrypoint  # noqa: E402 - tools dir must be importable first.

RUNNER = REPO_ROOT / "dev/tools/run_workflow.py"
INPUT_DIR = REPO_ROOT / "dev/implementation/workflow-harness/fixtures/entrypoint-inputs"
FIXTURE = "dev/implementation/workflow-harness/fixtures/entrypoint-inputs/sample-assets-minimal.json"
COMPLETE_FIXTURE = "dev/implementation/workflow-harness/fixtures/entrypoint-inputs/sample-assets-complete.json"
TMP_ROOT = REPO_ROOT / "dev/implementation/workflow-harness/tmp/entrypoint-tests"
WORKFLOW_DOCS = ["runbook.md", "workflow.json", "stage-contracts.md", "subagent-prompts.md", "output-structure.md"]
SUPPORTED_AGENTS = ("generic", "codex", "claude-code", "hermes")
EXPECTED_PACKET_TASK_IDS = [
    "asset-S1_general_asset_mining-eth-mainnet-sample-base-token",
    "asset-S2_asset_risk_analyst_report-eth-mainnet-sample-base-token",
    "asset-S1_general_asset_mining-eth-mainnet-sample-vault-token",
    "asset-S2_asset_risk_analyst_report-eth-mainnet-sample-vault-token",
    "asset-S6_quantitative_underwriting-run",
    "asset-S7_final_verification-run",
    "oracle-S0_scope_and_acceptance-eth-mainnet-sample-base-token-gearbox-oracle",
    "oracle-S1_feed_inventory_and_graph-eth-mainnet-sample-base-token-gearbox-oracle",
    "oracle-S2_node_classification-eth-mainnet-sample-base-token-gearbox-oracle",
    "oracle-S3_source_primitive_audit-eth-mainnet-sample-base-token-gearbox-oracle",
    "oracle-S4_stress_tradeoff_analysis-eth-mainnet-sample-base-token-gearbox-oracle",
    "oracle-S5_protocol_fit_and_parameter_context-eth-mainnet-sample-base-token-gearbox-oracle",
    "oracle-S6_final_verification-eth-mainnet-sample-base-token-gearbox-oracle",
    "oracle-S0_scope_and_acceptance-eth-mainnet-sample-vault-token-gearbox-oracle",
    "oracle-S1_feed_inventory_and_graph-eth-mainnet-sample-vault-token-gearbox-oracle",
    "oracle-S2_node_classification-eth-mainnet-sample-vault-token-gearbox-oracle",
    "oracle-S3_source_primitive_audit-eth-mainnet-sample-vault-token-gearbox-oracle",
    "oracle-S4_stress_tradeoff_analysis-eth-mainnet-sample-vault-token-gearbox-oracle",
    "oracle-S5_protocol_fit_and_parameter_context-eth-mainnet-sample-vault-token-gearbox-oracle",
    "oracle-S6_final_verification-eth-mainnet-sample-vault-token-gearbox-oracle",
]
EXPECTED_REGISTRY_PACKETS = [
    {
        "task_id": task_id,
        "json": f".workflow/packets/{task_id.split('-', 1)[0]}/{task_id}.json",
        "markdown": f".workflow/packets/{task_id.split('-', 1)[0]}/{task_id}.md",
    }
    for task_id in EXPECTED_PACKET_TASK_IDS
]


def run_entrypoint(*args: str) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    proc = subprocess.run(["python3", str(RUNNER), *args], cwd=REPO_ROOT, text=True, capture_output=True)
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"stdout was not JSON (rc={proc.returncode}): {proc.stdout[:500]}\nstderr={proc.stderr}") from exc
    return proc, data


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def read_s6_packet(root: Path) -> dict[str, Any]:
    matches = sorted((root / ".workflow/packets/asset").glob("asset-S6_quantitative_underwriting-*.json"))
    if not matches:
        raise AssertionError(f"missing S6 packet under {root}")
    return read_json(matches[0])


def strip_run_root(value: Any, roots: list[str]) -> Any:
    if isinstance(value, dict):
        cleaned = {}
        for key, nested in value.items():
            if key == "created_at":
                continue
            cleaned[key] = strip_run_root(nested, roots)
        return cleaned
    if isinstance(value, list):
        return [strip_run_root(item, roots) for item in value]
    if isinstance(value, str):
        result = value
        for root in roots:
            result = result.replace(root, "<RUN_ROOT>")
        return result
    return value


def token_proxy(text: str) -> int:
    return len(text.split())


def without_launcher_line(markdown: str) -> str:
    return "\n".join(line for line in markdown.splitlines() if not line.startswith("Launcher: "))


def path_scopes_conflict(left: str, right: str) -> bool:
    return left == right or left.startswith(f"{right}/") or right.startswith(f"{left}/")


def assert_packets_have_disjoint_output_scopes(testcase: unittest.TestCase, packets: list[dict[str, Any]]) -> None:
    seen: list[tuple[str, str]] = []
    for packet in packets:
        task_id = packet["task_id"]
        for root in packet.get("artifact_write_scope", {}).get("write_roots", []):
            for seen_task_id, seen_root in seen:
                testcase.assertFalse(
                    path_scopes_conflict(root, seen_root),
                    f"{task_id} writes {root}, conflicting with {seen_task_id} writing {seen_root}",
                )
            seen.append((task_id, root))


def assert_ready_packets_have_satisfied_dependencies(
    testcase: unittest.TestCase,
    graph: dict[str, Any],
    next_action: dict[str, Any],
) -> None:
    graph_by_task = {node["task_id"]: node for node in graph["tasks"]}
    ready_ids = graph["ready_packets"]
    testcase.assertEqual([packet["task_id"] for packet in next_action["ready_packets"]], ready_ids)
    for task_id in ready_ids:
        node = graph_by_task[task_id]
        testcase.assertEqual(node["scaffold_state"], "ready")
        testcase.assertEqual(node["depends_on_task_ids"], [], task_id)
        testcase.assertEqual(node["missing_artifacts"], [], task_id)
        testcase.assertEqual(node["blocking_unknowns"], [], task_id)
        testcase.assertEqual(node["blocked_reasons"], [], task_id)
    for packet in next_action["ready_packets"]:
        testcase.assertEqual(packet["depends_on_task_ids"], [], packet["task_id"])


class WorkflowEntrypointTests(unittest.TestCase):
    maxDiff = 20000

    def setUp(self) -> None:
        TMP_ROOT.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        if TMP_ROOT.exists():
            shutil.rmtree(TMP_ROOT)

    def test_cli_help_returns_zero(self) -> None:
        for args in [[], ["analyze-propose", "--help"]]:
            proc = subprocess.run(["python3", str(RUNNER), *args], cwd=REPO_ROOT, text=True, capture_output=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("analyze-propose", proc.stdout)

    def test_minimal_input_scaffolds_parent_children_and_packets(self) -> None:
        run_root = "dev/implementation/workflow-harness/tmp/entrypoint-tests/minimal"
        proc, data = run_entrypoint(
            "analyze-propose",
            "--input",
            FIXTURE,
            "--run-root",
            run_root,
            "--mode",
            "scaffold",
            "--agent",
            "generic",
            "--format",
            "json",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(data["status"], "scaffolded")
        root = REPO_ROOT / run_root
        expected = [
            ".workflow/input.normalized.json",
            ".workflow/plan.json",
            ".workflow/execution-graph.json",
            ".workflow/tasks.json",
            ".workflow/registry.json",
            ".workflow/agent-handoff.md",
            ".workflow/next-action.json",
            ".workflow/next-action.md",
            "asset-investment-diligence/run-manifest.json",
            "oracle-analysis/run-manifest.json",
            "agentic-flow/analyze-and-propose.md",
        ]
        for rel in expected:
            self.assertTrue((root / rel).exists(), rel)
        parent_return = (root / "agentic-flow/analyze-and-propose.md").read_text()
        self.assertIn("formal_validation_status", parent_return)
        self.assertIn("workflow_decision_status", parent_return)
        self.assertIn("request_more_inputs", parent_return)
        next_action = read_json(root / ".workflow/next-action.json")
        self.assertEqual(next_action["status"], "blocked")
        self.assertIn("first_packet", next_action)
        self.assertIsInstance(next_action["first_packet"], dict)
        self.assertEqual(next_action["first_packet"]["task_id"], EXPECTED_PACKET_TASK_IDS[0])
        self.assertEqual(next_action["first_packet"]["json"], EXPECTED_REGISTRY_PACKETS[0]["json"])
        self.assertEqual(next_action["first_packet"]["markdown"], EXPECTED_REGISTRY_PACKETS[0]["markdown"])
        packet_path = root / next_action["first_packet"]["json"]
        packet = read_json(packet_path)
        self.assertEqual(packet["packet_schema"], "workflow-stage-packet-v1")
        self.assertEqual(packet["schema_version"], "workflow-stage-packet-v1")
        self.assertEqual(packet["task_payload"]["workflow_id"], "asset-investment-diligence-v1")
        metadata = packet["packet_metadata"]
        self.assertEqual(packet["task_payload"]["packet_metadata"], metadata)
        self.assertEqual(next_action["first_packet"]["delegate_to_subagent"], metadata["delegate_to_subagent"])
        self.assertTrue(metadata["delegate_to_subagent"])
        self.assertEqual(metadata["subagent_prompt_reference"]["path"], "user/references/workflows/asset-investment-diligence/subagent-prompts.md")
        self.assertEqual(metadata["subagent_prompt_reference"]["section"], "S1 prompt — General asset mining")
        self.assertEqual(metadata["recommended_max_concurrent"], 3)
        self.assertTrue(metadata["return_contract"]["parent_verification_required"])
        self.assertTrue(metadata["return_contract"]["worker_self_report_is_advisory"])
        self.assertIn("asset-investment-diligence/tokens/", metadata["artifact_write_scope"]["write_roots"][0])
        packet_markdown = (root / next_action["first_packet"]["markdown"]).read_text()
        self.assertIn("## Delegation metadata", packet_markdown)
        self.assertIn("subagent_prompt_reference", packet_markdown)
        self.assertIn("parent validates artifacts", packet_markdown)
        self.assertNotIn("Collect token-level evidence for `[symbol]`", packet_markdown)
        self.assertNotIn("execution readiness: pass", packet_markdown.lower())

    def test_scaffold_writes_metadata_only_execution_graph(self) -> None:
        run_root = "dev/implementation/workflow-harness/tmp/entrypoint-tests/execution-graph"
        proc, _ = run_entrypoint(
            "analyze-propose",
            "--input",
            FIXTURE,
            "--run-root",
            run_root,
            "--mode",
            "scaffold",
            "--agent",
            "generic",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        root = REPO_ROOT / run_root
        plan = read_json(root / ".workflow/plan.json")
        graph = read_json(root / ".workflow/execution-graph.json")
        tasks = read_json(root / ".workflow/tasks.json")
        registry = read_json(root / ".workflow/registry.json")
        next_action = read_json(root / ".workflow/next-action.json")

        self.assertEqual(plan["execution_graph"], graph)
        self.assertEqual([task["task_id"] for task in tasks], EXPECTED_PACKET_TASK_IDS)
        self.assertEqual([packet["task_id"] for packet in registry["packets"]], EXPECTED_PACKET_TASK_IDS)
        self.assertEqual([task["task_id"] for task in graph["tasks"]], EXPECTED_PACKET_TASK_IDS)
        self.assertEqual({"ready", "blocked"}, {task["scaffold_state"] for task in graph["tasks"]})
        self.assertTrue(graph["dependency_edges"])
        self.assertFalse(graph["compatibility"]["validators_require_execution_graph"])
        self.assertIn("subagent_launch", graph["non_goals"])

        graph_by_task = {task["task_id"]: task for task in graph["tasks"]}
        first = graph_by_task[EXPECTED_PACKET_TASK_IDS[0]]
        second_token_s1 = graph_by_task[EXPECTED_PACKET_TASK_IDS[2]]
        first_s2 = graph_by_task[EXPECTED_PACKET_TASK_IDS[1]]
        underwriting = graph_by_task["asset-S6_quantitative_underwriting-run"]
        oracle_feed_parallel = graph_by_task["oracle-S1_feed_inventory_and_graph-eth-mainnet-sample-base-token-gearbox-oracle"]

        self.assertEqual(first["depends_on_task_ids"], [])
        self.assertIn("blocking_unknowns", first["blocked_reasons"])
        self.assertEqual(first_s2["depends_on_task_ids"], [EXPECTED_PACKET_TASK_IDS[0]])
        self.assertEqual(second_token_s1["scaffold_state"], "ready")
        self.assertTrue(second_token_s1["delegate_to_subagent"])
        self.assertEqual(second_token_s1["subagent_prompt_reference"]["path"], "user/references/workflows/asset-investment-diligence/subagent-prompts.md")
        self.assertEqual(second_token_s1["subagent_prompt_reference"]["section"], "S1 prompt — General asset mining")
        self.assertEqual(second_token_s1["return_contract"]["contract_id"], "stage-worker-compressed-handoff-v1")
        self.assertTrue(second_token_s1["return_contract"]["parent_verification_required"])
        self.assertEqual(next_action["ready_packets"][0]["task_id"], second_token_s1["task_id"])
        self.assertEqual(next_action["ready_packets"][0]["subagent_prompt_reference"], second_token_s1["subagent_prompt_reference"])
        self.assertEqual(next_action["ready_packets"][0]["return_contract"], second_token_s1["return_contract"])
        self.assertEqual(next_action["blocked_packets"][0]["task_id"], first["task_id"])
        self.assertEqual(next_action["first_packet"]["task_id"], EXPECTED_PACKET_TASK_IDS[0])
        ready_task_ids = [packet["task_id"] for packet in next_action["ready_packets"]]
        self.assertIn(second_token_s1["task_id"], ready_task_ids)
        self.assertNotIn(underwriting["task_id"], ready_task_ids)
        self.assertNotIn("asset-S7_final_verification-run", ready_task_ids)
        self.assertEqual([wave["packet_task_ids"] for wave in next_action["parallel_waves"]], [ready_task_ids])
        ready_wave = next_action["parallel_waves"][0]
        self.assertTrue(ready_wave["advisory_only"])
        self.assertEqual(ready_wave["harness_orchestration"], "none")
        self.assertIn("does not schedule", ready_wave["safety_rationale"])
        assert_packets_have_disjoint_output_scopes(self, ready_wave["packets"])
        next_action_markdown = (root / ".workflow/next-action.md").read_text()
        self.assertIn("## Ready packets", next_action_markdown)
        self.assertIn("## Parallel waves", next_action_markdown)
        self.assertIn("Advisory graph metadata only", next_action_markdown)
        self.assertIn("performs no scheduling", next_action_markdown)
        self.assertIn("Do not unlock downstream stages", next_action_markdown)
        self.assertEqual(oracle_feed_parallel["parallel_group_id"], "oracle.S1_feed_inventory_and_graph.oracle_scope")
        self.assertEqual(oracle_feed_parallel["source_parallel_group_id"], "G1_feed_trees")
        self.assertTrue(oracle_feed_parallel["delegate_to_subagent"])
        self.assertEqual(oracle_feed_parallel["subagent_prompt_reference"]["section"], "S1 — Feed inventory and graph worker")
        self.assertIn("waiting_on_dependencies", oracle_feed_parallel["blocked_reasons"])
        self.assertIn("blocking_unknowns", oracle_feed_parallel["blocked_reasons"])
        self.assertNotIn("serial_fallback", oracle_feed_parallel["blocked_reasons"])
        self.assertEqual({item["stage_id"] for item in underwriting["skipped_stage_dependencies"]}, {"S3_pt_market_economics", "S5_x_social_synthesis"})

        for group in graph["parallel_groups"]:
            self.assertTrue(group["safety_rationale"])
            self.assertEqual(group["artifact_write_scope"]["mode"], "exclusive_prefixes")
            self.assertTrue(group["artifact_write_scope"]["write_roots"])
            self.assertTrue(group["artifact_write_scope"]["required_outputs"])

    def test_graph_parallelization_fixture_matrix_covers_safe_and_unsafe_cases(self) -> None:
        run_root = "dev/implementation/workflow-harness/tmp/entrypoint-tests/graph-fixture-matrix"
        proc, _ = run_entrypoint("analyze-propose", "--input", COMPLETE_FIXTURE, "--run-root", run_root, "--mode", "scaffold", "--agent", "generic")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        root = REPO_ROOT / run_root
        plan = read_json(root / ".workflow/plan.json")
        graph = read_json(root / ".workflow/execution-graph.json")
        next_action = read_json(root / ".workflow/next-action.json")
        graph_by_task = {task["task_id"]: task for task in graph["tasks"]}
        groups = {group["parallel_group_id"]: group for group in graph["parallel_groups"]}

        ready_ids = [packet["task_id"] for packet in next_action["ready_packets"]]
        expected_ready = [EXPECTED_PACKET_TASK_IDS[0], EXPECTED_PACKET_TASK_IDS[2]]
        self.assertEqual(graph["ready_packets"], expected_ready)
        self.assertEqual(ready_ids, expected_ready)
        assert_ready_packets_have_satisfied_dependencies(self, graph, next_action)
        self.assertEqual([wave["packet_task_ids"] for wave in next_action["parallel_waves"]], [expected_ready])
        assert_packets_have_disjoint_output_scopes(self, next_action["parallel_waves"][0]["packets"])

        asset_s1_group = groups["asset.S1_general_asset_mining.token"]
        asset_s2_group = groups["asset.S2_asset_risk_analyst_report.token"]
        self.assertEqual(asset_s1_group["source_parallel_group_id"], "G1_token_mining")
        self.assertEqual(asset_s1_group["parallel_unit"], "token")
        self.assertEqual(asset_s1_group["task_ids"], [EXPECTED_PACKET_TASK_IDS[0], EXPECTED_PACKET_TASK_IDS[2]])
        self.assertEqual(asset_s2_group["source_parallel_group_id"], "G2_token_reports")
        self.assertEqual(asset_s2_group["parallel_unit"], "token")
        self.assertEqual(asset_s2_group["task_ids"], [EXPECTED_PACKET_TASK_IDS[1], EXPECTED_PACKET_TASK_IDS[3]])
        assert_packets_have_disjoint_output_scopes(self, [graph_by_task[task_id] for task_id in asset_s1_group["task_ids"]])
        assert_packets_have_disjoint_output_scopes(self, [graph_by_task[task_id] for task_id in asset_s2_group["task_ids"]])

        skipped = {(item["workflow"], item["stage_id"]): item["reason"] for item in plan["skipped_stages"]}
        self.assertIn(("asset", "S3_pt_market_economics"), skipped)
        self.assertIn(("asset", "S5_x_social_synthesis"), skipped)
        for skipped_stage_id in ("S3_pt_market_economics", "S5_x_social_synthesis"):
            self.assertNotIn(skipped_stage_id, "\n".join(graph["ready_packets"]))
            self.assertFalse(any(task["stage_id"] == skipped_stage_id for task in graph["tasks"]))

        for stage_id, task_id in (
            ("S6_quantitative_underwriting", "asset-S6_quantitative_underwriting-run"),
            ("S7_final_verification", "asset-S7_final_verification-run"),
        ):
            node = graph_by_task[task_id]
            self.assertEqual(node["stage_id"], stage_id)
            self.assertEqual(node["scope_type"], "run")
            self.assertIsNone(node["parallel_group_id"])
            self.assertFalse(node["delegate_to_subagent"])
            self.assertEqual(node["recommended_max_concurrent"], 1)
            self.assertIn("serial_fallback", node["blocked_reasons"])
            self.assertNotIn(task_id, ready_ids)
        self.assertEqual(graph_by_task["asset-S6_quantitative_underwriting-run"]["serial_section_id"], "asset.underwriting")
        self.assertEqual(graph_by_task["asset-S7_final_verification-run"]["serial_section_id"], "asset.verification")

        for task_id in (EXPECTED_PACKET_TASK_IDS[1], EXPECTED_PACKET_TASK_IDS[3]):
            node = graph_by_task[task_id]
            self.assertEqual(node["depends_on_task_ids"], [task_id.replace("S2_asset_risk_analyst_report", "S1_general_asset_mining")])
            self.assertIn("waiting_on_dependencies", node["blocked_reasons"])
            self.assertTrue(node["missing_artifacts"])
            self.assertNotIn(task_id, ready_ids)

        oracle_group = groups["oracle.S1_feed_inventory_and_graph.oracle_scope"]
        self.assertEqual(oracle_group["source_parallel_group_id"], "G1_feed_trees")
        self.assertEqual(oracle_group["parallel_unit"], "oracle_scope")
        self.assertEqual(oracle_group["task_ids"], [EXPECTED_PACKET_TASK_IDS[7], EXPECTED_PACKET_TASK_IDS[14]])
        assert_packets_have_disjoint_output_scopes(self, [graph_by_task[task_id] for task_id in oracle_group["task_ids"]])
        for task_id in oracle_group["task_ids"]:
            node = graph_by_task[task_id]
            self.assertTrue(node["delegate_to_subagent"])
            self.assertEqual(node["subagent_prompt_reference"]["section"], "S1 — Feed inventory and graph worker")
            self.assertIn("waiting_on_dependencies", node["blocked_reasons"])
            self.assertNotIn("serial_fallback", node["blocked_reasons"])
            self.assertNotIn(task_id, ready_ids)

        for task_id in (EXPECTED_PACKET_TASK_IDS[9], EXPECTED_PACKET_TASK_IDS[16]):
            node = graph_by_task[task_id]
            self.assertEqual(node["stage_id"], "S3_source_primitive_audit")
            self.assertIsNone(node["parallel_group_id"])
            self.assertFalse(node["delegate_to_subagent"])
            self.assertIn("waiting_on_dependencies", node["blocked_reasons"])
            self.assertIn("serial_fallback", node["blocked_reasons"])
            self.assertTrue(node["missing_artifacts"])
            self.assertNotIn(task_id, ready_ids)

    def test_artificial_write_conflict_blocks_parallel_ready_packet(self) -> None:
        run_root = "dev/implementation/workflow-harness/tmp/entrypoint-tests/write-conflict"
        proc, _ = run_entrypoint("analyze-propose", "--input", COMPLETE_FIXTURE, "--run-root", run_root, "--mode", "scaffold", "--agent", "generic")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        plan = read_json(REPO_ROOT / run_root / ".workflow/plan.json")
        conflict_plan = copy.deepcopy(plan)
        tasks_by_id = {task["task_id"]: task for task in conflict_plan["tasks"]}
        first_task_id = EXPECTED_PACKET_TASK_IDS[0]
        second_task_id = EXPECTED_PACKET_TASK_IDS[2]
        tasks_by_id[second_task_id]["artifact_dir"] = tasks_by_id[first_task_id]["artifact_dir"]

        conflict_graph = entrypoint.build_execution_graph(conflict_plan)
        conflict_nodes = {task["task_id"]: task for task in conflict_graph["tasks"]}

        self.assertEqual(conflict_nodes[first_task_id]["scaffold_state"], "ready")
        self.assertEqual(conflict_nodes[second_task_id]["scaffold_state"], "blocked")
        self.assertIn("write_scope_conflict", conflict_nodes[second_task_id]["blocked_reasons"])
        self.assertNotIn(second_task_id, conflict_graph["ready_packets"])
        assert_packets_have_disjoint_output_scopes(self, [conflict_nodes[task_id] for task_id in conflict_graph["ready_packets"]])

    def test_validate_mode_blocks_corrupt_execution_graph(self) -> None:
        run_root = "dev/implementation/workflow-harness/tmp/entrypoint-tests/corrupt-execution-graph"
        scaffold_proc, _ = run_entrypoint("analyze-propose", "--input", COMPLETE_FIXTURE, "--run-root", run_root, "--mode", "scaffold", "--agent", "generic")
        self.assertEqual(scaffold_proc.returncode, 0, scaffold_proc.stderr)
        root = REPO_ROOT / run_root
        graph_path = root / ".workflow/execution-graph.json"
        graph = read_json(graph_path)
        graph_by_task = {task["task_id"]: task for task in graph["tasks"]}
        first_task_id = EXPECTED_PACKET_TASK_IDS[0]
        second_task_id = EXPECTED_PACKET_TASK_IDS[2]
        del graph_by_task[first_task_id]["packet_json"]
        graph_by_task[first_task_id]["depends_on_task_ids"] = [second_task_id]
        graph_by_task[second_task_id]["depends_on_task_ids"] = [first_task_id]
        graph_by_task[second_task_id]["artifact_write_scope"] = copy.deepcopy(graph_by_task[first_task_id]["artifact_write_scope"])
        graph["dependency_edges"].extend(
            [
                {"from_task_id": second_task_id, "to_task_id": first_task_id},
                {"from_task_id": first_task_id, "to_task_id": second_task_id},
                {"from_task_id": "missing-task", "to_task_id": first_task_id},
            ]
        )
        graph["ready_packets"].append("missing-task")
        graph_path.write_text(json.dumps(graph, ensure_ascii=False, indent=2, sort_keys=True) + "\n")

        validate_proc, validate_data = run_entrypoint("analyze-propose", "--input", COMPLETE_FIXTURE, "--run-root", run_root, "--mode", "validate", "--resume")
        self.assertEqual(validate_proc.returncode, 2, validate_proc.stdout)
        graph_diagnostics = validate_data["validation"]["execution_graph"]
        self.assertEqual(graph_diagnostics["status"], "blocked")
        self.assertTrue(graph_diagnostics["checked"])
        graph_finding_ids = {finding["id"] for finding in graph_diagnostics["findings"]}
        self.assertIn("execution_graph.task.required_field", graph_finding_ids)
        self.assertIn("execution_graph.edge.unknown_task_id", graph_finding_ids)
        self.assertIn("execution_graph.ready_packets.unknown_task_id", graph_finding_ids)
        self.assertIn("execution_graph.ready_packets.unsafe_dependency", graph_finding_ids)
        self.assertIn("execution_graph.ready_packets.write_scope_collision", graph_finding_ids)
        self.assertIn("execution_graph.parallel_group.write_scope_collision", graph_finding_ids)
        self.assertIn("execution_graph.dependencies.cycle", graph_finding_ids)
        self.assertIn("execution_graph", {finding["source_workflow"] for finding in validate_data["validation"]["imported_findings"]})

        summary = read_json(root / ".workflow/validation/summary.json")
        self.assertEqual(summary["execution_graph"]["status"], "blocked")
        summary_md = (root / ".workflow/validation/summary.md").read_text()
        self.assertIn("## Execution graph", summary_md)
        self.assertIn("execution_graph.dependencies.cycle", summary_md)

    def test_validate_mode_preserves_legacy_graph_absent_path(self) -> None:
        run_root = "dev/implementation/workflow-harness/tmp/entrypoint-tests/legacy-graph-absent"
        scaffold_proc, _ = run_entrypoint("analyze-propose", "--input", COMPLETE_FIXTURE, "--run-root", run_root, "--mode", "scaffold", "--agent", "generic")
        self.assertEqual(scaffold_proc.returncode, 0, scaffold_proc.stderr)
        root = REPO_ROOT / run_root
        (root / ".workflow/execution-graph.json").unlink()
        plan_path = root / ".workflow/plan.json"
        plan = read_json(plan_path)
        plan.pop("execution_graph", None)
        plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True) + "\n")

        validate_proc, validate_data = run_entrypoint("analyze-propose", "--input", COMPLETE_FIXTURE, "--run-root", run_root, "--mode", "validate", "--resume")
        self.assertEqual(validate_proc.returncode, 2, validate_proc.stdout)
        validation = validate_data["validation"]
        graph_diagnostics = validation["execution_graph"]
        self.assertEqual(graph_diagnostics["status"], "absent_legacy")
        self.assertFalse(graph_diagnostics["checked"])
        self.assertEqual(graph_diagnostics["finding_counts"]["total"], 0)
        self.assertNotIn("execution_graph", {finding["source_workflow"] for finding in validation["imported_findings"]})
        summary_md = (root / ".workflow/validation/summary.md").read_text()
        self.assertIn("absent_legacy", summary_md)
        next_action = read_json(root / ".workflow/next-action.json")
        self.assertEqual(next_action["validation"]["execution_graph"]["status"], "absent_legacy")

    def test_deterministic_scaffold_across_isolated_roots(self) -> None:
        roots = [
            "dev/implementation/workflow-harness/tmp/entrypoint-tests/deterministic-a",
            "dev/implementation/workflow-harness/tmp/entrypoint-tests/deterministic-b",
        ]
        snapshots = []
        for run_root in roots:
            proc, _ = run_entrypoint("analyze-propose", "--input", FIXTURE, "--run-root", run_root, "--mode", "scaffold", "--agent", "generic")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            root = REPO_ROOT / run_root
            first_packet_rel = read_json(root / ".workflow/next-action.json")["first_packet"]["json"]
            packet = read_json(root / first_packet_rel)
            snapshots.append({
                "normalized": read_json(root / ".workflow/input.normalized.json"),
                "plan": strip_run_root(read_json(root / ".workflow/plan.json"), roots),
                "tasks": strip_run_root(read_json(root / ".workflow/tasks.json"), roots),
                "next_action": strip_run_root(read_json(root / ".workflow/next-action.json"), roots),
                "task_payload": strip_run_root(packet["task_payload"], roots),
            })
        self.assertEqual(snapshots[0], snapshots[1])

    def test_registry_packet_order_and_paths_stay_stable_for_entrypoint_fixtures(self) -> None:
        fixtures = [("minimal", FIXTURE), ("complete", COMPLETE_FIXTURE)]
        for label, fixture in fixtures:
            with self.subTest(fixture=label):
                run_root = f"dev/implementation/workflow-harness/tmp/entrypoint-tests/registry-{label}"
                proc, _ = run_entrypoint("analyze-propose", "--input", fixture, "--run-root", run_root, "--mode", "scaffold")
                self.assertEqual(proc.returncode, 0, proc.stderr)
                root = REPO_ROOT / run_root
                registry = read_json(root / ".workflow/registry.json")
                tasks = read_json(root / ".workflow/tasks.json")
                self.assertEqual(registry["packets"], EXPECTED_REGISTRY_PACKETS)
                self.assertEqual([task["task_id"] for task in tasks], EXPECTED_PACKET_TASK_IDS)
                for packet in registry["packets"]:
                    self.assertTrue((root / packet["json"]).exists(), packet["json"])
                    self.assertTrue((root / packet["markdown"]).exists(), packet["markdown"])
                next_action = read_json(root / ".workflow/next-action.json")
                self.assertEqual(next_action["first_packet"]["task_id"], EXPECTED_PACKET_TASK_IDS[0])
                self.assertEqual(next_action["first_packet"]["json"], EXPECTED_REGISTRY_PACKETS[0]["json"])
                self.assertEqual(next_action["first_packet"]["markdown"], EXPECTED_REGISTRY_PACKETS[0]["markdown"])

    def test_supported_agent_launchers_do_not_change_task_payload(self) -> None:
        run_root = "dev/implementation/workflow-harness/tmp/entrypoint-tests/agent-invariant"
        payloads = []
        launchers = []
        packet_shapes = []
        markdown_without_launchers = []
        packet_rel = None
        for agent in SUPPORTED_AGENTS:
            args = ["analyze-propose", "--input", FIXTURE, "--run-root", run_root, "--mode", "scaffold", "--agent", agent]
            if packet_rel is not None:
                args.append("--resume")
            proc, data = run_entrypoint(*args)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            root = REPO_ROOT / run_root
            packet_rel = data["next_action"]["first_packet"]["json"]
            registry = read_json(root / ".workflow/registry.json")
            self.assertEqual(registry["packets"], EXPECTED_REGISTRY_PACKETS)
            agent_packet_shapes = []
            agent_markdowns = []
            for entry in registry["packets"]:
                packet = read_json(root / entry["json"])
                self.assertEqual(packet["agent"], agent)
                self.assertTrue(packet["launcher"])
                agent_packet_shapes.append({key: value for key, value in packet.items() if key not in {"agent", "launcher"}})
                markdown = (root / entry["markdown"]).read_text()
                self.assertIn(f"Launcher: {packet['launcher']}", markdown)
                agent_markdowns.append(without_launcher_line(markdown))
            first_packet = read_json(root / packet_rel)
            payloads.append((first_packet["task_payload_sha256"], first_packet["task_payload"]))
            launchers.append(first_packet["launcher"])
            packet_shapes.append(agent_packet_shapes)
            markdown_without_launchers.append(agent_markdowns)
        self.assertEqual(len({json.dumps(payload, sort_keys=True) for payload in payloads}), 1)
        self.assertEqual(len(set(launchers)), len(SUPPORTED_AGENTS))
        self.assertTrue(all(shape == packet_shapes[0] for shape in packet_shapes[1:]))
        self.assertTrue(all(markdown == markdown_without_launchers[0] for markdown in markdown_without_launchers[1:]))

    def test_prompt_budget_surface_stays_below_twenty_five_percent(self) -> None:
        run_root = "dev/implementation/workflow-harness/tmp/entrypoint-tests/prompt-budget"
        proc, _ = run_entrypoint("analyze-propose", "--input", FIXTURE, "--run-root", run_root, "--mode", "scaffold")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        input_text = (REPO_ROOT / FIXTURE).read_text()
        baseline_parts = [input_text]
        for workflow in ["asset-investment-diligence", "oracle-analysis"]:
            base = REPO_ROOT / "user/references/workflows" / workflow
            baseline_parts.extend((base / name).read_text() for name in WORKFLOW_DOCS)
        baseline_text = "\n".join(baseline_parts)
        root = REPO_ROOT / run_root
        next_action = read_json(root / ".workflow/next-action.json")
        packet = read_json(root / next_action["first_packet"]["json"])
        new_parts = [
            input_text,
            (root / ".workflow/next-action.md").read_text(),
            (root / next_action["first_packet"]["markdown"]).read_text(),
        ]
        for rel in packet["task_payload"].get("mandatory_reference_paths", []):
            new_parts.append((REPO_ROOT / rel).read_text())
        new_text = "\n".join(new_parts)
        self.assertLess(len(new_text), len(baseline_text) * 0.25)
        self.assertLess(token_proxy(new_text), token_proxy(baseline_text) * 0.25)
        self.assertNotIn("Collect token-level evidence for `[symbol]`", new_text)
        self.assertNotIn("raw `subagent-prompts.md`", new_text)

    def test_agent_handoff_keeps_codex_prompt_compact_with_key_params(self) -> None:
        run_root = "dev/implementation/workflow-harness/tmp/entrypoint-tests/codex-handoff"
        proc, data = run_entrypoint("analyze-propose", "--input", COMPLETE_FIXTURE, "--run-root", run_root, "--mode", "scaffold", "--agent", "codex")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        root = REPO_ROOT / run_root
        handoff = data["next_action"]["agent_handoff"]
        copy_prompt = handoff["copy_prompt"]
        self.assertLess(len(copy_prompt), 900)
        self.assertIn(".workflow/agent-handoff.md", copy_prompt)
        self.assertIn("0x11111111", copy_prompt)
        self.assertIn("0x33333333", copy_prompt)
        self.assertIn("LTV/LT", copy_prompt)
        self.assertIn("Borrow rate", copy_prompt)
        self.assertIn("no Preview/Execute", copy_prompt)
        self.assertNotIn("Execute packets in registry order", copy_prompt)
        self.assertNotIn("Validation exit semantics", copy_prompt)
        self.assertTrue((root / handoff["markdown"]).exists())
        text = (root / handoff["markdown"]).read_text()
        self.assertIn("Paste this single line", text)
        self.assertIn("Execute packets in registry order", text)
        self.assertIn("advisory metadata only", text)
        self.assertIn("does not schedule packets", text)
        self.assertIn("Delegation is safe only", text)
        self.assertIn("Parent must stay serial", text)
        self.assertIn("worker `return_contract`", text)
        self.assertIn("Preview and Execute are blocked", text)
        self.assertIn("--mode validate --resume", text)

    def test_missing_live_fields_are_blockers_not_fatal_input_errors(self) -> None:
        run_root = "dev/implementation/workflow-harness/tmp/entrypoint-tests/missing-live"
        proc, data = run_entrypoint(
            "analyze-propose",
            "--input",
            "dev/implementation/workflow-harness/fixtures/entrypoint-inputs/missing-live-fields.json",
            "--run-root",
            run_root,
            "--mode",
            "scaffold",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(data["status"], "scaffolded")
        root = REPO_ROOT / run_root
        next_action = read_json(root / ".workflow/next-action.json")
        self.assertEqual(next_action["status"], "blocked")
        fields = {item["field"] for item in next_action["first_packet"]["blocking_unknowns"]}
        self.assertIn("token_address", fields)
        normalized = read_json(root / ".workflow/input.normalized.json")
        all_blocker_fields = {item["field"] for item in normalized["blocking_unknowns"]}
        self.assertTrue({"token_address", "feed_address", "position_side", "token_role", "position_size"}.issubset(all_blocker_fields))
        generated_text = (root / ".workflow/next-action.md").read_text() + "\n" + "\n".join(p.read_text() for p in (root / ".workflow/packets").glob("**/*.md"))
        self.assertNotIn("0x0000000000000000000000000000000000000000", generated_text)
        self.assertNotIn("risk-adjusted apr", generated_text.lower())

    def test_packets_embed_investigation_contract_and_fact_state_templates(self) -> None:
        run_root = "dev/implementation/workflow-harness/tmp/entrypoint-tests/stage-contract"
        proc, _ = run_entrypoint("analyze-propose", "--input", FIXTURE, "--run-root", run_root, "--mode", "scaffold")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        root = REPO_ROOT / run_root
        next_action = read_json(root / ".workflow/next-action.json")
        packet = read_json(root / next_action["first_packet"]["json"])
        payload = packet["task_payload"]
        contract = payload["stage_contract"]
        states = set(contract["allowed_unknown_states"])
        self.assertTrue({"input_missing", "not_investigated", "investigated_no_result", "not_applicable"}.issubset(states))
        self.assertTrue(any(item["state"] == "input_missing" for item in payload["blocking_unknowns"]))
        self.assertTrue(any(item.get("expected_state_until_resolved") == "input_missing" for item in contract["mandatory_facts"]))
        fact_result_states = {item["state"] for item in contract["fact_results_template"]["fact_results"]}
        self.assertIn("input_missing", fact_result_states)
        self.assertIn("not_investigated", fact_result_states)
        self.assertTrue(any(item["state"] == "not_applicable" for item in contract["precomputed_boundary_facts"]))
        no_result = contract["no_result_proof_template"]
        self.assertEqual(no_result["state"], "investigated_no_result")
        self.assertIn("methods_tried", no_result)
        self.assertIn("sources_checked", no_result)
        self.assertIn("negative_evidence_path", no_result)
        self.assertIn("residual_decision_effect", no_result)
        markdown = (root / next_action["first_packet"]["markdown"]).read_text()
        self.assertIn("## Protocol investigation adapter", markdown)
        self.assertIn("## Stage contract checklist", markdown)
        self.assertIn("## Fact results to produce", markdown)
        self.assertIn("## No-result proof template", markdown)
        self.assertIn("negative_evidence_path", markdown)
        self.assertNotIn("## Blocking unknowns\n\n- none", markdown)

    def test_asset_input_blockers_propagate_to_related_oracle_packet(self) -> None:
        run_root = "dev/implementation/workflow-harness/tmp/entrypoint-tests/propagated-blockers"
        proc, _ = run_entrypoint("analyze-propose", "--input", FIXTURE, "--run-root", run_root, "--mode", "scaffold")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        root = REPO_ROOT / run_root
        oracle_packet = read_json(root / ".workflow/packets/oracle/oracle-S0_scope_and_acceptance-eth-mainnet-sample-base-token-gearbox-oracle.json")
        payload = oracle_packet["task_payload"]
        fact_ids = {item["fact_id"] for item in payload["blocking_unknowns"]}
        self.assertIn("asset.eth-mainnet-sample-base-token.token_address", fact_ids)
        self.assertIn("oracle.eth-mainnet-sample-base-token-gearbox-oracle.feed_address", fact_ids)
        adapter = payload["protocol_adapter"]
        self.assertEqual(adapter["adapter_id"], "gearbox.oracle-market-parameter-context.v1")
        adapter_fact_ids = {item["fact_id"] for item in adapter["required_facts"]}
        self.assertIn("gearbox.market_or_credit_manager", adapter_fact_ids)
        self.assertIn("gearbox.allowed_token_status", adapter_fact_ids)
        self.assertIn("registry_checked", adapter["no_result_proof_classes"])
        oracle_markdown = (root / ".workflow/packets/oracle/oracle-S0_scope_and_acceptance-eth-mainnet-sample-base-token-gearbox-oracle.md").read_text()
        self.assertIn("## Protocol investigation adapter", oracle_markdown)
        self.assertIn("No-market/no-route semantics", oracle_markdown)
        self.assertIn("investigated_no_result", oracle_markdown)

    def test_s6_packet_allows_analyze_only_scenario_when_only_user_sizing_inputs_are_missing(self) -> None:
        run_root = "dev/implementation/workflow-harness/tmp/entrypoint-tests/scenario-allowed"
        proc, _ = run_entrypoint("analyze-propose", "--input", COMPLETE_FIXTURE, "--run-root", run_root, "--mode", "scaffold")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        root = REPO_ROOT / run_root
        packet = read_s6_packet(root)
        contract = packet["task_payload"]["stage_contract"]["scenario_band_contract"]
        self.assertTrue(contract["scenario_needed"])
        self.assertTrue(contract["scenario_allowed"])
        self.assertEqual(set(contract["missing_inputs"]), {"hold_horizon", "position_size", "target_leverage", "user_risk_policy"})
        self.assertEqual(contract["blocking_inputs_that_prevent_scenarios"], [])
        self.assertIn("request_more_inputs", contract["proposal_gate"])
        self.assertIn("Preview or Execute", contract["preview_execute_gate"])
        s6_markdown = sorted((root / ".workflow/packets/asset").glob("asset-S6_quantitative_underwriting-*.md"))[0].read_text()
        self.assertIn("## Analyze-only scenario contract", s6_markdown)
        self.assertIn("Scenario allowed: `True`", s6_markdown)

    def test_s6_packet_disallows_scenario_when_request_forbids_scenarios(self) -> None:
        source = read_json(REPO_ROOT / COMPLETE_FIXTURE)
        source["constraints"] = [*source["constraints"], "No scenario analysis; exact inputs only."]
        input_path = TMP_ROOT / "scenario-forbidden-input.json"
        input_path.write_text(json.dumps(source, indent=2))
        run_root = "dev/implementation/workflow-harness/tmp/entrypoint-tests/scenario-forbidden"
        proc, _ = run_entrypoint("analyze-propose", "--input", str(input_path), "--run-root", run_root, "--mode", "scaffold")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        packet = read_s6_packet(REPO_ROOT / run_root)
        contract = packet["task_payload"]["stage_contract"]["scenario_band_contract"]
        self.assertTrue(contract["scenario_needed"])
        self.assertFalse(contract["scenario_allowed"])
        self.assertIn("disallow", contract["reason"])

    def test_malformed_input_gets_stable_error_id(self) -> None:
        proc, data = run_entrypoint(
            "analyze-propose",
            "--input",
            "dev/implementation/workflow-harness/fixtures/entrypoint-inputs/malformed-missing-assets.json",
            "--run-root",
            "dev/implementation/workflow-harness/tmp/entrypoint-tests/malformed",
            "--mode",
            "scaffold",
        )
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(data["status"], "input_error")
        self.assertIn("WE_ASSETS", {finding["id"] for finding in data["findings"]})

    def test_path_escape_fixture_is_rejected_before_writing(self) -> None:
        proc, data = run_entrypoint(
            "analyze-propose",
            "--input",
            "dev/implementation/workflow-harness/fixtures/entrypoint-inputs/path-escape-artifact-root.json",
            "--mode",
            "scaffold",
        )
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(data["status"], "input_error")
        self.assertIn("WE_PATH_ESCAPE", {finding["id"] for finding in data["findings"]})
        self.assertIsNone(data.get("run_root"))

    def test_validate_mode_imports_child_validator_findings_into_next_action(self) -> None:
        run_root = "dev/implementation/workflow-harness/tmp/entrypoint-tests/validate-bridge"
        scaffold_proc, _ = run_entrypoint("analyze-propose", "--input", FIXTURE, "--run-root", run_root, "--mode", "scaffold")
        self.assertEqual(scaffold_proc.returncode, 0, scaffold_proc.stderr)
        validate_proc, validate_data = run_entrypoint("analyze-propose", "--input", FIXTURE, "--run-root", run_root, "--mode", "validate", "--resume")
        self.assertEqual(validate_proc.returncode, 2, validate_proc.stdout)
        self.assertEqual(validate_data["status"], "blocked")
        self.assertEqual(validate_data["exit_code"], 2)
        validation = validate_data["validation"]
        self.assertEqual(validation["status"], "blocked")
        self.assertEqual({report["workflow"] for report in validation["reports"]}, {"asset", "oracle", "combined"})
        self.assertEqual([report["exit_code"] for report in validation["reports"]], [2, 2, 2])
        self.assertEqual([report["status"] for report in validation["reports"]], ["fail", "fail", "fail"])
        self.assertEqual([command["exit_code"] for command in validation["commands"]], [2, 2, 2])
        self.assertGreater(validation["finding_counts"]["total"], 0)
        self.assertEqual({finding["source_workflow"] for finding in validation["imported_findings"]}, {"asset", "oracle", "combined"})
        root = REPO_ROOT / run_root
        summary = read_json(root / ".workflow/validation/summary.json")
        self.assertEqual(summary["status"], "blocked")
        self.assertEqual(summary["finding_counts"], validation["finding_counts"])
        next_action = read_json(root / ".workflow/next-action.json")
        self.assertEqual(next_action["status"], "blocked")
        self.assertEqual(next_action["validation"]["status"], "blocked")
        self.assertEqual(next_action["validation"]["finding_counts"], validation["finding_counts"])


if __name__ == "__main__":
    unittest.main()
