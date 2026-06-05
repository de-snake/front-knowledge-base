# Saturn USDat — MVP asset risk dossier

Report date: 2026-06-04 UTC
Analyst: Hermes kanban synthesis worker
Display: Saturn USDat
Chain: Ethereum mainnet (`chain_id: 1`)
Token address: `0x23238F20B894f29041f48d88Ee91131c395aAA71`
Symbol: `USDat`
Intended use: unknown

This dossier is an objective, source-linked asset context artifact. It does not advise asset selection, position sizing, position fit, or execution.

Citation format: inline source IDs resolve in Section 13 to URL or local evidence path, source class, access date, and confidence. Material rows also state source class/access/confidence inline when the source is especially important.

## 1. Agent-context summary

Saturn USDat is a 6-decimal Ethereum mainnet stablecoin at `0x23238F20B894f29041f48d88Ee91131c395aAA71`; direct RPC evidence recorded `name="USDat"`, `symbol="USDat"`, `decimals=6`, `paused=false`, and `isWhitelistEnabled=true` at the 2026-06-04 snapshot [R1/O2, onchain, 2026-06-04, high]. Saturn docs describe USDat as a fully collateralized, permissioned stablecoin backed at launch by M0's `$M` tokenized U.S. Treasuries product, mintable/redeemable through Saturn flows for onboarded addresses [D1, issuer_docs, 2026-06-04, medium]. The exact token is not an ordinary unrestricted ERC-20: it is a TransparentUpgradeableProxy with whitelist, pause, freeze, forced-transfer, role-management, asset-cap, and upgrade-control surfaces [R1/O1/O2/O3, onchain, 2026-06-04, high]. Material downstream behavior is therefore issuer-control and eligibility dependent; unresolved `$M` backing details, legal/onboarding policy, audit-scope matching, live admin state, and live route/eligibility checks are marked `review_required` or `block_automation` rather than treated as absence of risk [METH/R1/R2/R3, mixed, 2026-06-04, medium-high].

## 2. One-paragraph mechanism

USDat is Saturn's permissioned stablecoin wrapper/settlement asset: Saturn docs state that eligible users can mint USDat by depositing USDC or `$M`, redeem USDat for USDC through Saturn's interface, and hold a token intended to maintain 1:1 USD value while reserves are backed by M0 `$M` [D1, issuer_docs, 2026-06-04, medium]. Onchain evidence shows the live USDat token is implemented as an upgradeable Saturn/M0-extension-style token with AccessControl, whitelist, freeze, forced-transfer, pause, asset-cap, and yield-recipient mechanics; these controls can affect holding, transfer, redemption, and token behavior even if the issuer peg and current DEX market price appear close to $1 [R1/R2/R3/O2/O3/M1, mixed onchain+issuer_docs+market_data, 2026-06-04, medium-high].

## 3. Identity and token semantics

| Field | Value | Source |
|---|---|---|
| Canonical chain | Ethereum mainnet | User-supplied scope corroborated by Ethereum RPC/Etherscan evidence [R1/O1/O2, onchain, 2026-06-04, high] |
| chain_id | `1` | User-supplied scope and Ethereum mainnet RPC context [O2, onchain, 2026-06-04, high] |
| Token / proxy address | `0x23238F20B894f29041f48d88Ee91131c395aAA71` | User-supplied scope, Etherscan token/proxy page, direct RPC snapshot [R1/O1/O2, onchain, 2026-06-04, high] |
| `name()` | `USDat` | Direct RPC snapshot [R1/O2, onchain, 2026-06-04, high] |
| `symbol()` | `USDat` | Direct RPC snapshot [R1/O2, onchain, 2026-06-04, high] |
| `decimals()` | `6` | Direct RPC snapshot [R1/O2, onchain, 2026-06-04, high] |
| Current paused status | `paused=false` in the snapshot | Direct RPC snapshot [R1/O2, onchain, 2026-06-04, high] |
| Current whitelist status | `isWhitelistEnabled=true` in the snapshot | Direct RPC snapshot and verified source summary [R1/O2/O3, onchain, 2026-06-04, high] |
| Proxy pattern | TransparentUpgradeableProxy | EIP-1967 implementation/admin slots and verified proxy/source evidence [R1/O2/O3, onchain, 2026-06-04, high] |
| Current implementation | `0x17cAC25c6D6BBcB592837FEA083A5c8Eb4D1E52E` | EIP-1967 implementation slot in RPC snapshot [R1/O2, onchain, 2026-06-04, high] |
| ProxyAdmin | `0xcf1072DA5f0D127AEf99136489BAd08bFa3D1A7D` | EIP-1967 admin slot in RPC snapshot [R1/O2, onchain, 2026-06-04, high] |
| ProxyAdmin owner | `0x610182581C93687Ca03F4a8E7f124f8cEC616820` | ProxyAdmin `owner()` in RPC snapshot [R1/O2, onchain, 2026-06-04, high] |
| Token standard / behavior | Upgradeable ERC-20-style Saturn/M0 extension token; not a pure immutable ERC-20 | Verified implementation inherits `JMIExtension` and `ForcedTransferable`; inherited components add controls [R1/O3, onchain, 2026-06-04, high] |
| Asset type | Issuer-controlled / permissioned stablecoin backed per Saturn docs by M0 `$M` | Saturn docs plus exact-token source/role evidence [D1/R1/R2, mixed, 2026-06-04, medium-high] |
| Holder behavior | Non-rebasing stablecoin-style token; USDat itself does not directly accrue yield to holders in the cited Saturn overview | Saturn overview states yield from underlying reserves flows to Saturn's revenue vault and yield-seeking users are directed to sUSDat [D1/R2, issuer_docs/local research, 2026-06-04, medium] |
| Transition-stage behavior | No USDat-specific claim token/NFT/withdrawal queue was identified in parent artifacts; a live exit can still become issuer/interface/route dependent | Parent transfer/liquidity research [R3, local research, 2026-06-04, medium]. `missing_behavior: review_required` for settlement/eligibility details; `block_automation` for execution without Preview. |

