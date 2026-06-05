# Hastra PRIME — transfer, liquidity, oracle, governance research

Report date: 2026-06-04
Asset scope supplied by task: Hastra PRIME (`PRIME`) on Ethereum mainnet (`chain_id: 1`), token `0x19ebb35279A16207Ec4ba82799CC64715065F7F6`.
This report records objective, source-linked facts and unknowns only. It is not an investment recommendation, suitability verdict, or token-selection note.

## Agent-context summary

- Identity pinned on-chain: `name()` = `Hastra PRIME`, `symbol()` = `PRIME`, `decimals()` = 6, token/proxy address `0x19ebb35279A16207Ec4ba82799CC64715065F7F6`; EIP-1967 implementation slot resolves to `0x90fd843c68db38e2de0618AcBB39341CbA5A5abD`. Source: [S1], [S2].
- PRIME is an ERC-4626-style staking vault token over Hastra `wYLDS` (`asset()` / `yieldVault()` = `0x6aD038cA6C04e885630851278ca0a856Ad9a66Cc`). Users can stake wYLDS for PRIME; contract `redeem()` / `withdraw()` exits PRIME back to wYLDS, subject to pause/freeze/oracle conversion. Source: [S2], [S4], [S5], [S9].
- Hastra terms describe the product as USDC -> wYLDS -> PRIME, with wYLDS backed 1:1 by YLDS and PRIME earning wYLDS from Figure Democratized Prime HELOC lending operations. Terms also impose eligibility restrictions, including no U.S. residents/citizens/persons located in the U.S. and no sanctioned/illegal jurisdictions. Source: [S8].
- Transferability is not permissioned by a whitelist in the PRIME contract, but transfers, mint/burn, deposit, and redemption are blocked for frozen sender/receiver addresses and deposit/redeem/mint/withdraw are blocked when paused. Source: [S4], [S5].
- Current on-chain state at Ethereum block `25243546`/`25243612`: PRIME `paused=false`, YieldVault `paused=false`, `getVerifiedNav()` = `1.040904685772521320`, total PRIME supply = `129,096,016.382551`, vault wYLDS assets = `134,374,638.283899`, NAV-adjusted value = `139,871,190.638698` USDC-like units. Source: [S2].
- Secondary Ethereum liquidity is a Uniswap V3 PRIME/USDC 0.01% pool `0x5B70A1582135BD04e39CA94A6a56Fc3A828e3115`; on-chain balances at check time were ~`5,511,009.164971` PRIME and ~`3,268,302.323397` USDC, with DEXScreener reporting ~$9.0m liquidity and ~$11.7m 24h volume. Source: [S2], [S10], [S11].
- Primary price for ERC-4626 conversions is not DEX market price; PRIME reads `FeedVerifier.priceOf(navFeedId)` from `0xdF4ab20fA7752Be52E41e42F1FD667f37964d6a3`. The active feed id is `0x0007c8ed155d952e003b1e15ce7666fea785cfbe216577d578fce3920e997271`; FeedVerifier enforces `defaultMaxStaleness=3600` seconds and returned timestamp `2026-06-04T10:48:41Z`. Source: [S2], [S6], [S7].
- Current sensitive role structure: Safe `0x8D358B8aE881F8ea92C3d07783aBCA21727C6309` is DEFAULT_ADMIN and UPGRADER for PRIME/Yield/FeedVerifier; Safe threshold is 4-of-7 with no modules and no guard. EOA `0xA8C3...faCd` holds PRIME FREEZE/REWARDS/PAUSER and Yield FREEZE/REWARDS/PAUSER/WHITELIST/WITHDRAWAL; EOA `0xf0A5...73CD` holds FeedVerifier UPDATER. Source: [S2], [S12].
- Pending governance/admin change: one unexecuted Safe multisig transaction submitted `2026-06-03T17:42:20Z` would grant YieldVault REWARDS_ADMIN and WHITELIST_ADMIN to the Safe and revoke YieldVault WHITELIST_ADMIN from `0xA8C3...faCd`; it had 1/4 confirmations when checked. Source: [S12].

## Mechanism in one paragraph

