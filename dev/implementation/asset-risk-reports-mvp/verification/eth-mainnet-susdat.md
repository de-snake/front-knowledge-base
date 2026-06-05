# Verification — Saturn sUSDat MVP asset dossier

Verification date: 2026-06-04 UTC
Verifier: Hermes kanban QA worker
Methodology contract: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/methodology.md`
Dossier reviewed: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/reports/eth-mainnet-susdat.md`
Parent artifacts reviewed:
- `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/eth-mainnet-susdat/onchain-admin.md`
- `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/eth-mainnet-susdat/issuer-backing-security.md`
- `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/eth-mainnet-susdat/transfer-liquidity-oracle-governance.md`
- `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/eth-mainnet-susdat/raw/onchain-admin-snapshot-2026-06-04.json`
- `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/eth-mainnet-susdat/raw/dexscreener-saturn_susdat-2026-06-04.json`

## Approval summary

PASS. The Saturn sUSDat dossier is usable under the MVP asset-specific methodology: it pins the supplied Ethereum mainnet scope, covers all nine required pipeline sections through its section 3-11 mapping, cites multiple primary onchain and issuer sources, classifies NAV/backing exposure, checks admin/sensitive actions, checks transfer/redemption/liquidity/oracle paths, and carries material unknowns with explicit `missing_behavior` labels. I found no exact remediation item that should block this Kanban card.

## Scope check

| Required scope field | Expected | Dossier value | Result |
|---|---|---|---|
| Display | Saturn sUSDat | Saturn sUSDat | PASS |
| Chain | Ethereum mainnet | Ethereum mainnet | PASS |
| `chain_id` | `1` | `1` | PASS |
| Token address | `0xd166337499e176bbc38a1fbd113ab144e5bd2df7` | `0xD166337499E176bbC38a1FBd113Ab144e5bd2Df7` | PASS |
| Symbol | `sUSDat` | `sUSDat` | PASS |

The checksum-cased address in the dossier matches the user-supplied address case-insensitively. The parent onchain snapshot also records `sUSDat: 0xD166337499E176bbC38a1FBd113Ab144e5bd2Df7`, and the saved Dexscreener snapshot identifies the base token as `Staked USDat` / `sUSDat` at the same address.

## Methodology section coverage

| MVP pipeline section | Dossier section | Result |
|---|---|---|
| 1. Identity and token semantics | `## 3. Identity and token semantics` | PASS |
| 2. Issuer / protocol and business model | `## 4. Issuer / protocol and business model` | PASS |
| 3. Backing, NAV, and exposure map | `## 5. Backing, NAV, and exposure map` | PASS |
| 4. Contract admin, multisigs, and sensitive actions | `## 6. Contract admin, multisigs, and sensitive actions` | PASS |
| 5. Audits, formal verification, and incidents | `## 7. Audits, formal verification, and incidents` | PASS |
| 6. Transferability, redemption, and liquidity | `## 8. Transferability, redemption, and liquidity` | PASS |
| 7. Oracle and pricing methodology | `## 9. Oracle and pricing methodology` | PASS |
| 8. Governance / change-feed watchlist | `## 10. Governance / change-feed watchlist` | PASS |
| 9. Data quality and missing-data behavior | `## 11. Data quality and missing-data behavior` | PASS |

The dossier also includes the methodology's minimal wrapper sections: agent-context summary, one-paragraph mechanism, highest-impact unknowns, and a source list.

## Acceptance-criteria checks

