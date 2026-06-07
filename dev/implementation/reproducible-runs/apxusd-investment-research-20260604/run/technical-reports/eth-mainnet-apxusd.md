# apyx apxUSD — MVP asset risk dossier

Report date: 2026-06-04 UTC
Analyst: Hermes kanban synthesis worker
Display: apyx apxUSD
Chain: Ethereum mainnet (`chain_id: 1`)
Token address: `0x98A878b1Cd98131B271883B390f68D2c90674665`
Symbol: `apxUSD`
Intended use: unknown

This dossier is an objective, source-linked asset context artifact. It does not advise asset selection, position sizing, position fit, suitability, or execution.

Citation format: inline source IDs resolve in Section 13 to a URL or local evidence path, source class, access date, and confidence. Material missing fields include `missing_behavior` from the project methodology.

Synthesis inputs read before drafting:

- [methodology.md](../methodology.md)
- [requirements-brief.md](../requirements-brief.md)
- [research/eth-mainnet-apxusd/onchain-admin.md](../research/eth-mainnet-apxusd/onchain-admin.md)
- [research/eth-mainnet-apxusd/issuer-backing-security.md](../research/eth-mainnet-apxusd/issuer-backing-security.md)
- [research/eth-mainnet-apxusd/transfer-liquidity-oracle-governance.md](../research/eth-mainnet-apxusd/transfer-liquidity-oracle-governance.md)

## 1. Agent-context summary

apxUSD is an Ethereum-mainnet Apyx synthetic-dollar token at `0x98A878b1Cd98131B271883B390f68D2c90674665`; direct on-chain reads returned `name="apxUSD"`, `symbol="apxUSD"`, 18 decimals, `paused=false`, a 750,000,000 apxUSD supply cap, and about 466.229m apxUSD total supply at block `25245413` [R1][O1]. The token is an ERC-1967/UUPS upgradeable ERC-20 with permit, burn, pause, deny-list, AccessManager-controlled mint/admin functions, and a current implementation at `0xdd71fd677fde2ed2579a3c45204f41a11016ccb4` [R1][O1][O2]. Official Apyx materials describe apxUSD as a synthetic dollar backed by a diversified basket of low-volatility, variable-rate preferred shares issued by Digital Asset Treasuries, with eligible whitelisted participants able to mint and redeem through designated pathways while general users use external liquidity pools [R2][R3][D1].

The main operational risk surface is not ordinary ERC-20 market risk alone. Existing-holder-relevant controls include immediate pause, deny-list replacement, minting via MinterV0 and AccessManager, supply-cap changes, UUPS upgrades, authority rotation, CCIP admin rotation, and pending Safe / AccessManager change-feed risk [R1][O2][O3][O4][G1]. Backing assurance remains incomplete because the parent artifacts identified transparency dashboards and Wolf & Company attestation links but did not reconcile current dashboard or attestation contents to on-chain supply, preferred-share issuer concentration, custody, or current collateral composition [R2][D3][D4]. Liquidity evidence is point-in-time: DEXScreener showed meaningful Curve / Uniswap / PancakeSwap apxUSD-USDC venues, but the largest Curve venue was around `$0.9716` while another Uniswap v4 venue was around `$0.9999` at extraction [R3][M1]. Any downstream use must refresh route, pause, deny-list, eligibility, backing, and governance state rather than treating this dossier as live execution evidence [METH][R3].

## 2. One-paragraph mechanism

apxUSD is Apyx's base synthetic-dollar ERC-20: Apyx docs state that eligible whitelisted participants in permitted jurisdictions can mint and redeem apxUSD through designated issuance/redemption pathways, redemption settles in USDC, and the protocol may liquidate preferred-share collateral to USDC rather than transferring preferred shares directly to redeeming participants [R2][R3][D1]. General users are described as acquiring apxUSD through external liquidity pools and swaps rather than primary mint/redeem access [R2][R3][D1]. The live token contract adds issuer-control mechanics around that economic model: AccessManager roles control minting through MinterV0, supply cap, pause, deny-list, upgrades, and authority changes [R1][O2][O3][O4]. Practical value therefore combines issuer NAV/backing quality, primary-redemption eligibility, admin/control state, and executable secondary-market routes [R2][R3][M1].

## 3. Identity and token semantics

