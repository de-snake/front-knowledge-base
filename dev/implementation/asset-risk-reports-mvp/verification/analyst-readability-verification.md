# Analyst readability verification — four-asset battery

Verification date: 2026-06-04 UTC
Audience target: investment analyst

## Result

PASS.

The four asset-risk reports were rewritten from technical dossiers into analyst-readable risk notes. The original technical dossiers were preserved in `technical-reports/` for auditability.

## Files reviewed

Main analyst reports:

- `reports/eth-mainnet-susdat.md`
- `reports/eth-mainnet-apyusd.md`
- `reports/eth-mainnet-prime.md`
- `reports/base-despxa.md`

Technical originals preserved:

- `technical-reports/eth-mainnet-susdat.md`
- `technical-reports/eth-mainnet-apyusd.md`
- `technical-reports/eth-mainnet-prime.md`
- `technical-reports/base-despxa.md`

Supporting files:

- `INDEX.md`
- `requirements-brief.md`

## Readability checks

Passed:

- Each report starts with an executive view and plain-language description of what the token represents.
- Each report leads with investment risk implications rather than contract mechanics.
- Each report covers backing / NAV quality, liquidity and exit risk, controls and legal restrictions, pricing / oracle risk, and checks required before live use.
- Each report has a source map with actual clickable URL or local evidence links for every source ID.
- Each report has a technical appendix pointer.
- No analyst-facing report contains code fences.
- No analyst-facing report uses Markdown tables in the body.
- Raw method names, role IDs, proxy details, and low-level implementation details were reduced or moved behind the technical appendix pointer.
- `missing_behavior` labels were translated into analyst-facing language: human review required, cannot cleanly rank, or do not automate execution.
- Exact chain and token identity remain near the top of each report.
- The rewritten index explains the cross-asset risk themes and links both analyst reports and technical originals.

## Automated checks run

- Custom readability / structure script over `reports/*.md`: PASS
  - code fences: 0 in all four reports
  - Markdown table rows: 0 in all four reports
  - required analyst sections present in all four reports
  - every source-map bullet contains at least one clickable URL or local evidence link
  - `technical-reports/` contains four preserved originals
- Gearbox terminology scan: PASS
  - mandatory Credit Account / Credit Manager capitalization checked
  - prohibited hyphenated or camelCase Credit Account variants checked
  - prohibited alternatives to non-atomic settlement checked
  - prohibited timelock spelling variants checked
  - Gearbox app casing checked
  - prohibited RWA-backed debt wording variants checked
- `git diff --check` on asset-risk directory: PASS
- `python3 scripts/workspace_sync.py --check`: PASS
- `python3 scripts/workspace_policy_check.py --all`: PASS

## Remaining caveat

The prior asset-level verification files still verify the source-backed technical dossiers. The analyst-readable reports are a presentation rewrite, not new research. If the asset facts are refreshed later, both the analyst reports and technical reports should be regenerated from the new source evidence.
