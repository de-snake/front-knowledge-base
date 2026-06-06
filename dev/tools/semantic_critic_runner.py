#!/usr/bin/env python3
"""Independent semantic critic runner for workflow-stage artifacts.

The runner is intentionally standard-library only. It prepares a bounded review
bundle for an independent critic command and normalizes that critic's JSON into a
stable machine-readable report. When no critic command is configured, it returns
semantic_review_unavailable instead of fabricating a pass.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUBRIC = REPO_ROOT / "dev/implementation/workflow-harness/semantic-critic-rubric-v1.md"
SCHEMA_VERSION = "workflow-semantic-critic-report-v1"
REQUEST_SCHEMA_VERSION = "workflow-semantic-critic-request-v1"
RUBRIC_VERSION = "workflow-semantic-critic-rubric-v1"
VALID_REPORT_STATUSES = {"pass", "review_required", "blocked", "semantic_review_unavailable"}
VALID_FINDING_STATUSES = {"pass", "review_required", "blocked"}
STATUS_EXIT_CODES = {
    "pass": 0,
    "review_required": 1,
    "semantic_review_unavailable": 1,
    "blocked": 2,
}
DEFAULT_MAX_BYTES_PER_ARTIFACT = 12_000
DEFAULT_MAX_TOTAL_BYTES = 60_000
DEFAULT_MAX_DIRECTORY_ENTRIES = 80


@dataclass
class SemanticEvidence:
    path: str
    quote: str


@dataclass
class SemanticFinding:
    id: str
    status: str
    severity: str
    violated_requirement: str
    evidence: dict[str, str]
    required_remediation: str
    source: str = "semantic_critic"


@dataclass
class SemanticReport:
    schema_version: str = SCHEMA_VERSION
    generated_at: str = ""
    rubric_version: str = RUBRIC_VERSION
    status: str = "semantic_review_unavailable"
    stage: dict[str, Any] = field(default_factory=dict)
    critic: dict[str, Any] = field(default_factory=dict)
    request_summary: dict[str, Any] = field(default_factory=dict)
    findings: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["generated_at"] = data["generated_at"] or utc_now()
        return data


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def repo_relative(path: Path, root: Path = REPO_ROOT) -> str:
    resolved = path.resolve(strict=False)
    root_resolved = root.resolve(strict=False)
    try:
        return resolved.relative_to(root_resolved).as_posix() or "."
    except ValueError:
        return resolved.as_posix()


def resolve_path(path_text: str | None, *, base: Path = REPO_ROOT) -> Path | None:
    if not path_text:
        return None
    path = Path(path_text).expanduser()
    if not path.is_absolute():
        path = base / path
    return path.resolve(strict=False)


def file_sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_bounded_text(path: Path, max_bytes: int) -> tuple[str, bool, int, str | None]:
    if not path.exists() or not path.is_file():
        return "", False, 0, None
    byte_count = path.stat().st_size
    with path.open("rb") as handle:
        raw = handle.read(max_bytes + 1)
    truncated = len(raw) > max_bytes
    if truncated:
        raw = raw[:max_bytes]
    return raw.decode("utf-8", errors="replace"), truncated or byte_count > max_bytes, byte_count, file_sha256(path)


def directory_manifest(path: Path, max_entries: int) -> tuple[str, bool, int]:
    if not path.is_dir():
        return "", False, 0
    entries: list[str] = []
    count = 0
    for child in sorted(path.rglob("*")):
        if child.is_dir():
            continue
        count += 1
        if len(entries) < max_entries:
            entries.append(repo_relative(child))
    truncated = count > len(entries)
    text = "\n".join(entries)
    if truncated:
        text += f"\n... {count - len(entries)} more files omitted by semantic critic directory budget"
    return text, truncated, count


def artifact_record(path_text: str | Path | None, kind: str, *, max_bytes: int, max_directory_entries: int) -> dict[str, Any]:
    if path_text is None:
        return {
            "kind": kind,
            "path": "not_configured",
            "exists": False,
            "content": "",
            "truncated": False,
            "byte_count": 0,
            "sha256": None,
        }
    path = resolve_path(str(path_text)) or Path(str(path_text))
    record: dict[str, Any] = {
        "kind": kind,
        "path": repo_relative(path),
        "exists": path.exists(),
        "content": "",
        "truncated": False,
        "byte_count": 0,
        "sha256": None,
    }
    if path.is_dir():
        content, truncated, count = directory_manifest(path, max_directory_entries)
        record.update({"type": "directory", "content": content, "truncated": truncated, "entry_count": count})
        return record
    if path.is_file():
        content, truncated, byte_count, sha = read_bounded_text(path, max_bytes)
        record.update({"type": "file", "content": content, "truncated": truncated, "byte_count": byte_count, "sha256": sha})
        return record
    record["type"] = "missing"
    return record


def load_json_file(path: Path | None) -> dict[str, Any] | None:
    if not path or not path.is_file():
        return None
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


def derive_stage_contract(packet_path: Path | None) -> dict[str, Any]:
    packet = load_json_file(packet_path)
    payload = (packet or {}).get("task_payload") if isinstance(packet, dict) else None
    if not isinstance(payload, dict):
        return {"packet_path": repo_relative(packet_path) if packet_path else "not_configured", "derived": False}
    keys = (
        "command",
        "workflow_id",
        "stage_id",
        "stage_title",
        "scope_id",
        "scope_type",
        "run_root",
        "artifact_dir",
        "objective",
        "input_paths",
        "required_outputs",
        "required_packet_headings",
        "blocking_unknowns",
        "stage_contract",
        "protocol_adapter",
        "validation_command",
        "return_envelope",
        "do_not",
    )
    return {"derived": True, **{key: payload.get(key) for key in keys}}


def enforce_total_content_budget(records: list[dict[str, Any]], max_total_bytes: int) -> int:
    used = 0
    for record in records:
        content = record.get("content")
        if not isinstance(content, str) or not content:
            continue
        raw = content.encode("utf-8", errors="replace")
        remaining = max(max_total_bytes - used, 0)
        if len(raw) <= remaining:
            used += len(raw)
            continue
        kept = raw[:remaining].decode("utf-8", errors="replace") if remaining else ""
        marker = "\n[TRUNCATED by workflow semantic critic total context budget]\n"
        record["content"] = kept + marker
        record["truncated"] = True
        record["truncated_by_total_budget"] = True
        used = max_total_bytes
    return used


def build_request(args: argparse.Namespace) -> dict[str, Any]:
    packet_path = resolve_path(args.packet)
    records: list[dict[str, Any]] = []
    rubric = artifact_record(args.rubric, "rubric", max_bytes=args.max_bytes_per_artifact, max_directory_entries=args.max_directory_entries)
    packet = artifact_record(packet_path, "packet", max_bytes=args.max_bytes_per_artifact, max_directory_entries=args.max_directory_entries)
    records.extend([rubric, packet])
    stage_contract_artifact = None
    if args.stage_contract:
        stage_contract_artifact = artifact_record(args.stage_contract, "stage_contract", max_bytes=args.max_bytes_per_artifact, max_directory_entries=args.max_directory_entries)
        records.append(stage_contract_artifact)
    output_artifacts = [
        artifact_record(path, "output_artifact", max_bytes=args.max_bytes_per_artifact, max_directory_entries=args.max_directory_entries)
        for path in args.output
    ]
    evidence_ledgers = [
        artifact_record(path, "evidence_ledger", max_bytes=args.max_bytes_per_artifact, max_directory_entries=args.max_directory_entries)
        for path in args.evidence_ledger
    ]
    validator_summary = artifact_record(args.validator_summary, "validator_summary", max_bytes=args.max_bytes_per_artifact, max_directory_entries=args.max_directory_entries) if args.validator_summary else None
    parent_contexts = [
        artifact_record(path, "parent_context", max_bytes=args.max_bytes_per_artifact, max_directory_entries=args.max_directory_entries)
        for path in args.parent_context
    ]
    records.extend(output_artifacts)
    records.extend(evidence_ledgers)
    if validator_summary:
        records.append(validator_summary)
    records.extend(parent_contexts)
    content_budget_used = enforce_total_content_budget(records, args.max_total_bytes)
    return {
        "schema_version": REQUEST_SCHEMA_VERSION,
        "generated_at": utc_now(),
        "rubric_version": RUBRIC_VERSION,
        "instructions": "Apply the rubric as an independent critic. Return only JSON matching workflow-semantic-critic-report-v1.",
        "stage_contract": derive_stage_contract(packet_path),
        "stage_contract_artifact": stage_contract_artifact,
        "rubric": rubric,
        "packet": packet,
        "output_artifacts": output_artifacts,
        "evidence_ledgers": evidence_ledgers,
        "validator_summary": validator_summary,
        "parent_contexts": parent_contexts,
        "bounds": {
            "max_bytes_per_artifact": args.max_bytes_per_artifact,
            "max_total_bytes": args.max_total_bytes,
            "content_budget_used": content_budget_used,
            "max_directory_entries": args.max_directory_entries,
        },
    }


def request_summary(request: dict[str, Any]) -> dict[str, Any]:
    groups = [
        request.get("rubric"),
        request.get("packet"),
        request.get("stage_contract_artifact"),
        request.get("validator_summary"),
        *request.get("output_artifacts", []),
        *request.get("evidence_ledgers", []),
        *request.get("parent_contexts", []),
    ]
    records = [item for item in groups if isinstance(item, dict)]
    return {
        "artifact_count": len(records),
        "missing_artifacts": [item["path"] for item in records if not item.get("exists")],
        "truncated_artifacts": [item["path"] for item in records if item.get("truncated")],
        "bounds": request.get("bounds", {}),
    }


def unavailable_report(request: dict[str, Any], reason: str) -> dict[str, Any]:
    stage = request.get("stage_contract", {})
    packet_path = ((request.get("packet") or {}).get("path")) or "not_available"
    finding = SemanticFinding(
        id="semantic.semantic_review_unavailable",
        status="review_required",
        severity="P1",
        violated_requirement="Independent semantic critic must run when semantic review is enabled.",
        evidence={"path": packet_path, "quote": reason[:500]},
        required_remediation="Configure an independent critic command or rerun without the semantic-review gate only for scaffold/deterministic-only checks.",
    )
    return SemanticReport(
        generated_at=utc_now(),
        status="semantic_review_unavailable",
        stage=stage,
        critic={"type": "unavailable"},
        request_summary=request_summary(request),
        findings=[asdict(finding)],
    ).to_dict()


def severity_for_status(status: str) -> str:
    if status == "blocked":
        return "P0"
    if status == "review_required":
        return "P1"
    return "P2"


def normalize_evidence(item: dict[str, Any]) -> dict[str, str]:
    evidence = item.get("evidence")
    if isinstance(evidence, dict):
        path = str(evidence.get("path") or item.get("evidence_path") or "not_available")
        quote = str(evidence.get("quote") or item.get("evidence_quote") or "")
        return {"path": path, "quote": quote[:2000]}
    return {
        "path": str(item.get("evidence_path") or "not_available"),
        "quote": str(item.get("evidence_quote") or item.get("quote") or "")[:2000],
    }


def normalize_provider_report(raw: dict[str, Any], request: dict[str, Any], critic_command: str) -> dict[str, Any]:
    stage = request.get("stage_contract", {})
    requested_status = str(raw.get("status") or "").strip()
    status = requested_status if requested_status in {"pass", "review_required", "blocked"} else "blocked"
    raw_findings = raw.get("findings")
    if not isinstance(raw_findings, list):
        raw_findings = []
    findings: list[dict[str, Any]] = []
    stage_id = str(stage.get("stage_id") or "stage")
    for index, item in enumerate(raw_findings, start=1):
        if not isinstance(item, dict):
            continue
        finding_status = str(item.get("status") or status).strip()
        if finding_status not in VALID_FINDING_STATUSES:
            finding_status = status if status in VALID_FINDING_STATUSES else "blocked"
        severity = str(item.get("severity") or severity_for_status(finding_status)).upper()
        if severity not in {"P0", "P1", "P2"}:
            severity = severity_for_status(finding_status)
        finding = SemanticFinding(
            id=str(item.get("id") or f"semantic.{stage_id}.{index}"),
            status=finding_status,
            severity=severity,
            violated_requirement=str(item.get("violated_requirement") or item.get("requirement") or "Semantic critic reported an unspecified requirement violation."),
            evidence=normalize_evidence(item),
            required_remediation=str(item.get("required_remediation") or item.get("remediation") or item.get("fix_hint") or "Remediate the semantic critic finding and rerun the gate."),
        )
        findings.append(asdict(finding))
    if requested_status not in {"pass", "review_required", "blocked"}:
        findings.append(asdict(SemanticFinding(
            id="semantic.critic_output_invalid_status",
            status="blocked",
            severity="P0",
            violated_requirement="Semantic critic output status must be pass, review_required, or blocked.",
            evidence={"path": "critic_stdout", "quote": f"status={requested_status or 'missing'}"},
            required_remediation="Fix the critic adapter to emit the required schema before trusting semantic review.",
        )))
    elif status != "pass" and not findings:
        findings.append(asdict(SemanticFinding(
            id="semantic.critic_output_missing_findings",
            status="blocked",
            severity="P0",
            violated_requirement="Non-pass semantic critic output must include actionable findings.",
            evidence={"path": "critic_stdout", "quote": stable_json(raw)[:1000]},
            required_remediation="Return at least one finding with severity, violated_requirement, evidence, and required_remediation.",
        )))
        status = "blocked"
    if any(item["severity"] == "P0" for item in findings):
        status = "blocked"
    elif any(item["severity"] == "P1" for item in findings) and status == "pass":
        status = "review_required"
    command_label = shlex.split(critic_command)[0] if critic_command else "not_configured"
    return SemanticReport(
        generated_at=utc_now(),
        status=status,
        stage=stage,
        critic={"type": "command", "command_label": command_label},
        request_summary=request_summary(request),
        findings=findings,
    ).to_dict()


def run_critic_command(command: str, request: dict[str, Any], request_out: Path | None, timeout: int) -> dict[str, Any]:
    if request_out:
        request_out.parent.mkdir(parents=True, exist_ok=True)
        request_out.write_text(stable_json(request))
        request_path = request_out
        cleanup = None
    else:
        cleanup = tempfile.TemporaryDirectory(prefix="workflow-semantic-critic-")
        request_path = Path(cleanup.name) / "request.json"
        request_path.write_text(stable_json(request))
    try:
        argv = shlex.split(command) + [str(request_path)]
        proc = subprocess.run(argv, cwd=REPO_ROOT, text=True, capture_output=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        if cleanup:
            cleanup.cleanup()
        return unavailable_report(request, f"critic command unavailable: {exc}")
    if cleanup:
        cleanup.cleanup()
    if proc.returncode != 0:
        reason = (proc.stderr or proc.stdout or f"critic command exited {proc.returncode}").strip()
        return unavailable_report(request, reason[:1000])
    try:
        raw = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return unavailable_report(request, f"critic stdout was not JSON: {exc.msg}")
    if not isinstance(raw, dict):
        return unavailable_report(request, "critic stdout JSON root was not an object")
    return normalize_provider_report(raw, request, command)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run an independent semantic critic over bounded workflow-stage artifacts.")
    parser.add_argument("--packet", required=True, help="Stage packet JSON or Markdown path.")
    parser.add_argument("--stage-contract", help="Optional explicit stage contract artifact. Defaults to contract fields derived from the packet JSON.")
    parser.add_argument("--output", action="append", default=[], help="Stage output artifact path. May be repeated.")
    parser.add_argument("--evidence-ledger", action="append", default=[], help="Evidence ledger or source-evidence path. May be repeated.")
    parser.add_argument("--validator-summary", help="Deterministic validator summary JSON/Markdown path.")
    parser.add_argument("--parent-context", action="append", default=[], help="Parent context artifact path when the stage needs it. May be repeated.")
    parser.add_argument("--rubric", default=str(DEFAULT_RUBRIC), help="Versioned semantic critic rubric path.")
    parser.add_argument("--critic-command", help="Independent critic command. The bounded request JSON path is appended as the last argv item. Defaults to WORKFLOW_SEMANTIC_CRITIC_COMMAND.")
    parser.add_argument("--timeout", type=int, default=120, help="Critic command timeout in seconds.")
    parser.add_argument("--max-bytes-per-artifact", type=int, default=DEFAULT_MAX_BYTES_PER_ARTIFACT)
    parser.add_argument("--max-total-bytes", type=int, default=DEFAULT_MAX_TOTAL_BYTES)
    parser.add_argument("--max-directory-entries", type=int, default=DEFAULT_MAX_DIRECTORY_ENTRIES)
    parser.add_argument("--request-out", help="Optional path to persist the bounded critic request JSON.")
    parser.add_argument("--report-out", help="Optional path to persist the normalized semantic critic report JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    request = build_request(args)
    request_out_path = resolve_path(args.request_out) if args.request_out else None
    if request_out_path:
        request_out_path.parent.mkdir(parents=True, exist_ok=True)
        request_out_path.write_text(stable_json(request))
    command = args.critic_command or os.environ.get("WORKFLOW_SEMANTIC_CRITIC_COMMAND")
    if command:
        report = run_critic_command(command, request, request_out_path, args.timeout)
    else:
        report = unavailable_report(request, "no WORKFLOW_SEMANTIC_CRITIC_COMMAND or --critic-command configured")
    if args.report_out:
        report_path = resolve_path(args.report_out)
        assert report_path is not None
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(stable_json(report))
    print(stable_json(report), end="")
    return STATUS_EXIT_CODES.get(str(report.get("status")), 2)


if __name__ == "__main__":
    raise SystemExit(main())