Hastra PRIME is an upgradeable Ethereum staking-vault token whose underlying asset is Hastra wYLDS. The public/official user flow is USDC -> wYLDS -> PRIME; wYLDS is described by Hastra terms as backed 1:1 by YLDS, and PRIME accrues wYLDS linked to Figure Democratized Prime HELOC lending operations. PRIME deposits/redemptions use a Chainlink Data Streams-style FeedVerifier NAV/redemption-rate value instead of the raw ERC-4626 share ratio, so token conversions can fail when the oracle is unset, stale, or non-positive. Exit can occur through PRIME redemption to wYLDS if not paused/frozen and if vault liquidity/oracle permits, and ultimate USDC settlement depends on wYLDS redemption mechanics, whitelist/redeem-vault operations, and Hastra eligibility restrictions. Source: [S4], [S5], [S6], [S8], [S9].

## Compact sections 1-5 context used by sections 6-9

### 1. Identity and scope

- Exact scoped asset: Hastra PRIME (`PRIME`), Ethereum mainnet, `0x19ebb35279A16207Ec4ba82799CC64715065F7F6`.
- Verified on-chain calls returned name/symbol/decimals and proxy implementation noted above. Source: [S2].
- Etherscan token page identifies the contract as ERC-20 Source Code (Proxy), implementation `0x90fd843c...CbA5A5abD`. Source: [S1].

### 2. Issuer/protocol and legal/eligibility framing

- Hastra terms are issued by Signum Ltd., described as a BVI company and wholly owned subsidiary of Provenance Cayman Foundation. Source: [S8].
- Terms prohibit use by U.S. residents/citizens/persons located in the U.S. and by sanctioned/illegal jurisdictions, and reserve discretion to verify eligibility or block site/protocol access/property interests as required by law. Source: [S8].
- Missing: no separate KYC/AML onboarding spec, jurisdictional registry contract, or current issuer operating runbook was found in the bounded search. `missing_behavior: review_required` for any automation that assumes a user is eligible to mint/redeem/settle.

### 3. NAV/backing model

```text
nav_model: staking-share / issuer NAV / collateralized vault
```

- PRIME depends on wYLDS as its vault asset and uses a FeedVerifier NAV/redemption-rate value for PRIME<->wYLDS conversions. Source: [S4], [S6].
- Hastra terms state wYLDS is backed 1:1 by YLDS, a yield-bearing stablecoin issued by Figure and SEC-registered, and that Hastra holds YLDS as collateral for wYLDS while not issuing YLDS. Source: [S8].
- PRIME yield source is described as wYLDS from Figure Democratized Prime HELOC lending operations. Source: [S8].
- Missing: no current reserve attestation, YLDS custody report, backing composition report, or NAV construction memo was found. `missing_behavior: review_required` for clean risk ranking; `cannot_rank_cleanly` for any ranking field that depends on reserve/NAV quality.

### 4. Contract admin, multisigs, and sensitive actions

Current observed sensitive holders:

| Contract | Role/action | Holder(s) observed | Holder type | Existing-holder impact | Execution speed |
|---|---:|---|---|---|---|
| PRIME | DEFAULT_ADMIN_ROLE | `0x8D358B8aE881F8ea92C3d07783aBCA21727C6309` | Safe 4-of-7 | indirect/direct depending on role grants/config changes | immediate after Safe threshold; no timelock observed |
| PRIME | UPGRADER_ROLE | `0x8D358B8aE881F8ea92C3d07783aBCA21727C6309` | Safe 4-of-7 | direct/indirect via implementation change | immediate after Safe threshold; no timelock observed |
| PRIME | FREEZE_ADMIN_ROLE | `0xA8C3CF6183D49d5D372f8FC149BD2cb5CFC0faCd` | EOA | direct_freeze / direct_redemption_block | immediate |
| PRIME | PAUSER_ROLE | `0xA8C3CF6183D49d5D372f8FC149BD2cb5CFC0faCd` | EOA | direct_redemption_block / transfer block via paused deposit/redeem functions | immediate |
| PRIME | REWARDS_ADMIN_ROLE | `0xA8C3CF6183D49d5D372f8FC149BD2cb5CFC0faCd` | EOA | direct_dilution/asset growth via rewards distribution caps | immediate |
| PRIME | NAV_ORACLE_UPDATER_ROLE | no current holder among event-identified addresses; previously `0x5f134E...659b3` then revoked | unknown/currently absent | indirect via oracle config if re-granted | review_required |
| YieldVault | DEFAULT_ADMIN_ROLE / UPGRADER_ROLE | `0x8D358B8aE881F8ea92C3d07783aBCA21727C6309` | Safe 4-of-7 | direct/indirect through wYLDS/redeem path | immediate after Safe threshold |
| YieldVault | FREEZE/REWARDS/PAUSER/WHITELIST/WITHDRAWAL | `0xA8C3CF6183D49d5D372f8FC149BD2cb5CFC0faCd` | EOA | direct_freeze / direct_redemption_block / settlement controls | immediate |
| FeedVerifier | DEFAULT_ADMIN_ROLE / UPGRADER_ROLE | `0x8D358B8aE881F8ea92C3d07783aBCA21727C6309` | Safe 4-of-7 | indirect via oracle verifier/feed/staleness/upgrade | immediate after Safe threshold |
| FeedVerifier | UPDATER_ROLE | `0xf0A5BaEBF749562FAE5f3d9d2928357Ae6cd73CD` | EOA | indirect via NAV updates, bounded by verifier logic | immediate |
| FeedVerifier | PAUSER_ROLE | `0xA8C3CF6183D49d5D372f8FC149BD2cb5CFC0faCd` | EOA | direct oracle-read failure if paused updater path stops freshness | immediate |

