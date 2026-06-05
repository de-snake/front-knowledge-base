# Verification — Pendle PT apxUSD — 05 Nov 2026 PT market QA

Verification date: 2026-06-04 UTC
Verifier: Hermes operator recovery after QA worker crash
Task: `t_0e9401e2`

## Final decision

PASS. The Pendle PT technical dossier and analyst-readable report satisfy the QA contract for `Pendle PT apxUSD — 05 Nov 2026`.

No remediation card is required for this PT analysis.

This verification approves the artifacts as factual source-linked analysis. It does not decide final use, collateral acceptance, token selection, or live execution.

## Artifacts reviewed

- `reports/eth-mainnet-apxusd.md`
- `technical-reports/eth-mainnet-apxusd.md`
- `verification/eth-mainnet-apxusd.md`
- `technical-reports/pendle-pt-eth-mainnet-apxusd-2026-11-05.md`
- `reports/pendle-pt-eth-mainnet-apxusd-2026-11-05.md`

## Scope check

- Protocol: Pendle.
- Chain: Ethereum mainnet.
- `chain_id`: `1`.
- Underlying: `apxUSD` at `0x98a878b1cd98131b271883b390f68d2c90674665`.
- Market: `0xaf0349fb9b1ba07d34381870c59b560b31412660`.
- PT: `0xaf687b5ecb525ccea96115088999b4ed80c388b6`.
- SY: `0x4f116ee5bcd227d1a1c4f57918d694a4abe7b3fc`.
- YT: `0x7fbc01c63b0ac372ec75907f3a1d8adc8cf28e1f`.
- Maturity: `2026-11-05`.
- Supplied days-to-maturity label: `153 days`.

The market identity is sourced from Pendle active-market and market-detail API snapshots in `research/pendle-pt-eth-mainnet-apxusd-2026-11-05/raw/`. The technical report explicitly records same-underlying candidate context and confirms the exact supplied underlying/maturity match.

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

- Inherited risk: PASS. The report carries the underlying `apxUSD` issuer/backing/admin/transfer/oracle restrictions forward from the upstream analyst report, technical dossier, and verification artifact.
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

`PENDLE_PT_QA_CHECK_PASS::pendle-pt-eth-mainnet-apxusd-2026-11-05`

## Final verifier decision

The PT market analysis artifacts are approved for the MVP research battery. Downstream synthesis can use them as source-linked factual inputs while preserving the live-use caveats above.