USDat should therefore be modeled as a permissioned issuer-controlled stablecoin and not as an unrestricted stablecoin or immutable cash-equivalent token. Missing ordinary-collateral assumptions have `missing_behavior: review_required` before clean ranking or production collateral analysis [METH/R1/R2/R3, mixed, 2026-06-04, medium-high].

## 4. Issuer / protocol and business model

| Topic | Facts | Source |
|---|---|---|
| Issuer / protocol context | Saturn is the protocol/issuer context named by the official docs for USDat | Saturn USDat docs and parent research [D1/R2, issuer_docs/local research, 2026-06-04, medium] |
| Product framing | Saturn describes USDat as a fully collateralized stablecoin for liquidity and settlement, maintaining a 1:1 peg to the U.S. dollar | USDat overview [D1, issuer_docs, 2026-06-04, medium] |
| Backing claim | Saturn docs state launch reserves are 100% M0 `$M`, described as tokenized U.S. Treasuries exposure | USDat overview [D1, issuer_docs, 2026-06-04, medium] |
| Mint / redeem path | Saturn docs say users can mint with USDC or `$M` and redeem USDat for USDC through Saturn's interface | USDat overview [D1/R3, issuer_docs/local research, 2026-06-04, medium] |
| Access model | Saturn docs say only addresses that completed Saturn onboarding can mint, redeem, or hold USDat; onchain whitelist was enabled in the snapshot | USDat overview plus RPC/source evidence [D1/R1/R3, issuer_docs+onchain, 2026-06-04, medium-high] |
| Holder yield | USDat does not directly accrue yield to holders according to the extracted Saturn overview; yield from underlying reserves flows to Saturn protocol revenue, while sUSDat is the yield-bearing product | Parent issuer/backing research [R2/D1, issuer_docs/local research, 2026-06-04, medium] |
| Offchain dependencies | Saturn onboarding/compliance, `$M` backing asset availability and terms, issuer mint/redeem infrastructure, and USDC redemption capacity | Synthesized from Saturn docs and missing-field analysis [D1/D2/R2/R3, mixed, 2026-06-04, medium] |
| Control dependencies | Upgrade/admin, default-admin, compliance, whitelist, freeze, forced-transfer, pause, asset-cap, and yield-recipient roles are material to token behavior | Onchain/admin artifact and verified source evidence [R1/O2/O3, onchain, 2026-06-04, high] |

Business-model caveat: the parent artifacts did not independently verify Saturn's legal entity, onboarding terms, revenue-vault policy, M0 `$M` custody/reserve terms, or user-specific redemption eligibility beyond official Saturn docs and onchain role surfaces. `missing_behavior: review_required` for issuer/legal analysis and `block_automation` for live actions that assume eligibility or unrestricted redemption [METH/R2/R3, mixed, 2026-06-04, medium-high].

## 5. Backing, NAV, and exposure map

`nav_model: 1:1 reserve / tokenized-treasury-backed issuer stablecoin / permissioned wrapper`

