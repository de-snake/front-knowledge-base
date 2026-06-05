# Apyx apxUSD — transfer, liquidity, oracle, governance research

Report date: 2026-06-04 UTC
Analyst: Hermes operator recovery after repeated Kanban worker crashes
Task scope: methodology sections 6, 7, and 8 only — transferability/redemption/liquidity; oracle/pricing methodology; governance/change-feed watchlist.
Input asset: Ethereum mainnet (`chain_id: 1`), `0x98A878b1Cd98131B271883B390f68D2c90674665`, symbol `apxUSD`, intended use unknown.
Output type: objective source-linked facts, not token selection, ranking, suitability verdict, or investment recommendation.

Related evidence:

- `research/eth-mainnet-apxusd/onchain-admin.md`
- `research/eth-mainnet-apxusd/issuer-backing-security.md`
- `research/eth-mainnet-apxusd/raw/onchain-admin-snapshot-2026-06-04.json`
- `research/eth-mainnet-apxusd/raw/dexscreener-apxusd-2026-06-04.json`
- `research/eth-mainnet-apxusd/raw/safe-pending-2026-06-04.json`

## Source index

| ID | URL / local evidence | source_class | freshness | accessed | confidence | Notes |
|---|---|---:|---:|---:|---:|---|
| S1 | `research/eth-mainnet-apxusd/onchain-admin.md` and raw snapshot | onchain | current | 2026-06-04 | high | Exact token controls: pause/deny-list/mint/upgrade/AdminManager role state. |
| S2 | `research/eth-mainnet-apxusd/issuer-backing-security.md` | issuer_docs / onchain | current | 2026-06-04 | medium/high | Issuer/backing/security context. |
| S3 | `https://docs.apyx.fi/product-overview/apxusd-overview` | issuer_docs | current | 2026-06-04 | medium | Official apxUSD docs: collateral allocation, peg model, eligible mint/redemption, external pools. |
| S4 | `https://docs.apyx.fi/product-overview/apyusd-overview` | issuer_docs | current | 2026-06-04 | medium | apyUSD docs show apxUSD as underlying and describe permissionless vault wrapper over apxUSD. |
| S5 | `research/eth-mainnet-apxusd/raw/dexscreener-apxusd-2026-06-04.json` | market_data | current | 2026-06-04 | medium | DEXScreener snapshot for apxUSD and related apyUSD/apxUSD markets. |
| S6 | `research/eth-mainnet-apxusd/raw/evm-contracts/src/ApxUSD.sol` | onchain | current | 2026-06-04 | medium/high | Source for pause, deny-list, supply-cap, mint, UUPS, CCIP admin. |
| S7 | `research/eth-mainnet-apxusd/raw/evm-contracts/src/exts/ERC20DenyListUpgradable.sol` | onchain | current | 2026-06-04 | medium/high | Source for deny-list checks on sender and receiver. |
| S8 | `research/eth-mainnet-apxusd/raw/safe-pending-2026-06-04.json` | governance | current | 2026-06-04 | medium | Safe Transaction Service pending transaction snapshot; not exhaustively decoded. |
| S9 | `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/methodology.md` | unknown | current | 2026-06-04 | high | Methodology labels and missing-data behavior. |

## Agent-context summary

apxUSD has ordinary ERC-20 transfer methods, but it is not operationally equivalent to an unrestricted stablecoin. The token can be paused, checks a shared deny-list on sender/receiver, is UUPS-upgradeable, and is minted through AccessManager/MinterV0 controls. Primary mint/redemption is restricted to eligible whitelisted participants in permitted jurisdictions, while general users are expected to use external liquidity pools. DEXScreener showed meaningful Ethereum apxUSD/USDC Curve liquidity at extraction, but also point-in-time prices below $1 and route-dependent differences. Pricing should be modeled as issuer/NAV/redeemability plus market-route evidence, not as token-native oracle truth.

## 6. Transferability, redemption, and liquidity

### 6.1 Transfer restrictions and eligibility / KYC requirements