| Field | Current dossier value | Evidence |
|---|---|---|
| Canonical chain | Ethereum mainnet, `chain_id: 1` | Task scope and direct RPC snapshot [R1][O1]. |
| Token / proxy address | `0x98A878b1Cd98131B271883B390f68D2c90674665` | Task scope and direct RPC snapshot [R1][O1]. |
| Name / symbol / decimals | `apxUSD` / `apxUSD` / `18` | Direct `name()`, `symbol()`, `decimals()` reads [R1][O1]. |
| Current implementation | `0xdd71fd677fde2ed2579a3c45204f41a11016ccb4` | EIP-1967 implementation slot and UUPS `proxiableUUID` check [R1][O1]. |
| Proxy type | ERC-1967 proxy with UUPS implementation; EIP-1967 admin and beacon slots zero | Direct storage reads and implementation check [R1][O1]. |
| Authority / AccessManager | `0xe167330E2Eac88666de253e9607C6d9ae0cA2824` | Parent on-chain role snapshot [R1][O1]. |
| Paused state in snapshot | `false` | Direct `paused()` read [R1][O1]. |
| Deny-list contract in snapshot | `0x2c271ddF484aC0386d216eB7eB9Ff02D4Dc0F6AA` | Direct `denyList()` read [R1][O1]. |
| Supply cap | `750,000,000 apxUSD` | Direct `supplyCap()` read [R1][O1]. |
| Total supply | About `466,229,030.895898820992229055 apxUSD` at block `25245413` | Direct `totalSupply()` read [R1][O1]. |
| Remaining cap | About `283,770,969.104101179007770945 apxUSD` | Direct `supplyCapRemaining()` read [R1][O1]. |
| Token standard / source behavior | ERC-20, ERC-20Permit, pausable, deny-list-gated, burnable, AccessManaged, UUPS-upgradeable | Verified source inheritance and source comments [R1][O2][O4]. |
| Asset type | Issuer-controlled synthetic-dollar stablecoin backed by off-chain preferred-share / DAT exposure | Apyx docs and source comments [R1][R2][D1][C1]. |
| Token behavior | Non-rebasing ERC-20 with supply cap, permit, burn path, pause and deny-list gates | Direct source and snapshot [R1][O1][O2][O4]. |
| Transition-stage behavior | apxUSD is the underlying for apyUSD and can become an intermediate asset in wrapper / receipt flows; apxUSD itself did not show a separate claim token in parent apxUSD source review | apyUSD docs relationship and apxUSD source review [R1][R2][R3][D2]. |

Missing-data behavior: identity and proxy facts are high-confidence for the sampled date and can be used for descriptive reasoning. Any changed implementation, AccessManager, deny-list, pause state, supply cap, or MinterV0 state has `missing_behavior: review_required` before reuse [METH][R1].

## 4. Issuer / protocol and business model

Apyx is the issuer/protocol context named by the official Apyx documentation and public contracts README for apxUSD and apyUSD [R2][D1][D2][C1]. Apyx docs describe apxUSD as a synthetic dollar backed by preferred shares issued by Digital Asset Treasuries; the docs frame apxUSD as collateral / quote asset infrastructure while apyUSD is the savings asset that receives rewards from the collateral stack [R2][D1][D2]. The public contracts README describes Apyx as a dividend-backed stablecoin protocol transforming DAT preferred equity into programmable digital dollars, with apxUSD as the base stablecoin and apyUSD as the yield-bearing wrapper [R2][C1].

| Topic | Facts | Source / missing behavior |
|---|---|---|
| Issuer / protocol | Apyx / APYX Protocol context in official docs and public contracts README | Issuer docs / contract README [R2][D1][D2][C1], confidence medium. |
| One-paragraph mechanism | Synthetic-dollar apxUSD backed by preferred-share collateral; primary mint/redeem path for eligible whitelisted participants; external liquidity pools for general users | Official apxUSD overview [R2][R3][D1], confidence medium. |
| Revenue / yield source | Preferred-share dividends are described as the economic source for the broader collateral stack; apxUSD itself is the base synthetic dollar, while apyUSD is the savings wrapper that surfaces yield | Official docs and contracts README [R2][D1][D2][C1], confidence medium. |
| Off-chain dependencies | DAT preferred-share issuers, custodian/attestation processes, collateral valuation, liquidity of preferred shares, eligible redemption operations, and Apyx operational execution | Transparency and attestation docs [R2][D3][D4], confidence medium; reserve details remain `review_required`. |
| Contract dependencies | ApxUSD proxy/implementation, AccessManager `0xe167...2824`, MinterV0 `0x2c36...a76e`, deny-list `0x2c271d...F6AA`, Safe-like role holders, CCIP/token-admin configuration | On-chain snapshot and verified source [R1][O1][O2][O3][O4], confidence high for sampled state. |
| Mint controls | Token `mint(address,uint256,uint256)` is AccessManager role `4`, with MinterV0 as callable candidate and a 4-hour observed token mint delay; MinterV0 validates signed orders, nonces, max mint amount, and 24-hour rate limit | On-chain snapshot and MinterV0 source [R1][O1][O3], confidence high for sampled state. |
| Direct redemption access | Docs say eligible participants in permitted jurisdictions who are whitelisted, such as institutional market makers, may mint and redeem; redemptions settle in USDC and holders do not receive preferred shares directly | Official apxUSD docs [R2][R3][D1], confidence medium; user-specific eligibility is `review_required`. |
| General user access | Docs say general users can acquire apxUSD through permissionless external liquidity pools and swaps | Official apxUSD docs [R2][R3][D1], confidence medium; real exit is `block_automation` without fresh route quote. |

## 5. Backing, NAV, and exposure map

`nav_model: issuer NAV / off-chain preferred-share collateral / overcollateralized synthetic dollar`