| Field | Current facts | Source |
|---|---|---|
| Reserve / backing asset named by issuer | Saturn docs state USDat is backed by M0 `$M`, with launch reserves 100% `$M` | USDat overview [D1/R2, issuer_docs/local research, 2026-06-04, medium] |
| Reserve location claim | Saturn transparency page states all USDat capital is held directly in the USDat smart contract and verifiable onchain | Transparency/audits page [D2/R2, issuer_docs/local research, 2026-06-04, medium] |
| Contract support for wrapper framing | Verified source shows an M-extension/JMI-style token with whitelist wrapping/unwrapping hooks | Verified source extracts and onchain/admin research [R1/O3, onchain, 2026-06-04, high] |
| Custody and legal terms | Not independently expanded in parent artifacts for M0 `$M`, reserve custody, M0 redemption, or Saturn legal/onboarding terms | Parent issuer/backing research [R2, local research, 2026-06-04, medium]. `missing_behavior: review_required`. |
| Reserve report / proof cadence | Not independently established; transparency page was located, but a reserve/NAV reconciler was not built in this pass | Transparency page and transfer/oracle research [D2/R2/R3, issuer_docs/local research, 2026-06-04, medium]. `missing_behavior: review_required`. |
| Primary redemption model | Saturn interface / issuer path returning USDC, subject to onboarding/whitelist/restriction state | USDat overview plus onchain controls [D1/R1/R3, mixed, 2026-06-04, medium-high] |
| NAV vs secondary price | Practical exit value can diverge from the issuer 1:1 framing if eligibility, whitelist/freeze/pause, `$M` backing/liquidity, USDC redemption capacity, or DEX liquidity are impaired | Synthesized from docs/onchain/market data [R1/R2/R3/M1, mixed, 2026-06-04, medium-high] |
| Market snapshot | Saved DEXScreener data showed a Curve USDat/USDC venue at price `1.00010`, about `$16.52m` liquidity, and about `$7.37m` 24h volume at extraction; a tiny Balancer venue also appeared | Saved DEXScreener JSON [M1/R3, market_data/local research, 2026-06-04, medium] |

Backing/NAV missing-data behavior: issuer docs explain the intended backing model, but the parent artifacts did not independently verify `$M` reserve composition, custody, redemption terms, reserve reports, or legal recourse. For descriptive context this can continue with explicit caveats; for clean ranking, collateral acceptance, or live automation it is `missing_behavior: review_required`, and a concrete exit without live eligibility/route/issuer-state checks is `missing_behavior: block_automation` [METH/R2/R3, mixed, 2026-06-04, medium-high].

## 6. Contract admin, multisigs, and sensitive actions

### 6.1 Proxy / implementation / upgradeability

| Contract | Address | Pattern / current admin state | Existing-holder relevance | Source |
|---|---|---|---|---|
| USDat proxy | `0x23238F20B894f29041f48d88Ee91131c395aAA71` | TransparentUpgradeableProxy | Implementation upgrade can change token behavior, including controls that affect existing holders | Etherscan/source/storage RPC [O1/O2/O3/R1, onchain, 2026-06-04, high] |
| USDat implementation | `0x17cAC25c6D6BBcB592837FEA083A5c8Eb4D1E52E` | Verified implementation | Current logic includes whitelist, freeze, forced-transfer, pause, asset-cap, and yield-recipient mechanics | EIP-1967 slot and source extracts [O2/O3/R1, onchain, 2026-06-04, high] |
| ProxyAdmin | `0xcf1072DA5f0D127AEf99136489BAd08bFa3D1A7D` | OpenZeppelin ProxyAdmin | Owner can upgrade Transparent proxy implementation | Proxy admin slot and owner call [O2/O3/R1, onchain, 2026-06-04, high] |
| SaturnTimelock | `0xfD5782E3BFF366601da3973aE30C583dE4F08A67` | TimelockController-derived; 432,000 seconds / 5 days minimum delay; open executor | Holds USDat default-admin role, but does not remove the immediate ProxyAdmin-owner path observed in the snapshot | Timelock/source/RPC state [R1/O2/O4, onchain, 2026-06-04, high] |
| AssetCapTimelock | `0x7D343D17896D2cd87A49b4fB8872298A883f78f7` | TimelockController-derived; 432,000 seconds / 5 days minimum delay | Holds asset-cap-manager role | RPC role state [R1/O2, onchain, 2026-06-04, medium-high] |

### 6.2 Current sensitive role holders

