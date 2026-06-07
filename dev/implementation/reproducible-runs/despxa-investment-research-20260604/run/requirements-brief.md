# Requirements brief — investment analyst readability rewrite

Date: 2026-06-04 UTC

## Source of truth

The source facts are the existing four technical dossiers and their parent research artifacts under `research/`.

Before rewriting, the technical dossiers were copied to `technical-reports/` so detailed on-chain evidence, addresses, role names, and method-level notes remain available without dominating the analyst-facing reports.

## Target audience

Investment analyst evaluating asset risk, liquidity, backing, governance/control, and operational implications.

Assumed reader knowledge:

- understands NAV, liquidity, custody, redemption, issuer risk, governance risk, and market stress;
- may not be fluent in Solidity, ERC standards, proxy patterns, role IDs, or contract method names;
- needs to know why a detail changes the risk assessment, not how to reproduce every technical call.

## Requested change

Make the reports less technical and more readable:

- reduce code terms, raw contract mechanics, addresses, role IDs, and method names in the main body;
- explain what the asset is in plain language;
- put risk implications before technical evidence;
- convert `missing_behavior` labels into analyst-facing decision implications;
- keep source links and confidence notes, but make them secondary;
- preserve technical evidence in appendices / technical-reports for auditability.

## New report shape

Each analyst-facing report should use this structure:

1. Executive view
2. What the token represents
3. Main risk implications
4. Backing and NAV quality
5. Liquidity and exit risk
6. Controls, governance, and legal restrictions
7. Pricing / oracle risk in plain language
8. What must be checked before live use
9. Evidence quality
10. Source map
11. Technical appendix pointer

## Style rules

- No code fences in analyst-facing reports.
- Avoid method names and role IDs unless there is no plain-language equivalent.
- Use short paragraphs and bullets.
- Prefer phrases like “can block redemptions” over `direct_redemption_block`.
- Prefer “requires human review” and “do not automate execution” over raw `review_required` / `block_automation` labels.
- Explain why each unknown matters economically.
- Do not give asset-selection, position-sizing, buy/sell/hold, collateral-acceptance, or suitability recommendations.

## Verification criteria

- Four reports still exist at `reports/*.md`.
- Four original technical reports exist at `technical-reports/*.md`.
- Analyst reports contain no code fences.
- Analyst reports contain plain-language sections for risk implications, liquidity/exit, controls/governance, pricing/oracle, checks before live use, evidence quality, and source map.
- Analyst reports retain the exact chain/token identity once near the top.
- Analyst reports retain source IDs and links/source pointers.
- Terminology checks pass for Gearbox terms: Credit Account, Credit Manager, transition-stage assets, non-atomic settlement, timelock, Safe.
- Workspace sync and policy checks pass or any unrelated pre-existing failure is reported with evidence.