Source: [S2], [S3], [S12].

Sensitive recent events from on-chain logs:

- FeedVerifier deployed/upgraded and initial feed id set at block `24894016`; YieldVault/PRIME proxies deployed/upgraded at blocks `24901860`/`24901862`. Source: [S2].
- PRIME NAV feed rotated from `0x000700f43b35146a1cb16373ac6225ad597535e928e6dc4d179c3b4225f2b6d3` to active `0x0007c8ed155d952e003b1e15ce7666fea785cfbe216577d578fce3920e997271` around blocks `24945331`/`24945422`. Source: [S2].
- PRIME and YieldVault have been paused and unpaused multiple times; current paused state is false. Most recent pause/unpause observed at blocks `25230418`/`25230421` and `25230599`/`25230601`. Source: [S2].
- Two YieldVault accounts are currently frozen from observed events and direct `frozen(address)` checks: `0xe08d97e151473a848c3d9ca3f323cb720472d015`, `0xa0f1c3ad83e07d97b5e7030e177718be175275ea`. No PRIME freeze events were observed in the same bounded event scan. Source: [S2].

### 5. Audits, formal verification, and incidents

- Public audit/formal-verification report for the current mainnet contracts was not found in the bounded local repo/web search. The local README contains stale/testnet-era statements such as "Not yet deployed - Pending audit and security review" and "Testnet deployment. Not audited" that conflict with the current mainnet deployment; treat as stale source for current audit status. Source: [S3].
- Incidents/events observed in bounded on-chain scan: pauses/unpauses on PRIME/YieldVault and two YieldVault freezes. No exploit/depeg/bridge incident source was found in bounded search. Source: [S2].
- `missing_behavior: review_required` for audit status and incident history if this report is used beyond explanatory MVP reasoning.

## 6. Transferability, redemption, and liquidity

### 6.1 Transfer restrictions and eligibility/KYC

- PRIME contract transfer logic checks a `frozen` mapping in `_update`; if `from` or `to` is frozen, the transfer/mint/burn path reverts with `AccountIsFrozen()`. Source: [S4].
- PRIME deposit, mint, redeem, and withdraw are gated by `whenNotPaused`; when the contract is paused, these primary vault actions revert. Source: [S4].
- There is no PRIME whitelist/allowlist check in the transfer path found in `StakingVault.sol`. Source: [S4].
- Eligibility restrictions are legal/product-side rather than visible as a PRIME transfer whitelist: Hastra terms exclude U.S. persons/locations and sanctioned/illegal jurisdictions and reserve the ability to determine eligibility, request information, block site access, and block interests in property as required by law. Source: [S8].

Field record:

```text
transfer_restrictions: frozen-address transfer block; paused vault action block; no PRIME transfer whitelist found
eligibility_kyc: legal/product-side restrictions in Hastra Terms; on-chain PRIME transfer whitelist not found
source_class: onchain + legal_terms
freshness: current for onchain; dated/current for terms last updated 2025-12-03
confidence: high for contract behavior; medium for full eligibility process
missing_behavior: review_required for user-specific eligibility/redemption assumptions
```

### 6.2 Freeze, blacklist, forced-transfer, registry mechanics