| Check | Evidence | Result |
|---|---|---|
| Token supplied by user/backend scope | Header uses the supplied display, chain, chain_id, address, symbol, and intended use unknown. | PASS |
| Identity facts pinned to chain/address | Section 3 pins Ethereum mainnet, `chain_id: 1`, exact address, name, symbol, decimals, asset, and proxy/source status. | PASS |
| At least two primary sources cited when available | Source table includes onchain primary sources O1-O6 and issuer primary sources D1-D6; inline sections cite both classes. | PASS |
| Admin roles and sensitive actions checked or marked unknown | Section 6 inventories proxy/implementation state, `DEFAULT_ADMIN_ROLE`, `PROCESSOR_ROLE`, `COMPLIANCE_ROLE`, timelock, USDat roles, Safe scan result, pending admin transition, and sensitive action impact/speed classifications. | PASS |
| NAV/backing/reserve exposure classified | Section 5 states `nav_model: collateralized vault / issuer NAV / offchain-credit exposure` and maps USDat, STRC, dynamic reserve, app split, custody/NAV proof caveats, and NAV-vs-market-price divergence. | PASS |
| Transfer/freeze/redemption/liquidity paths checked or unknown | Section 8 covers ERC-20 transfer checks, sUSDat blacklist/pause state, USDat whitelist/freeze/forced-transfer controls, queue/NFT redemption, queue state, DEX venues, live-quote caveat, and eligible-liquidator unknown. | PASS |
| Oracle methodology checked or unknown | Section 9 describes `totalAssets()` accounting, STRC oracle address, wrapped Chainlink-compatible dependency, staleness/bounds/observed price, redemption validation, blind spots, and missing Gearbox oracle state. | PASS |
| Missing material fields change behavior | Sections 5, 7, 8, 9, 11, and 12 include `review_required`, `block_automation`, `continue`, and `cannot_rank_cleanly` labels. A literal scan found 21 `missing_behavior` occurrences. | PASS |
| No recommendation / suitability verdict / token-selection language | The dossier does not give a buy/sell/hold call, asset-selection verdict, suitability verdict, or clean collateral conclusion. The only asset-selection hit is the negative disclaimer: “does not advise asset selection, position sizing, position fit, or execution.” | PASS |

## Parent-artifact consistency checks

| Topic | Parent evidence | Dossier consistency | Result |
|---|---|---|---|
| Identity and semantics | `onchain-admin.md` records name `Staked USDat`, symbol `sUSDat`, 18 decimals, USDat asset, queue, STRC oracle, UUPS proxy, and disabled standard ERC-4626 withdraw/redeem. | Dossier sections 1-3 and 6-9 carry the same facts and cite O1/O2/O3/O5/O6/R1. | PASS |
| Admin roles and pending timelock migration | `onchain-admin.md` records EOA + timelock default-admin holders, 5-day timelock, pending revocations around 2026-06-08, no Safe holder found, and compliance/processor roles. | Dossier sections 6, 10, 11, and 12 preserve the immediate-vs-pending-timelock distinction and the Safe/no-Safe caveat. | PASS |
| Backing/NAV/security | `issuer-backing-security.md` records `nav_model: collateralized vault / issuer NAV / offchain-credit exposure`, USDat + STRC exposure, app split, unverified reserve/NAV proof, audit-scope caveat, and incident caveat. | Dossier sections 4, 5, 7, 11, and 12 preserve those facts and missing behaviors. | PASS |
| Transfer/liquidity/oracle/governance | `transfer-liquidity-oracle-governance.md` records blacklist/freeze/pause/whitelist controls, queue/NFT redemption, point-in-time DEX liquidity, STRC oracle methodology and blind spots, and change-feed items. | Dossier sections 8, 9, 10, 11, and 12 carry the same bounded claims and explicitly block automation without live quote/Preview. | PASS |

## Gearbox terminology scan

| Term | Dossier count | QA note |
|---|---:|---|
| `Credit Account` | 2 | Used only in methodology-relevant conditional phrasing: if used as Credit Account collateral. No unsupported current Gearbox support claim. |
| `Credit Manager` | 0 | No unsupported Credit Manager claim. |
| `transition-stage assets` | 0 | No generic phrase hit; the dossier uses `Transition-stage behavior` for the redemption-queue/NFT state. |
| `non-atomic settlement` | 0 | No unsupported settlement-term claim. |
| `timelock` | 12 | Supported by onchain/timelock evidence and pending-operation state. |
| `Safe` | 5 | Used to report that no Safe multisig was identified among current onchain role holders. |

## Non-blocking notes

- Section 6's sensitive-action table uses human-readable column labels (`Existing-holder impact`, `Execution speed in snapshot`) rather than the exact methodology key strings (`existing_holder_impact`, `execution_speed`), but the row values use the methodology categories (`direct_freeze`, `direct_transfer`, `direct_redemption_block`, `indirect`, `unknown`, `immediate`, `timelocked`) and satisfy the contract.
- The negative disclaimer about not advising asset selection is acceptable because it is an out-of-scope statement, not token-selection guidance.
- Current-state facts are point-in-time to 2026-06-04. The dossier correctly flags the pending 2026-06-08 admin revocation recheck and live quote/Preview requirements rather than converting them into clean conclusions.

## Final verifier decision

Approved for MVP dossier use. No Kanban-blocking remediation required.