| Field | Current facts | Source / missing behavior |
|---|---|---|
| Reserve / underlying assets | Official docs describe apxUSD as backed by a basket of low-volatility, variable-rate preferred shares issued by DATs | Issuer docs [R2][D1], confidence medium. |
| Collateral allocation | Apyx docs state the basket is dynamically allocated across DAT preferred shares, with rebalancing subject to issuer concentration, liquidity requirements, and coverage requirements intended to keep apxUSD overcollateralized | Issuer docs [R2][D1], confidence medium. |
| Custody / transparency model | Official docs reference Accountable near-real-time visibility, an Apyx dashboard, a Dune dashboard, and custodian attestations | Transparency docs [R2][D3], confidence medium for source existence; current dashboard data was not reconciled. |
| Reserve / attestation reports | Official docs list Wolf & Company March and April 2026 attestation opinions and state custodians provide monthly attestations on backing existence, custody control, and valuation | Attestation docs [R2][D4], confidence medium for listed links; low for reserve conclusions because PDFs were not parsed/reconciled. |
| Update cadence | Monthly Wolf & Company reports were listed for March/April 2026; machine-readable live NAV cadence was not established in the parent artifacts | Attestation and transparency docs [R2][D3][D4], `missing_behavior: review_required`. |
| Redemption mechanism | Eligible whitelisted participants redeem for USDC; in drawdown scenarios the protocol liquidates preferred shares to USDC and does not transfer preferred shares directly | apxUSD docs [R2][R3][D1], confidence medium. |
| Primary redemption access restrictions | Eligible / whitelisted / permitted-jurisdiction participants for primary paths; general users rely on external pools | apxUSD docs [R2][R3][D1], `missing_behavior: review_required` for a specific holder. |
| Known haircut / basis / collateral exposure | Preferred-share credit/dividend/valuation quality, issuer concentration, custody, preferred-share liquidation timing, USDC settlement path, and secondary-market discount | Synthesis from issuer and liquidity artifacts [R2][R3][D1][D3][D4][M1]. |
| NAV vs secondary market | NAV/backing/redemption value can diverge from DEX price; saved DEXScreener venues showed different apxUSD-USDC prices, including a top Curve pair below `$1` | Market artifact and raw market data [R3][M1]. |
| Dependency on another token / oracle | apxUSD itself has no token-native price oracle in reviewed source; value depends on issuer NAV/backing, primary redemption eligibility, and external market routes | Source review and pricing artifact [R3][O2][M1]. |

Missing-data behavior for backing/NAV: current collateral composition, custodian identities/details, preferred-share issuer concentration, attestation PDF contents, dashboard values, and supply reconciliation were not independently expanded in parent artifacts. For explanation-only use, unknown fields can continue with labels. For clean comparative scoring they create `missing_behavior: cannot_rank_cleanly`; for production collateral valuation they are `review_required`; for real exit execution they are `block_automation` until live route, eligibility, and issuer-state checks are refreshed [METH][R2][R3].

## 6. Contract admin, multisigs, and sensitive actions

### 6.1 Proxy / implementation / upgradeability

| Surface | Current finding | Source-linked status |
|---|---|---|
| Token / proxy | `0x98A878b1Cd98131B271883B390f68D2c90674665` | Direct RPC and task scope [R1][O1]. |
| Current implementation | `0xdd71fd677fde2ed2579a3c45204f41a11016ccb4` | EIP-1967 implementation slot [R1][O1]. |
| Proxy admin / beacon | EIP-1967 admin and beacon slots zero | Direct storage reads [R1][O1]. |
| Upgrade pattern | UUPS; implementation `proxiableUUID` returned the ERC-1967 implementation slot | Direct implementation check and verified source [R1][O1][O2]. |
| Upgrade authorization | `ApxUSD._authorizeUpgrade` is AccessManager-restricted | Verified source [R1][O2]. |
| Current upgrade executor path | AccessManager role `24`, Safe-like `0xf986...3CE2`, observed 259,200 second / 3-day delay | Role snapshot [R1][O1]. |

### 6.2 Current role holders and holder types

| Role / authority | Current holder(s) | Holder type | Sensitive powers observed in parent artifacts | Source / confidence |
|---|---|---|---|---|
| AccessManager `ADMIN_ROLE` / role `0` | `0xabdd8c8ee69e5F5180EB9352AeFFc5CeEAd65e96` | Safe-like contract, 4-of-6 owners | AccessManager admin role; `cleanMintHistory` on MinterV0; likely role/target configuration surface | [R1][O1], high for role holder, medium for full admin surface. |
| Role `2` | `0xf9862EfC1704aC05e687f66E5cD8c130E5663CE2` | Safe-like contract, 3-of-6 owners | `requestMint`, `executeMint` on MinterV0 with zero observed delay | [R1][O1][O3], high. |
| Role `4` | MinterV0 `0x2c36e1adfaa80ee0324b04cc814f5207bb7ba76e` | Contract | Token `mint(address,uint256,uint256)` with 4-hour observed delay | [R1][O1][O3], high. |
| Role `21` | `0xf986...3CE2` | Safe-like 3-of-6 | `pause()` on apxUSD and MinterV0 with zero observed delay | [R1][O1], high. |
| Role `22` | `0xf986...3CE2` | Safe-like 3-of-6 | `unpause()` with 4-hour observed delay | [R1][O1], high. |
| Role `23` | `0xf986...3CE2` | Safe-like 3-of-6 | `setSupplyCap`, `setDenyList`, `setMaxMintAmount` with 1-day observed delay | [R1][O1][O2][O3], high. |
| Role `24` | `0xf986...3CE2` | Safe-like 3-of-6 | `upgradeToAndCall`, `setRateLimit` with 3-day observed delay | [R1][O1][O2][O3], high. |
| Role `25` | `0xf986...3CE2` | Safe-like 3-of-6 | `setCCIPAdmin`, `setAuthority` with 7-day observed delay | [R1][O1][O2], high. |
| Role `31` | `0xf986...3CE2` | Safe-like 3-of-6 | `cancelMint` guardian with zero observed delay | [R1][O1][O3], high. |

