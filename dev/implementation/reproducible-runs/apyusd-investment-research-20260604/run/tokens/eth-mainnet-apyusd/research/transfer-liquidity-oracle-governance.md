# Apyx apyUSD — transfer, liquidity, oracle, governance research

Report date: 2026-06-04
Asset scope supplied by task: Apyx `apyUSD` on Ethereum mainnet (`chain_id: 1`), token `0x38EEb52F0771140d10c4E9A9a72349A329Fe8a6A`.
This report records objective, source-linked facts and unknowns only. It is not an investment recommendation, suitability verdict, or token-selection note.

## Agent-context summary

- Identity pinned on-chain: `name()` = `apyUSD`, `symbol()` = `apyUSD`, `decimals()` = 18, token/proxy address `0x38EEb52F0771140d10c4E9A9a72349A329Fe8a6A`; EIP-1967 implementation slot resolves to `0xfd616567ecc1607f61073951a1e822f7315bb112`. Source: [S1], [S2].
- `apyUSD` is an ERC-4626 vault over `apxUSD` (`asset()` = `0x98A878b1Cd98131B271883B390f68D2c90674665`). Official docs describe it as a non-rebasing savings token whose yield accrues through the `apxUSD`/`apyUSD` exchange rate. Source: [S2], [S4], [S6].
- Current point-in-time vault accounting at Ethereum block `25243667`: `totalAssets=233,809,171.647960937357117861 apxUSD`, `totalSupply=170,121,464.165379658144127124 apyUSD`, implied ERC-4626 rate `1.3743660907 apxUSD / apyUSD`; `paused=false`. Source: [S2].
- Transferability is permissionless at the docs level, but the token has pause and deny-list gates. Transfer hooks check both sender and receiver against `denyList()` = `0x2c271ddF484aC0386d216eB7eB9Ff02D4Dc0F6AA`; deposit/withdraw paths also check caller/receiver/owner where relevant. Source: [S2], [S3], [S4], [S6].
- Legal/product access is not fully permissionless: Apyx docs say no KYB/KYC requirement for apyUSD vault access, while Terms prohibit site/protocol use by restricted territories including the United States, EU, UK, Canada, and sanctioned/embargoed jurisdictions; apxUSD primary mint/redeem docs refer to eligible whitelisted participants. Source: [S6], [S7], [S12].
- Current redemption path is a variable unlock receipt model, not immediate return of liquid `apxUSD`: `withdraw`/`redeem` burn `apyUSD`, charge a vault-side upfront unlocking fee, escrow net `apxUSD`, and mint an Unlock Receipt NFT (`receipt()` = `0x9bf51F33955EC70f87C4b5C49441815589043237`) to the share owner. Source: [S2], [S3], [S5], [S8].
- Current receipt state: name `apxUSD Unlock Receipt`, symbol `apxUSD_receipt`, `asset=apxUSD`, `vault=apyUSD`, `paused=false`, fee wallet `0x6F93635F2A1C19b4F7f1BD9BA655F6A073C629Dc`. Receipt fee curve reads `minFee=0`, `maxFee=0.034e18` (3.4%), `minDuration=259200` seconds (3 days), `maxDuration=1728000` seconds (20 days), `curvature=1e18`; vault-side `unlockingFee=0.001e18` (0.1%). Source: [S2], [S5].
- Main Ethereum secondary liquidity found in market APIs is `apyUSD/apxUSD`. DEXScreener’s top Ethereum pair is Curve pool `0xe41be7B340f7c2EDA4DA1e99b42Ee1b228b526b7` with reported liquidity about `$13.23m` and 24h volume about `$25.09m`; direct Curve reads showed coins `apyUSD`/`apxUSD` and balances about `6.05m apyUSD` / `6.68m apxUSD`. Source: [S2], [S10], [S11].
- Current Curve point quotes from `0xe41be...526b7`: 1 `apyUSD` -> `1.321608 apxUSD` (~3.84% below vault rate); 100k -> `1.317427` each (~4.14% below); 1m -> `1.278121` each (~7.00% below). Source: [S2].
- `apxUSD` itself was below $1 in the checked Curve `apxUSD/USDC` route: 1 `apxUSD` -> `0.903873 USDC`; 1m -> `885,587.709549 USDC`. Source: [S2].
- `apyUSD` contract pricing is ERC-4626 internal accounting, not a separate external price oracle: `totalAssets()` returns vault `apxUSD` balance plus `vesting.vestedAmount()`, and the official `ApyUSDRateView` computes APY from unvested vesting yield over remaining period divided by total assets. Source: [S3], [S9].
- Governance/admin surface is AccessManager-controlled and upgradeable: `authority()` = `0xe167330E2Eac88666de253e9607C6d9ae0cA2824`; observed role holder for roles 21-25 is Safe-like contract `0xf9862EfC1704aC05e687f66E5cD8c130E5663cE2` with `getThreshold()=3` and six owners. AccessManager delays observed: pause and `setUnlockReceipt` callable immediately; unpause 4h; deny-list/unlocking-fee 1d; implementation/vesting/fee-wallet 3d; CCIP admin 7d. Source: [S2], [S13].
- Pending governance/admin data quality caveat: Safe Transaction Service returned 103 unexecuted transactions for `0xf986...63cE2`; the bounded pass recorded the first five but did not decode all payloads, so any production action package should refresh and decode pending Safe transactions before execution. Source: [S13].

