# Saturn USDat — technical + analyst report QA verification

Verification date: 2026-06-04 UTC
Verifier: Hermes operator recovery after QA worker crashed
Methodology contract: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/methodology.md`
Technical dossier reviewed: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/technical-reports/eth-mainnet-usdat.md`
Analyst report reviewed: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/reports/eth-mainnet-usdat.md`
Parent artifacts reviewed:
- `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/eth-mainnet-usdat/onchain-admin.md`
- `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/eth-mainnet-usdat/issuer-backing-security.md`
- `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/eth-mainnet-usdat/transfer-liquidity-oracle-governance.md`

## Approval summary

PASS. The Saturn USDat technical dossier and analyst report satisfy the MVP asset-risk QA contract. The reports pin the supplied Ethereum-mainnet token scope, cover the nine methodology areas, cite multiple primary source classes, preserve source-linked evidence, classify backing/NAV and admin/sensitive-action risk, carry material unknowns with explicit `missing_behavior`, and do not provide recommendations, suitability verdicts, rankings, token-selection language, or execution instructions.

## Scope check

| Required scope field | Expected | Report value | Result |
|---|---|---|---|
| Display | Saturn USDat | Saturn USDat | PASS |
| Chain | Ethereum mainnet | Ethereum mainnet | PASS |
| `chain_id` | `1` | `1` | PASS |
| Token address | `0x23238F20B894f29041f48d88Ee91131c395aAA71` | `0x23238F20B894f29041f48d88Ee91131c395aAA71` | PASS |
| Symbol | `USDat` | `USDat` | PASS |

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
| Chain/address/symbol match user scope | Headers and identity section pin Ethereum mainnet, `chain_id: 1`, exact address, and symbol `USDat`. | PASS |
| Technical dossier covers all nine pipeline areas | Sections 3-11 map to methodology sections 1-9. | PASS |
| At least two primary sources cited | Source list includes onchain/Etherscan/RPC/source evidence and Saturn issuer docs; market data is also cited. | PASS |
| Admin roles and sensitive actions checked or unknown | Section 6 inventories Transparent proxy, implementation, ProxyAdmin, owner, timelocks, default admin, compliance roles, freeze, forced transfer, whitelist, pause, and sensitive action impacts/speeds. | PASS |
| NAV/backing/reserve exposure classified | Section 5 states `nav_model: 1:1 reserve / tokenized-treasury-backed issuer stablecoin / permissioned wrapper` and preserves `$M` backing caveats. | PASS |
| Transfer/freeze/redemption/liquidity paths checked | Section 8 covers whitelist, onboarding, freeze, forced transfer, pause, primary redemption, Curve/Balancer liquidity, and live quote caveats. | PASS |
| Oracle methodology checked or unknown | Section 9 states no token-native holder price oracle was found and explains issuer peg, reserve, redemption, and market-route dependencies. | PASS |
| Highest-impact unknowns include missing behavior | Section 12 contains explicit `missing_behavior` for reserve, eligibility, audit scope, admin migration, oracle/route, and incident-history unknowns. | PASS |
| Analyst readability | Analyst report uses prose/bullets, has no code fences and no Markdown tables. | PASS |
| Source map linkability | Analyst source map bullets contain actual clickable URLs or local evidence links for every source ID. | PASS |
| Recommendation/ranking scan | Deterministic scan found no buy/sell/recommend/ranking/execution-language hit beyond explicit negative disclaimers. | PASS |

## Gearbox terminology scan

| Term | Combined report count | QA note |
|---|---:|---|
| `Credit Account` | 4 | Used only as conditional collateral/oracle context; no unsupported current Gearbox support claim. |
| `Credit Manager` | 0 | No unsupported Credit Manager claim. |
| `transition-stage assets` | 0 | No unsupported transition-stage claim. |
| `non-atomic settlement` | 0 | No unsupported settlement-term claim. |
| `timelock` | 19 | Supported by the onchain/timelock role evidence and pending-role-migration caveats. |
| `Safe` | 6 | Used mainly to state no Safe multisig holder was identified for the current USDat role snapshot. |

## Minor caveats retained intentionally

- `$M` reserve composition, custody, redemption terms, and legal recourse were not independently expanded; the reports correctly keep this as `review_required`.
- Current admin classification is point-in-time and must be refreshed because pending role migration evidence was not proof of execution; the reports correctly mark live control classification as `review_required`.
- DEXScreener liquidity is static market data, not an executable quote; live exits remain `block_automation` until route, eligibility, and token-state checks are refreshed.
- Audit report existence is documented, but deployed-scope matching was not completed; the reports correctly leave this as `review_required`.

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

Approved for MVP dossier use. No Kanban-blocking remediation required. Any production use still requires fresh Preview checks for route quotes, eligibility/whitelist/freeze/pause state, backing/reserve evidence, audit-scope mapping, and current admin/governance state.