Safe-like holder details in the parent snapshot: `0xabdd...5e96` returned threshold `4` with six owners, and `0xf986...3CE2` returned threshold `3` with six owners [R1][O1]. Safe module, guard, fallback-handler, operational policy, and all pending payloads were not fully decoded; `missing_behavior: review_required` before relying on effective Safe execution semantics [R1][G1].

### 6.3 Sensitive action classification

| Sensitive action | Current authorized path | Holder type | existing_holder_impact | execution_speed | Evidence / missing behavior |
|---|---|---|---|---|---|
| Pause apxUSD | Role `21` / Safe-like `0xf986...3CE2` | 3-of-6 Safe-like | `direct_freeze` and transfer/mint/burn block while paused | `immediate` | Pausable source and role delay [R1][O1][O2]. |
| Unpause apxUSD | Role `22` / Safe-like `0xf986...3CE2` | 3-of-6 Safe-like | unblocks paused flows | `timelocked` / 4 hours | Role snapshot [R1][O1]. |
| Replace deny-list | Role `23` / Safe-like `0xf986...3CE2` | 3-of-6 Safe-like | `direct_freeze` / possible `direct_redemption_block` depending registry contents | `timelocked` / 1 day | Deny-list source and role snapshot [R1][O1][O2][O4]. |
| Mint apxUSD | MinterV0 signed-order flow plus token role `4` | Contract + Safe-like role holders | `direct_dilution` if issuance is not backed; otherwise supply expansion | `timelocked` / token mint 4 hours; request/execute roles zero-delay in snapshot | [R1][O1][O3]. |
| Raise/lower supply cap | Role `23` | 3-of-6 Safe-like | `indirect`, changes future issuance capacity | `timelocked` / 1 day | [R1][O1][O2]. |
| Upgrade implementation | Role `24` | 3-of-6 Safe-like | `unknown`, because implementation can change token semantics | `timelocked` / 3 days | [R1][O1][O2]. |
| Rotate AccessManager authority | Role `25` | 3-of-6 Safe-like | `unknown`, can replace the core permission manager | `timelocked` / 7 days | [R1][O1][O2]. |
| Rotate CCIP admin | Role `25` | 3-of-6 Safe-like | `indirect` through cross-chain/token-admin integration | `timelocked` / 7 days | [R1][O1][O2]. |
| Cancel mint | Role `31` | 3-of-6 Safe-like | `none` for existing holders; prevents issuance | `immediate` | [R1][O1][O3]. |
| Burn by ordinary holders | ERC20Burnable path | Token holders / allowances | `none` for voluntary holder burn | Ordinary ERC-20 action | No special seizure in `ApxUSD.sol` [R1][O2]. |
| General forced transfer | None identified in `ApxUSD.sol` parent review | n/a | n/a | n/a | Deny-list can block transfers; no USDat-style forced-transfer function identified [R1][O2][O4]. |
| Governance vote | No DAO governor role holder identified in parent artifacts | unknown | `unknown` | `unknown` | `missing_behavior: review_required` if governance process matters [R1]. |

### 6.4 Pending Safe / governance feed caveat

The parent Safe Transaction Service snapshot returned unexecuted transactions for `0xabdd...5e96`, including a pending transaction to the apxUSD token and a large pending multisend setting AccessManager function roles [R1][G1]. The bounded research did not fully decode every pending payload or determine execution likelihood. Any production action package must refresh Safe Transaction Service, decode pending payloads, and compare AccessManager function-role assignments to this dossier before relying on the snapshot. `missing_behavior: review_required`; unresolved pending admin changes before a state-changing action imply `missing_behavior: block_automation` [METH][R1][G1].

## 7. Audits, formal verification, and incidents

| Item | Facts found | Source / confidence |
|---|---|---|
| Quantstamp reports | Official Apyx docs list Quantstamp reports dated 2026-02 and 2026-04 | Audit docs [R2][D5], confidence medium for existence. |
| Certora report | Official Apyx docs list a Certora 2026-03 report; Certora's public summary page for Apyx apxUSD/apyUSD says the March 2, 2026 manual code review found 11 issues including one high-severity issue, and says the high issue was fixed and confirmed | Audit docs and Certora summary [R2][D5][D6], confidence medium. |
| Zellic report | Official Apyx docs list a Zellic 2026-03 report | Audit docs [R2][D5], confidence medium for existence. |
| Audit-scope match | Parent artifacts did not download/read every audit PDF body end-to-end or map report scope to current implementation `0xdd71...ccb4`, AccessManager roles, MinterV0, deny-list, pending Safe transactions, or collateral/custody process | Parent caveat [R2], `missing_behavior: review_required`. |
| Formal verification details | Certora security work is listed, but formal rules, verified invariants, and deployed-scope match were not fully extracted in parent artifacts | [R2][D5][D6], `missing_behavior: review_required`. |
| Bug bounty | No bug-bounty program and scope was established in the parent artifacts | Parent security section [R2], `missing_behavior: continue` for description and `review_required` for security acceptance. |
| Incident history | No confirmed public exploit, depeg/freeze/redemption-delay postmortem for the exact apxUSD token was identified in bounded parent sources | Parent incident pass [R2], confidence low/medium; absence of found incident is not proof of no incident. |
| Market discount signal | DEXScreener market data showed some apxUSD venues below `$1`, including a top Curve pair around `$0.9716`; this is a market-exit signal, not itself an incident conclusion | Transfer/liquidity artifact and market snapshot [R2][R3][M1]. |

