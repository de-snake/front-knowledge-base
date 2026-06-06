#!/usr/bin/env python3
"""Deterministic workflow entrypoint for Analyze -> Propose runs.

This module scaffolds and validates front-knowledge-base workflow runs from one
small JSON input. It is deliberately standard-library only and performs no live
research, semantic judgment, or state-changing action.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import workflow_entrypoint_contracts as contracts
import workflow_protocol_adapters as protocol_adapters

REPO_ROOT = Path(__file__).resolve().parents[2]
DEV_IMPLEMENTATION = REPO_ROOT / "dev" / "implementation"
SEMANTIC_CRITIC_RUNNER = REPO_ROOT / "dev" / "tools" / "semantic_critic_runner.py"
WORKFLOW_MANIFEST_PATHS = {
    "asset": REPO_ROOT / "user" / "references" / "workflows" / "asset-investment-diligence" / "workflow.json",
    "oracle": REPO_ROOT / "user" / "references" / "workflows" / "oracle-analysis" / "workflow.json",
}

EXECUTION_GRAPH_REQUIRED_TOP_LEVEL_KEYS = (
    "schema_version",
    "command",
    "run_root",
    "input_sha256",
    "plan_schema_version",
    "packet_schema_version",
    "graph_status",
    "fallback_behavior",
    "tasks",
    "dependency_edges",
    "ready_packets",
    "blocked_packets",
    "parallel_groups",
    "serial_sections",
    "compatibility",
)
EXECUTION_GRAPH_REQUIRED_TASK_KEYS = (
    "task_id",
    "workflow_key",
    "workflow_id",
    "stage_id",
    "registry_index",
    "packet_json",
    "packet_markdown",
    "depends_on_task_ids",
    "dependency_edges",
    "artifact_write_scope",
    "ready_after_validation",
    "blocking_unknowns",
    "scaffold_state",
    "blocked_reasons",
    "missing_artifacts",
    "parallel_group_id",
    "delegate_to_subagent",
    "recommended_max_concurrent",
)
EXECUTION_GRAPH_REQUIRED_LIST_FIELDS = (
    "tasks",
    "dependency_edges",
    "ready_packets",
    "blocked_packets",
    "parallel_groups",
    "serial_sections",
)

SUBAGENT_PROMPT_SECTIONS = {
    ("asset", "S1_general_asset_mining"): "S1 prompt — General asset mining",
    ("asset", "S2_asset_risk_analyst_report"): "S2 prompt — Asset-risk analyst report",
    ("asset", "S3_pt_market_economics"): "S3 prompt — PT market/economics analysis",
    ("asset", "S4_x_social_mining"): "S4 prompt — X/social mining",
    ("oracle", "S1_feed_inventory_and_graph"): "S1 — Feed inventory and graph worker",
    ("oracle", "S3_source_primitive_audit"): "S3 — Source primitive audit worker",
}

SUBAGENT_RETURN_CONTRACT_SECTION = "Shared stage-worker return contract"

FACT_STATES = (
    "not_applicable",
    "input_missing",
    "not_investigated",
    "investigated_no_result",
    "source_unavailable",
    "source_inconclusive",
    "contradicted",
)

MISSING_VALUE_MARKERS = {
    "",
    "unknown",
    "not found",
    "not_available",
    "not available",
    "n/a",
    "na",
    "none",
    "null",
    "tbd",
    "todo",
}

DISALLOWED_PLACEHOLDERS = (
    "unknown",
    "not found",
    "not_available",
    "TBD",
    "none",
    "blank required fields",
)

STATE_EVIDENCE_REQUIREMENTS = {
    "not_applicable": "Record applicability_rule_id, scope/input evidence path, reason, and decision_effect.",
    "input_missing": "Record input_schema_key, expected input, why defaults are unsafe, requested_input, and decision_effect.",
    "not_investigated": "Failure state for required facts: name the missing investigation and return blocked/review_required.",
    "investigated_no_result": "Attach a no_result_proof with methods_tried, sources_checked, negative_evidence_path, coverage, freshness, and residual_decision_effect.",
    "source_unavailable": "Record source identity, method, timestamp, exact error/status, retry or alternate-source notes, and decision_effect.",
    "source_inconclusive": "Record sources read, insufficient/ambiguous evidence, freshness/coverage limits, follow-up, and decision_effect.",
    "contradicted": "Record conflicting sources/values, timestamps, source-authority rule, reconciliation status, and decision_effect.",
}

ANALYZE_ONLY_SCENARIO_INPUT_FIELDS = {
    "position_size": "position size / notional band",
    "target_leverage": "leverage band",
    "hold_horizon": "holding horizon band",
    "user_risk_policy": "risk-policy / HF-floor band",
}

SCENARIO_DISABLE_PATTERNS = (
    "do not produce scenario",
    "do not provide scenario",
    "no scenario analysis",
    "no scenario bands",
    "scenario analysis prohibited",
    "scenario analysis forbidden",
    "exact inputs only",
)

SCENARIO_BAND_CONTRACT_VERSION = "asset-s6-analyze-only-scenario-band-v1"
SCENARIO_BAND_LEVELS = ("conservative", "base", "upside")

STAGE_FACT_SLOT_DESCRIPTIONS = {
    "S1_general_asset_mining": (
        "token identity/address/chain/decimals with source path",
        "admin, proxy, mint, freeze, pause, transfer, and upgrade controls",
        "issuer/backing/redemption/security facts",
        "transferability, liquidity, oracle, and governance constraints",
    ),
    "S2_asset_risk_analyst_report": (
        "S1 source evidence imported without silent gaps",
        "risk classification by admin, issuer/backing, transferability, liquidity, oracle, and governance axis",
        "explicit unresolved fact states and decision effects",
    ),
    "S6_quantitative_underwriting": (
        "all quantitative assumptions: borrow rate, LTV/LT, size, leverage, horizon, liquidity, and pricing basis",
        "PT/social/market inputs are known, not_applicable, or proven no-result",
        "Analyze-only scenario bands when sizing, leverage, horizon, or risk-policy inputs are missing and scenarios are allowed",
        "non-execution recommendation gate from unresolved facts",
    ),
    "S7_final_verification": (
        "required reports and indexes exist",
        "fact-state summary matches stage artifacts",
        "Preview/Execute remain blocked unless a separate proposal gate is satisfied",
    ),
    "S0_scope_and_acceptance": (
        "oracle scope: chain, protocol, market/credit manager, position side, token role, and position size",
        "feed address or replayable feed-discovery plan",
        "accepted methodologies and non-execution acceptance policy",
    ),
    "S1_feed_inventory_and_graph": (
        "feed contract inventory and dependency graph",
        "recursive source-node discovery with raw probe artifacts",
        "missing feed/dependency results represented as fact states, not prose placeholders",
    ),
    "S2_node_classification": (
        "node class and math reconstruction for each feed dependency",
        "source primitive, scaling, staleness, and fallback behavior",
        "unclassified nodes carry explicit unknown state and evidence path",
    ),
    "S3_source_primitive_audit": (
        "source primitive authority, freshness, update path, and manipulation surface",
        "raw source evidence saved for every checked primitive",
        "negative source searches include no-result proof bundles",
    ),
    "S4_stress_tradeoff_analysis": (
        "borrower/pool/liquidator side-specific stress scenarios",
        "size, liquidity, staleness, redemption, and route assumptions",
        "tradeoff conclusion derived from fact states rather than placeholder gaps",
    ),
    "S5_protocol_fit_and_parameter_context": (
        "protocol-fit memo ties oracle facts to Gearbox parameter context",
        "unresolved material facts map to review_required/request_more_inputs/blocked",
        "no Preview/Execute readiness claim without separate parent proposal gate",
    ),
    "S6_final_verification": (
        "oracle output files and final indexes exist",
        "feed/source/protocol-fit fact states are summarized",
        "final oracle status is consistent with unresolved fact decision effects",
    ),
}


@dataclass(frozen=True)
class Finding:
    id: str
    severity: str
    message: str
    path: str = "."
    field: str | None = None
    fix_hint: str | None = None
    actual: Any | None = None
    expected: Any | None = None


@dataclass
class RunnerResult:
    schema_version: str = contracts.RESULT_SCHEMA_VERSION
    command: str = contracts.COMMAND
    mode: str = "scaffold"
    status: str = "pass"
    exit_code: int = 0
    run_root: str | None = None
    input_sha256: str | None = None
    next_action: dict[str, Any] | None = None
    validation: dict[str, Any] | None = None
    findings: list[dict[str, Any]] = field(default_factory=list)
    files_written: list[str] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        return stable_json(asdict(self))


class WorkflowInputError(ValueError):
    def __init__(self, findings: list[Finding]):
        super().__init__(findings[0].message if findings else "workflow input error")
        self.findings = findings


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def slugify(value: Any, fallback: str = "scope") -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or fallback


def repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def ensure_under(path: Path, root: Path, finding_path: str = ".") -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise WorkflowInputError([
            Finding(
                id="WE_PATH_ESCAPE",
                severity="P0",
                message="path resolves outside the allowed root",
                path=finding_path,
                expected=f"under {repo_relative(root)}",
                actual=str(path),
                fix_hint="Use a path under dev/implementation or omit the field to let the runner choose a deterministic run root.",
            )
        ]) from exc
    return resolved


def resolve_existing_repo_path(path_text: str, *, field: str) -> Path:
    path = Path(path_text).expanduser()
    if not path.is_absolute():
        path = REPO_ROOT / path
    resolved = path.resolve()
    try:
        resolved.relative_to(REPO_ROOT.resolve())
    except ValueError as exc:
        raise WorkflowInputError([
            Finding(
                id="WE_PATH_ESCAPE",
                severity="P0",
                message="input path resolves outside the vault",
                path=field,
                expected="path under front-knowledge-base",
                actual=path_text,
                fix_hint="Move the input file into this repository or pass a repository-relative path.",
            )
        ]) from exc
    return resolved


def load_input(path_text: str) -> dict[str, Any]:
    path = resolve_existing_repo_path(path_text, field="--input")
    try:
        raw = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise WorkflowInputError([
            Finding(
                id="WE_SCHEMA_VERSION",
                severity="P0",
                message=f"input is not valid JSON: {exc.msg}",
                path=repo_relative(path),
                field="json",
                fix_hint="Provide a JSON file using schema_version workflow-entrypoint-input-v1.",
            )
        ]) from exc
    if not isinstance(raw, dict):
        raise WorkflowInputError([
            Finding(
                id="WE_SCHEMA_VERSION",
                severity="P0",
                message="input root must be a JSON object",
                path=repo_relative(path),
                field="root",
            )
        ])
    raw["_source_input"] = repo_relative(path)
    return raw


def listify(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def normalize_asset(raw_asset: dict[str, Any], index: int) -> dict[str, Any]:
    symbol = str(raw_asset.get("symbol") or raw_asset.get("asset_symbol") or "").strip()
    address = raw_asset.get("token_address", raw_asset.get("address"))
    address = str(address).strip() if address not in (None, "") else None
    chain = str(raw_asset.get("chain") or "not_available").strip() or "not_available"
    chain_id = raw_asset.get("chain_id")
    address_prefix = slugify(address[:10], "no-address") if address else "no-address"
    scope_slug = slugify(raw_asset.get("scope_slug") or raw_asset.get("scope_id") or f"{chain}-{symbol}-{address_prefix}", f"asset-{index + 1}")
    return {
        "scope_id": str(raw_asset.get("scope_id") or scope_slug),
        "scope_slug": scope_slug,
        "symbol": symbol,
        "name": raw_asset.get("name"),
        "chain": chain,
        "chain_id": chain_id,
        "token_address": address,
        "intended_use": raw_asset.get("intended_use") or "Analyze token/issuer/oracle/liquidity risks before any proposal.",
        "artifact_dir": f"tokens/{scope_slug}",
        "notes": listify(raw_asset.get("notes")),
    }


def normalize_oracle_scope(raw_scope: dict[str, Any], assets_by_symbol: dict[str, dict[str, Any]], index: int) -> dict[str, Any]:
    symbol = str(raw_scope.get("asset_symbol") or raw_scope.get("symbol") or raw_scope.get("asset") or "").strip()
    matched_asset = assets_by_symbol.get(symbol.lower()) if symbol else None
    chain = str(raw_scope.get("chain") or (matched_asset or {}).get("chain") or "not_available").strip() or "not_available"
    address = raw_scope.get("token_address") or (matched_asset or {}).get("token_address")
    scope_slug = slugify(
        raw_scope.get("scope_slug") or raw_scope.get("scope_id") or f"{chain}-{symbol or 'asset'}-oracle",
        f"oracle-{index + 1}",
    )
    return {
        "scope_id": str(raw_scope.get("scope_id") or scope_slug),
        "scope_slug": scope_slug,
        "asset_symbol": symbol,
        "related_asset_scope_id": raw_scope.get("related_asset_scope_id") or (matched_asset or {}).get("scope_id"),
        "chain": chain,
        "chain_id": raw_scope.get("chain_id") if raw_scope.get("chain_id") is not None else (matched_asset or {}).get("chain_id"),
        "token_address": address,
        "protocol": raw_scope.get("protocol") or "Gearbox",
        "market_or_credit_manager": raw_scope.get("market_or_credit_manager") or raw_scope.get("market") or "not_available",
        "feed_address": raw_scope.get("feed_address") or raw_scope.get("price_feed_address"),
        "feed_discovery_paths": listify(raw_scope.get("feed_discovery_paths") or raw_scope.get("feed_discovery_path")),
        "position_side": raw_scope.get("position_side"),
        "token_role": raw_scope.get("token_role"),
        "position_size": raw_scope.get("position_size"),
        "accepted_methodologies": listify(raw_scope.get("accepted_methodologies")) or [
            "recursive feed graph",
            "source primitive audit",
            "side-specific stress tradeoff analysis",
        ],
        "analysis_questions": listify(raw_scope.get("analysis_questions")),
        "artifact_dir": f"tokens/{scope_slug}",
    }


def is_missing_value(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().lower() in MISSING_VALUE_MARKERS
    return False


def _blocker(
    *,
    scope_type: str,
    scope_id: str,
    field: str,
    input_schema_key: str,
    expected_input: str,
    next_step: str,
    required_by: list[str],
    propagate_to_scope_ids: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "scope_type": scope_type,
        "scope_id": scope_id,
        "field": field,
        "fact_id": f"{scope_type}.{scope_id}.{field}",
        "state": "input_missing",
        "status": "input_missing",
        "input_schema_key": input_schema_key,
        "expected_input": expected_input,
        "source_path": ".workflow/input.normalized.json",
        "required_by": required_by,
        "decision_effect": "request_more_inputs",
        "propagate_to_scope_ids": sorted(set(propagate_to_scope_ids or [])),
        "next_step": next_step,
    }


def collect_blocking_unknowns(normalized: dict[str, Any]) -> list[dict[str, Any]]:
    blockers: list[dict[str, Any]] = []
    oracle_scopes_by_asset: dict[str, list[str]] = {}
    for scope in normalized["oracle_scopes"]:
        related = scope.get("related_asset_scope_id")
        if related:
            oracle_scopes_by_asset.setdefault(str(related), []).append(scope["scope_id"])

    for index, asset in enumerate(normalized["assets"]):
        if is_missing_value(asset.get("token_address")):
            blockers.append(_blocker(
                scope_type="asset",
                scope_id=asset["scope_id"],
                field="token_address",
                input_schema_key=f"assets[{index}].token_address",
                expected_input="deployed token contract address or an artifact proving discovery failed",
                next_step="Provide the deployed token address, or have the stage discover it and record a fact-result before conclusions.",
                required_by=["asset.S1_general_asset_mining", "asset.S2_asset_risk_analyst_report", "oracle.S0_scope_and_acceptance"],
                propagate_to_scope_ids=oracle_scopes_by_asset.get(asset["scope_id"], []),
            ))

    oracle_field_contracts = {
        "market_or_credit_manager": (
            "oracle_scopes[{index}].market_or_credit_manager",
            "Gearbox market, Credit Manager, pool, or explicit not-applicable rule",
            "Name the evaluated Gearbox market/Credit Manager/pool, or record a deterministic not_applicable rule.",
            ["oracle.S0_scope_and_acceptance", "oracle.S5_protocol_fit_and_parameter_context"],
        ),
        "feed_address": (
            "oracle_scopes[{index}].feed_address",
            "deployed protocol price-feed address or replayable feed-discovery no-result proof",
            "Discover the deployed protocol price feed or record why no deployed feed exists.",
            ["oracle.S0_scope_and_acceptance", "oracle.S1_feed_inventory_and_graph"],
        ),
        "position_side": (
            "oracle_scopes[{index}].position_side",
            "evaluated position side: borrower, pool LP, liquidator, curator/operator, or deterministic not_applicable rule",
            "Name the evaluated position side; do not infer side-specific losses from a blank or placeholder.",
            ["oracle.S0_scope_and_acceptance", "oracle.S4_stress_tradeoff_analysis"],
        ),
        "token_role": (
            "oracle_scopes[{index}].token_role",
            "token role such as collateral, debt asset, pool underlying, PT, or deterministic not_applicable rule",
            "Name the token role before protocol-fit or liquidation conclusions.",
            ["oracle.S0_scope_and_acceptance", "oracle.S5_protocol_fit_and_parameter_context"],
        ),
        "position_size": (
            "oracle_scopes[{index}].position_size",
            "position size, scenario size range, or input_missing fact with requested input",
            "Provide a size/scenario range or preserve input_missing before route, liquidity, or liquidation conclusions.",
            ["oracle.S0_scope_and_acceptance", "oracle.S4_stress_tradeoff_analysis", "asset.S6_quantitative_underwriting"],
        ),
    }
    for index, scope in enumerate(normalized["oracle_scopes"]):
        for field_name, (schema_key_template, expected_input, next_step, required_by) in oracle_field_contracts.items():
            if is_missing_value(scope.get(field_name)):
                blockers.append(_blocker(
                    scope_type="oracle",
                    scope_id=scope["scope_id"],
                    field=field_name,
                    input_schema_key=schema_key_template.format(index=index),
                    expected_input=expected_input,
                    next_step=next_step,
                    required_by=required_by,
                ))

    constraint_patterns = (
        ("position_size", r"\bno\s+position\s+size\b", "constraints", "position size, scenario size range, or input_missing fact with requested input", "Provide a size/scenario range or preserve input_missing before route, liquidity, or liquidation conclusions."),
        ("target_leverage", r"\bno\s+target\s+leverage\b", "constraints", "target leverage or explicit scenario range", "Provide target leverage/scenario leverage before quantitative proposal readiness."),
        ("hold_horizon", r"\bno\s+hold\s+horizon\b", "constraints", "hold horizon or deterministic not_applicable rule", "Provide hold horizon before risk/return conclusions."),
        ("user_risk_policy", r"\bno\s+user\s+(hf\s+floor|risk\s+policy)\b", "constraints", "user HF floor/risk policy or explicit not_applicable rule", "Provide user HF floor/risk policy before Preview/Execute readiness."),
    )
    constraint_text = "\n".join(str(item) for item in normalized.get("constraints", []))
    for field, pattern, schema_key, expected_input, next_step in constraint_patterns:
        if re.search(pattern, constraint_text, flags=re.IGNORECASE):
            blockers.append(_blocker(
                scope_type="run",
                scope_id="run",
                field=field,
                input_schema_key=schema_key,
                expected_input=expected_input,
                next_step=next_step,
                required_by=["asset.S6_quantitative_underwriting", "combined.Propose"],
            ))

    deduped: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for blocker in blockers:
        key = (blocker["scope_id"], blocker["field"], blocker["input_schema_key"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(blocker)
    return deduped


def normalize_input(raw: dict[str, Any]) -> dict[str, Any]:
    assets_raw = [item for item in listify(raw.get("assets")) if isinstance(item, dict)]
    assets = [normalize_asset(item, i) for i, item in enumerate(assets_raw)]
    assets_by_symbol = {asset["symbol"].lower(): asset for asset in assets if asset.get("symbol")}
    oracle_raw = [item for item in listify(raw.get("oracle_scopes")) if isinstance(item, dict)]
    oracle_scopes = [normalize_oracle_scope(item, assets_by_symbol, i) for i, item in enumerate(oracle_raw)]
    objective_raw = raw.get("objective", {})
    if isinstance(objective_raw, str):
        objective = {"question": objective_raw}
    elif isinstance(objective_raw, dict):
        objective = dict(objective_raw)
    else:
        objective = {}
    primary_scope = raw.get("primary_scope") or raw.get("scope") or "-".join([asset.get("symbol") or asset["scope_slug"] for asset in assets]) or "workflow"
    normalized = {
        "schema_version": raw.get("schema_version"),
        "command": raw.get("command") or contracts.COMMAND,
        "primary_scope": str(primary_scope),
        "primary_scope_slug": slugify(primary_scope, "workflow"),
        "objective": {
            "question": objective.get("question"),
            "thesis": objective.get("thesis"),
            "requested_decision": objective.get("requested_decision") or "Analyze evidence and propose only non-execution next checks.",
        },
        "assets": assets,
        "oracle_scopes": oracle_scopes,
        "pt_markets": [item for item in listify(raw.get("pt_markets")) if isinstance(item, dict)],
        "social_scopes": [item for item in listify(raw.get("social_scopes")) if isinstance(item, dict)],
        "constraints": listify(raw.get("constraints")),
        "requested_run_root": raw.get("run_root") or raw.get("artifact_root"),
        "source_input": raw.get("_source_input"),
    }
    normalized["blocking_unknowns"] = collect_blocking_unknowns(normalized)
    return normalized


def canonical_input_payload(normalized: dict[str, Any]) -> dict[str, Any]:
    payload = dict(normalized)
    payload.pop("source_input", None)
    return payload


def scenario_analysis_forbidden(normalized: dict[str, Any]) -> bool:
    """Return true when the request explicitly disallows fallback scenarios."""
    objective = normalized.get("objective") or {}
    text_parts = [str(objective.get(key) or "") for key in ("question", "thesis", "requested_decision")]
    text_parts.extend(str(item) for item in normalized.get("constraints") or [])
    request_text = "\n".join(text_parts).lower()
    return any(pattern in request_text for pattern in SCENARIO_DISABLE_PATTERNS)


def input_missing_fields_for_stage(task: dict[str, Any], stage_ref: str) -> set[str]:
    fields: set[str] = set()
    for blocker in task.get("blocking_unknowns") or []:
        if blocker.get("state") != "input_missing":
            continue
        if stage_ref in (blocker.get("required_by") or []):
            fields.add(str(blocker.get("field") or ""))
    return {field for field in fields if field}


def input_sha256(normalized: dict[str, Any]) -> str:
    return hashlib.sha256(stable_json(canonical_input_payload(normalized)).encode("utf-8")).hexdigest()


def validate_input(normalized: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    if normalized.get("schema_version") != contracts.SCHEMA_VERSION:
        findings.append(Finding(
            id="WE_SCHEMA_VERSION",
            severity="P0",
            message="input schema_version is missing or unsupported",
            field="schema_version",
            expected=contracts.SCHEMA_VERSION,
            actual=normalized.get("schema_version"),
            fix_hint="Use schema_version workflow-entrypoint-input-v1.",
        ))
    if normalized.get("command") != contracts.COMMAND:
        findings.append(Finding(
            id="WE_COMMAND",
            severity="P0",
            message="only analyze-propose is supported by this entrypoint slice",
            field="command",
            expected=contracts.COMMAND,
            actual=normalized.get("command"),
        ))
    if not normalized.get("objective", {}).get("question"):
        findings.append(Finding(
            id="WE_OBJECTIVE_QUESTION",
            severity="P0",
            message="objective.question is required",
            field="objective.question",
            fix_hint="State the analysis question the child packets should answer.",
        ))
    if not normalized.get("assets"):
        findings.append(Finding(
            id="WE_ASSETS",
            severity="P0",
            message="assets[] must contain at least one token scope",
            field="assets",
        ))
    else:
        for asset in normalized["assets"]:
            if not asset.get("symbol"):
                findings.append(Finding(
                    id="WE_ASSETS",
                    severity="P0",
                    message="each asset must declare symbol",
                    path=asset.get("artifact_dir") or "assets",
                    field="symbol",
                ))
    if not normalized.get("oracle_scopes"):
        findings.append(Finding(
            id="WE_ORACLE_SCOPE",
            severity="P0",
            message="oracle_scopes[] must contain at least one oracle-analysis scope for analyze-propose",
            field="oracle_scopes",
            fix_hint="Add an oracle scope, even if live feed fields are null and must be filled by a stage packet.",
        ))
    for blocker in normalized.get("blocking_unknowns", []):
        findings.append(Finding(
            id="WE_LIVE_FIELD_MISSING",
            severity="P2",
            message=f"live input missing: {blocker['scope_id']}.{blocker['field']}",
            path=blocker["scope_id"],
            field=blocker["field"],
            fix_hint=blocker["next_step"],
        ))
    if normalized.get("requested_run_root"):
        requested = Path(str(normalized["requested_run_root"]))
        if not requested.is_absolute():
            requested = REPO_ROOT / requested
        try:
            ensure_under(requested, DEV_IMPLEMENTATION, "run_root")
        except WorkflowInputError as exc:
            findings.extend(exc.findings)
    return findings


def fatal_findings(findings: list[Finding]) -> list[Finding]:
    return [item for item in findings if item.id in contracts.INPUT_FATAL_ERROR_IDS]


def resolve_run_root(normalized: dict[str, Any], explicit_run_root: str | None) -> Path:
    if explicit_run_root:
        candidate = Path(explicit_run_root).expanduser()
    elif normalized.get("requested_run_root"):
        candidate = Path(str(normalized["requested_run_root"])).expanduser()
    else:
        sha8 = input_sha256(normalized)[:8]
        candidate = DEV_IMPLEMENTATION / f"analyze-propose-{normalized['primary_scope_slug']}-{sha8}"
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate
    return ensure_under(candidate, DEV_IMPLEMENTATION, "run_root")


def format_template(value: str, scope: dict[str, Any]) -> str:
    return value.format(scope_slug=scope.get("scope_slug", "run"), scope_id=scope.get("scope_id", "run"))


def workflow_manifest(workflow_key: str) -> dict[str, Any]:
    return json.loads(WORKFLOW_MANIFEST_PATHS[workflow_key].read_text())


def workflow_graph_sources() -> dict[str, dict[str, Any]]:
    sources: dict[str, dict[str, Any]] = {}
    for workflow_key in ("asset", "oracle"):
        manifest = workflow_manifest(workflow_key)
        parallel_groups_by_stage: dict[str, dict[str, Any]] = {}
        for group in manifest.get("parallel_groups", []):
            for stage_id in group.get("stages", []):
                parallel_groups_by_stage[stage_id] = group
        serial_groups_by_stage: dict[str, dict[str, Any]] = {}
        for group in manifest.get("serial_groups", []):
            for stage_id in group.get("stages", []):
                serial_groups_by_stage[stage_id] = group
        sources[workflow_key] = {
            "manifest_path": repo_relative(WORKFLOW_MANIFEST_PATHS[workflow_key]),
            "subagent_prompts_path": join_posix(manifest.get("workflow_dir", ""), "subagent-prompts.md"),
            "artifact_return_contract": (manifest.get("artifact_layout") or {}).get("return_contract"),
            "subagent_output_policy": (manifest.get("global_rules") or {}).get("subagent_output_policy"),
            "stages": {stage["id"]: stage for stage in manifest.get("stages", [])},
            "parallel_groups_by_stage": parallel_groups_by_stage,
            "serial_groups_by_stage": serial_groups_by_stage,
        }
    return sources


def join_posix(*parts: str) -> str:
    return "/".join(str(part).strip("/") for part in parts if str(part).strip("/"))


def parent_posix(path: str) -> str:
    cleaned = path.rstrip("/")
    if "/" not in cleaned:
        return cleaned
    return cleaned.rsplit("/", 1)[0]


def posix_is_under(path: str, root: str) -> bool:
    clean_path = path.rstrip("/")
    clean_root = root.rstrip("/")
    return clean_path == clean_root or clean_path.startswith(f"{clean_root}/")


def task_child_root_relative(plan: dict[str, Any], task: dict[str, Any]) -> str:
    run_root = plan["run_root"].rstrip("/")
    child_root = task["child_run_root"].rstrip("/")
    prefix = f"{run_root}/"
    if child_root.startswith(prefix):
        return child_root[len(prefix):]
    return child_root


def task_run_relative_path(plan: dict[str, Any], task: dict[str, Any], rel_path: str) -> str:
    return join_posix(task_child_root_relative(plan, task), rel_path)


def normalized_parallel_unit(workflow_key: str, raw_unit: str | None) -> str:
    text = (raw_unit or "").lower()
    if workflow_key == "asset" and "token" in text:
        return "token"
    if "pt" in text:
        return "pt_market"
    if "social" in text:
        return "social_scope"
    if "source primitive" in text:
        return "source_primitive_candidate"
    if workflow_key == "oracle" and ("feed" in text or "asset" in text or "token" in text):
        return "oracle_scope"
    return "run"


def artifact_write_scope(plan: dict[str, Any], task: dict[str, Any]) -> dict[str, Any]:
    required_outputs = [task_run_relative_path(plan, task, path) for path in task.get("required_outputs", [])]
    read_roots = [task_run_relative_path(plan, task, path) for path in task.get("input_paths", [])]
    write_roots: list[str] = []
    artifact_root = task_run_relative_path(plan, task, task.get("artifact_dir") or "")
    if artifact_root:
        write_roots.append(artifact_root)
    for output in required_outputs:
        output_root = output if output.endswith("/") else parent_posix(output)
        if not any(posix_is_under(output_root, root) for root in write_roots):
            write_roots.append(output_root)
    return {
        "mode": "exclusive_prefixes",
        "write_roots": sorted(dict.fromkeys(write_roots)),
        "required_outputs": required_outputs,
        "shared_write_roots": [],
        "read_roots": read_roots,
    }


def subagent_prompt_reference(workflow_key: str, stage_id: str, source: dict[str, Any]) -> dict[str, str] | None:
    section = SUBAGENT_PROMPT_SECTIONS.get((workflow_key, stage_id))
    path = source.get("subagent_prompts_path")
    if not section or not path:
        return None
    return {
        "path": path,
        "section": section,
        "return_contract_section": SUBAGENT_RETURN_CONTRACT_SECTION,
    }


def stage_worker_return_contract(task: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    prompts_path = source.get("subagent_prompts_path")
    return {
        "contract_id": "stage-worker-compressed-handoff-v1",
        "reference": None if not prompts_path else {
            "path": prompts_path,
            "section": SUBAGENT_RETURN_CONTRACT_SECTION,
        },
        "required_fields": ["status", "artifact_paths", "validation_status", "blockers", "commands_run"],
        "artifact_paths": task.get("required_outputs", []),
        "artifact_layout_return_contract": source.get("artifact_return_contract"),
        "parent_verification_required": True,
        "worker_self_report_is_advisory": True,
    }


def write_scopes_conflict(left: dict[str, Any], right: dict[str, Any]) -> bool:
    for left_root in left.get("write_roots", []):
        for right_root in right.get("write_roots", []):
            if posix_is_under(left_root, right_root) or posix_is_under(right_root, left_root):
                return True
    return False


def select_dependency_tasks(task: dict[str, Any], candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if task.get("scope_type") == "run":
        return candidates
    same_scope = [candidate for candidate in candidates if candidate.get("scope_id") == task.get("scope_id")]
    if same_scope:
        return same_scope
    run_scope = [candidate for candidate in candidates if candidate.get("scope_type") == "run"]
    return run_scope or candidates


def build_execution_graph(plan: dict[str, Any]) -> dict[str, Any]:
    sources = workflow_graph_sources()
    tasks = plan["tasks"]
    tasks_by_stage: dict[tuple[str, str], list[dict[str, Any]]] = {}
    task_by_id = {task["task_id"]: task for task in tasks}
    for task in tasks:
        tasks_by_stage.setdefault((task["workflow_key"], task["stage_id"]), []).append(task)

    skipped_by_workflow_stage = {(item["workflow"], item["stage_id"]): item for item in plan.get("skipped_stages", [])}
    nodes: list[dict[str, Any]] = []
    dependency_edges: list[dict[str, str]] = []
    for index, task in enumerate(tasks):
        workflow_key = task["workflow_key"]
        source = sources[workflow_key]
        stage = source["stages"].get(task["stage_id"], {})
        depends_on = stage.get("depends_on")
        dependency_task_ids: list[str] = []
        skipped_dependencies: list[dict[str, str]] = []
        serial_fallback_reason = None
        if depends_on is None:
            if index:
                dependency_task_ids.append(tasks[index - 1]["task_id"])
            serial_fallback_reason = "Source stage lacks explicit depends_on metadata; safe fallback is previous registry packet."
        else:
            for dependency_stage_id in depends_on:
                candidates = tasks_by_stage.get((workflow_key, dependency_stage_id), [])
                selected = select_dependency_tasks(task, candidates)
                if selected:
                    dependency_task_ids.extend(candidate["task_id"] for candidate in selected)
                elif (workflow_key, dependency_stage_id) in skipped_by_workflow_stage:
                    skipped = skipped_by_workflow_stage[(workflow_key, dependency_stage_id)]
                    skipped_dependencies.append({"stage_id": dependency_stage_id, "reason": skipped.get("reason", "stage skipped by input shape")})
                else:
                    skipped_dependencies.append({"stage_id": dependency_stage_id, "reason": "dependency stage has no scaffold-time packet"})
        dependency_task_ids = list(dict.fromkeys(dependency_task_ids))
        for dependency_task_id in dependency_task_ids:
            dependency_edges.append({"from_task_id": dependency_task_id, "to_task_id": task["task_id"], "type": "depends_on"})

        parallelization = stage.get("parallelization") or {}
        source_group = source["parallel_groups_by_stage"].get(task["stage_id"])
        serial_group = source["serial_groups_by_stage"].get(task["stage_id"])
        explicit_safety_reason = parallelization.get("reason")
        parallel_unit = normalized_parallel_unit(workflow_key, (source_group or {}).get("parallel_unit") or parallelization.get("unit"))
        scope = artifact_write_scope(plan, task)
        parallel_safe = bool(parallelization.get("parallelizable") and explicit_safety_reason and task.get("scope_type") != "run")
        parallel_group_id = f"{workflow_key}.{task['stage_id']}.{parallel_unit}" if parallel_safe else None
        recommended_max_concurrent = 1
        if parallel_safe:
            recommended_max_concurrent = max(1, int(parallelization.get("recommended_max_concurrent") or 1))
        delegate_to_subagent = bool(parallel_safe and stage.get("delegate_to_subagent"))
        prompt_reference = subagent_prompt_reference(workflow_key, task["stage_id"], source) if delegate_to_subagent else None
        return_contract = stage_worker_return_contract(task, source)
        safety_rationale = explicit_safety_reason or serial_fallback_reason or "Serial fallback: source workflow lacks an explicit parallel safety reason for this scaffold-time packet."
        dependency_required_artifacts: list[str] = []
        for dependency_task_id in dependency_task_ids:
            dependency_task = task_by_id[dependency_task_id]
            dependency_required_artifacts.extend(task_run_relative_path(plan, dependency_task, path) for path in dependency_task.get("required_outputs", []))
        node = {
            "task_id": task["task_id"],
            "workflow_key": workflow_key,
            "workflow_id": task["workflow_id"],
            "stage_id": task["stage_id"],
            "stage_title": task["stage_title"],
            "scope_type": task["scope_type"],
            "scope_id": task.get("scope_id"),
            "scope_slug": task.get("scope_slug"),
            "registry_index": index,
            "packet_json": task["packet_json"],
            "packet_markdown": task["packet_markdown"],
            "depends_on_task_ids": dependency_task_ids,
            "dependency_edges": [{"from_task_id": dependency_task_id, "to_task_id": task["task_id"]} for dependency_task_id in dependency_task_ids],
            "skipped_stage_dependencies": skipped_dependencies,
            "parallel_group_id": parallel_group_id,
            "source_parallel_group_id": None if not source_group else source_group.get("id"),
            "serial_section_id": None if not serial_group else f"{workflow_key}.{serial_group.get('id')}",
            "parallel_unit": parallel_unit,
            "delegate_to_subagent": delegate_to_subagent,
            "subagent_prompt_reference": prompt_reference,
            "recommended_max_concurrent": recommended_max_concurrent,
            "return_contract": return_contract,
            "artifact_write_scope": scope,
            "ready_after_validation": {
                "type": "none" if not dependency_task_ids else "dependency_artifacts",
                "required_task_ids": dependency_task_ids,
                "required_artifacts": dependency_required_artifacts,
                "required_statuses": [],
            },
            "blocking_unknowns": task.get("blocking_unknowns", []),
            "safety_rationale": safety_rationale,
        }
        blocked_reasons: list[str] = []
        if dependency_task_ids:
            blocked_reasons.append("waiting_on_dependencies")
        if task.get("blocking_unknowns"):
            blocked_reasons.append("blocking_unknowns")
        if not parallel_safe and index != 0:
            blocked_reasons.append("serial_fallback")
        if skipped_dependencies:
            node["skipped_dependency_policy"] = "skipped dependencies are recorded as satisfied-by-input-shape and never become dangling task ids"
        node["missing_artifacts"] = dependency_required_artifacts if dependency_task_ids else []
        node["scaffold_state"] = "ready" if not blocked_reasons else "blocked"
        node["ready_reason"] = "No upstream packet dependency, no packet-level blockers, and exclusive artifact write scope."
        node["blocked_reasons"] = blocked_reasons
        node["blocked_reason"] = "; ".join(blocked_reasons) if blocked_reasons else ""
        nodes.append(node)

    selected_ready: list[dict[str, Any]] = []
    group_counts: dict[str, int] = {}
    for node in nodes:
        if node["scaffold_state"] != "ready":
            continue
        group_id = node.get("parallel_group_id") or node["task_id"]
        if group_counts.get(group_id, 0) >= node["recommended_max_concurrent"]:
            node["scaffold_state"] = "blocked"
            node["blocked_reasons"].append("recommended_max_concurrent")
            node["blocked_reason"] = "; ".join(node["blocked_reasons"])
            continue
        if any(write_scopes_conflict(node["artifact_write_scope"], ready["artifact_write_scope"]) for ready in selected_ready):
            node["scaffold_state"] = "blocked"
            node["blocked_reasons"].append("write_scope_conflict")
            node["blocked_reason"] = "; ".join(node["blocked_reasons"])
            continue
        selected_ready.append(node)
        group_counts[group_id] = group_counts.get(group_id, 0) + 1

    parallel_groups: dict[str, dict[str, Any]] = {}
    serial_sections: dict[str, dict[str, Any]] = {}
    for node in nodes:
        if node.get("parallel_group_id"):
            group = parallel_groups.setdefault(node["parallel_group_id"], {
                "parallel_group_id": node["parallel_group_id"],
                "source_parallel_group_id": node.get("source_parallel_group_id"),
                "parallel_unit": node["parallel_unit"],
                "task_ids": [],
                "recommended_max_concurrent": node["recommended_max_concurrent"],
                "artifact_write_scope_policy": "disjoint_write_roots_required",
                "artifact_write_scope": {"mode": "exclusive_prefixes", "write_roots": [], "required_outputs": [], "shared_write_roots": []},
                "delegate_to_subagent": node["delegate_to_subagent"],
                "subagent_prompt_reference": node["subagent_prompt_reference"],
                "safety_rationale": node["safety_rationale"],
            })
            group["task_ids"].append(node["task_id"])
            group["artifact_write_scope"]["write_roots"].extend(node["artifact_write_scope"].get("write_roots", []))
            group["artifact_write_scope"]["required_outputs"].extend(node["artifact_write_scope"].get("required_outputs", []))
            group["artifact_write_scope"]["write_roots"] = sorted(dict.fromkeys(group["artifact_write_scope"]["write_roots"]))
            group["artifact_write_scope"]["required_outputs"] = sorted(dict.fromkeys(group["artifact_write_scope"]["required_outputs"]))
        else:
            section_id = node.get("serial_section_id") or f"{node['workflow_key']}.{node['stage_id']}.serial"
            section = serial_sections.setdefault(section_id, {"id": section_id, "task_ids": [], "reason": node["safety_rationale"]})
            section["task_ids"].append(node["task_id"])

    return {
        "schema_version": contracts.EXECUTION_GRAPH_SCHEMA_VERSION,
        "command": contracts.COMMAND,
        "run_root": plan["run_root"],
        "input_sha256": plan["input_sha256"],
        "plan_schema_version": contracts.PLAN_SCHEMA_VERSION,
        "packet_schema_version": contracts.PACKET_SCHEMA_VERSION,
        "registry_source": ".workflow/registry.json",
        "graph_status": "metadata_only",
        "fallback_behavior": "serial_registry_order",
        "manifest_sources": {workflow_key: source["manifest_path"] for workflow_key, source in sources.items()},
        "tasks": nodes,
        "dependency_edges": dependency_edges,
        "ready_packets": [node["task_id"] for node in nodes if node["scaffold_state"] == "ready"],
        "blocked_packets": [node["task_id"] for node in nodes if node["scaffold_state"] == "blocked"],
        "parallel_groups": list(parallel_groups.values()),
        "serial_sections": list(serial_sections.values()),
        "compatibility": {
            "first_packet_preserved": True,
            "legacy_serial_registry_supported": True,
            "validators_require_execution_graph": False,
            "proposal_gate_requires_execution_graph": False,
        },
        "non_goals": ["scheduler", "subagent_launch", "worker_queue", "preview_or_execute_gate_changes"],
    }


def execution_graph_finding(
    finding_id: str,
    severity: str,
    *,
    path: str,
    field: str,
    message: str,
    expected: str | None = None,
    actual: str | None = None,
    fix_hint: str | None = None,
) -> dict[str, Any]:
    finding = {
        "id": finding_id,
        "severity": severity,
        "workflow": contracts.EXECUTION_GRAPH_SCHEMA_VERSION,
        "source_workflow": "execution_graph",
        "path": path,
        "field": field,
        "message": message,
    }
    if expected is not None:
        finding["expected"] = expected
    if actual is not None:
        finding["actual"] = actual
    if fix_hint is not None:
        finding["fix_hint"] = fix_hint
    return finding


def _json_preview(value: Any) -> str:
    try:
        rendered = json.dumps(value, ensure_ascii=False, sort_keys=True)
    except TypeError:
        rendered = repr(value)
    if len(rendered) > 240:
        return rendered[:237] + "..."
    return rendered


def _graph_reference_list(
    findings: list[dict[str, Any]],
    graph_path: str,
    task_ids: set[str],
    value: Any,
    *,
    field: str,
    finding_id: str,
) -> list[str]:
    if not isinstance(value, list):
        findings.append(
            execution_graph_finding(
                "execution_graph.field.type",
                "P0",
                path=graph_path,
                field=field,
                expected="list of task IDs",
                actual=type(value).__name__,
                message=f"execution graph field {field} must be a list of task IDs",
                fix_hint="Regenerate the workflow scaffold so graph references are emitted as arrays of task_id strings.",
            )
        )
        return []
    refs: list[str] = []
    for index, item in enumerate(value):
        item_field = f"{field}[{index}]"
        if not isinstance(item, str):
            findings.append(
                execution_graph_finding(
                    "execution_graph.reference.type",
                    "P0",
                    path=graph_path,
                    field=item_field,
                    expected="task_id string",
                    actual=type(item).__name__,
                    message=f"execution graph reference {item_field} is not a task_id string",
                    fix_hint="Regenerate the graph; task references must be stable string IDs.",
                )
            )
            continue
        refs.append(item)
        if item not in task_ids:
            findings.append(
                execution_graph_finding(
                    finding_id,
                    "P0",
                    path=graph_path,
                    field=item_field,
                    expected="known task_id from execution_graph.tasks",
                    actual=item,
                    message=f"execution graph references unknown task ID {item!r}",
                    fix_hint="Regenerate the graph or remove stale task references so every edge/list item points to an emitted task.",
                )
            )
    return refs


def _graph_write_conflicts(nodes: list[dict[str, Any]]) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    conflicts: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for index, left in enumerate(nodes):
        left_scope = left.get("artifact_write_scope")
        if not isinstance(left_scope, dict):
            continue
        for right in nodes[index + 1:]:
            right_scope = right.get("artifact_write_scope")
            if isinstance(right_scope, dict) and write_scopes_conflict(left_scope, right_scope):
                conflicts.append((left, right))
    return conflicts


def _graph_cycle(edges: list[tuple[str, str]], task_ids: set[str]) -> list[str] | None:
    adjacency: dict[str, list[str]] = {task_id: [] for task_id in task_ids}
    for source, target in sorted(set(edges)):
        adjacency.setdefault(source, []).append(target)
    state: dict[str, str] = {}
    stack: list[str] = []

    def visit(task_id: str) -> list[str] | None:
        state[task_id] = "visiting"
        stack.append(task_id)
        for target in adjacency.get(task_id, []):
            if state.get(target) == "visiting":
                return stack[stack.index(target):] + [target]
            if state.get(target) is None:
                cycle = visit(target)
                if cycle:
                    return cycle
        stack.pop()
        state[task_id] = "visited"
        return None

    for task_id in sorted(task_ids):
        if state.get(task_id) is None:
            cycle = visit(task_id)
            if cycle:
                return cycle
    return None


def _execution_graph_status(findings: list[dict[str, Any]]) -> str:
    counts = count_findings(findings)
    if counts["P0"]:
        return "blocked"
    if counts["P1"]:
        return "review_required"
    if counts["P2"]:
        return "warning"
    return "pass"


def validate_execution_graph(plan: dict[str, Any], run_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    graph_file = run_root / ".workflow" / "execution-graph.json"
    graph_path = repo_relative(graph_file)
    diagnostics: dict[str, Any] = {
        "path": graph_path,
        "expected_schema_version": contracts.EXECUTION_GRAPH_SCHEMA_VERSION,
        "schema_version": None,
        "status": "absent_legacy",
        "checked": False,
        "skipped_reason": "execution graph file absent; legacy validation path preserved",
        "task_count": 0,
        "ready_packet_count": 0,
        "finding_counts": {"P0": 0, "P1": 0, "P2": 0, "total": 0},
        "findings": [],
    }
    findings: list[dict[str, Any]] = []
    if not graph_file.exists():
        return diagnostics, findings
    diagnostics["skipped_reason"] = None
    try:
        graph = json.loads(graph_file.read_text())
    except json.JSONDecodeError as exc:
        findings.append(
            execution_graph_finding(
                "execution_graph.json_valid",
                "P0",
                path=graph_path,
                field=".",
                expected="parseable JSON object",
                actual=f"{exc.msg} at line {exc.lineno} column {exc.colno}",
                message=".workflow/execution-graph.json is not parseable JSON",
                fix_hint="Regenerate the workflow scaffold or fix the JSON before using graph-aware validation.",
            )
        )
        diagnostics.update({"status": _execution_graph_status(findings), "finding_counts": count_findings(findings), "findings": findings})
        return diagnostics, findings
    if not isinstance(graph, dict):
        findings.append(
            execution_graph_finding(
                "execution_graph.object",
                "P0",
                path=graph_path,
                field=".",
                expected="JSON object",
                actual=type(graph).__name__,
                message=".workflow/execution-graph.json must contain a JSON object",
                fix_hint="Regenerate the workflow scaffold so the execution graph uses the v1 object schema.",
            )
        )
        diagnostics.update({"status": _execution_graph_status(findings), "finding_counts": count_findings(findings), "findings": findings})
        return diagnostics, findings

    schema_version = graph.get("schema_version")
    diagnostics["schema_version"] = schema_version
    if schema_version != contracts.EXECUTION_GRAPH_SCHEMA_VERSION:
        findings.append(
            execution_graph_finding(
                "execution_graph.schema_version",
                "P2",
                path=graph_path,
                field="schema_version",
                expected=contracts.EXECUTION_GRAPH_SCHEMA_VERSION,
                actual=_json_preview(schema_version),
                message="execution graph schema is missing or unknown; graph-specific blockers are skipped for compatibility",
                fix_hint="Regenerate the run with the current entrypoint before relying on graph diagnostics.",
            )
        )
        diagnostics.update({
            "status": _execution_graph_status(findings),
            "checked": False,
            "skipped_reason": "unknown graph schema; legacy validation path preserved",
            "finding_counts": count_findings(findings),
            "findings": findings,
        })
        return diagnostics, findings

    diagnostics["checked"] = True
    for key in EXECUTION_GRAPH_REQUIRED_TOP_LEVEL_KEYS:
        if key not in graph:
            findings.append(
                execution_graph_finding(
                    "execution_graph.required_field",
                    "P0",
                    path=graph_path,
                    field=key,
                    expected="required v1 graph field present",
                    actual="missing",
                    message=f"execution graph is missing required field {key!r}",
                    fix_hint="Regenerate .workflow/execution-graph.json from the current entrypoint.",
                )
            )
    for key in EXECUTION_GRAPH_REQUIRED_LIST_FIELDS:
        if key in graph and not isinstance(graph.get(key), list):
            findings.append(
                execution_graph_finding(
                    "execution_graph.field.type",
                    "P0",
                    path=graph_path,
                    field=key,
                    expected="list",
                    actual=type(graph.get(key)).__name__,
                    message=f"execution graph field {key!r} must be a list",
                    fix_hint="Regenerate the graph so collection fields use stable arrays.",
                )
            )

    raw_tasks = graph.get("tasks")
    if not isinstance(raw_tasks, list):
        diagnostics.update({"status": _execution_graph_status(findings), "finding_counts": count_findings(findings), "findings": findings})
        return diagnostics, findings

    task_by_id: dict[str, dict[str, Any]] = {}
    dependency_edges: list[tuple[str, str]] = []
    for index, task in enumerate(raw_tasks):
        field_prefix = f"tasks[{index}]"
        if not isinstance(task, dict):
            findings.append(
                execution_graph_finding(
                    "execution_graph.task.object",
                    "P0",
                    path=graph_path,
                    field=field_prefix,
                    expected="task object",
                    actual=type(task).__name__,
                    message="execution graph task entries must be objects",
                    fix_hint="Regenerate the graph so every task entry carries full packet metadata.",
                )
            )
            continue
        task_id = task.get("task_id")
        if not isinstance(task_id, str) or not task_id:
            findings.append(
                execution_graph_finding(
                    "execution_graph.task.task_id",
                    "P0",
                    path=graph_path,
                    field=f"{field_prefix}.task_id",
                    expected="non-empty task_id string",
                    actual=_json_preview(task_id),
                    message="execution graph task is missing a stable task_id string",
                    fix_hint="Regenerate the graph; task IDs are the key used for dependency validation.",
                )
            )
            continue
        if task_id in task_by_id:
            findings.append(
                execution_graph_finding(
                    "execution_graph.task.duplicate_task_id",
                    "P0",
                    path=graph_path,
                    field=f"{field_prefix}.task_id",
                    expected="unique task_id",
                    actual=task_id,
                    message=f"execution graph task ID {task_id!r} appears more than once",
                    fix_hint="Regenerate the graph so each packet has one canonical node.",
                )
            )
        task_by_id[task_id] = task
        for key in EXECUTION_GRAPH_REQUIRED_TASK_KEYS:
            if key not in task:
                findings.append(
                    execution_graph_finding(
                        "execution_graph.task.required_field",
                        "P0",
                        path=graph_path,
                        field=f"tasks.{task_id}.{key}",
                        expected="required v1 task field present",
                        actual="missing",
                        message=f"execution graph task {task_id!r} is missing required field {key!r}",
                        fix_hint="Regenerate .workflow/execution-graph.json from the current entrypoint.",
                    )
                )
        if "artifact_write_scope" in task and not isinstance(task.get("artifact_write_scope"), dict):
            findings.append(
                execution_graph_finding(
                    "execution_graph.task.field_type",
                    "P0",
                    path=graph_path,
                    field=f"tasks.{task_id}.artifact_write_scope",
                    expected="object with write_roots list",
                    actual=type(task.get("artifact_write_scope")).__name__,
                    message=f"execution graph task {task_id!r} has invalid artifact_write_scope",
                    fix_hint="Regenerate the graph so write-scope collision checks can run deterministically.",
                )
            )
        elif isinstance(task.get("artifact_write_scope"), dict) and not isinstance(task["artifact_write_scope"].get("write_roots", []), list):
            findings.append(
                execution_graph_finding(
                    "execution_graph.task.field_type",
                    "P0",
                    path=graph_path,
                    field=f"tasks.{task_id}.artifact_write_scope.write_roots",
                    expected="list",
                    actual=type(task["artifact_write_scope"].get("write_roots")).__name__,
                    message=f"execution graph task {task_id!r} has invalid write_roots",
                    fix_hint="Regenerate the graph so write-scope collision checks can run deterministically.",
                )
            )
        if "scaffold_state" in task and task.get("scaffold_state") not in {"ready", "blocked"}:
            findings.append(
                execution_graph_finding(
                    "execution_graph.task.scaffold_state",
                    "P0",
                    path=graph_path,
                    field=f"tasks.{task_id}.scaffold_state",
                    expected="ready or blocked",
                    actual=_json_preview(task.get("scaffold_state")),
                    message=f"execution graph task {task_id!r} has an unknown scaffold_state",
                    fix_hint="Regenerate the graph so next-action readiness can be trusted.",
                )
            )
        if "recommended_max_concurrent" in task and (not isinstance(task.get("recommended_max_concurrent"), int) or task.get("recommended_max_concurrent", 0) < 1):
            findings.append(
                execution_graph_finding(
                    "execution_graph.task.recommended_max_concurrent",
                    "P0",
                    path=graph_path,
                    field=f"tasks.{task_id}.recommended_max_concurrent",
                    expected="positive integer",
                    actual=_json_preview(task.get("recommended_max_concurrent")),
                    message=f"execution graph task {task_id!r} has invalid concurrency metadata",
                    fix_hint="Regenerate the graph so advisory parallel waves have bounded concurrency.",
                )
            )

    task_ids = set(task_by_id)
    diagnostics["task_count"] = len(task_by_id)
    expected_task_ids = {task.get("task_id") for task in plan.get("tasks", []) if isinstance(task, dict) and isinstance(task.get("task_id"), str)}
    if expected_task_ids:
        missing_from_graph = sorted(expected_task_ids - task_ids)
        extra_in_graph = sorted(task_ids - expected_task_ids)
        if missing_from_graph or extra_in_graph:
            findings.append(
                execution_graph_finding(
                    "execution_graph.plan.task_mismatch",
                    "P0",
                    path=graph_path,
                    field="tasks",
                    expected="same task IDs as .workflow/plan.json",
                    actual=f"missing={missing_from_graph}; extra={extra_in_graph}",
                    message="execution graph task IDs do not match the plan task registry",
                    fix_hint="Regenerate the run so plan.json, tasks.json, registry.json, and execution-graph.json share one task registry.",
                )
            )

    for task_id, task in task_by_id.items():
        if "depends_on_task_ids" in task:
            deps = _graph_reference_list(
                findings,
                graph_path,
                task_ids,
                task.get("depends_on_task_ids"),
                field=f"tasks.{task_id}.depends_on_task_ids",
                finding_id="execution_graph.task.unknown_dependency_task_id",
            )
            dependency_edges.extend((dep, task_id) for dep in deps if dep in task_ids)
        ready_after = task.get("ready_after_validation")
        if "ready_after_validation" in task and not isinstance(ready_after, dict):
            findings.append(
                execution_graph_finding(
                    "execution_graph.task.field_type",
                    "P0",
                    path=graph_path,
                    field=f"tasks.{task_id}.ready_after_validation",
                    expected="object",
                    actual=type(ready_after).__name__,
                    message=f"execution graph task {task_id!r} has invalid ready_after_validation metadata",
                    fix_hint="Regenerate the graph so blocked packets name concrete unlock conditions.",
                )
            )
        elif isinstance(ready_after, dict) and "required_task_ids" in ready_after:
            _graph_reference_list(
                findings,
                graph_path,
                task_ids,
                ready_after.get("required_task_ids"),
                field=f"tasks.{task_id}.ready_after_validation.required_task_ids",
                finding_id="execution_graph.task.unknown_ready_after_task_id",
            )

    if isinstance(graph.get("dependency_edges"), list):
        for index, edge in enumerate(graph.get("dependency_edges", [])):
            field_prefix = f"dependency_edges[{index}]"
            if not isinstance(edge, dict):
                findings.append(
                    execution_graph_finding(
                        "execution_graph.edge.object",
                        "P0",
                        path=graph_path,
                        field=field_prefix,
                        expected="dependency edge object",
                        actual=type(edge).__name__,
                        message="execution graph dependency_edges entries must be objects",
                        fix_hint="Regenerate the graph so dependency edges carry from_task_id and to_task_id.",
                    )
                )
                continue
            source = edge.get("from_task_id")
            target = edge.get("to_task_id")
            for key, value in (("from_task_id", source), ("to_task_id", target)):
                if not isinstance(value, str):
                    findings.append(
                        execution_graph_finding(
                            "execution_graph.edge.required_field",
                            "P0",
                            path=graph_path,
                            field=f"{field_prefix}.{key}",
                            expected="known task_id string",
                            actual=_json_preview(value),
                            message=f"execution graph edge {field_prefix} has invalid {key}",
                            fix_hint="Regenerate the graph so every edge endpoint points at a task_id.",
                        )
                    )
                elif value not in task_ids:
                    findings.append(
                        execution_graph_finding(
                            "execution_graph.edge.unknown_task_id",
                            "P0",
                            path=graph_path,
                            field=f"{field_prefix}.{key}",
                            expected="known task_id from execution_graph.tasks",
                            actual=value,
                            message=f"execution graph edge references unknown task ID {value!r}",
                            fix_hint="Regenerate the graph or remove stale edge endpoints.",
                        )
                    )
            if isinstance(source, str) and isinstance(target, str) and source in task_ids and target in task_ids:
                dependency_edges.append((source, target))

    ready_ids = _graph_reference_list(
        findings,
        graph_path,
        task_ids,
        graph.get("ready_packets", []),
        field="ready_packets",
        finding_id="execution_graph.ready_packets.unknown_task_id",
    ) if "ready_packets" in graph else []
    blocked_ids = _graph_reference_list(
        findings,
        graph_path,
        task_ids,
        graph.get("blocked_packets", []),
        field="blocked_packets",
        finding_id="execution_graph.blocked_packets.unknown_task_id",
    ) if "blocked_packets" in graph else []
    diagnostics["ready_packet_count"] = len([task_id for task_id in ready_ids if task_id in task_ids])
    duplicate_state_ids = sorted(set(ready_ids).intersection(blocked_ids))
    if duplicate_state_ids:
        findings.append(
            execution_graph_finding(
                "execution_graph.packet_state.duplicate",
                "P0",
                path=graph_path,
                field="ready_packets/blocked_packets",
                expected="task IDs appear in exactly one readiness list",
                actual=", ".join(duplicate_state_ids),
                message="execution graph lists the same task as both ready and blocked",
                fix_hint="Regenerate the graph so task readiness has one canonical state.",
            )
        )

    ready_nodes = [task_by_id[task_id] for task_id in ready_ids if task_id in task_by_id]
    for node in ready_nodes:
        task_id = node["task_id"]
        if node.get("scaffold_state") != "ready":
            findings.append(
                execution_graph_finding(
                    "execution_graph.ready_packets.state_mismatch",
                    "P0",
                    path=graph_path,
                    field=f"tasks.{task_id}.scaffold_state",
                    expected="ready",
                    actual=_json_preview(node.get("scaffold_state")),
                    message=f"ready packet {task_id!r} is not marked ready on its task node",
                    fix_hint="Regenerate the graph so ready_packets is derived from task scaffold_state.",
                )
            )
        if node.get("depends_on_task_ids"):
            findings.append(
                execution_graph_finding(
                    "execution_graph.ready_packets.unsafe_dependency",
                    "P0",
                    path=graph_path,
                    field=f"tasks.{task_id}.depends_on_task_ids",
                    expected="empty for ready packets",
                    actual=_json_preview(node.get("depends_on_task_ids")),
                    message=f"ready packet {task_id!r} still has upstream dependencies",
                    fix_hint="Treat this packet as blocked until dependencies validate; regenerate next-action metadata.",
                )
            )
        unsafe_blockers = []
        for key in ("blocking_unknowns", "missing_artifacts", "blocked_reasons"):
            if node.get(key):
                unsafe_blockers.append(key)
        if unsafe_blockers:
            findings.append(
                execution_graph_finding(
                    "execution_graph.ready_packets.unsafe_blockers",
                    "P0",
                    path=graph_path,
                    field=f"tasks.{task_id}",
                    expected="no blocking_unknowns, missing_artifacts, or blocked_reasons on ready packets",
                    actual=", ".join(unsafe_blockers),
                    message=f"ready packet {task_id!r} still carries blocking metadata",
                    fix_hint="Treat this packet as blocked and regenerate next-action metadata before parallel work.",
                )
            )
    for left, right in _graph_write_conflicts(ready_nodes):
        findings.append(
            execution_graph_finding(
                "execution_graph.ready_packets.write_scope_collision",
                "P0",
                path=graph_path,
                field="ready_packets",
                expected="disjoint artifact_write_scope.write_roots for ready packets",
                actual=f"{left['task_id']} {left.get('artifact_write_scope', {}).get('write_roots', [])} conflicts with {right['task_id']} {right.get('artifact_write_scope', {}).get('write_roots', [])}",
                message="execution graph ready packet wave has colliding write scopes",
                fix_hint="Do not parallelize these packets; regenerate the graph so one conflicting packet is blocked or scopes are disjoint.",
            )
        )

    if isinstance(graph.get("parallel_groups"), list):
        for index, group in enumerate(graph.get("parallel_groups", [])):
            field_prefix = f"parallel_groups[{index}]"
            if not isinstance(group, dict):
                findings.append(
                    execution_graph_finding(
                        "execution_graph.parallel_group.object",
                        "P0",
                        path=graph_path,
                        field=field_prefix,
                        expected="parallel group object",
                        actual=type(group).__name__,
                        message="execution graph parallel_groups entries must be objects",
                        fix_hint="Regenerate the graph so advisory parallel metadata is structured.",
                    )
                )
                continue
            group_ids = _graph_reference_list(
                findings,
                graph_path,
                task_ids,
                group.get("task_ids", []),
                field=f"{field_prefix}.task_ids",
                finding_id="execution_graph.parallel_group.unknown_task_id",
            )
            max_concurrent = group.get("recommended_max_concurrent")
            if not isinstance(max_concurrent, int) or max_concurrent < 1:
                findings.append(
                    execution_graph_finding(
                        "execution_graph.parallel_group.recommended_max_concurrent",
                        "P0",
                        path=graph_path,
                        field=f"{field_prefix}.recommended_max_concurrent",
                        expected="positive integer",
                        actual=_json_preview(max_concurrent),
                        message="execution graph parallel group has invalid concurrency metadata",
                        fix_hint="Regenerate the graph so advisory parallel waves have bounded concurrency.",
                    )
                )
            group_nodes = [task_by_id[task_id] for task_id in group_ids if task_id in task_by_id]
            for left, right in _graph_write_conflicts(group_nodes):
                findings.append(
                    execution_graph_finding(
                        "execution_graph.parallel_group.write_scope_collision",
                        "P0",
                        path=graph_path,
                        field=f"{field_prefix}.task_ids",
                        expected="disjoint artifact_write_scope.write_roots inside parallel groups",
                        actual=f"{left['task_id']} {left.get('artifact_write_scope', {}).get('write_roots', [])} conflicts with {right['task_id']} {right.get('artifact_write_scope', {}).get('write_roots', [])}",
                        message="execution graph parallel group has colliding write scopes",
                        fix_hint="Do not use this group as parallel-safe until the graph is regenerated with disjoint write scopes.",
                    )
                )
            ready_in_group = [task_id for task_id in group_ids if task_id in set(ready_ids)]
            if isinstance(max_concurrent, int) and max_concurrent >= 1 and len(ready_in_group) > max_concurrent:
                findings.append(
                    execution_graph_finding(
                        "execution_graph.parallel_group.unsafe_concurrency",
                        "P0",
                        path=graph_path,
                        field=f"{field_prefix}.recommended_max_concurrent",
                        expected="ready task count <= recommended_max_concurrent",
                        actual=f"{len(ready_in_group)} ready tasks for max {max_concurrent}: {ready_in_group}",
                        message="execution graph ready wave exceeds group concurrency metadata",
                        fix_hint="Reduce the advisory ready wave or regenerate graph metadata so max concurrency is honored.",
                    )
                )

    if isinstance(graph.get("serial_sections"), list):
        for index, section in enumerate(graph.get("serial_sections", [])):
            field_prefix = f"serial_sections[{index}]"
            if not isinstance(section, dict):
                findings.append(
                    execution_graph_finding(
                        "execution_graph.serial_section.object",
                        "P0",
                        path=graph_path,
                        field=field_prefix,
                        expected="serial section object",
                        actual=type(section).__name__,
                        message="execution graph serial_sections entries must be objects",
                        fix_hint="Regenerate the graph so serial fallback metadata is structured.",
                    )
                )
                continue
            _graph_reference_list(
                findings,
                graph_path,
                task_ids,
                section.get("task_ids", []),
                field=f"{field_prefix}.task_ids",
                finding_id="execution_graph.serial_section.unknown_task_id",
            )

    cycle = _graph_cycle(dependency_edges, task_ids)
    if cycle:
        findings.append(
            execution_graph_finding(
                "execution_graph.dependencies.cycle",
                "P0",
                path=graph_path,
                field="dependency_edges",
                expected="acyclic dependency graph",
                actual=" -> ".join(cycle),
                message="execution graph contains a dependency cycle",
                fix_hint="Fix stage dependency metadata or regenerate the graph before unlocking downstream packets.",
            )
        )

    diagnostics.update({
        "status": _execution_graph_status(findings),
        "finding_counts": count_findings(findings),
        "findings": findings,
    })
    return diagnostics, findings


def build_plan(normalized: dict[str, Any], run_root: Path) -> dict[str, Any]:
    sha = input_sha256(normalized)
    asset_root = run_root / contracts.CHILD_DIRECTORIES["asset"]
    oracle_root = run_root / contracts.CHILD_DIRECTORIES["oracle"]
    run_root_rel = repo_relative(run_root)
    tasks: list[dict[str, Any]] = []

    for asset in normalized["assets"]:
        for stage_id, stage in contracts.ASSET_STAGES.items():
            if stage["scope"] != "asset":
                continue
            tasks.append(task_from_stage("asset", stage_id, stage, asset, asset_root, normalized))
    for stage_id, stage in contracts.ASSET_STAGES.items():
        if stage["scope"] == "run":
            tasks.append(task_from_stage("asset", stage_id, stage, {"scope_id": "run", "scope_slug": "run"}, asset_root, normalized))

    for scope in normalized["oracle_scopes"]:
        for stage_id, stage in contracts.ORACLE_STAGES.items():
            tasks.append(task_from_stage("oracle", stage_id, stage, scope, oracle_root, normalized))

    skipped_stages = []
    for input_key, stages in contracts.ASSET_SKIPPED_STAGES_WHEN_EMPTY.items():
        if not normalized.get(input_key):
            skipped_stages.extend({"workflow": "asset", "stage_id": stage, "reason": f"{input_key} is empty in input"} for stage in stages)

    plan = {
        "schema_version": contracts.PLAN_SCHEMA_VERSION,
        "command": contracts.COMMAND,
        "created_at": utc_now(),
        "input_sha256": sha,
        "input_sha8": sha[:8],
        "run_root": run_root_rel,
        "agent_handoff": {
            "markdown": ".workflow/agent-handoff.md",
            "copy_prompt": build_copy_prompt(normalized, run_root_rel),
        },
        "children": {
            "asset": {"workflow": "asset-investment-diligence", "workflow_id": contracts.WORKFLOW_IDS["asset"], "run_root": repo_relative(asset_root)},
            "oracle": {"workflow": "oracle-analysis", "workflow_id": contracts.WORKFLOW_IDS["oracle"], "run_root": repo_relative(oracle_root)},
        },
        "normalized_input_path": ".workflow/input.normalized.json",
        "packet_root": ".workflow/packets",
        "tasks": tasks,
        "skipped_stages": skipped_stages,
        "blocking_unknowns": normalized.get("blocking_unknowns", []),
        "validator_commands": {
            "asset": [part.format(asset_run_root=repo_relative(asset_root), asset_report_dir=repo_relative(asset_root / "verification")) for part in contracts.VALIDATOR_COMMANDS["asset"]],
            "oracle": [part.format(oracle_run_root=repo_relative(oracle_root), oracle_report_dir=repo_relative(oracle_root / "verification")) for part in contracts.VALIDATOR_COMMANDS["oracle"]],
            "combined": [
                part.format(
                    run_root=repo_relative(run_root),
                    combined_report_dir=repo_relative(run_root / "verification"),
                )
                for part in contracts.VALIDATOR_COMMANDS["combined"]
            ],
        },
    }
    plan["execution_graph"] = build_execution_graph(plan)
    return plan


def task_from_stage(workflow_key: str, stage_id: str, stage: dict[str, Any], scope: dict[str, Any], child_root: Path, normalized: dict[str, Any]) -> dict[str, Any]:
    relevant_blockers = []
    scope_id = scope.get("scope_id")
    for blocker in normalized.get("blocking_unknowns", []):
        propagated = set(blocker.get("propagate_to_scope_ids") or [])
        if stage["scope"] == "run" or blocker.get("scope_id") == scope_id or scope_id in propagated:
            relevant_blockers.append(blocker)
    required_outputs = [format_template(path, scope) for path in stage["required_outputs_template"]]
    input_paths = [format_template(path, scope) for path in stage["input_paths_template"]]
    packet_stem = f"{workflow_key}-{stage_id}-{scope.get('scope_slug', 'run')}"
    return {
        "task_id": packet_stem,
        "workflow_key": workflow_key,
        "workflow_id": contracts.WORKFLOW_IDS[workflow_key],
        "child_run_root": repo_relative(child_root),
        "stage_id": stage_id,
        "stage_title": stage["title"],
        "scope_type": stage["scope"],
        "scope_id": scope.get("scope_id"),
        "scope_slug": scope.get("scope_slug"),
        "artifact_dir": format_template(stage["artifact_dir_template"], scope),
        "input_paths": input_paths,
        "required_outputs": required_outputs,
        "blocking_unknowns": relevant_blockers,
        "scenario_analysis_forbidden": scenario_analysis_forbidden(normalized),
        "packet_json": f".workflow/packets/{workflow_key}/{packet_stem}.json",
        "packet_markdown": f".workflow/packets/{workflow_key}/{packet_stem}.md",
        "validation_command": " ".join(build_validation_command(workflow_key, repo_relative(child_root))),
    }


def build_validation_command(workflow_key: str, child_run_root: str) -> list[str]:
    if workflow_key == "asset":
        return [part.format(asset_run_root=child_run_root, asset_report_dir=f"{child_run_root}/verification") for part in contracts.VALIDATOR_COMMANDS["asset"]]
    return [part.format(oracle_run_root=child_run_root, oracle_report_dir=f"{child_run_root}/verification") for part in contracts.VALIDATOR_COMMANDS["oracle"]]


def write_text(path: Path, content: str, written: list[str]) -> None:
    ensure_under(path, DEV_IMPLEMENTATION, repo_relative(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    written.append(repo_relative(path))


def write_json(path: Path, value: Any, written: list[str]) -> None:
    write_text(path, stable_json(value), written)


def scaffold_run(normalized: dict[str, Any], plan: dict[str, Any], agent: str, *, resume: bool = False) -> RunnerResult:
    run_root = REPO_ROOT / plan["run_root"]
    findings = validate_input(normalized)
    fatal = fatal_findings(findings)
    if fatal:
        return result_from_findings("scaffold", run_root, normalized, fatal, status="input_error")
    if run_root.exists():
        if not resume:
            return result_from_findings(
                "scaffold",
                run_root,
                normalized,
                [Finding(
                    id="WE_RUN_ROOT_EXISTS",
                    severity="P0",
                    message="run root already exists; pass --resume to regenerate packets for the same input",
                    path=repo_relative(run_root),
                    fix_hint="Use --resume only when the existing .workflow/input.normalized.json matches the input hash.",
                )],
                status="input_error",
            )
        existing = run_root / ".workflow" / "input.normalized.json"
        if existing.exists():
            existing_normalized = json.loads(existing.read_text())
            if input_sha256(existing_normalized) != plan["input_sha256"]:
                return result_from_findings(
                    "scaffold",
                    run_root,
                    normalized,
                    [Finding(
                        id="WE_INPUT_HASH_MISMATCH",
                        severity="P0",
                        message="existing run root was created from a different normalized input",
                        path=repo_relative(existing),
                        expected=plan["input_sha256"],
                        actual=input_sha256(existing_normalized),
                        fix_hint="Choose a new --run-root or pass the original input.",
                    )],
                    status="input_error",
                )
    run_root.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    write_json(run_root / ".workflow" / "input.normalized.json", normalized, written)
    write_json(run_root / ".workflow" / "plan.json", plan, written)
    write_json(run_root / ".workflow" / "execution-graph.json", plan["execution_graph"], written)
    write_json(run_root / ".workflow" / "tasks.json", plan["tasks"], written)
    write_json(run_root / ".workflow" / "registry.json", build_registry(plan), written)
    write_parent_files(run_root, normalized, plan, written)
    write_child_asset_files(run_root, normalized, plan, written)
    write_child_oracle_files(run_root, normalized, plan, written)
    write_packets(run_root, normalized, plan, agent, written)
    write_text(run_root / ".workflow" / "agent-handoff.md", render_agent_handoff_markdown(normalized, plan, agent), written)
    next_action = build_next_action(plan, status="blocked" if plan.get("blocking_unknowns") else "ready", validation=None)
    write_json(run_root / ".workflow" / "next-action.json", next_action, written)
    write_text(run_root / ".workflow" / "next-action.md", render_next_action_markdown(next_action), written)
    result_findings = [asdict(item) for item in findings if item.id == "WE_LIVE_FIELD_MISSING"]
    result = RunnerResult(
        mode="scaffold",
        status="scaffolded",
        exit_code=0,
        run_root=repo_relative(run_root),
        input_sha256=plan["input_sha256"],
        next_action=next_action,
        findings=result_findings,
        files_written=written,
        summary={"tasks": len(plan["tasks"]), "blocking_unknowns": len(plan.get("blocking_unknowns", [])), "files_written": len(written)},
    )
    return result


def build_registry(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "workflow-entrypoint-registry-v1",
        "run_root": plan["run_root"],
        "input_sha256": plan["input_sha256"],
        "children": plan["children"],
        "packets": [
            {"task_id": task["task_id"], "json": task["packet_json"], "markdown": task["packet_markdown"]}
            for task in plan["tasks"]
        ],
    }


def write_parent_files(run_root: Path, normalized: dict[str, Any], plan: dict[str, Any], written: list[str]) -> None:
    write_text(run_root / "README.md", render_parent_readme(normalized, plan), written)
    write_text(run_root / "index.md", render_parent_index(normalized, plan), written)
    manifest = {
        "schema_version": "analyze-propose-run-manifest-v1",
        "workflow": contracts.WORKFLOW_IDS["combined"],
        "status": "scaffolded",
        "run_root": plan["run_root"],
        "input_sha256": plan["input_sha256"],
        "children": plan["children"],
        "next_action": ".workflow/next-action.json",
        "parent_return": "agentic-flow/analyze-and-propose.md",
        "preview_gate": {"status": "blocked", "reason": "Analyze artifacts are not complete."},
        "execute_gate": {"status": "blocked", "reason": "No state-changing action is in scope."},
    }
    write_json(run_root / "run-manifest.json", manifest, written)
    write_text(run_root / "agentic-flow" / "analyze-and-propose.md", render_parent_return(normalized, plan), written)


def render_parent_readme(normalized: dict[str, Any], plan: dict[str, Any]) -> str:
    return f"""# Analyze → Propose scaffold — {normalized['primary_scope']}

