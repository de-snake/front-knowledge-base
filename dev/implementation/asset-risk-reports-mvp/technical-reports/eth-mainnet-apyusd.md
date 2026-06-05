# apyx apyUSD — MVP asset risk dossier

Report date: 2026-06-04 UTC
Analyst: Hermes synthesis worker
Input asset: Ethereum mainnet (`chain_id: 1`), `apyUSD`, token address `0x38EEb52F0771140d10c4E9A9a72349A329Fe8a6A`.
Issuer / protocol hint supplied by task: apyx.
Intended use: unknown.
Output type: objective source-linked dossier for later agent reasoning. No ranking, acceptance, suitability verdict, portfolio action, or investment recommendation is provided.

Synthesis inputs read before drafting:

- `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/methodology.md`
- `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/eth-mainnet-apyusd/onchain-admin.md`
- `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/eth-mainnet-apyusd/issuer-backing-security.md`
- `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/eth-mainnet-apyusd/transfer-liquidity-oracle-governance.md`

Source IDs in sections below resolve to URLs, source class, access date, and confidence in section 13.

## 1. Agent-context summary

`apyUSD` is an Ethereum-mainnet Apyx token at `0x38EEb52F0771140d10c4E9A9a72349A329Fe8a6A`; direct on-chain reads and Apyx docs identify it as an 18-decimal, non-rebasing ERC-4626-style vault share over `apxUSD` at `0x98A878b1Cd98131B271883B390f68D2c90674665` [S1][S2][S5][S6]. The token is an ERC-1967/UUPS-upgradeable proxy with implementation `0xfd616567eCc1607F61073951A1e822f7315bb112` and OpenZeppelin-style AccessManager authority `0xe167330E2Eac88666de253E9607C6d9Ae0cA2824` [S1][S2][S3]. Users deposit `apxUSD` into the vault and receive `apyUSD`; value accrues through the vault exchange rate rather than by rebasing balances, while exits currently burn `apyUSD`, charge a vault-side fee, escrow net `apxUSD`, and mint an Unlock Receipt NFT before claim [S4][S5][S8]. Existing-holder-relevant controls include immediate pause, deny-list replacement, receipt rotation, fee and vesting changes, UUPS upgrades, and AccessManager role changes; sampled role reads show operational roles 21-25 held by Safe-compatible address `0xf9862EfC1704aC05e687f66E5cD8c130E5663CE2` with 3-of-6 owner threshold, while AccessManager role 0 is held by EOA `0xabdd8c8ee69e5F5180EB9352AeFFc5CeEAd65e96` [S1][S16]. The asset inherits `apxUSD` backing, custody, attestation, preferred-share, redemption, and legal-access dependencies; Apyx docs list Accountable transparency, Wolf & Company monthly attestations, and Quantstamp / Certora / Zellic security work, but this synthesis did not reconcile reserve PDFs or map every audit scope to the live implementation [S9][S10][S11][S12]. Secondary market observations in the parent research showed the main Curve `apyUSD/apxUSD` route below the ERC-4626 vault rate and the `apxUSD/USDC` second leg below $1 at the sampled time; real exits therefore require fresh route, pause, deny-list, receipt, governance, and backing-state checks before automation [S1][S14][S15].

## 2. One-paragraph mechanism

`apyUSD` is an upgradeable Apyx ERC-4626-style savings vault for `apxUSD`: holders deposit `apxUSD` and receive non-rebasing `apyUSD` shares, with share value determined by `totalAssets()` divided by supply and with yield reflected through exchange-rate growth that includes the vault’s direct `apxUSD` balance plus vested yield from a configured vesting contract [S1][S4][S5]. The current exit path is asynchronous rather than immediate liquid settlement: `withdraw` / `redeem` burn `apyUSD`, charge a vault-side unlocking fee, escrow net `apxUSD`, and mint an Unlock Receipt NFT that can later claim `apxUSD` subject to receipt age, fee curve, receipt pause, and underlying `apxUSD` transfer / deny-list checks [S1][S4][S8]. Secondary exit can use `apyUSD/apxUSD` liquidity and then `apxUSD/USDC` liquidity, but point-in-time market quotes were below the vault accounting rate and below $1 on the second leg [S1][S14][S15].

## 3. Identity and token semantics