Missing-data behavior: audit bodies, formal-scope mapping, incident history, bug-bounty scope, and deployed-bytecode mapping are `review_required`. No confirmed incident found in bounded sources has `missing_behavior: continue` only for explanation and does not clear acceptance or production review [METH][R2].

## 8. Transferability, redemption, and liquidity

### 8.1 Transfer restrictions and eligibility

apxUSD has ordinary ERC-20 transfer methods, but transferability is pause- and deny-list-sensitive. `ApxUSD.sol` includes `ERC20PausableUpgradeable` and `ERC20DenyListUpgradable`; the deny-list extension checks both sender and receiver before token updates [R1][R3][O2][O4]. The on-chain snapshot read `paused=false` and active `denyList=0x2c271ddF484aC0386d216eB7eB9Ff02D4Dc0F6AA` [R1][R3][O1].

Primary issuance/redemption is not described as universally open. Official docs say eligible participants in permitted jurisdictions who are whitelisted may mint and redeem apxUSD through designated pathways, while general users can use external liquidity pools and swaps [R2][R3][D1]. Legal/user-specific eligibility was not validated in the parent artifacts; `missing_behavior: review_required` for primary mint/redeem access and `block_automation` for any real redemption or exit action without live user/process checks [METH][R3].

### 8.2 Freeze, blacklist, forced-transfer, and registry mechanics

The active restriction primitive found in the apxUSD source is the shared deny-list registry plus global pause, not a general forced-transfer role [R1][R3][O2][O4]. `setDenyList(address)` is controlled through AccessManager role `23`, with Safe-like `0xf986...3CE2` and an observed 86,400 second / 1-day delay [R1][O1]. The parent source review did not identify a general forced-transfer or seizure function in `ApxUSD.sol`; ordinary burn is holder/allowance-based through ERC20Burnable [R1][O2]. Deny-list administration and currently denied accounts were not fully enumerated; `missing_behavior: review_required` before compliance-action automation or user-specific transferability assumptions [METH][R3].

### 8.3 Primary redemption path and settlement process

Official docs say eligible whitelisted participants may redeem apxUSD through designated pathways, with redemption settling in USDC; holders do not receive preferred shares directly [R2][R3][D1]. In drawdown scenarios, protocol collateral may be liquidated from preferred shares to USDC to facilitate redemption [R2][D1]. The docs say mint/redemption requests are processed quickly and note liquidity may be more limited outside traditional trading hours and weekends, though a buffer remains available; parent artifacts did not verify a live primary redemption SLA or quote [R3][D1]. General users may be limited to external liquidity pools [R2][R3][D1].

Field record:

| Field | Current facts | missing_behavior |
|---|---|---|
| primary_redemption_path | Whitelisted/eligible participant redemption pathway settling in USDC; general users rely on external pools | `review_required` for exact eligibility/SLA; `block_automation` for real exits without Preview. |
| cooldown_queue_settlement | Docs say requests are processed quickly; no live SLA, queue, or quote was validated in parent artifacts | `review_required`. |
| claim_token_receipt | None identified for apxUSD itself; apyUSD wrapper has separate receipt mechanics | `continue` for apxUSD explanation; `review_required` if wrapper/transition flow is involved. |
| claim_readiness | Depends on eligibility, deny-list/pause state, issuer liquidity buffer, and live redemption pathway | `review_required`; `block_automation` for a state-changing exit. |

### 8.4 Secondary liquidity venues and size-dependent exit caveats

Saved DEXScreener data for apxUSD and related Apyx venues was point-in-time market data, not executable quotes [R3][M1]. Relevant venues from the parent artifact included:

| Chain | DEX | Pair / address | priceUsd at extraction | liquidity_usd at extraction | volume_24h_usd at extraction | Evidence |
|---|---|---|---:|---:|---:|---|
| Ethereum | Curve | `0xE1B96555BbecA40E583BbB41a11C68Ca4706A414` apxUSD/USDC | `0.9716` | `38,260,350.97` | `57,481,401.95` | [R3][M1]. |
| Ethereum | Uniswap v4 | pool id `0x2480...63b1` apxUSD/USDC | `0.9999` | `10,995,035.91` | `522,474.55` | [R3][M1]. |
| Ethereum | PancakeSwap v3 | `0x1D8177897FC90819CF644fa84B3247AC690985D5` apxUSD/USDC | `0.9944` | `2,987,692.46` | `222,990.77` | [R3][M1]. |
| Ethereum | Curve | `0xe41be7B340f7c2EDA4DA1e99b42Ee1b228b526b7` apyUSD/apxUSD | apyUSD leg price in apxUSD | `14,261,672.19` | `21,185,031.44` | [R3][M1]. |

Liquidity caveats: the API values are current only at extraction, venue prices differed materially, and primary redemption eligibility may be necessary to arbitrage or exit near NAV [R3][M1]. Live position-specific exit analysis has `missing_behavior: block_automation` until route quote, size, recipient eligibility, pause/deny-list state, and pending governance state are refreshed [METH][R3]. Longer historical depeg/premium/discount behavior was not established; `missing_behavior: review_required` [R3].

## 9. Oracle and pricing methodology

apxUSD's token source does not expose a holder-facing Chainlink-style price feed or token-native NAV oracle in the reviewed source; it implements token/admin/mint/deny-list controls [R3][O2]. Official docs describe a peg/backing model based on preferred-share collateral, overcollateralized issuance, cross-market arbitrage by Apyx and eligible whitelisted users, derivative-based tail hedging, and USDC primary redemption for eligible participants [R2][R3][D1].