| Role / control | Current holder(s) | Holder type | Sensitive powers | Source |
|---|---|---|---|---|
| ProxyAdmin owner | `0x610182581C93687Ca03F4a8E7f124f8cEC616820` | EOA | Upgrades the Transparent proxy implementation | RPC snapshot [R1/O2, onchain, 2026-06-04, high] |
| `DEFAULT_ADMIN_ROLE` | `0x610182581C93687Ca03F4a8E7f124f8cEC616820`; `0xfD5782E3BFF366601da3973aE30C583dE4F08A67` | EOA; timelock contract | Grants/revokes roles and controls AccessControl admin surface | RPC role checks [R1/O2, onchain, 2026-06-04, high] |
| `PAUSER_ROLE` | `0x10D59F776db12b4B271b2609CB8b7Ddd0A82703B` | EOA | Pause/unpause token flows | RPC/source evidence [R1/O2/O3, onchain, 2026-06-04, high] |
| `FREEZE_MANAGER_ROLE` | `0x10D59F776db12b4B271b2609CB8b7Ddd0A82703B` | EOA | Freeze/unfreeze accounts | RPC/source evidence [R1/O2/O3, onchain, 2026-06-04, high] |
| `FORCED_TRANSFER_MANAGER_ROLE` | `0x10D59F776db12b4B271b2609CB8b7Ddd0A82703B` | EOA | Forced transfer from frozen accounts | RPC/source evidence [R1/O2/O3, onchain, 2026-06-04, high] |
| `WHITELIST_MANAGER_ROLE` | `0x10D59F776db12b4B271b2609CB8b7Ddd0A82703B` | EOA | Enable/disable whitelist and add/remove accounts | RPC/source evidence [R1/O2/O3, onchain, 2026-06-04, high] |
| `YIELD_RECIPIENT_MANAGER_ROLE` | `0x09D6E34cE24D54890fF0BC6a090b5f880F8C729f` | EOA | Yield-recipient management in inherited extension | RPC/source evidence [R1/O2/O3, onchain, 2026-06-04, medium] |
| `ASSET_CAP_MANAGER_ROLE` | `0x7D343D17896D2cd87A49b4fB8872298A883f78f7` | Timelock contract | Asset-cap management in inherited extension | RPC/source evidence [R1/O2/O3, onchain, 2026-06-04, medium] |
| Safe multisig | No Safe multisig role holder identified in the current USDat role snapshot | n/a / unknown offchain | No enforceable Safe threshold found for current onchain role holders | Parent onchain/admin artifact [R1, local onchain research, 2026-06-04, medium-high] |

### 6.3 Pending admin transition caveat

The onchain/admin parent artifact observed companion evidence of a pending timelock operation to revoke the immediate EOA default-admin path for USDat, with readiness around 2026-06-08 UTC. The parent artifact explicitly states that this was not proof of execution and that current role state must be rechecked before classifying control as timelocked-only after that date [R1/O2/O4, onchain/local research, 2026-06-04, medium-high]. The ProxyAdmin-owner path also remained immediate in the snapshot [R1/O2, onchain, 2026-06-04, high]. `missing_behavior: review_required` for any live governance/control classification.

### 6.4 Sensitive action classification

| Sensitive action | Current authorized path | Existing-holder impact | Execution speed in snapshot | Source / missing behavior |
|---|---|---|---|---|
| Upgrade USDat implementation | ProxyAdmin owner `0x610182...6820` | `unknown`; implementation can change token semantics | `immediate` | Proxy/source/RPC [R1/O1/O2/O3, onchain, 2026-06-04, high]. Recheck ownership before live use: `review_required`. |
| Grant/revoke token roles | `DEFAULT_ADMIN_ROLE`: EOA `0x610182...6820` plus SaturnTimelock | `unknown` to direct depending role | `immediate` while EOA holds role; timelocked for SaturnTimelock path | Role snapshot [R1/O2/O4, onchain, 2026-06-04, high]. Pending migration: `review_required`. |
| Pause USDat | `PAUSER_ROLE` EOA `0x10D59...03B` | `direct_redemption_block` / transfer block while paused | `immediate` | Source/RPC [R1/O2/O3, onchain, 2026-06-04, high] |
| Freeze accounts | `FREEZE_MANAGER_ROLE` EOA `0x10D59...03B` | `direct_freeze` | `immediate` | Source/RPC [R1/O2/O3, onchain, 2026-06-04, high] |
| Forced transfer from frozen accounts | `FORCED_TRANSFER_MANAGER_ROLE` EOA `0x10D59...03B` | `direct_transfer` | `immediate` | Source/RPC [R1/O2/O3, onchain, 2026-06-04, high] |
| Enable/disable whitelist | `WHITELIST_MANAGER_ROLE` EOA `0x10D59...03B` | `direct_redemption_block` / transferability change for permissioned users | `immediate` | Source/RPC [R1/O2/O3, onchain, 2026-06-04, high] |
| Add/remove whitelisted account | `WHITELIST_MANAGER_ROLE` EOA `0x10D59...03B` | `direct_redemption_block` for affected accounts | `immediate` | Source/RPC [R1/O2/O3, onchain, 2026-06-04, high] |
| Set asset cap | AssetCapTimelock `0x7D343...f7` | `indirect` for future mint/wrap capacity | `timelocked` / 5 days | Source/RPC [R1/O2/O3, onchain, 2026-06-04, medium-high] |
| Change yield recipient | `YIELD_RECIPIENT_MANAGER_ROLE` EOA `0x09D6...729f` | `indirect` | `immediate` | Inherited extension only partially expanded [R1/O2/O3, onchain, 2026-06-04, medium]. `missing_behavior: review_required` for full economic analysis. |