| Field | Current dossier value | Evidence |
|---|---|---|
| Canonical chain | Ethereum mainnet, `chain_id: 1` | Task scope and direct Ethereum mainnet RPC snapshot [S1]. |
| Token address | `0x38EEb52F0771140d10c4E9A9a72349A329Fe8a6A` | Task scope, on-chain snapshot, Etherscan contract page, Apyx address docs [S1][S2][S7]. |
| Name / symbol / decimals | `apyUSD` / `apyUSD` / `18` | Direct `name()`, `symbol()`, `decimals()` reads [S1]. |
| Immediate underlying asset | `apxUSD` at `0x98A878b1Cd98131B271883B390f68D2c90674665` | Direct `asset()` read and official Apyx docs [S1][S5][S6]. |
| Token standard / source behavior | ERC-20 / ERC-20Permit / ERC-4626-style upgradeable vault share with pause and deny-list gates | Verified source imports/inheritance and docs [S2][S4][S5]. |
| Proxy / implementation | ERC-1967 proxy; UUPS implementation `0xfd616567eCc1607F61073951A1e822f7315bb112`; EIP-1967 admin slot zero | Direct slot reads, UUPS `proxiableUUID`, Etherscan, Dedaub [S1][S2][S3]. |
| Authority / access control | AccessManager `0xe167330E2Eac88666de253E9607C6d9Ae0cA2824` | Direct `authority()` read [S1]. |
| Current operational state in snapshots | `paused=false`; deny-list `0x2c271ddF484aC0386d216eB7eB9Ff02D4Dc0F6AA`; receipt `0x9bf51F33955EC70f87C4b5C49441815589043237`; vesting `0x0D62B4cC02b4B51Ed19DDF41D7a7979CF394C99f`; vault-side unlocking fee `0.001e18` / 0.1% | Direct RPC snapshots [S1]. |
| Asset type | issuer-controlled synthetic-dollar savings / vault share over `apxUSD` | Official mechanism docs and verified vault source [S4][S5][S6]. |
| Token behavior | Non-rebasing share token; yield accrues through exchange-rate growth rather than balance rebasing | Official `apyUSD` docs and ERC-4626 source behavior [S4][S5]. |
| Transition-stage asset behavior | `apyUSD` exits can create a separate Unlock Receipt NFT / pending claim state before final `apxUSD` claim | Verified source and official unlocking docs [S4][S8]. |

Missing-data behavior: identity and proxy facts are high-confidence for the sampled date and can be used for explanation. If implementation, authority, receipt, vesting, deny-list, or pause state changes, `missing_behavior: review_required` before treating prior conclusions as current [S1][S17].

## 4. Issuer / protocol and business model

Apyx docs and Terms describe APYX Protocol as made available by Preference Capital (BVI) Ltd. and affiliates; the scoped token is `apyUSD`, the Apyx savings token for `apxUSD` [S5][S6][S13]. Official docs state that users deposit `apxUSD` into a permissionless ERC-4626 vault and receive `apyUSD`, with yield accruing through the `apxUSD` / `apyUSD` exchange rate [S5]. The parent research identified the yield / backing dependency as Apyx’s underlying collateral stack and dividend process; Certora’s public report summary describes `apxUSD` as backed by off-chain preferred shares that generate dividend yields, and describes `apyUSD` as a yield-bearing ERC-4626 wrapper whose yield is distributed through vesting [S6][S9][S12].

Business-model and dependency map:

| Dimension | Finding | Evidence / behavior |
|---|---|---|
| Revenue / yield source | Dividends / yield from the underlying `apxUSD` collateral stack, reflected in `apyUSD` exchange-rate growth | Official docs and Certora report summary [S5][S6][S12]. |
| Off-chain dependencies | `apyUSD` inherits `apxUSD` backing, custody, preferred-share, Accountable dashboard, custodian attestation, and collateral-management assumptions | Transparency and attestation docs [S9][S10]. |
| Contract dependencies | AccessManager, deny-list contract, Unlock Receipt contract, vesting contract, fee wallet, and CCIP admin all affect current token behavior | Direct on-chain reads and verified source [S1][S4]. |
| Mint / vault entry | `apyUSD` vault access is described as permissionless with no KYB/KYC requirement; contract entry still checks pause / deny-list state | Apyx docs and verified source [S4][S5]. |
| Direct redemption / exit | Exits create an Unlock Receipt NFT before claim; `apxUSD` primary mint / redeem docs refer to eligible whitelisted participants for direct primary pathways | Official docs, unlocking docs, source [S4][S6][S8]. |
| Legal / jurisdiction access | Docs say no KYB/KYC for `apyUSD` vault access, while Terms restrict use by restricted territories/persons including United States, EU, UK, Canada, and sanctioned/embargoed jurisdictions | Apyx `apyUSD` docs and Terms [S5][S13]. |
| Sensitive actors | AccessManager role holders can pause, rotate deny-list/receipt/vesting, change fees, and upgrade implementation; `apxUSD` primary workflows depend on eligible participants | On-chain role reads and official docs [S1][S6][S16]. |

Missing-data behavior: user-specific legal eligibility, `apxUSD` primary mint/redeem process details, and off-chain collateral-management state are `review_required`; any automated real exit or settlement package requires live Preview / route / eligibility checks and uses `missing_behavior: block_automation` until refreshed [S6][S13][S17].

## 5. Backing, NAV, and exposure map

```text
nav_model: collateralized vault / issuer NAV / dividend-backed underlying
```

Backing and exposure chain:

1. Immediate accounting layer: `apyUSD` is an ERC-4626-style vault share over `apxUSD`; direct snapshot reads returned `asset() = 0x98A878b1Cd98131B271883B390f68D2c90674665`, `totalAssets()`, and `totalSupply()` [S1][S5].
2. Exchange-rate layer: the share value is not a hardcoded $1 value; it is an `apxUSD`-denominated vault accounting rate from `totalAssets / totalSupply` [S1][S4].
3. Underlying issuer layer: Apyx docs describe `apxUSD` as backed by a basket of low-volatility, variable-rate preferred shares issued by Digital Asset Treasuries, and redemption scenarios liquidate preferred shares to USDC rather than transferring preferred shares to holders [S6].
4. Transparency layer: Apyx docs point to Accountable for near-real-time reserve / collateral visibility and to Apyx / Dune dashboards for capital deployment, reserve position, and on-chain data [S9].
5. Attestation layer: Apyx docs list Wolf & Company March and April 2026 attestation opinions and state that custodians provide monthly attestations validating backing assets exist, remain under custody control, and are valued appropriately [S10].

Snapshot values and exposure caveats:

| Field | Finding | Evidence / caveat |
|---|---|---|
| Sampled `totalAssets()` | `233786308355629929225483777` raw `apxUSD` units in the admin snapshot; market snapshot also captured a close point-in-time value | Direct RPC snapshots at sampled blocks [S1]. |
| Sampled `totalSupply()` | `170104409453165089753438983` raw `apyUSD` units in the admin snapshot; market snapshot also captured a close point-in-time value | Direct RPC snapshots [S1]. |
| NAV / market divergence | The ERC-4626 accounting rate can diverge from secondary market exit value; parent market snapshot showed Curve `apyUSD/apxUSD` below vault rate and `apxUSD/USDC` below $1 | Market and on-chain quote data [S1][S14][S15]. |
| Reserve reconciliation | Attestation links were identified, but reserve / collateral PDF contents were not parsed and not reconciled to current `apxUSD` / `apyUSD` supply | Apyx attestation docs [S10]. |
| Custody model | Custodian attestation process exists in docs, but custodian identities, report details, and current reserve composition were not fully reconciled in the synthesis inputs | Transparency and attestation docs [S9][S10]. |
| Haircut / basis / liquidation exposure | Practical exit can be affected by receipt timing/fees, `apxUSD` peg/liquidity, preferred-share liquidation timing, off-chain custody/reporting, and secondary DEX depth | Source and market observations [S4][S6][S8][S14][S15]. |

Missing-data behavior: backing / reserve / custodian reconciliation has `missing_behavior: cannot_rank_cleanly` for comparative scoring and `review_required` for production collateral valuation. Real exits have `missing_behavior: block_automation` until fresh quote, receipt, pause, deny-list, and governance state are checked [S10][S17].

## 6. Contract admin, multisigs, and sensitive actions

Current admin architecture:

| Surface | Current finding | Source-linked status |
|---|---|---|
| Upgradeability | ERC-1967/UUPS proxy; implementation `0xfd616567eCc1607F61073951A1e822f7315bb112`; proxy admin slot zero | Direct slots / Etherscan / Dedaub [S1][S2][S3]. |
| AccessManager | `authority() = 0xe167330E2Eac88666de253E9607C6d9Ae0cA2824`; target admin delay for `apyUSD` observed as 259200 seconds / 3 days | Direct on-chain reads [S1]. |
| AccessManager role 0 | EOA `0xabdd8c8ee69e5F5180EB9352AeFFc5CeEAd65e96`; can administer AccessManager state and, in sampled mapping, call restricted burn-with-assets functions | Direct role reads [S1]. |
| Operational roles 21-25 | Safe-compatible address `0xf9862EfC1704aC05e687f66E5cD8c130E5663CE2`; Safe-like `getThreshold()=3` and 6 owners | Direct Safe-like calls [S1][S16]. |
| Safe modules / guard | Not exhaustively checked; Safe Transaction Service returned 103 unexecuted transactions for the Safe-like role holder, first page not fully decoded in parent research | Governance API and direct reads [S16]. |

Sensitive action matrix:

| Sensitive action | Current authorized path | Existing-holder impact | Execution speed | Evidence / missing behavior |
|---|---|---|---|---|
| Pause `apyUSD` | Role 21 via Safe-compatible `0xf986...3CE2` | `direct_redemption_block` plus transfer/deposit/redeem block while paused | `immediate` | Role delay 0 and pausable source [S1][S4]. |
| Unpause `apyUSD` | Role 22 via Safe-compatible `0xf986...3CE2` | unblocks paused flows | `timelocked` / 4 hours | Direct role/delay read [S1]. |
| Replace deny-list contract | Role 23 via Safe-compatible `0xf986...3CE2` | `direct_freeze` / `direct_redemption_block` depending registry contents | `timelocked` / 1 day | Deny-list checks transfer/deposit/withdraw paths [S1][S4]. |
| Rotate Unlock Receipt contract | Role 21 via Safe-compatible `0xf986...3CE2` | Can alter receipt routing for future exits; misconfiguration could block new redemptions | `immediate` | Source says old receipts remain claimable through old contract, but new exits use current receipt [S1][S4]. |
| Set vault-side unlocking fee | Role 23 via Safe-compatible `0xf986...3CE2` | `indirect` for future exits; source caps at 1% | `timelocked` / 1 day | Current fee 0.1% [S1][S4]. |
| Set fee wallet | Role 24 via Safe-compatible `0xf986...3CE2` | Fee routing for future exits | `timelocked` / 3 days | Direct role/delay and source [S1][S4]. |
| Set vesting contract | Role 24 via Safe-compatible `0xf986...3CE2` | Can alter `totalAssets()` / APY accounting dependency | `timelocked` / 3 days | Current vesting address and source behavior [S1][S4]. |
| Upgrade implementation | Role 24 via Safe-compatible `0xf986...3CE2` | `unknown` because implementation can alter token behavior | `timelocked` / 3 days | UUPS source and AccessManager role mapping [S1][S4]. |
| Set CCIP admin | Role 25 via Safe-compatible `0xf986...3CE2` | Bridge / token-admin integration; no direct ordinary ERC-20 balance effect identified in the parent source review | `timelocked` / 7 days | Source comments and role mapping [S1][S4]. |
| AccessManager role / target reconfiguration | Role 0 EOA `0xabdd...5e96` | `unknown` to direct intervention depending new mapping | Not fully established; sampled direct role-0 calls were immediate | Full admin-operation history not reconstructed; `missing_behavior: review_required` [S1][S17]. |
| Restricted burn-with-assets functions | Role 0 EOA `0xabdd...5e96` | No unilateral forced-transfer identified in reviewed code; third-party burn path spends allowance when `account != spender` | `immediate` in sampled map | Verified source and role reads [S1][S4]. |

Missing-data behavior: AccessManager admin history, EOA identity, Safe module/guard state, all pending Safe transactions, deny-list contract administration, and full receipt admin role mapping are `review_required`; pending role/oracle/implementation/fee/liquidity changes before an action package imply `missing_behavior: block_automation` until refreshed [S16][S17].

## 7. Audits, formal verification, and incidents

Security reports identified from official Apyx docs:

| Report / source | Finding | Evidence / caveat |
|---|---|---|
| Quantstamp 2026-02 | Listed on Apyx audit page | Report body and deployed-scope mapping were not parsed in synthesis inputs [S11]. |
| Certora 2026-03 | Listed on Apyx audit page; Certora summary says 11 issues were found, including one high-severity issue, and that the high-severity issue was fixed and confirmed | Public report summary; deployed-scope mapping remains `review_required` [S11][S12]. |
| Zellic 2026-03 | Listed on Apyx audit page | Report body and deployed-scope mapping were not parsed in synthesis inputs [S11]. |
| Quantstamp 2026-04 | Listed on Apyx audit page | Report body and deployed-scope mapping were not parsed in synthesis inputs [S11]. |

Formal verification / proof status: Certora security work is listed and the public summary describes the March 2026 review, but the synthesis inputs did not extract all formal rules, invariants, or exact verified scope against current deployed `apyUSD`, `apxUSD`, Unlock Receipt, AccessManager, and vesting contracts [S11][S12].

Incident signals: the bounded parent research did not identify a confirmed public exploit, depeg postmortem, freeze event, or redemption-delay postmortem for the exact `apyUSD` token; this is a bounded-source observation rather than a clean incident history [S11][S14][S15]. Market snapshots did show material point-in-time discounts between vault accounting, `apyUSD/apxUSD`, and `apxUSD/USDC` quotes, which should be treated as a market-data signal rather than an incident conclusion [S1][S14][S15].

Missing-data behavior: audit/report contents, formal-scope mapping, and incident history are `review_required`; absence of a found incident in these sources has `missing_behavior: continue` for explanation only and does not clear security or market-stress review [S17].

## 8. Transferability, redemption, and liquidity

### 8.1 Transfer restrictions and eligibility

`apyUSD` is transferable through ERC-20 paths when not paused and when sender and receiver are not denied; the verified source’s `_update` path checks both sender and receiver against the active deny-list contract, and deposit / withdraw paths add caller, receiver, and owner checks where relevant [S1][S4]. On-chain snapshots read `paused=false` and deny-list `0x2c271ddF484aC0386d216eB7eB9Ff02D4Dc0F6AA` [S1]. Official docs describe `apyUSD` vault access as permissionless with no KYB/KYC requirement, but Terms restrict use by restricted persons / territories, and `apxUSD` primary mint / redemption docs refer to eligible whitelisted participants [S5][S6][S13].

