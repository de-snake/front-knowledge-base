# Centrifuge deSPXA — transfer/liquidity/oracle/governance research

Report date: 2026-06-04 UTC
Analyst: Hermes operator recovery after worker provider-preflight overflow
Task scope: methodology sections 6, 7, and 8 only — transferability/redemption/liquidity; oracle/pricing methodology; governance/change-feed watchlist.
Input asset: Base (`chain_id: 8453`), `0x9c5C365e764829876243d0b289733B9D2b729685`, symbol `deSPXA`, intended use unknown.
Output type: objective source-linked facts, not token selection, ranking, suitability verdict, or investment recommendation.

Related evidence:

- `research/base-despxa/raw/blockscout-read-contract-summary.json`
- `research/base-despxa/raw/blockscout-smart-contract-token.json`
- `research/base-despxa/raw/sources/src__core__spoke__ShareToken.sol`
- `research/base-despxa/raw/sources/src__vaults__AsyncVault.sol`
- `research/base-despxa/raw/sources/src__vaults__BaseVaults.sol`
- `research/base-despxa/raw/sources/blockscout-hook-FreelyTransferable.sol`
- `research/base-despxa/raw/dexscreener-base_despxa-2026-06-04.json`

## Source index

| ID | URL / local evidence | source_class | freshness | accessed | confidence | Notes |
|---|---|---:|---:|---:|---:|---|
| S1 | `research/base-despxa/raw/blockscout-read-contract-summary.json` | onchain | current | 2026-06-04 | high | Blockscout/RPC-derived token/vault/hook/root/manager state for exact Base token and vault. |
| S2 | `research/base-despxa/raw/sources/src__core__spoke__ShareToken.sol` | onchain | current | 2026-06-04 | high | Verified/share-token source: ERC20, hook, ERC1404 restriction checks, authTransferFrom. |
| S3 | `research/base-despxa/raw/sources/blockscout-hook-FreelyTransferable.sol` | onchain | current | 2026-06-04 | high | Verified transfer hook: ordinary transfers allowed unless frozen; deposits/redeems require member state. |
| S4 | `research/base-despxa/raw/sources/src__vaults__AsyncVault.sol` and `src__vaults__BaseVaults.sol` | onchain | current | 2026-06-04 | high | Verified AsyncVault / BaseVault source: ERC-7540 async request/claim flow and price-per-share methods. |
| S5 | `https://centrifuge.io/blog/despxa-on-base` | issuer_docs | current | 2026-06-04 | medium | Centrifuge launch post: deSPXA on Base, SPXA exposure, non-US Authorized Participants, DeFi venues, Chronicle/LayerZero/Keyrock references. |
| S6 | `research/base-despxa/raw/dexscreener-base_despxa-2026-06-04.json` | market_data | current | 2026-06-04 | medium | DEX market/liquidity snapshot saved via Dexscreener API. |
| S7 | `https://chroniclelabs.org/blog/raising-the-standard-of-real-world-assets-with-centrifuge-anemoy-and-the-rwa-oracle` | issuer_docs | current | 2026-06-04 | low | Search result/source hint for Chronicle RWA oracle integration; not fully extracted in this recovery pass. |
| S8 | `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/methodology.md` | unknown | current | 2026-06-04 | high | Report labels and missing-data behavior. |

## Agent-context summary

deSPXA is a Centrifuge V3 share token on Base with a linked AsyncVault over Base USDC. The exact token uses a `FreelyTransferable` hook: ordinary transfers are allowed unless an address is frozen, while deposit/redeem request and claim flows require membership/hook data. That distinction matters: secondary-market transfers can be broadly liquid, but primary mint/redeem at NAV is not the same path as an ordinary holder DEX trade. Onchain vault pricing uses Centrifuge manager-provided price-per-share and epoch/async request mechanics; official Centrifuge launch material says Chronicle supplies verifiable pricing data and that non-US Authorized Participants can mint/redeem at NAV.