This run root was generated by `dev/tools/run_workflow.py`. It contains deterministic child workflow roots, stage packets, and validation commands. The scaffold does not perform live research or claim readiness for Preview or Execute.

## Start here

For Codex or another local coding agent, paste only this short prompt:

```text
{short_agent_prompt(plan)}
```

Manual path:

1. Open `.workflow/agent-handoff.md`.
2. Open `.workflow/next-action.md`.
3. Assign or run the first packet named there.
4. After child artifacts are filled, run:

```bash
python3 dev/tools/run_workflow.py analyze-propose --input {normalized.get('source_input') or '<input.json>'} --run-root {plan['run_root']} --mode validate --format markdown --resume
```

## Children

- Asset diligence: `{plan['children']['asset']['run_root']}`
- Oracle analysis: `{plan['children']['oracle']['run_root']}`

## Gates

Preview and Execute are blocked until Analyze reports pass and a separate human-reviewed proposal exists.
"""


def clean_inline(value: Any) -> str:
    return " ".join(str(value).strip().rstrip(".").split())


def first_constraint(normalized: dict[str, Any], *, prefix: str | None = None, contains: str | None = None) -> str | None:
    for item in normalized.get("constraints", []):
        text = clean_inline(item)
        lower = text.lower()
        if prefix and lower.startswith(prefix.lower()):
            return text
        if contains and contains.lower() in lower:
            return text
    return None


def build_copy_prompt(normalized: dict[str, Any], run_root_rel: str) -> str:
    oracle_by_symbol = {
        str(scope.get("asset_symbol", "")).lower(): scope
        for scope in normalized.get("oracle_scopes", [])
        if scope.get("asset_symbol")
    }
    parts = [f"Open {run_root_rel}/.workflow/agent-handoff.md"]
    for asset in normalized.get("assets", []):
        symbol = asset.get("symbol") or asset.get("scope_id") or "asset"
        oracle = oracle_by_symbol.get(str(symbol).lower(), {})
        details = [f"token {clean_inline(asset.get('token_address') or 'not_available')}"]
        if oracle:
            details.append(f"feed {clean_inline(oracle.get('feed_address') or 'not_available')}")
        ltv = first_constraint(normalized, prefix=f"{symbol} LTV/LT")
        if ltv:
            details.append(ltv)
        parts.append(f"{symbol}: {', '.join(details)}")
    shared = [
        item
        for item in (
            first_constraint(normalized, prefix="Borrow asset"),
            first_constraint(normalized, prefix="Borrow rate"),
        )
        if item
    ]
    if shared:
        parts.append(", ".join(shared))
    parts.append("Analyze→Propose only; no Preview/Execute.")
    return "; ".join(parts)


def short_agent_prompt(plan: dict[str, Any]) -> str:
    handoff = plan.get("agent_handoff") or {}
    return handoff.get("copy_prompt") or f"Open {plan['run_root']}/.workflow/agent-handoff.md. Analyze→Propose only; no Preview/Execute."


def render_agent_handoff_markdown(normalized: dict[str, Any], plan: dict[str, Any], agent: str) -> str:
    validate_command = f"python3 dev/tools/run_workflow.py analyze-propose --input {normalized.get('source_input') or '<input.json>'} --run-root {plan['run_root']} --mode validate --resume --format markdown"
    return f"""# Agent handoff — Analyze → Propose