```text
transfer_restrictions: pause + deny-list checks on sender/receiver; deposit/redeem path checks caller/receiver/owner; receiver must equal owner for receipt mints
eligibility_kyc: apyUSD docs say permissionless/no KYB-KYC; Terms and apxUSD primary mint/redeem docs impose jurisdiction/whitelist constraints at legal/product layer
source_class: onchain + verified source + issuer_docs + legal_terms
freshness: current for sampled on-chain state; current docs at access date
confidence: high for contract behavior, medium for practical eligibility process
missing_behavior: review_required for user-specific eligibility; block_automation for real exits without fresh eligibility/pause/deny-list checks
```

### 8.2 Redemption and claim process

Current source and on-chain path:

1. Holder calls standard `withdraw` / `redeem` or helper receipt functions while not blocked by pause or deny-list state [S4].
2. `apyUSD` requires `receiver == owner`, computes a vault-side unlocking fee, burns shares, routes the upfront fee if needed, approves the Unlock Receipt, and mints a receipt NFT to the receiver/owner for net `apxUSD` assets [S4].
3. Current `receipt()` is `0x9bf51F33955EC70f87C4b5C49441815589043237`; parent reads show receipt name `apxUSD Unlock Receipt`, symbol `apxUSD_receipt`, `asset=apxUSD`, `vault=apyUSD`, and `paused=false` [S1].
4. The receipt fee curve in the parent snapshot was `minFee=0`, `maxFee=0.034e18` / 3.4%, `minDuration=259200` seconds / 3 days, `maxDuration=1728000` seconds / 20 days, `curvature=1e18`; vault-side `unlockingFee()` was `0.001e18` / 0.1% [S1][S8].
5. Claim-time failure can occur if the receipt is paused or if underlying `apxUSD` transfer / deny-list checks fail between receipt mint and claim [S4][S8].

Docs consistency caveat: the official product overview describes the current flexible Unlock Receipt NFT model, while the technical unlocking page also contains legacy `apxUSD_unlock` wording; the current verified source treats `receipt()` as the live path and ignores deprecated `unlockToken()` in the live flow [S4][S5][S8].

### 8.3 Liquidity and size-dependent exit caveats

| Venue / route | Point-in-time finding | Caveat |
|---|---|---|
| Curve `apyUSD/apxUSD` pool `0xe41be7B340f7c2EDA4DA1e99b42Ee1b228b526b7` | DEXScreener top Ethereum pair reported about `$13.23m` liquidity and about `$25.09m` 24h volume; direct Curve reads showed about 6.05m `apyUSD` and 6.68m `apxUSD` balances in parent snapshot | This route exits to `apxUSD`, not directly to final USD settlement [S1][S14][S15]. |
| Curve quote samples | Parent snapshot quoted 1 `apyUSD` -> 1.321608 `apxUSD`, 100k -> 1.317427 each, 1m -> 1.278121 each, while vault accounting rate was about 1.374366 `apxUSD/apyUSD` | Point-in-time `eth_call` quotes, not guaranteed execution; discount increased with size [S1]. |
| PancakeSwap V3 / Uniswap V4 Ethereum `apyUSD/apxUSD` venues | Market APIs found additional venues with smaller depth than the main Curve venue | API-derived current market data; not fully routed in synthesis inputs [S14][S15]. |
| Curve `apxUSD/USDC` second leg `0xE1B96555BbecA40E583BbB41a11C68Ca4706A414` | Parent snapshot quoted 1 `apxUSD` -> 0.903873 USDC and 1m `apxUSD` -> 885,587.709549 USDC | This second leg controls practical USD exit after `apyUSD -> apxUSD` or receipt claim; point-in-time only [S1]. |
| Historical stress | Longer premium / discount / depeg history was not built in the parent research | `missing_behavior: review_required` for stress modeling [S17]. |

Missing-data behavior: secondary market exit has `missing_behavior: block_automation` for real transactions without fresh route quotes, execution simulation, pause / deny-list / receipt checks, and governance pending-tx refresh; longer market stress history and eligible-liquidator depth are `review_required` [S14][S16][S17].

## 9. Oracle and pricing methodology

`apyUSD` contract conversions use ERC-4626 accounting rather than a Chainlink-style external USD price feed in the reviewed source [S4]. `totalAssets()` returns the vault’s `apxUSD` balance plus `vesting.vestedAmount()` if a vesting contract is configured; current `vesting()` was `0x0D62B4cC02b4B51Ed19DDF41D7a7979CF394C99f` in the parent snapshot [S1][S4]. Apyx’s official `ApyUSDRateView` address is listed in docs and the verified source computes displayed APY from unvested vesting yield over remaining vesting period divided by `ApyUSD.totalAssets()`; this is an APY display formula, not an independent USD NAV proof [S7].

