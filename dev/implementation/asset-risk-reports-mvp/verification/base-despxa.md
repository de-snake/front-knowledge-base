# Verification — Centrifuge deSPXA MVP asset dossier

Verification date: 2026-06-04 UTC
Verifier: Hermes kanban QA worker
Methodology contract: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/methodology.md`
Dossier reviewed: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/reports/base-despxa.md`
Parent artifacts reviewed:
- `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/base-despxa/onchain-admin.md`
- `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/base-despxa/issuer-backing-security.md`
- `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/base-despxa/transfer-liquidity-oracle-governance.md`

## Approval summary

PASS. The Centrifuge deSPXA dossier is usable under the MVP asset-specific methodology: it pins the supplied Base scope, covers all nine required pipeline sections through its section 3-11 mapping, cites multiple primary onchain and issuer sources, classifies issuer-NAV/tokenized-fund exposure, checks admin/sensitive actions, checks transfer/redemption/liquidity/oracle paths, and carries material unknowns with explicit `missing_behavior` labels. I found no exact remediation item that should block this Kanban card.

## Scope check

| Required scope field | Expected | Dossier value | Result |
|---|---|---|---|
| Display | Centrifuge deSPXA | Centrifuge deSPXA | PASS |
| Chain | Base | Base | PASS |
| `chain_id` | `8453` | `8453` | PASS |
| Token address | `0x9c5C365e764829876243d0b289733B9D2b729685` | `0x9c5C365e764829876243d0b289733B9D2b729685` | PASS |
| Symbol | `deSPXA` | `deSPXA` | PASS |

The dossier header, section 3 identity table, and parent onchain artifact all match the supplied Base chain, `chain_id`, token address, and symbol.

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
| Token supplied by user/backend scope | Header uses the supplied display, chain, `chain_id`, address, symbol, and intended use unknown. | PASS |
| Identity facts pinned to chain/address | Section 3 pins Base, `chain_id: 8453`, exact address, name, symbol, decimals, token/vault/hook addresses, Root/admin hub, and proxy/source status. | PASS |
| At least two primary sources cited when available | Source table includes parent research artifacts plus primary onchain sources O1-O6 and issuer/governance sources D1-D3, D5, D6; inline sections cite both source classes. | PASS |
| Admin roles and sensitive actions checked or marked unknown | Section 6 inventories the non-proxy token, AsyncVault, hook, Root, request manager, Root ward state, four unresolved active Root ward contracts, sensitive action impact/speed classifications, and Safe/timelock unknowns. | PASS |
| NAV/backing/reserve exposure classified | Section 5 states `nav_model: issuer NAV / tokenized fund wrapper / async vault`, maps Base USDC vault accounting, SPXA/S&P 500 economic exposure, manager price-per-share, NAV-vs-DEX divergence, and legal/fund-doc unknowns. | PASS |
| Transfer/freeze/redemption/liquidity paths checked or unknown | Section 8 covers `FreelyTransferable` ordinary transfer behavior, freeze/member mechanics, ERC-1404 checks, async deposit/redeem/claim paths, AP/member eligibility, saved DEX venues, and live quote/Preview caveats. | PASS |
| Oracle methodology checked or unknown | Section 9 describes manager-provided price-per-share, price timestamp, Chronicle source hint, missing feed/cadence/staleness details, NAV/market divergence, oracle blind spots, and missing Gearbox oracle state. | PASS |
| Missing material fields change behavior | Sections 5, 6, 7, 8, 9, 11, and 12 include `review_required`, `block_automation`, `continue`, and `cannot_rank_cleanly` labels. A literal scan found 20 `missing_behavior` occurrences. | PASS |
| No recommendation / suitability verdict / token-selection language | The dossier does not give a buy/sell/hold call, suitability verdict, clean collateral conclusion, or token-selection guidance. The token-selection / investment hits are a negative disclaimer and a factual RWA.xyz minimum-investment field. | PASS |

## Parent-artifact consistency checks

| Topic | Parent evidence | Dossier consistency | Result |
|---|---|---|---|
| Identity and semantics | `onchain-admin.md` records Base `chain_id: 8453`, exact deSPXA address, name, symbol, 18 decimals, non-proxy `ShareToken`, linked Base USDC `AsyncVault`, `FreelyTransferable` hook, Root, and async request manager. | Dossier sections 1-3 and 6-9 carry the same facts and cite R1/O1-O6. | PASS |
| Admin roles and sensitive actions | `onchain-admin.md` records Centrifuge `Auth`/`wards`, Root `delay=172800`, `paused=false`, four active unverified Root ward contracts, no resolved Safe threshold, and sensitive surfaces including hook replacement, forced transfer, mint/burn, vault manager changes, and Root operations. | Dossier sections 6, 10, 11, and 12 preserve the same admin surfaces, impact/speed classifications, and unresolved ward/Safe caveats. | PASS |
| Issuer, backing, and security | `issuer-backing-security.md` records deSPXA as a freely transferable Base wrapper/exposure for SPXA / Janus Henderson Anemoy S&P 500 Index Fund, `nav_model: issuer NAV / tokenized fund wrapper / async vault`, AP/KYC redemption caveats, missing legal/fund docs, no exact deployed-scope audit match, and bounded incident caveat. | Dossier sections 4, 5, 7, 11, and 12 preserve those facts and missing behaviors without converting them into clean acceptance claims. | PASS |
| Transfer, liquidity, oracle, governance | `transfer-liquidity-oracle-governance.md` records ordinary non-frozen transfers, member-gated primary request/claim flows, async ERC-7540 redemption, point-in-time DEX liquidity, manager/Centrifuge/Chronicle pricing, oracle blind spots, and watchlist surfaces. | Dossier sections 8, 9, 10, 11, and 12 carry the same bounded claims and explicitly block automation without live quotes, holder eligibility, and request-state checks. | PASS |

## Gearbox terminology scan

| Term | Dossier count | QA note |
|---|---:|---|
| `Credit Account` | 2 | Used only in methodology-relevant conditional phrasing: if deSPXA is used as Credit Account collateral. No unsupported current Gearbox support claim. |
| `Credit Manager` | 0 | No unsupported Credit Manager claim. |
| `transition-stage assets` | 0 | No generic phrase hit. The dossier uses `Transition-stage behavior` to describe async pending request/claim states. |
| `non-atomic settlement` | 0 | No unsupported settlement-term claim. |
| `timelock` | 3 | Used for Root/new-ward delay and unresolved Safe/timelock owner caveats; supported by parent onchain evidence or explicitly unknown. |
| `Safe` | 8 | Used to report unresolved Safe owner/threshold state, not to assert a confirmed Safe-controlled governance path. |

## Non-blocking notes

- Section 6's sensitive-action table uses human-readable column labels rather than the exact methodology key names, but the row values use the methodology categories (`direct_freeze`, `direct_transfer`, `direct_dilution`, `direct_redemption_block`, `indirect`, `unknown`, `immediate`, `timelocked`) and satisfy the contract.
- The source list's `METH` row has `source_class: unknown`, which is acceptable for the local methodology contract; material asset facts cite onchain, issuer_docs, governance, market_data, or local research source classes.
- Current-state facts are point-in-time to 2026-06-04. The dossier correctly flags Root ward identity, holder eligibility, fund/legal documents, audit scope, Chronicle feed details, and executable liquidity as review/blocking unknowns instead of clean conclusions.

## Final verifier decision

Approved for MVP dossier use. No Kanban-blocking remediation required.