## Mechanism in one paragraph

`apyUSD` is an upgradeable ERC-4626-style savings vault for Apyx `apxUSD`. Users deposit `apxUSD` and receive non-rebasing `apyUSD`; the exchange rate increases through vault accounting that includes the vault’s liquid `apxUSD` balance and vested yield from a configured vesting contract. Exiting is not immediate liquid `apxUSD`: the current implementation burns `apyUSD`, charges an upfront vault fee, escrows net `apxUSD` into an Unlock Receipt contract, and mints a receipt NFT that becomes claimable after the fee-curve minimum duration; the claim path can still be blocked by receipt pause or by underlying `apxUSD` deny-list transfer checks. Secondary exit depends on `apyUSD/apxUSD` and then `apxUSD/USDC` liquidity, where point-in-time market quotes were below the vault accounting rate. Source: [S2], [S3], [S5], [S6], [S8], [S10].

## Compact sections 1-5 context used by sections 6-9

### 1. Identity and scope

- Exact scoped asset: Apyx `apyUSD`, Ethereum mainnet, `0x38EEb52F0771140d10c4E9A9a72349A329Fe8a6A`.
- Official docs list Ethereum mainnet `apyUSD` at the same address and `apxUSD` at `0x98A878b1Cd98131B271883B390f68D2c90674665`. Source: [S1].
- Verified on-chain calls returned name/symbol/decimals/asset and proxy implementation noted above. Source: [S2].

### 2. Issuer/protocol and legal/eligibility framing

- Terms identify the site/protocol as APYX Protocol made available by Preference Capital (BVI) Ltd. and affiliates. Source: [S12].
- Official `apyUSD` overview states access is permissionless and has no KYB/KYC requirement, but also states frontend access is restricted for certain jurisdictions. Source: [S6].
- Terms prohibit restricted persons/territories from using the site and related services, including United States, EU, UK, Canada, Cuba, Iran, North Korea, Syria, Crimea, DPR/LPR regions, and other embargoed/sanctioned countries. Source: [S12].
- `apxUSD` primary mint/redemption docs say eligible participants in permitted jurisdictions who are whitelisted, such as institutional market makers, may mint/redeem through designated pathways; general users can acquire `apxUSD` through external liquidity pools. Source: [S7].

### 3. NAV/backing model

```text
nav_model: ERC-4626 vault-share / synthetic-dollar savings asset / RWA-backed apxUSD dependency
```

- `apyUSD` share accounting follows `totalAssets()` over supply; `totalAssets()` includes direct `apxUSD` vault balance plus `vesting.vestedAmount()`. Source: [S3], [S2].
- Official `apxUSD` docs describe `apxUSD` as backed by a basket of low-volatility, variable-rate preferred shares issued by Digital Asset Treasuries, with redemption scenarios liquidating preferred shares to USDC rather than transferring preferred shares to holders. Source: [S7].
- Third-party attestation docs list Wolf & Company April 2026 and March 2026 attestation PDFs, but this bounded pass did not parse the PDFs or reconcile current reserve balances to supply. Source: [S14].
- `missing_behavior: cannot_rank_cleanly` for reserve/collateral quality; `review_required` before using this report for production collateral valuation.

### 4. Contract admin, multisigs, and sensitive actions

Current observed sensitive surfaces:

| Contract | Role/action | Observed holder / authority | Existing-holder impact | Execution speed |
|---|---:|---|---|---|
| apyUSD proxy | UUPS implementation | implementation slot `0xfd616567ecc1607f61073951a1e822f7315bb112` | indirect/direct via code change | role 24; observed delay 3d for role holder |
| apyUSD | pause | role 21 via AccessManager; `0xf986...63cE2` can call now | direct transfer/deposit/redeem block | immediate |
| apyUSD | unpause | role 22 | restores flow | 4h delay observed |
| apyUSD | setDenyList | role 23 | direct transfer/redeem eligibility change | 1d delay observed |
| apyUSD | setUnlockReceipt | role 21 | direct redemption/claim-routing change for future receipts | immediate |
| apyUSD | setVesting | role 24 | direct exchange-rate/yield-accounting dependency | 3d delay observed |
| apyUSD | setUnlockingFee | role 23 | direct exit fee change, capped at 1% in source | 1d delay observed |
| apyUSD | setFeeWallet | role 24 | fee routing / share-price effect | 3d delay observed |
| apyUSD | setCCIPAdmin | role 25 | bridge/token-admin integration | 7d delay observed |
| UnlockReceipt | pause / fee curve / fee wallet | AccessManager-controlled; exact role mapping for receipt not fully enumerated in this pass | direct claimability and in-flight receipt fee impact | review_required |
| apxUSD | pause / deny-list / upgrade | same AccessManager authority observed; exact full surface not fully enumerated here | direct final-hop transfer / settlement block | review_required |