| Field | Current facts | Source / missing behavior |
|---|---|---|
| primary_price_source | Issuer NAV/redeemability plus external market price; no token-native price oracle found in apxUSD source | Issuer docs, source review, market data [R3][O2][D1][M1], confidence medium. |
| oracle_follows | Backing/NAV/redemption assumptions and DEX market prices, not automatic token contract accounting | [R3][D1][M1]. |
| update cadence | Unknown for issuer NAV/collateral dashboards in this pass; monthly attestations listed for March/April 2026; on-chain state updates live by RPC | [R2][R3][D3][D4], `missing_behavior: review_required`. |
| staleness window | No feed-style staleness window found in token contract; dashboards/attestations/market data require independent freshness checks | [R3][O2][D3][D4][M1]. |
| composite dependencies | Preferred-share collateral, Accountable/attestation data, primary redemption eligibility, AccessManager/Safe state, DEX liquidity | [R2][R3][D1][D3][D4][G1][M1]. |
| observed market divergence | DEXScreener top Curve apxUSD/USDC price below `$1` at extraction; venue prices differed | [R3][M1], confidence medium/high for API observation. |
| missed risk classes | Market discount, primary-redemption eligibility, deny-list/pause, collateral liquidation timing, custody/reporting, Safe/admin changes | [R2][R3][O1][D1][D3][D4][G1][M1]. |
| Gearbox-specific main/reserve oracle | Not checked or found in parent research | `missing_behavior: review_required` if used as Credit Account collateral [METH][R3]. |

Pricing implication: any Health Factor, collateral valuation, or portfolio display that uses a fixed `$1`, stale NAV, or unrefreshed market price can miss DEX discount, denied-address restrictions, pause state, primary-redemption ineligibility, collateral liquidation delays, and governance/admin changes [R3][METH].

## 10. Governance / change-feed watchlist

Refresh these fields against the last accepted state before production reuse:

1. Token/proxy address remains `0x98A878b1Cd98131B271883B390f68D2c90674665` [R1][O1].
2. EIP-1967 implementation remains `0xdd71fd677fde2ed2579a3c45204f41a11016ccb4`; any UUPS implementation change is material [R1][O1][O2].
3. AccessManager remains `0xe167330E2Eac88666de253e9607C6d9ae0cA2824` [R1][O1].
4. AccessManager role assignments for apxUSD and MinterV0, especially roles `0`, `2`, `4`, `21`, `22`, `23`, `24`, `25`, and `31` [R1][O1].
5. AccessManager target delays and function-role mapping for pause, unpause, setDenyList, setSupplyCap, mint, upgrade, setAuthority, setCCIPAdmin, setMaxMintAmount, setRateLimit, and cancelMint [R1][O1][O2][O3].
6. Safe-like role holder `0xf986...3CE2`: threshold, owners, modules, guard, fallback handler, executed transactions, and pending transactions [R1][G1].
7. AccessManager admin holder `0xabdd...5e96`: threshold, owners, pending transactions, and any role/target reconfiguration payload [R1][G1].
8. Safe Transaction Service pending queue; parent research found unexecuted payloads and did not fully decode them [R1][G1].
9. `paused()` state for apxUSD and MinterV0 [R1][O1][O2][O3].
10. `denyList()` address, deny-list contract administration, and current denied accounts if user-specific flow depends on it [R1][O1][O4].
11. MinterV0 parameters: `maxMintAmount`, `rateLimitAmount`, `rateLimitPeriod`, pending orders, nonce history, and pause state [R1][O3].
12. Supply cap and remaining issuance capacity [R1][O1][O2].
13. Primary redemption eligibility, permitted jurisdictions, liquidity buffer, and operational SLA [R2][R3][D1].
14. Accountable / reserve dashboards, Wolf & Company attestations, DAT issuer concentration, custody, and reserve coverage [R2][D3][D4].
15. DEX route liquidity and venue price divergence across Curve, Uniswap v4, and PancakeSwap v3 [R3][M1].
16. Audit/report scope updates, bug-bounty scope, and any public Apyx incident statement or postmortem [R2][D5][D6].
17. Gearbox-specific support or oracle configuration if this asset is later used as Credit Account collateral [METH][R3].

Missing-data behavior: governance/admin drift is `review_required`; pending role, implementation, minting, oracle/pricing, deny-list, backing, or liquidity changes before a production action imply `missing_behavior: block_automation` until decoded and reflected in a fresh Preview [METH][R1][R3][G1].

## 11. Data quality and missing-data behavior

