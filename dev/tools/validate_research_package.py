#!/usr/bin/env python3
"""Integrity checks for shareable methodology-guided research packages.

The checker keeps the original apyUSD package contract strict, while also
supporting later rich-report packages generated from the old asset-risk corpus.
It intentionally does not judge investment quality.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

APY_REQUIRED_FILES = [
    "README.md",
    "REPRODUCE.md",
    "RESULT.md",
    "input.json",
    "run/README.md",
    "run/methodology.md",
    "run/tokens/eth-mainnet-apyusd/technical-report.md",
    "run/tokens/eth-mainnet-apyusd/verification.md",
    "run/tokens/eth-mainnet-apyusd/research/onchain-admin.md",
    "run/tokens/eth-mainnet-apyusd/research/issuer-backing-security.md",
    "run/tokens/eth-mainnet-apyusd/research/transfer-liquidity-oracle-governance.md",
    "run/tokens/eth-mainnet-apyusd/research/raw/onchain-admin-snapshot-2026-06-04.json",
    "run/tokens/eth-mainnet-apyusd/research/raw/onchain-market-snapshot-2026-06-04.json",
    "run/x-research/x-research-apyusd-points-stac-pt-2026-08-27.md",
    "run/investment-analysis/investment-analyst-report-points-pt-risk-return.md",
    "run/investment-analysis/quantitative-underwriting-methodology.md",
    "run/pt-markets/pendle-pt-eth-mainnet-apyusd-2026-08-27/analyst-report.md",
    "run/pt-markets/pendle-pt-eth-mainnet-apyusd-2026-08-27/technical-report.md",
]

APY_RESULT_SECTIONS = [
    "# apyx apyUSD — investment analyst risk note",
    "## 1. Executive view",
    "## 2. What the token represents",
    "## 3. Main risk implications",
    "## 4. Backing and NAV quality",
    "## 5. Liquidity and exit risk",
    "## 6. Controls, governance, and legal restrictions",
    "## 7. Pricing / oracle risk in plain language",
    "## 8. X / social research layer",
    "## 9. Quantitative risk / return layer",
    "## 10. What must be checked before live use",
    "## 11. Evidence quality",
    "## 12. Source map",
    "## 13. Technical appendix pointer",
]

APY_TECHNICAL_SECTIONS = [
    "# apyx apyUSD — MVP asset risk dossier",
    "## 1. Agent-context summary",
    "## 2. One-paragraph mechanism",
    "## 3. Identity and token semantics",
    "## 4. Issuer / protocol and business model",
    "## 5. Backing, NAV, and exposure map",
    "## 6. Contract admin, multisigs, and sensitive actions",
    "## 7. Audits, formal verification, and incidents",
    "## 8. Transferability, redemption, and liquidity",
    "## 9. Oracle and pricing methodology",
    "## 10. Governance / change-feed watchlist",
    "## 11. Data quality and missing-data behavior",
    "## 12. Highest-impact unknowns",
    "## 13. Sources",
]

APY_REQUIRED_RESULT_SNIPPETS = [
    "0x38EEb52F0771140d10c4E9A9a72349A329Fe8a6A",
    "not an asset-selection recommendation",
    "not an investment recommendation",
    "review_required",
    "block_automation",
    "run/tokens/eth-mainnet-apyusd/technical-report.md",
    "run/x-research/x-research-apyusd-points-stac-pt-2026-08-27.md",
    "PT-apyUSD",
    "5.6168%",
    "Risk-adjusted annualized return before points: -14.70%",
]

REQUIRED_METHODOLOGY_SNIPPETS = [
    "## Source priority",
    "## Asset-specific pipeline",
    "### 1. Identity and token semantics",
    "### 9. Data quality and missing-data behavior",
    "## Acceptance criteria",
]

LOCAL_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
SOURCE_ID_RE = re.compile(r"\[([A-Z]*\d+)\]")


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def require(condition: bool, errors: list[str], message: str) -> None:
    if not condition:
        errors.append(message)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_required_files(root: Path, files: list[str], errors: list[str]) -> None:
    for name in files:
        require((root / name).is_file(), errors, f"missing required file: {name}")


def check_json_file(path: Path, errors: list[str]) -> Any | None:
    if not path.exists():
        errors.append(f"missing JSON file: {rel(path, path.parent)}")
        return None
    try:
        return json.loads(read(path))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON {path}: {exc}")
        return None


def check_sections(text: str, sections: list[str], label: str, errors: list[str]) -> None:
    last = -1
    for section in sections:
        idx = text.find(section)
        require(idx != -1, errors, f"{label}: missing section {section!r}")
        if idx != -1:
            require(idx > last, errors, f"{label}: section out of order {section!r}")
            last = idx


def check_source_map(text: str, heading: str, label: str, errors: list[str]) -> None:
    used = sorted({match for match in SOURCE_ID_RE.findall(text) if match.startswith(("S", "D", "O", "P"))})
    if not used:
        return
    source_start = text.find(heading)
    require(source_start != -1, errors, f"{label}: missing source-map heading {heading!r}")
    source_text = text[source_start:] if source_start != -1 else ""
    for source_id in used:
        require(
            re.search(rf"\b{re.escape(source_id)}\b", source_text) is not None,
            errors,
            f"{label}: source ID {source_id} is used but not resolved after {heading}",
        )


def check_local_links(root: Path, errors: list[str]) -> None:
    for path in root.rglob("*.md"):
        text = read(path)
        for target in LOCAL_LINK_RE.findall(text):
            clean_target = target.split("#", 1)[0]
            if not clean_target or re.match(r"^[a-z]+://", clean_target) or clean_target.startswith("mailto:"):
                continue
            resolved = (path.parent / clean_target).resolve()
            require(resolved.exists(), errors, f"broken local markdown link in {rel(path, root)} -> {target}")


def iter_declared_paths(value: Any) -> list[str]:
    paths: list[str] = []
    if isinstance(value, str):
        if value.endswith((".md", ".json", ".txt", ".csv")) or value.startswith("run/") or value in {"RESULT.md", "REPRODUCE.md", "README.md"}:
            paths.append(value)
    elif isinstance(value, list):
        for item in value:
            paths.extend(iter_declared_paths(item))
    elif isinstance(value, dict):
        for item in value.values():
            paths.extend(iter_declared_paths(item))
    return paths


def check_declared_artifacts(root: Path, input_doc: dict[str, Any], errors: list[str]) -> None:
    keys = [
        "methodology",
        "research_artifacts",
        "outputs",
        "x_social_artifacts",
        "quantitative_artifacts",
        "pt_market_artifacts",
        "pt_markets",
        "social_scopes",
    ]
    for key in keys:
        for path_text in iter_declared_paths(input_doc.get(key)):
            if path_text.startswith(("http://", "https://")):
                continue
            require((root / path_text).exists(), errors, f"input.json declares missing artifact: {path_text}")


def check_methodology(root: Path, errors: list[str]) -> None:
    methodology_path = root / "run/methodology.md"
    if not methodology_path.exists():
        return
    methodology = read(methodology_path)
    for snippet in REQUIRED_METHODOLOGY_SNIPPETS:
        require(snippet in methodology, errors, f"run/methodology.md missing required snippet: {snippet!r}")


def check_apy_package(root: Path, errors: list[str]) -> None:
    check_required_files(root, APY_REQUIRED_FILES, errors)
    for name in [
        "input.json",
        "run/tokens/eth-mainnet-apyusd/research/raw/onchain-admin-snapshot-2026-06-04.json",
        "run/tokens/eth-mainnet-apyusd/research/raw/onchain-market-snapshot-2026-06-04.json",
    ]:
        if (root / name).exists():
            check_json_file(root / name, errors)
    result_path = root / "RESULT.md"
    technical_path = root / "run/tokens/eth-mainnet-apyusd/technical-report.md"
    if result_path.exists():
        result = read(result_path)
        check_sections(result, APY_RESULT_SECTIONS, "RESULT.md", errors)
        for snippet in APY_REQUIRED_RESULT_SNIPPETS:
            require(snippet in result, errors, f"RESULT.md missing required snippet: {snippet!r}")
        check_source_map(result, "## 12. Source map", "RESULT.md", errors)
    if technical_path.exists():
        technical = read(technical_path)
        check_sections(technical, APY_TECHNICAL_SECTIONS, "technical-report.md", errors)
        check_source_map(technical, "## 13. Sources", "technical-report.md", errors)
        require("missing_behavior" in technical, errors, "technical-report.md missing missing_behavior labels")


def check_generic_package(root: Path, errors: list[str]) -> None:
    check_required_files(root, ["README.md", "RESULT.md", "input.json", "run/README.md"], errors)
    input_doc = check_json_file(root / "input.json", errors)
    if not isinstance(input_doc, dict):
        return
    check_declared_artifacts(root, input_doc, errors)
    result_path = root / "RESULT.md"
    if result_path.exists():
        result = read(result_path)
        require(result.startswith("# "), errors, "RESULT.md must start with a top-level heading")
        require("not an investment recommendation" in result or "Analyze → Propose" in result, errors, "RESULT.md missing research/execution boundary")
        for snippet in input_doc.get("required_result_snippets", []):
            require(snippet in result, errors, f"RESULT.md missing required snippet: {snippet!r}")
        if "Source map" in result:
            source_heading = next((line for line in result.splitlines() if "Source map" in line and line.startswith("##")), "## Source map")
            check_source_map(result, source_heading, "RESULT.md", errors)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate a public investment research package.")
    parser.add_argument("package_root", help="Path to package root, e.g. dev/implementation/reproducible-runs/...")
    args = parser.parse_args(argv)

    root = Path(args.package_root).resolve()
    errors: list[str] = []

    require(root.is_dir(), errors, f"package root is not a directory: {root}")
    if root.is_dir():
        if root.name == "apyusd-investment-research-20260604":
            check_apy_package(root, errors)
        else:
            check_generic_package(root, errors)
        check_methodology(root, errors)
        check_local_links(root, errors)

    if errors:
        print("Status: fail")
        print("Errors:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Status: pass")
    print(f"Package: {root}")
    print("Required files/artifacts: pass")
    print("Result sections/snippets: pass")
    print("Source maps: pass")
    print("Local links: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