Source: [S2], [S3], [S5], [S13].

### 5. Audits, formal verification, and incidents

- Apyx docs list audits/formal work by Quantstamp (2026-02 and 2026-04), Certora (2026-03), and Zellic (2026-03). The extraction did not surface direct PDF/report text for each item, so report contents and resolved findings were not reviewed. Source: [S15].
- The verified source comments explicitly reference audit findings H-1/H-2/M-2/M-3/M-4/M-5 and document trust assumptions for pause coupling, compliance/deny-list claim failure, fee-wallet behavior, and receipt event interpretation. Source: [S3], [S5].
- Incident history was not established in this bounded pass; no exploit/depeg incident source was reviewed beyond point-in-time market data. `missing_behavior: review_required` for incident history.

## 6. Transferability, redemption, and liquidity

### 6.1 Transfer restrictions and eligibility/KYC

- `apyUSD` is a pausable ERC-20/ERC-4626 vault. The source says `pause()` pauses all token transfers, and on-chain `paused()` was `false` at block `25243667`. Source: [S2], [S3].
- `apyUSD` inherits `ERC20DenyListUpgradable`; `_update(from,to,value)` calls `_revertIfDenied(from)` and `_revertIfDenied(to)` before the ERC-20 transfer/mint/burn update. Source: [S4].
- Deposit/mint internal flow checks `caller` and `receiver` against the deny list; withdraw/redeem checks `caller`, `receiver`, and `owner`, and additionally requires `receiver == owner`. Source: [S3].
- On-chain `denyList()` returned `0x2c271ddF484aC0386d216eB7eB9Ff02D4Dc0F6AA`; `apxUSD` uses the same deny-list address in the current read. Source: [S2].
- Official `apyUSD` docs say access is permissionless with no KYB/KYC requirement, but terms and `apxUSD` primary mint/redeem docs impose restricted-territory and whitelist/eligible-participant constraints at the legal/product layer. Source: [S6], [S7], [S12].

Field record:

```text
transfer_restrictions: ERC-20 pause + deny-list checks on sender/receiver; deposit/redeem path checks caller/receiver/owner; receiver must equal owner for receipt mints
eligibility_kyc: apyUSD docs say no KYB/KYC and permissionless vault access; ToS and apxUSD primary mint/redeem docs impose jurisdiction/whitelist constraints
source_class: onchain + verified_source + official_docs + legal_terms
freshness: current for on-chain; docs pages last updated 6 days to 1 month ago; terms accessed current
confidence: high for contract behavior; medium for full eligibility process
missing_behavior: review_required for user-specific eligibility/redemption assumptions
```

### 6.2 Freeze, blacklist, forced-transfer, registry mechanics

- The active restriction primitive is a shared deny-list registry contract, not a per-token allowlist in the `apyUSD` source reviewed. The registry’s `contains(user)` result determines transfer/deposit/redeem denial. Source: [S4], [S2].
- `apyUSD` has `setDenyList(address)` controlled by AccessManager role 23; the observed role holder cannot call it immediately but has an execution delay of 86400 seconds. Source: [S2], [S13].
- No general forced-transfer function was found in reviewed `apyUSD` source. `burnWithAssets` / `burnWithAssetsFrom` are restricted functions, but `burnWithAssetsFrom` still spends standard ERC-20 allowance before burning shares and backing `apxUSD`; this is not a unilateral forced transfer in the reviewed code path. Source: [S3].
- The final claim transfer is mediated by underlying `apxUSD`; the `IUnlockReceipt` source says the receipt has no deny-list integration of its own and that claim-time compliance is routed through underlying `apxUSD` transfer checks. Source: [S5].

Field record:

```text
freeze_blacklist: yes, deny-list registry blocks transfer/mint/burn/deposit/redeem paths and apxUSD final transfers
forced_transfer: no general forced-transfer function found in apyUSD source; restricted burn-with-assets path requires allowance for third-party burn
registry_mechanics: shared AddressList deny-list at 0x2c271d...F6AA; setDenyList is AccessManager role 23
source_class: onchain + verified_source
freshness: current
confidence: high for deny-list; medium for absence of forced-transfer because source review was bounded to verified apyUSD snippets
missing_behavior: review_required before compliance-action automation
```

### 6.3 Primary redemption path and settlement process

Current on-chain/source path:

1. Holder calls standard `withdraw` / `redeem`, or helper `withdrawForReceipt` / `redeemForReceipt`, while not blocked by pause/deny-list. Source: [S3].
2. `apyUSD` enforces `receiver == owner`, pulls vested yield if configured, computes vault-side `unlockingFee`, burns shares for gross assets, routes the upfront fee if needed, approves `UnlockReceipt`, and mints a receipt NFT to the receiver/owner for net `apxUSD` assets. Source: [S3].
3. On-chain `unlockingFee()` = `0.001e18` = 0.1%; source caps this vault-side fee at 1%. Source: [S2], [S3].
4. Current `receipt()` = `0x9bf51F33955EC70f87C4b5C49441815589043237`; receipt reads `asset=apxUSD`, `vault=apyUSD`, `paused=false`. Source: [S2].
5. Receipt fee curve is global and can affect existing receipts: current on-chain curve is 0% min fee, 3.4% max fee, 3-day min duration/claimable point, 20-day max duration, linear curvature. Source: [S2], [S5].
6. Receipt `pause()` pauses mint and claim; interface notes no on-chain timelock cap on pause duration and no per-holder emergency-exit bypass. Source: [S5].
7. Claim-time denial can occur at the `apxUSD` final transfer if the holder is added to the underlying deny list between receipt mint and claim. Source: [S3], [S5].