| Material field | Current data quality | source_class | freshness | confidence | missing_behavior |
|---|---|---|---|---|---|
| Token identity and exact address | Direct RPC snapshot, task scope, verified local source context | onchain | current at sampled date | high | `continue`; `review_required` if implementation/authority changes. |
| Proxy / implementation | ERC-1967/UUPS, implementation `0xdd71...ccb4` | onchain | current at sampled date | high | `review_required` if changed. |
| Token behavior | ERC-20 permit/burn/pausable/deny-list/supply-cap/AccessManager/UUPS | onchain verified source | current source snapshot | medium/high | `continue` for explanation; refresh before use. |
| Issuer / protocol | Apyx, apxUSD as base synthetic dollar, apyUSD as savings wrapper | issuer_docs | current docs at access date | medium | `review_required` for legal/process assumptions. |
| Backing / reserve model | Preferred-share / DAT basket, overcollateralized issuance framework, dashboards and attestations listed | issuer_docs | current docs, dated attestations | medium for existence, low for reserve conclusions | `cannot_rank_cleanly` / `review_required`. |
| Custody / attestation details | Wolf & Company March/April 2026 links listed; custodian attestation process described; PDFs not parsed/reconciled | issuer_docs | dated reports | low/medium | `review_required`. |
| Primary redemption eligibility | Eligible whitelisted participants in permitted jurisdictions; general users via external pools | issuer_docs | current docs at access date | medium | `review_required` for a specific holder; `block_automation` for redemption action. |
| Transfer restriction | Pause and deny-list checks on sender/receiver | onchain + verified source | current sampled state | high | `review_required` for current/user-specific status. |
| Forced transfer / seizure | No general forced-transfer function identified in `ApxUSD.sol` parent review | onchain verified source | bounded review | medium | `continue` for source-scoped statement; `review_required` if broader contract system is expanded. |
| Secondary liquidity | Curve / Uniswap v4 / PancakeSwap apxUSD-USDC and apyUSD-apxUSD venues in saved DEXScreener data | market_data | point-in-time | medium | `block_automation` without fresh route quote. |
| Historical market stress | Point-in-time discount observed; longer history not built | market_data | point-in-time only | low/medium | `review_required`. |
| Oracle / pricing | No token-native price feed found; practical value from issuer NAV/redeemability plus market routes | issuer_docs + onchain + market_data | sampled/current | medium | `review_required` for collateral oracle use. |
| AccessManager / role state | Role mappings, holders, delays, Safe-like thresholds sampled | onchain + governance_api/local | current at sampled date | high for reads, medium for policy | `review_required`; `block_automation` if pending queue not decoded. |
| Pending governance | Safe pending transactions returned, not fully decoded | governance | current at sampled date | medium | `review_required`; `block_automation` for action packages. |
| Audits | Quantstamp, Certora, Zellic listed; Certora summary located | audit + issuer_docs | dated | medium for existence, low for full scope | `review_required`. |
| Incident history | No confirmed exact-token incident found in bounded parent inputs | unknown / market_data | bounded | low | `continue` for explanation; `review_required` for production acceptance. |
| Gearbox support/oracle | Not checked / not found in parent research | unknown | unknown | low | `continue` unless integration depends on it; then `review_required`. |
| Ranking / position-fit decision | Out of scope; requires mandate, position context, live state, and missing-field resolution | methodology | current | high | `cannot_rank_cleanly`; no suitability verdict in this dossier. |

## 12. Highest-impact unknowns

| Unknown / caveat | Why it matters | missing_behavior | Confidence |
|---|---|---|---|
| Current collateral dashboard values, attestation PDFs, custodian details, preferred-share issuer concentration, and reserve composition were not reconciled to on-chain supply | Backing proof and overcollateralization are central to asset quality; source existence is not reserve verification | `cannot_rank_cleanly` and `review_required` | high |
| Primary mint/redeem legal eligibility, whitelist process, permitted jurisdictions, and live redemption SLA were not verified beyond official docs | Primary redemption may be the cleanest NAV path but may be unavailable to a specific holder | `review_required`; `block_automation` for real redemption | high |
| Audit/FV PDF bodies were not fully parsed and mapped to live apxUSD implementation, AccessManager roles, MinterV0, deny-list, and pending Safe state | Audit existence is not deployed-system coverage | `review_required` | high |
| Full AccessManager admin-operation history and pending Safe payloads were not exhaustively decoded | Role delays, callable holders, implementation, minting, and deny-list settings can change materially | `review_required`; `block_automation` for production action packages | high |
| Safe modules, guards, fallback handlers, human/entity identities, and operational policies for Safe-like contracts were not verified | Threshold/owners are known, but effective execution policy may differ | `review_required` | medium/high |
| Deny-list contract administration and current denied-address state were not fully expanded | Transfer, mint, burn, redemption, and route settlement can be holder-specific | `review_required`; `block_automation` for user-specific actions | high |
| No token-native oracle / staleness methodology was found, and off-chain NAV cadence was not machine-reconciled | Collateral value can diverge from market and issuer reports, and stale data can miss depeg or redemption stress | `review_required` | high |
| Live executable slippage for a specific position was not quoted | Market depth is size-dependent and point-in-time API data is not an executable route | `block_automation` | high |
| Longer premium / discount / depeg history and comprehensive incident history were not built | A point-in-time discount was observed, but stress persistence is unknown | `review_required`; incident absence only `continue` for explanation | medium |
| Gearbox-specific support / oracle configuration was not checked in parent research | If used as Credit Account collateral, exact main/reserve oracle and policy state are required | `review_required` for integration | low/medium |

## 13. Sources