## 7. Audits, formal verification, and incidents

| Item | Facts found | Source / confidence |
|---|---|---|
| Audit reports listed by Saturn | Saturn's transparency/audits page lists Certora Formal Verification, Certora Audit #3, Certora Audit #2, and Three Sigma Audit #1 | Official transparency/audits page as cited by parent research [D2/R2, issuer_docs/local research, 2026-06-04, medium] |
| Formal verification | Certora formal verification is listed by Saturn, but the parent artifact did not extract verified invariants or match them to the exact deployed implementation/admin state | Transparency/audits page and parent caveat [D2/R2, issuer_docs/local research, 2026-06-04, medium]. `missing_behavior: review_required`. |
| Audit scope match | Parent research established report existence but did not download/read each PDF end-to-end or map report scope to current implementation `0x17cAC...1E52E`, ProxyAdmin owner, SaturnTimelock, inherited contracts, and current roles | Parent issuer/security research plus onchain inventory [R2/R1/O2/O3, mixed, 2026-06-04, medium-high]. `missing_behavior: review_required`. |
| Bug bounty | A bug-bounty program and scope were not located in the parent artifacts | Parent source index and security section [R2, local research, 2026-06-04, medium]. `missing_behavior: review_required` for security acceptance, `continue` for descriptive context. |
| Incidents | No confirmed public exploit, reserve shortfall, depeg postmortem, freeze event postmortem, redemption-delay postmortem, oracle failure, or emergency-governance postmortem for exact USDat was found in bounded parent sources | Parent incident pass [R2, local research, 2026-06-04, medium]. Absence of found evidence is not comprehensive incident assurance; `missing_behavior: continue` for explanation and `review_required` for production acceptance. |
| Material governance/control signal | Immediate EOA admin/compliance paths and pending role migration were identified; these are control signals, not incidents by themselves | Onchain/admin parent [R1, local/onchain research, 2026-06-04, high] |

## 8. Transferability, redemption, and liquidity

| Field | Current facts | Source |
|---|---|---|
| Transfer restrictions | USDat is permissioned according to Saturn docs; only onboarded addresses can mint, redeem, or hold USDat | USDat overview [D1/R3, issuer_docs/local research, 2026-06-04, medium] |
| Current onchain restriction state | `isWhitelistEnabled=true`; `paused=false` in the 2026-06-04 snapshot | RPC/source evidence [R1/O2/O3, onchain, 2026-06-04, high] |
| Freeze / forced-transfer / pause | Freezable, ForcedTransferable, Pausable, and whitelist controls exist; compliance EOA holds the relevant roles | Verified source and role snapshot [R1/O2/O3, onchain, 2026-06-04, high] |
| Account-state inventory | Exact list of whitelisted/frozen accounts was not fully enumerated in parent artifacts | Parent transfer research [R3, local research, 2026-06-04, medium]. `missing_behavior: review_required` for holder-specific analysis. |
| Primary redemption path | Saturn interface / issuer pathway; docs state redemptions return USDC to the user's wallet | USDat overview [D1/R3, issuer_docs/local research, 2026-06-04, medium] |
| Redemption conditions | Depends on Saturn onboarding/whitelist state, pause/freeze state, interface availability, and issuer liquidity; live UI/API redemption quote was not tested | Docs plus onchain controls [D1/R1/R3, mixed, 2026-06-04, medium-high]. `missing_behavior: review_required`; `block_automation` for live exits without Preview. |
| Claim token / receipt | None identified for USDat itself in the parent artifacts | Parent transfer research [R3, local research, 2026-06-04, medium]. `missing_behavior: continue` for descriptive context. |
| Secondary venues | Saved DEXScreener snapshot found a Curve USDat/USDC venue and a small Balancer USDat/USDC venue | Market snapshot [M1/R3, market_data/local research, 2026-06-04, medium] |
| Current depth in saved snapshot | Curve USDat/USDC pair `0xF4d0CF32908b2C7f1021339c43Df0F77f06896d7`: `priceUsd=1.00010`, liquidity about `$16,520,157.99`, 24h volume about `$7,372,297.26`; Balancer venue had about `$1,193.01` liquidity | Saved DEXScreener data [M1/R3, market_data/local research, 2026-06-04, medium] |
| Eligible-liquidator depth | Unknown for permissioned holder/recipient constraints; DEX route liquidity may not solve issuer redemption eligibility | Parent transfer research [R3, local research, 2026-06-04, medium]. `missing_behavior: review_required`; `block_automation` for liquidation/execution assumptions without route/eligibility proof. |