Docs consistency caveat:

- The product overview describes current flexible redemptions as on-chain Unlock Receipt NFT, claimable after 3 days with fee declining over time. Source: [S6].
- The technical unlocking page still contains legacy language that withdrawals return non-transferable `apxUSD_unlock`, while also mentioning the flexible receipt model. Source: [S8].
- The current verified source states `unlockToken()` is deprecated and ignored by the live flow, while `receipt()` is the live path. Source: [S3].

Field record:

```text
primary_redemption_path: apyUSD burn -> vault-side unlocking fee -> net apxUSD escrow -> Unlock Receipt NFT -> claim to apxUSD
cooldown_queue_settlement: current fee curve claimable point 3 days; fee bottoms out at 20 days; docs also describe approximately 20-day cooldown/full wait
claim_token_receipt: yes, Unlock Receipt NFT at 0x9bf51...3237; receipt is described as soulbound in interface/source comments
claim_readiness: depends on receipt not paused, receipt age, fee curve, apxUSD transfer success, and deny-list state
source_class: onchain + verified_source + official_docs
freshness: current
confidence: high for current on-chain receipt path; medium for user-facing SLA because docs contain legacy/current wording tension
missing_behavior: review_required for exact frontend/user-process SLA; block_automation for real exits without fresh preview/fee/deny-list/pause checks
```

### 6.4 Secondary liquidity venues and size-dependent exit caveats

Primary Ethereum venues found in APIs at check time:

| Venue | Pair / address | Point-in-time data | Caveat |
|---|---|---|---|
| Curve | `apyUSD/apxUSD` `0xe41be7B340f7c2EDA4DA1e99b42Ee1b228b526b7` | DEXScreener liquidity ~$13.23m, 24h volume ~$25.09m; on-chain balances ~6.05m `apyUSD` and ~6.68m `apxUSD` | exit still leaves holder in `apxUSD`; route to USDC has its own discount/liquidity |
| PancakeSwap V3 Ethereum | `apyUSD/apxUSD` `0x7413522cA4B846Ff826E6d757af70a2Cb4083065` | DEXScreener liquidity ~$1.43m, 24h volume ~$5.74m | secondary market data only; not direct on-chain quoted in this pass |
| Uniswap V4 Ethereum | `apyUSD/apxUSD` pool id from API | lower volume/liquidity in API sample | pool-id style address; not directly quoted in this pass |
| Curve | `apxUSD/USDC` `0xE1B96555BbecA40E583BbB41a11C68Ca4706A414` | on-chain balances ~42.40m `apxUSD` and ~5.01m USDC | relevant second leg for USD exit; current `apxUSD` quotes below $1 |

Source: [S2], [S10], [S11].

Curve `apyUSD -> apxUSD` quote samples from the main Curve pool at report time:

| Sell size | Quoted `apxUSD` out | Effective `apxUSD/apyUSD` | Discount vs vault rate `1.3743660907` |
|---:|---:|---:|---:|
| 1 `apyUSD` | 1.321608 | 1.321608 | ~3.84% |
| 1,000 `apyUSD` | 1,321.566511 | 1.321567 | ~3.84% |
| 10,000 `apyUSD` | 13,211.909995 | 1.321191 | ~3.87% |
| 100,000 `apyUSD` | 131,742.663440 | 1.317427 | ~4.14% |
| 1,000,000 `apyUSD` | 1,278,121.339059 | 1.278121 | ~7.00% |

Source: [S2]. These are point-in-time `eth_call` quotes, not guaranteed executable settlement.

Curve `apxUSD -> USDC` quote samples from the official docs-listed Curve pool at report time:

| Sell size | Quoted USDC out | Effective USDC/apxUSD |
|---:|---:|---:|
| 1 `apxUSD` | 0.903873 | 0.903873 |
| 10,000 `apxUSD` | 9,037.162703 | 0.903716 |
| 1,000,000 `apxUSD` | 885,587.709549 | 0.885588 |

Source: [S2].

Historical premium/discount/stress:

- CoinGecko current `apyUSD` price returned about `$1.22`, market cap about `$209.57m`, total volume about `$30.16m`, and 24h price change `-6.83569%`. Source: [S11].
- DEXScreener top Curve pair price returned `priceUsd=1.18` and `priceNative=1.3182 apxUSD`, while CoinGecko’s top Curve ticker last price was `1.3254 apxUSD`; both are below the vault accounting rate at the same check. Source: [S10], [S11], [S2].
- Longer depeg/premium/discount history was not established in this bounded pass. Source-class remains market data only; `missing_behavior: review_required` for stress modeling.