| ID | URL / local evidence | source_class | accessed | confidence | Used for |
|---|---|---|---|---|---|
| METH | [methodology.md](../methodology.md) | unknown | 2026-06-04 | high | Project-specific source priority, nine-section pipeline, and `missing_behavior` labels. |
| REQ | [requirements-brief.md](../requirements-brief.md) | requirements | 2026-06-04 | high | Analyst readability structure and style constraints. |
| R1 | [research/eth-mainnet-apxusd/onchain-admin.md](../research/eth-mainnet-apxusd/onchain-admin.md) | onchain | 2026-06-04 | high | Parent onchain/admin research: identity, proxy, roles, delays, Safe-like holders, sensitive actions. |
| R2 | [research/eth-mainnet-apxusd/issuer-backing-security.md](../research/eth-mainnet-apxusd/issuer-backing-security.md) | mixed issuer_docs/onchain/audit | 2026-06-04 | medium/high | Parent issuer/backing/security research: mechanism, backing/NAV, transparency/attestation/audit caveats. |
| R3 | [research/eth-mainnet-apxusd/transfer-liquidity-oracle-governance.md](../research/eth-mainnet-apxusd/transfer-liquidity-oracle-governance.md) | mixed onchain/issuer_docs/market_data/governance | 2026-06-04 | medium/high | Parent transfer/liquidity/oracle/governance research: restrictions, redemption, venues, pricing, watchlist. |
| O1 | [ethereum-rpc.publicnode.com](https://ethereum-rpc.publicnode.com) plus [research/eth-mainnet-apxusd/raw/onchain-admin-snapshot-2026-06-04.json](../research/eth-mainnet-apxusd/raw/onchain-admin-snapshot-2026-06-04.json) | onchain | 2026-06-04 | high | Direct RPC block snapshot for token metadata, proxy slots, AccessManager roles/delays, Safe-like reads, supply cap, total supply, pause/deny-list state. |
| O2 | [research/eth-mainnet-apxusd/raw/evm-contracts/src/ApxUSD.sol](../research/eth-mainnet-apxusd/raw/evm-contracts/src/ApxUSD.sol) | onchain verified source | 2026-06-04 | medium/high | apxUSD source behavior: ERC-20, permit, pausable, deny-list, supply cap, AccessManaged UUPS upgradeability, mint/admin functions. |
| O3 | [research/eth-mainnet-apxusd/raw/evm-contracts/src/MinterV0.sol](../research/eth-mainnet-apxusd/raw/evm-contracts/src/MinterV0.sol) | onchain verified source | 2026-06-04 | medium/high | Signed mint order, nonce, max mint amount, and rate-limit mechanics. |
| O4 | [research/eth-mainnet-apxusd/raw/evm-contracts/src/Roles.sol](../research/eth-mainnet-apxusd/raw/evm-contracts/src/Roles.sol) and [research/eth-mainnet-apxusd/raw/evm-contracts/src/exts/ERC20DenyListUpgradable.sol](../research/eth-mainnet-apxusd/raw/evm-contracts/src/exts/ERC20DenyListUpgradable.sol) | onchain verified source | 2026-06-04 | medium/high | Role definitions/function-role helper context and deny-list checks on sender/receiver. |
| G1 | [research/eth-mainnet-apxusd/raw/safe-pending-2026-06-04.json](../research/eth-mainnet-apxusd/raw/safe-pending-2026-06-04.json) and [Safe Transaction Service pending tx API](https://safe-transaction-mainnet.safe.global/api/v1/safes/0xf9862EfC1704aC05e687f66E5cD8c130E5663cE2/multisig-transactions/?executed=false&limit=5) | governance | 2026-06-04 | medium | Pending Safe transaction caveat; payloads not exhaustively decoded. |
| D1 | Apyx docs, [apxUSD overview](https://docs.apyx.fi/product-overview/apxusd-overview) | issuer_docs | 2026-06-04 | medium | apxUSD mechanism, preferred-share backing, collateral allocation, peg model, eligible mint/redemption, general external pools. |
| D2 | Apyx docs, [apyUSD overview](https://docs.apyx.fi/product-overview/apyusd-overview) | issuer_docs | 2026-06-04 | medium | Relationship between apxUSD and apyUSD; apxUSD as underlying for savings wrapper. |
| D3 | Apyx docs, [Transparency](https://docs.apyx.fi/collateral-and-custody/transparency) | issuer_docs | 2026-06-04 | medium | Accountable, Apyx dashboard, Dune dashboard, custodian attestation framing. |
| D4 | Apyx docs, [Third Party Attestation](https://docs.apyx.fi/collateral-and-custody/third-party-attestation) | issuer_docs | 2026-06-04 | medium for listed PDFs, low for reserve conclusions | Wolf & Company March/April 2026 attestation links and custodian attestation claims. |
| D5 | Apyx docs, [Audits](https://docs.apyx.fi/resources/audits) | audit / issuer_docs | 2026-06-04 | medium for listed reports | Listed Quantstamp, Certora, and Zellic audit reports. |
| D6 | Certora public report summary, [Apyx apxUSD](https://www.certora.com/reports/apyx-apxusd) | audit | 2026-06-04 | medium | Certora March 2026 issue count and high-severity fixed/confirmed statement. |
| C1 | [research/eth-mainnet-apxusd/raw/evm-contracts/README.md](../research/eth-mainnet-apxusd/raw/evm-contracts/README.md) | issuer_docs / onchain | 2026-06-04 | medium | Public Apyx contracts repository README: protocol overview and contract architecture. |
| M1 | [research/eth-mainnet-apxusd/raw/dexscreener-apxusd-2026-06-04.json](../research/eth-mainnet-apxusd/raw/dexscreener-apxusd-2026-06-04.json), [DEXScreener token API](https://api.dexscreener.com/latest/dex/tokens/0x98A878b1Cd98131B271883B390f68D2c90674665), [Curve apxUSD/USDC pair](https://dexscreener.com/ethereum/0xe1b96555bbeca40e583bbb41a11c68ca4706a414) | market_data | 2026-06-04 | medium | Point-in-time venues, prices, liquidity, volume, and route divergence. |