Static market data is not an executable quote. A concrete exit, liquidation, or state-changing action has `missing_behavior: block_automation` until live route quotes, holder/recipient eligibility, pause/freeze/whitelist state, and issuer/interface availability are refreshed [METH/R3/M1, mixed, 2026-06-04, medium-high].

## 9. Oracle and pricing methodology

| Field | Current facts | Source |
|---|---|---|
| Token-native price oracle | No holder-facing Chainlink-style price feed was found in the reviewed USDat token source; source is token/accounting/control logic rather than NAV oracle logic | Parent oracle research and verified source [R3/R1/O3, onchain/local research, 2026-06-04, high] |
| Issuer pricing claim | Saturn docs describe a 1:1 USD peg, `$M` collateralization, and USDC redemption | USDat overview [D1/R2/R3, issuer_docs/local research, 2026-06-04, medium] |
| Practical price source | Combination of issuer peg/NAV claim, redemption access, reserve quality, and external market quote/route data | Synthesized from docs/onchain/market data [R1/R2/R3/M1, mixed, 2026-06-04, medium-high] |
| Update cadence | Unknown for issuer reserve/NAV proof; onchain roles/state can be refreshed by RPC; DEX/route data is point-in-time and must be refreshed | Parent oracle research [R3, local research, 2026-06-04, medium]. `missing_behavior: review_required` for reserve/NAV freshness. |
| Staleness window | No token-native staleness window identified for USDat pricing | Parent oracle research [R3/R1, local/onchain research, 2026-06-04, medium-high]. `missing_behavior: review_required` if used as Credit Account collateral oracle methodology. |
| Composite dependencies | Saturn onboarding/whitelist, compliance controls, `$M` backing, USDC redemption route, and DEX liquidity | Parent oracle research [R3, local research, 2026-06-04, medium] |
| Market-vs-NAV mismatch | Curve price was close to $1 in the saved snapshot, but this is not proof of issuer redemption availability; market, issuer peg, and practical exit value can diverge | Market data plus parent analysis [M1/R3, market_data/local research, 2026-06-04, medium] |
| Gearbox-specific oracle notes | Parent artifacts did not identify an active Gearbox main/reserve oracle configuration for this exact token | Parent artifacts [R1/R2/R3, local research, 2026-06-04, medium]. `missing_behavior: review_required` if used as Credit Account collateral. |

Pricing missing-data behavior: for explanation-only context, the issuer peg and point-in-time market data can be described with caveats. For collateral valuation, ranking, Health Factor reasoning, liquidation, or execution, unresolved oracle methodology, reserve/NAV freshness, compliance state, and route depth require human review; stale or missing route/restriction data blocks automation [METH/R3, mixed, 2026-06-04, medium-high].

## 10. Governance / change-feed watchlist

Track these fields before reusing this dossier for live reasoning:

| Watch item | Why it matters | Source / missing behavior |
|---|---|---|
| ProxyAdmin owner and USDat implementation | Direct upgrade path can change token semantics, transfer controls, or admin surface | Onchain/admin artifact [R1/O2/O3, onchain/local research, 2026-06-04, high]. `review_required` before live use. |
| USDat `DEFAULT_ADMIN_ROLE` holders and pending revocation of the EOA path | Role execution speed may change after pending timelock operations; the snapshot was not proof of execution | Onchain/admin artifact [R1/O2/O4, onchain/local research, 2026-06-04, high]. `review_required`. |
| SaturnTimelock and AssetCapTimelock scheduled operations | Timelock queue can alter admin speed and asset-cap state | Onchain/admin artifact [R1/O2/O4, onchain/local research, 2026-06-04, medium-high]. `review_required`. |
| Compliance EOA role changes and pause/freeze/forced-transfer/whitelist events | These can directly affect holder transferability and redemption access | Onchain/source role state [R1/R3/O2/O3, onchain/local research, 2026-06-04, high]. `review_required` for holder-specific checks. |
| `isWhitelistEnabled` and per-account whitelist/freeze state | USDat is permissioned; account-specific ability to hold/redeem/transfer matters | Onchain/source role state [R1/R3/O2/O3, onchain/local research, 2026-06-04, high]. `block_automation` for live actions without refresh. |
| `$M` reserve/custody/redemption state and Saturn transparency updates | Backing quality and redemption confidence depend on the named backing asset and reserve evidence | Saturn docs/transparency page [D1/D2/R2, issuer_docs/local research, 2026-06-04, medium]. `review_required`. |
| DEX route liquidity and USDat/USDC market price | Static market data is not executable and can drift with size/stress | Dexscreener snapshot [M1/R3, market_data/local research, 2026-06-04, medium]. `block_automation` until fresh quote/Preview. |
| Audit/report scope updates and incident/postmortem publications | Report existence does not prove exact deployed-scope coverage; incident absence was bounded | Transparency page and parent security pass [D2/R2, issuer_docs/local research, 2026-06-04, medium]. `review_required`. |
| Gearbox support/oracle status if introduced | Parent artifacts did not identify a Gearbox-specific oracle or support state for this exact token | Parent artifacts [R1/R2/R3, local research, 2026-06-04, medium]. `review_required` if used as Credit Account collateral. |

## 11. Data quality and missing-data behavior

| Material field | Current data quality | missing_behavior |
|---|---|---|
| Token identity, decimals, paused state, whitelist state | High-confidence direct RPC + Etherscan/source evidence [R1/O1/O2/O3, onchain, 2026-06-04, high] | `continue` for descriptive context |
| Proxy / implementation / role state | High-confidence snapshot evidence for current state at the extraction block [R1/O2/O3, onchain, 2026-06-04, high] | `continue` for snapshot description; `review_required` for live classification after pending operations |
| EOA human/entity identity and operating policy | Not verified from a primary Saturn governance/ops document [R1/R2, local research, 2026-06-04, medium] | `review_required` |
| Safe owners / thresholds | No Safe multisig role holder identified onchain; offchain control arrangements unknown [R1, local research, 2026-06-04, medium-high] | `continue` for onchain role description; `review_required` if operational custody policy is required |
| Saturn legal/onboarding/whitelist policy | Product docs say onboarding is required; full legal terms and user-specific eligibility were not independently mapped [D1/R2/R3, issuer_docs/local research, 2026-06-04, medium] | `review_required`; `block_automation` for live user action without eligibility proof |
| `$M` reserve/custody/redemption details | Saturn docs identify `$M` backing, but independent M0 reserve/custody/redemption analysis was not completed [D1/R2, issuer_docs/local research, 2026-06-04, medium] | `review_required` |
| Reserve/NAV proof cadence | Transparency page located; automated reserve/NAV reconciliation not built [D2/R2/R3, issuer_docs/local research, 2026-06-04, medium] | `review_required` |
| Audit/formal-verification scope | Reports listed by Saturn; exact deployed-scope and unresolved issues were not matched [D2/R2, issuer_docs/local research, 2026-06-04, medium] | `review_required` |
| Incident history | No confirmed incident found in bounded sources; absence is not proof of none [R2, local research, 2026-06-04, medium] | `continue` for explanation; `review_required` for production acceptance |
| Token-native oracle methodology | No token-native price oracle found; issuer peg and market data are external to token source [R3/R1, local/onchain research, 2026-06-04, medium-high] | `review_required` for collateral/oracle use |
| Live executable liquidity / slippage | Saved Dexscreener snapshot exists; no route quote for a specific size [M1/R3, market_data/local research, 2026-06-04, medium] | `block_automation` until live quote / Preview |
| Ranking / position-fit decision | Out of scope for this dossier by methodology and task body | `cannot_rank_cleanly` without mandate, position context, live state, and missing-field resolution [METH, methodology, 2026-06-04, high] |

## 12. Highest-impact unknowns