Field record:

```text
secondary_liquidity: Curve and PancakeSwap/Uniswap Ethereum apyUSD-apxUSD venues; official docs list Curve apxUSD-USDC pool for second leg
current_depth: DEXScreener top Curve apyUSD/apxUSD liquidity about $13.23m; apxUSD/USDC pool visible USDC balance about 5.01m
historical_depeg_discount: point-in-time apyUSD/apxUSD market below vault exchange rate and apxUSD/USDC below $1; longer history not verified
eligible_liquidator_depth: unknown; legal/frontend/primary redemption eligibility may matter outside permissionless DEX swaps
source_class: market_data + onchain + official_docs
freshness: current point-in-time
confidence: high for current pool/quote; medium/low for historical stress
missing_behavior: block_automation for real exits without fresh route quote; review_required for compliance-gated exit eligibility
```

## 7. Oracle and pricing methodology

### 7.1 Primary price/oracle source

- `apyUSD` does not read a Chainlink-style external price feed for its own share conversions in the reviewed source. It uses ERC-4626 conversion math driven by `totalAssets()` and `totalSupply()`. Source: [S3].
- `totalAssets()` is overridden to return direct `apxUSD` balance in the vault plus `vesting.vestedAmount()` if a vesting contract is configured. Source: [S3].
- Current `vesting()` = `0x0D62B4cC02b4B51Ed19DDF41D7a7979CF394C99f`. Source: [S2].
- Official `ApyUSDRateView` address is `0xCABa36EDE2C08e16F3602e8688a8bE94c1B4e484`; source computes APY as annualized unvested yield divided by `ApyUSD.totalAssets()`, returning zero if total assets are zero, vesting is unset, or remaining vesting period is zero. Source: [S1], [S9].
- Underlying `apxUSD` dollar value is external to `apyUSD` conversion accounting. Official docs describe `apxUSD` backing and peg mechanisms, but this pass did not find or verify a current machine-readable NAV oracle for preferred-share collateral. Source: [S7], [S14].

Field record:

```text
primary_price_source: ERC-4626 internal exchange rate = totalAssets / totalSupply; APY display from ApyUSDRateView over vesting yield
oracle_follows: apxUSD-denominated vault accounting, not directly USD market value or preferred-share NAV
source_class: onchain + verified_source + official_docs
freshness: current
confidence: high for apyUSD conversion mechanics; medium/low for apxUSD backing/NAV methodology
missing_behavior: review_required before using as Credit Account collateral oracle methodology
```

### 7.2 Cadence, staleness, and dependencies

- There is no staleness window in `apyUSD` share conversion analogous to a feed max-staleness parameter; conversions use current on-chain balances, supply, and vesting contract view values. Source: [S3].
- `ApyUSDRateView` APY depends on `vesting.unvestedAmount()` and `vesting.vestingPeriodRemaining()`; if period remaining is zero or no vesting contract is configured, APY returns zero. Source: [S9].
- `totalAssets()` can change when `apxUSD` enters/leaves the vault, when vested yield is pulled, or when governance rotates `vesting`. Source: [S3].
- Composite dependencies include: `apxUSD` contract and deny-list/pause behavior, `apyUSD` vault implementation, vesting contract, Unlock Receipt contract, AccessManager roles/delays, `apxUSD` backing/custody/attestation process, and secondary `apyUSD/apxUSD` plus `apxUSD/USDC` liquidity. Source: [S2], [S3], [S5], [S7], [S14].

Field record:

```text
update_cadence: continuous on-chain accounting; APY depends on vesting-period state; no explicit feed cadence found
staleness_window: none found for apyUSD share conversion; external apxUSD backing/report freshness not machine-verified
composite_dependencies: apxUSD, vesting, receipt, AccessManager, deny-list, collateral/custody attestations, market liquidity
source_class: onchain + verified_source + official_docs
freshness: current for contracts; attestation docs list April/March 2026 but PDFs not parsed
confidence: high for no apyUSD feed staleness; medium for composite off-chain dependencies
missing_behavior: review_required for reserve/NAV/off-chain cadence; block_automation if route/action depends on stale market or governance state
```

### 7.3 Market-vs-NAV mismatch risk

- The accounting exchange rate was `1.374366 apxUSD/apyUSD`, while the main Curve market quoted about `1.3216 apxUSD/apyUSD` for 1 unit and lower rates for larger exits. Source: [S2].
- Even after a successful `apyUSD -> apxUSD` swap or receipt claim, the `apxUSD -> USDC` route quoted below $1. Source: [S2].
- The ERC-4626 rate can miss exit frictions: receipt wait/fee, receipt pause, deny-list/eligibility, `apxUSD` peg/liquidity, preferred-share liquidation timing, custody/attestation uncertainty, and DEX depth cliffs. Source: [S3], [S5], [S7], [S10], [S14].
- Secondary market price can diverge from vault accounting without changing `totalAssets()` immediately, because `totalAssets()` is `apxUSD`-denominated and does not mark `apxUSD` to USDC market price. Source: [S3], [S2].