- PRIME has `freezeAccount(address)` and `thawAccount(address)` gated by `FREEZE_ADMIN_ROLE`; `frozen(address)` is public. Source: [S4].
- PRIME does not expose a forced-transfer function in the reviewed source; frozen accounts are blocked from sending and receiving due `_update` checks. Source: [S4].
- YieldVault has the same freeze/thaw transfer block, and its `completeRedeem(address user)` explicitly checks `frozen[user]` because requestRedeem already moved shares into the contract. Source: [S5].
- Compliance docs state frozen accounts cannot transfer, receive, deposit, request redemptions, or claim rewards; they can be burned by an admin for redemption completion. The doc is repo documentation, not a direct on-chain state read; contract source is primary for exact mechanics. Source: [S9].
- Observed current state includes two frozen YieldVault users, both still frozen; no PRIME freezes in the bounded scan. Source: [S2].

Field record:

```text
freeze_blacklist: yes, account-level freeze in PRIME and wYLDS/YieldVault
forced_transfer: not found in PRIME source; admin burn path discussed in compliance docs for frozen-account remediation, not regular transfer
registry_mechanics: no PRIME registry contract found; YieldVault has whitelist for withdrawal/admin flow
source_class: onchain + issuer_docs
freshness: current
confidence: high for freeze; medium for no forced-transfer because absence is based on reviewed source/search
missing_behavior: continue for explanation; review_required for compliance-action automation
```

### 6.3 Primary redemption path and settlement process

Observed contract path:

1. PRIME holder calls `redeem(shares, receiver, owner)` or `withdraw(assets, receiver, owner)` on PRIME when not paused and not frozen.
2. PRIME calculates assets using `_convertToAssets(shares)`, which calls `getVerifiedNav()` and uses `shares * NAV / 1e18`.
3. The returned asset is wYLDS (`0x6aD038...66Cc`), not USDC. Source: [S4].
4. Ultimate wYLDS->USDC settlement is handled by YieldVault mechanics: direct ERC-4626 `withdraw`/`redeem` are disabled and revert with `Use requestRedeem/completeRedeem`; users call `requestRedeem(shares)`, then a `REWARDS_ADMIN_ROLE` account calls `completeRedeem(address user)` to pay USDC from `redeemVault` if it has sufficient USDC and the user is not frozen. Source: [S5].
5. YieldVault `redeemVault()` currently returns `0xA8C3CF6183D49d5D372f8FC149BD2cb5CFC0faCd`; `getWhitelistedAddresses()` returned `0xEcDEb94b4f464d7Be68B48cf7786Dc5FE19b59Ea` and `0xA8C3CF6183D49d5D372f8FC149BD2cb5CFC0faCd`. Source: [S2].

No claim token/NFT/receipt was found for PRIME redemption. YieldVault uses an internal `pendingRedemptions(address)` mapping and events, not a transferable claim token, in the reviewed source. Source: [S5].

Field record:

```text
primary_redemption_path: PRIME -> wYLDS through PRIME ERC-4626 redeem/withdraw; wYLDS -> USDC through YieldVault requestRedeem/completeRedeem
cooldown_queue_settlement: no PRIME-specific cooldown found; YieldVault has pendingRedemptions and admin-completed settlement, with no public SLA found
claim_token_receipt: no transferable claim token/NFT found; internal pending redemption mapping/events in YieldVault
claim_readiness: depends on YieldVault redeemVault USDC balance, admin completion, non-frozen user, and eligibility/product process
source_class: onchain + legal_terms + issuer_docs
freshness: current
confidence: high for contract mechanics; low/medium for off-chain settlement timing because no SLA source found
missing_behavior: review_required for any redemption/settlement automation; block_automation if a concrete exit must be executed without a live route quote or redemption preview
```

### 6.4 Secondary liquidity venues and size-dependent exit caveats

Ethereum mainnet venue:

- DEXScreener returned one Ethereum pair for the scoped token: Uniswap V3 PRIME/USDC pool `0x5B70A1582135BD04e39CA94A6a56Fc3A828e3115`, fee tier `100` (0.01%). Source: [S10], [S11].
- On-chain pool checks: `token0=PRIME`, `token1=USDC`, `fee=100`, `liquidity=5351230848763709`, `balanceOf(pool)` = ~`5.511m` PRIME and ~`3.268m` USDC. Source: [S2].
- DEXScreener reported `priceUsd=1.040`, 24h volume `$11,701,620.17`, 24h tx count 18 buys/24 sells, liquidity `$9,001,343.47`, base `5,511,009` PRIME and quote `3,268,315` USDC. Source: [S10].
- CoinGecko reported PRIME price ~$1.04, 24h volume ~$21.3m globally across 5 exchanges/6 markets and included non-Ethereum/Solana venues; those global figures are not chain-specific for the Ethereum token and should not be used as Ethereum exit depth. Source: [S11].

Uniswap V3 quote samples from the on-chain Quoter at report time:

| Sell size | Quoted USDC out | Effective USDC/PRIME | Caveat |
|---:|---:|---:|---|
| 1,000 PRIME | 1,040.18 | 1.040182 | near spot |
| 10,000 PRIME | 10,401.80 | 1.040180 | near spot |
| 100,000 PRIME | 104,016.25 | 1.040163 | near spot |
| 1,000,000 PRIME | 1,039,984.13 | 1.039984 | modest impact in quoted pool |
| 3,000,000 PRIME | 3,118,763.86 | 1.039588 | still near spot in quote, but large fraction of pool inventory |
| 5,000,000 PRIME | 3,268,261.82 | 0.653652 | quote drains almost all visible USDC; high cliff risk |

Source: [S2]. These are point-in-time `eth_call` quotes, not guaranteed executable settlement.

Historical premium/discount/stress:

- CoinGecko 30-day daily API sample returned 31 points with min price `$1.034466`, max `$1.040575`, last `$1.040213`, average daily volume about `$7.14m`, min daily volume about `$0.48m`, max daily volume about `$30.30m`. Source: [S11].
- Longer history and event-context for early trading was not established in this bounded pass; Uniswap pool creation timestamp from DEXScreener was `2026-05-05T14:27:11Z`. Source: [S10], [S2].

Field record:

```text
secondary_liquidity: Uniswap V3 Ethereum PRIME/USDC 0.01% pool; non-Ethereum venues exist in CoinGecko global data but are out of scoped Ethereum exit depth
current_depth: ~$9.0m DEXScreener liquidity; ~3.27m USDC pool balance; size-dependent quote cliff around visible USDC depth
historical_depeg_discount: no material 30-day price break observed in CoinGecko daily sample; longer history not verified
eligible_liquidator_depth: unknown; legal eligibility/compliance gating may matter off-chain even when DEX transfer is technically possible
source_class: market_data + onchain
freshness: current point-in-time
confidence: high for current pool/quote; medium for historical stress due short observable history
missing_behavior: block_automation for real exits without fresh route quote; review_required for compliance-gated exit eligibility
```

## 7. Oracle and pricing methodology

### 7.1 Primary price/oracle source

- PRIME conversion functions `_convertToShares` and `_convertToAssets` call `getVerifiedNav()`; there is no fallback to a raw ERC-4626 ratio when NAV oracle is unset/stale. Source: [S4].
- `getVerifiedNav()` reads `IFeedVerifier(navOracle).priceOf(navFeedId)` and rejects non-positive prices. Source: [S4].
- Current PRIME `navOracle` is `0xdF4ab20fA7752Be52E41e42F1FD667f37964d6a3`; current `navFeedId` is `0x0007c8ed155d952e003b1e15ce7666fea785cfbe216577d578fce3920e997271`. Source: [S2].
- FeedVerifier contract docs/source describe it as an on-chain verifier for Chainlink Data Streams Schema v7 redemption rates. It stores latest price per feed id, enforces allowed feed id, and `priceOf(feedId)` reverts if no report, zero/non-positive price, or stale price. Source: [S6], [S7].

Field record:

```text
primary_price_source: Chainlink Data Streams-style FeedVerifier redemption-rate/NAV feed, not DEX market price
oracle_follows: NAV/exchange/redemption rate for PRIME-to-wYLDS conversion; exact off-chain construction not fully documented in found sources
source_class: onchain + issuer_docs
freshness: current
confidence: high for on-chain use; medium for off-chain methodology details
missing_behavior: review_required before using as Credit Account collateral oracle methodology
```

### 7.2 Cadence, staleness, and dependencies

- FeedVerifier active feed price at check: `priceByFeed(activeFeedId)=1040904685772521320` (`1.040904685772521320` scaled 1e18). Source: [S2].
- Feed timestamp at check: `timestampByFeed(activeFeedId)=1780570121` = `2026-06-04T10:48:41Z`. Source: [S2].
- `defaultMaxStaleness()` on-chain returned `3600` seconds. Source: [S2].
- FeedVerifier source sets `defaultMaxStaleness = 3600` in initializer; docs text says 24h in one place, so on-chain/source code should override docs for current behavior. Source: [S6], [S7].
- FeedVerifier depends on Chainlink VerifierProxy `0x5A1634A86e9b7BfEf33F0f3f3EA3b1aBBc4CC85F` and an updater account with `UPDATER_ROLE`. Source: [S3], [S6], [S2].

Field record:

```text
update_cadence: not explicitly documented; observed recent feed timestamp and last reward timestamp are near report time
staleness_window: 3600 seconds on-chain default unless per-feed override is set
composite_dependencies: Chainlink Data Streams report/API, Chainlink VerifierProxy, FeedVerifier admin/updater, active feed id, wYLDS/YLDS/HELOC NAV source
source_class: onchain + issuer_docs
freshness: current
confidence: high for staleness config; medium for update cadence
missing_behavior: review_required for exact cadence/off-chain NAV construction
```

### 7.3 Market-vs-NAV mismatch risk

- The oracle value used by PRIME was `1.0409046858`, while DEXScreener/CoinGecko market values were about `$1.040`; current divergence was small at report time. Source: [S2], [S10], [S11].
- The oracle is a NAV/redemption-rate feed and can miss practical exit frictions that do not change reported NAV immediately: DEX liquidity cliff, freeze/eligibility, redemption delay, YieldVault redeemVault USDC availability, underlying YLDS/collateral impairment, or paused contracts. Source: [S4], [S5], [S6], [S8], [S10].
- If FeedVerifier price becomes stale or absent, PRIME deposit/redeem/mint/withdraw conversions revert through `getVerifiedNav()`. Source: [S4], [S6].

Field record:

```text
observed_oracle_market_divergence: small at report time (~1.0409 NAV vs ~1.040 market)
missed_risk_classes: market depeg/liquidity break, issuer freeze, redemption delay, redeemVault balance shortfall, legal eligibility, underlying NAV impairment
source_class: onchain + market_data + legal_terms
freshness: current
confidence: medium/high
missing_behavior: review_required for production collateral valuation; block_automation for liquidation/execution without fresh market route and oracle check
```

## 8. Governance / change-feed watchlist

Watchlist items to compare against future runs:

1. PRIME proxy implementation slot: current `0x90fd843c68db38e2de0618AcBB39341CbA5A5abD`. Any change is material. Source: [S2].
2. YieldVault proxy implementation slot: current `0xDA962f7a0308e9D4F2F60c5Aab94f173C26d1A1D`. Any change is material because it controls wYLDS redemption and rewards. Source: [S2].
3. FeedVerifier proxy implementation slot: current `0xbC6023cb49F8E8cA6cef563d5FD97ba4C6A5D937`. Any change is material for oracle behavior. Source: [S2].
4. Active PRIME `navOracle`, `navFeedId`, FeedVerifier `allowedFeedId`, `defaultMaxStaleness`, `maxStalenessByFeed(activeFeedId)`, `priceByFeed`, and `timestampByFeed`. Source: [S2], [S6].
5. Safe `0x8D358B8aE881F8ea92C3d07783aBCA21727C6309` threshold/owners/modules/guard and pending multisig transactions. Current Safe: 4-of-7, no modules, no guard. Source: [S12].
6. Pending Safe transaction `0x95b5137c13d8a10592d00bae1404dcf05cf25597dc2c88d040ef728524b0895f`: if executed, it changes YieldVault admin distribution by granting Safe REWARDS_ADMIN/WHITELIST_ADMIN and revoking WHITELIST_ADMIN from EOA `0xA8C3...faCd`. Source: [S12].
7. EOA `0xA8C3...faCd` roles on PRIME/Yield/Feed; it currently has immediate freeze/pause/rewards/withdrawal/whitelist powers across the redemption path. Source: [S2].
8. FeedVerifier updater EOA `0xf0A5...73CD`; loss or compromise affects freshness/NAV update path. Source: [S2].
9. PRIME/YieldVault pause/unpause and AccountFrozen/AccountThawed events. Current recent on-chain history includes repeated pauses/unpauses and two YieldVault freezes. Source: [S2].
10. Hastra Terms changes, especially eligibility, redemption, collateral/backing, fee, and property-blocking language. Source: [S8].
11. Uniswap pool `0x5B70...3115` liquidity/balances/fee tier and route quote for any size-sensitive exit; DEX liquidity is concentrated and can cliff before nominal pool TVL is exhausted. Source: [S10], [S2].
12. Public reserve/NAV reports, YLDS backing/custody attestations, audit reports, bug bounty disclosures, and incident statements if published later. Current bounded pass did not find clean current artifacts. Source: [S3], [S8].

Field record:

```text
governance_model: Safe-administered upgradeable contracts plus immediate EOA operational roles; no timelock observed
pending_changes: one Safe tx affecting YieldVault roles, unexecuted with 1/4 confirmations at check time
source_class: onchain + governance + legal_terms + market_data
freshness: current
confidence: high for on-chain/Safe state; medium for absence of broader governance sources
missing_behavior: review_required for admin/governance drift; block_automation if pending role/oracle/implementation tx executes before action package is refreshed
```

## 9. Data quality and missing-data behavior

### 9.1 Material field quality table

| Field | Current value / finding | source_class | freshness | confidence | missing_behavior |
|---|---|---|---|---|---|
| Token identity | Hastra PRIME / PRIME / 6 decimals / exact Ethereum address | onchain | current | high | continue |
| Proxy/implementation | EIP-1967 proxy with implementation `0x90fd...5abD` | onchain | current | high | review_required if changed |
| Underlying asset | wYLDS YieldVault `0x6aD0...66Cc` | onchain | current | high | review_required if changed |
| Legal eligibility | Terms exclude U.S. and sanctioned/illegal jurisdictions; Hastra may verify/block | legal_terms | dated/current | high for text; medium for process | review_required |
| PRIME transfer restriction | Freeze-based transfer block; no whitelist found | onchain | current | high | continue |
| Forced transfer | No PRIME forced-transfer function found | onchain | current | medium | review_required before compliance conclusions |
| PRIME redemption | PRIME redeem/withdraw returns wYLDS using NAV oracle | onchain | current | high | review_required for full USDC settlement |
| wYLDS redemption | requestRedeem + admin completeRedeem from redeemVault USDC | onchain | current | high | block_automation without live settlement/eligibility check |
| Claim token/NFT | none found; internal pendingRedemption mapping | onchain | current | medium/high | continue |
| Secondary ETH liquidity | Uniswap V3 PRIME/USDC pool only in DEXScreener Ethereum token-pairs API | market_data + onchain | current | high | block_automation without fresh route quote |
| Market history | 30-day CG sample stable around 1.034-1.041; longer stress history not established | market_data | current | medium | continue for explanation; review_required for stress modeling |
| Oracle source | FeedVerifier Chainlink Data Streams Schema v7 redemption-rate/NAV feed | onchain + issuer_docs | current | high for contract use; medium for off-chain formula | review_required |
| Staleness | FeedVerifier defaultMaxStaleness = 3600s on-chain | onchain | current | high | review_required if unset/changed |
| Admin Safe | Safe 4-of-7, no modules/guard | governance/onchain | current | high | review_required if changed |
| EOA operational roles | `0xA8C3...faCd` immediate operational powers | onchain | current | high | review_required |
| Pending governance | one unexecuted Safe tx affects YieldVault role split | governance | current | high | review_required; block_automation if execution affects action package |
| Reserve/NAV reports | not found | unknown | unknown | low | cannot_rank_cleanly / review_required |
| Audit/current security review | not found; local README stale/conflicting | issuer_docs/unknown | stale/unknown | low | review_required |
| Gearbox support/oracle notes | not checked/found in this scoped research pass | unknown | unknown | low | continue unless Gearbox integration depends on it, then review_required |

### 9.2 Highest-impact unknowns

1. Exact off-chain NAV/redemption-rate construction for the active Chainlink Data Streams feed was not found. On-chain use is clear; feed methodology inputs are not. `missing_behavior: review_required` for collateral valuation.
2. Current reserve/custody/attestation reporting for wYLDS/YLDS backing was not found. Terms describe backing, but no current reserve report was located. `missing_behavior: cannot_rank_cleanly` and `review_required`.
3. User-specific eligibility/KYC/redemption process and SLA are not fully specified in found sources. `missing_behavior: review_required`; `block_automation` for executing a real exit without eligibility and settlement confirmation.
4. Audit/current security-review report for deployed implementations was not found. `missing_behavior: review_required`.
5. NAV_ORACLE_UPDATER_ROLE has no current holder among event-identified addresses after revocation from deployer; DEFAULT_ADMIN Safe can regrant, but current operational update path for PRIME `setNavOracle` requires role regrant. `missing_behavior: review_required` for oracle-configuration-change workflows.
6. Ethereum DEX liquidity is deep for small/medium exits but cliffs around visible USDC pool inventory; route quotes must be refreshed at action time. `missing_behavior: block_automation` for size-sensitive exits.

## Source list

[S1] Etherscan token page, `https://etherscan.io/token/0x19ebb35279a16207ec4ba82799cc64715065f7f6`; source_class: onchain explorer; accessed: 2026-06-04; confidence: high for explorer-displayed proxy identity, medium for dynamic token stats.