1. Independent M0 `$M` reserve, custody, legal, and redemption details were not expanded beyond Saturn's own USDat overview; `missing_behavior: review_required` because USDat backing quality depends on the named backing asset [D1/R2, issuer_docs/local research, 2026-06-04, medium].
2. Saturn onboarding/legal eligibility, per-holder whitelist state, freeze state, and redemption access were not tested for any actual holder; `missing_behavior: review_required`, and `block_automation` for state-changing live use without eligibility and restriction refresh [D1/R1/R3/O2/O3, mixed, 2026-06-04, medium-high].
3. Audit and formal-verification report scopes were not matched to the current USDat implementation, ProxyAdmin owner, timelock state, inherited components, and current role holders; `missing_behavior: review_required` before treating audit listings as deployed-scope assurance [D2/R2/R1, mixed, 2026-06-04, medium-high].
4. Admin execution speed was in transition: a pending timelock migration was observed but not proven executed, and the ProxyAdmin-owner EOA path remained immediate in the snapshot; `missing_behavior: review_required` for live governance/control classification [R1/O2/O4, onchain/local research, 2026-06-04, high].
5. Token-native oracle methodology was not found, and issuer peg / reserve evidence / DEX market price can diverge from practical exit value; `missing_behavior: review_required` for collateral valuation and `block_automation` for live exits without a route quote [R3/M1/METH, mixed, 2026-06-04, medium-high].
6. No comprehensive incident assurance was completed; no incident was found in bounded sources, but this is not proof of no exploit, reserve event, freeze event, redemption delay, or emergency action; `missing_behavior: continue` for description and `review_required` for acceptance workflows [R2, local research, 2026-06-04, medium].

## 13. Sources

| ID | URL / local evidence | source_class | Accessed | Confidence | Notes |
|---|---|---|---|---|---|
| METH | [methodology.md](../methodology.md) | unknown | 2026-06-04 | high | Project-specific asset mining pipeline, section requirements, labels, and missing-data behavior. |
| REQ | [requirements-brief.md](../requirements-brief.md) | unknown | 2026-06-04 | high | Analyst readability requirements and no-recommendation/style constraints. |
| R1 | [research/eth-mainnet-usdat/onchain-admin.md](../research/eth-mainnet-usdat/onchain-admin.md) | onchain | 2026-06-04 | high | Parent onchain/admin research; summarizes exact-token RPC/source/role/timelock evidence. |
| R2 | [research/eth-mainnet-usdat/issuer-backing-security.md](../research/eth-mainnet-usdat/issuer-backing-security.md) | mixed issuer_docs/onchain/audit | 2026-06-04 | medium-high | Parent issuer/backing/security synthesis. |
| R3 | [research/eth-mainnet-usdat/transfer-liquidity-oracle-governance.md](../research/eth-mainnet-usdat/transfer-liquidity-oracle-governance.md) | mixed onchain/issuer_docs/market_data | 2026-06-04 | medium-high | Parent transfer/liquidity/oracle/governance synthesis. |
| O1 | [etherscan.io/address/0x23238F20B894f29041f48d88Ee91131c395aAA71](https://etherscan.io/address/0x23238F20B894f29041f48d88Ee91131c395aAA71) | onchain | 2026-06-04 | high | USDat Etherscan address/token/proxy/source page. |
| O2 | [ethereum-rpc.publicnode.com](https://ethereum-rpc.publicnode.com) and [raw/usdat-onchain-admin-snapshot-2026-06-04.json](../research/eth-mainnet-usdat/raw/usdat-onchain-admin-snapshot-2026-06-04.json) | onchain | 2026-06-04 | high | Direct RPC snapshot at block `25245745`: identity, proxy slots, role checks, timelock state, ProxyAdmin owner. |
| O3 | [raw/source/](../research/eth-mainnet-usdat/raw/source/) | onchain | 2026-06-04 | high | Local verified source extracts for USDat implementation, Freezable, ForcedTransferable, Pausable, and ProxyAdmin mechanics. |
| O4 | [etherscan.io/address/0xfD5782E3BFF366601da3973aE30C583dE4F08A67](https://etherscan.io/address/0xfD5782E3BFF366601da3973aE30C583dE4F08A67) | onchain | 2026-06-04 | high | Saturn timelock source/role/delay evidence referenced by parent artifact. |
| D1 | [saturncredit.gitbook.io/saturn-docs/solution/usdat-overview](https://saturncredit.gitbook.io/saturn-docs/solution/usdat-overview) | issuer_docs | 2026-06-04 | medium | USDat overview: fully collateralized stablecoin, `$M` backing, permissioned access, mint/redeem framing, non-yielding USDat holder model. |
| D2 | [saturncredit.gitbook.io/saturn-docs/operations-and-governance/transparency-and-audits](https://saturncredit.gitbook.io/saturn-docs/operations-and-governance/transparency-and-audits) | issuer_docs | 2026-06-04 | medium | Transparency/audit page: USDat capital statement and listed Certora/Three Sigma reports. |
| M1 | [raw/dexscreener-usdat-2026-06-04.json](../research/eth-mainnet-usdat/raw/dexscreener-usdat-2026-06-04.json) | market_data | 2026-06-04 | medium | Saved DEXScreener API snapshot for USDat/USDC venues, price, liquidity, and 24h volume. |