Field record:

```text
observed_oracle_market_divergence: main Curve apyUSD/apxUSD quote ~3.84% below vault exchange rate for 1 apyUSD and ~7.00% below for 1m apyUSD; apxUSD/USDC also below $1
missed_risk_classes: market discount, receipt delay/fee, pause/deny-list, apxUSD peg/backing, collateral liquidation timing, off-chain custody/reporting, governance changes
source_class: onchain + market_data + verified_source + official_docs
freshness: current point-in-time
confidence: medium/high for point-in-time divergence; medium for risk-class mapping
missing_behavior: review_required for production collateral valuation; block_automation for liquidation/execution without fresh route and governance checks
```

## 8. Governance / change-feed watchlist

Watchlist items to compare against future runs:

1. `apyUSD` proxy implementation slot: current `0xfd616567ecc1607f61073951a1e822f7315bb112`. Any change is material. Source: [S2].
2. `apyUSD.authority()`: current AccessManager `0xe167330E2Eac88666de253e9607C6d9ae0cA2824`. Source: [S2].
3. `apyUSD.denyList()`: current `0x2c271ddF484aC0386d216eB7eB9Ff02D4Dc0F6AA`; changes affect transfers, deposits, and redemption eligibility. Source: [S2], [S4].
4. `apxUSD.denyList()` and `apxUSD.paused()`: current same deny-list and `paused=false`; claim final-hop can fail at `apxUSD` transfer. Source: [S2], [S5].
5. `apyUSD.paused()` and receipt `paused()`: both `false` at check; either pause can block transfer/redemption/claim flow. Source: [S2], [S3], [S5].
6. `apyUSD.receipt()`: current `0x9bf51F33955EC70f87C4b5C49441815589043237`; `setUnlockReceipt` can be called immediately by observed role holder and changes future receipt routing, while old receipts remain claimable through the old contract. Source: [S2], [S3], [S13].
7. Receipt fee curve and fee wallet: current curve 0%-3.4%, 3d-20d, curvature 1e18; interface says `setFeeCurve` is global and affects existing receipts. Source: [S2], [S5].
8. `apyUSD.unlockingFee()` and `feeWallet()`: current 0.1% upfront vault fee and wallet `0x6F93635F2A1C19b4F7f1BD9BA655F6A073C629Dc`; fee can affect exit amount. Source: [S2], [S3].
9. `apyUSD.vesting()`: current `0x0D62B4cC02b4B51Ed19DDF41D7a7979CF394C99f`; rotation affects totalAssets/APY accounting. Source: [S2], [S3], [S9].
10. AccessManager function-role mappings and role grant/delay events for roles 21-25. Current observed holder `0xf986...63cE2` has immediate `pause` and `setUnlockReceipt`, 4h `unpause`, 1d `setDenyList`/`setUnlockingFee`, 3d `upgradeToAndCall`/`setVesting`/`setFeeWallet`, 7d `setCCIPAdmin`. Source: [S2], [S13].
11. Safe-like role holder `0xf9862EfC1704aC05e687f66E5cD8c130E5663cE2`: threshold/owners, modules/guard, pending transactions, and executed transaction queue. Current threshold read is 3-of-6; modules/guard were not checked. Source: [S13].
12. Safe Transaction Service pending queue: returned 103 unexecuted transactions at access time; payloads were not decoded in this bounded pass. Decode before any action package or production integration. Source: [S13].
13. Official docs changes in `apyUSD` overview, locking/unlocking pages, smart contract address page, terms, audits, and attestations. Source: [S1], [S6], [S8], [S12], [S14], [S15].
14. Main Curve/Pancake/Uniswap `apyUSD/apxUSD` liquidity and Curve `apxUSD/USDC` depth/quotes; point-in-time market discount was material. Source: [S2], [S10], [S11].
15. Published reserve/collateral attestations, preferred-share concentration/liquidity updates, audit reports, and incident statements. Source: [S7], [S14], [S15].

Field record:

```text
governance_model: UUPS upgradeable contracts controlled by AccessManager roles/delays; operational role holder appears Safe-like 3-of-6
pending_changes: Safe Transaction Service returned 103 unexecuted transactions, not decoded in this bounded pass
source_class: onchain + governance_api + official_docs + market_data
freshness: current point-in-time
confidence: high for direct role/delay reads; medium for pending-change impact because queue was not decoded
missing_behavior: review_required for admin/governance drift; block_automation if pending role/oracle/implementation/fee/liquidity tx executes before action package refresh
```

## 9. Data quality and missing-data behavior

### 9.1 Material field quality table

