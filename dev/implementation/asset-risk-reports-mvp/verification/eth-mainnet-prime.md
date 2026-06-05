# Verification — Hastra PRIME MVP asset risk dossier

Verification date: 2026-06-04 UTC
Verifier: Hermes kanban QA worker
Methodology contract: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/methodology.md`
Report reviewed: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/reports/eth-mainnet-prime.md`

## Approval summary

PASS. The Hastra PRIME dossier is usable under the MVP asset-specific mining pipeline. It pins the supplied Ethereum mainnet scope, includes all nine pipeline sections, cites multiple primary sources, records admin/oracle/redemption/liquidity controls with missing-data behavior, and avoids final-use verdict or asset-selection language.

No blocking remediation item was found.

## Scope check

| Field | Expected | Dossier status |
|---|---|---|
| Display | Hastra PRIME | Pass; title, report inputs, and identity section use Hastra PRIME. |
| Chain | Ethereum mainnet | Pass. |
| `chain_id` | `1` | Pass; report inputs state `chain_id: 1`. |
| Token address | `0x19ebb35279A16207Ec4ba82799CC64715065F7F6` | Pass; report inputs and identity section match exactly. |
| Symbol | `PRIME` | Pass; report inputs and on-chain identity section match. |

## Artifact coverage reviewed

- Methodology: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/methodology.md`
- Synthesized dossier: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/reports/eth-mainnet-prime.md`
- Parent research:
  - `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/eth-mainnet-prime/issuer-backing-security.md`
  - `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/eth-mainnet-prime/transfer-liquidity-oracle-governance.md`
  - `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/hastra-prime/onchain-admin.md`
- Raw on-chain evidence spot-checked:
  - `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/hastra-prime/raw/onchain-admin-snapshot-2026-06-04.json`
  - `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/hastra-prime/raw/feed-verifier-snapshot-2026-06-04.json`

The additional `research/hastra-prime/onchain-admin.md` artifact is outside the `eth-mainnet-prime/` directory named in the task body, but it is explicitly cited by the dossier and by both PRIME parent artifacts. It was therefore included in verification.

## Pipeline-section checklist

| Methodology section | Dossier section | Result | Notes |
|---|---|---|---|
| 1. Identity and token semantics | `## 3. Identity and token semantics` | Pass | Chain, address, name, symbol, decimals, proxy, implementation, token behavior, underlying asset, and transition-stage behavior are recorded. |
| 2. Issuer / protocol and business model | `## 4. Issuer / protocol and business model` | Pass | Issuer/legal entity, mechanism, value-accrual model, access restrictions, and off-chain dependencies are stated with source IDs. |
| 3. Backing, NAV, and exposure map | `## 5. Backing, NAV, and exposure map` | Pass | `nav_model` is classified as `staking-share / issuer NAV / RWA-linked HELOC exposure`; reserve/NAV and exposure caveats are included. |
| 4. Contract admin, multisigs, and sensitive actions | `## 6. Contract admin, multisigs, and sensitive actions` | Pass | Admin roles, Safe threshold, EOA operational powers, sensitive actions, existing-holder impact, execution speed, and recent role/admin events are covered. |
| 5. Audits, formal verification, and incidents | `## 7. Audits, formal verification, and incidents` | Pass | Source verification is separated from third-party audit status; missing deployed-audit scope and formal verification are marked `review_required`. |
| 6. Transferability, redemption, and liquidity | `## 8. Transferability, redemption, and liquidity` | Pass | Transfer freeze mechanics, pause effects, legal eligibility, primary redemption, YieldVault settlement, claim-token absence, and Ethereum liquidity/quote caveats are covered. |
| 7. Oracle and pricing methodology | `## 9. Oracle and pricing methodology` | Pass | FeedVerifier/NAV source, feed ID, staleness, dependencies, market-vs-NAV mismatch, and missing off-chain construction are stated. |
| 8. Governance / change-feed watchlist | `## 10. Governance / change-feed watchlist` | Pass | Implementation slots, feed fields, Safe state, pending Safe tx, role holders, pause/freeze events, terms, liquidity, and reserve/audit publications are listed as watch items. |
| 9. Data quality and missing-data behavior | `## 11. Data quality and missing-data behavior` | Pass | Material fields include `source_class`, freshness, confidence, and `missing_behavior`; highest-impact unknowns also include missing behavior. |

## Acceptance-check results

