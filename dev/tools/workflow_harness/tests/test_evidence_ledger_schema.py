"""Regression checks for the workflow evidence-ledger contract fixture."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
SCHEMA_PATH = REPO_ROOT / "dev/implementation/workflow-harness/contracts/evidence-ledger.schema.json"
FIXTURE_ROOT = REPO_ROOT / "dev/implementation/workflow-harness/fixtures/evidence-ledger/positive-and-no-result"
LEDGER_PATH = FIXTURE_ROOT / "evidence-ledger.json"

MINIMUM_FACT_FIELDS = {
    "fact_id",
    "claim",
    "scope_id",
    "stage_id",
    "source_type",
    "retrieved_at",
    "method",
    "command_or_query",
    "raw_output_path",
    "decoded_value",
    "status",
    "freshness",
    "decision_effect",
}
RPC_REQUIRED = {"chain_id", "block_number", "contract", "signature_or_selector", "raw_output", "decoder"}
HTTP_REQUIRED = {"url", "request", "response_path", "status_code", "timestamp"}
NEGATIVE_REQUIRED = {"search_space", "queries_or_methods_tried", "sources_checked", "sufficiency_assessment"}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def facts() -> list[dict]:
    return load_json(LEDGER_PATH)["facts"]


def test_schema_declares_required_fact_envelope_and_source_types() -> None:
    schema = load_json(SCHEMA_PATH)
    fact_schema = schema["$defs"]["fact"]

    assert schema["properties"]["schema_version"]["const"] == "evidence-ledger-v1"
    assert MINIMUM_FACT_FIELDS <= set(fact_schema["required"])
    assert {
        "rpc",
        "explorer",
        "http_api",
        "source_code",
        "docs",
        "negative_search",
    } <= set(fact_schema["properties"]["source_type"]["enum"])
    assert {
        "confirmed",
        "investigated_no_result",
        "source_unavailable",
        "source_inconclusive",
        "contradicted",
        "input_missing",
        "not_investigated",
        "not_applicable",
    } <= set(fact_schema["properties"]["status"]["enum"])


def test_schema_declares_rpc_http_and_negative_required_fields() -> None:
    schema = load_json(SCHEMA_PATH)

    assert RPC_REQUIRED <= set(schema["$defs"]["rpc_fact"]["required"])
    assert {"decoder", "abi_or_source"} <= set(schema["$defs"]["rpc_fact"]["properties"]["decoder"]["required"])
    assert HTTP_REQUIRED <= set(schema["$defs"]["http_api_fact"]["required"])
    assert NEGATIVE_REQUIRED <= set(schema["$defs"]["negative_investigation"]["required"])
    assert {"verdict", "rationale"} <= set(
        schema["$defs"]["negative_investigation"]["properties"]["sufficiency_assessment"]["required"]
    )


def test_fixture_demonstrates_positive_and_no_result_facts() -> None:
    ledger = load_json(LEDGER_PATH)
    statuses = {fact["status"] for fact in ledger["facts"]}

    assert ledger["schema_version"] == "evidence-ledger-v1"
    assert "confirmed" in statuses
    assert "investigated_no_result" in statuses
    assert any(fact["source_type"] == "rpc" and fact["status"] == "confirmed" for fact in ledger["facts"])
    assert any(
        fact["source_type"] == "negative_search" and fact["status"] == "investigated_no_result"
        for fact in ledger["facts"]
    )


def test_fixture_facts_have_required_envelope_and_resolvable_raw_paths() -> None:
    for fact in facts():
        assert MINIMUM_FACT_FIELDS <= set(fact), fact["fact_id"]
        raw_path = FIXTURE_ROOT / fact["raw_output_path"]
        assert raw_path.is_file(), (fact["fact_id"], raw_path)
        assert fact["decision_effect"].get("effect")
        assert fact["decision_effect"].get("rationale")
        assert fact["freshness"].get("status")
        assert fact["freshness"].get("basis")


def test_fixture_type_specific_fields_are_complete() -> None:
    for fact in facts():
        if fact["source_type"] == "rpc":
            assert RPC_REQUIRED <= set(fact["rpc"]), fact["fact_id"]
            assert {"decoder", "abi_or_source"} <= set(fact["rpc"]["decoder"]), fact["fact_id"]
        if fact["source_type"] in {"http_api", "explorer"}:
            assert HTTP_REQUIRED <= set(fact["http_api"]), fact["fact_id"]
            assert (FIXTURE_ROOT / fact["http_api"]["response_path"]).is_file(), fact["fact_id"]
        if fact["source_type"] == "negative_search" or fact["status"] == "investigated_no_result":
            assert NEGATIVE_REQUIRED <= set(fact["negative_investigation"]), fact["fact_id"]
            sufficiency = fact["negative_investigation"]["sufficiency_assessment"]
            assert sufficiency["verdict"] in {"sufficient", "insufficient"}, fact["fact_id"]
            assert sufficiency["rationale"], fact["fact_id"]