```text
primary_price_source: ERC-4626 internal exchange rate = totalAssets / totalSupply
oracle_follows: apxUSD-denominated vault accounting; not direct USD market price, preferred-share NAV, or secondary-market exit value
update_cadence: continuous on-chain accounting; no feed-style cadence or max-staleness window found for apyUSD share conversion
composite_dependencies: apxUSD, vesting, receipt, AccessManager, deny-list, collateral/custody attestations, market liquidity
observed_market_divergence: parent snapshot showed Curve apyUSD/apxUSD below vault exchange rate and apxUSD/USDC below $1
source_class: onchain + verified source + issuer_docs + market_data
freshness: current for sampled contracts and current point-in-time market data; off-chain reserve cadence only partially verified
confidence: high for apyUSD conversion mechanics, medium/low for external USD/backing/NAV methodology
missing_behavior: review_required before using as Credit Account collateral oracle methodology; block_automation for liquidation/execution without fresh route, governance, and backing-state checks
```

Gearbox-specific main / reserve oracle status: not checked or found in the scoped parent research. If a later integration depends on Gearbox oracle configuration for `apyUSD`, `missing_behavior: review_required` until exact oracle contracts, staleness rules, and market-vs-NAV handling are verified [S17].

## 10. Governance / change-feed watchlist

Refresh these fields against the last accepted state before any production use:

1. `apyUSD` token/proxy address remains `0x38EEb52F0771140d10c4E9A9a72349A329Fe8a6A` [S1][S2][S7].
2. EIP-1967 implementation remains `0xfd616567eCc1607F61073951A1e822f7315bb112`; any implementation change is material [S1][S2].
3. `authority()` remains AccessManager `0xe167330E2Eac88666de253E9607C6d9Ae0cA2824` [S1].
4. AccessManager target delays and role mappings for roles 21-25 remain unchanged, especially immediate pause / receipt rotation, 1-day deny-list / fee changes, and 3-day upgrade / vesting / fee-wallet changes [S1][S16].
5. AccessManager role 0 holder and admin-operation history, including role / target reconfiguration [S1].
6. Safe-compatible role holder `0xf9862EfC1704aC05e687f66E5cD8c130E5663CE2`: threshold, owners, modules, guard, fallback handler, executed transactions, and pending transactions [S1][S16].
7. Safe Transaction Service pending queue: parent research saw 103 unexecuted transactions and did not decode all payloads [S16].
8. `paused()` state for `apyUSD`, Unlock Receipt, and `apxUSD` [S1][S4][S8].
9. `denyList()` addresses for `apyUSD` and `apxUSD`, plus deny-list contract admin and current denied addresses if user-specific flow depends on it [S1][S4].
10. `receipt()` address and receipt implementation / fee curve / pause state / fee wallet [S1][S4][S8].
11. `vesting()` address, vesting period, unvested amount, and `ApyUSDRateView` output dependencies [S1][S7].
12. `unlockingFee()` and `feeWallet()` values for vault-side exit economics [S1][S4].
13. Apyx docs changes: `apyUSD` overview, `apxUSD` overview, unlocking docs, contract-address page, Terms, audit page, and attestation page [S5][S6][S7][S8][S10][S11][S13].
14. Accountable / reserve / attestation data and any new Wolf & Company or custodian reports [S9][S10].
15. Curve / PancakeSwap / Uniswap `apyUSD/apxUSD` liquidity and Curve `apxUSD/USDC` quotes, with size-specific slippage [S14][S15].
16. Any public Apyx incident statement, postmortem, audit update, emergency pause, deny-list event, redemption delay, or reserve-report discrepancy [S9][S10][S11].

Missing-data behavior: governance/admin drift is `review_required`; pending role, implementation, oracle, fee, receipt, deny-list, or liquidity changes before a production action imply `missing_behavior: block_automation` until decoded and reflected in a fresh Preview [S16][S17].

## 11. Data quality and missing-data behavior