Paste this single line to the agent instead of pasting workflow details:

```text
{short_agent_prompt(plan)}
```

Agent launcher: `{agent}`.

## Contract

- Work in repository root `{REPO_ROOT}`.
- Write only under `{plan['run_root']}`.
- Discover is already complete; perform Analyze → Propose only.
- Preview and Execute are blocked. Do not perform state-changing on-chain actions.
- Use generated files for context: `.workflow/input.normalized.json`, child `scope.json` files, packets, and required references.
- `.workflow/next-action.json` may include `ready_packets`, `blocked_packets`, and `parallel_waves`; these fields are advisory metadata only.
- The harness does not schedule packets, launch workers, call subagents, or enforce concurrency. A graph-aware agent must verify disjoint artifact write scopes before parallel work and otherwise fall back to serial registry order.
- Delegation is safe only when a packet is ready, has `delegate_to_subagent: true`, includes a `subagent_prompt_reference`, and writes only inside its declared `artifact_write_scope`. The parent launches any worker outside the harness and keeps responsibility for reviewing returned artifacts.
- Parent must stay serial for blocked packets, serial fallbacks, run-wide synthesis/verification stages, missing prompt references, write-scope conflicts, or any case where returned artifacts cannot be independently validated.
- Treat the worker `return_contract` as a compressed handoff contract, not proof of completion: inspect artifact paths and run validation before unblocking downstream packets or trusting the worker self-report.
- Do not invent missing live values. Record unresolved gates and validator findings explicitly.

