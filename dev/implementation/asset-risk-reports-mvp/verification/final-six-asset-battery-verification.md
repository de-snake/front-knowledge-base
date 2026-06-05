# Final battery verification — six MVP asset-risk reports

Verification date: 2026-06-04 UTC
Verifier: Hermes operator recovery after final QA worker crashed
Methodology contract: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/methodology.md`
Analyst-readability contract: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/requirements-brief.md`
Battery index reviewed: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/INDEX.md`

## Final decision

PASS. The expanded six-asset research battery satisfies the requested verification checks under the methodology and analyst-readability contracts.

No remediation cards are required for the six base asset dossiers.

This artifact verifies the reports as factual, source-linked dossiers for later analyst and agent reasoning. It does not rank assets, approve portfolio actions, provide a suitability verdict, select tokens, or give execution instructions.

## Artifacts reviewed

- Methodology: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/methodology.md`
- Analyst requirements: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/requirements-brief.md`
- Battery index: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/INDEX.md`
- Report directory: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/reports/`
- Technical report directory: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/technical-reports/`
- Asset-level verification directory: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/verification/`

## Scope check

| Asset | chain_id | Token address | Symbol | Analyst report | Technical report | Asset verification | Result |
|---|---:|---|---|---|---|---|---|
| Saturn sUSDat | `1` | `0xd166337499e176bbc38a1fbd113ab144e5bd2df7` | `sUSDat` | `reports/eth-mainnet-susdat.md` | `technical-reports/eth-mainnet-susdat.md` | `verification/eth-mainnet-susdat.md` | PASS |
| apyx apyUSD | `1` | `0x38eeb52f0771140d10c4e9a9a72349a329fe8a6a` | `apyUSD` | `reports/eth-mainnet-apyusd.md` | `technical-reports/eth-mainnet-apyusd.md` | `verification/eth-mainnet-apyusd.md` | PASS |
| Hastra PRIME | `1` | `0x19ebb35279A16207Ec4ba82799CC64715065F7F6` | `PRIME` | `reports/eth-mainnet-prime.md` | `technical-reports/eth-mainnet-prime.md` | `verification/eth-mainnet-prime.md` | PASS |
| Centrifuge deSPXA | `8453` | `0x9c5C365e764829876243d0b289733B9D2b729685` | `deSPXA` | `reports/base-despxa.md` | `technical-reports/base-despxa.md` | `verification/base-despxa.md` | PASS |
| Saturn USDat | `1` | `0x23238F20B894f29041f48d88Ee91131c395aAA71` | `USDat` | `reports/eth-mainnet-usdat.md` | `technical-reports/eth-mainnet-usdat.md` | `verification/eth-mainnet-usdat.md` | PASS |
| apyx apxUSD | `1` | `0x98A878b1Cd98131B271883B390f68D2c90674665` | `apxUSD` | `reports/eth-mainnet-apxusd.md` | `technical-reports/eth-mainnet-apxusd.md` | `verification/eth-mainnet-apxusd.md` | PASS |

Findings:

- `INDEX.md` represents exactly the six supplied assets above.
- `reports/` contains exactly six scoped report files.
- `technical-reports/` contains exactly six scoped technical report files.
- The six asset-level verification files above are PASS artifacts.
- Supporting files such as `analyst-readability-verification.md`, the older four-asset `final-battery-verification.md`, and this final six-asset verifier are not counted as additional scoped assets.
- Underlying tokens, vaults, queues, receipts, oracles, funds, managers, Safe addresses, role holders, liquidity pools, and backing instruments appear only as explanatory dependencies for the six supplied assets.

## Methodology checklist

| Check | Result | Evidence |
|---|---|---|
| Exactly the six user-supplied assets are represented, no extras | PASS | `INDEX.md` lists only the six supplied assets with their chain IDs, token addresses, symbols, issuer hints, and links. Report and technical-report directories each contain exactly the six expected markdown files. |
| Every report passed asset-level verification or has remediation listed | PASS | All six asset-level verification artifacts are PASS/approved. No remediation item blocks the final battery card. |
| Every technical report follows the nine-section pipeline | PASS | Each technical report contains the required methodology sections: identity/token semantics; issuer/business model; backing/NAV; admin/sensitive actions; audits/incidents; transfer/redemption/liquidity; oracle/pricing; governance/change-feed; data quality/missing-data behavior. Each also includes the wrapper sections for summary, mechanism, highest-impact unknowns, and sources. |
| Every analyst report is readable and table-free | PASS | All six analyst reports have no code fences and no Markdown tables. They use prose and bullets for analyst-readable risk notes. |
| Analyst source maps have URL/local evidence links | PASS | Each analyst report source map contains actual URLs or local evidence links for source IDs. |
| Source lists include classes, access dates, and confidence | PASS | Report and technical-source sections include source class, 2026-06-04 access dates, and confidence values or explicit confidence language. |
| Unknowns include `missing_behavior` or analyst-facing equivalent | PASS | All six reports and technical dossiers preserve `review_required`, `block_automation`, `cannot_rank_cleanly`, `continue`, or direct analyst equivalents for unresolved material fields. |
| No recommendation / suitability / ranking / token-selection / execution instruction language | PASS | Automated scan found no buy/sell/recommend/ranking/action instruction hits beyond explicit negative disclaimers and factual route/exit wording. |
| Terminology scan is clean | PASS | Terms including `Credit Account`, `Credit Manager`, `transition-stage assets`, `non-atomic settlement`, `timelock`, and `Safe` are used only in supported contextual or negative-disclaimer ways. |

## Per-asset verification notes

### Saturn sUSDat

- Scope: Ethereum mainnet `chain_id: 1`, `0xd166337499e176bbc38a1fbd113ab144e5bd2df7`, `sUSDat`.
- Asset-level QA: PASS in `verification/eth-mainnet-susdat.md`.
- Technical coverage: PASS; all nine methodology areas present.
- Analyst readability: PASS; prose/bullets only, no code fences, no Markdown tables.
- Source metadata: PASS; onchain, issuer-docs, local research, market-data, audit/transparency, access date, and confidence evidence are present.
- Missing behavior: PASS; STRC/NAV proof, audit-scope mapping, pending admin transition, USDat restrictions, queue/slippage, vesting mismatch, and bounded incident history are carried with `missing_behavior` labels.
- Terminology/language: PASS; no final-use call or unsupported Gearbox terminology claim.

### apyx apyUSD

- Scope: Ethereum mainnet `chain_id: 1`, `0x38eeb52f0771140d10c4e9a9a72349a329fe8a6a`, `apyUSD`.
- Asset-level QA: PASS in `verification/eth-mainnet-apyusd.md`.
- Technical coverage: PASS; all nine methodology areas present.
- Analyst readability: PASS; prose/bullets only, no code fences, no Markdown tables.
- Source metadata: PASS; onchain, issuer-docs, legal-terms, audit, governance, market-data, access date, and confidence evidence are present.
- Missing behavior: PASS; reserve/custody attestations, audit mapping, AccessManager/Safe state, deny-list state, Unlock Receipt, primary settlement, market history, oracle methodology, Gearbox support, and user eligibility are carried with `missing_behavior` labels.
- Terminology/language: PASS; negative final-use disclaimers are not recommendations.

### Hastra PRIME

- Scope: Ethereum mainnet `chain_id: 1`, `0x19ebb35279A16207Ec4ba82799CC64715065F7F6`, `PRIME`.
- Asset-level QA: PASS in `verification/eth-mainnet-prime.md`.
- Technical coverage: PASS; all nine methodology areas present.
- Analyst readability: PASS; prose/bullets only, no code fences, no Markdown tables.
- Source metadata: PASS; onchain/RPC/Sourcify, legal terms, issuer docs/source, governance/onchain, market-data, access date, freshness, and confidence evidence are present.
- Missing behavior: PASS; NAV-feed construction, wYLDS/YLDS reserve/custody reports, audit scope, eligibility/SLA, Safe/EOA process, frozen-account checks, DEX depth, and incident-history bounds are carried with `missing_behavior` labels.
- Terminology/language: PASS; liquidity wording is factual route-depth context, not an instruction.

### Centrifuge deSPXA

- Scope: Base `chain_id: 8453`, `0x9c5C365e764829876243d0b289733B9D2b729685`, `deSPXA`.
- Asset-level QA: PASS in `verification/base-despxa.md`.
- Technical coverage: PASS; all nine methodology areas present.
- Analyst readability: PASS; prose/bullets only, no code fences, no Markdown tables.
- Source metadata: PASS; onchain, issuer-docs, governance, market-data / risk-assessment, mixed source classes, access date, and confidence evidence are present.
- Missing behavior: PASS; Root ward identity, holder eligibility/member state, legal/fund terms, audit/formal-verification scope, Chronicle feed details, live depth, and incident-history bounds are carried with `missing_behavior` labels.
- Terminology/language: PASS; no final-use call or unsupported Gearbox terminology claim.

### Saturn USDat

- Scope: Ethereum mainnet `chain_id: 1`, `0x23238F20B894f29041f48d88Ee91131c395aAA71`, `USDat`.
- Asset-level QA: PASS in `verification/eth-mainnet-usdat.md`.
- Technical coverage: PASS; all nine methodology areas present.
- Analyst readability: PASS; prose/bullets only, no code fences, no Markdown tables.
- Source metadata: PASS; onchain, issuer-docs, source extracts, market-data, audit/transparency, access date, and confidence evidence are present.
- Missing behavior: PASS; M0 `$M` reserve/custody/legal evidence, onboarding/whitelist/freeze state, audit-scope mapping, admin-timelock transition, oracle methodology, route quotes, and incident-history bounds are carried with `missing_behavior` labels.
- Terminology/language: PASS; no final-use call or unsupported Gearbox terminology claim.

### apyx apxUSD

- Scope: Ethereum mainnet `chain_id: 1`, `0x98A878b1Cd98131B271883B390f68D2c90674665`, `apxUSD`.
- Asset-level QA: PASS in `verification/eth-mainnet-apxusd.md`.
- Technical coverage: PASS; all nine methodology areas present.
- Analyst readability: PASS; prose/bullets only, no code fences, no Markdown tables.
- Source metadata: PASS; onchain/RPC/source, issuer-docs, governance/Safe API, audit, contract README, market-data, access date, and confidence evidence are present.
- Missing behavior: PASS; reserve reconciliation, primary redemption eligibility, audit/FV mapping, AccessManager/Safe history, modules/guards, deny-list state, oracle methodology, and live route depth are carried with `missing_behavior` labels.
- Terminology/language: PASS; no final-use call or unsupported Gearbox terminology claim.

## Terminology scan

The final scan covered `INDEX.md`, the six analyst reports, six technical reports, and six asset-level verification artifacts.

| Term | Count | QA note |
|---|---:|---|
| `Credit Account` | 33 | Used as conditional collateral/oracle context or in live-use caveats; no unsupported current Gearbox support claim. |
| `Credit Manager` | 9 | Used in methodology/Gearbox-scope context; no unsupported Credit Manager integration claim. |
| `transition-stage assets` | 6 | Used to describe receipt/queue or methodology state, not to introduce extra scoped assets. |
| `non-atomic settlement` | 8 | Used as a settlement-risk descriptor for queues/receipts, not as unsupported execution guidance. |
| `timelock` | 105 | Supported by role/timelock evidence, pending-operation caveats, or governance-state checks. |
| `Safe` | 268 | Supported by Safe/Safe-like holder, threshold, pending transaction, or no-Safe-found evidence and caveats. |

## Automated checks run

A local verification script checked:

- report files: 6/6 expected;
- technical report files: 6/6 expected;
- `INDEX.md` scope entries: 6/6 expected;
- asset-level verification PASS artifacts: 6/6 expected;
- technical report nine-section coverage: PASS for all six;
- analyst readability: no code fences and no Markdown tables for all six;
- source map links and metadata: PASS for all six;
- highest-impact unknown / `missing_behavior`: PASS for all six;
- recommendation / final-use / ranking language scan: PASS;
- terminology scan: PASS.

Result: `FINAL_SIX_BATTERY_CHECK_PASS`.

Workspace checks also passed after writing this artifact:

- `python3 scripts/workspace_sync.py --check`
- `python3 scripts/workspace_policy_check.py --all`

## Final verifier decision

The expanded six-asset battery is approved for MVP use as a factual asset-risk research substrate. No remediation tasks are needed before completing the final six-asset verifier Kanban card.

Live use remains subject to fresh Preview checks for route quotes, holder eligibility, restriction state, redemption/queue/receipt state, oracle freshness, backing/reserve evidence, and current admin/governance state.
