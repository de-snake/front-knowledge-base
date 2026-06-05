# Verification — Pendle PT apyUSD — 27 Aug 2026 PT market QA

Verification date: 2026-06-04 UTC
Verifier: Hermes operator recovery after QA worker crash
Task: `t_8176ae89`

## Final decision

PASS. The Pendle PT technical dossier and analyst-readable report satisfy the QA contract for `Pendle PT apyUSD — 27 Aug 2026`.

No remediation card is required for this PT analysis.

This verification approves the artifacts as factual source-linked analysis. It does not decide final use, collateral acceptance, token selection, or live execution.

## Artifacts reviewed

- `reports/eth-mainnet-apyusd.md`
- `technical-reports/eth-mainnet-apyusd.md`
- `verification/eth-mainnet-apyusd.md`
- `technical-reports/pendle-pt-eth-mainnet-apyusd-2026-08-27.md`
- `reports/pendle-pt-eth-mainnet-apyusd-2026-08-27.md`

## Scope check

- Protocol: Pendle.
- Chain: Ethereum mainnet.
- `chain_id`: `1`.
- Underlying: `apyUSD` at `0x38eeb52f0771140d10c4e9a9a72349a329fe8a6a`.
- Market: `0x30bb9ee8dc6aab322dc3a0d36063cbf06a9e5952`.
- PT: `0xee5c7cda577484b70b65c21235ecbd302bb290e2`.
- SY: `0x04f8dca7bccd8997ac57ca6fef7c705e17d6bcb6`.
- YT: `0x67553fb2ab2a411029387e1c53c0a3e55f8d10c9`.
- Maturity: `2026-08-27`.
- Supplied days-to-maturity label: `83 days`.

The market identity is sourced from Pendle active-market and market-detail API snapshots in `research/pendle-pt-eth-mainnet-apyusd-2026-08-27/raw/`. The technical report explicitly records same-underlying candidate context and confirms the exact supplied underlying/maturity match.

## QA checklist

| Check | Result |
|---|---|
| source files exist | PASS |
| scope chain underlying maturity days | PASS |
| exact market pt sy yt addresses | PASS |
| market correspondence sourced | PASS |
| inherited risk carried | PASS |
| incremental pt analysis | PASS |
| analyst no code fences | PASS |
| analyst no markdown tables | PASS |
| analyst source bullets links metadata | PASS |
| technical sections present | PASS |
| analyst sections present | PASS |
| technical source classes access confidence | PASS |
| missing behavior and unknowns | PASS |
| no forbidden language | PASS |
| gearbox terms scan clean | PASS |

## Coverage notes

- Inherited risk: PASS. The report carries the underlying `apyUSD` issuer/backing/admin/transfer/oracle restrictions forward from the upstream analyst report, technical dossier, and verification artifact.
- Incremental PT risk: PASS. The report separately covers fixed-maturity PT economics, discount and implied APY assumptions, maturity/redemption mechanics, pre-maturity Pendle AMM liquidity, pricing/oracle/valuation dependencies, Pendle contract dependencies, and adverse scenarios.
- Analyst readability: PASS. The analyst note uses prose and bullets, has no code fences, has no Markdown tables, and its source-map bullets include URL or local evidence paths plus source class, access date, and confidence.
- Technical traceability: PASS. The technical dossier includes source classes, access dates, confidence, `missing_behavior`, highest-impact unknowns, and local raw evidence paths.

## Gearbox terminology scan

| Term | Count | QA note |
|---|---:|---|
| `Credit Account` | 2 | clean / contextual use |
| `Credit Manager` | 0 | clean / contextual use |
| `transition-stage assets` | 0 | clean / contextual use |
| `non-atomic settlement` | 0 | clean / contextual use |
| `timelock` | 0 | clean / contextual use |
| `Safe` | 0 | clean / contextual use |

Forbidden variants scanned and not found: lowercase `credit account`, lowercase `credit manager`, `time-lock`, `time lock`, `slow settlement`, `delayed settlement`, `debt-backed RWA`, and `debt-based RWA`.

## Retained caveats

The following caveats are intentionally retained and are not QA failures:

- Live size-specific PT/SY route depth and slippage were not computed; the artifacts correctly mark live automation as blocked without a fresh Preview.
- A Gearbox-compatible PT oracle/feed was not verified; the artifacts correctly require human review before valuation or integration use.
- Pendle market/PT/SY/YT role and upgrade state were not fully audited; the artifacts include Etherscan pointers and preserve `review_required`.
- Underlying issuer/backing/restriction state must be refreshed for live use according to the upstream dossier.

## Deterministic check result

`PENDLE_PT_QA_CHECK_PASS::pendle-pt-eth-mainnet-apyusd-2026-08-27`

## Final verifier decision

The PT market analysis artifacts are approved for the MVP research battery. Downstream synthesis can use them as source-linked factual inputs while preserving the live-use caveats above.