| Field | Current value / finding | source_class | freshness | confidence | missing_behavior |
|---|---|---|---|---|---|
| Token identity | apyUSD / apyUSD / 18 decimals / exact Ethereum address | onchain + official_docs | current | high | continue |
| Proxy/implementation | EIP-1967 implementation `0xfd6165...b112`; admin/beacon slots zero | onchain | current | high | review_required if changed |
| Underlying asset | `apxUSD` `0x98A878...4665` | onchain + official_docs | current | high | review_required if changed |
| Vault rate | `1.3743660907 apxUSD/apyUSD` at block `25243667` | onchain | current | high | continue; refresh before use |
| Transfer restriction | Pause + deny-list checks; receiver/owner constraints on exit | onchain + verified_source | current | high | review_required for user-specific eligibility |
| Legal/product eligibility | Docs say no KYB/KYC for apyUSD; terms restrict territories; apxUSD primary mint/redeem whitelisted | official_docs + legal_terms | current docs | medium/high | review_required |
| Forced transfer | No general forced-transfer function found; restricted burn-with-assets path requires allowance for third-party burn | verified_source | current source | medium | review_required before compliance conclusions |
| Primary redemption | Burn shares and mint Unlock Receipt NFT escrowing net apxUSD | onchain + verified_source | current | high | block_automation without fresh preview/fee/claimability checks |
| Claim token/NFT | Unlock Receipt NFT `0x9bf51...3237`, `paused=false` | onchain + verified_source | current | high | continue |
| Receipt fee curve | 0%-3.4%, claimable after 3d, bottoms at 20d, global curve | onchain + verified_source | current | high | review_required if changed |
| Vault-side exit fee | `unlockingFee=0.1%`, fee wallet `0x6F93...29Dc` | onchain + verified_source | current | high | review_required if changed |
| Secondary ETH liquidity | Curve `apyUSD/apxUSD`, PancakeSwap, Uniswap; Curve `apxUSD/USDC` second leg | market_data + onchain | current | high for current pools | block_automation without fresh route quote |
| Market-vs-vault divergence | Curve `apyUSD/apxUSD` below vault rate; `apxUSD/USDC` below $1 | onchain + market_data | current | high for point-in-time | review_required for stress history |
| Oracle/pricing source | ERC-4626 internal `totalAssets/totalSupply`; APY view over vesting | onchain + verified_source | current | high | review_required for USD/backing oracle methodology |
| Staleness | No feed staleness found in apyUSD conversions; off-chain reserve/report cadence not machine-verified | verified_source + official_docs | current/partial | medium | review_required |
| AccessManager | `0xe167...2824`, roles/delays observed | onchain | current | high | review_required if changed |
| Role holder | `0xf986...63cE2`, Safe-like threshold 3-of-6 | onchain | current | medium/high | review_required for modules/guard/pending queue |
| Pending governance | 103 unexecuted Safe tx returned; not decoded | governance_api | current | medium | review_required; block_automation before execution |
| Audits | Docs list Quantstamp, Certora, Zellic audits/formal work; PDFs not parsed | official_docs | current docs | medium/low for contents | review_required |
| Attestations/backing | Wolf & Company March/April 2026 attestation PDFs listed; PDFs not parsed/reconciled | official_docs | docs current | low/medium | cannot_rank_cleanly / review_required |
| Incident history | not established in bounded pass | unknown | unknown | low | review_required |
| Gearbox support/oracle notes | not checked/found in this scoped research pass | unknown | unknown | low | continue unless Gearbox integration depends on it, then review_required |

### 9.2 Highest-impact unknowns

1. Full reserve/custody/attestation content and current collateral composition were not parsed or reconciled to supply. Docs list attestations, but this pass did not validate the PDFs or current backing. `missing_behavior: cannot_rank_cleanly` and `review_required`.
2. Exact `apxUSD` primary mint/redemption operational SLA, whitelist process, settlement constraints, and weekend/off-hours behavior were not independently verified beyond official docs. `missing_behavior: review_required`; `block_automation` for executing real primary settlement without live process confirmation.
3. Receipt implementation source was not fully expanded in this artifact beyond interface/on-chain reads and `apyUSD` source comments; exact ERC-721 transfer-disable mechanics and all receipt role mappings should be verified before relying on transferability/claim automation. `missing_behavior: review_required`.
4. Safe-like role-holder modules/guard and all 103 pending Safe transactions were not decoded. `missing_behavior: review_required`; `block_automation` for production action packages until refreshed/decoded.
5. Longer price/depeg/premium history was not built. Current market-vs-vault divergence is point-in-time only. `missing_behavior: review_required` for stress modeling.
6. Audit reports and formal-verification PDFs were not parsed; docs list audit providers/dates only. `missing_behavior: review_required` for security posture.
7. No dedicated external USD oracle methodology for `apyUSD` was found; `apyUSD` accounting is apxUSD-denominated ERC-4626 math. `missing_behavior: review_required` before using as collateral oracle methodology.

## Source list

[S1] Apyx docs, Smart Contract Addresses, `https://docs.apyx.fi/resources/smart-contract-addresses`; source_class: official_docs; accessed: 2026-06-04; confidence: high for listed addresses, medium for dynamic state.

