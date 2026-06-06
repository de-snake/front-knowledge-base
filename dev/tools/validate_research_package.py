#!/usr/bin/env python3
"""Lightweight integrity check for methodology-guided research packages.

This intentionally does not judge investment quality. It verifies that the public
package has the expected files, source maps, local links, and missing-data markers
needed for a human reviewer to reproduce/check the dossier.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED_FILES = [
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
]

RESULT_SECTIONS = [
    "# apyx apyUSD — investment analyst risk note",
    "## 1. Executive view",
    "## 2. What the token represents",
    "## 3. Main risk implications",
    "## 4. Backing and NAV quality",
    "## 5. Liquidity and exit risk",
    "## 6. Controls, governance, and legal restrictions",
    "## 7. Pricing / oracle risk in plain language",
    "## 8. What must be checked before live use",
    "## 9. Evidence quality",
    "## 10. Source map",
    "## 11. Technical appendix pointer",
]

TECHNICAL_SECTIONS = [
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

REQUIRED_RESULT_SNIPPETS = [
    "0x38EEb52F0771140d10c4E9A9a72349A329Fe8a6A",
    "not an asset-selection recommendation",
    "not an investment recommendation",
    "review_required",
    "block_automation",
    "run/tokens/eth-mainnet-apyusd/technical-report.md",
]

REQUIRED_METHODOLOGY_SNIPPETS = [
    "## Source priority",
    "## Asset-specific pipeline",
    "### 1. Identity and token semantics",
    "### 9. Data quality and missing-data behavior",
    "## Acceptance criteria",
]

LOCAL_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
SOURCE_ID_RE = re.compile(r"\[S(\d+)\]")


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


def check_required_files(root: Path, errors: list[str]) -> None:
    for name in REQUIRED_FILES:
        require((root / name).is_file(), errors, f"missing required file: {name}")


def check_json(root: Path, errors: list[str]) -> None:
    for name in [
        "input.json",
        "run/tokens/eth-mainnet-apyusd/research/raw/onchain-admin-snapshot-2026-06-04.json",
        "run/tokens/eth-mainnet-apyusd/research/raw/onchain-market-snapshot-2026-06-04.json",
    ]:
        path = root / name
        if not path.exists():
            continue
        try:
            json.loads(read(path))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON {name}: {exc}")


def check_sections(text: str, sections: list[str], label: str, errors: list[str]) -> None:
    last = -1
    for section in sections:
        idx = text.find(section)
        require(idx != -1, errors, f"{label}: missing section {section!r}")
        if idx != -1:
            require(idx > last, errors, f"{label}: section out of order {section!r}")
            last = idx


def check_source_map(text: str, heading: str, label: str, errors: list[str]) -> None:
    used = sorted({int(match) for match in SOURCE_ID_RE.findall(text)})
    if not used:
        errors.append(f"{label}: no bracketed source IDs found")
        return
    source_start = text.find(heading)
    require(source_start != -1, errors, f"{label}: missing source-map heading {heading!r}")
    source_text = text[source_start:] if source_start != -1 else ""
    for source_id in used:
        require(
            re.search(rf"\bS{source_id}\b", source_text) is not None,
            errors,
            f"{label}: source ID S{source_id} is used but not resolved after {heading}",
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


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate a public investment research package.")
    parser.add_argument("package_root", help="Path to package root, e.g. dev/implementation/reproducible-runs/...")
    args = parser.parse_args(argv)

    root = Path(args.package_root).resolve()
    errors: list[str] = []

    require(root.is_dir(), errors, f"package root is not a directory: {root}")
    if not root.is_dir():
        for error in errors:
            print(f"- {error}")
        print("Status: fail")
        return 1

    check_required_files(root, errors)
    check_json(root, errors)

    result_path = root / "RESULT.md"
    technical_path = root / "run/tokens/eth-mainnet-apyusd/technical-report.md"
    methodology_path = root / "run/methodology.md"

    if result_path.exists():
        result = read(result_path)
        check_sections(result, RESULT_SECTIONS, "RESULT.md", errors)
        for snippet in REQUIRED_RESULT_SNIPPETS:
            require(snippet in result, errors, f"RESULT.md missing required snippet: {snippet!r}")
        check_source_map(result, "## 10. Source map", "RESULT.md", errors)

    if technical_path.exists():
        technical = read(technical_path)
        check_sections(technical, TECHNICAL_SECTIONS, "technical-report.md", errors)
        check_source_map(technical, "## 13. Sources", "technical-report.md", errors)
        require("missing_behavior" in technical, errors, "technical-report.md missing missing_behavior labels")

    if methodology_path.exists():
        methodology = read(methodology_path)
        for snippet in REQUIRED_METHODOLOGY_SNIPPETS:
            require(snippet in methodology, errors, f"run/methodology.md missing required snippet: {snippet!r}")

    check_local_links(root, errors)

    if errors:
        print("Status: fail")
        print("Errors:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Status: pass")
    print(f"Package: {root}")
    print(f"Required files: {len(REQUIRED_FILES)}/{len(REQUIRED_FILES)}")
    print("Result sections: pass")
    print("Technical sections: pass")
    print("Source maps: pass")
    print("Local links: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
