# apyx apxUSD — technical + analyst report QA verification

Verification date: 2026-06-04 UTC
Verifier: Hermes operator recovery after QA worker crashed
Methodology contract: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/methodology.md`
Technical dossier reviewed: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/technical-reports/eth-mainnet-apxusd.md`
Analyst report reviewed: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/reports/eth-mainnet-apxusd.md`
Parent artifacts reviewed:
- `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/eth-mainnet-apxusd/onchain-admin.md`
- `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/eth-mainnet-apxusd/issuer-backing-security.md`
- `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/eth-mainnet-apxusd/transfer-liquidity-oracle-governance.md`

## Approval summary

PASS. The apyx apxUSD technical dossier and analyst report satisfy the MVP asset-risk QA contract. The reports pin the supplied Ethereum-mainnet token scope, cover the nine methodology areas, cite multiple primary source classes, preserve source-linked evidence, classify backing/NAV and admin/sensitive-action risk, carry material unknowns with explicit `missing_behavior`, and do not provide recommendations, suitability verdicts, rankings, token-selection language, or execution instructions.

## Scope check

| Required scope field | Expected | Report value | Result |
|---|---|---|---|
| Display | apyx apxUSD | apyx apxUSD | PASS |
| Chain | Ethereum mainnet | Ethereum mainnet | PASS |
| `chain_id` | `1` | `1` | PASS |
| Token address | `0x98A878b1Cd98131B271883B390f68D2c90674665` | `0x98A878b1Cd98131B271883B390f68D2c90674665` | PASS |
| Symbol | `apxUSD` | `apxUSD` | PASS |

## Methodology section coverage

| MVP pipeline section | Technical dossier section | Result |
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

The technical dossier also includes the wrapper sections required by the synthesize task: agent-context summary, one-paragraph mechanism, highest-impact unknowns, and sources.

## Acceptance-criteria checks

| Check | Evidence | Result |
|---|---|---|
| Chain/address/symbol match user scope | Headers and identity section pin Ethereum mainnet, `chain_id: 1`, exact address, and symbol `apxUSD`. | PASS |
| Technical dossier covers all nine pipeline areas | Sections 3-11 map to methodology sections 1-9. | PASS |
| At least two primary sources cited | Source list includes onchain/RPC/source evidence and Apyx issuer docs; governance, audit, contract README, and market data are also cited. | PASS |
| Admin roles and sensitive actions checked or unknown | Section 6 inventories UUPS proxy/implementation, AccessManager, Safe-like role holders, minting, pause, deny-list, supply cap, upgrades, authority rotation, CCIP admin, and pending Safe caveats. | PASS |
| NAV/backing/reserve exposure classified | Section 5 states `nav_model: issuer NAV / off-chain preferred-share collateral / overcollateralized synthetic dollar` and preserves reserve/custody/attestation gaps. | PASS |
| Transfer/freeze/redemption/liquidity paths checked | Section 8 covers pause, deny-list, eligibility, primary redemption, no identified general forced-transfer path, Curve/Uniswap/PancakeSwap liquidity, and live quote caveats. | PASS |
| Oracle methodology checked or unknown | Section 9 states no token-native holder price oracle was found and explains issuer NAV, redemption, market routes, and staleness dependencies. | PASS |
| Highest-impact unknowns include missing behavior | Section 12 contains explicit `missing_behavior` for backing/NAV, redemption eligibility, market-route, governance, audit scope, incident-history, and Gearbox-oracle unknowns. | PASS |
| Analyst readability | Analyst report uses prose/bullets, has no code fences and no Markdown tables. | PASS |
| Source map linkability | Analyst source map bullets contain actual clickable URLs or local evidence links for every source ID. | PASS |
| Recommendation/ranking scan | Deterministic scan found no buy/sell/recommend/ranking/execution-language hit beyond explicit negative disclaimers. | PASS |

## Gearbox terminology scan

| Term | Combined report count | QA note |
|---|---:|---|
| `Credit Account` | 5 | Used only as conditional collateral/oracle context; no unsupported current Gearbox support claim. |
| `Credit Manager` | 0 | No unsupported Credit Manager claim. |
| `transition-stage assets` | 0 | No unsupported transition-stage claim. |
| `non-atomic settlement` | 0 | No unsupported settlement-term claim. |
| `timelock` | 7 | Used in methodology/control timing context, not as an unsupported governance conclusion. |
| `Safe` | 60 | Supported by Safe-like holder and pending Safe Transaction Service evidence; caveats about modules/guards/pending payloads are preserved. |

## Minor caveats retained intentionally

- Collateral dashboard values, attestation PDFs, preferred-share issuer concentration, and custody details were not reconciled to onchain supply; the reports correctly preserve `cannot_rank_cleanly` / `review_required`.
- Primary redemption is eligibility-gated and user-specific access was not verified; live redemption remains `block_automation` until refreshed.
- DEXScreener market data is point-in-time and venue prices diverged; live exits remain `block_automation` without route quote, holder/recipient status, and current pause/deny-list/governance checks.
- Audit report existence is documented, but deployed-scope matching against current contracts/roles/pending Safe state was not completed; the reports correctly leave this as `review_required`.

## Deterministic check result

A local QA script verified:

- both output files exist;
- required technical and analyst headings are present;
- primary source classes are represented;
- admin/sensitive-action, NAV/backing, transfer/liquidity/redemption, and oracle sections are present;
- analyst report has no code fences or Markdown tables;
- technical and analyst source sections contain URL/local-evidence links;
- no forbidden recommendation/ranking/execution-language patterns were found.

## Final verifier decision

Approved for MVP dossier use. No Kanban-blocking remediation required. Any production use still requires fresh Preview checks for route quotes, eligibility/deny-list/pause state, backing/reserve evidence, audit-scope mapping, and current AccessManager/Safe/governance state.