## 6. Transferability, redemption, and liquidity

### Transferability and restrictions

- Exact token: `ShareToken` at `0x9c5C365e764829876243d0b289733B9D2b729685`, name from contract `DeFi Janus Henderson Anemoy S&P500® Fund Token`, symbol `deSPXA`, decimals `18`, totalSupply raw `4236891729691416512194`. Source: S1 high.
- Token hook: `hook() = 0x2a9B9C14851Baf7AD19f26607C9171CA1E7a1A61`, verified as `FreelyTransferable`. Source: S1/S3 high.
- `FreelyTransferable` source says it allows any non-frozen account to receive and transfer tokens; it requires accounts to be added as a member before submitting deposit or redemption requests; and it supports freezing accounts that blocks transfers both to and from them. Source: S3 high.
- `ShareToken` routes `transfer`, `transferFrom`, `mint`, and `burn` through `_onTransfer`, which calls the hook if set; it also exposes ERC-1404 `detectTransferRestriction` and `messageForTransferRestriction`. Source: S2 high.
- Membership caveat: the raw summary's sample `permission_checks` returned `false` for sample/random addresses; this aligns with hook-member gating for vault request flows, not necessarily ordinary secondary-market transfers. Source: S1/S3 high. `missing_behavior: review_required` for any holder-specific AP/redemption eligibility claim.

### Primary redemption / mint path

- Linked vault: `0x2dA40F061536c2f3a8f95f23a5f4c133d07D393a`, verified as `AsyncVault`; `asset()` is Base USDC `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`, `share()` is the deSPXA token, and `poolId=281474976710668`. Source: S1/S4 high.
- `AsyncVault` uses ERC-7540 async request mechanics. `requestDeposit` transfers assets to the manager/global escrow and emits `DepositRequest`; later `deposit` or `mint` claims executed requests. Source: S4 high.
- Redeem flow is async: `requestRedeem` sends shares into the manager flow and emits `RedeemRequest`; later `withdraw`/`redeem` claim executed redemption requests through the manager. Preview functions for ERC-7540 vaults revert, so static preview cannot be treated like standard synchronous ERC-4626. Source: S4 high.
- Official Centrifuge launch post states deSPXA can be minted/redeemed at NAV by non-US Authorized Participants, akin to ETF creation/redemption. Source: S5 medium.
- Ordinary-holder caveat: this card did not verify whether a given wallet is a member / Authorized Participant / eligible controller. Therefore primary redemption is `review_required` for any specific account and `block_automation` for automatic redemption execution without eligibility and request-state confirmation.

### Secondary market liquidity

Dexscreener snapshot saved in S6 showed these deSPXA venues:

| Chain | DEX | Pair | priceUsd | liquidity_usd | volume_24h_usd | Evidence |
|---|---|---|---:|---:|---:|---|
| Base | Uniswap | `0xD08f1fb797BfaCdeD23323178672557034c64CfA` | `752.59` | `3,692,816.33` | `1,939,581.32` | S6 medium |
| Base | Aerodrome | `0xf840346faFEdc1c0466216F3A899A599E6D03E75` | `752.73` | `40,666.24` | `83,702.25` | S6 medium |
| Base | Aerodrome | `0x7AE311B9cB94635dD4De5f42220469F6f5501d54` | `752.82` | `10,778.53` | `112,827.12` | S6 medium |
| Base | PancakeSwap | `0x46070EE625BEb75AC1CcC496553a596a9d24B4b4` | `752.86` | `1,244.68` | `495.48` | S6 medium |
| Base | Hydrex | `0xa3C25d3f65e11008465F477665CF2303A420CfB2` | `754.14` | `52.06` | `34.43` | S6 medium |

Liquidity caveat: market-data API values are point-in-time and not executable quotes. For any position-specific exit, `missing_behavior: block_automation` until Preview / live quotes confirm route depth and slippage.

## 7. Oracle and pricing methodology

### Contract/NAV pricing