## Loop

1. Read `.workflow/next-action.md`.
2. Read `.workflow/registry.json`.
3. Execute packets in registry order, filling only each packet's declared `required_outputs`.
4. Keep raw evidence inside the child run roots; do not expand it into parent context.
5. After filling artifacts, run validation:

```bash
{validate_command}
```

Validation exit semantics:

- `0`: pass — summarize final recommendation and exact report paths.
- `1`: review_required — summarize unresolved finding IDs and why they remain review gates.
- `2`: blocked — fix P0 findings, rerun validation, or report the exact blocker if not fixable.

## Required final response

- Run root: `{plan['run_root']}`.
- Final validator exit code and status.
- Recommendation for the requested assets, with Preview/Execute still blocked unless separately authorized.
- Unresolved gates from `.workflow/input.normalized.json` and `.workflow/validation/summary.md`.
- Exact child report paths and parent `agentic-flow/analyze-and-propose.md` path.
"""


def render_parent_index(normalized: dict[str, Any], plan: dict[str, Any]) -> str:
    blockers = normalized.get("blocking_unknowns", [])
    blocker_lines = "\n".join(f"- `{item['scope_id']}.{item['field']}` — {item['next_step']}" for item in blockers) or "- none recorded in the input scaffold"
    return f"""# Run index