[S2] Direct Ethereum JSON-RPC / Foundry `cast` calls to Ethereum mainnet via `https://ethereum-rpc.publicnode.com` at blocks `25243546` and `25243612`; source_class: onchain; accessed: 2026-06-04; confidence: high. Calls included EIP-1967 implementation slots, `name/symbol/decimals`, `asset`, `yieldVault`, `navOracle`, `navFeedId`, `paused`, `totalSupply`, `totalAssets`, `getVerifiedNav`, `getTotalValueAtNav`, `hasRole`, FeedVerifier `allowedFeedId/defaultMaxStaleness/priceByFeed/timestampByFeed`, YieldVault `redeemVault/getWhitelistedAddresses`, role/config/pause/freeze event logs, Uniswap pool `token0/token1/fee/liquidity/slot0/balances`, and Uniswap Quoter samples.

[S3] Hastra Ethereum vault deployment/source repo, `https://github.com/provenance-io/hastra-eth-vault` at commit `1b91d4eb0eca9bd71b1284cd7d0cb05279e2affd`; source_class: issuer_docs / source repo; accessed: 2026-06-04; confidence: high for source code matching deployed implementation addresses where verified by Etherscan/on-chain slots, medium for stale README status text.

[S4] `StakingVault.sol`, `https://github.com/provenance-io/hastra-eth-vault/blob/1b91d4eb0eca9bd71b1284cd7d0cb05279e2affd/contracts/StakingVault.sol`; source_class: issuer source code; accessed: 2026-06-04; confidence: high.

[S5] `YieldVault.sol`, `https://github.com/provenance-io/hastra-eth-vault/blob/1b91d4eb0eca9bd71b1284cd7d0cb05279e2affd/contracts/YieldVault.sol`; source_class: issuer source code; accessed: 2026-06-04; confidence: high.

[S6] `FeedVerifier.sol`, `https://github.com/provenance-io/hastra-eth-vault/blob/1b91d4eb0eca9bd71b1284cd7d0cb05279e2affd/chainlink-hub/contracts/FeedVerifier.sol`; source_class: issuer source code / oracle; accessed: 2026-06-04; confidence: high for contract behavior.

[S7] `FeedVerifier.md`, `https://github.com/provenance-io/hastra-eth-vault/blob/1b91d4eb0eca9bd71b1284cd7d0cb05279e2affd/chainlink-hub/docs/FeedVerifier.md`; source_class: issuer_docs / oracle docs; accessed: 2026-06-04; confidence: medium because docs contained a staleness-default mismatch with source/on-chain state.

[S8] Hastra Terms of Use, `https://hastra.io/terms`; source_class: legal_terms; accessed: 2026-06-04; confidence: high for published terms text, medium for operational process details not specified there.

[S9] Hastra repo compliance/roles/architecture docs, especially `docs/COMPLIANCE.md`, `docs/ROLES.md`, `docs/ARCHITECTURE.md` under `https://github.com/provenance-io/hastra-eth-vault/tree/1b91d4eb0eca9bd71b1284cd7d0cb05279e2affd/docs`; source_class: issuer_docs; accessed: 2026-06-04; confidence: medium/high when consistent with contract source, medium when describing operations not directly observed on-chain.

[S10] DEXScreener API / token pair page, `https://api.dexscreener.com/token-pairs/v1/ethereum/0x19ebb35279A16207Ec4ba82799CC64715065F7F6` and `https://dexscreener.com/ethereum/0x5b70a1582135bd04e39ca94a6a56fc3a828e3115`; source_class: market_data; accessed: 2026-06-04; confidence: high for current reported pair data, medium for API-derived market cap/FDV.

[S11] CoinGecko Hastra PRIME page/API, `https://www.coingecko.com/en/coins/hastra-prime` and public API `/api/v3/coins/hastra-prime`; source_class: market_data; accessed: 2026-06-04; confidence: medium because global stats include non-Ethereum markets and may not equal Ethereum-mainnet exit liquidity.

[S12] Safe Transaction Service and on-chain Safe calls for `0x8D358B8aE881F8ea92C3d07783aBCA21727C6309`, `https://safe-transaction-mainnet.safe.global/api/v1/safes/0x8D358B8aE881F8ea92C3d07783aBCA21727C6309/` and multisig transaction endpoint; source_class: governance; accessed: 2026-06-04; confidence: high for Safe owners/threshold/pending tx returned by service and confirmed via Safe contract calls where applicable.
