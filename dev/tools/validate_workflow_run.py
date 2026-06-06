#!/usr/bin/env python3
"""Deterministic workflow-run compliance validator for front-knowledge-base.

This script is intentionally standard-library only. It emits a stable JSON
report schema and optional Markdown verification output for formal workflow
compliance checks; it does not assess token economics, oracle quality, or
investment suitability.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import workflow_protocol_adapters as protocol_adapters

SCHEMA_VERSION = "workflow-harness-report-v1"
WORKFLOW_IDS = {
    "asset-investment-diligence": "asset-investment-diligence-v1",
    "oracle-analysis": "oracle-analysis-v1",
    "combined-analyze-propose": "combined-analyze-propose-v1",
}
VALID_FORMATS = {"json", "markdown", "json,markdown"}
SEVERITIES = ("P0", "P1", "P2")
FACT_STATES = set(protocol_adapters.FACT_STATES)
INVESTIGATION_FACT_STATES = {"investigated_no_result", "source_unavailable", "source_inconclusive", "contradicted"}
NON_PASS_WORKFLOW_FACT_STATES = INVESTIGATION_FACT_STATES | {"input_missing", "not_investigated"}
UNKNOWN_PLACEHOLDER_PATTERN = re.compile(
    r"\b(?:unknown|not[_ -]?found|not[_ -]?available|not[_ -]?checked|not[_ -]?proven|unverified|unproven|tbd|todo|pending|placeholder)\b",
    re.IGNORECASE,
)
STALE_VALIDATION_PENDING_PATTERN = re.compile(
    r"\b(?:validation|validator|harness)\b.{0,80}\b(?:pending|not yet run|not run|to be run|awaiting)\b|"
    r"\b(?:pending|not yet run|not run|to be run|awaiting)\b.{0,80}\b(?:validation|validator|harness)\b",
    re.IGNORECASE | re.DOTALL,
)
CANONICAL_STAGES = ("Discover", "Analyze", "Propose", "Preview", "Execute", "Monitor")
CHILD_SPECS = {
    "asset": {
        "dir": "asset-investment-diligence",
        "workflow": "asset-investment-diligence-v1",
        "root_check": "flow.child_asset_root_exists",
        "json_check": "flow.child_asset_report_json_valid",
        "validation_check": "flow.child_asset_validation_runs",
        "report_path": "asset-investment-diligence/verification/workflow-harness-report.json",
    },
    "oracle": {
        "dir": "oracle-analysis",
        "workflow": "oracle-analysis-v1",
        "root_check": "flow.child_oracle_root_exists",
        "json_check": "flow.child_oracle_report_json_valid",
        "validation_check": "flow.child_oracle_validation_runs",
        "report_path": "oracle-analysis/verification/workflow-harness-report.json",
    },
}
REQUIRED_CHILD_REPORT_KEYS = {
    "schema_version",
    "workflow",
    "run_root",
    "status",
    "exit_code",
    "summary",
    "findings",
    "checks",
}
CANONICAL_FINAL_VERIFICATIONS = {
    "combined-analyze-propose-v1": "verification/combined-analyze-propose-verification.md",
    "asset-investment-diligence-v1": "verification/final-investment-analysis-verification.md",
    "oracle-analysis-v1": "verification/final-oracle-analysis-verification.md",
}
VALID_ARTIFACT_STATUSES = {"pass", "review_required", "blocked"}
STATUS_BLOCK_REQUIRED_KEYS = (
    "formal_validation_status",
    "semantic_review_status",
    "workflow_decision_status",
    "proposal_gate",
)
DECISION_STATUS_ORDER = {
    "pass": 0,
    "ready": 0,
    "ready_for_preview": 0,
    "not_run": 0,
    "not_applicable": 0,
    "scaffolded": 1,
    "semantic_review_unavailable": 1,
    "review_required": 1,
    "request_more_inputs": 1,
    "blocked": 2,
    "fail": 2,
    "input_error": 2,
}
NON_DECISION_GRADE_STATUSES = {
    "review_required",
    "request_more_inputs",
    "blocked",
    "fail",
    "input_error",
    "semantic_review_unavailable",
}
ASSET_REQUIRED_ROOT_FILES = (
    "README.md",
    "run-manifest.json",
    "index.md",
    "investment-analysis/quantitative-underwriting-methodology.md",
    "investment-analysis/investment-analyst-report-points-pt-risk-return.md",
    "investment-analysis/index.md",
    "verification/final-investment-analysis-verification.md",
)
ASSET_REQUIRED_TOKEN_FILES = ("scope.json", "technical-report.md", "analyst-report.md", "verification.md")
ASSET_REQUIRED_TOKEN_RESEARCH_FILES = (
    "research/onchain-admin.md",
    "research/issuer-backing-security.md",
    "research/transfer-liquidity-oracle-governance.md",
)
ASSET_S1_FACT_SLOTS: dict[str, tuple[str, ...]] = {
    "token_identity": ("token identity", "symbol", "address", "token_address", "scope_slug"),
    "decimals": ("decimals", "decimal"),
    "implementation_proxy_status": ("implementation", "proxy", "upgradeability", "upgradeable"),
    "issuer_protocol_entity": ("issuer", "protocol entity", "issuer/protocol", "protocol"),
    "backing_nav_model": ("backing", "nav", "net asset value", "reserve"),
    "transfer_restrictions": ("transfer restriction", "permissioned", "whitelist", "allowlist", "restricted transfer"),
    "mint_redeem_access": ("mint", "redeem", "redemption", "mint/redeem"),
    "admin_control_surface": ("freeze", "blacklist", "pause", "forced-transfer", "forced transfer", "admin-control", "admin control", "seizure", "seize"),
    "liquidity_depth": ("liquidity", "venue", "pool", "depth", "volume"),
    "oracle_accounting_method": ("oracle", "accounting", "price feed", "pricing"),
    "audits_incidents": ("audit", "incident", "exploit", "security event"),
    "missing_fields_decision_effect": ("missing", "decision effect", "blocker", "unknown", "not_found", "blocked"),
}
ASSET_S2_TECHNICAL_SECTIONS = (
    "Scope and inputs",
    "Source-grounded token facts",
    "Controls and restrictions",
    "Liquidity and oracle surface",
    "Missing fields and decision effect",
    "Technical appendix",
)
ASSET_S2_ANALYST_SECTIONS = (
    "Executive view",
    "What the token represents",
    "Main risk implications",
    "Backing and NAV quality",
    "Liquidity and exit risk",
    "Controls, governance, and legal restrictions",
    "Pricing/oracle risk in plain language",
    "What must be checked before live use",
    "Evidence quality",
    "Source map",
    "Technical appendix pointer",
)
ASSET_S6_REQUIRED_FIELDS: dict[str, tuple[str, ...]] = {
    "gross_roi": ("Gross ROI", "gross_roi"),
    "simple_annualized_return": ("Simple annualized return", "simple_annualized_return"),
    "compound_annualized_return": ("Compound annualized return", "compound_annualized_return"),
    "points_ev": ("Points EV", "points_ev"),
    "points_roi": ("Points ROI", "points_roi"),
    "points_annualized_return": ("Points annualized return", "points_annualized_return"),
    "expected_loss": ("Expected loss", "expected_loss"),
    "exit_cost": ("Exit cost", "exit_cost"),
    "risk_adjusted_roi": ("Risk-adjusted ROI", "risk_adjusted_roi"),
    "risk_adjusted_annualized_return": ("Risk-adjusted annualized return", "risk_adjusted_annualized_return"),
    "break_even_points_roi": ("Break-even points ROI", "break_even_points_roi"),
    "break_even_terminal_drawdown": ("Break-even terminal drawdown", "break_even_terminal_drawdown"),
    "price_stability_certainty_score": ("Price-stability certainty score", "price_stability_certainty_score"),
}
ASSET_STATUS_MARKERS = {"pass", "review_required", "blocked", "fail"}
ASSET_S6_SCENARIO_ELIGIBLE_INPUT_TERMS = (
    "position size",
    "notional",
    "target leverage",
    "leverage",
    "hold horizon",
    "horizon",
    "risk policy",
    "hf floor",
    "health factor",
    "risk budget",
)
ASSET_S6_SCENARIO_BAND_TERMS = (
    "scenario band",
    "scenario-band",
    "scenario matrix",
    "sensitivity band",
    "analyze-only scenario",
    "non-executable scenario",
)
ASSET_S6_SCENARIO_LEVEL_TERMS = ("conservative", "base", "upside", "downside", "severe")


@dataclass
class Finding:
    id: str
    severity: str
    workflow: str
    path: str = "."
    field: str | None = None
    expected: str | None = None
    actual: str | None = None
    message: str = ""
    fix_hint: str | None = None
    source: dict[str, Any] | None = None
    check_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("check_id", None)
        data = {key: value for key, value in data.items() if value is not None}
        return data


@dataclass
class CheckResult:
    id: str
    severity: str
    result: str
    path: str = "."
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Report:
    schema_version: str
    generated_at: str
    workflow: str
    run_root: str
    status: str
    exit_code: int
    summary: dict[str, int]
    inputs: dict[str, Any]
    findings: list[dict[str, Any]]
    checks: list[dict[str, Any]]
    generated_files: list[str]
    formal_validation_status: str = ""
    semantic_review_status: str = ""
    workflow_decision_status: str = ""
    proposal_gate: dict[str, Any] = field(default_factory=dict)
    status_block: dict[str, Any] = field(default_factory=dict)
    formal_validation: dict[str, Any] = field(default_factory=dict)
    workflow_decision: dict[str, Any] = field(default_factory=dict)
    fact_state_summary: dict[str, Any] = field(default_factory=dict)
    rendered_outputs: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationContext:
    workflow_arg: str
    workflow_id: str
    run_root: Path
    repo_root: Path
    formats: str
    strict_warnings: bool
    command: list[str]
    parent_return: str | None = None
    report_dir: Path | None = None
    write_verification: bool = False


class FindingCollector:
    def __init__(self, workflow_id: str, repo_root: Path, run_root: Path) -> None:
        self.workflow_id = workflow_id
        self.repo_root = repo_root
        self.run_root = run_root
        self.findings: list[Finding] = []
        self.checks: list[CheckResult] = []
        self.fact_state_summary: dict[str, Any] = {}
        self.workflow_decision: dict[str, Any] = {}

    def rel(self, path: Path | str | None) -> str:
        if path is None:
            return "."
        if isinstance(path, Path):
            try:
                return repo_relative(path, self.run_root)
            except Exception:
                return repo_relative(path, self.repo_root)
        return str(path)

    def check(
        self,
        check_id: str,
        severity: str,
        ok: bool,
        *,
        path: Path | str | None = None,
        pass_message: str = "pass",
        fail_message: str = "fail",
        expected: str | None = None,
        actual: str | None = None,
        fix_hint: str | None = None,
    ) -> None:
        rel_path = self.rel(path)
        self.checks.append(
            CheckResult(
                id=check_id,
                severity=severity,
                result="pass" if ok else "fail",
                path=rel_path,
                message=pass_message if ok else fail_message,
            )
        )
        if not ok:
            self.findings.append(
                Finding(
                    id=check_id,
                    severity=severity,
                    workflow=self.workflow_id,
                    path=rel_path,
                    expected=expected,
                    actual=actual,
                    message=fail_message,
                    fix_hint=fix_hint,
                )
            )

    def skipped(self, check_id: str, severity: str, *, path: Path | str | None = None, message: str) -> None:
        self.checks.append(
            CheckResult(id=check_id, severity=severity, result="skipped", path=self.rel(path), message=message)
        )

    def finding(
        self,
        finding_id: str,
        severity: str,
        *,
        path: Path | str | None = None,
        field: str | None = None,
        expected: str | None = None,
        actual: str | None = None,
        message: str,
        fix_hint: str | None = None,
        source: dict[str, Any] | None = None,
    ) -> None:
        self.findings.append(
            Finding(
                id=finding_id,
                severity=severity,
                workflow=self.workflow_id,
                path=self.rel(path),
                field=field,
                expected=expected,
                actual=actual,
                message=message,
                fix_hint=fix_hint,
                source=source,
            )
        )


def repo_relative(path: Path, repo_root: Path) -> str:
    path_resolved = path.resolve(strict=False)
    root_resolved = repo_root.resolve(strict=False)
    try:
        return path_resolved.relative_to(root_resolved).as_posix() or "."
    except ValueError:
        return path_resolved.as_posix()


def _strip_path_value(value: str) -> str:
    cleaned = value.strip().strip("`'\"")
    cleaned = cleaned.split("#", 1)[0]
    cleaned = cleaned.rstrip(".,;:)")
    return cleaned.strip()


def resolve_under_root(value: str, *, root: Path, source_file: Path | None = None) -> tuple[Path | None, str | None]:
    cleaned = _strip_path_value(value)
    if not cleaned:
        return None, "empty path"
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", cleaned):
        return None, f"external or absolute URI is not a run-local path: {value}"
    candidate_value = Path(cleaned)
    if candidate_value.is_absolute():
        return None, f"absolute paths are not allowed in run-local artifacts: {value}"
    base = source_file.parent if source_file is not None else root
    root_resolved = root.resolve(strict=False)
    candidate = (base / candidate_value).resolve(strict=False)
    try:
        candidate.relative_to(root_resolved)
    except ValueError:
        return None, f"path escapes run root: {value}"
    return candidate, None


def load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "file does not exist"
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON: {exc.msg} at line {exc.lineno} column {exc.colno}"
    except OSError as exc:
        return None, f"cannot read JSON: {exc}"
    if not isinstance(data, dict):
        return None, "JSON root must be an object"
    return data, None


def load_manifest(run_root: Path) -> tuple[dict[str, Any] | None, list[Finding], list[CheckResult]]:
    workflow_id = "asset-investment-diligence-v1"
    manifest_path = run_root / "run-manifest.json"
    findings: list[Finding] = []
    checks: list[CheckResult] = []
    if not manifest_path.exists():
        checks.append(CheckResult("manifest.file_exists", "P0", "fail", "run-manifest.json", "run-manifest.json is missing"))
        findings.append(
            Finding(
                id="manifest.file_exists",
                severity="P0",
                workflow=workflow_id,
                path="run-manifest.json",
                expected="run-manifest.json present",
                actual="missing",
                message="run-manifest.json is missing",
                fix_hint="Create the run manifest required by the workflow output structure.",
            )
        )
        return None, findings, checks
    data, err = load_json(manifest_path)
    if err:
        checks.append(CheckResult("manifest.json_valid", "P0", "fail", "run-manifest.json", err))
        findings.append(
            Finding(
                id="manifest.json_valid",
                severity="P0",
                workflow=workflow_id,
                path="run-manifest.json",
                expected="parseable JSON object",
                actual=err,
                message=err,
                fix_hint="Fix run-manifest.json so it is valid JSON.",
            )
        )
        return None, findings, checks
    checks.append(CheckResult("manifest.file_exists", "P0", "pass", "run-manifest.json", "run-manifest.json exists"))
    checks.append(CheckResult("manifest.json_valid", "P0", "pass", "run-manifest.json", "run-manifest.json parsed successfully"))
    return data, findings, checks


def extract_markdown_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if match:
            current = _normalize_heading(match.group(2))
            sections.setdefault(current, [])
            continue
        if current is not None:
            sections[current].append(line)
    return {key: "\n".join(value).strip() for key, value in sections.items()}


def _normalize_heading(value: str) -> str:
    value = re.sub(r"[`*_#]+", "", value).strip().lower()
    value = re.sub(r"\s+", " ", value)
    return value


def extract_local_markdown_links(text: str) -> list[str]:
    links: list[str] = []
    for match in re.finditer(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", text):
        target = match.group(1).strip()
        if _is_local_target(target):
            links.append(target)
    for match in re.finditer(r"\[\[([^\]]+)\]\]", text):
        target = match.group(1).split("|", 1)[0].strip()
        if _is_local_target(target):
            links.append(target)
    return links


def _is_local_target(target: str) -> bool:
    target = target.strip()
    if not target or target.startswith("#"):
        return False
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
        return False
    return True


def extract_code_spanned_paths(text: str) -> list[str]:
    paths: list[str] = []
    suffixes = (".md", ".json", ".txt", ".csv", ".yaml", ".yml")
    for match in re.finditer(r"`([^`]+)`", text):
        value = _strip_path_value(match.group(1))
        if not value or " " in value or value.startswith("--"):
            continue
        if "/" in value or value.endswith(suffixes):
            if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", value):
                paths.append(value)
    return paths


def has_skipped_marker(text: str, topic: str) -> bool:
    lower = text.lower()
    topic_lower = topic.lower()
    markers = ("skipped", "not_in_scope", "not in scope", "not applicable", f"no {topic_lower} in scope")
    return topic_lower in lower and any(marker in lower for marker in markers)


def validate_common(ctx: ValidationContext) -> tuple[list[Finding], list[CheckResult], dict[str, Any]]:
    collector = FindingCollector(ctx.workflow_id, ctx.repo_root, ctx.run_root)
    collector.check("cli.input_valid", "P0", True, path=".", pass_message="CLI arguments accepted")
    root_ok = ctx.run_root.exists() and ctx.run_root.is_dir()
    collector.check(
        "run_root.exists",
        "P0",
        root_ok,
        path=ctx.run_root,
        pass_message="run root exists and is a directory",
        fail_message="run root does not exist or is not a directory",
        expected="existing directory",
        actual=str(ctx.run_root),
        fix_hint="Pass --run-root pointing to the workflow run artifact root.",
    )
    inputs: dict[str, Any] = {"manifest": None, "final_index": None, "final_verification": None, "parent_return": None}
    if not root_ok:
        return collector.findings, collector.checks, inputs

    if ctx.workflow_arg == "combined-analyze-propose":
        collector.skipped(
            "manifest.file_exists",
            "P0",
            path="run-manifest.json",
            message="combined manifest deferred until M5; M4 uses parent index plus child reports",
        )
        return collector.findings, collector.checks, inputs

    manifest_path = ctx.run_root / "run-manifest.json"
    if not manifest_path.exists():
        collector.check(
            "manifest.file_exists",
            "P0",
            False,
            path=manifest_path,
            fail_message="run-manifest.json is missing",
            expected="run-manifest.json present",
            actual="missing",
            fix_hint="Create run-manifest.json at the workflow run root.",
        )
    else:
        collector.check("manifest.file_exists", "P0", True, path=manifest_path, pass_message="run-manifest.json exists")
        manifest, err = load_json(manifest_path)
        collector.check(
            "manifest.json_valid",
            "P0",
            err is None,
            path=manifest_path,
            pass_message="run-manifest.json parsed successfully",
            fail_message=err or "run-manifest.json is invalid",
            expected="parseable JSON object",
            actual=err,
            fix_hint="Fix run-manifest.json so it is valid JSON.",
        )
        if manifest:
            inputs["manifest"] = repo_relative(manifest_path, ctx.run_root)
            inputs["final_index"] = manifest.get("final_index")
            inputs["final_verification"] = manifest.get("final_verification")

    if ctx.workflow_arg == "oracle-analysis":
        validate_oracle_analysis(ctx, collector, inputs)
    elif ctx.workflow_arg == "asset-investment-diligence":
        validate_asset_investment_diligence(ctx, collector, inputs)
    elif not any(f.severity == "P0" for f in collector.findings):
        collector.finding(
            "validator.workflow_checks_deferred",
            "P1",
            path=".",
            expected="workflow-specific checks implemented before production pass",
            actual="common validator core only",
            message="Workflow-specific checks are deferred for this workflow in the current validator slice, so this report cannot be treated as a production pass.",
            fix_hint="Run the later workflow-specific validator milestone for this workflow before using the report as production evidence.",
        )
    return collector.findings, collector.checks, inputs



def _asset_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _asset_json_text(path: Path) -> str:
    data, err = load_json(path)
    if err or data is None:
        return _asset_read_text(path)
    return json.dumps(data, sort_keys=True, ensure_ascii=False)


def _asset_norm(value: str) -> str:
    value = value.lower().replace("&", " and ")
    value = value.replace("_", " ").replace("-", " ")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _asset_contains_label(text: str, labels: Iterable[str]) -> bool:
    norm_text = _asset_norm(text)
    return any(_asset_norm(label) in norm_text for label in labels)


def _asset_status_from_text(text: str) -> str | None:
    match = re.search(r"(?im)\b(?:final\s+validation\s+status|final\s+status|validation\s+status|status)\s*[:|]\s*(pass|review_required|blocked|fail)\b", text)
    return match.group(1) if match else None


def _asset_norm_status(value: Any) -> str | None:
    if isinstance(value, str):
        lowered = value.strip().lower().replace(" ", "_").replace("-", "_")
        return lowered if lowered in ASSET_STATUS_MARKERS else lowered or None
    return None


def _asset_status_rank(status: str | None) -> int:
    order = {"pass": 0, "review_required": 1, "blocked": 2, "fail": 3}
    return order.get(status or "", -1)


def _asset_manifest_tokens(manifest: dict[str, Any] | None) -> list[dict[str, Any]]:
    tokens = manifest.get("tokens") if isinstance(manifest, dict) else None
    return [token for token in tokens if isinstance(token, dict)] if isinstance(tokens, list) else []


def _asset_scope_id(token: dict[str, Any]) -> str:
    return str(token.get("token_slug") or token.get("scope_slug") or token.get("symbol") or "token").strip() or "token"


def _asset_expected_token_dir(token: dict[str, Any]) -> str:
    return f"tokens/{_asset_scope_id(token)}"


def _asset_manifest_path(manifest: dict[str, Any], key: str, *, root: Path, default: str | None = None) -> tuple[str | None, Path | None, str | None]:
    value = manifest.get(key, default)
    if not isinstance(value, str) or not value.strip():
        return None, None, "missing or non-string path"
    resolved, err = resolve_under_root(value, root=root)
    return value, resolved, err


def _asset_stage_reason_from_manifest(manifest: dict[str, Any] | None, stage: str) -> tuple[bool, bool]:
    skipped = manifest.get("skipped_stages") if isinstance(manifest, dict) else None
    if isinstance(skipped, dict):
        for key, value in skipped.items():
            if stage.lower() in str(key).lower():
                if isinstance(value, dict):
                    reason = str(value.get("reason") or value.get("because") or "").strip()
                    return True, bool(reason)
                if isinstance(value, str):
                    return True, bool(value.strip())
                return True, False
    if isinstance(skipped, list):
        for item in skipped:
            text = json.dumps(item, sort_keys=True) if isinstance(item, (dict, list)) else str(item)
            if stage.lower() in text.lower():
                return True, any(word in text.lower() for word in ("reason", "because", "no ", "not_in_scope", "not in scope", "missing"))
    return False, False


def _asset_marker_from_text(text: str, stage: str, topic: str) -> tuple[bool, bool]:
    lower = text.lower()
    stage_lower = stage.lower()
    topic_lower = topic.lower()
    present = (stage_lower in lower or topic_lower in lower) and any(marker in lower for marker in ("skipped", "not_in_scope", "not in scope", "not applicable", "no "))
    if not present:
        return False, False
    reason = any(word in lower for word in ("reason", "because", "due to", f"no {topic_lower}", "not supplied", "not provided", "not_in_scope"))
    return True, reason


def _asset_has_section(sections: dict[str, str], label: str) -> bool:
    target = _asset_norm(label)
    return any(_asset_norm(section) == target for section in sections)


def _asset_find_labeled_line(text: str, labels: Iterable[str]) -> tuple[str | None, bool]:
    label_norms = [_asset_norm(label) for label in labels]
    heading_only = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        line_norm = _asset_norm(line)
        if any(label in line_norm for label in label_norms):
            if line.startswith("#"):
                heading_only = True
                continue
            if re.match(r"^\|?\s*-{3,}\s*\|", line):
                continue
            return line, heading_only
    return None, heading_only


def _asset_line_has_value_state(line: str) -> bool:
    state_words = ("not_in_scope", "not in scope", "skipped_due_to_missing_input", "scenario_band", "scenario band", "unknown", "blocked", "null", "n/a")
    if any(word in line.lower() for word in state_words):
        return True
    return bool(re.search(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?\s*(?:%|bps|x)?(?![A-Za-z])", line))


def _asset_line_is_non_numeric(line: str) -> bool:
    return not bool(re.search(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?\s*(?:%|bps|x)?(?![A-Za-z])", line))


def _asset_non_numeric_has_reason(line: str) -> bool:
    lower = line.lower()
    if any(word in lower for word in ("reason", "because", "due to", "no ", "not relevant", "missing input", "not supplied", "not provided")):
        return True
    if "|" in line:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        state_idx = next((idx for idx, cell in enumerate(cells) if any(word in cell.lower() for word in ("not_in_scope", "skipped_due_to_missing_input", "scenario_band", "scenario band", "unknown", "blocked", "null", "n/a"))), -1)
        if state_idx >= 0:
            return any(cell for idx, cell in enumerate(cells) if idx > state_idx)
    return False


def _asset_s6_line_is_scenario_eligible_skip(line: str) -> bool:
    lower = line.lower()
    skip_state = any(term in lower for term in ("skipped_due_to_missing_input", "skipped due to missing input", "missing input", "not supplied", "not provided"))
    return skip_state and any(term in lower for term in ASSET_S6_SCENARIO_ELIGIBLE_INPUT_TERMS)


def _asset_s6_has_scenario_bands(text: str) -> bool:
    lower = text.lower()
    if not any(term in lower for term in ASSET_S6_SCENARIO_BAND_TERMS):
        return False
    if "non-executable" not in lower and "analyze-only" not in lower and "analysis-only" not in lower:
        return False
    level_count = sum(1 for term in ASSET_S6_SCENARIO_LEVEL_TERMS if term in lower)
    numeric_count = len(re.findall(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?\s*(?:%|bps|x|days?|weeks?|months?|usd|\$)?(?![A-Za-z])", text, flags=re.IGNORECASE))
    return level_count >= 2 and numeric_count >= 3


def _asset_final_claims_pass(text: str) -> bool:
    lower = text.lower()
    return bool(re.search(r"\b(?:final\s+validation\s+status|final\s+status|status)\s*[:|]\s*pass\b", lower)) or "all required" in lower and "pass" in lower


def _asset_ready_overclaim(text: str) -> bool:
    lower = text.lower()
    claims = ("execution-ready", "allocation-ready", "ready to execute", "ready to allocate", "ready for allocation", "ready for live use")
    negations = ("not execution-ready", "not allocation-ready", "not ready to execute", "not ready to allocate", "not ready for allocation", "not ready for live use", "cannot execute", "cannot allocate")
    return any(claim in lower for claim in claims) and not any(neg in lower for neg in negations)


def _asset_section_groups_present(text: str, groups: Iterable[tuple[str, tuple[str, ...]]]) -> tuple[bool, list[str]]:
    lower = text.lower()
    missing: list[str] = []
    for name, terms in groups:
        if not all(term.lower() in lower for term in terms):
            missing.append(name)
    return not missing, missing


def validate_asset_investment_diligence(ctx: ValidationContext, collector: FindingCollector, inputs: dict[str, Any]) -> None:
    root = ctx.run_root
    manifest_path = root / "run-manifest.json"
    manifest: dict[str, Any] | None = None
    if manifest_path.exists():
        manifest, manifest_err = load_json(manifest_path)
        if manifest_err:
            manifest = None
    inputs["manifest"] = "run-manifest.json" if manifest is not None else inputs.get("manifest")

    # Manifest schema and declared path reconciliation.
    required_manifest_fields = (
        "workflow_id",
        "run_id",
        "run_artifact_root",
        "tokens",
        "pt_markets",
        "x_research_scopes",
        "final_index",
        "final_verification",
    )
    if manifest is not None:
        for field in required_manifest_fields:
            collector.check(
                "asset.manifest.required_field_present",
                "P1",
                field in manifest,
                path=manifest_path,
                pass_message=f"manifest field {field} is present",
                fail_message=f"manifest field {field} is missing",
                expected=field,
                actual="missing",
                fix_hint="Add the required asset-investment-diligence manifest field without changing workflow semantics.",
            )
        collector.check(
            "asset.manifest.workflow_id",
            "P0",
            manifest.get("workflow_id") == ctx.workflow_id,
            path=manifest_path,
            pass_message="manifest workflow_id matches asset-investment-diligence-v1",
            fail_message="manifest workflow_id does not match asset-investment-diligence-v1",
            expected=ctx.workflow_id,
            actual=str(manifest.get("workflow_id")),
            fix_hint="Set run-manifest.json.workflow_id to asset-investment-diligence-v1.",
        )
        declared_root = manifest.get("run_artifact_root")
        root_ok = False
        if isinstance(declared_root, str) and declared_root.strip():
            candidate = Path(declared_root)
            if not candidate.is_absolute():
                candidate = ctx.repo_root / candidate
            root_ok = candidate.resolve(strict=False) == root.resolve(strict=False)
        collector.check(
            "asset.manifest.run_artifact_root_reconciles",
            "P0",
            root_ok,
            path=manifest_path,
            pass_message="manifest run_artifact_root resolves to the supplied run root",
            fail_message="manifest run_artifact_root does not resolve to the supplied run root",
            expected=repo_relative(root, ctx.repo_root),
            actual=str(declared_root),
            fix_hint="Point run_artifact_root at the actual run artifact folder.",
        )
        for key, expected_rel in (("final_index", "index.md"), ("final_verification", CANONICAL_FINAL_VERIFICATIONS[ctx.workflow_id])):
            raw, resolved, err = _asset_manifest_path(manifest, key, root=root, default=expected_rel)
            ok = err is None and resolved is not None and resolved.exists()
            collector.check(
                "asset.manifest.declared_path_resolves",
                "P0",
                ok,
                path=manifest_path,
                pass_message=f"manifest {key} resolves under run root",
                fail_message=f"manifest {key} does not resolve under run root",
                expected=f"existing run-local path for {key}",
                actual=err or raw or "missing",
                fix_hint="Use run-local relative paths for final_index and final_verification and ensure the targets exist.",
            )
            expected_ok = raw == expected_rel
            collector.check(
                "asset.manifest.canonical_path_declared",
                "P1",
                expected_ok,
                path=manifest_path,
                pass_message=f"manifest {key} uses the canonical asset path",
                fail_message=f"manifest {key} does not use the canonical asset path",
                expected=expected_rel,
                actual=raw,
                fix_hint="Use the canonical asset workflow final index and verification paths.",
            )
            if key == "final_index":
                inputs["final_index"] = raw
            else:
                inputs["final_verification"] = raw

    tokens = _asset_manifest_tokens(manifest)
    collector.check(
        "asset.manifest.token_entries_present",
        "P0",
        bool(tokens),
        path=manifest_path,
        pass_message="manifest declares at least one token scope",
        fail_message="manifest must declare at least one token scope",
        expected="tokens[] with token_slug/address/artifact_dir",
        actual="missing or empty",
        fix_hint="Declare each analyzed token in run-manifest.json.tokens.",
    )
    token_dirs: list[tuple[dict[str, Any], Path]] = []
    for token in tokens:
        slug = _asset_scope_id(token)
        expected_dir_rel = _asset_expected_token_dir(token)
        artifact_dir = token.get("artifact_dir") or expected_dir_rel
        artifact_dir_ok = artifact_dir == expected_dir_rel
        token_dir = root / expected_dir_rel
        token_dirs.append((token, token_dir))
        collector.check(
            "asset.manifest.artifact_dir_reconciles",
            "P0",
            artifact_dir_ok,
            path=manifest_path,
            pass_message=f"token {slug} artifact_dir matches tokens/<slug>",
            fail_message=f"token {slug} artifact_dir does not match tokens/<slug>",
            expected=expected_dir_rel,
            actual=str(artifact_dir),
            fix_hint="Set each token artifact_dir to tokens/<token_slug>.",
        )
        scope_path = token_dir / "scope.json"
        scope, scope_err = load_json(scope_path)
        scope_ok = scope_err is None and isinstance(scope, dict)
        collector.check(
            "asset.scope.json_valid",
            "P0",
            scope_ok,
            path=scope_path,
            pass_message=f"{slug} scope.json parses",
            fail_message=f"{slug} scope.json is missing or invalid",
            expected="parseable scope.json object",
            actual=scope_err,
            fix_hint="Create a parseable token scope.json for each token scope.",
        )
        if scope_ok and scope is not None:
            manifest_addr = str(token.get("token_address") or token.get("address") or "").lower()
            scope_addr = str(scope.get("token_address") or scope.get("address") or "").lower()
            scope_slug = str(scope.get("token_slug") or scope.get("scope_slug") or "")
            identity_ok = (not manifest_addr or manifest_addr == scope_addr) and (not scope_slug or scope_slug == slug)
            collector.check(
                "asset.scope.identity_reconciles",
                "P0",
                identity_ok,
                path=scope_path,
                pass_message=f"{slug} scope identity reconciles with manifest",
                fail_message=f"{slug} scope identity does not reconcile with manifest",
                expected=f"slug={slug} address={manifest_addr}",
                actual=f"slug={scope_slug} address={scope_addr}",
                fix_hint="Keep token_slug/scope_slug and token_address consistent between manifest and scope.json.",
            )

    # Required root and token files.
    for rel in ASSET_REQUIRED_ROOT_FILES:
        path = root / rel
        collector.check(
            "asset.root.required_file_exists",
            "P0",
            path.exists() and path.is_file(),
            path=path,
            pass_message=f"required root file exists: {rel}",
            fail_message=f"required root file missing: {rel}",
            expected=rel,
            actual="missing",
            fix_hint="Create every required run-level asset workflow artifact.",
        )
    for _token, token_dir in token_dirs:
        for rel in ASSET_REQUIRED_TOKEN_FILES:
            path = token_dir / rel
            collector.check(
                "asset.token.required_file_exists",
                "P0",
                path.exists() and path.is_file(),
                path=path,
                pass_message=f"required token file exists: {token_dir.name}/{rel}",
                fail_message=f"required token file missing: {token_dir.name}/{rel}",
                expected=rel,
                actual="missing",
                fix_hint="Create the required per-token file set.",
            )
        for rel in ASSET_REQUIRED_TOKEN_RESEARCH_FILES:
            path = token_dir / rel
            collector.check(
                "asset.token.required_research_file_exists",
                "P0",
                path.exists() and path.is_file(),
                path=path,
                pass_message=f"required token research file exists: {token_dir.name}/{rel}",
                fail_message=f"required token research file missing: {token_dir.name}/{rel}",
                expected=rel,
                actual="missing",
                fix_hint="Create all required per-token research files.",
            )

    missing_s1 = 0
    missing_s2 = 0
    missing_s6_fields: list[str] = []
    s6_field_state_failures = 0

    for _token, token_dir in token_dirs:
        s1_text_parts = [_asset_json_text(token_dir / "scope.json")]
        for rel in ASSET_REQUIRED_TOKEN_RESEARCH_FILES:
            s1_text_parts.append(_asset_read_text(token_dir / rel))
        s1_text_parts.append(_asset_read_text(token_dir / "technical-report.md"))
        s1_text = "\n".join(s1_text_parts)
        for slot, labels in ASSET_S1_FACT_SLOTS.items():
            ok = _asset_contains_label(s1_text, labels)
            if not ok:
                missing_s1 += 1
            collector.check(
                "asset.s1.required_fact_slot_present",
                "P1",
                ok,
                path=token_dir,
                pass_message=f"S1 fact slot present: {slot}",
                fail_message=f"S1 fact slot missing: {slot}",
                expected=slot,
                actual="missing",
                fix_hint="Name every required S1 fact slot with a value or explicit unknown/not_in_scope/blocked state.",
            )
        state_words_present = any(word in s1_text.lower() for word in ("unknown", "not_found", "not in scope", "not_in_scope", "blocked"))
        decision_effect_present = any(word in s1_text.lower() for word in ("decision effect", "blocker", "reason", "because", "impact"))
        collector.check(
            "asset.s1.unknown_has_decision_effect",
            "P1",
            (not state_words_present) or decision_effect_present,
            path=token_dir,
            pass_message="unknown or blocked S1 states include decision effect context",
            fail_message="unknown or blocked S1 states are missing decision effect context",
            expected="unknown/not_found/not_in_scope/blocked states tied to decision effect",
            actual="state present without decision effect",
            fix_hint="For every unknown or blocked S1 fact, state what decision it affects.",
        )

        analyst_path = token_dir / "analyst-report.md"
        analyst_text = _asset_read_text(analyst_path)
        sections = extract_markdown_sections(analyst_text)
        for section in ASSET_S2_ANALYST_SECTIONS:
            if section == "Source map":
                continue
            if section == "Technical appendix pointer":
                continue
            ok = _asset_has_section(sections, section)
            if not ok:
                missing_s2 += 1
            collector.check(
                "asset.s2.required_section_present",
                "P1",
                ok,
                path=analyst_path,
                pass_message=f"S2 analyst section present: {section}",
                fail_message=f"S2 analyst section missing: {section}",
                expected=section,
                actual="missing",
                fix_hint="Add the required analyst-report.md section heading.",
            )
        source_map_ok = _asset_has_section(sections, "Source map")
        if not source_map_ok:
            missing_s2 += 1
        collector.check(
            "asset.s2.source_map_present",
            "P1",
            source_map_ok,
            path=analyst_path,
            pass_message="S2 Source map section is present",
            fail_message="S2 Source map section is missing",
            expected="Source map heading or explicit block",
            actual="missing",
            fix_hint="Add a Source map section; prose mentions elsewhere are insufficient.",
        )
        appendix_ok = _asset_has_section(sections, "Technical appendix pointer") or ("technical appendix" in analyst_text.lower() and "technical-report.md" in analyst_text.lower())
        if not appendix_ok:
            missing_s2 += 1
        collector.check(
            "asset.s2.technical_appendix_pointer_present",
            "P1",
            appendix_ok,
            path=analyst_path,
            pass_message="S2 technical appendix pointer is present",
            fail_message="S2 technical appendix pointer is missing",
            expected="Technical appendix pointer to technical-report.md",
            actual="missing",
            fix_hint="Add a Technical appendix pointer section or labeled block linking to the token technical report.",
        )

    # Skipped PT and X/social markers.
    pt_markets = manifest.get("pt_markets") if isinstance(manifest, dict) else []
    x_scopes = manifest.get("x_research_scopes") if isinstance(manifest, dict) else []
    pt_empty = not isinstance(pt_markets, list) or len(pt_markets) == 0
    x_empty = not isinstance(x_scopes, list) or len(x_scopes) == 0
    pt_index = root / "pt-markets" / "index.md"
    x_index = root / "x-research" / "index.md"
    if pt_empty:
        pt_text = _asset_read_text(pt_index)
        manifest_present, manifest_reason = _asset_stage_reason_from_manifest(manifest, "S3_pt_market_economics")
        text_present, text_reason = _asset_marker_from_text(pt_text, "S3_pt_market_economics", "pt")
        collector.check("asset.skipped_pt.index_exists", "P1", pt_index.exists(), path=pt_index, pass_message="PT skipped index exists", fail_message="pt-markets/index.md is missing for empty PT scope", expected="pt-markets/index.md", actual="missing", fix_hint="Create pt-markets/index.md with an explicit skipped marker and reason.")
        collector.check("asset.skipped_pt.marker_present", "P1", manifest_present or text_present, path=pt_index if text_present else manifest_path, pass_message="PT skipped marker present", fail_message="PT scope is empty without an explicit skipped marker", expected="S3_pt_market_economics skipped marker", actual="missing", fix_hint="Record S3_pt_market_economics as skipped in the manifest or pt-markets/index.md.")
        collector.check("asset.skipped_pt.reason_present", "P1", manifest_reason or text_reason, path=pt_index if text_present else manifest_path, pass_message="PT skipped marker has a reason", fail_message="PT skipped marker is missing a reason", expected="reason for skipped PT market economics", actual="missing", fix_hint="State why no PT market was analyzed.")
    else:
        collector.finding("asset.pt_social.full_validation_out_of_scope", "P2", path="pt-markets", message="PT market validation is outside the M2 asset harness slice; review the dedicated workflow before treating PT economics as fully validated.", fix_hint="Run the later PT/social validation slice for non-empty PT market scopes.")
    if x_empty:
        x_text = _asset_read_text(x_index)
        s4_present, s4_reason = _asset_stage_reason_from_manifest(manifest, "S4_x_social_mining")
        s5_present, s5_reason = _asset_stage_reason_from_manifest(manifest, "S5_x_social_synthesis")
        text4_present, text4_reason = _asset_marker_from_text(x_text, "S4_x_social_mining", "x")
        text5_present, text5_reason = _asset_marker_from_text(x_text, "S5_x_social_synthesis", "x")
        collector.check("asset.skipped_social.index_exists", "P1", x_index.exists(), path=x_index, pass_message="X/social skipped index exists", fail_message="x-research/index.md is missing for empty X/social scope", expected="x-research/index.md", actual="missing", fix_hint="Create x-research/index.md with explicit skipped markers and reasons.")
        collector.check("asset.skipped_social.marker_present", "P1", (s4_present or text4_present) and (s5_present or text5_present), path=x_index, pass_message="X/social skipped markers present", fail_message="X/social scope is empty without both skipped markers", expected="S4 and S5 skipped markers", actual="missing", fix_hint="Record S4_x_social_mining and S5_x_social_synthesis as skipped.")
        collector.check("asset.skipped_social.reason_present", "P1", (s4_reason or text4_reason) and (s5_reason or text5_reason), path=x_index, pass_message="X/social skipped markers have reasons", fail_message="X/social skipped markers are missing reasons", expected="reasons for skipped S4 and S5", actual="missing", fix_hint="State why X/social mining and synthesis were skipped.")
    else:
        collector.finding("asset.pt_social.full_validation_out_of_scope", "P2", path="x-research", message="X/social validation is outside the M2 asset harness slice; review the dedicated workflow before treating social evidence as fully validated.", fix_hint="Run the later PT/social validation slice for non-empty X/social scopes.")

    # S6 quantitative fields.
    s6_paths = [root / "investment-analysis" / "quantitative-underwriting-methodology.md", root / "investment-analysis" / "investment-analyst-report-points-pt-risk-return.md", root / "investment-analysis" / "index.md"]
    s6_text = "\n".join(_asset_read_text(path) for path in s6_paths)
    broad_s6_claim = any(heading in s6_text.lower() for heading in ("gross return stack", "risk-adjusted return stack", "risk adjusted return stack", "points valuation", "price-stability certainty", "price stability certainty"))
    scenario_eligible_skip_lines: list[str] = []
    for field, labels in ASSET_S6_REQUIRED_FIELDS.items():
        line, heading_only = _asset_find_labeled_line(s6_text, labels)
        present = line is not None
        if not present:
            missing_s6_fields.append(field)
        collector.check("asset.s6.required_field_present", "P1", present, path="investment-analysis", pass_message=f"S6 field present: {field}", fail_message=f"S6 field missing: {field}", expected=" or ".join(labels), actual="heading-only" if heading_only else "missing", fix_hint="Add an exact labeled S6 field with a numeric value or allowed explicit state.")
        if present and line is not None:
            has_value = _asset_line_has_value_state(line)
            if not has_value:
                s6_field_state_failures += 1
            collector.check("asset.s6.required_field_has_value_state", "P1", has_value, path="investment-analysis", pass_message=f"S6 field has value state: {field}", fail_message=f"S6 field lacks a numeric value or allowed explicit state: {field}", expected="numeric | scenario_band | null | not_in_scope | skipped_due_to_missing_input | unknown | blocked", actual=line, fix_hint="Add a machine-readable or explicitly labeled value state for every required S6 field.")
            if _asset_s6_line_is_scenario_eligible_skip(line):
                scenario_eligible_skip_lines.append(line)
            if _asset_line_is_non_numeric(line):
                reason_ok = _asset_non_numeric_has_reason(line)
                if not reason_ok:
                    s6_field_state_failures += 1
                collector.check("asset.s6.non_numeric_value_has_reason", "P1", reason_ok, path="investment-analysis", pass_message=f"S6 non-numeric state has reason: {field}", fail_message=f"S6 non-numeric state lacks a reason: {field}", expected="reason on the same row/object/labeled block", actual=line, fix_hint="For non-numeric S6 states, add the reason beside the field.")
    scenario_band_ok = not scenario_eligible_skip_lines or _asset_s6_has_scenario_bands(s6_text)
    if not scenario_band_ok:
        s6_field_state_failures += len(scenario_eligible_skip_lines)
    collector.check(
        "asset.s6.skipped_calculation_requires_analyze_only_scenario_band",
        "P1",
        scenario_band_ok,
        path="investment-analysis",
        pass_message="S6 missing sizing/horizon/policy skips are backed by Analyze-only scenario bands",
        fail_message="S6 skips calculations for scenario-eligible missing inputs without Analyze-only scenario bands",
        expected="labelled non-executable conservative/base/upside scenario bands with numeric assumptions and outputs",
        actual="; ".join(scenario_eligible_skip_lines[:3]) or "no scenario-eligible skips",
        fix_hint="When only sizing/leverage/horizon/risk-policy inputs are missing, keep Proposal as request_more_inputs but provide non-executable Analyze-only scenario bands instead of skipping all calculations.",
    )
    collector.check("asset.s6.heading_only_false_pass", "P1", not (broad_s6_claim and missing_s6_fields), path="investment-analysis", pass_message="broad S6 headings do not mask missing exact fields", fail_message="broad S6 calculation headings appear while exact required fields are missing", expected="exact required field labels with value states", actual=", ".join(missing_s6_fields), fix_hint="Do not count broad calculation group headings as exact S6 field evidence.")

    # Final verification and top-level handoff checks.
    final_path = root / CANONICAL_FINAL_VERIFICATIONS[ctx.workflow_id]
    final_text = _asset_read_text(final_path)
    final_exists = final_path.exists() and final_path.is_file()
    collector.check("asset.final_verification.file_exists", "P0", final_exists, path=final_path, pass_message="canonical final investment verification exists", fail_message="canonical final investment verification is missing", expected=CANONICAL_FINAL_VERIFICATIONS[ctx.workflow_id], actual="missing", fix_hint="Create verification/final-investment-analysis-verification.md.")
    final_status = _asset_status_from_text(final_text)
    _check_final_verification_not_pending(
        collector,
        "asset.final_verification.not_pending",
        path=final_path,
        text=final_text,
        workflow_label="asset-investment-diligence",
    )
    collector.check("asset.final_verification.status_present", "P1", final_status in ASSET_STATUS_MARKERS, path=final_path, pass_message="final verification status marker present", fail_message="final verification status marker missing", expected="pass | review_required | blocked | fail", actual=str(final_status), fix_hint="Add a final status marker to the final verification artifact.")
    collector.check("asset.final_verification.required_file_checks_present", "P1", all(term in final_text.lower() for term in ("required", "root file", "per-token", "manifest")), path=final_path, pass_message="final verification records required file checks", fail_message="final verification does not record required file/root/token/manifest checks", expected="required root files, per-token files, manifest paths", actual="missing", fix_hint="Record direct evidence that required root/per-token files and manifest paths were checked.")
    field_terms_ok = all(term in final_text.lower() for term in ("s1", "s2", "s6")) and any(term in final_text.lower() for term in ("required field", "quantitative field", "compound annualized return"))
    collector.check("asset.final_verification.required_field_checks_present", "P1", field_terms_ok, path=final_path, pass_message="final verification records S1/S2/S6 checks", fail_message="final verification does not record S1/S2/S6 required section/field checks", expected="S1/S2/S6 required checks", actual="missing", fix_hint="Record S1 fact slots, S2 sections, and exact S6 quantitative fields in final verification.")
    skipped_ok = "skipped" in final_text.lower() and ("s3" in final_text.lower() or "pt" in final_text.lower()) and ("s4" in final_text.lower() or "s5" in final_text.lower() or "social" in final_text.lower())
    collector.check("asset.final_verification.skipped_stage_checks_present", "P1", skipped_ok, path=final_path, pass_message="final verification records skipped-stage checks", fail_message="final verification does not record PT/social skipped-stage checks", expected="S3/S4/S5 skipped-stage checks", actual="missing", fix_hint="Record skipped-stage checks for empty PT and X/social scopes.")
    cross_ok = any(term in final_text.lower() for term in ("cross-link", "cross link", "links.local_paths_resolve", "local link")) and any(term in final_text.lower() for term in ("pass", "resolved", "checked"))
    collector.check("asset.final_verification.cross_links_checked", "P1", cross_ok, path=final_path, pass_message="final verification records cross-link checks", fail_message="final verification does not record cross-link resolution checks", expected="cross-link/local link resolution evidence", actual="missing", fix_hint="Record local Markdown/Obsidian link resolution evidence in final verification.")
    workspace_ok = "workspace validation" in final_text.lower() and any(term in final_text.lower() for term in ("exit status", "exit code", "pass", "failed unrelated", "unrelated failure"))
    collector.check("asset.final_verification.workspace_validation_present", "P1", workspace_ok, path=final_path, pass_message="final verification records workspace validation evidence", fail_message="final verification does not record workspace validation command evidence", expected="workspace validation commands with command text and exit status", actual="missing", fix_hint="Record command text and exit status for workspace validation, or isolate unrelated failures.")
    detected_content_issues = missing_s1 + missing_s2 + len(missing_s6_fields) + s6_field_state_failures
    collector.check("asset.final_verification.overclaim", "P1", not (detected_content_issues and _asset_final_claims_pass(final_text)), path=final_path, pass_message="final verification does not overclaim pass against detected content issues", fail_message="final verification claims pass despite detected required content issues", expected="review_required/fail/blocker status when required content is missing", actual="pass claim with detected issues", fix_hint="Reconcile final verification status with validator-detected missing required sections/fields.")
    combined_text = "\n".join([final_text, _asset_read_text(root / "README.md"), _asset_read_text(root / "index.md"), json.dumps(manifest or {}, sort_keys=True)])
    unresolved_present = any(term in combined_text.lower() for term in ("blocked", "unknown", "missing live", "issuer eligibility", "feed support", "route support", "user policy", "live-use blocker", "not_found"))
    collector.check("asset.final_verification.no_unsupported_execution_ready_claim", "P1", not (unresolved_present and _asset_ready_overclaim(combined_text)), path=final_path, pass_message="final verification avoids unsupported execution/allocation-ready claims", fail_message="run claims execution/allocation readiness despite unresolved blockers", expected="no unsupported execution-ready/allocation-ready claim", actual="ready claim with unresolved blocker text", fix_hint="Remove execution/allocation-ready claims unless live prerequisites are actually validated.")

    readme_path = root / "README.md"
    index_path = root / "index.md"
    readme_ok, readme_missing = _asset_section_groups_present(_asset_read_text(readme_path), (("what analyzed", ("analyzed",)), ("manifest", ("manifest",)), ("token folders", ("tokens",)), ("read first", ("read first",)), ("final validation status", ("validation status",))))
    collector.check("asset.readme_handoff_sections", "P1", readme_ok, path=readme_path, pass_message="README handoff sections are present", fail_message="README handoff sections are missing", expected="what analyzed, manifest, token folders, read first, final validation status", actual=", ".join(readme_missing), fix_hint="Update README.md with the required handoff sections and concrete artifact paths.")
    index_text = _asset_read_text(index_path)
    index_ok, index_missing = _asset_section_groups_present(index_text, (("tokens", ("tokens",)), ("PT skipped", ("pt",)), ("headline risk/return", ("risk", "return")), ("missing blockers", ("missing",)), ("artifact map", ("artifact",))))
    if not re.search(r"\bfinal\s+(?:verification|validation)\s+status\b", index_text, re.IGNORECASE):
        index_ok = False
        index_missing.append("final verification status")
    collector.check("asset.index_contract_sections", "P1", index_ok, path=index_path, pass_message="index contract sections are present", fail_message="index contract sections are missing", expected="tokens, PT/skipped, headline risk/return, missing blockers, artifact map, final verification status", actual=", ".join(index_missing), fix_hint="Update index.md with the required artifact map, status, missing data, and risk/return summary sections.")
    statuses: dict[str, str] = {}
    if isinstance(manifest, dict):
        status = _asset_norm_status(manifest.get("status"))
        if status:
            statuses["run-manifest.json"] = status
    for path in (readme_path, index_path, final_path):
        status = _asset_status_from_text(_asset_read_text(path))
        if status:
            statuses[repo_relative(path, root)] = status
    ranks = {name: _asset_status_rank(status) for name, status in statuses.items() if _asset_status_rank(status) >= 0}
    reconcile_ok = len(set(ranks.values())) <= 1
    collector.check("asset.run_status_reconciles", "P1", reconcile_ok, path=".", pass_message="asset run statuses reconcile", fail_message="asset run statuses contradict each other", expected="consistent pass/review_required/blocked/fail status across manifest, README, index, final verification", actual=json.dumps(statuses, sort_keys=True), fix_hint="Reconcile top-level status markers before claiming the run passed.")

    source_file_set = {path for path in [readme_path, index_path, final_path, *s6_paths] if path.exists()}
    source_file_set.update(path for path in root.rglob("*.md") if path.is_file())
    validate_run_local_paths(collector, root, sorted(source_file_set))


def _oracle_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _oracle_status_from_text(text: str) -> str | None:
    match = re.search(r"(?im)\b(?:final\s+status|status)\s*:\s*(pass|review_required|blocked|fail)\b", text)
    return match.group(1) if match else None


def _oracle_norm_status(value: Any) -> str | None:
    if isinstance(value, str):
        lowered = value.strip().lower().replace(" ", "_").replace("-", "_")
        if lowered in VALID_ARTIFACT_STATUSES:
            return lowered
        return lowered if lowered else None
    return None


def _oracle_status_rank(status: str | None) -> int:
    return {"pass": 0, "review_required": 1, "blocked": 2}.get(status or "", 1)


def _oracle_has_formula(text: str) -> bool:
    lowered = text.lower()
    return bool(
        re.search(r"(?im)\bformula\s*:", text)
        and ("=" in text or "×" in text or "*" in text or "/" in text)
        and any(term in lowered for term in ("chainlink", "pyth", "redstone", "twap", "nav", "hardcoded", "aggregator"))
    )


def _oracle_has_any(text: str, terms: Iterable[str]) -> bool:
    lowered = text.lower()
    return any(term.lower() in lowered for term in terms)


def _oracle_missing_terms(text: str, terms: Iterable[str]) -> list[str]:
    lowered = text.lower()
    return [term for term in terms if term.lower() not in lowered]


def _oracle_fact_terms(fact: protocol_adapters.ProtocolFactSlot) -> tuple[str, ...]:
    return (fact.label, *fact.aliases, fact.fact_id, fact.fact_id.split(".")[-1].replace("_", "-"), fact.fact_id.split(".")[-1].replace("_", " "))


def _oracle_missing_adapter_facts(text: str, adapter: protocol_adapters.ProtocolInvestigationAdapter) -> list[str]:
    missing = []
    for fact in adapter.required_facts:
        if not _oracle_has_any(text, _oracle_fact_terms(fact)):
            missing.append(fact.fact_id)
    return missing


def _normalise_fact_state(value: str | None) -> str | None:
    if not value:
        return None
    state = value.strip().strip("`*_.,;:()[]{}").lower().replace("-", "_").replace(" ", "_")
    if state == "confirmed":
        return "found"
    return state if state in FACT_STATES else None


def _extract_fact_state(line: str) -> str | None:
    explicit = re.search(r"\b(?:state|status|value\s+state)\s*[:=]\s*`?([a-zA-Z0-9_ -]+)`?", line)
    if explicit:
        candidates = re.split(r"\s*(?:[;,.|]|\s+and\s+|\s+with\s+)\s*", explicit.group(1), maxsplit=1)
        state = _normalise_fact_state(candidates[0])
        if state:
            return state
    lowered = line.lower().replace("-", "_")
    for state in sorted(FACT_STATES, key=len, reverse=True):
        if state in lowered or state.replace("_", " ") in lowered:
            return state
    if re.search(r"\bfound\b", lowered):
        return "found"
    return None


def _oracle_fact_line(text: str, fact: protocol_adapters.ProtocolFactSlot) -> tuple[int, str] | None:
    terms = _oracle_fact_terms(fact)
    for line_no, line in enumerate(text.splitlines(), start=1):
        line_lower = line.lower()
        if line.lstrip().startswith(("-", "*", "|")) and _oracle_has_any(line_lower, terms):
            return line_no, line.strip()
    for line_no, line in enumerate(text.splitlines(), start=1):
        if _oracle_has_any(line, terms):
            return line_no, line.strip()
    return None


def _oracle_fact_state_observations(
    text: str,
    adapter: protocol_adapters.ProtocolInvestigationAdapter,
    path: Path,
) -> list[dict[str, Any]]:
    observations: list[dict[str, Any]] = []
    for fact in adapter.required_facts:
        line_hit = _oracle_fact_line(text, fact)
        if not line_hit:
            continue
        line_no, line = line_hit
        observations.append(
            {
                "fact_id": fact.fact_id,
                "label": fact.label,
                "line_no": line_no,
                "line": line,
                "path": path,
                "state": _extract_fact_state(line),
                "unknown_placeholder": bool(UNKNOWN_PLACEHOLDER_PATTERN.search(line)),
                "requires_no_result_proof": fact.requires_no_result_proof,
                "aliases": fact.aliases,
            }
        )
    return observations


def _oracle_state_summary(observations: list[dict[str, Any]]) -> dict[str, Any]:
    by_state: dict[str, list[str]] = {}
    facts_needing_investigation: list[str] = []
    facts_investigated_no_result: list[str] = []
    facts_with_unproven_unknowns: list[str] = []
    for obs in observations:
        fact_name = f"{obs['fact_id']} ({obs['label']})"
        state = obs.get("state") or "missing_state"
        by_state.setdefault(state, []).append(fact_name)
        unproven_unknown = bool(obs.get("unknown_placeholder") and state not in FACT_STATES - {"found"})
        if state in {"input_missing", "not_investigated"} or unproven_unknown:
            facts_needing_investigation.append(fact_name)
        if state == "investigated_no_result":
            facts_investigated_no_result.append(fact_name)
        if unproven_unknown:
            facts_with_unproven_unknowns.append(fact_name)
    return {
        "by_state": by_state,
        "facts_needing_investigation": facts_needing_investigation,
        "facts_investigated_no_result": facts_investigated_no_result,
        "facts_with_unproven_unknowns": facts_with_unproven_unknowns,
    }


def _oracle_collect_evidence_facts(run_root: Path, scope_root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    facts: list[dict[str, Any]] = []
    errors: list[str] = []
    candidates = [
        run_root / "evidence-ledger.json",
        run_root / "verification" / "evidence-ledger.json",
        scope_root / "evidence-ledger.json",
        scope_root / "verification" / "evidence-ledger.json",
        scope_root / "raw" / "evidence-ledger.json",
    ]
    seen: set[Path] = set()
    for ledger_path in candidates:
        ledger_path = ledger_path.resolve(strict=False)
        if ledger_path in seen or not ledger_path.exists():
            continue
        seen.add(ledger_path)
        ledger, err = load_json(ledger_path)
        if err or not isinstance(ledger, dict):
            errors.append(f"{ledger_path}: {err or 'JSON root must be an object'}")
            continue
        ledger_facts = ledger.get("facts")
        if not isinstance(ledger_facts, list):
            errors.append(f"{ledger_path}: facts must be an array")
            continue
        for fact in ledger_facts:
            if isinstance(fact, dict):
                item = dict(fact)
                item["_ledger_path"] = ledger_path
                facts.append(item)
    return facts, errors


def _oracle_evidence_matches_observation(
    evidence: dict[str, Any],
    obs: dict[str, Any],
    *,
    scope_id: str | None,
) -> tuple[bool, str | None]:
    if evidence.get("status") != obs.get("state"):
        return False, None
    evidence_scope = evidence.get("scope_id")
    if scope_id and evidence_scope and str(evidence_scope) != scope_id:
        return False, None
    evidence_text = "\n".join(
        str(evidence.get(key) or "")
        for key in ("fact_id", "claim", "method", "command_or_query", "raw_output_path")
    )
    terms = (obs["fact_id"], obs["label"], *obs.get("aliases", ()))
    if not _oracle_has_any(evidence_text, terms):
        return False, None
    raw_path = evidence.get("raw_output_path")
    if not isinstance(raw_path, str) or not raw_path.strip():
        return True, "missing raw_output_path"
    ledger_path = evidence.get("_ledger_path")
    if isinstance(ledger_path, Path):
        raw_candidate = (ledger_path.parent / raw_path).resolve(strict=False)
        if not raw_candidate.exists():
            return True, f"raw_output_path does not resolve: {raw_path}"
    if obs.get("state") == "investigated_no_result" and not isinstance(evidence.get("negative_investigation"), dict):
        return True, "missing negative_investigation proof bundle"
    return True, None


def _oracle_has_blocker_propagation(obs: dict[str, Any], texts: Iterable[str]) -> bool:
    terms = (obs["fact_id"], obs["label"], *obs.get("aliases", ()))
    blocker_terms = ("blocker", "blocked", "review_required", "requires review", "decision effect", "blocks_stage", "request more input", "missing input")
    for text in texts:
        for line in text.splitlines():
            if _oracle_has_any(line, terms) and _oracle_has_any(line, blocker_terms):
                return True
    return False


def _check_final_verification_not_pending(
    collector: FindingCollector,
    check_id: str,
    *,
    path: Path,
    text: str,
    workflow_label: str,
) -> None:
    stale = bool(STALE_VALIDATION_PENDING_PATTERN.search(text))
    collector.check(
        check_id,
        "P1",
        not stale,
        path=path,
        pass_message=f"{workflow_label} final verification does not claim validator status is pending",
        fail_message=f"{workflow_label} final verification still says validation is pending after validator execution",
        expected="final verification records actual validator command/status or omits pending-validation claims",
        actual="pending/not-yet-run validation claim",
        fix_hint="Replace stale pending-validation wording with the command that was run and its actual exit status.",
    )


def _oracle_no_result_claimed(text: str) -> bool:
    return _oracle_has_any(
        text,
        (
            "investigated_no_result",
            "investigated no result",
            "no market",
            "no route",
            "no credit manager",
            "no supported market",
            "no supported route",
            "no result",
        ),
    )


def _oracle_no_result_proof_missing(text: str, adapter: protocol_adapters.ProtocolInvestigationAdapter) -> list[str]:
    required_markers = {
        "registry_checked": ("registry",),
        "api_or_contract_query_attempted": ("api", "contract", "on-chain", "onchain"),
        "network_context_named": ("network", "chain", "mainnet", "ethereum", "arbitrum", "optimism", "base"),
        "evidence_path_present": ("evidence", "raw/", ".json", ".md"),
    }
    missing = []
    for proof_class in adapter.no_result_proof_classes:
        markers = required_markers.get(proof_class, (proof_class.replace("_", " "), proof_class))
        if not _oracle_has_any(text, markers):
            missing.append(proof_class)
    return missing


def _oracle_no_result_conflicts_with_not_investigated(text: str) -> bool:
    return _oracle_no_result_claimed(text) and _oracle_has_any(
        text,
        (
            "state=not_investigated",
            "state: not_investigated",
            "not_investigated",
            "not investigated",
            "not searched",
            "not checked",
            "not attempted",
        ),
    )


def _oracle_validate_protocol_adapter(
    collector: FindingCollector,
    *,
    ctx: ValidationContext,
    protocol: Any,
    fit_text: str,
    fit_path: Path,
    scope_root: Path,
    scope_id: str | None,
    run_status: str | None,
    propagation_texts: Iterable[str],
) -> None:
    adapter = protocol_adapters.get_protocol_adapter(protocol)
    if not adapter:
        _oracle_pass(
            collector,
            "oracle.protocol_adapter_detected",
            "P2",
            path=fit_path,
            message=f"no protocol-specific adapter registered for {protocol or 'unknown protocol'}; generic checks applied",
        )
        return

    _oracle_pass(
        collector,
        "oracle.protocol_adapter_detected",
        "P2",
        path=fit_path,
        message=f"protocol adapter selected: {adapter.adapter_id}",
    )
    missing_facts = _oracle_missing_adapter_facts(fit_text, adapter)
    if missing_facts:
        _oracle_issue(
            collector,
            "oracle.protocol_adapter_required_facts_present",
            "P1",
            path=fit_path,
            field="protocol_adapter_required_facts",
            expected="protocol-fit memo covers every adapter-required fact or explicitly marks it not_investigated/input_missing with evidence",
            actual=", ".join(missing_facts),
            message="protocol-fit memo is missing adapter-required protocol facts",
            fix_hint="Use the protocol investigation adapter fact list. For absent facts, write not_investigated unless a no-result proof bundle supports investigated_no_result.",
        )
    else:
        _oracle_pass(collector, "oracle.protocol_adapter_required_facts_present", "P1", path=fit_path, message="protocol adapter required facts present")

    observations = _oracle_fact_state_observations(fit_text, adapter, fit_path)
    state_summary = _oracle_state_summary(observations)
    collector.fact_state_summary = state_summary

    unproven_unknowns = state_summary["facts_with_unproven_unknowns"]
    if unproven_unknowns:
        _oracle_issue(
            collector,
            "oracle.protocol_adapter_unknown_requires_state",
            "P1",
            path=fit_path,
            field="protocol_adapter_required_facts",
            expected="unknown placeholders on required facts use explicit state=not_applicable/input_missing/source_unavailable/source_inconclusive/investigated_no_result/contradicted/not_investigated",
            actual=", ".join(unproven_unknowns),
            message="required protocol facts contain unknown placeholders without an allowed investigation-result state",
            fix_hint="Annotate each unknown required fact with an explicit taxonomy state and decision effect, or replace it with a source-grounded fact.",
        )
    else:
        _oracle_pass(collector, "oracle.protocol_adapter_unknown_requires_state", "P1", path=fit_path, message="required fact unknown placeholders carry explicit taxonomy states")

    not_investigated_without_blocker = []
    for obs in observations:
        if obs.get("state") != "not_investigated":
            continue
        status_allows_blocker = run_status in {"blocked", "review_required"}
        blocker_propagates = _oracle_has_blocker_propagation(obs, propagation_texts)
        if not (status_allows_blocker and blocker_propagates):
            not_investigated_without_blocker.append(f"{obs['fact_id']} ({obs['label']})")
    if not_investigated_without_blocker:
        _oracle_issue(
            collector,
            "oracle.protocol_adapter_not_investigated_requires_blocker",
            "P1",
            path=fit_path,
            field="protocol_adapter_required_facts",
            expected="mandatory not_investigated facts force status=blocked/review_required and are named in propagated blockers",
            actual=", ".join(not_investigated_without_blocker),
            message="mandatory protocol facts are marked not_investigated without explicit blocker propagation",
            fix_hint="Either complete the investigation, or set the run/stage status to blocked/review_required and name each not_investigated fact in open blockers/decision effect.",
        )
    else:
        _oracle_pass(collector, "oracle.protocol_adapter_not_investigated_requires_blocker", "P1", path=fit_path, message="not_investigated mandatory facts are absent or explicitly propagated as blockers")

    evidence_facts, evidence_errors = _oracle_collect_evidence_facts(ctx.run_root, scope_root)
    if evidence_errors:
        _oracle_issue(
            collector,
            "oracle.evidence_ledger_json_valid",
            "P1",
            path=scope_root,
            field="evidence-ledger.json",
            expected="parseable evidence ledger with facts array when ledger files are present",
            actual="; ".join(evidence_errors),
            message="evidence ledger could not be parsed for protocol adapter validation",
            fix_hint="Fix evidence-ledger.json so it is a JSON object with a facts array, or remove invalid stale ledger files.",
        )
    missing_ledger = []
    invalid_ledger = []
    for obs in observations:
        if obs.get("state") != "investigated_no_result":
            continue
        matched_error: str | None = None
        matched = False
        for evidence in evidence_facts:
            ok, error = _oracle_evidence_matches_observation(evidence, obs, scope_id=scope_id)
            if not ok:
                continue
            matched = True
            matched_error = error
            break
        fact_name = f"{obs['fact_id']} ({obs['label']})"
        if not matched:
            missing_ledger.append(fact_name)
        elif matched_error:
            invalid_ledger.append(f"{fact_name}: {matched_error}")
    if missing_ledger or invalid_ledger:
        _oracle_issue(
            collector,
            "oracle.protocol_adapter_no_result_evidence_ledger",
            "P1",
            path=fit_path,
            field="investigated_no_result",
            expected="each investigated_no_result required fact has a matching evidence-ledger fact with negative_investigation and resolving raw_output_path",
            actual=", ".join(missing_ledger + invalid_ledger),
            message="investigated_no_result required facts lack matching proof-backed evidence ledger entries",
            fix_hint="Add evidence-ledger facts for the named required facts, with status=investigated_no_result, negative_investigation, command/query, decision_effect, and raw output paths.",
        )
    else:
        _oracle_pass(collector, "oracle.protocol_adapter_no_result_evidence_ledger", "P1", path=fit_path, message="investigated_no_result facts have matching proof-backed evidence ledger entries or are absent")

    decision_facts = []
    for obs in observations:
        state = obs.get("state")
        if state in NON_PASS_WORKFLOW_FACT_STATES:
            decision_facts.append(f"{obs['fact_id']} ({obs['label']}): {state}")
    decision_facts.extend(f"{fact}: needs_investigation" for fact in state_summary["facts_with_unproven_unknowns"])
    decision_status = "review_required" if decision_facts else "pass"
    if run_status == "blocked":
        decision_status = "blocked"
    collector.workflow_decision = {
        "status": decision_status,
        "basis": "mandatory protocol facts include non-decision-grade taxonomy states" if decision_facts else "mandatory protocol facts are decision-grade for deterministic taxonomy checks",
        "facts_needing_investigation": state_summary["facts_needing_investigation"],
        "facts_investigated_no_result": state_summary["facts_investigated_no_result"],
        "non_pass_facts": decision_facts,
    }

    if _oracle_no_result_claimed(fit_text):
        if _oracle_no_result_conflicts_with_not_investigated(fit_text):
            _oracle_issue(
                collector,
                "oracle.protocol_adapter_not_investigated_not_no_result",
                "P1",
                path=fit_path,
                field="investigated_no_result",
                expected="not_investigated when the adapter search was not performed; investigated_no_result only after proof-backed investigation",
                actual="no-result state is paired with not-investigated language",
                message="not-investigated work is incorrectly represented as investigated_no_result",
                fix_hint="Use state=not_investigated for unperformed searches; reserve state=investigated_no_result for adapter proof bundles.",
            )
        else:
            _oracle_pass(
                collector,
                "oracle.protocol_adapter_not_investigated_not_no_result",
                "P1",
                path=fit_path,
                message="no-result claim is not paired with not-investigated language",
            )
        missing_proof = _oracle_no_result_proof_missing(fit_text, adapter)
        if missing_proof:
            _oracle_issue(
                collector,
                "oracle.protocol_adapter_no_result_proof_bundle",
                "P1",
                path=fit_path,
                field="investigated_no_result",
                expected="adapter-defined no-result proof classes present for any no-market/no-route claim",
                actual=", ".join(missing_proof),
                message="no-market/no-route claim lacks the adapter-required proof bundle",
                fix_hint="For investigated_no_result, name methods tried, sources checked, network context, negative evidence path, and residual decision effect. If no investigation happened, use not_investigated instead.",
            )
        else:
            _oracle_pass(collector, "oracle.protocol_adapter_no_result_proof_bundle", "P1", path=fit_path, message="no-result proof bundle satisfies protocol adapter")
    else:
        _oracle_pass(collector, "oracle.protocol_adapter_no_result_proof_bundle", "P1", path=fit_path, message="no no-result claim requiring adapter proof")


def _oracle_issue(
    collector: FindingCollector,
    check_id: str,
    severity: str,
    *,
    path: Path | str,
    field: str | None = None,
    expected: str,
    actual: str | None,
    message: str,
    fix_hint: str,
) -> None:
    collector.checks.append(CheckResult(check_id, severity, "fail", collector.rel(path), message))
    collector.finding(
        check_id,
        severity,
        path=path,
        field=field,
        expected=expected,
        actual=actual,
        message=message,
        fix_hint=fix_hint,
    )


def _oracle_pass(collector: FindingCollector, check_id: str, severity: str, *, path: Path | str, message: str) -> None:
    collector.checks.append(CheckResult(check_id, severity, "pass", collector.rel(path), message))


def validate_oracle_analysis(ctx: ValidationContext, collector: FindingCollector, inputs: dict[str, Any]) -> None:
    """Workflow-specific checks for oracle-analysis-v1.

    The checks are structural/compliance gates only. They deliberately verify
    evidence shape, canonical paths, and required fields without scoring oracle
    economics or deciding whether a feed is good.
    """
    manifest_path = ctx.run_root / "run-manifest.json"
    manifest, err = load_json(manifest_path)
    if err or manifest is None:
        return

    canonical_final = CANONICAL_FINAL_VERIFICATIONS["oracle-analysis-v1"]
    required_root_files = (
        "README.md",
        "index.md",
        canonical_final,
    )
    required_scope_files = (
        "scope.json",
        "oracle/scope.md",
        "oracle/feed-graph.md",
        "oracle/node-classification.md",
        "oracle/source-primitive-audit.md",
        "oracle/stress-tradeoff-analysis.md",
        "oracle/protocol-fit-memo.md",
        "raw/feed-probes.json",
        "verification/oracle-analysis-verification.md",
    )
    required_manifest_fields = ("workflow_id", "run_id", "run_artifact_root", "status", "scopes", "final_index", "final_verification")
    required_scope_fields = ("scope_id", "scope_slug", "scope_type", "chain", "artifact_dir", "status", "protocol", "position_sides", "token_roles")

    missing_manifest_fields = [field for field in required_manifest_fields if field not in manifest]
    if missing_manifest_fields:
        _oracle_issue(
            collector,
            "oracle.manifest_schema",
            "P0",
            path=manifest_path,
            field="run-manifest.json",
            expected="manifest includes required oracle-analysis fields",
            actual=", ".join(missing_manifest_fields),
            message="run-manifest.json is missing required oracle-analysis fields",
            fix_hint="Add the missing workflow_id, run_id, run_artifact_root, status, scopes, final_index, and final_verification fields.",
        )
    else:
        _oracle_pass(collector, "oracle.manifest_schema", "P0", path=manifest_path, message="manifest includes required oracle-analysis fields")

    workflow_id = manifest.get("workflow_id")
    if workflow_id != "oracle-analysis-v1":
        _oracle_issue(
            collector,
            "oracle.manifest_schema",
            "P0",
            path=manifest_path,
            field="workflow_id",
            expected="oracle-analysis-v1",
            actual=str(workflow_id),
            message="manifest workflow_id is not oracle-analysis-v1",
            fix_hint="Set workflow_id to oracle-analysis-v1 for oracle-analysis runs.",
        )

    final_index = manifest.get("final_index")
    if final_index != "index.md":
        _oracle_issue(
            collector,
            "oracle.manifest_schema",
            "P0",
            path=manifest_path,
            field="final_index",
            expected="index.md",
            actual=str(final_index),
            message="manifest final_index must point to the top-level index.md",
            fix_hint="Set final_index to index.md and keep the final index at the run root.",
        )

    final_verification = manifest.get("final_verification")
    if final_verification != canonical_final:
        _oracle_issue(
            collector,
            "oracle.canonical_final_verification_path",
            "P0",
            path=manifest_path,
            field="final_verification",
            expected=canonical_final,
            actual=str(final_verification),
            message="manifest final_verification does not use the canonical oracle-analysis final verification path",
            fix_hint=f"Move the final verification to {canonical_final} and update run-manifest.json.",
        )
    else:
        _oracle_pass(collector, "oracle.canonical_final_verification_path", "P0", path=manifest_path, message="canonical final verification path declared")

    for rel_path in required_root_files:
        path = ctx.run_root / rel_path
        if not path.exists():
            _oracle_issue(
                collector,
                "oracle.required_files_present",
                "P0",
                path=path,
                field=rel_path,
                expected="required oracle-analysis root file present",
                actual="missing",
                message=f"required root file is missing: {rel_path}",
                fix_hint="Create the required root-level handoff, index, and final verification files.",
            )
        else:
            _oracle_pass(collector, "oracle.required_files_present", "P0", path=path, message=f"required root file present: {rel_path}")

    index_path = ctx.run_root / "index.md"
    readme_path = ctx.run_root / "README.md"
    final_path = ctx.run_root / canonical_final
    index_text = _oracle_text(index_path)
    readme_text = _oracle_text(readme_path)
    final_text = _oracle_text(final_path)

    index_required = ("scope table", "feed formulas", "side-specific verdict", "open blockers", "artifact map", "validation result")
    index_missing = _oracle_missing_terms(index_text, index_required)
    if index_missing:
        _oracle_issue(
            collector,
            "oracle.index_contract_sections",
            "P1",
            path=index_path,
            field="sections",
            expected="top-level index includes oracle handoff sections",
            actual=", ".join(index_missing),
            message="index.md is missing required oracle-analysis handoff sections",
            fix_hint="Add scope table, feed formulas, side-specific verdict matrix, open blockers, artifact map, and validation result sections.",
        )
    else:
        _oracle_pass(collector, "oracle.index_contract_sections", "P1", path=index_path, message="index.md includes required oracle handoff sections")

    readme_required = ("what was analyzed", "manifest", "run-manifest.json", "scope folders", "files to read first", "final validation status")
    readme_missing = _oracle_missing_terms(readme_text, readme_required)
    if readme_missing:
        _oracle_issue(
            collector,
            "oracle.readme_handoff_sections",
            "P1",
            path=readme_path,
            field="sections",
            expected="README includes operator handoff sections",
            actual=", ".join(readme_missing),
            message="README.md is missing required oracle-analysis handoff sections",
            fix_hint="Add what was analyzed, manifest, scope folders, files to read first, and final validation status sections.",
        )
    else:
        _oracle_pass(collector, "oracle.readme_handoff_sections", "P1", path=readme_path, message="README.md includes required handoff sections")

    _check_final_verification_not_pending(
        collector,
        "oracle.final_verification.not_pending",
        path=final_path,
        text=final_text,
        workflow_label="oracle-analysis",
    )

    raw_scopes = manifest.get("scopes")
    scopes = raw_scopes if isinstance(raw_scopes, list) else []
    if not isinstance(raw_scopes, list) or not scopes:
        _oracle_issue(
            collector,
            "oracle.manifest_schema",
            "P0",
            path=manifest_path,
            field="scopes",
            expected="non-empty list of oracle-analysis scopes",
            actual=type(raw_scopes).__name__,
            message="manifest scopes must be a non-empty list",
            fix_hint="Declare one scope object per token or PT-market artifact folder.",
        )
        return

    status_observations: list[tuple[str, str, str]] = []
    root_status = _oracle_norm_status(manifest.get("status"))
    status_observations.append(("manifest.status", root_status or "missing", "run-manifest.json"))
    index_status = _oracle_status_from_text(index_text)
    final_status = _oracle_status_from_text(final_text)
    if index_status:
        status_observations.append(("index.md", index_status, "index.md"))
    if final_status:
        status_observations.append((canonical_final, final_status, canonical_final))

    all_scope_statuses: list[str] = []
    scope_fact_summaries: list[dict[str, Any]] = []
    scope_workflow_decisions: list[dict[str, Any]] = []
    for idx, scope in enumerate(scopes):
        if not isinstance(scope, dict):
            _oracle_issue(
                collector,
                "oracle.manifest_schema",
                "P0",
                path=manifest_path,
                field=f"scopes[{idx}]",
                expected="scope object",
                actual=type(scope).__name__,
                message="manifest scope entry is not an object",
                fix_hint="Replace every scope entry with an object containing scope_id, scope_slug, scope_type, artifact_dir, and status.",
            )
            continue
        missing_scope_fields = [field for field in required_scope_fields if field not in scope]
        if missing_scope_fields:
            _oracle_issue(
                collector,
                "oracle.manifest_schema",
                "P0",
                path=manifest_path,
                field=f"scopes[{idx}]",
                expected="scope includes required fields",
                actual=", ".join(missing_scope_fields),
                message="manifest scope is missing required oracle-analysis fields",
                fix_hint="Add scope_id, scope_slug, scope_type, chain, artifact_dir, and status to every scope.",
            )
            continue
        artifact_dir = str(scope.get("artifact_dir"))
        if not artifact_dir.startswith(("tokens/", "pt-markets/")):
            _oracle_issue(
                collector,
                "oracle.manifest_schema",
                "P0",
                path=manifest_path,
                field=f"scopes[{idx}].artifact_dir",
                expected="tokens/<scope-slug> or pt-markets/<scope-slug>",
                actual=artifact_dir,
                message="oracle-analysis artifact_dir must live under tokens/ or pt-markets/",
                fix_hint="Move token scopes under tokens/<slug>/ and PT-market scopes under pt-markets/<slug>/.",
            )
        scope_root = ctx.run_root / artifact_dir
        for rel_path in required_scope_files:
            path = scope_root / rel_path
            if not path.exists():
                _oracle_issue(
                    collector,
                    "oracle.required_files_present",
                    "P0",
                    path=path,
                    field=rel_path,
                    expected="required per-scope oracle-analysis file present",
                    actual="missing",
                    message=f"required per-scope file is missing: {artifact_dir}/{rel_path}",
                    fix_hint="Create the full per-scope oracle-analysis package before validating the run.",
                )
            else:
                _oracle_pass(collector, "oracle.required_files_present", "P0", path=path, message=f"required per-scope file present: {rel_path}")
        source_evidence_dir = scope_root / "raw/source-evidence"
        if not source_evidence_dir.exists() or not any(source_evidence_dir.glob("*")):
            _oracle_issue(
                collector,
                "oracle.source_primitive_audit_present",
                "P1",
                path=source_evidence_dir,
                field="raw/source-evidence",
                expected="raw source evidence files for primitive audit",
                actual="missing or empty",
                message="raw source evidence directory is missing or empty",
                fix_hint="Store raw evidence files under raw/source-evidence/ and reference them from oracle/source-primitive-audit.md.",
            )

        scope_json_path = scope_root / "scope.json"
        scope_json, scope_err = load_json(scope_json_path)
        if scope_err:
            _oracle_issue(
                collector,
                "oracle.manifest_schema",
                "P0",
                path=scope_json_path,
                field="scope.json",
                expected="parseable per-scope JSON object",
                actual=scope_err,
                message="scope.json is missing or invalid",
                fix_hint="Write a valid scope.json for every manifest scope.",
            )
            scope_json = {}
        scope_status = _oracle_norm_status(scope.get("status"))
        scope_file_status = _oracle_norm_status(scope_json.get("status")) if scope_json else None
        per_scope_verification = scope_root / "verification/oracle-analysis-verification.md"
        per_scope_verification_status = _oracle_status_from_text(_oracle_text(per_scope_verification))
        for field_name, status, path_label in (
            ("manifest scope status", scope_status, "run-manifest.json"),
            ("scope.json status", scope_file_status, f"{artifact_dir}/scope.json"),
            ("per-scope verification status", per_scope_verification_status, f"{artifact_dir}/verification/oracle-analysis-verification.md"),
        ):
            if status:
                status_observations.append((field_name, status, path_label))
                all_scope_statuses.append(status)
            else:
                _oracle_issue(
                    collector,
                    "oracle.run_status_reconciles",
                    "P1",
                    path=path_label,
                    field="status",
                    expected="status is pass, review_required, or blocked",
                    actual="missing or invalid",
                    message=f"{field_name} is missing or invalid",
                    fix_hint="Add explicit artifact statuses using pass, review_required, or blocked.",
                )

        feed_graph_path = scope_root / "oracle/feed-graph.md"
        node_classification_path = scope_root / "oracle/node-classification.md"
        source_audit_path = scope_root / "oracle/source-primitive-audit.md"
        stress_path = scope_root / "oracle/stress-tradeoff-analysis.md"
        fit_path = scope_root / "oracle/protocol-fit-memo.md"
        feed_text = _oracle_text(feed_graph_path)
        node_text = _oracle_text(node_classification_path)
        source_text = _oracle_text(source_audit_path)
        stress_text = _oracle_text(stress_path)
        fit_text = _oracle_text(fit_path)

        formula_missing = []
        if not _oracle_has_formula(feed_text):
            formula_missing.append("oracle/feed-graph.md")
        if not _oracle_has_formula(node_text):
            formula_missing.append("oracle/node-classification.md")
        if formula_missing:
            _oracle_issue(
                collector,
                "oracle.pricing_formula_present",
                "P1",
                path=scope_root,
                field="pricing_formula",
                expected="pricing formula stated directly in feed-graph.md and node-classification.md",
                actual=", ".join(formula_missing),
                message="pricing formula evidence is missing from required oracle files",
                fix_hint="Add a Formula: line with the concrete source-node expression to both feed-graph.md and node-classification.md.",
            )
        else:
            _oracle_pass(collector, "oracle.pricing_formula_present", "P1", path=scope_root, message="pricing formula present in feed graph and node classification")

        source_required_terms = ("source identity", "source type", "timestamp", "cadence", "trust", "methodology", "raw evidence pointer")
        source_missing = _oracle_missing_terms(source_text, source_required_terms)
        primitive_terms_ok = _oracle_has_any(source_text + feed_text + node_text, ("source primitive", "child feed", "chainlink", "pyth", "redstone", "hardcoded", "twap", "nav"))
        source_audit_failed = False
        if source_missing or not primitive_terms_ok:
            source_audit_failed = True
            actual_bits = list(source_missing)
            if not primitive_terms_ok:
                actual_bits.append("source primitive detail")
            _oracle_issue(
                collector,
                "oracle.source_primitive_audit_present",
                "P1",
                path=source_audit_path,
                field="source_primitive_audit",
                expected="source identity/type/timestamp-cadence/trust-methodology/raw evidence pointer plus primitive-specific evidence",
                actual=", ".join(actual_bits),
                message="source primitive audit is missing required evidence fields",
                fix_hint="Expand source-primitive-audit.md beyond feed labels and include primitive identity, type, timestamp/cadence, trust/methodology, and raw evidence pointers.",
            )
        evidence_refs = sorted({m.group(0).rstrip(".,);]") for m in re.finditer(r"raw/source-evidence/[A-Za-z0-9._/-]+", source_text)})
        missing_evidence_refs = [ref for ref in evidence_refs if not (scope_root / ref).exists()]
        if not evidence_refs:
            source_audit_failed = True
            _oracle_issue(
                collector,
                "oracle.source_primitive_audit_present",
                "P1",
                path=source_audit_path,
                field="raw_evidence_pointer",
                expected="at least one raw/source-evidence/... pointer in source-primitive-audit.md",
                actual="no raw evidence pointer path found",
                message="source primitive audit does not link to raw source evidence files",
                fix_hint="Add concrete raw/source-evidence/... paths for each audited primitive.",
            )
        elif missing_evidence_refs:
            source_audit_failed = True
            _oracle_issue(
                collector,
                "oracle.source_primitive_audit_present",
                "P1",
                path=source_audit_path,
                field="raw_evidence_pointer",
                expected="all raw/source-evidence/... pointers resolve within the scope folder",
                actual=", ".join(missing_evidence_refs),
                message="source primitive audit references missing raw evidence files",
                fix_hint="Fix the raw/source-evidence/... links or add the missing evidence files under the same scope folder.",
            )
        if not source_audit_failed:
            _oracle_pass(collector, "oracle.source_primitive_audit_present", "P1", path=source_audit_path, message="source primitive audit includes required evidence fields and resolving raw evidence pointers")

        classification_required = ("market", "fundamental", "nav", "hardcoded", "hybrid")
        if not _oracle_has_any(node_text + fit_text, classification_required) or _oracle_missing_terms(node_text + fit_text, ("market", "hardcoded", "hybrid")):
            _oracle_issue(
                collector,
                "oracle.node_classification_present",
                "P1",
                path=node_classification_path,
                field="node_classification",
                expected="nodes classified using market/fundamental/NAV/hardcoded/hybrid taxonomy where applicable",
                actual="classification taxonomy incomplete",
                message="node classification does not show the required oracle-analysis taxonomy",
                fix_hint="Classify feed nodes with the oracle-analysis taxonomy and mark unavailable/non-applicable categories explicitly.",
            )
        else:
            _oracle_pass(collector, "oracle.node_classification_present", "P1", path=node_classification_path, message="node classification taxonomy present")

        stress_missing = _oracle_missing_terms(stress_text, ("liquidity-cascade", "liquidity-trap"))
        if stress_missing:
            _oracle_issue(
                collector,
                "oracle.stress_tradeoff_fields",
                "P1",
                path=stress_path,
                field="cascade_vs_trap",
                expected="liquidity-cascade and liquidity-trap tradeoff branches covered",
                actual=", ".join(stress_missing),
                message="stress tradeoff analysis is missing required cascade/trap branches",
                fix_hint="Add explicit liquidity-cascade and liquidity-trap analysis before concluding the oracle fit.",
            )
        else:
            _oracle_pass(collector, "oracle.stress_tradeoff_fields", "P1", path=stress_path, message="cascade/trap stress branches present")

        conclusion_required = ("position_side", "token_role", "stress_direction", "loss_bearer")
        conclusion_missing = _oracle_missing_terms(fit_text, conclusion_required)
        side_names = [str(s) for s in (scope.get("position_sides") if isinstance(scope.get("position_sides"), list) else [])]
        side_surface = re.sub(r"[^a-z0-9]+", " ", fit_text.lower())
        missing_side_mentions = []
        for side in side_names:
            normalized_side = re.sub(r"[^a-z0-9]+", " ", side.lower()).strip()
            if normalized_side and normalized_side not in side_surface:
                tokens = [token for token in normalized_side.split() if token]
                if not tokens or not all(token in side_surface for token in tokens):
                    missing_side_mentions.append(side)
        if conclusion_missing or missing_side_mentions:
            actual_bits = list(conclusion_missing)
            if missing_side_mentions:
                actual_bits.append("missing side verdicts: " + ", ".join(missing_side_mentions))
            _oracle_issue(
                collector,
                "oracle.conclusion_quad_present",
                "P1",
                path=fit_path,
                field="side_specific_verdict_matrix",
                expected="position_side, token_role, stress_direction, and loss_bearer named for each relevant side",
                actual="; ".join(actual_bits),
                message="side-specific verdict matrix is missing required conclusion fields",
                fix_hint="Add a verdict matrix that names position_side, token_role, stress_direction, and loss_bearer for borrower, LP, liquidator, and curator/operator sides where in scope.",
            )
        else:
            _oracle_pass(collector, "oracle.conclusion_quad_present", "P1", path=fit_path, message="side-specific conclusion fields present")

        protocol_value = (scope_json or scope).get("protocol") or scope.get("protocol")
        _oracle_validate_protocol_adapter(
            collector,
            ctx=ctx,
            protocol=protocol_value,
            fit_text=fit_text,
            fit_path=fit_path,
            scope_root=scope_root,
            scope_id=str((scope_json or scope).get("scope_id") or scope.get("scope_id") or "") or None,
            run_status=root_status,
            propagation_texts=(fit_text, final_text, index_text, readme_text, _oracle_text(per_scope_verification)),
        )
        if collector.fact_state_summary:
            scoped_summary = dict(collector.fact_state_summary)
            scoped_summary["scope_id"] = str((scope_json or scope).get("scope_id") or scope.get("scope_id") or "") or None
            scoped_summary["artifact_dir"] = artifact_dir
            scope_fact_summaries.append(scoped_summary)
        if collector.workflow_decision:
            scoped_decision = dict(collector.workflow_decision)
            scoped_decision["scope_id"] = str((scope_json or scope).get("scope_id") or scope.get("scope_id") or "") or None
            scoped_decision["artifact_dir"] = artifact_dir
            scope_workflow_decisions.append(scoped_decision)

        combined_source_text = fit_text
        only_label = "external feed label" in combined_source_text.lower() and not _oracle_has_any(combined_source_text, ("chainlink", "pyth", "redstone", "hardcoded", "source primitive", "child-source", "child feed"))
        missing_child_source = not _oracle_has_any(combined_source_text, ("chainlink", "pyth", "redstone", "hardcoded", "source primitive", "child-source", "child feed"))
        if only_label or missing_child_source:
            _oracle_issue(
                collector,
                "oracle.no_top_level_only_verdict",
                "P1",
                path=fit_path,
                field="feed_depth",
                expected="verdict reaches child/source primitives rather than stopping at a top-level feed label",
                actual="top-level feed label only",
                message="oracle verdict appears to stop at the top-level feed label",
                fix_hint="Parse the feed DAG through child/source primitives and cite source-node evidence before concluding.",
            )
        else:
            _oracle_pass(collector, "oracle.no_top_level_only_verdict", "P1", path=fit_path, message="verdict reaches child/source primitives")

    invalid_statuses = [(field, status, path) for field, status, path in status_observations if status not in VALID_ARTIFACT_STATUSES]
    if invalid_statuses:
        _oracle_issue(
            collector,
            "oracle.run_status_reconciles",
            "P1",
            path=".",
            field="status",
            expected="statuses limited to pass, review_required, blocked",
            actual="; ".join(f"{field}={status}" for field, status, _path in invalid_statuses),
            message="one or more oracle-analysis artifact statuses are invalid",
            fix_hint="Use only pass, review_required, or blocked inside oracle-analysis run artifacts.",
        )

    child_statuses = [status for _field, status, _path in status_observations if status in VALID_ARTIFACT_STATUSES and _field != "manifest.status"]
    expected_root_status = max(child_statuses or ["pass"], key=_oracle_status_rank)
    inconsistent = []
    if root_status in VALID_ARTIFACT_STATUSES and root_status != expected_root_status:
        inconsistent.append(f"manifest.status={root_status}, expected {expected_root_status}")
    if final_status in VALID_ARTIFACT_STATUSES and final_status != expected_root_status:
        inconsistent.append(f"final verification status={final_status}, expected {expected_root_status}")
    if index_status in VALID_ARTIFACT_STATUSES and index_status != expected_root_status:
        inconsistent.append(f"index status={index_status}, expected {expected_root_status}")
    if inconsistent:
        _oracle_issue(
            collector,
            "oracle.run_status_reconciles",
            "P1",
            path=".",
            field="status",
            expected="root/index/final status equals the worst per-scope status",
            actual="; ".join(inconsistent),
            message="oracle-analysis run statuses contradict each other",
            fix_hint="Reconcile run-manifest.json, index.md, per-scope verification files, and final verification status before claiming the run passed.",
        )
    else:
        _oracle_pass(collector, "oracle.run_status_reconciles", "P1", path=".", message="oracle-analysis statuses reconcile")

    if scope_fact_summaries:
        facts_needing_investigation = [
            fact
            for summary in scope_fact_summaries
            for fact in summary.get("facts_needing_investigation", [])
        ]
        facts_investigated_no_result = [
            fact
            for summary in scope_fact_summaries
            for fact in summary.get("facts_investigated_no_result", [])
        ]
        non_pass_facts = [
            fact
            for decision in scope_workflow_decisions
            for fact in decision.get("non_pass_facts", [])
        ]
        decision_statuses = [str(decision.get("status") or "pass") for decision in scope_workflow_decisions]
        workflow_decision_status = "blocked" if "blocked" in decision_statuses else "review_required" if "review_required" in decision_statuses else "pass"
        inputs["fact_state_summary"] = {
            "scopes": scope_fact_summaries,
            "facts_needing_investigation": facts_needing_investigation,
            "facts_investigated_no_result": facts_investigated_no_result,
        }
        inputs["workflow_decision"] = {
            "status": workflow_decision_status,
            "basis": "oracle protocol adapter fact taxonomy",
            "facts_needing_investigation": facts_needing_investigation,
            "facts_investigated_no_result": facts_investigated_no_result,
            "non_pass_facts": non_pass_facts,
        }

def resolve_parent_return_path(ctx: ValidationContext) -> Path:
    """Resolve the combined Analyze→Propose parent-return artifact.

    By default this preserves the canonical parent-run-root path. When
    --parent-return is supplied, accept either a parent-run-root-relative path
    or a repo-relative/absolute path so fixture matrices can point at explicit
    good and bad parent-return variants without copying them into the default
    handoff location.
    """
    if not ctx.parent_return:
        return ctx.run_root / "agentic-flow" / "analyze-and-propose.md"
    raw = Path(ctx.parent_return)
    if raw.is_absolute():
        return raw.resolve(strict=False)
    run_relative = (ctx.run_root / raw).resolve(strict=False)
    repo_relative_candidate = (ctx.repo_root / raw).resolve(strict=False)
    if run_relative.exists() or not repo_relative_candidate.exists():
        return run_relative
    return repo_relative_candidate


def validate_combined(ctx: ValidationContext) -> tuple[list[Finding], list[CheckResult], dict[str, Any]]:
    common_findings, common_checks, inputs = validate_common(ctx)
    collector = FindingCollector(ctx.workflow_id, ctx.repo_root, ctx.run_root)
    collector.findings.extend(common_findings)
    collector.checks.extend(common_checks)
    if any(f.severity == "P0" and f.id == "run_root.exists" for f in collector.findings):
        return collector.findings, collector.checks, inputs

    root = ctx.run_root
    handoff_path = resolve_parent_return_path(ctx)
    inputs.update(
        {
            "manifest": None,
            "final_index": _first_existing_index(root),
            "final_verification": None,
            "parent_return": repo_relative(handoff_path, ctx.repo_root),
        }
    )

    child_reports: dict[str, dict[str, Any]] = {}
    child_states: dict[str, dict[str, Any]] = {}
    for child_name, spec in CHILD_SPECS.items():
        child_root = root / spec["dir"]
        collector.check(
            spec["root_check"],
            "P0",
            child_root.exists() and child_root.is_dir(),
            path=child_root,
            pass_message=f"{spec['dir']} child root exists",
            fail_message=f"{spec['dir']} child root is missing",
            expected=f"{spec['dir']}/ directory under parent run root",
            actual="missing" if not child_root.exists() else "not a directory",
            fix_hint="Wrap split child runs in a parent combined run root with sibling asset and oracle child directories.",
        )
        report_path = root / spec["report_path"]
        report: dict[str, Any] | None = None
        err: str | None = None
        if not report_path.exists():
            err = "workflow-harness-report.json is missing"
        else:
            report, err = load_json(report_path)
        collector.check(
            spec["json_check"],
            "P0",
            err is None and report is not None,
            path=report_path,
            pass_message=f"{child_name} child workflow-harness-report.json exists and parses",
            fail_message=err or f"{child_name} child workflow-harness-report.json is invalid",
            expected="parseable child workflow-harness-report.json",
            actual=err,
            fix_hint="Run or import the child workflow validator and place its workflow-harness-report.json at the required path.",
        )
        if report is not None:
            child_reports[child_name] = report
            child_state = validate_child_report(collector, child_name, spec, report, report_path, child_root)
            child_states[child_name] = child_state
            import_child_findings(collector, child_name, spec, report, report_path)
            import_child_status(collector, child_name, spec, report, report_path)

    child_workflow_decisions: dict[str, dict[str, Any]] = {}
    child_status_blocks: dict[str, dict[str, Any]] = {}
    child_fact_state_summary: dict[str, Any] = {}
    for child_name, report in child_reports.items():
        raw_decision = report.get("workflow_decision")
        decision = raw_decision if isinstance(raw_decision, dict) else None
        status_block = child_status_block(report)
        child_status_blocks[child_name] = status_block
        missing_decision_note = "child report missing workflow_decision; rerun child validator before decision-grade success"
        child_workflow_decisions[child_name] = {
            "status": status_block["workflow_decision_status"],
            "formal_validation_status": status_block["formal_validation_status"],
            "semantic_review_status": status_block["semantic_review_status"],
            "proposal_gate": status_block["proposal_gate"],
            "basis": (decision or {}).get("basis", missing_decision_note if decision is None else "child report status"),
            "facts_needing_investigation": (decision or {}).get("facts_needing_investigation", []),
            "facts_investigated_no_result": (decision or {}).get("facts_investigated_no_result", []),
            "non_pass_facts": (decision or {}).get("non_pass_facts", [missing_decision_note] if decision is None else []),
        }
        fact_summary = report.get("fact_state_summary") if isinstance(report.get("fact_state_summary"), dict) else {}
        if fact_summary:
            child_fact_state_summary[child_name] = fact_summary
    if child_workflow_decisions:
        statuses = [decision["status"] for decision in child_workflow_decisions.values()]
        semantic_status = worst_decision_status(
            [block.get("semantic_review_status") for block in child_status_blocks.values() if block.get("semantic_review_status") != "not_run"],
            default="not_run",
        )
        combined_decision_status = worst_decision_status(statuses, default="pass")
        proposal_gate = build_proposal_gate(combined_decision_status, child_status_blocks)
        inputs["workflow_decision"] = {
            "status": combined_decision_status,
            "basis": "worst child workflow_decision/semantic/formal status, kept separate from parent formal validation",
            "children": child_workflow_decisions,
            "facts_needing_investigation": [
                f"{child}.{fact}"
                for child, decision in child_workflow_decisions.items()
                for fact in decision.get("facts_needing_investigation", [])
            ],
            "facts_investigated_no_result": [
                f"{child}.{fact}"
                for child, decision in child_workflow_decisions.items()
                for fact in decision.get("facts_investigated_no_result", [])
            ],
            "non_pass_facts": [
                f"{child}.{fact}"
                for child, decision in child_workflow_decisions.items()
                for fact in decision.get("non_pass_facts", [])
            ],
        }
        inputs["formal_validation_status"] = "pending_parent_validator"
        inputs["semantic_review_status"] = semantic_status
        inputs["workflow_decision_status"] = combined_decision_status
        inputs["proposal_gate"] = proposal_gate
        inputs["status_block"] = status_block_for_report(
            formal_validation_status="pending_parent_validator",
            semantic_review_status=semantic_status,
            workflow_decision_status=combined_decision_status,
            proposal_gate=proposal_gate,
        )
        if child_fact_state_summary:
            inputs["fact_state_summary"] = {"children": child_fact_state_summary}

    handoff_exists = handoff_path.exists() and handoff_path.is_file()
    collector.check(
        "flow.propose_handoff_exists",
        "P0",
        handoff_exists,
        path=handoff_path,
        pass_message="agentic-flow/analyze-and-propose.md exists",
        fail_message="agentic-flow/analyze-and-propose.md is missing",
        expected="parent Analyze→Propose handoff artifact",
        actual="missing",
        fix_hint="Create agentic-flow/analyze-and-propose.md at the parent run root.",
    )

    handoff_text = ""
    parsed = ParsedHandoff()
    if handoff_exists:
        handoff_text = handoff_path.read_text(encoding="utf-8")
        parsed = parse_handoff(handoff_text)
        validate_handoff_contract(collector, parsed, handoff_text, handoff_path, child_states)
        validate_run_local_paths(collector, root, [handoff_path, *(p for p in _index_paths(root) if p.exists())])
        validate_parent_index(collector, root)
    else:
        validate_run_local_paths(collector, root, [p for p in _index_paths(root) if p.exists()])

    # Parent/child status reconciliation is checked after parent statuses are known.
    if handoff_exists:
        validate_child_status_reconciliation(collector, parsed, child_reports, child_status_blocks)

    return collector.findings, collector.checks, inputs


def _first_existing_index(root: Path) -> str | None:
    for name in ("README.md", "index.md"):
        if (root / name).exists():
            return name
    return None


def _index_paths(root: Path) -> list[Path]:
    return [root / "README.md", root / "index.md"]


def validate_child_report(
    collector: FindingCollector,
    child_name: str,
    spec: dict[str, str],
    report: dict[str, Any],
    report_path: Path,
    child_root: Path,
) -> dict[str, Any]:
    failures: list[str] = []
    missing = sorted(REQUIRED_CHILD_REPORT_KEYS - set(report))
    if missing:
        failures.append(f"missing required keys: {', '.join(missing)}")
    if report.get("schema_version") != SCHEMA_VERSION:
        failures.append(f"schema_version is {report.get('schema_version')!r}")
    if report.get("workflow") != spec["workflow"]:
        failures.append(f"workflow is {report.get('workflow')!r}, expected {spec['workflow']!r}")
    if report.get("status") not in {"pass", "review_required", "fail"}:
        failures.append(f"status is {report.get('status')!r}")
    if not isinstance(report.get("exit_code"), int):
        failures.append("exit_code is not an integer")
    if not isinstance(report.get("summary"), dict):
        failures.append("summary is not an object")
    if not isinstance(report.get("findings"), list):
        failures.append("findings is not a list")
    if not isinstance(report.get("checks"), list):
        failures.append("checks is not a list")
    run_root_value = report.get("run_root")
    if not _child_run_root_matches(run_root_value, child_root):
        failures.append(f"run_root {run_root_value!r} does not match child root {child_root}")

    ok = not failures
    collector.check(
        spec["validation_check"],
        "P1",
        ok,
        path=report_path,
        pass_message=f"{child_name} child report matches the expected workflow and run root",
        fail_message="; ".join(failures) or f"{child_name} child report contract is invalid",
        expected=f"{spec['workflow']} report with run_root matching {spec['dir']}/",
        actual="; ".join(failures) if failures else None,
        fix_hint="Regenerate or correct the child workflow-harness-report.json before validating the combined parent flow.",
    )
    return {"status": report.get("status"), "has_contract_failures": not ok}


def _child_run_root_matches(value: Any, child_root: Path) -> bool:
    if not isinstance(value, str) or not value:
        return False
    root_resolved = child_root.resolve(strict=False)
    candidates = [Path(value)]
    if not Path(value).is_absolute():
        candidates.append(child_root.parent / value)
        candidates.append(Path.cwd() / value)
    for candidate in candidates:
        if candidate.resolve(strict=False) == root_resolved:
            return True
    return False


def normalize_decision_status(value: Any, *, default: str = "review_required") -> str:
    if value is None:
        return default
    cleaned = str(value).strip().strip("` ").lower()
    cleaned = cleaned.replace("→", " ")
    cleaned = re.sub(r"[`*]", "", cleaned)
    cleaned = cleaned.replace("-", "_").replace(" ", "_")
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    if cleaned in {"ok", "passed", "complete", "completed"}:
        return "pass"
    if cleaned in {"ready_for_preview", "ready_preview", "ready"}:
        return "ready_for_preview"
    if cleaned in DECISION_STATUS_ORDER:
        return cleaned
    return default


def worst_decision_status(values: Iterable[Any], *, default: str = "pass") -> str:
    normalized = [normalize_decision_status(value, default=default) for value in values if value is not None]
    if not normalized:
        return default
    return max(normalized, key=lambda value: DECISION_STATUS_ORDER.get(value, 1))


def explicit_status_block(report: dict[str, Any]) -> dict[str, Any]:
    raw = report.get("status_block")
    return raw if isinstance(raw, dict) else {}


def report_finding_status(findings: Iterable[Any], *, semantic_only: bool = False) -> str:
    saw_p1 = False
    for raw in findings:
        if not isinstance(raw, dict):
            continue
        if semantic_only:
            raw_id = str(raw.get("id") or raw.get("check_id") or "")
            if raw.get("source_review") != "semantic_critic" and not raw_id.startswith("semantic."):
                continue
        if raw.get("severity") == "P0":
            return "blocked"
        if raw.get("severity") == "P1":
            saw_p1 = True
    return "review_required" if saw_p1 else "pass"


def derive_formal_validation_status(report: dict[str, Any]) -> str:
    status_block = explicit_status_block(report)
    raw = report.get("formal_validation_status") or status_block.get("formal_validation_status")
    if raw:
        return normalize_decision_status(raw, default="review_required")
    formal = report.get("formal_validation")
    if isinstance(formal, dict) and formal.get("status"):
        return normalize_decision_status(formal.get("status"), default="review_required")
    return normalize_decision_status(report.get("status"), default="review_required")


def derive_semantic_review_status(report: dict[str, Any]) -> str:
    status_block = explicit_status_block(report)
    raw = report.get("semantic_review_status") or status_block.get("semantic_review_status")
    if raw:
        return normalize_decision_status(raw, default="review_required")
    semantic = report.get("semantic_review")
    if isinstance(semantic, dict):
        if semantic.get("status"):
            return normalize_decision_status(semantic.get("status"), default="review_required")
        if semantic.get("enabled") is False:
            return "not_run"
    semantic_finding_status = report_finding_status(report.get("findings", []), semantic_only=True)
    return semantic_finding_status if semantic_finding_status != "pass" else "not_run"


def derive_workflow_decision_status(report: dict[str, Any]) -> str:
    status_block = explicit_status_block(report)
    raw = report.get("workflow_decision_status") or status_block.get("workflow_decision_status")
    if raw:
        return normalize_decision_status(raw, default="review_required")
    workflow_decision = report.get("workflow_decision")
    if isinstance(workflow_decision, dict) and workflow_decision.get("status"):
        return normalize_decision_status(workflow_decision.get("status"), default="review_required")
    report_status = normalize_decision_status(report.get("status"), default="review_required")
    if report_status in {"pass", "ready_for_preview"}:
        # A formally passing child without an explicit workflow-decision status is
        # not decision-grade. The parent must request a decision owner/source/method
        # before presenting the combined result as ready for Preview.
        return "review_required"
    return report_status


def child_status_block(report: dict[str, Any]) -> dict[str, Any]:
    formal_status = derive_formal_validation_status(report)
    semantic_status = derive_semantic_review_status(report)
    workflow_status = worst_decision_status(
        [derive_workflow_decision_status(report), semantic_status if semantic_status != "not_run" else None, formal_status if formal_status != "pass" else None],
        default="pass",
    )
    proposal_gate = report.get("proposal_gate") or explicit_status_block(report).get("proposal_gate")
    if not isinstance(proposal_gate, dict):
        proposal_gate = {"type": "ready_for_preview" if workflow_status in {"pass", "ready_for_preview"} else "request_more_inputs", "status": workflow_status}
    return {
        "formal_validation_status": formal_status,
        "semantic_review_status": semantic_status,
        "workflow_decision_status": workflow_status,
        "proposal_gate": proposal_gate,
    }


def build_request_more_inputs_blockers(child_statuses: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    blockers: list[dict[str, Any]] = []
    for child_name, status_block in sorted(child_statuses.items()):
        for field in ("formal_validation_status", "semantic_review_status", "workflow_decision_status"):
            status = normalize_decision_status(status_block.get(field), default="not_run")
            if status in NON_DECISION_GRADE_STATUSES:
                blockers.append({
                    "owner": f"{child_name}_stage_owner",
                    "source": f"{child_name}.{field}",
                    "method": "Resolve or explicitly accept the child review finding before parent proposal readiness.",
                    "acceptance_criteria": f"{child_name} {field} becomes pass or the parent keeps Propose=request_more_inputs/blocked.",
                    "status": status,
                })
    return blockers


def build_proposal_gate(workflow_decision_status: str, child_statuses: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    normalized = normalize_decision_status(workflow_decision_status, default="review_required")
    if normalized in {"pass", "ready_for_preview"}:
        return {
            "type": "ready_for_preview",
            "status": "pass",
            "blockers": [],
            "explanation": "Formal validation and workflow decision inputs do not expose parent blockers.",
        }
    blockers = build_request_more_inputs_blockers(child_statuses or {})
    if not blockers:
        blockers = [{
            "owner": "parent_decision_owner",
            "source": "workflow_decision_status",
            "method": "Review the validation findings and supply the missing decision-grade evidence.",
            "acceptance_criteria": "workflow_decision_status becomes pass before Preview readiness is claimed.",
            "status": normalized,
        }]
    return {
        "type": "request_more_inputs" if normalized != "blocked" else "blocked",
        "status": normalized,
        "blockers": blockers,
        "explanation": "Parent synthesis is not decision-grade until the listed blockers are resolved.",
    }


def proposal_gate_type(gate: dict[str, Any] | None) -> str:
    if not isinstance(gate, dict):
        return "missing"
    return normalize_decision_status(gate.get("type") or gate.get("status"), default="missing")


def proposal_gate_blockers_complete(gate: dict[str, Any]) -> bool:
    blockers = gate.get("blockers")
    if not isinstance(blockers, list) or not blockers:
        return False
    required = {"owner", "source", "method", "acceptance_criteria"}
    for blocker in blockers:
        if not isinstance(blocker, dict) or not required.issubset({key for key, value in blocker.items() if value}):
            return False
    return True


def status_block_for_report(
    *,
    formal_validation_status: str,
    semantic_review_status: str,
    workflow_decision_status: str,
    proposal_gate: dict[str, Any],
) -> dict[str, Any]:
    return {
        "formal_validation_status": formal_validation_status,
        "semantic_review_status": semantic_review_status,
        "workflow_decision_status": workflow_decision_status,
        "proposal_gate": proposal_gate,
        "explanation": "Formal validation checks artifact structure; semantic review and workflow decision status determine whether the output is decision-grade.",
    }


def import_child_findings(
    collector: FindingCollector,
    child_name: str,
    spec: dict[str, str],
    report: dict[str, Any],
    report_path: Path,
) -> None:
    child_findings_raw = report.get("findings")
    child_findings = child_findings_raw if isinstance(child_findings_raw, list) else []
    for raw in child_findings:
        if not isinstance(raw, dict):
            continue
        severity = raw.get("severity")
        if severity not in {"P0", "P1"}:
            continue
        original_id = str(raw.get("id") or raw.get("check_id") or "unnamed_child_finding")
        collector.finding(
            f"child.{child_name}.{original_id}",
            severity,
            path=report_path,
            field=f"findings[{original_id}]",
            expected=raw.get("expected"),
            actual=raw.get("actual"),
            message=f"Imported {child_name} child {severity} finding: {raw.get('message') or original_id}",
            fix_hint=raw.get("fix_hint") or "Resolve the child workflow finding, then regenerate the child harness report.",
            source={"child_workflow": spec["workflow"], "child_finding_id": original_id},
        )


def import_child_status(
    collector: FindingCollector,
    child_name: str,
    spec: dict[str, str],
    report: dict[str, Any],
    report_path: Path,
) -> None:
    status = report.get("status")
    if status == "fail":
        collector.finding(
            f"child.{child_name}.status_fail",
            "P0",
            path=report_path,
            field="status",
            expected="pass or non-blocking review_required reconciled in parent",
            actual="fail",
            message=f"{child_name} child report status is fail, so the combined parent flow cannot pass.",
            fix_hint="Fix the failing child run or keep the combined parent flow blocked.",
            source={"child_workflow": spec["workflow"], "child_status": status},
        )
    elif status == "review_required":
        collector.finding(
            f"child.{child_name}.status_review_required",
            "P1",
            path=report_path,
            field="status",
            expected="pass or parent handoff explicitly requesting more inputs",
            actual="review_required",
            message=f"{child_name} child report status is review_required and must be carried into the parent flow gate.",
            fix_hint="Do not mark the parent Propose/Preview gates ready until the child review-required condition is resolved or requested as an input.",
            source={"child_workflow": spec["workflow"], "child_status": status},
        )


@dataclass
class ParsedHandoff:
    json_status: dict[str, str] = field(default_factory=dict)
    markdown_status: dict[str, str] = field(default_factory=dict)
    stage_status: dict[str, str] = field(default_factory=dict)
    json_payload: dict[str, Any] | None = None
    has_structured_json: bool = False
    unresolved_gates: list[str] = field(default_factory=list)
    analyze_artifacts: dict[str, Any] = field(default_factory=dict)
    requested_inputs: list[str] = field(default_factory=list)
    status_block: dict[str, Any] = field(default_factory=dict)
    proposal_gate: dict[str, Any] = field(default_factory=dict)


def parse_handoff(text: str) -> ParsedHandoff:
    parsed = ParsedHandoff()
    parsed.json_payload = _extract_agentic_json(text)
    if parsed.json_payload is not None:
        parsed.has_structured_json = True
        raw_status = parsed.json_payload.get("stage_status", {})
        if isinstance(raw_status, dict):
            for stage in CANONICAL_STAGES:
                if stage in raw_status:
                    parsed.json_status[stage] = normalize_stage_status(stage, str(raw_status[stage]))
        raw_artifacts = parsed.json_payload.get("analyze_artifacts", {})
        if isinstance(raw_artifacts, dict):
            parsed.analyze_artifacts = raw_artifacts
        raw_status_block = parsed.json_payload.get("status_block", {})
        if isinstance(raw_status_block, dict):
            parsed.status_block = raw_status_block
        raw_proposal_gate = parsed.json_payload.get("proposal_gate")
        if isinstance(raw_proposal_gate, dict):
            parsed.proposal_gate = raw_proposal_gate
        elif isinstance(parsed.status_block.get("proposal_gate"), dict):
            parsed.proposal_gate = parsed.status_block["proposal_gate"]
        raw_gates = parsed.json_payload.get("unresolved_gates", [])
        if isinstance(raw_gates, list):
            for item in raw_gates:
                if isinstance(item, dict):
                    gate = item.get("gate") or item.get("requested_input") or json.dumps(item, sort_keys=True)
                    parsed.unresolved_gates.append(str(gate))
                    if item.get("requested_input"):
                        parsed.requested_inputs.append(str(item["requested_input"]))
                else:
                    parsed.unresolved_gates.append(str(item))
        for key in ("preview_gate", "execute_gate"):
            gate = parsed.json_payload.get(key)
            if isinstance(gate, dict) and gate.get("status"):
                stage = "Preview" if key.startswith("preview") else "Execute"
                parsed.json_status.setdefault(stage, normalize_stage_status(stage, str(gate.get("status"))))
    parsed.markdown_status = _parse_markdown_stage_status(text)
    parsed.stage_status = {**parsed.markdown_status, **parsed.json_status}
    return parsed


def _extract_agentic_json(text: str) -> dict[str, Any] | None:
    for match in re.finditer(r"```json\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE):
        raw = match.group(1).strip()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and data.get("schema_version") == "agentic-analyze-propose-v1":
            return data
    return None


def _parse_markdown_stage_status(text: str) -> dict[str, str]:
    statuses: dict[str, str] = {}
    stage_re = re.compile(r"^\s*[-*]\s*(Discover|Analyze|Propose|Preview|Execute|Monitor)\s*:\s*(.+?)\s*$", re.IGNORECASE)
    stage_lookup = {stage.lower(): stage for stage in CANONICAL_STAGES}
    for line in text.splitlines():
        match = stage_re.match(line)
        if not match:
            continue
        stage = stage_lookup[match.group(1).lower()]
        value = match.group(2).strip()
        statuses[stage] = normalize_stage_status(stage, value)
    return statuses


def normalize_stage_status(stage: str, value: str) -> str:
    cleaned = value.strip().strip("` ").lower()
    cleaned = cleaned.replace("→", " ")
    cleaned = re.sub(r"[`*]", "", cleaned)
    cleaned = cleaned.replace("-", " ")
    cleaned = cleaned.rstrip(".")
    cleaned = re.sub(r"\s+", " ", cleaned)
    underscored = cleaned.replace(" ", "_")
    if stage == "Discover":
        if "user premise" in cleaned or underscored == "complete_by_user_premise":
            return "complete_by_user_premise"
        if "agent" in cleaned and ("complete" in cleaned or "completed" in cleaned):
            return "complete_by_agent"
        if cleaned in {"complete", "completed"}:
            return "complete_by_agent"
        if "blocked" in cleaned:
            return "blocked"
    if stage == "Analyze":
        if cleaned in {"complete", "completed"}:
            return "complete"
        if "review required" in cleaned or "review_required" in value.lower():
            return "review_required"
        if "blocked" in cleaned:
            return "blocked"
    if stage == "Propose":
        if "ready_for_preview" in value.lower() or "ready for preview" in cleaned:
            return "ready_for_preview"
        if "request_more_inputs" in value.lower() or "request more inputs" in cleaned or "more input" in cleaned:
            return "request_more_inputs"
        if "blocked" in cleaned:
            return "blocked"
    if stage in {"Preview", "Execute"}:
        if cleaned.startswith("blocked") or "blocked" in cleaned:
            return "blocked"
        if cleaned.startswith("ready") or "ready" in cleaned:
            return "ready"
        if cleaned.startswith("complete") or "completed" in cleaned:
            return "complete"
    if stage == "Monitor":
        if "not_started" in value.lower() or "not started" in cleaned:
            return "not_started"
        if "active" in cleaned:
            return "active"
        if "blocked" in cleaned:
            return "blocked"
    return underscored


def validate_handoff_contract(
    collector: FindingCollector,
    parsed: ParsedHandoff,
    text: str,
    handoff_path: Path,
    child_states: dict[str, dict[str, Any]],
) -> None:
    missing_stages = [stage for stage in CANONICAL_STAGES if stage not in parsed.stage_status]
    collector.check(
        "flow.stage_status_table_present",
        "P1",
        not missing_stages,
        path=handoff_path,
        pass_message="handoff declares all canonical stage statuses",
        fail_message=f"handoff is missing canonical stage statuses: {', '.join(missing_stages)}",
        expected="Discover, Analyze, Propose, Preview, Execute, Monitor statuses",
        actual=", ".join(missing_stages) if missing_stages else None,
        fix_hint="Add a Stage status section or structured JSON block naming all six canonical stages.",
    )

    for stage in CANONICAL_STAGES:
        if stage in parsed.json_status and stage in parsed.markdown_status and parsed.json_status[stage] != parsed.markdown_status[stage]:
            collector.finding(
                "flow.stage_status_conflict",
                "P1",
                path=handoff_path,
                field=f"stage_status.{stage}",
                expected=parsed.json_status[stage],
                actual=parsed.markdown_status[stage],
                message=f"Structured JSON and markdown stage statuses conflict for {stage}.",
                fix_hint="Make the markdown Stage status bullets match the structured agentic-analyze-propose JSON block.",
            )
    collector.check(
        "flow.stage_status_conflict",
        "P1",
        not any(
            stage in parsed.json_status
            and stage in parsed.markdown_status
            and parsed.json_status[stage] != parsed.markdown_status[stage]
            for stage in CANONICAL_STAGES
        ),
        path=handoff_path,
        pass_message="JSON and markdown stage statuses do not conflict",
        fail_message="JSON and markdown stage statuses conflict",
        expected="matching statuses when both formats are present",
        actual="conflict",
        fix_hint="Align or remove one status source.",
    )

    discover_ok = parsed.stage_status.get("Discover") in {"complete_by_user_premise", "complete_by_agent", "blocked"}
    collector.check(
        "flow.discover_state_declared",
        "P1",
        discover_ok,
        path=handoff_path,
        pass_message="Discover state is explicitly declared",
        fail_message="Discover must say whether it was supplied by premise, completed by agent, or blocked",
        expected="complete_by_user_premise | complete_by_agent | blocked",
        actual=parsed.stage_status.get("Discover"),
        fix_hint="Declare Discover as complete by user premise, complete by agent, or blocked.",
    )

    artifacts_ok = _analyze_artifacts_declared(parsed, text)
    collector.check(
        "flow.analyze_artifacts_declared",
        "P1",
        artifacts_ok,
        path=handoff_path,
        pass_message="Analyze artifacts declare asset and oracle child report evidence",
        fail_message="Analyze artifacts must link both child harness reports or final verification artifacts",
        expected="asset and oracle child report/final verification artifact paths",
        actual="missing asset or oracle Analyze artifact path",
        fix_hint="Add Analyze artifacts linking the asset and oracle child workflow-harness-report.json files or final verification artifacts.",
    )

    propose_ok = parsed.stage_status.get("Propose") in {"ready_for_preview", "request_more_inputs", "blocked"}
    collector.check(
        "flow.propose_status_declared",
        "P1",
        propose_ok,
        path=handoff_path,
        pass_message="Propose status is one of the allowed values",
        fail_message="Propose must be ready_for_preview, request_more_inputs, or blocked",
        expected="ready_for_preview | request_more_inputs | blocked",
        actual=parsed.stage_status.get("Propose"),
        fix_hint="Set Propose to ready_for_preview, request_more_inputs, or blocked.",
    )

    validate_structured_parent_status(collector, parsed, text, handoff_path)

    unresolved = unresolved_gates_present(parsed, text)
    if unresolved:
        propose_blocks = parsed.stage_status.get("Propose") in {"request_more_inputs", "blocked"}
        collector.check(
            "flow.unresolved_gates_request_more_inputs",
            "P1",
            propose_blocks,
            path=handoff_path,
            pass_message="unresolved gates keep Propose in request_more_inputs or blocked",
            fail_message="unresolved gates are present but Propose is not request_more_inputs or blocked",
            expected="Propose=request_more_inputs or blocked while gates remain unresolved",
            actual=parsed.stage_status.get("Propose"),
            fix_hint="Set Propose to request_more_inputs or blocked until support, eligibility, feed, route, wallet, policy, and live-input gates are resolved.",
        )
        preview_execute_blocked = parsed.stage_status.get("Preview") == "blocked" and parsed.stage_status.get("Execute") == "blocked"
        collector.check(
            "flow.preview_execute_blocked_when_unresolved",
            "P1",
            preview_execute_blocked,
            path=handoff_path,
            pass_message="Preview and Execute remain blocked while unresolved gates remain",
            fail_message="unresolved gates are present but Preview or Execute is not blocked",
            expected="Preview=blocked and Execute=blocked while unresolved gates remain",
            actual=f"Preview={parsed.stage_status.get('Preview')}; Execute={parsed.stage_status.get('Execute')}",
            fix_hint="Keep Preview and Execute blocked; M4 has no human-override bypass.",
        )
    else:
        collector.check(
            "flow.unresolved_gates_request_more_inputs",
            "P1",
            True,
            path=handoff_path,
            pass_message="no unresolved gates requiring request_more_inputs were detected",
        )
        collector.check(
            "flow.preview_execute_blocked_when_unresolved",
            "P1",
            True,
            path=handoff_path,
            pass_message="no unresolved gates requiring Preview/Execute block were detected",
        )

    collector.check(
        "flow.no_unsupported_execution_recommendation",
        "P1",
        not contains_unsupported_execution_recommendation(text),
        path=handoff_path,
        pass_message="handoff does not recommend unsupported execution from Analyze-only evidence",
        fail_message="handoff appears to recommend execution or capital movement from Analyze-only evidence",
        expected="no opening, allocation, signing, or Execute recommendation before Preview",
        actual="execution recommendation detected",
        fix_hint="Replace execution recommendations with request_more_inputs or blocked Preview/Execute gates.",
    )

    execute_status = parsed.stage_status.get("Execute")
    monitor_ok = execute_status == "complete" or parsed.stage_status.get("Monitor") in {"not_started", "blocked"}
    collector.check(
        "flow.monitor_not_started_before_execute",
        "P1",
        monitor_ok,
        path=handoff_path,
        pass_message="Monitor is not started or blocked until Execute is complete",
        fail_message="Monitor cannot be active before Execute is complete",
        expected="Monitor=not_started or blocked unless Execute=complete",
        actual=f"Execute={execute_status}; Monitor={parsed.stage_status.get('Monitor')}",
        fix_hint="Keep Monitor not_started or blocked until an Execute stage completes.",
    )

    if parsed.stage_status.get("Propose") == "request_more_inputs":
        requested_ok = requested_next_checks_named(parsed, text)
        collector.check(
            "flow.requested_next_checks_named",
            "P1",
            requested_ok,
            path=handoff_path,
            pass_message="request_more_inputs handoff names concrete next checks",
            fail_message="Propose=request_more_inputs but concrete next checks are missing",
            expected="requested next checks or requested_input values",
            actual="missing",
            fix_hint="Add a Requested next checks section naming the exact live inputs or validation artifacts needed.",
        )
    else:
        collector.check(
            "flow.requested_next_checks_named",
            "P1",
            True,
            path=handoff_path,
            pass_message="Propose is not request_more_inputs, so requested next checks are not required",
        )


def _analyze_artifacts_declared(parsed: ParsedHandoff, text: str) -> bool:
    serialized = json.dumps(parsed.analyze_artifacts, sort_keys=True).lower() if parsed.analyze_artifacts else ""
    lower = (text + "\n" + serialized).lower()
    asset_ok = (
        "asset-investment-diligence/verification/workflow-harness-report.json" in lower
        or "asset-investment-diligence" in lower and "final-investment-analysis-verification" in lower
        or "asset_child_report" in lower
    )
    oracle_ok = (
        "oracle-analysis/verification/workflow-harness-report.json" in lower
        or "oracle-analysis" in lower and "final-oracle-analysis-verification" in lower
        or "oracle_child_report" in lower
    )
    return asset_ok and oracle_ok


def validate_structured_parent_status(
    collector: FindingCollector,
    parsed: ParsedHandoff,
    text: str,
    handoff_path: Path,
) -> None:
    missing_keys = [key for key in STATUS_BLOCK_REQUIRED_KEYS if key not in parsed.status_block]
    collector.check(
        "flow.parent_status_block_present",
        "P1",
        not missing_keys,
        path=handoff_path,
        pass_message="parent return separates formal validation, semantic review, workflow decision, and proposal gate",
        fail_message=f"parent return status block is missing keys: {', '.join(missing_keys)}",
        expected=", ".join(STATUS_BLOCK_REQUIRED_KEYS),
        actual=", ".join(missing_keys) if missing_keys else None,
        fix_hint="Add structured JSON status_block with formal_validation_status, semantic_review_status, workflow_decision_status, and proposal_gate.",
    )
    explanation_ok = bool(parsed.status_block.get("explanation")) or bool(re.search(r"^##\s+Status block\b[\s\S]{0,1200}\bexplanation\b", text, flags=re.IGNORECASE | re.MULTILINE))
    collector.check(
        "flow.parent_status_explanation_present",
        "P1",
        explanation_ok,
        path=handoff_path,
        pass_message="parent return explains how formal validation differs from decision readiness",
        fail_message="parent return status block lacks a human-readable explanation",
        expected="status explanation describing formal vs semantic/workflow readiness",
        actual="missing explanation",
        fix_hint="Add an Explanation line near the status block or status_block.explanation in JSON.",
    )
    gate = parsed.proposal_gate
    gate_type = proposal_gate_type(gate)
    workflow_status = normalize_decision_status(parsed.status_block.get("workflow_decision_status"), default="review_required")
    propose_status = parsed.stage_status.get("Propose")
    decision_grade = workflow_status in {"pass", "ready_for_preview"} and gate_type in {"pass", "ready_for_preview"}
    parent_not_overclaiming = decision_grade or propose_status in {"request_more_inputs", "blocked"}
    collector.check(
        "flow.parent_decision_status_reconciles_propose",
        "P1",
        parent_not_overclaiming,
        path=handoff_path,
        pass_message="non-decision-grade parent status keeps Propose out of ready_for_preview",
        fail_message="parent status is not decision-grade but Propose is ready_for_preview",
        expected="Propose=request_more_inputs or blocked when workflow_decision_status/proposal_gate is non-pass",
        actual=f"workflow_decision_status={workflow_status}; proposal_gate={gate_type}; Propose={propose_status}",
        fix_hint="Use Propose=request_more_inputs/blocked until child statuses and critic findings support decision-grade readiness.",
    )
    if gate_type == "request_more_inputs" or propose_status == "request_more_inputs":
        collector.check(
            "flow.request_more_inputs_proposal_contract",
            "P1",
            isinstance(gate, dict) and proposal_gate_type(gate) == "request_more_inputs" and proposal_gate_blockers_complete(gate),
            path=handoff_path,
            pass_message="request_more_inputs is represented as a structured proposal gate with actionable blockers",
            fail_message="request_more_inputs lacks owner/source/method/acceptance_criteria blocker contract",
            expected="proposal_gate.type=request_more_inputs with blockers[].owner/source/method/acceptance_criteria",
            actual=json.dumps(gate, sort_keys=True) if isinstance(gate, dict) else "missing proposal_gate",
            fix_hint="Represent request_more_inputs as a first-class proposal_gate object listing blocker owner, source, method, and acceptance criteria.",
        )


def unresolved_gates_present(parsed: ParsedHandoff, text: str) -> bool:
    if parsed.unresolved_gates:
        return True
    sections = extract_markdown_sections(text)
    unresolved_section = sections.get("unresolved gates") or sections.get("blockers") or sections.get("dominant blockers")
    if unresolved_section and re.search(r"^\s*[-*]\s+\S", unresolved_section, flags=re.MULTILINE):
        return True
    families = (
        "support",
        "gearbox support",
        "pfs",
        "credit manager envelope",
        "credit manager",
        "eligibility",
        "kyc",
        "wallet",
        "issuer",
        "transfer",
        "redeem",
        "feed",
        "oracle",
        "safe pricing",
        "lt",
        "lltv",
        "market",
        "route",
        "liquidity",
        "exit",
        "quote",
        "user policy",
        "mandate",
        "position size",
        "live input",
        "current state",
        "fresh data",
    )
    markers = (
        "unsupported",
        "not enabled",
        "unavailable",
        "not eligible",
        "not verified",
        "to be confirmed",
        "tbd",
        "no route",
        "no quote",
        "no active market",
        "no credit manager",
        "cannot determine",
        "insufficient data",
        "not supplied",
        "missing",
        "unknown",
        "unresolved",
        "requires",
        "must check",
        "blocked",
        "review_required",
        "requires confirmation",
    )
    for line in text.lower().splitlines():
        if any(marker in line for marker in markers) and any(family in line for family in families):
            return True
    return False


def contains_unsupported_execution_recommendation(text: str) -> bool:
    patterns = (
        "recommend opening a credit account",
        "ready to open a credit account",
        "open a credit account now",
        "allocate funds",
        "move funds",
        "sign the transaction",
        "sign transactions",
        "move to execute",
        "execute now",
        "preview is ready and execute is ready",
    )
    for line in text.lower().splitlines():
        if any(neg in line for neg in ("do not", "does not", "cannot", "must not", "not recommend", "no signed")):
            continue
        if any(pattern in line for pattern in patterns):
            return True
    return False


def requested_next_checks_named(parsed: ParsedHandoff, text: str) -> bool:
    if parsed.requested_inputs:
        return True
    sections = extract_markdown_sections(text)
    for key in ("requested next checks", "next checks", "requested inputs", "request more inputs"):
        body = sections.get(key)
        if body and re.search(r"^\s*[-*]\s+\S", body, flags=re.MULTILINE):
            return True
    return False


def validate_child_status_reconciliation(
    collector: FindingCollector,
    parsed: ParsedHandoff,
    child_reports: dict[str, dict[str, Any]],
    child_status_blocks: dict[str, dict[str, Any]],
) -> None:
    permissive_status = (
        parsed.stage_status.get("Propose") == "ready_for_preview"
        or parsed.stage_status.get("Preview") in {"ready", "complete"}
        or parsed.stage_status.get("Execute") in {"ready", "complete"}
    )
    child_blockers: list[str] = []
    for child_name, status_block in child_status_blocks.items():
        for field in ("formal_validation_status", "semantic_review_status", "workflow_decision_status"):
            status = normalize_decision_status(status_block.get(field), default="not_run")
            if status in NON_DECISION_GRADE_STATUSES:
                child_blockers.append(f"{child_name}.{field}={status}")
    for child_name, report in child_reports.items():
        if report.get("status") in {"review_required", "fail"}:
            child_blockers.append(f"{child_name} status={report.get('status')}")
        for raw in report.get("findings", []) if isinstance(report.get("findings"), list) else []:
            if isinstance(raw, dict) and raw.get("severity") in {"P0", "P1"}:
                child_blockers.append(f"{child_name}:{raw.get('id') or raw.get('check_id') or 'unnamed'}")
    collector.check(
        "flow.status_reconciles_children",
        "P1",
        not (permissive_status and child_blockers),
        path=".",
        pass_message="parent status does not claim readiness while child reports or critic/status blocks require review",
        fail_message="parent status claims preview/execute readiness while child statuses require review",
        expected="non-pass child formal/semantic/workflow statuses keep parent Propose request_more_inputs/blocked and Preview/Execute blocked",
        actual="; ".join(child_blockers) if child_blockers else "no child blockers",
        fix_hint="Propagate child review_required/fail statuses and critic findings into the parent status block and proposal_gate before claiming readiness.",
    )


def validate_run_local_paths(collector: FindingCollector, root: Path, source_files: Iterable[Path]) -> None:
    failures: list[str] = []
    checked = 0
    for source_file in source_files:
        if not source_file.exists() or not source_file.is_file():
            continue
        text = source_file.read_text(encoding="utf-8")
        candidates = extract_local_markdown_links(text) + extract_code_spanned_paths(text)
        for raw in candidates:
            if not _looks_like_run_artifact_path(raw):
                continue
            checked += 1
            resolved, err = resolve_under_root(raw, root=root, source_file=source_file)
            if err is None and resolved is not None and resolved.exists():
                continue
            # Parent handoff code spans often use parent-root-relative paths even though
            # the handoff itself lives under agentic-flow/. Accept that deterministic form.
            resolved_root, err_root = resolve_under_root(raw, root=root)
            if err_root is None and resolved_root is not None and resolved_root.exists():
                continue
            failures.append(f"{repo_relative(source_file, root)} -> {raw}: {err or err_root or 'target does not exist'}")
    collector.check(
        "links.local_paths_resolve",
        "P0",
        not failures,
        path=".",
        pass_message=f"run-local artifact links resolve ({checked} checked)",
        fail_message="; ".join(failures[:5]) + ("; ..." if len(failures) > 5 else ""),
        expected="all run-local links and code-spanned artifact paths resolve under the parent run root",
        actual="; ".join(failures[:5]) if failures else None,
        fix_hint="Fix local artifact paths so they are source-relative or parent-run-root-relative and remain under the parent run root.",
    )


def _looks_like_run_artifact_path(value: str) -> bool:
    cleaned = _strip_path_value(value)
    if not cleaned or cleaned.startswith("#"):
        return False
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", cleaned):
        return False
    if cleaned.startswith(("asset-investment-diligence/", "oracle-analysis/", "agentic-flow/", "verification/")):
        return True
    if cleaned.endswith("/") and "/" in cleaned:
        return True
    return cleaned.endswith((".md", ".json")) and "/" in cleaned


def validate_parent_index(collector: FindingCollector, root: Path) -> None:
    index_path = next((path for path in _index_paths(root) if path.exists() and path.is_file()), None)
    if index_path is None:
        collector.finding(
            "flow.parent_index_maps_children",
            "P2",
            path=root,
            expected="README.md or index.md mapping child reports and parent handoff",
            actual="missing",
            message="Parent combined run root has no README.md or index.md mapping the child reports and parent handoff.",
            fix_hint="Add a lightweight parent index linking both child reports and agentic-flow/analyze-and-propose.md.",
        )
        collector.check(
            "flow.parent_index_maps_children",
            "P2",
            False,
            path=root,
            fail_message="parent index is missing",
        )
        return
    text = index_path.read_text(encoding="utf-8").lower()
    required = [
        "asset-investment-diligence/verification/workflow-harness-report.json",
        "oracle-analysis/verification/workflow-harness-report.json",
        "agentic-flow/analyze-and-propose.md",
    ]
    missing = [item for item in required if item not in text]
    collector.check(
        "flow.parent_index_maps_children",
        "P2",
        not missing,
        path=index_path,
        pass_message="parent index links child reports and parent handoff",
        fail_message=f"parent index is missing links: {', '.join(missing)}",
        expected="links to both child reports and agentic-flow/analyze-and-propose.md",
        actual=", ".join(missing) if missing else None,
        fix_hint="Update the parent index to link concrete child report/final verification artifacts and the parent handoff, not only child directories.",
    )


def make_report(
    ctx: ValidationContext,
    findings: list[Finding],
    checks: list[CheckResult],
    inputs: dict[str, Any],
    generated_files: list[str] | None = None,
) -> Report:
    finding_dicts = [finding.to_dict() for finding in findings]
    check_dicts = [check.to_dict() for check in checks]
    summary = {severity: sum(1 for finding in findings if finding.severity == severity) for severity in SEVERITIES}
    summary.update(
        {
            "checks_passed": sum(1 for check in checks if check.result == "pass"),
            "checks_failed": sum(1 for check in checks if check.result == "fail"),
            "checks_skipped": sum(1 for check in checks if check.result == "skipped"),
            "files_checked": len({check.path for check in checks if check.path}),
            "json_files_parsed": sum(1 for check in checks if check.id.endswith("json_valid") and check.result == "pass"),
            "links_checked": sum(1 for check in checks if check.id == "links.local_paths_resolve"),
            "declared_paths_checked": sum(1 for check in checks if check.id == "links.local_paths_resolve"),
        }
    )
    if summary["P0"]:
        status, exit_code = "fail", 2
    elif summary["P1"] or (ctx.strict_warnings and summary["P2"]):
        status, exit_code = "review_required", 1
    else:
        status, exit_code = "pass", 0
    formal_validation = {
        "status": status,
        "exit_code": exit_code,
        "basis": "deterministic validator findings: P0 => fail, P1/strict-P2 => review_required, otherwise pass",
    }
    formal_validation_status = normalize_decision_status(inputs.get("formal_validation_status"), default=status)
    if formal_validation_status == "unknown":
        formal_validation_status = status
    workflow_decision = inputs.get("workflow_decision") if isinstance(inputs.get("workflow_decision"), dict) else {}
    if not workflow_decision:
        workflow_decision = {
            "status": status,
            "basis": "no separate workflow decision metadata emitted; mirrors formal validation status",
        }
    semantic_review_status = normalize_decision_status(inputs.get("semantic_review_status"), default="not_run")
    workflow_decision_status = normalize_decision_status(
        inputs.get("workflow_decision_status") or workflow_decision.get("status"),
        default=status,
    )
    proposal_gate_input = inputs.get("proposal_gate")
    if isinstance(proposal_gate_input, dict):
        proposal_gate: dict[str, Any] = proposal_gate_input
    else:
        proposal_gate = build_proposal_gate(workflow_decision_status)
    status_block_input = inputs.get("status_block")
    if isinstance(status_block_input, dict):
        status_block: dict[str, Any] = dict(status_block_input)
    else:
        status_block = {}
    status_block.update(
        status_block_for_report(
            formal_validation_status=formal_validation_status,
            semantic_review_status=semantic_review_status,
            workflow_decision_status=workflow_decision_status,
            proposal_gate=proposal_gate,
        )
    )
    fact_state_summary = inputs.get("fact_state_summary") if isinstance(inputs.get("fact_state_summary"), dict) else {}
    return Report(
        schema_version=SCHEMA_VERSION,
        generated_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        workflow=ctx.workflow_id,
        run_root=repo_relative(ctx.run_root, ctx.repo_root),
        status=status,
        exit_code=exit_code,
        summary=summary,
        inputs=inputs,
        findings=finding_dicts,
        checks=check_dicts,
        generated_files=generated_files or [],
        formal_validation_status=formal_validation_status,
        semantic_review_status=semantic_review_status,
        workflow_decision_status=workflow_decision_status,
        proposal_gate=proposal_gate,
        status_block=status_block,
        formal_validation=formal_validation,
        workflow_decision=workflow_decision,
        fact_state_summary=fact_state_summary,
        rendered_outputs={},
    )


def render_json(report: Report) -> str:
    return json.dumps(report.to_dict(), separators=(",", ":"), sort_keys=True)


def render_markdown(report: Report, command: list[str]) -> str:
    data = report.to_dict()
    json_copy = dict(data)
    json_copy["rendered_outputs"] = {}
    rows = [
        "# Workflow harness verification",
        "",
        f"- Workflow: {report.workflow}",
        f"- Run root: {report.run_root}",
        f"- Status: {report.status}",
        f"- Formal validation: {report.formal_validation.get('status', report.status)}",
        f"- Workflow decision: {report.workflow_decision.get('status', report.status)}",
        f"- Generated at: {report.generated_at}",
        f"- Validator command: `{_escape_pipe(' '.join(command))}`",
        f"- Exit code: {report.exit_code}",
        "",
        "## Summary",
        "",
        "| Severity | Count |",
        "| --- | ---: |",
    ]
    for severity in SEVERITIES:
        rows.append(f"| {severity} | {report.summary.get(severity, 0)} |")
    rows.extend(["", "## Findings", "", "| Severity | Check ID | Path | Message | Fix hint |", "| --- | --- | --- | --- | --- |"])
    if report.findings:
        for finding in report.findings:
            rows.append(
                "| {severity} | {check_id} | {path} | {message} | {fix_hint} |".format(
                    severity=_escape_pipe(str(finding.get("severity", ""))),
                    check_id=_escape_pipe(str(finding.get("id", ""))),
                    path=_escape_pipe(str(finding.get("path", ""))),
                    message=_escape_pipe(str(finding.get("message", ""))),
                    fix_hint=_escape_pipe(str(finding.get("fix_hint") or "")),
                )
            )
    else:
        rows.append("| - | - | - | No findings. | - |")
    rows.extend(["", "## Checks run", "", "| Check ID | Result | Path | Message |", "| --- | --- | --- | --- |"])
    for check in report.checks:
        rows.append(
            "| {check_id} | {result} | {path} | {message} |".format(
                check_id=_escape_pipe(str(check.get("id", ""))),
                result=_escape_pipe(str(check.get("result", ""))),
                path=_escape_pipe(str(check.get("path", ""))),
                message=_escape_pipe(str(check.get("message", ""))),
            )
        )
    rows.extend(["", "## JSON report", "", "```json", json.dumps(json_copy, separators=(",", ":"), sort_keys=True), "```", ""])
    return "\n".join(rows)


def _escape_pipe(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def determine_generated_files(ctx: ValidationContext) -> list[str]:
    generated: list[str] = []
    if ctx.report_dir is not None:
        generated.append(repo_relative(ctx.report_dir / "workflow-harness-report.json", ctx.repo_root))
        generated.append(repo_relative(ctx.report_dir / "workflow-harness-verification.md", ctx.repo_root))
    if ctx.write_verification:
        name = "combined-analyze-propose-verification.md" if ctx.workflow_arg == "combined-analyze-propose" else "workflow-harness-verification.md"
        generated.append(repo_relative(ctx.run_root / "verification" / name, ctx.repo_root))
    return generated


def write_outputs(ctx: ValidationContext, report: Report, markdown: str) -> None:
    if ctx.report_dir is not None:
        ctx.report_dir.mkdir(parents=True, exist_ok=True)
        (ctx.report_dir / "workflow-harness-report.json").write_text(render_json(report) + "\n", encoding="utf-8")
        (ctx.report_dir / "workflow-harness-verification.md").write_text(markdown, encoding="utf-8")
    if ctx.write_verification:
        verification_dir = ctx.run_root / "verification"
        verification_dir.mkdir(parents=True, exist_ok=True)
        name = "combined-analyze-propose-verification.md" if ctx.workflow_arg == "combined-analyze-propose" else "workflow-harness-verification.md"
        target = verification_dir / name
        canonical = CANONICAL_FINAL_VERIFICATIONS.get(ctx.workflow_id)
        if canonical and (ctx.run_root / canonical).resolve(strict=False) == target.resolve(strict=False):
            raise RuntimeError(f"refusing to overwrite canonical final verification: {canonical}")
        target.write_text(markdown, encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate front-knowledge-base workflow run artifacts.")
    parser.add_argument("--workflow", required=True, choices=sorted(WORKFLOW_IDS))
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--format", default="json", choices=sorted(VALID_FORMATS))
    parser.add_argument("--parent-return", help="Optional combined workflow parent-return artifact path, relative to --run-root or the repository root.")
    parser.add_argument("--report-dir")
    parser.add_argument("--write-verification", action="store_true")
    parser.add_argument("--strict-warnings", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = Path.cwd().resolve(strict=False)
    run_root = Path(args.run_root)
    if not run_root.is_absolute():
        run_root = (repo_root / run_root).resolve(strict=False)
    else:
        run_root = run_root.resolve(strict=False)
    report_dir = Path(args.report_dir).resolve(strict=False) if args.report_dir else None
    command = [Path(sys.argv[0]).as_posix(), *(argv if argv is not None else sys.argv[1:])]
    ctx = ValidationContext(
        workflow_arg=args.workflow,
        workflow_id=WORKFLOW_IDS[args.workflow],
        run_root=run_root,
        repo_root=repo_root,
        formats=args.format,
        strict_warnings=args.strict_warnings,
        command=command,
        parent_return=args.parent_return,
        report_dir=report_dir,
        write_verification=args.write_verification,
    )
    if args.workflow == "combined-analyze-propose":
        findings, checks, inputs = validate_combined(ctx)
    else:
        findings, checks, inputs = validate_common(ctx)
    generated_files = determine_generated_files(ctx)
    report = make_report(ctx, findings, checks, inputs, generated_files=generated_files)
    markdown = render_markdown(report, command)
    if args.format == "json,markdown" and ctx.report_dir is None and not ctx.write_verification:
        report.rendered_outputs["markdown"] = markdown
        markdown = render_markdown(report, command)
    write_outputs(ctx, report, markdown)
    if args.format == "markdown":
        sys.stdout.write(markdown)
    else:
        sys.stdout.write(render_json(report) + "\n")
    return report.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