## Scope

- Primary scope: {normalized['primary_scope']}
- Question: {normalized['objective'].get('question') or 'not_available'}
- Input hash: `{plan['input_sha256']}`

## Generated roots

- Parent: `{plan['run_root']}`
- Asset child: `{plan['children']['asset']['run_root']}`
- Oracle child: `{plan['children']['oracle']['run_root']}`

## Blocking unknowns

{blocker_lines}

## Packet registry

See `.workflow/registry.json` for machine-readable packet paths.
"""


def render_parent_return(normalized: dict[str, Any], plan: dict[str, Any]) -> str:
    raw_blockers = normalized.get("blocking_unknowns", [])
    proposal_blockers = [
        {
            "owner": "workflow_operator",
            "source": f"{item.get('scope_id', 'scope')}.{item.get('field', 'input')}",
            "method": item.get("next_step") or "Provide the missing input or record investigated_no_result evidence.",
            "acceptance_criteria": f"{item.get('scope_id', 'scope')}.{item.get('field', 'input')} is resolved in the relevant child report before parent Preview.",
            "requested_input": f"{item.get('scope_id', 'scope')}.{item.get('field', 'input')}",
            "status": "request_more_inputs",
        }
        for item in raw_blockers
        if isinstance(item, dict)
    ]
    if not proposal_blockers:
        proposal_blockers = [
            {
                "owner": "workflow_operator",
                "source": "child.workflow_reports",
                "method": "Run or delegate the first packet in .workflow/next-action.md and import the child reports.",
                "acceptance_criteria": "Asset and oracle child workflow reports expose formal_validation_status, semantic_review_status, workflow_decision_status, and proposal_gate before parent Preview.",
                "requested_input": "child workflow reports",
                "status": "request_more_inputs",
            }
        ]
    proposal_gate = {
        "type": "request_more_inputs",
        "status": "request_more_inputs",
        "blockers": proposal_blockers,
        "explanation": "The scaffold is an input request, not a decision-grade proposal; formal validation, semantic review, and workflow decision readiness are separate.",
    }
    status_block = {
        "formal_validation_status": "pending_parent_validator",
        "semantic_review_status": "not_run",
        "workflow_decision_status": "request_more_inputs",
        "proposal_gate": proposal_gate,
        "explanation": "Formal validation only checks scaffold structure; semantic review and child workflow decisions must pass before proposal readiness.",
    }
    return f"""# Analyze → Propose parent return

## Stage status

- Discover: complete by user premise
- Analyze: scaffolded
- Propose: request_more_inputs
- Preview: blocked
- Execute: blocked
- Monitor: not started

## Status block

Formal validation is pending this parent validator. Semantic review has not run, and workflow decision readiness is request_more_inputs because the child workflow reports still need to resolve the listed blockers. This is an input request, not a decision-grade pass.

## Analyze artifacts

- asset child root: [{plan['children']['asset']['run_root']}](../asset-investment-diligence/)
- oracle child root: [{plan['children']['oracle']['run_root']}](../oracle-analysis/)
- next action: [`.workflow/next-action.md`](../.workflow/next-action.md)

## Requested next checks

Run or delegate the packet in `.workflow/next-action.md`, then run the entrypoint validation command. Do not advance to Preview or Execute from this scaffold.