- Source `ApxUSD.sol` includes `ERC20PausableUpgradeable` and `ERC20DenyListUpgradable`; source `ERC20DenyListUpgradable` checks both `from` and `to` against the active AddressList before ERC-20 updates. Sources: S6/S7 medium/high.
- Onchain snapshot: `paused=false`, `denyList=0x2c271ddF484aC0386d216eB7eB9Ff02D4Dc0F6AA`. Source: S1 high.
- Official docs: eligible participants in permitted jurisdictions who are whitelisted may mint and redeem apxUSD through designated issuance/redemption pathways; general users can acquire apxUSD through external liquidity pools and swaps. Source: S3 medium.
- Legal/user-specific eligibility was not validated in this card. `missing_behavior: review_required` for primary mint/redeem access.

Field record:

```text
transfer_restrictions: ERC-20 transfers exist but are pause- and deny-list-sensitive; primary issuance/redemption is whitelisted/eligible-participant gated
eligibility_kyc: eligible whitelisted participants for mint/redeem; general users via external pools per docs
source_class: onchain + verified_source + issuer_docs
freshness: current for onchain; current docs as accessed
confidence: high for contract behavior; medium for full eligibility process
missing_behavior: review_required for user-specific eligibility and redemption assumptions
```

### 6.2 Freeze, blacklist, forced-transfer, registry mechanics

- The active restriction primitive found in apxUSD source is a shared deny-list registry, not a USDat-style forced-transfer role. Source: S6/S7.
- `setDenyList(address)` is controlled through AccessManager role `23`, with Safe-like `0xf986...3CE2` and an observed 86,400 second / 1-day delay. Source: S1 high.
- No general forced-transfer/seizure function was identified in `ApxUSD.sol`; ordinary burn functionality is holder/allowance-based through ERC20Burnable. Source: S6.
- Deny-list administration and current denied accounts were not fully expanded. `missing_behavior: review_required` before compliance-action automation.

Field record:

```text
freeze_blacklist: yes, deny-list registry blocks transfers/mints/burns involving denied addresses; pause can block token flow globally
forced_transfer: no general forced-transfer function identified in ApxUSD source
registry_mechanics: shared AddressList at 0x2c271d...F6AA; registry replacement via AccessManager role 23
source_class: onchain + verified_source
freshness: current
confidence: high for deny-list/pause; medium for absence of forced-transfer because review was bounded to ApxUSD source
missing_behavior: review_required before compliance-action automation
```

### 6.3 Primary redemption path and settlement process

- Official docs say eligible participants in permitted jurisdictions who are whitelisted, such as institutional market makers, may mint and redeem apxUSD through designated issuance and redemption pathways. Source: S3 medium.
- Redemptions settle in USDC; protocol does not transfer preferred shares directly to redeeming participants. In drawdown scenarios, protocol would sell preferred shares to USDC to facilitate redemption. Source: S3 medium.
- Docs say mint/redemption requests are processed quickly and that liquidity may be more limited outside traditional trading hours and weekends, though a buffer remains available. This pass did not verify a live primary redemption SLA or quote. Source: S3 medium.
- General users can use external liquidity pools but may not have primary redemption access. Source: S3 medium.

Field record:

```text
primary_redemption_path: whitelisted/eligible participant redemption pathway settling in USDC; general users rely on external pools
cooldown_queue_settlement: docs say requests processed quickly but this pass did not validate SLA or live queue
claim_token_receipt: none identified for apxUSD itself; apyUSD wrapper has separate receipt mechanics
claim_readiness: depends on eligibility, deny-list/pause state, issuer liquidity buffer, and live redemption pathway
source_class: issuer_docs + onchain controls
freshness: current docs/onchain snapshot
confidence: medium
missing_behavior: review_required for exact primary redemption eligibility/SLA; block_automation for real exits without Preview
```

### 6.4 Secondary liquidity venues and size-dependent exit caveats

DEXScreener snapshot saved in S5 showed these relevant Ethereum venues at extraction time:

| Chain | DEX | Pair / address | priceUsd | liquidity_usd | volume_24h_usd | Evidence |
|---|---|---|---:|---:|---:|---|
| Ethereum | Curve | `0xE1B96555BbecA40E583BbB41a11C68Ca4706A414` apxUSD/USDC | `0.9716` | `38,260,350.97` | `57,481,401.95` | S5 medium |
| Ethereum | Uniswap v4 | pool id `0x2480...63b1` apxUSD/USDC | `0.9999` | `10,995,035.91` | `522,474.55` | S5 medium |
| Ethereum | PancakeSwap v3 | `0x1D8177897FC90819CF644fa84B3247AC690985D5` apxUSD/USDC | `0.9944` | `2,987,692.46` | `222,990.77` | S5 medium |
| Ethereum | Curve | `0xe41be7B340f7c2EDA4DA1e99b42Ee1b228b526b7` apyUSD/apxUSD | apyUSD leg price in apxUSD; relevant to apyUSD exits | `14,261,672.19` | `21,185,031.44` | S5 medium |

Liquidity caveats:

- API values are point-in-time and not executable quotes.
- Different venues showed different prices around the same extraction window; this matters for market-vs-NAV and route selection.
- The largest apxUSD/USDC venue in the snapshot was Curve, but its price was below $1; primary redemption eligibility may be needed to arbitrage or exit at NAV. Source: S3/S5.

Field record:

```text
secondary_liquidity: Curve, Uniswap v4, PancakeSwap v3 apxUSD/USDC venues; apyUSD/apxUSD venues also relevant as apxUSD liquidity sink/source
current_depth: DEXScreener top Curve apxUSD/USDC liquidity about $38.26m and 24h volume about $57.48m at extraction
historical_depeg_discount: point-in-time API prices included apxUSD below $1; longer history not established
eligible_liquidator_depth: unknown for primary redemption because eligibility/whitelist matters; DEX route depth must be quoted live
source_class: market_data + issuer_docs + onchain
freshness: current point-in-time
confidence: medium for current venues; low for historical stress
missing_behavior: block_automation for real exits without fresh route quote; review_required for redemption eligibility
```

## 7. Oracle and pricing methodology

### 7.1 Primary price / oracle source

- apxUSD token source does not expose a holder-facing Chainlink-style price feed or NAV oracle in the reviewed contract. It implements token/admin/mint/deny-list controls. Source: S6.
- Official docs describe a peg/backing model: preferred-share collateral, overcollateralized issuance, cross-market arbitrage, tail hedging, and USDC primary redemption for eligible whitelisted participants. Source: S3.
- Therefore apxUSD's practical valuation depends on issuer NAV/backing process, primary redemption access, and external market routes; it is not directly solved by an on-token oracle. Sources: S2/S3/S5/S6.

Field record:

```text
primary_price_source: issuer NAV/redeemability plus external market price; no token-native price oracle found in apxUSD source
oracle_follows: backing/NAV/redemption and DEX market price, not automatic token contract accounting
source_class: issuer_docs + onchain + market_data
freshness: current point-in-time
confidence: medium
missing_behavior: review_required before using as Credit Account collateral oracle methodology
```

### 7.2 Cadence, staleness, and dependencies

- No token-native staleness window was identified for apxUSD price. Source: S6.
- Official transparency docs point to Accountable, Apyx app, and Dune dashboards, plus monthly Wolf & Company attestations. This pass did not establish a machine-readable NAV cadence or reconcile data to onchain supply. Source: S2.
- Dependencies include collateral dashboards/attestations, DAT preferred-share valuation and liquidity, custody, eligible primary redemption, deny-list/pause/admin state, DEX routes, and pending governance/Safe operations. Sources: S1/S2/S3/S5/S8.

Field record:

```text
update_cadence: unknown for issuer NAV/collateral dashboards in this pass; monthly attestations listed for March/April 2026; onchain state updates live by RPC
staleness_window: none found in token contract; dashboard/attestation/market data require freshness checks
composite_dependencies: preferred-share collateral, Accountable/attestation data, primary redemption eligibility, AccessManager/Safe state, DEX liquidity
source_class: issuer_docs + onchain + market_data
freshness: current for token and API snapshot; attestation docs dated March/April 2026
confidence: medium
missing_behavior: review_required for reserve/NAV/offchain cadence; block_automation if route/action depends on stale market/governance state
```