[S2] Direct Ethereum JSON-RPC / Foundry `cast` calls to Ethereum mainnet via `https://ethereum-rpc.publicnode.com`, recorded in `run/tokens/eth-mainnet-apyusd/research/raw/onchain-market-snapshot-2026-06-04.json`; source_class: onchain; accessed: 2026-06-04; confidence: high. Calls included EIP-1967 slots, token metadata, `asset`, `totalAssets`, `totalSupply`, `paused`, `denyList`, `receipt`, `vesting`, `unlockingFee`, `feeWallet`, `authority`, `feeCurve`, AccessManager roles/delays/canCall, Safe-like threshold/owners, Curve pool balances/rates/quotes, and market API snapshots.

[S3] Etherscan verified/source-code review for `apyUSD` proxy/implementation, token `0x38EEb52F0771140d10c4E9A9a72349A329Fe8a6A`, especially `ApyUSD.sol` local extraction `/tmp/apyx_sources/apyusd/src__ApyUSD.sol`; source URL `https://etherscan.io/address/0x38EEb52F0771140d10c4E9A9a72349A329Fe8a6A#code`; source_class: verified_source; accessed: 2026-06-04; confidence: high for reviewed implementation behavior matched to implementation slot.

[S4] Etherscan verified/source-code review for deny-list extension `ERC20DenyListUpgradable.sol`, local extraction `/tmp/apyx_sources/apyusd/src__exts__ERC20DenyListUpgradable.sol`; source URL as part of `apyUSD` verified source at `https://etherscan.io/address/0x38EEb52F0771140d10c4E9A9a72349A329Fe8a6A#code`; source_class: verified_source; accessed: 2026-06-04; confidence: high.

[S5] Etherscan verified/source-code review for `IUnlockReceipt.sol` and `FeeCurve.sol`, local extraction `/tmp/apyx_sources/apyusd/src__interfaces__IUnlockReceipt.sol` and `/tmp/apyx_sources/apyusd/src__FeeCurve.sol`; source URL as part of verified `apyUSD` / receipt-adjacent source; source_class: verified_source; accessed: 2026-06-04; confidence: high for interface/fee-curve constraints, medium for full receipt implementation because implementation body was not fully expanded in this bounded pass.

[S6] Apyx docs, `apyUSD` overview, `https://docs.apyx.fi/product-overview/apyusd-overview`; source_class: official_docs; accessed: 2026-06-04; confidence: high for published user-facing statements, medium where docs conflict with source/current implementation details.

[S7] Apyx docs, `apxUSD` overview, `https://docs.apyx.fi/product-overview/apxusd-overview`; source_class: official_docs; accessed: 2026-06-04; confidence: medium/high for published mechanism text, medium for operational process details not independently verified.

[S8] Apyx docs, Unlocking apyUSD for apxUSD, `https://docs.apyx.fi/technical-overview/unlocking`; source_class: official_docs; accessed: 2026-06-04; confidence: medium because page contains both legacy `apxUSD_unlock` wording and current receipt-model wording.

[S9] Etherscan verified/source-code review for `ApyUSDRateView`, local extraction `/tmp/apyx_sources/rateview/src__views__ApyUSDRateView.sol`; official address listed at `https://docs.apyx.fi/resources/smart-contract-addresses`; source_class: verified_source + official_docs; accessed: 2026-06-04; confidence: high for APY formula.

[S10] DEXScreener API/token-pair data for `apyUSD`, `https://api.dexscreener.com/latest/dex/tokens/0x38EEb52F0771140d10c4E9A9a72349A329Fe8a6A` and Curve pair page `https://dexscreener.com/ethereum/0xe41be7b340f7c2eda4da1e99b42ee1b228b526b7`; source_class: market_data; accessed: 2026-06-04; confidence: high for current reported pair data, medium for API-derived market cap/FDV.

[S11] CoinGecko API/page for `apyUSD`, `https://www.coingecko.com/en/coins/apyusd` and public API `/api/v3/coins/apyusd`; source_class: market_data; accessed: 2026-06-04; confidence: medium because global market stats can include venues beyond Ethereum-mainnet executable depth.

[S12] Apyx Terms of Service, `https://docs.apyx.fi/resources/terms-of-service`; source_class: legal_terms; accessed: 2026-06-04; confidence: high for published terms text, medium for practical enforcement details.

[S13] Safe Transaction Service plus direct on-chain calls for role-holder Safe-like address `0xf9862EfC1704aC05e687f66E5cD8c130E5663cE2`, endpoint `https://safe-transaction-mainnet.safe.global/api/v1/safes/0xf9862EfC1704aC05e687f66E5cD8c130E5663cE2/multisig-transactions/?executed=false&limit=5`; source_class: governance_api + onchain; accessed: 2026-06-04; confidence: high for threshold/owners/pending-count returned, medium for pending impact because tx payloads were not decoded.

[S14] Apyx docs, Third Party Attestation, `https://docs.apyx.fi/collateral-and-custody/third-party-attestation`; source_class: official_docs / attestation index; accessed: 2026-06-04; confidence: medium for listed PDF availability, low for reserve conclusions because PDFs were not parsed.

[S15] Apyx docs, Audits, `https://docs.apyx.fi/resources/audits`; source_class: official_docs / audit index; accessed: 2026-06-04; confidence: medium for listed auditor/date names, low for finding status because report contents were not extracted.