```json
{stable_json({
    'schema_version': 'agentic-analyze-propose-v1',
    'stage_status': {
        'Discover': 'complete by user premise',
        'Analyze': 'scaffolded',
        'Propose': 'request_more_inputs',
        'Preview': 'blocked',
        'Execute': 'blocked',
        'Monitor': 'not started',
    },
    'status_block': status_block,
    'proposal_gate': proposal_gate,
    'analyze_artifacts': {
        'asset_child_root': 'asset-investment-diligence',
        'oracle_child_root': 'oracle-analysis',
        'next_action': '.workflow/next-action.json',
    },
    'preview_gate': {'status': 'blocked'},
    'execute_gate': {'status': 'blocked'},
    'unresolved_gates': raw_blockers,
}).rstrip()}
```
"""


def write_child_asset_files(run_root: Path, normalized: dict[str, Any], plan: dict[str, Any], written: list[str]) -> None:
    child = run_root / contracts.CHILD_DIRECTORIES["asset"]
    child.mkdir(parents=True, exist_ok=True)
    token_entries = []
    for asset in normalized["assets"]:
        token_entries.append({
            "token_slug": asset["scope_slug"],
            "symbol": asset["symbol"],
            "address": asset.get("token_address"),
            "artifact_dir": asset["artifact_dir"],
            "status": "scaffolded",
        })
        write_json(child / asset["artifact_dir"] / "scope.json", asset, written)
        write_text(child / asset["artifact_dir"] / "research" / "README.md", render_stage_placeholder("Asset research", asset, "Fill S1 research artifacts before S2."), written)
        write_text(child / asset["artifact_dir"] / "technical-report.md", render_stage_placeholder("Technical report", asset, "Not run. Packet S1 must fill this report with source-mapped evidence."), written)
        write_text(child / asset["artifact_dir"] / "analyst-report.md", render_stage_placeholder("Analyst report", asset, "Not run. Packet S2 must convert evidence into an analyst report without execution recommendations."), written)
        write_text(child / asset["artifact_dir"] / "verification.md", render_stage_placeholder("Token verification", asset, "Not run. Verify report sections, source map, and unknowns."), written)
    manifest = {
        "schema_version": "asset-investment-diligence-run-v1",
        "workflow": contracts.WORKFLOW_IDS["asset"],
        "status": "scaffolded",
        "run_root": repo_relative(child),
        "parent_run_root": plan["run_root"],
        "tokens": token_entries,
        "pt_markets": normalized.get("pt_markets", []),
        "skipped_stages": [item for item in plan["skipped_stages"] if item["workflow"] == "asset"],
        "final_verification": "verification/final-investment-analysis-verification.md",
    }
    write_text(child / "README.md", "# Asset investment diligence child root\n\nGenerated scaffold. Fill stage packets before treating this as analysis.\n", written)
    write_json(child / "run-manifest.json", manifest, written)
    write_text(child / "index.md", render_asset_index(normalized), written)
    write_text(child / "pt-markets" / "index.md", "# PT markets\n\nStatus: skipped. Reason: input `pt_markets` is empty unless later filled explicitly.\n\nSkipped stage: S3_pt_market_economics.\n", written)
    write_text(child / "x-research" / "index.md", "# X/social research\n\nStatus: skipped. Reason: input `social_scopes` is empty unless later filled explicitly.\n\nSkipped stages: S4_x_social_mining, S5_x_social_synthesis.\n", written)
    write_text(child / "investment-analysis" / "quantitative-underwriting-methodology.md", render_stage_placeholder("Quantitative underwriting methodology", {"scope_id": "run"}, "Not run. Packet S6 must fill formulas, inputs, unknowns, and risk-adjusted calculations."), written)
    write_text(child / "investment-analysis" / "investment-analyst-report-points-pt-risk-return.md", render_stage_placeholder("Investment analyst report", {"scope_id": "run"}, "Not run. Packet S6 must fill decision-surface analysis. No suitability claim is allowed."), written)
    write_text(child / "investment-analysis" / "index.md", "# Investment analysis index\n\nStatus: not_run. Fill S6 outputs before validation can pass.\n", written)
    write_text(child / "verification" / "final-investment-analysis-verification.md", render_stage_placeholder("Final investment analysis verification", {"scope_id": "run"}, "Not run. Execute validator and record commands/results here."), written)


def render_asset_index(normalized: dict[str, Any]) -> str:
    lines = ["# Asset diligence index", "", "## Tokens"]
    for asset in normalized["assets"]:
        lines.append(f"- `{asset['scope_slug']}` — {asset['symbol']} — status: scaffolded")
    lines.extend(["", "## Final validation status", "", "Status: not_run. Run the entrypoint validation bridge after filling stage outputs."])
    return "\n".join(lines) + "\n"


def write_child_oracle_files(run_root: Path, normalized: dict[str, Any], plan: dict[str, Any], written: list[str]) -> None:
    child = run_root / contracts.CHILD_DIRECTORIES["oracle"]
    child.mkdir(parents=True, exist_ok=True)
    scope_entries = []
    for scope in normalized["oracle_scopes"]:
        scope_entries.append({
            "scope_slug": scope["scope_slug"],
            "asset_symbol": scope.get("asset_symbol"),
            "artifact_dir": scope["artifact_dir"],
            "status": "scaffolded",
        })
        write_json(child / scope["artifact_dir"] / "scope.json", scope, written)
        write_text(child / scope["artifact_dir"] / "oracle" / "scope.md", render_oracle_scope(scope), written)
        for name in ("feed-graph.md", "node-classification.md", "source-primitive-audit.md", "stress-tradeoff-analysis.md", "protocol-fit-memo.md"):
            title = name.replace("-", " ").replace(".md", "").title()
            write_text(child / scope["artifact_dir"] / "oracle" / name, render_stage_placeholder(title, scope, "Not run. Fill from the corresponding oracle-analysis packet."), written)
        write_json(child / scope["artifact_dir"] / "raw" / "feed-probes.json", {"status": "not_run", "probes": [], "blocking_unknowns": [b for b in normalized.get("blocking_unknowns", []) if b.get("scope_id") == scope["scope_id"]]}, written)
        write_text(child / scope["artifact_dir"] / "raw" / "source-evidence" / "README.md", "# Source evidence\n\nStatus: not_run. Store raw source references here, not in parent context.\n", written)
        write_text(child / scope["artifact_dir"] / "verification" / "oracle-analysis-verification.md", render_stage_placeholder("Oracle analysis verification", scope, "Not run. Verify recursive graph, source primitives, side-specific verdicts, and links."), written)
    manifest = {
        "schema_version": "oracle-analysis-run-v1",
        "workflow": contracts.WORKFLOW_IDS["oracle"],
        "status": "scaffolded",
        "run_root": repo_relative(child),
        "parent_run_root": plan["run_root"],
        "scopes": scope_entries,
        "tokens": scope_entries,
        "final_verification": "verification/final-oracle-analysis-verification.md",
    }
    write_text(child / "README.md", "# Oracle analysis child root\n\nGenerated scaffold. Fill stage packets before treating this as oracle analysis.\n", written)
    write_json(child / "run-manifest.json", manifest, written)
    write_text(child / "index.md", render_oracle_index(normalized), written)
    write_text(child / "verification" / "final-oracle-analysis-verification.md", render_stage_placeholder("Final oracle analysis verification", {"scope_id": "run"}, "Not run. Execute validator and record commands/results here."), written)


def render_oracle_scope(scope: dict[str, Any]) -> str:
    return f"""# Oracle scope — {scope.get('scope_id')}

## Scope

- Asset: {scope.get('asset_symbol') or 'not_available'}
- Protocol: {scope.get('protocol') or 'not_available'}
- Chain: {scope.get('chain') or 'not_available'}
- Market or Credit Manager: {scope.get('market_or_credit_manager') or 'not_available'}
- Feed address: {scope.get('feed_address') or 'not_available'}
- Position side: {scope.get('position_side') or 'not_available'}
- Token role: {scope.get('token_role') or 'not_available'}
- Position size: {scope.get('position_size') or 'not_available'}

Status: scaffolded. Fill live feed discovery and side-specific oracle analysis before writing a verdict.
"""


def render_oracle_index(normalized: dict[str, Any]) -> str:
    lines = ["# Oracle analysis index", "", "## Scopes"]
    for scope in normalized["oracle_scopes"]:
        lines.append(f"- `{scope['scope_slug']}` — {scope.get('asset_symbol') or 'asset'} — status: scaffolded")
    lines.extend(["", "## Final validation status", "", "Status: not_run. Run the entrypoint validation bridge after filling stage outputs."])
    return "\n".join(lines) + "\n"


def render_stage_placeholder(title: str, scope: dict[str, Any], note: str) -> str:
    return f"""# {title}

Status: not_run

Scope: `{scope.get('scope_id', 'run')}`

{note}

## Required before pass

- Replace this scaffold with source-grounded content.
- Record explicit unknowns instead of inventing values.
- Keep Preview and Execute blocked unless a separate human-reviewed proposal authorizes them.
"""


def write_packets(run_root: Path, normalized: dict[str, Any], plan: dict[str, Any], agent: str, written: list[str]) -> None:
    for task in plan["tasks"]:
        packet = build_packet(task, normalized, plan, agent)
        write_json(run_root / task["packet_json"], packet, written)
        write_text(run_root / task["packet_markdown"], render_packet_markdown(packet), written)


def build_packet_metadata(task: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    graph_node = next((node for node in (plan.get("execution_graph") or {}).get("tasks", []) if node.get("task_id") == task["task_id"]), None)
    if graph_node:
        return {
            "delegate_to_subagent": graph_node.get("delegate_to_subagent", False),
            "subagent_prompt_reference": graph_node.get("subagent_prompt_reference"),
            "recommended_max_concurrent": graph_node.get("recommended_max_concurrent", 1),
            "return_contract": graph_node.get("return_contract"),
            "artifact_write_scope": graph_node.get("artifact_write_scope", {}),
        }
    sources = workflow_graph_sources()
    source = sources[task["workflow_key"]]
    return {
        "delegate_to_subagent": False,
        "subagent_prompt_reference": None,
        "recommended_max_concurrent": 1,
        "return_contract": stage_worker_return_contract(task, source),
        "artifact_write_scope": artifact_write_scope(plan, task),
    }


def build_packet(task: dict[str, Any], normalized: dict[str, Any], plan: dict[str, Any], agent: str) -> dict[str, Any]:
    metadata = build_packet_metadata(task, plan)
    payload = build_task_payload(task, normalized, plan, metadata)
    return {
        "packet_schema": contracts.PACKET_SCHEMA_VERSION,
        "schema_version": contracts.PACKET_SCHEMA_VERSION,
        "agent": agent,
        "launcher": contracts.AGENT_LAUNCHERS[agent],
        "packet_metadata": metadata,
        "task_payload_sha256": hashlib.sha256(stable_json(payload).encode("utf-8")).hexdigest(),
        "task_payload": payload,
    }


def build_required_fact_slots(task: dict[str, Any]) -> list[dict[str, Any]]:
    stage_key = f"{task['workflow_key']}.{task['stage_id']}"
    scope_slug = task.get("scope_slug") or "run"
    slots = [{
        "fact_id": f"{stage_key}.{scope_slug}.scope_loaded",
        "description": "stage scope, input paths, and required outputs are loaded before claims",
        "required": True,
        "minimum_evidence": [".workflow/input.normalized.json", *task["input_paths"]],
        "if_missing_state": "not_investigated",
        "decision_effect_if_unresolved": "blocked",
    }]
    for index, description in enumerate(STAGE_FACT_SLOT_DESCRIPTIONS.get(task["stage_id"], ()), start=1):
        slots.append({
            "fact_id": f"{stage_key}.{scope_slug}.f{index}_{slugify(description, f'fact-{index}')[:48]}",
            "description": description,
            "required": True,
            "minimum_evidence": ["source/evidence artifact path", "fact result state", "decision_effect"],
            "if_missing_state": "not_investigated",
            "decision_effect_if_unresolved": "blocked",
        })
    return slots


def build_blocker_fact_slots(task: dict[str, Any]) -> list[dict[str, Any]]:
    slots = []
    for blocker in task.get("blocking_unknowns") or []:
        slots.append({
            "fact_id": blocker["fact_id"],
            "description": f"input missing for {blocker['scope_id']}.{blocker['field']}",
            "required": True,
            "expected_state_until_resolved": "input_missing",
            "input_schema_key": blocker.get("input_schema_key"),
            "expected_input": blocker.get("expected_input"),
            "minimum_evidence": [blocker.get("source_path", ".workflow/input.normalized.json")],
            "decision_effect_if_unresolved": blocker.get("decision_effect", "request_more_inputs"),
        })
    return slots


def build_precomputed_boundary_facts(task: dict[str, Any], plan: dict[str, Any]) -> list[dict[str, Any]]:
    facts = []
    for item in plan.get("skipped_stages", []):
        if item.get("workflow") != task["workflow_key"]:
            continue
        facts.append({
            "fact_id": f"{item['workflow']}.{item['stage_id']}.stage_applicability",
            "state": "not_applicable",
            "applicability_rule_id": "empty-input-stage-skip",
            "reason": item.get("reason"),
            "evidence_path": ".workflow/plan.json",
            "decision_effect": "no_gate",
        })
    return facts


def build_fact_results_template(task: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    fact_results = []
    for blocker in task.get("blocking_unknowns") or []:
        fact_results.append({
            "fact_id": blocker["fact_id"],
            "state": "input_missing",
            "input_schema_key": blocker.get("input_schema_key"),
            "requested_input": blocker.get("expected_input"),
            "reason": "Required input is absent or is a disallowed placeholder; do not invent it.",
            "evidence_path": blocker.get("source_path", ".workflow/input.normalized.json"),
            "decision_effect": blocker.get("decision_effect", "request_more_inputs"),
        })
    fact_results.append({
        "fact_id": "<required_fact_id_from_stage_contract>",
        "state": "not_investigated",
        "missing_investigation": "<method/source/fact not attempted>",
        "evidence_path": "<stage artifact path showing omission or explicit blocked return>",
        "decision_effect": "blocked",
    })
    return {
        "fact_results": fact_results,
        "precomputed_boundary_facts": build_precomputed_boundary_facts(task, plan),
        "fact_state_summary": {state: 0 for state in FACT_STATES},
        "blocking_fact_ids": [item["fact_id"] for item in task.get("blocking_unknowns") or []],
    }


def build_no_result_proof_template(task: dict[str, Any]) -> dict[str, Any]:
    stage_key = f"{task['workflow_key']}.{task['stage_id']}"
    return {
        "proof_id": f"{stage_key}.<fact>.no_result.v1",
        "fact_id": "<required_fact_id>",
        "state": "investigated_no_result",
        "methods_tried": [
            {
                "source_class": "<authoritative_registry|contract_probe|docs_or_governance|market_source>",
                "method": "<tool/command/API/RPC/search method>",
                "query_or_endpoint": "<exact query, contract call, endpoint, registry key, or document path>",
                "timestamp_utc": "<YYYY-MM-DDTHH:MM:SSZ>",
                "artifact_path": "raw/<fact>-negative-evidence.json",
                "result": "negative",
            }
        ],
        "sources_checked": ["<source ids/classes checked>"],
        "negative_evidence_path": "raw/<fact>-negative-evidence.json",
        "coverage": "<chain/protocol/registry/time-window/search boundary covered>",
        "freshness_utc": "<YYYY-MM-DDTHH:MM:SSZ>",
        "residual_decision_effect": "pass|review_required|request_more_inputs|blocked",
    }


def build_s6_scenario_band_contract(task: dict[str, Any]) -> dict[str, Any] | None:
    if task.get("workflow_key") != "asset" or task.get("stage_id") != "S6_quantitative_underwriting":
        return None

    missing_s6_fields = input_missing_fields_for_stage(task, "asset.S6_quantitative_underwriting")
    scenario_missing_fields = sorted(field for field in missing_s6_fields if field in ANALYZE_ONLY_SCENARIO_INPUT_FIELDS)
    non_scenario_missing_fields = sorted(field for field in missing_s6_fields if field not in ANALYZE_ONLY_SCENARIO_INPUT_FIELDS)
    scenario_needed = bool(scenario_missing_fields)
    forbidden = bool(task.get("scenario_analysis_forbidden"))
    scenario_allowed = scenario_needed and not non_scenario_missing_fields and not forbidden

    reason_parts: list[str] = []
    if not scenario_needed:
        reason_parts.append("no scenario-eligible sizing/leverage/horizon/policy input is missing")
    if non_scenario_missing_fields:
        reason_parts.append("non-scenario blockers remain: " + ", ".join(non_scenario_missing_fields))
    if forbidden:
        reason_parts.append("request constraints disallow fallback scenarios")
    if scenario_allowed:
        reason_parts.append("only scenario-eligible Analyze inputs are missing")

    bands = [
        {
            "band_id": level,
            "required_axes": [ANALYZE_ONLY_SCENARIO_INPUT_FIELDS[field] for field in scenario_missing_fields],
            "must_include": [
                "assumption values with units and source/derivation notes",
                "gross ROI and simple/compound annualized return",
                "risk-adjusted ROI/annualized return and expected loss",
                "exit cost, liquidation/oracle stress, and break-even logic",
            ],
        }
        for level in SCENARIO_BAND_LEVELS
    ]

    return {
        "contract_schema": SCENARIO_BAND_CONTRACT_VERSION,
        "scenario_needed": scenario_needed,
        "scenario_allowed": scenario_allowed,
        "missing_inputs": scenario_missing_fields,
        "blocking_inputs_that_prevent_scenarios": non_scenario_missing_fields,
        "reason": "; ".join(reason_parts),
        "bands": bands,
        "proposal_gate": "Missing user inputs stay propagated to combined.Propose as request_more_inputs.",
        "preview_execute_gate": "Analyze-only scenarios must not set Preview or Execute to ready/pass.",
        "if_allowed": [
            "Produce labelled conservative/base/upside scenario bands instead of skipping all S6 calculations.",
            "Mark every band non-executable and assumption-bound.",
            "Ask for exact missing sizing/leverage/horizon/risk-policy inputs before Proposal, Preview, or Execute readiness.",
        ],
        "if_not_allowed": [
            "Do not invent fallback scenarios.",
            "Keep exact underwriting blocked/request_more_inputs with the unresolved input_missing fact IDs.",
        ],
    }


def build_stage_contract(task: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    contract = {
        "contract_schema": "workflow-stage-contract-v1",
        "mandatory_facts": build_required_fact_slots(task) + build_blocker_fact_slots(task),
        "required_methods": [
            "Load the input paths and stage scope before writing claims.",
            "For every material claim, save or cite a source/evidence artifact path under the child run root.",
            "If a source search finds nothing, fill no_result_proof_template; do not write bare 'not found'.",
            "If you cannot investigate a required fact, return a fact_result with state=not_investigated and status=blocked/review_required.",
        ],
        "allowed_unknown_states": list(FACT_STATES),
        "state_evidence_requirements": STATE_EVIDENCE_REQUIREMENTS,
        "minimum_source_evidence_requirements": [
            "fact_id, state, scope_id, required_by, decision_effect",
            "source/evidence artifact path for every known, inconclusive, unavailable, contradicted, or no-result fact",
            "input_schema_key/requested_input for input_missing facts",
            "applicability_rule_id/evidence_path for not_applicable facts",
        ],
        "disallowed_placeholders": list(DISALLOWED_PLACEHOLDERS),
        "precomputed_boundary_facts": build_precomputed_boundary_facts(task, plan),
        "fact_results_template": build_fact_results_template(task, plan),
        "no_result_proof_template": build_no_result_proof_template(task),
    }
    scenario_contract = build_s6_scenario_band_contract(task)
    if scenario_contract:
        contract["scenario_band_contract"] = scenario_contract
    return contract


def protocol_adapter_for_task(task: dict[str, Any], normalized: dict[str, Any]) -> dict[str, Any] | None:
    if task["workflow_key"] != "oracle":
        return None
    scope_id = task.get("scope_id")
    scope = next((item for item in normalized["oracle_scopes"] if item.get("scope_id") == scope_id), None)
    if not scope:
        return None
    return protocol_adapters.packet_payload_for_protocol(scope.get("protocol"))


def build_task_payload(task: dict[str, Any], normalized: dict[str, Any], plan: dict[str, Any], packet_metadata: dict[str, Any]) -> dict[str, Any]:
    return {
        "command": contracts.COMMAND,
        "workflow_id": task["workflow_id"],
        "stage_id": task["stage_id"],
        "stage_title": task["stage_title"],
        "scope_id": task["scope_id"],
        "scope_type": task["scope_type"],
        "run_root": task["child_run_root"],
        "artifact_dir": task["artifact_dir"],
        "objective": normalized["objective"],
        "known_inputs": {
            "assets": normalized["assets"],
            "oracle_scopes": normalized["oracle_scopes"],
            "pt_markets": normalized["pt_markets"],
            "social_scopes": normalized["social_scopes"],
        },
        "input_paths": task["input_paths"],
        "required_outputs": task["required_outputs"],
        "packet_metadata": packet_metadata,
        "required_packet_headings": list(contracts.REQUIRED_PACKET_HEADINGS),
        "blocking_unknowns": task["blocking_unknowns"],
        "stage_contract": build_stage_contract(task, plan),
        "protocol_adapter": protocol_adapter_for_task(task, normalized),
        "mandatory_reference_paths": list(contracts.MANDATORY_REFERENCES),
        "optional_reference_paths": list(contracts.OPTIONAL_REFERENCES[task["workflow_key"]]),
        "validation_command": task["validation_command"],
        "return_envelope": {
            "artifact_paths": task["required_outputs"],
            "status": "pass|review_required|blocked",
            "blockers": "list concrete blockers, empty if pass",
            "validation_status": "validator status and report path",
            "fact_state_summary": {state: 0 for state in FACT_STATES},
            "blocking_fact_ids": [item["fact_id"] for item in task.get("blocking_unknowns") or []],
            "fact_result_artifact_paths": ["<path to fact-results.json or markdown fenced JSON>"],
            "no_result_proof_paths": ["<path to no-result-proofs.json when any fact is investigated_no_result>"],
        },
        "do_not": list(contracts.COMMON_DO_NOT),
    }


def render_protocol_adapter_section(adapter: dict[str, Any] | None) -> str:
    if not adapter:
        return "- none"
    state_lines = "\n".join(f"- `{state}`" for state in adapter["fact_result_states"])
    proof_lines = "\n".join(f"- `{item}`" for item in adapter["no_result_proof_classes"])
    fact_lines = []
    for fact in adapter["required_facts"]:
        discovery = "; ".join(fact.get("discovery_methods") or []) or "not specified"
        negative = "; ".join(fact.get("negative_search_methods") or []) or "not specified"
        no_result = fact.get("no_result_semantics") or "Use the adapter-level no-market/no-route semantics when this fact is absent."
        proof_required = "yes" if fact.get("requires_no_result_proof") else "no"
        fact_lines.append(
            f"- `{fact['fact_id']}` — {fact['label']}\n"
            f"  - discovery: {discovery}\n"
            f"  - negative search: {negative}\n"
            f"  - no-result proof required: {proof_required}\n"
            f"  - no-result semantics: {no_result}"
        )
    return f"""Adapter: `{adapter['adapter_id']}` ({adapter['protocol']} v{adapter['version']})

