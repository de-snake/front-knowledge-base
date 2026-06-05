# Saturn sUSDat — transfer/liquidity/oracle/governance research

Report date: 2026-06-04 UTC
Analyst: Hermes operator recovery after worker timeout/provider-preflight failures
Task scope: methodology sections 6, 7, and 8 only — transferability/redemption/liquidity; oracle/pricing methodology; governance/change-feed watchlist.
Input asset: Ethereum mainnet (`chain_id: 1`), `0xd166337499e176bbc38a1fbd113ab144e5bd2df7`, symbol `sUSDat`, intended use unknown.
Output type: objective source-linked facts, not token selection, ranking, suitability verdict, or investment recommendation.

Related evidence:

- `research/eth-mainnet-susdat/onchain-admin.md`
- `research/eth-mainnet-susdat/issuer-backing-security.md`
- `research/eth-mainnet-susdat/raw/onchain-admin-snapshot-2026-06-04.json`
- `research/eth-mainnet-susdat/raw/dexscreener-saturn_susdat-2026-06-04.json`

## Source index

| ID | URL / local evidence | source_class | freshness | accessed | confidence | Notes |
|---|---|---:|---:|---:|---:|---|
| S1 | `research/eth-mainnet-susdat/onchain-admin.md` and raw snapshot | onchain | current | 2026-06-04 | high | Exact token/queue/USDat/STRC-oracle roles, pending timelock operations, blacklists, event history. |
| S2 | `https://saturncredit.gitbook.io/saturn-docs/solution/susdat-overview/staking-and-unstaking-process` | issuer_docs | current | 2026-06-04 | medium | Staking/unstaking, NFT receipt, processor, oracle validation, secondary market statement. |
| S3 | `https://saturncredit.gitbook.io/saturn-docs/solution/susdat-overview` | issuer_docs | current | 2026-06-04 | medium | ERC-4626 tokenized vault, underlying USDat, deposit fee, target yield, reward vesting. |
| S4 | `research/eth-mainnet-susdat/raw/dexscreener-saturn_susdat-2026-06-04.json` | market_data | current | 2026-06-04 | medium | DEX liquidity/volume snapshot saved via Dexscreener API. |
| S5 | `https://app.saturn.credit/insights` | issuer_docs | current | 2026-06-04 | medium | App data for APY/TVL/reserve split; used only as context. |
| S6 | `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/methodology.md` | unknown | current | 2026-06-04 | high | Report labels and missing-data behavior. |

## Agent-context summary

sUSDat is transferable as an ERC-20 share token but is not a simple liquid stablecoin wrapper. Standard ERC-4626 withdraw/redeem are disabled; holder exits use `requestRedeem`, a withdrawal-queue NFT, processor execution, STRC sale/conversion, and claim. Transfers, deposits, request creation, queue claims, and underlying USDat flows are sensitive to blacklist/freeze/pause/whitelist controls documented in the companion onchain/admin artifact. Pricing is a hybrid of ERC-4626 share accounting and STRC oracle valuation; DEX market price can diverge from NAV/queue exit value.

## 6. Transferability, redemption, and liquidity

### Transferability and restrictions

- sUSDat has standard ERC-20 transfer functions, but verified source / onchain-admin summary shows blacklist checks on transfer, transferFrom, deposits, and withdrawal request creation. Source: S1 high.
- The withdrawal queue checks both sUSDat blacklist and USDat frozen status for relevant claim/seizure flows. Source: S1 high.
- Current state from the onchain/admin artifact: `paused=false`; sUSDat blacklist events were observed for two addresses; no sUSDat pause/unpause events were found in the scanned range. Source: S1 high.
- USDat underlying currently has whitelist/freeze/forced-transfer roles that can affect entry/exit flows around sUSDat. Source: S1 high.

### Primary redemption path

- Saturn docs state unstaking uses a three-stage process: request, processing, claim. The user requests redemption by specifying shares and a minimum USDat amount; sUSDat is transferred to the withdrawal queue and an NFT receipt is minted. Source: S2 medium.
- During processing, Saturn's processor locks a batch, sells corresponding STRC on secondary markets to obtain USDat, and submits results onchain. Each user's USDat owed is pro-rata by shares in the batch; execution price is validated against the onchain oracle, and if USDat owed is below the user's minimum the transaction reverts. Source: S2 medium; current processor role from S1 high.
- Claim: once processed, the user redeems the NFT to claim USDat and the NFT is burned. Source: S2 medium.
- Contract caveat: the companion onchain/admin artifact states standard ERC-4626 `withdraw` and `redeem` revert with `OperationNotAllowed`, so the queue is the primary contract exit path. Source: S1 high.

### Secondary market liquidity

Dexscreener snapshot saved in S4 showed these sUSDat venues at extraction time:

| Chain | DEX | Pair | priceUsd | liquidity_usd | volume_24h_usd | Evidence |
|---|---|---|---:|---:|---:|---|
| Ethereum | Curve | `0x6206cA315c2fCDd2A857b47EFB285AA12c529a7a` | `0.9260` | `2,755,680.11` | `3,025,785.78` | S4 medium |
| Ethereum | Uniswap | `0x37083adb580cbe6355fe1a875e497c52dc48e8250dcc5c943b473fbcfa8a0a11` | `0.9434` | `286,998.44` | `45,476.34` | S4 medium |
| Ethereum | Curve | `0xcAF1969E9ba98C05113b75d8633A17196e2D02a5` | `1.0010` | `179,672.26` | `260,970.15` | S4 medium |
| Ethereum | Balancer | composite pool id beginning `0xC32474B0...` | `0.7962` | `803.83` | `210.61` | S4 medium |

Liquidity caveat: these API values are point-in-time market data, not executable quote guarantees. For any automated exit, `missing_behavior: block_automation` until a route quote / Preview resolves size-dependent slippage and eligible-path constraints.

## 7. Oracle and pricing methodology

### Contract/NAV pricing

- Verified onchain/admin summary states `totalAssets()` is internally tracked as USDat balance plus vested STRC value; `_strcTotalAssets()` prices vested STRC using `STRC_ORACLE.getPrice()`. Source: S1 high.
- Current STRC oracle address: `0x5f7EcD0D045C393DA6CB6C933C671AC305a871BF`; wrapped Chainlink-compatible oracle: `0xf4d2076277FFf631eFC4385AB36b1f7734218d23`; snapshot `getPrice()` returned `94.72e8`, with max staleness 26 hours and min/max price bounds `20e8` / `150e8`. Source: S1 high.
- Request/processing path validates STRC execution price against the oracle and user minimum amount. Source: S2 medium, S1 high.

### Oracle blind spots

- The oracle/NAV path can fail to capture immediate DEX discount/premium, queue congestion, processor availability, compliance freeze/blacklist, USDat whitelist/freeze, offchain STRC settlement delay, and secondary-market liquidity stress. `missing_behavior: review_required` for risk scoring and `block_automation` for execution without live quote/Preview.
- A stale or misconfigured STRC oracle can block or distort queue processing and share accounting; default admin currently can update oracle address/staleness/bounds immediately until pending timelock revocations execute. Source: S1 high.

## 8. Governance / change-feed watchlist

Current watch items from S1:

- Pending timelock operations scheduled to revoke `DEFAULT_ADMIN_ROLE` from EOA `0x610182...` on sUSDat, USDat, STRC oracle, and withdrawal queue; ready timestamps around 2026-06-08 UTC. Recheck after ready time before classifying admin speed.
- sUSDat/queue implementation upgrades occurred before the current implementation; future upgrades remain a critical watch item.
- sUSDat blacklist events were observed for two addresses; monitor `Blacklisted` / `UnBlacklisted` and queue seizure events.
- USDat freeze/forced-transfer/whitelist/pause roles can affect sUSDat exits; monitor USDat role changes and freeze/whitelist state.
- STRC oracle configuration changes: wrapped oracle, max staleness, price bounds.
- Withdrawal queue events: pending count, lock/unlock/process/claim/seizure events, pause/unpause.
- Fees/parameters: deposit fee, fee recipient, vesting period, tolerance, max rewards bps.
- Offchain reserve/NAV: Saturn Accountable/Chainlink reserve/NAV rollout, STRC allocation, LTV allocation threshold changes, app reserve ratio and collateral split.

## Highest-impact unknowns

| Unknown / caveat | Why it matters | missing_behavior | Confidence |
|---|---|---|---|
| Queue state and claim readiness were not exhaustively enumerated. | Actual redemption timing depends on queue batches and processor state. | `review_required` | medium |
| Live executable slippage for a specific position was not quoted. | DEX liquidity is point-in-time and size-dependent. | `block_automation` | high |
| Oracle methodology depends on STRC price source and bounds; full wrapped oracle details were not expanded. | Health factor/NAV can miss market or offchain settlement stress. | `review_required` | high |
| Admin role migration was pending, not complete, as of snapshot. | Execution speed may change from immediate to timelocked after revocation. | `review_required` | high |
| USDat underlying whitelist/freeze policy and exact affected accounts not fully mapped. | Underlying controls affect sUSDat exits. | `review_required` | high |

## Minimal handoff

sUSDat has an exit path, but it is queue/processor/oracle/compliance dependent. Secondary DEX liquidity exists, with the largest saved venue being Curve at about `$2.76M` liquidity and `$3.03M` 24h volume at extraction, but execution must use live quotes. Pricing should be modeled as NAV/share accounting with STRC oracle dependency plus separate market-price slippage and compliance/queue risks.