| Material field | Current value / finding | source_class | freshness | confidence | missing_behavior |
|---|---|---|---|---|---|
| Token identity | `apyUSD`, exact Ethereum address, 18 decimals | onchain + issuer_docs | current at sampled date | high | continue |
| Proxy / implementation | ERC-1967/UUPS, implementation `0xfd6165...b112` | onchain | current at sampled date | high | review_required if changed |
| Underlying asset | `apxUSD` `0x98A878...4665` | onchain + issuer_docs | current at sampled date | high | review_required if changed |
| Vault accounting | `totalAssets / totalSupply` in `apxUSD`; sample rate around 1.374366 `apxUSD/apyUSD` in market snapshot | onchain | current point-in-time | high | continue for explanation; refresh before use |
| Issuer / protocol | Apyx / APYX Protocol, Preference Capital (BVI) Ltd. and affiliates in Terms | issuer_docs + legal_terms | current docs at access date | medium/high | review_required for legal/process assumptions |
| Backing / reserve model | `apxUSD` dependency on preferred-share / collateral stack; transparency and attestation docs listed | issuer_docs + audit/attestation index | current docs, dated attestations | medium for existence, low for reserve conclusions | cannot_rank_cleanly / review_required |
| Custody / attestations | Wolf & Company March/April 2026 links listed; PDFs not parsed or reconciled | issuer_docs | dated reports | low/medium | review_required |
| Transfer restriction | Pause + deny-list checks on transfer/deposit/redeem paths | onchain + verified source | current at sampled date | high | review_required for user-specific eligibility |
| Legal/product eligibility | No KYB/KYC in `apyUSD` docs; restricted territories in Terms; `apxUSD` primary flows whitelisted | issuer_docs + legal_terms | current docs at access date | medium | review_required |
| Primary redemption | `apyUSD` burn -> vault fee -> net `apxUSD` escrow -> Unlock Receipt NFT -> claim | onchain + verified source + issuer_docs | current at sampled date | high | block_automation without fresh preview / fee / pause / claimability checks |
| Claim token / receipt | Unlock Receipt NFT `0x9bf51...3237`, parent snapshot `paused=false` | onchain + verified source | current at sampled date | high for basic state, medium for full implementation | review_required for full role mapping |
| Secondary liquidity | Curve / PancakeSwap / Uniswap `apyUSD-apxUSD`; Curve `apxUSD-USDC` second leg | market_data + onchain | current point-in-time | high for sampled pool data | block_automation without fresh route quote |
| Historical market stress | Point-in-time market discount observed; longer history not built | market_data | point-in-time only | low/medium | review_required |
| Oracle / pricing | ERC-4626 internal accounting; no dedicated external `apyUSD` USD oracle found in parent research | onchain + verified source | current at sampled date | high for contract mechanics, low for full USD/NAV oracle | review_required |
| AccessManager / roles | AccessManager and role mappings observed; Safe-like holder threshold 3-of-6 | onchain + governance_api | current at sampled date | high for reads, medium for operational policy | review_required |
| Pending governance | 103 unexecuted Safe transactions returned, not fully decoded | governance_api | current at sampled date | medium | review_required; block_automation for action packages |
| Audits | Quantstamp, Certora, Zellic listed; Certora summary located | audit + issuer_docs | dated | medium for existence, low for full scope | review_required |
| Incident history | No confirmed exact-token incident found in bounded parent inputs | unknown / market_data | bounded | low | continue for explanation; review_required for production acceptance |
| Gearbox support/oracle | Not checked / not found in parent research | unknown | unknown | low | continue unless integration depends on it, then review_required |

## 12. Highest-impact unknowns

| Unknown / caveat | Why it matters | missing_behavior | Confidence |
|---|---|---|---|
| Full reserve / custody / attestation contents and current collateral composition were not parsed or reconciled to on-chain supply | `apyUSD` inherits `apxUSD` backing and off-chain preferred-share exposure; dashboard or PDF existence does not prove current coverage in this dossier | `cannot_rank_cleanly` and `review_required` | high |
| Audit and formal-verification PDFs were not fully parsed and mapped to the live implementation, AccessManager, receipt, vesting, and `apxUSD` contracts | Audit existence is not the same as current deployed-scope coverage | `review_required` | high |
| AccessManager admin-operation history and EOA `0xabdd...5e96` operational identity were not fully verified from primary governance records | Role 0 can materially affect access configuration and sampled restricted calls | `review_required` | medium/high |
| Safe-compatible holder modules, guard, fallback handler, and all 103 pending Safe transactions were not decoded | Modules or pending transactions can change execution semantics or pre-stage sensitive actions | `review_required`; `block_automation` before production action packages | medium/high |
| Deny-list contract administration and current denied-address state were not fully expanded | Deny-list state can block transfers, deposits, redemptions, and final `apxUSD` claims | `review_required` | medium/high |
| Unlock Receipt implementation body and full role mapping were not fully expanded | In-flight claims depend on receipt pause, fee curve, claim semantics, and possible global settings | `review_required`; `block_automation` for real exits without fresh receipt checks | medium |
| `apxUSD` primary mint/redeem operational SLA, whitelist process, and weekend/off-hours settlement behavior were not independently verified | `apyUSD` final exit value depends on `apxUSD` settlement and liquidity | `review_required`; `block_automation` for primary-settlement execution | medium/high |
| Longer premium / discount / depeg history was not built | Point-in-time quotes showed a material discount, but stress behavior needs history | `review_required` | medium |
| No dedicated external USD oracle methodology for `apyUSD` was found in parent research | ERC-4626 accounting can miss market discount, `apxUSD` peg stress, receipt friction, and backing impairment | `review_required` before collateral-oracle use | high |
| Gearbox-specific support / oracle configuration was not checked | If this asset is later used in Gearbox, main/reserve oracle and policy state must be exact | `continue` for this dossier; `review_required` for Gearbox integration | low/medium |
| User-specific legal / jurisdiction / eligibility state is not known | Terms and primary `apxUSD` flows impose restrictions outside the token address itself | `review_required`; `block_automation` for state-changing user flows without user/process checks | medium |

## 13. Sources

