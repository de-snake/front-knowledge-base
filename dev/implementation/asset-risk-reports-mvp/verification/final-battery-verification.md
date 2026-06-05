# Final battery verification — four MVP asset-risk reports

Verification date: 2026-06-04 UTC
Verifier: Hermes kanban worker
Methodology contract: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/methodology.md`

## Final decision

PASS. The final four-asset research battery satisfies the requested verification checks under `methodology.md`.

No remediation cards are required.

This artifact verifies the reports as factual source-linked dossiers for later agent reasoning. It does not rank assets, approve portfolio actions, or decide final use for a user.

## Artifacts reviewed

- Methodology: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/methodology.md`
- Battery index: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/INDEX.md`
- Reports:
  - `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/reports/eth-mainnet-susdat.md`
  - `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/reports/eth-mainnet-apyusd.md`
  - `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/reports/eth-mainnet-prime.md`
  - `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/reports/base-despxa.md`
- Asset-level verification files:
  - `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/verification/eth-mainnet-susdat.md`
  - `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/verification/eth-mainnet-apyusd.md`
  - `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/verification/eth-mainnet-prime.md`
  - `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/verification/base-despxa.md`

Note: this final verification file is the fifth file in `verification/` after creation; the four asset-level verification files above were the scoped verification inputs.

## Scope check

| Asset | chain_id | Token address | Symbol | Report | Asset-level verification | Result |
|---|---:|---|---|---|---|---|
| Saturn sUSDat | `1` | `0xD166337499E176bbC38a1FBd113Ab144e5bd2Df7` | `sUSDat` | `reports/eth-mainnet-susdat.md` | `verification/eth-mainnet-susdat.md` | PASS |
| apyx apyUSD | `1` | `0x38EEb52F0771140d10c4E9A9a72349A329Fe8a6A` | `apyUSD` | `reports/eth-mainnet-apyusd.md` | `verification/eth-mainnet-apyusd.md` | PASS |
| Hastra PRIME | `1` | `0x19ebb35279A16207Ec4ba82799CC64715065F7F6` | `PRIME` | `reports/eth-mainnet-prime.md` | `verification/eth-mainnet-prime.md` | PASS |
| Centrifuge deSPXA | `8453` | `0x9c5C365e764829876243d0b289733B9D2b729685` | `deSPXA` | `reports/base-despxa.md` | `verification/base-despxa.md` | PASS |

Findings:

- The index contains exactly the four supplied token addresses above.
- The report directory contains exactly the four report files above.
- The scoped asset-level verification inputs contain exactly the four verification files above.
- Underlying tokens, vaults, queues, oracles, Safe addresses, role holders, pools, and backing instruments appear only as explanatory dependencies for the four supplied assets, not as additional scoped assets.

## Methodology checklist

| Check | Result | Evidence |
|---|---|---|
| Exactly the four user-supplied assets are represented, no extras | PASS | `INDEX.md` lists only sUSDat, apyUSD, PRIME, and deSPXA with their supplied chain IDs and token addresses; `reports/` has exactly four markdown reports matching those assets. |
| Every report passed asset-level verification or has explicit remediation listed | PASS | All four asset-level verification artifacts are PASS/approved and list no blocking remediation. |
| Every report follows the nine-section pipeline | PASS | Each report contains the nine methodology sections: identity/token semantics; issuer/business model; backing/NAV; admin/sensitive actions; audits/incidents; transfer/redemption/liquidity; oracle/pricing; governance/change-feed; data quality/missing-data behavior. The reports also include the required summary, mechanism, highest-impact unknowns, and source list wrapper sections. |
| Source lists include URLs/classes/access dates/confidence | PASS | Each report has a `Sources` table with URL/local evidence, `source_class`, accessed date, and confidence. Counts reviewed: sUSDat 17 source rows, apyUSD 17, PRIME 15, deSPXA 17. |
| Unknowns include `missing_behavior` | PASS | Each report's highest-impact unknowns explicitly include `missing_behavior` labels such as `continue`, `cannot_rank_cleanly`, `review_required`, and `block_automation`. |
| Recommendation / final-use language is absent | PASS | Automated and manual scans found only negative disclaimers and factual liquidity table labels, not a buy/sell/hold call, asset-selection instruction, clean-collateral conclusion, or final-use decision. |
| Terminology scan is clean | PASS | No bad variants were found for `Credit Account`, `Credit Manager`, transition-stage assets, non-atomic settlement, timelock, Safe, or related Gearbox terminology across `INDEX.md`, the reports, and the four asset-level verification files. |

## Per-asset verification notes

### Saturn sUSDat

- Scope: Ethereum mainnet `chain_id: 1`, `0xD166337499E176bbC38a1FBd113Ab144e5bd2Df7`, `sUSDat`.
- Asset-level QA: PASS in `verification/eth-mainnet-susdat.md`.
- Pipeline coverage: PASS; report sections 3-11 map to the nine methodology sections.
- Source metadata: PASS; source table has onchain, issuer_docs, mixed issuer/onchain/audit, mixed onchain/issuer/market data, market_data, accessed dates, and confidence values.
- Missing behavior: PASS; highest-impact unknowns cover STRC/NAV proof, audit-scope matching, pending admin transition, USDat legal/freeze/whitelist policy, queue/slippage, vesting mismatch, and bounded incident search with explicit `missing_behavior` labels.
- Language / terminology: PASS; no final-use call or bad Gearbox terminology variant found.

### apyx apyUSD

- Scope: Ethereum mainnet `chain_id: 1`, `0x38EEb52F0771140d10c4E9A9a72349A329Fe8a6A`, `apyUSD`.
- Asset-level QA: PASS in `verification/eth-mainnet-apyusd.md`.
- Pipeline coverage: PASS; report sections 3-11 map to the nine methodology sections, with additional subsection detail for redemption and liquidity.
- Source metadata: PASS; source table has onchain, issuer_docs, legal_terms, audit, governance, market_data, accessed dates, and confidence values.
- Missing behavior: PASS; highest-impact unknowns cover reserve/custody attestations, audit mapping, AccessManager/Safe state, deny-list state, Unlock Receipt, primary settlement, market history, oracle methodology, Gearbox support, and user eligibility with explicit `missing_behavior` labels.
- Language / terminology: PASS; the only final-use language hit is the explicit negative disclaimer in the header.

### Hastra PRIME

- Scope: Ethereum mainnet `chain_id: 1`, `0x19ebb35279A16207Ec4ba82799CC64715065F7F6`, `PRIME`.
- Asset-level QA: PASS in `verification/eth-mainnet-prime.md`.
- Pipeline coverage: PASS; report sections 3-11 map to the nine methodology sections.
- Source metadata: PASS; source table has direct onchain/RPC/Sourcify, legal_terms, issuer_docs/source, market_data, governance/onchain, accessed dates, freshness notes, and confidence values.
- Missing behavior: PASS; highest-impact unknowns cover feed/NAV construction, reserve/custody reports, audit scope, eligibility/SLA, Safe/EOA process, frozen-account checks, DEX liquidity, and bounded incident search with explicit `missing_behavior` labels.
- Language / terminology: PASS; the `Sell size` phrase appears only as a factual quote-table column for exit-depth analysis, not as an action recommendation.

### Centrifuge deSPXA

- Scope: Base `chain_id: 8453`, `0x9c5C365e764829876243d0b289733B9D2b729685`, `deSPXA`.
- Asset-level QA: PASS in `verification/base-despxa.md`.
- Pipeline coverage: PASS; report sections 3-11 map to the nine methodology sections.
- Source metadata: PASS; source table has onchain, issuer_docs, governance, market_data/risk_assessment, mixed onchain/issuer/market data, accessed dates, and confidence values.
- Missing behavior: PASS; highest-impact unknowns cover Root ward identity, holder eligibility/member state, legal/fund terms, audit/formal-verification scope, Chronicle feed details, live executable depth, and bounded incident search with explicit `missing_behavior` labels.
- Language / terminology: PASS; no final-use call or bad Gearbox terminology variant found.

## Automated checks run

```text
python3 verification script over methodology/INDEX/reports/verification
- report files: 4/4 expected
- asset-level verification files: 4/4 expected
- INDEX supplied addresses: 4/4 expected
- nine-section report coverage: PASS for all reports
- source metadata tables: PASS for all reports
- highest-impact unknown `missing_behavior`: PASS for all reports
- recommendation/final-use language scan: PASS after manual review of negative disclaimers and liquidity-table labels
- terminology scan: PASS
```

The strict first-pass script produced four false positives: two data-quality tables used bracketed citation metadata rather than literal `source_class` column labels, and two verification files contained negative phrases such as “no exact remediation item should block.” Manual review confirmed these are not methodology failures.

## Final verifier decision

The battery is approved for MVP use as a factual asset-risk research substrate. No remediation tasks are needed before completing this Kanban card.