### 7.3 Market-vs-NAV mismatch risk

- Official docs describe apxUSD as designed to trade close to $1 and supported by redemption/arbitrage mechanics for eligible whitelisted users. Source: S3.
- DEXScreener showed the largest Curve apxUSD/USDC pair at `priceUsd=0.9716` while another Uniswap v4 pool showed `0.9999` at extraction. Source: S5.
- Secondary market price can diverge from issuer NAV/redeemability because primary redemption is eligibility-gated, collateral liquidation can depend on preferred-share markets, and route depth varies by venue and size. Sources: S3/S5.
- Any Health Factor/collateral valuation logic that uses a fixed $1 or stale NAV can miss DEX discount, denied-address restrictions, pause state, primary-redemption ineligibility, or collateral liquidation delays. `missing_behavior: review_required` for scoring and `block_automation` for state-changing execution without Preview.

Field record:

```text
observed_oracle_market_divergence: DEXScreener top Curve apxUSD/USDC price below $1 at extraction; venue prices differed
missed_risk_classes: market discount, primary-redemption eligibility, deny-list/pause, collateral liquidation timing, custody/reporting, Safe/admin changes
source_class: market_data + issuer_docs + onchain
freshness: current point-in-time
confidence: medium/high for observed API divergence; medium for risk-class mapping
missing_behavior: review_required for production collateral valuation; block_automation for exits without fresh quote/governance checks
```

## 8. Governance / change-feed watchlist

Current watch items:

- AccessManager role assignments for apxUSD and MinterV0, especially roles `0`, `2`, `4`, `21`, `22`, `23`, `24`, `25`, and `31`. Source: S1.
- Pending Safe transactions for `0xabdd...5e96` and `0xf986...3CE2`; S8 was not fully decoded and must be refreshed for production. Source: S8.
- UUPS implementation upgrades and `setAuthority` / `setDenyList` / `setSupplyCap` / `setCCIPAdmin` calls. Source: S1/S6.
- MinterV0 parameters: `maxMintAmount`, `rateLimitAmount`, `rateLimitPeriod`, pending order flow, and pause state. Source: S1/S3.
- Deny-list contract address and denied-address state. Source: S1/S7.
- Primary redemption eligibility rules, allowed jurisdictions, and operational SLA. Source: S3.
- Collateral/backing dashboards, Accountable data, Wolf & Company attestations, DAT issuer concentration, and reserve coverage. Source: S2/S3.
- DEX route liquidity and price divergence across Curve/Uniswap/PancakeSwap. Source: S5.
- Audit/report scope updates and incident/postmortem publications. Source: S2.

## Highest-impact unknowns

| Unknown / caveat | Why it matters | missing_behavior | Confidence |
|---|---|---|---|
| Live executable slippage for a specific position was not quoted. | Market depth is point-in-time and size-dependent. | `block_automation` | high |
| Primary redemption eligibility and live process were not verified for a specific holder. | Whitelisted primary redemption may be the cleanest NAV path but may not be available. | `review_required`; `block_automation` for redemption action | high |
| Token-native oracle was not found; external NAV/backing cadence was not machine-reconciled. | Collateral valuation depends on external data and market/redeemability assumptions. | `review_required` | high |
| Pending Safe transactions were only bounded-sampled, not exhaustively decoded. | Admin role/function changes may be pending. | `review_required` | high |
| Deny-list account state was not enumerated. | Transfer/redeemability can be account-specific. | `review_required` | high |

## Minimal handoff

apxUSD has meaningful secondary liquidity, especially a large Curve apxUSD/USDC venue in the saved snapshot, but pricing is route- and eligibility-dependent. Primary redemption is for eligible whitelisted participants and settles in USDC; general users rely on external pools. The token itself has no price oracle in the reviewed source; valuation must combine issuer/backing/NAV evidence, primary-redemption access, and live DEX quotes. For automation, missing route quotes, eligibility, deny-list/pause state, and pending Safe/admin changes are blocking until refreshed by Preview.