- Vault `pricePerShare()` returned raw `763973338`, interpreted as `763.973338` USDC per 1 deSPXA share given USDC 6 decimals and deSPXA 18 decimals. Source: S1 high.
- Vault `priceLastUpdated()` returned `1780401600`; this is the last manager price timestamp in the raw snapshot. Source: S1 high.
- `totalAssets()` returned `3236872318793` raw USDC units, consistent with roughly `3,236,872.318793` USDC. Source: S1 high.
- `BaseVault` source says `convertToShares` and `convertToAssets` are based on the token price from the most recent epoch retrieved from Centrifuge and that actual conversion may change between order submission and execution. Source: S4 high.
- Official Centrifuge launch post says Chronicle delivers real-time, verifiable pricing data for underlying assets. Source: S5 medium; Chronicle blog search result S7 low.

### Pricing blind spots

- Contract price-per-share/NAV and DEX market price can diverge. The saved DEX snapshot showed top pool price around `$752.59` while the manager price-per-share raw value was about `$763.97`. That is an observed point-in-time difference, not a full depeg analysis. Sources: S1/S6.
- Oracle/manager price may not capture DEX liquidity stress, member/AP eligibility restrictions, freeze state, async request latency, or issuer/compliance controls. `missing_behavior: review_required` for analysis and `block_automation` for execution.
- The full Chronicle feed address, update cadence, and staleness policy were not expanded in this recovery card. `missing_behavior: review_required`.

## 8. Governance / change-feed watchlist

Watch these current surfaces from the raw onchain/source evidence:

- Token hook changes: `ShareToken.file("hook", address)` is admin-gated; hook replacement can change transfer/member/freeze behavior. Source: S2 high.
- Vault manager changes: `BaseVault.file("manager", address)` / async redeem manager changes can alter request processing. Source: S4 high.
- Root/ward changes: `wards` in raw summary show root `0x7Ed48C31f2fdC40d37407cBaBf0870B2b688368f` is a ward on token/vault and `0xF48256...61Ae` has vault ward access. Source: S1 high.
- Freeze/member state: `FreelyTransferable` can block frozen accounts and requires membership for deposit/redeem requests. Source: S3 high.
- Price updates: monitor `pricePerShare`, `priceLastUpdated`, manager price events, and Chronicle oracle/feed changes. Sources: S1/S4/S5.
- Primary issuance/redemption eligibility: non-US Authorized Participant status is the official NAV mint/redeem path; monitor Centrifuge/deRWA eligibility docs and any jurisdiction or member policy changes. Source: S5 medium.
- Secondary venue health: monitor Uniswap/Aerodrome liquidity and market price vs manager NAV. Source: S6 medium.

## Highest-impact unknowns

| Unknown / caveat | Why it matters | missing_behavior | Confidence |
|---|---|---|---|
| Holder-specific member/AP eligibility was not determined. | Primary mint/redeem at NAV may be unavailable to ordinary holders. | `review_required`; `block_automation` for redemption | high |
| Full freeze/member list is not enumerable from this card. | Transfers and requests may fail for specific addresses. | `review_required` | high |
| Chronicle feed address/staleness/update cadence not fully expanded. | Oracle/NAV freshness matters for pricing and request execution. | `review_required` | high |
| Live executable slippage for any position was not quoted. | Secondary market exit depth is size-dependent. | `block_automation` | high |
| Governance/admin holder identities and timelocks were not fully expanded in this sections 6-8 recovery. | Hook/manager/root changes can materially alter transfer/redemption behavior. | `review_required` | medium |

## Minimal handoff

deSPXA should be modeled as a freely transferable secondary-market token with compliance/member-gated primary request flows. The top observed DEX route had material Base liquidity, but primary NAV redemption requires AP/member eligibility and async request handling. Oracle/pricing is manager/Centrifuge/Chronicle-driven and may diverge from DEX price, so execution must use live quotes plus eligibility checks.