Purpose: {adapter['purpose']}

Required fact states:
{state_lines}

Required no-result proof classes:
{proof_lines}

No-market/no-route semantics:
- {adapter['no_market_no_route_semantics']}

Protocol-required facts:
{chr(10).join(fact_lines)}"""


def render_scenario_band_contract_section(contract: dict[str, Any] | None) -> str:
    if not contract:
        return "- none"
    band_lines = "\n".join(
        f"- `{band['band_id']}` — axes: {', '.join(band.get('required_axes') or ['none'])}; include: {', '.join(band.get('must_include') or [])}"
        for band in contract.get("bands") or []
    ) or "- none"
    allowed_lines = "\n".join(f"- {item}" for item in contract.get("if_allowed") or []) or "- none"
    blocked_lines = "\n".join(f"- {item}" for item in contract.get("if_not_allowed") or []) or "- none"
    return f"""Contract: `{contract['contract_schema']}`

- Scenario needed: `{contract['scenario_needed']}`
- Scenario allowed: `{contract['scenario_allowed']}`
- Missing scenario inputs: `{', '.join(contract.get('missing_inputs') or []) or 'none'}`
- Inputs preventing scenarios: `{', '.join(contract.get('blocking_inputs_that_prevent_scenarios') or []) or 'none'}`
- Reason: {contract.get('reason') or 'not specified'}
- Proposal gate: {contract['proposal_gate']}
- Preview/Execute gate: {contract['preview_execute_gate']}

Required bands when allowed:
{band_lines}

When allowed:
{allowed_lines}

When not allowed:
{blocked_lines}"""


def render_packet_delegation_section(metadata: dict[str, Any]) -> str:
    prompt = metadata.get("subagent_prompt_reference") or {}
    contract = metadata.get("return_contract") or {}
    prompt_reference = "none"
    if prompt:
        section = str(prompt.get("section") or "")
        compact_section = section.split(" prompt", 1)[0] if " prompt" in section else section.split(" — ", 1)[0]
        prompt_reference = f"`{Path(prompt['path']).name}#{compact_section}`"
    return f"- `delegate_to_subagent`: `{str(bool(metadata.get('delegate_to_subagent'))).lower()}`; `recommended_max_concurrent`: `{metadata.get('recommended_max_concurrent', 1)}`; `subagent_prompt_reference`: {prompt_reference}; `return_contract`: `{contract.get('contract_id', 'not_declared')}`; `artifact_write_scope`: packet_metadata; parent validates artifacts; worker self-report advisory."


def render_packet_markdown(packet: dict[str, Any]) -> str:
    payload = packet["task_payload"]
    metadata = packet.get("packet_metadata") or payload.get("packet_metadata") or {}
    blockers = payload.get("blocking_unknowns") or []
    blocker_lines = "\n".join(
        f"- `{item['fact_id']}` — `{item.get('state', 'input_missing')}` from `{item.get('input_schema_key', item['field'])}`; {item['next_step']}"
        for item in blockers
    ) or "- none"
    outputs = "\n".join(f"- `{path}`" for path in payload["required_outputs"])
    input_paths = "\n".join(f"- `{path}`" for path in payload["input_paths"])
    references = "\n".join(f"- `{path}`" for path in payload["optional_reference_paths"])
    contract = payload["stage_contract"]
    mandatory_fact_lines = "\n".join(
        f"- `{slot['fact_id']}` — {slot['description']} (if unresolved: `{slot.get('expected_state_until_resolved') or slot.get('if_missing_state')}`)"
        for slot in contract["mandatory_facts"]
    )
    method_lines = "\n".join(f"- {item}" for item in contract["required_methods"])
    state_lines = "\n".join(f"- `{state}` — {contract['state_evidence_requirements'][state]}" for state in contract["allowed_unknown_states"])
    evidence_lines = "\n".join(f"- {item}" for item in contract["minimum_source_evidence_requirements"])
    placeholder_lines = "\n".join(f"- `{item}`" for item in contract["disallowed_placeholders"])
    boundary_lines = "\n".join(
        f"- `{item['fact_id']}` — `not_applicable`: {item['reason']} (evidence: `{item['evidence_path']}`)"
        for item in contract["precomputed_boundary_facts"]
    ) or "- none"
    fact_template = stable_json(contract["fact_results_template"]).rstrip()
    no_result_template = stable_json(contract["no_result_proof_template"]).rstrip()
    protocol_adapter_section = render_protocol_adapter_section(payload.get("protocol_adapter"))
    scenario_contract_section = render_scenario_band_contract_section(contract.get("scenario_band_contract"))
    delegation_section = render_packet_delegation_section(metadata)
    return f"""# Stage packet — {payload['stage_id']} — {payload['scope_id']}

Launcher: {packet['launcher']}

## Scope

- Workflow: `{payload['workflow_id']}`
- Child run root: `{payload['run_root']}`
- Artifact directory: `{payload['artifact_dir']}`
- Objective: {payload['objective'].get('question') or 'not_available'}

## Delegation metadata

{delegation_section}

## Known inputs

Input paths:
{input_paths}

Optional references:
{references}

## Blocking unknowns

{blocker_lines}

## Protocol investigation adapter

{protocol_adapter_section}

## Analyze-only scenario contract

{scenario_contract_section}

## Stage contract checklist

Mandatory facts:
{mandatory_fact_lines}

Required methods:
{method_lines}

Allowed unknown states and evidence:
{state_lines}

Minimum source/evidence requirements:
{evidence_lines}

Disallowed placeholders:
{placeholder_lines}

Precomputed not-applicable boundaries:
{boundary_lines}

## Fact results to produce

```json
{fact_template}
```

## No-result proof template

Use this only for `investigated_no_result`; fill methods tried, sources checked, negative evidence path, and residual decision effect.

```json
{no_result_template}
```

## Work to perform

Fill this stage only. Preserve source evidence in the child run root and return only the envelope fields. Do not expand raw evidence into the parent prompt.

## Required outputs

{outputs}

## Validation command

```bash
{payload['validation_command']}
```

## Return envelope

```json
{stable_json(payload['return_envelope']).rstrip()}
```
"""


def ready_packet_summary(node: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": node["task_id"],
        "json": node["packet_json"],
        "markdown": node["packet_markdown"],
        "parallel_group_id": node.get("parallel_group_id"),
        "parallel_unit": node.get("parallel_unit"),
        "delegate_to_subagent": node.get("delegate_to_subagent", False),
        "subagent_prompt_reference": node.get("subagent_prompt_reference"),
        "recommended_max_concurrent": node.get("recommended_max_concurrent", 1),
        "return_contract": node.get("return_contract"),
        "artifact_write_scope": node.get("artifact_write_scope", {}),
        "depends_on_task_ids": node.get("depends_on_task_ids", []),
        "ready_reason": node.get("ready_reason", ""),
    }


def blocked_packet_summary(node: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": node["task_id"],
        "json": node["packet_json"],
        "markdown": node["packet_markdown"],
        "delegate_to_subagent": node.get("delegate_to_subagent", False),
        "subagent_prompt_reference": node.get("subagent_prompt_reference"),
        "recommended_max_concurrent": node.get("recommended_max_concurrent", 1),
        "return_contract": node.get("return_contract"),
        "artifact_write_scope": node.get("artifact_write_scope", {}),
        "blocked_by_task_ids": node.get("depends_on_task_ids", []),
        "missing_artifacts": node.get("missing_artifacts", []),
        "blocking_unknowns": node.get("blocking_unknowns", []),
        "ready_after_validation": node.get("ready_after_validation", {}),
        "blocked_reasons": node.get("blocked_reasons", []),
        "blocked_reason": node.get("blocked_reason", ""),
    }


def build_parallel_waves(graph_tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ready_nodes = [node for node in graph_tasks if node.get("scaffold_state") == "ready"]
    if not ready_nodes:
        return []
    return [
        {
            "wave_id": "ready-wave-1",
            "wave_index": 1,
            "status": "ready",
            "advisory_only": True,
            "harness_orchestration": "none",
            "artifact_write_scope_policy": "disjoint_write_roots_required",
            "recommended_max_concurrent": len(ready_nodes),
            "packet_task_ids": [node["task_id"] for node in ready_nodes],
            "packets": [ready_packet_summary(node) for node in ready_nodes],
            "safety_rationale": "All packets in this wave have no unresolved packet dependencies or packet-level blockers, and their artifact write scopes are disjoint. The harness records advisory metadata only; it does not schedule, launch, or orchestrate workers.",
        }
    ]


def build_next_action(plan: dict[str, Any], *, status: str, validation: dict[str, Any] | None) -> dict[str, Any]:
    first_task = plan["tasks"][0] if plan.get("tasks") else None
    graph_tasks = (plan.get("execution_graph") or {}).get("tasks", [])
    graph_by_task = {node["task_id"]: node for node in graph_tasks}
    first_graph_node = None if not first_task else graph_by_task.get(first_task["task_id"])
    if validation and validation.get("status") in ("pass", "review_required", "blocked"):
        action_status = validation["status"]
    else:
        action_status = status
    return {
        "schema_version": contracts.NEXT_ACTION_SCHEMA_VERSION,
        "status": action_status,
        "reason": next_action_reason(action_status, plan, validation),
        "run_root": plan["run_root"],
        "input_sha256": plan["input_sha256"],
        "agent_handoff": plan.get("agent_handoff", {"markdown": ".workflow/agent-handoff.md", "copy_prompt": short_agent_prompt(plan)}),
        "first_packet": None if not first_task else {
            "task_id": first_task["task_id"],
            "json": first_task["packet_json"],
            "markdown": first_task["packet_markdown"],
            "delegate_to_subagent": False if not first_graph_node else first_graph_node.get("delegate_to_subagent", False),
            "subagent_prompt_reference": None if not first_graph_node else first_graph_node.get("subagent_prompt_reference"),
            "recommended_max_concurrent": 1 if not first_graph_node else first_graph_node.get("recommended_max_concurrent", 1),
            "return_contract": None if not first_graph_node else first_graph_node.get("return_contract"),
            "artifact_write_scope": {} if not first_graph_node else first_graph_node.get("artifact_write_scope", {}),
            "blocking_unknowns": first_task["blocking_unknowns"],
        },
        "ready_packets": [ready_packet_summary(node) for node in graph_tasks if node.get("scaffold_state") == "ready"],
        "blocked_packets": [blocked_packet_summary(node) for node in graph_tasks if node.get("scaffold_state") == "blocked"],
        "parallel_waves": build_parallel_waves(graph_tasks),
        "validation": validation or {"status": "not_run"},
        "children": plan["children"],
    }


def next_action_reason(status: str, plan: dict[str, Any], validation: dict[str, Any] | None) -> str:
    if validation:
        if status == "pass":
            return "Child validators passed; parent can inspect filled artifacts before any separate proposal gate."
        if status == "review_required":
            return "Validation completed with warning/review findings; inspect reports before proceeding."
        return "Validation found blocking findings; fill the listed artifacts or missing inputs before proceeding."
    if plan.get("blocking_unknowns"):
        return "Scaffold created with live inputs missing; first stage packet lists concrete blockers to fill."
    return "Scaffold created; run the first packet, then validate."


def ready_packet_markdown_lines(packets: list[dict[str, Any]]) -> str:
    if not packets:
        return "- none"
    lines = []
    for packet in packets:
        group = packet.get("parallel_group_id") or "serial"
        scope = packet.get("artifact_write_scope") or {}
        prompt = packet.get("subagent_prompt_reference") or {}
        write_roots = ", ".join(f"`{root}`" for root in scope.get("write_roots", [])) or "not_declared"
        prompt_line = "none" if not prompt else f"`{prompt['path']}` → `{prompt['section']}`"
        reason = packet.get("ready_reason") or "ready"
        lines.append(f"- `{packet['task_id']}` — group `{group}`; delegate `{str(bool(packet.get('delegate_to_subagent'))).lower()}`; prompt {prompt_line}; writes {write_roots}; reason: {reason}")
    return "\n".join(lines)


def blocked_packet_markdown_lines(packets: list[dict[str, Any]]) -> str:
    if not packets:
        return "- none"
    lines = []
    for packet in packets:
        blockers = ", ".join(f"`{task_id}`" for task_id in packet.get("blocked_by_task_ids", [])) or "none"
        missing = ", ".join(f"`{path}`" for path in packet.get("missing_artifacts", [])) or "none"
        reason = packet.get("blocked_reason") or ", ".join(packet.get("blocked_reasons", [])) or "blocked"
        lines.append(f"- `{packet['task_id']}` — reason: {reason}; blocked by: {blockers}; missing artifacts: {missing}")
    return "\n".join(lines)


def parallel_wave_markdown_lines(waves: list[dict[str, Any]]) -> str:
    if not waves:
        return "- none"
    lines = []
    for wave in waves:
        packet_ids = ", ".join(f"`{task_id}`" for task_id in wave.get("packet_task_ids", [])) or "none"
        wave_id = wave.get("wave_id") or f"wave-{wave.get('wave_index', '?')}"
        lines.append(f"- `{wave_id}` — advisory only, max `{wave.get('recommended_max_concurrent', 1)}` concurrent: {packet_ids}")
    return "\n".join(lines)


def render_next_action_markdown(next_action: dict[str, Any]) -> str:
    first = next_action.get("first_packet") or {}
    blockers = first.get("blocking_unknowns") or []
    blocker_lines = "\n".join(f"- `{item['scope_id']}.{item['field']}` — {item['next_step']}" for item in blockers) or "- none"
    validation = next_action.get("validation") or {}
    handoff = next_action.get("agent_handoff") or {}
    ready_lines = ready_packet_markdown_lines(next_action.get("ready_packets", []))
    blocked_lines = blocked_packet_markdown_lines(next_action.get("blocked_packets", []))
    wave_lines = parallel_wave_markdown_lines(next_action.get("parallel_waves", []))
    return f"""# Next action

Status: {next_action['status']}

Reason: {next_action['reason']}

## Agent handoff

- File: `{handoff.get('markdown', '.workflow/agent-handoff.md')}`
- Copy-paste prompt: `{handoff.get('copy_prompt', '')}`

## First packet

- JSON: `{first.get('json', 'not_available')}`
- Markdown: `{first.get('markdown', 'not_available')}`

## Blocking unknowns in first packet

{blocker_lines}

## Ready packets

Advisory graph metadata only. These packets can be worked now if the agent chooses a graph-aware path; the harness performs no scheduling, worker launch, subagent call, or orchestration. Only launch a subagent when `delegate_to_subagent` is true, a `subagent_prompt_reference` is present, and the parent will validate returned artifact paths.

{ready_lines}

## Parallel waves

Packets in the same wave have disjoint artifact write scopes. Treat conflicts, blocked packets, missing prompt references, or missing dependency metadata as serial/blocking and fall back to `first_packet` plus registry order.

{wave_lines}

## Blocked packets

Blocked packets are not failed. Do not unlock downstream stages until declared upstream outputs exist and validation state permits it.

{blocked_lines}

## Validation status