| ID | URL / local evidence | source_class | accessed | confidence | Used for |
|---|---|---|---|---|---|
| S1 | `https://ethereum-rpc.publicnode.com` plus local raw snapshots `research/eth-mainnet-apyusd/raw/onchain-admin-snapshot-2026-06-04.json` and `research/eth-mainnet-apyusd/raw/onchain-market-snapshot-2026-06-04.json` | onchain | 2026-06-04 | high | Token metadata, proxy slots, implementation, AccessManager, roles/delays, Safe-like reads, pause/deny-list/receipt/vesting/fee values, ERC-4626 totals, Curve quotes. |
| S2 | Etherscan token / contract page, `https://etherscan.io/address/0x38EEb52F0771140d10c4E9A9a72349A329Fe8a6A` | onchain | 2026-06-04 | high | Verified proxy/source, token page, implementation corroboration. |
| S3 | Dedaub contract explorer, `https://app.dedaub.com/ethereum/address/0x38eeb52f0771140d10c4e9a9a72349a329fe8a6a` | onchain | 2026-06-04 | medium | Secondary proxy / ERC-20 metadata corroboration. |
| S4 | Apyx EVM contracts repository, `https://github.com/apyx-labs/evm-contracts` | issuer_docs / onchain | 2026-06-04 | medium | `ApyUSD.sol`, deny-list extension, receipt interfaces, fee curve, APY view source behavior. |
| S5 | Apyx docs, `apyUSD` overview, `https://docs.apyx.fi/product-overview/apyusd-overview` | issuer_docs | 2026-06-04 | medium | Savings-token mechanism, ERC-4626 vault, non-rebasing exchange-rate accrual, permissionless access, flexible redemption. |
| S6 | Apyx docs, `apxUSD` overview, `https://docs.apyx.fi/product-overview/apxusd-overview` | issuer_docs | 2026-06-04 | medium | Underlying `apxUSD`, preferred-share backing description, mint/redeem eligibility context. |
| S7 | Apyx docs, Smart Contract Addresses, `https://docs.apyx.fi/resources/smart-contract-addresses` | issuer_docs | 2026-06-04 | high for listed addresses, medium for dynamic state | Official listed token / view addresses. |
| S8 | Apyx docs, Unlocking `apyUSD` for `apxUSD`, `https://docs.apyx.fi/technical-overview/unlocking` | issuer_docs | 2026-06-04 | medium | Unlock Receipt / cooldown / fee path; caveat that page mixes current receipt wording with legacy unlock-token wording. |
| S9 | Apyx docs, Transparency, `https://docs.apyx.fi/collateral-and-custody/transparency` | issuer_docs | 2026-06-04 | medium | Accountable, Apyx dashboard, Dune dashboard, custodian attestation process. |
| S10 | Apyx docs, Third Party Attestation, `https://docs.apyx.fi/collateral-and-custody/third-party-attestation` | issuer_docs | 2026-06-04 | medium for listed PDFs, low for reserve conclusions | Wolf & Company March / April 2026 attestation links. |
| S11 | Apyx docs, Audits, `https://docs.apyx.fi/resources/audits` | audit | 2026-06-04 | medium for listed reports, low for unresolved finding status | Listed Quantstamp, Certora, and Zellic reports. |
| S12 | Certora public report summary, `https://www.certora.com/reports/apyx-apxusd` | audit | 2026-06-04 | medium | Certora March 2026 summary, issue count, high-severity fixed/confirmed statement. |
| S13 | Apyx Terms of Service, `https://docs.apyx.fi/resources/terms-of-service` | legal_terms | 2026-06-04 | high for published terms, medium for practical enforcement | Restricted-territory / restricted-person framing and APYX Protocol legal entity references. |
| S14 | DEXScreener API and pair page, `https://api.dexscreener.com/latest/dex/tokens/0x38EEb52F0771140d10c4E9A9a72349A329Fe8a6A`, `https://dexscreener.com/ethereum/0xe41be7b340f7c2eda4da1e99b42ee1b228b526b7` | market_data | 2026-06-04 | high for current reported pair data, medium for API-derived market statistics | Secondary venues, liquidity, volume, pair price. |
| S15 | CoinGecko `apyUSD`, `https://www.coingecko.com/en/coins/apyusd` and public API `/api/v3/coins/apyusd` | market_data | 2026-06-04 | medium | Market price, market cap, volume, broader venue context. |
| S16 | Safe Transaction Service and direct on-chain Safe-like reads for `0xf9862EfC1704aC05e687f66E5cD8c130E5663CE2`, `https://safe-transaction-mainnet.safe.global/api/v1/safes/0xf9862EfC1704aC05e687f66E5cD8c130E5663cE2/multisig-transactions/?executed=false&limit=5` | governance | 2026-06-04 | high for threshold / owners / pending-count reads, medium for pending impact | Safe-like role holder, 3-of-6 threshold, pending unexecuted transaction caveat. |
| S17 | Project methodology, `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/methodology.md` | unknown | 2026-06-04 | high | Source-priority rules, asset-section requirements, `missing_behavior` labels. |