| Check | Result | Evidence |
|---|---|---|
| All nine pipeline sections present or explicitly not applicable | Pass | Automated heading scan found no missing methodology sections. |
| Chain/address/symbol match supplied scope | Pass | Report inputs and identity section match Ethereum mainnet, `chain_id: 1`, `0x19ebb35279A16207Ec4ba82799CC64715065F7F6`, `PRIME`. |
| At least two primary sources cited where available | Pass | Dossier source list includes 12 `S*` sources, including direct Ethereum RPC/Sourcify, verified source, Hastra terms/site/proof pages, GitHub source, market data, and Safe Transaction Service. |
| Admin roles and sensitive actions checked or unknown | Pass | DEFAULT_ADMIN, UPGRADER, PAUSER, FREEZE_ADMIN, REWARDS_ADMIN, NAV_ORACLE_UPDATER, FeedVerifier roles, Safe threshold, and sensitive actions are listed. Missing off-chain owner/process facts are marked `review_required`. |
| NAV/backing/reserve exposure classified | Pass | NAV model and exposure map cover PRIME, wYLDS/YieldVault, YLDS/Hastra collateral, Figure HELOC operations, NAV feed, and DEX market. |
| Transfer/freeze/redemption/liquidity paths checked or unknown | Pass | PRIME freeze/pause path, YieldVault request/complete redemption path, claim-token absence, Uniswap V3 venue, and liquidity cliffs are covered with `review_required` / `block_automation` where appropriate. |
| Oracle methodology checked or unknown | Pass | FeedVerifier NAV/redemption-rate methodology, feed ID, staleness, dependencies, and oracle miss classes are covered. Exact off-chain NAV construction is marked unknown with `review_required`. |
| Highest-impact unknowns include missing behavior | Pass | Highest-impact unknowns table includes explicit `missing_behavior` for NAV construction, reserve/custody reports, audit scope, eligibility/SLA, Safe/EOA process, frozen-account status, liquidity, and incident-history absence. |
| No final-use verdict / asset-selection language | Pass | Automated scan found no positive selection/usage verdict language in the dossier. Scope-setting phrases only state that the dossier does not rank or decide final use. |
| Gearbox terminology scan | Pass | No bad variants found for Credit Account / Credit Manager, transition-stage assets, non-atomic settlement, timelock, Safe, or RWA-backed debt terminology. Uses `Credit Account`, `transition-stage`, `timelock`, and `Safe` correctly where present. |

## Primary-source spot checks

| Claim family | Spot-check result |
|---|---|
| Token identity and implementation | Raw on-chain snapshot confirms token proxy `0x19ebb35279A16207Ec4ba82799CC64715065F7F6`, implementation `0x90fd843c68db38e2de0618AcBB39341CbA5A5abD`, `name = Hastra PRIME`, `symbol = PRIME`, `decimals = 6`, `asset = yieldVault = 0x6aD038cA6C04e885630851278ca0a856Ad9a66Cc`, `paused = false`. |
| Role/admin state | Raw on-chain snapshot confirms Safe `0x8D358B8aE881F8ea92C3d07783aBCA21727C6309` holds DEFAULT_ADMIN and UPGRADER, EOA `0xA8C3CF6183D49d5D372f8FC149BD2cb5CFC0faCd` holds FREEZE_ADMIN / PAUSER / REWARDS_ADMIN, NAV_ORACLE_UPDATER has no holder, and Safe probe returned threshold `4` with seven owners. |
| FeedVerifier/oracle state | Raw FeedVerifier snapshot confirms proxy `0xdF4ab20fA7752Be52E41e42F1FD667f37964d6a3`, implementation `0xbC6023cb49F8E8cA6cef563d5FD97ba4C6A5D937`, `allowedFeedId = 0x0007c8ed155d952e003b1e15ce7666fea785cfbe216577d578fce3920e997271`, `defaultMaxStaleness = 3600`, `paused = false`, active feed price and timestamp present. |
| Parent-artifact consistency | The dossier's admin/NAV/transfer/redemption/liidity/oracle/governance facts align with the three reviewed parent artifacts. Unknowns from the parent artifacts are preserved rather than collapsed into clean status. |

## Non-blocking observations

- The dossier has more sections than the minimal methodology output because it includes summary, mechanism, highest-impact unknowns, and source list sections. This is acceptable; the nine methodology sections are present.
- The report cites both original sources and parent research artifacts. Material claims are generally tied back to original source IDs in the report body, so the parent artifacts are not the only evidence layer.
- The `Gearbox support/oracle notes` field is explicitly marked not found/unknown with behavior that escalates to `review_required` if a Gearbox integration depends on it. This is acceptable for `intended_use: unknown`.

## Final status

Approved for MVP dossier use. No remediation card is required.