- Status: {validation.get('status', 'not_run')}
- Reports: {validation.get('reports', [])}
"""


def validate_run(
    normalized: dict[str, Any],
    plan: dict[str, Any],
    *,
    strict_warnings: bool = False,
    semantic_review: bool = False,
    semantic_critic_command: str | None = None,
    semantic_critic_timeout: int = 120,
) -> RunnerResult:
    run_root = REPO_ROOT / plan["run_root"]
    findings = validate_input(normalized)
    fatal = fatal_findings(findings)
    if fatal:
        return result_from_findings("validate", run_root, normalized, fatal, status="input_error")
    written: list[str] = []
    validation_dir = run_root / ".workflow" / "validation"
    validation_dir.mkdir(parents=True, exist_ok=True)
    reports = []
    imported_findings: list[dict[str, Any]] = []
    command_records = []
    worst_exit = 0
    for workflow_key in ("asset", "oracle", "combined"):
        cmd = list(plan["validator_commands"][workflow_key])
        if workflow_key == "combined":
            cmd = [part for part in cmd if part != "--write-verification"]
        proc = subprocess.run(cmd, cwd=REPO_ROOT, text=True, capture_output=True)
        stdout_path = validation_dir / f"{workflow_key}-stdout.txt"
        stderr_path = validation_dir / f"{workflow_key}-stderr.txt"
        write_text(stdout_path, proc.stdout, written)
        write_text(stderr_path, proc.stderr, written)
        report = parse_validator_stdout(proc.stdout, workflow_key)
        if report:
            if workflow_key == "combined":
                report_path = f"{plan['run_root']}/verification/workflow-harness-report.json"
            else:
                report_path = f"{plan['children'][workflow_key]['run_root']}/verification/workflow-harness-report.json"
            reports.append({
                "workflow": workflow_key,
                "status": report.get("status"),
                "exit_code": proc.returncode,
                "stdout": repo_relative(stdout_path),
                "stderr": repo_relative(stderr_path),
                "report_path": report_path,
            })
            for finding in report.get("findings", []):
                imported = dict(finding)
                imported["source_workflow"] = workflow_key
                imported_findings.append(imported)
        else:
            reports.append({"workflow": workflow_key, "status": "blocked", "exit_code": proc.returncode, "stdout": repo_relative(stdout_path), "stderr": repo_relative(stderr_path), "parse_error": True})
            imported_findings.append({"id": f"{workflow_key}.validator.stdout_json", "severity": "P0", "message": "validator stdout was not parseable JSON", "source_workflow": workflow_key})
        command_records.append({"workflow": workflow_key, "command": cmd, "exit_code": proc.returncode})
        worst_exit = max(worst_exit, min(proc.returncode, 2))

    execution_graph, graph_findings = validate_execution_graph(plan, run_root)
    imported_findings.extend(graph_findings)
    status = validation_status_from_reports(reports, imported_findings, strict_warnings)
    validation = {
        "status": status,
        "strict_warnings": strict_warnings,
        "reports": reports,
        "commands": command_records,
        "imported_findings": imported_findings,
        "finding_counts": count_findings(imported_findings),
        "execution_graph": execution_graph,
        "semantic_review": {"enabled": False},
    }
    validation_summary_path = validation_dir / "summary.json"
    if semantic_review:
        write_json(validation_summary_path, validation, written)
        semantic_findings, semantic_reviews = run_semantic_reviews(
            plan,
            validation_summary_path,
            critic_command=semantic_critic_command,
            timeout=semantic_critic_timeout,
            written=written,
        )
        imported_findings.extend(semantic_findings)
        status = validation_status_from_reports(reports, imported_findings, strict_warnings)
        validation.update({
            "status": status,
            "imported_findings": imported_findings,
            "finding_counts": count_findings(imported_findings),
            "semantic_review": {
                "enabled": True,
                "command_configured": bool(semantic_critic_command),
                "reviews": semantic_reviews,
            },
        })
    exit_code = contracts.STATUS_EXIT_CODES[status]
    write_json(validation_summary_path, validation, written)
    write_text(validation_dir / "summary.md", render_validation_summary(validation), written)
    next_action = build_next_action(plan, status=status, validation=validation)
    write_json(run_root / ".workflow" / "next-action.json", next_action, written)
    write_text(run_root / ".workflow" / "next-action.md", render_next_action_markdown(next_action), written)
    return RunnerResult(
        mode="validate",
        status=status,
        exit_code=exit_code,
        run_root=repo_relative(run_root),
        input_sha256=plan["input_sha256"],
        next_action=next_action,
        validation=validation,
        findings=imported_findings,
        files_written=written,
        summary={"reports": len(reports), "findings": len(imported_findings), "status": status},
    )


def parse_validator_stdout(stdout: str, workflow_key: str) -> dict[str, Any] | None:
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    return data


def semantic_review_truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def task_review_root(plan: dict[str, Any], task: dict[str, Any]) -> Path:
    workflow_key = task.get("workflow_key")
    if workflow_key in plan.get("children", {}):
        return REPO_ROOT / plan["children"][workflow_key]["run_root"]
    return REPO_ROOT / plan["run_root"]


def task_semantic_paths(plan: dict[str, Any], task: dict[str, Any]) -> tuple[list[Path], list[Path], list[Path]]:
    stage_root = task_review_root(plan, task)
    output_paths = [stage_root / path for path in task.get("required_outputs", [])]
    evidence_paths: list[Path] = []
    for raw_path in [*task.get("input_paths", []), *task.get("required_outputs", [])]:
        if re.search(r"(?:evidence|source|raw|research|verification|manifest|index)", str(raw_path), re.IGNORECASE):
            evidence_paths.append(stage_root / raw_path)
    run_root = REPO_ROOT / plan["run_root"]
    parent_contexts = [run_root / "README.md", run_root / "index.md", run_root / "agentic-flow" / "analyze-and-propose.md"]
    return output_paths, evidence_paths, parent_contexts


def import_semantic_finding(finding: dict[str, Any], task: dict[str, Any], report_path: Path) -> dict[str, Any]:
    imported = dict(finding)
    imported.setdefault("id", f"semantic.{task.get('task_id', 'task')}")
    imported.setdefault("severity", "P1")
    imported.setdefault("message", imported.get("violated_requirement") or "semantic critic finding")
    imported["source_workflow"] = task.get("workflow_key")
    imported["source_task_id"] = task.get("task_id")
    imported["source_stage_id"] = task.get("stage_id")
    imported["source_review"] = "semantic_critic"
    imported["semantic_report"] = repo_relative(report_path)
    return imported


def run_semantic_reviews(
    plan: dict[str, Any],
    validation_summary_path: Path,
    *,
    critic_command: str | None,
    timeout: int,
    written: list[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    semantic_dir = REPO_ROOT / plan["run_root"] / ".workflow" / "semantic-review"
    semantic_dir.mkdir(parents=True, exist_ok=True)
    imported_findings: list[dict[str, Any]] = []
    reviews: list[dict[str, Any]] = []
    for task in plan.get("tasks", []):
        task_id = str(task.get("task_id") or "task")
        report_path = semantic_dir / f"{task_id}.json"
        request_path = semantic_dir / f"{task_id}.request.json"
        output_paths, evidence_paths, parent_contexts = task_semantic_paths(plan, task)
        cmd = [
            "python3",
            repo_relative(SEMANTIC_CRITIC_RUNNER),
            "--packet",
            f"{plan['run_root']}/{task['packet_json']}",
            "--validator-summary",
            repo_relative(validation_summary_path),
            "--request-out",
            repo_relative(request_path),
            "--report-out",
            repo_relative(report_path),
            "--timeout",
            str(timeout),
        ]
        if critic_command:
            cmd.extend(["--critic-command", critic_command])
        for path in output_paths:
            cmd.extend(["--output", repo_relative(path)])
        for path in evidence_paths:
            cmd.extend(["--evidence-ledger", repo_relative(path)])
        for path in parent_contexts:
            if path.exists():
                cmd.extend(["--parent-context", repo_relative(path)])
        proc = subprocess.run(cmd, cwd=REPO_ROOT, text=True, capture_output=True)
        stdout_path = semantic_dir / f"{task_id}-stdout.txt"
        stderr_path = semantic_dir / f"{task_id}-stderr.txt"
        write_text(stdout_path, proc.stdout, written)
        write_text(stderr_path, proc.stderr, written)
        if report_path.exists():
            report = json.loads(report_path.read_text())
        else:
            report = parse_validator_stdout(proc.stdout, "semantic") or {
                "status": "blocked",
                "findings": [{
                    "id": "semantic.runner.no_report",
                    "status": "blocked",
                    "severity": "P0",
                    "violated_requirement": "Semantic critic runner must emit a report.",
                    "evidence": {"path": repo_relative(stdout_path), "quote": proc.stdout[:500]},
                    "required_remediation": "Fix semantic critic runner invocation before trusting semantic gates.",
                }],
            }
            write_json(report_path, report, written)
        reviews.append({
            "task_id": task_id,
            "workflow": task.get("workflow_key"),
            "stage_id": task.get("stage_id"),
            "status": report.get("status"),
            "exit_code": proc.returncode,
            "report_path": repo_relative(report_path),
            "request_path": repo_relative(request_path),
            "stdout": repo_relative(stdout_path),
            "stderr": repo_relative(stderr_path),
            "command_configured": bool(critic_command),
        })
        for finding in report.get("findings", []):
            if isinstance(finding, dict):
                imported_findings.append(import_semantic_finding(finding, task, report_path))
        if report.get("status") == "semantic_review_unavailable" and not report.get("findings"):
            imported_findings.append(import_semantic_finding({
                "id": "semantic.semantic_review_unavailable",
                "severity": "P1",
                "message": "semantic review unavailable",
            }, task, report_path))
    return imported_findings, reviews


def count_findings(findings: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"P0": 0, "P1": 0, "P2": 0, "total": 0}
    for finding in findings:
        severity = str(finding.get("severity") or "").upper()
        if severity in counts:
            counts[severity] += 1
        counts["total"] += 1
    return counts


def validation_status_from_reports(reports: list[dict[str, Any]], findings: list[dict[str, Any]], strict_warnings: bool) -> str:
    report_statuses = {str(report.get("status")) for report in reports}
    counts = count_findings(findings)
    if "blocked" in report_statuses or "fail" in report_statuses or counts["P0"] > 0:
        return "blocked"
    if "review_required" in report_statuses or counts["P1"] > 0:
        return "review_required"
    if strict_warnings and counts["P2"] > 0:
        return "review_required"
    return "pass"


def render_validation_summary(validation: dict[str, Any]) -> str:
    lines = ["# Workflow entrypoint validation", "", f"Status: {validation['status']}", "", "## Commands"]
    for command in validation["commands"]:
        lines.append(f"- {command['workflow']}: exit {command['exit_code']} — `{' '.join(command['command'])}`")
    semantic_review = validation.get("semantic_review") or {}
    lines.extend(["", "## Semantic review", ""])
    if semantic_review.get("enabled"):
        lines.append(f"- Enabled: yes")
        lines.append(f"- Critic command configured: {'yes' if semantic_review.get('command_configured') else 'no'}")
        for review in semantic_review.get("reviews", []):
            lines.append(f"- {review.get('task_id')}: {review.get('status')} — `{review.get('report_path')}`")
    else:
        lines.append("- Enabled: no")
    execution_graph = validation.get("execution_graph") or {}
    lines.extend(["", "## Execution graph", ""])
    lines.append(f"- Status: {execution_graph.get('status', 'not_checked')}")
    lines.append(f"- Checked: {'yes' if execution_graph.get('checked') else 'no'}")
    lines.append(f"- Path: `{execution_graph.get('path', '.workflow/execution-graph.json')}`")
    lines.append(f"- Schema: {execution_graph.get('schema_version') or 'absent'}")
    if execution_graph.get("skipped_reason"):
        lines.append(f"- Skipped reason: {execution_graph['skipped_reason']}")
    graph_counts = execution_graph.get("finding_counts") or {"P0": 0, "P1": 0, "P2": 0, "total": 0}
    lines.append(
        f"- Findings: P0={graph_counts.get('P0', 0)}, P1={graph_counts.get('P1', 0)}, P2={graph_counts.get('P2', 0)}, total={graph_counts.get('total', 0)}"
    )
    graph_findings = execution_graph.get("findings") or []
    if graph_findings:
        lines.append("")
        for finding in graph_findings[:10]:
            field = finding.get("field") or "."
            lines.append(f"- {finding.get('severity')} `{finding.get('id')}` at `{field}` — {finding.get('message')}")
        if len(graph_findings) > 10:
            lines.append(f"- ... {len(graph_findings) - 10} more execution-graph findings in summary.json")
    lines.extend(["", "## Finding counts", ""])
    counts = validation["finding_counts"]
    lines.append(f"- P0: {counts['P0']}")
    lines.append(f"- P1: {counts['P1']}")
    lines.append(f"- P2: {counts['P2']}")
    lines.append(f"- Total: {counts['total']}")
    return "\n".join(lines) + "\n"


def result_from_findings(mode: str, run_root: Path | None, normalized: dict[str, Any] | None, findings: list[Finding], *, status: str) -> RunnerResult:
    exit_code = contracts.STATUS_EXIT_CODES.get(status, 2)
    return RunnerResult(
        mode=mode,
        status=status,
        exit_code=exit_code,
        run_root=repo_relative(run_root) if run_root else None,
        input_sha256=input_sha256(normalized) if normalized else None,
        findings=[asdict(item) for item in findings],
        summary={"findings": len(findings)},
    )


def load_existing_plan(run_root: Path) -> dict[str, Any] | None:
    plan_path = run_root / ".workflow" / "plan.json"
    if not plan_path.exists():
        return None
    return json.loads(plan_path.read_text())


def execute(args: argparse.Namespace) -> RunnerResult:
    raw = load_input(args.input)
    normalized = normalize_input(raw)
    findings = validate_input(normalized)
    fatal = fatal_findings(findings)
    if fatal:
        return result_from_findings(args.mode, None, normalized, fatal, status="input_error")
    run_root = resolve_run_root(normalized, args.run_root)
    if args.mode == "validate":
        existing_plan = load_existing_plan(run_root)
        plan = existing_plan or build_plan(normalized, run_root)
        semantic_review = args.semantic_review or semantic_review_truthy(os.environ.get("WORKFLOW_SEMANTIC_REVIEW"))
        critic_command = args.semantic_critic_command or os.environ.get("WORKFLOW_SEMANTIC_CRITIC_COMMAND")
        critic_timeout = args.semantic_critic_timeout or int(os.environ.get("WORKFLOW_SEMANTIC_CRITIC_TIMEOUT") or "120")
        return validate_run(
            normalized,
            plan,
            strict_warnings=args.strict_warnings,
            semantic_review=semantic_review,
            semantic_critic_command=critic_command,
            semantic_critic_timeout=critic_timeout,
        )
    plan = build_plan(normalized, run_root)
    return scaffold_run(normalized, plan, args.agent, resume=args.resume)


def print_result(result: RunnerResult, fmt: str) -> None:
    if fmt == "json":
        print(result.to_json(), end="")
        return
    if fmt == "markdown":
        print(render_result_markdown(result), end="")
        return
    print(result.to_json(), end="")


def render_result_markdown(result: RunnerResult) -> str:
    lines = ["# Workflow entrypoint result", "", f"Status: {result.status}", f"Exit code: {result.exit_code}"]
    if result.run_root:
        lines.append(f"Run root: `{result.run_root}`")
    if result.next_action:
        lines.extend(["", "## Next action", "", f"Status: {result.next_action.get('status')}", f"Reason: {result.next_action.get('reason')}"])
        first = result.next_action.get("first_packet") or {}
        if first:
            lines.append(f"Packet: `{first.get('markdown')}`")
    if result.validation:
        lines.extend(["", "## Validation", "", f"Status: {result.validation.get('status')}"])
        for report in result.validation.get("reports", []):
            lines.append(f"- {report.get('workflow')}: {report.get('status')} (exit {report.get('exit_code')})")
    if result.findings:
        lines.extend(["", "## Findings", ""])
        for finding in result.findings[:20]:
            lines.append(f"- {finding.get('severity', '?')} `{finding.get('id')}` — {finding.get('message')}")
        if len(result.findings) > 20:
            lines.append(f"- ... {len(result.findings) - 20} more findings")
    return "\n".join(lines) + "\n"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the front-knowledge-base workflow entrypoint.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    analyze = subparsers.add_parser("analyze-propose", help="Scaffold or validate Analyze -> Propose workflow roots.")
    analyze.add_argument("--input", required=True, help="Repository-local JSON input file.")
    analyze.add_argument("--mode", choices=("scaffold", "validate"), default="scaffold")
    analyze.add_argument("--agent", choices=contracts.SUPPORTED_AGENTS, default="generic")
    analyze.add_argument("--format", choices=("json", "markdown"), default="json")
    analyze.add_argument("--run-root", help="Optional run root under dev/implementation.")
    analyze.add_argument("--resume", action="store_true", help="Regenerate packets or validate an existing run root for the same input.")
    analyze.add_argument("--strict-warnings", action="store_true", help="Treat P2 validator findings as review_required during validation.")
    analyze.add_argument("--semantic-review", action="store_true", help="Run independent semantic critic gates during validate mode. Also configurable with WORKFLOW_SEMANTIC_REVIEW=1.")
    analyze.add_argument("--semantic-critic-command", help="Independent critic command. The bounded request JSON path is appended to the command. Defaults to WORKFLOW_SEMANTIC_CRITIC_COMMAND.")
    analyze.add_argument("--semantic-critic-timeout", type=int, help="Semantic critic command timeout in seconds. Defaults to WORKFLOW_SEMANTIC_CRITIC_TIMEOUT or 120.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        parser.print_help()
        return 0
    args = parser.parse_args(argv)
    try:
        result = execute(args)
    except WorkflowInputError as exc:
        result = RunnerResult(mode=getattr(args, "mode", "scaffold"), status="input_error", exit_code=2, findings=[asdict(item) for item in exc.findings], summary={"findings": len(exc.findings)})
    print_result(result, getattr(args, "format", "json"))
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
