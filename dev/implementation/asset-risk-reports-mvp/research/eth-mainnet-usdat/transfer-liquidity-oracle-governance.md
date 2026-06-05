# Saturn USDat — transfer, liquidity, oracle, governance research

Report date: 2026-06-04 UTC
Analyst: Hermes operator recovery after repeated Kanban worker crashes
Task scope: methodology sections 6, 7, and 8 only — transferability/redemption/liquidity; oracle/pricing methodology; governance/change-feed watchlist.
Input asset: Ethereum mainnet (`chain_id: 1`), `0x23238F20B894f29041f48d88Ee91131c395aAA71`, symbol `USDat`, intended use unknown.
Output type: objective source-linked facts, not token selection, ranking, suitability verdict, or investment recommendation.

Related evidence:

- `research/eth-mainnet-usdat/onchain-admin.md`
- `research/eth-mainnet-usdat/issuer-backing-security.md`
- `research/eth-mainnet-usdat/raw/usdat-onchain-admin-snapshot-2026-06-04.json`
- `research/eth-mainnet-usdat/raw/dexscreener-usdat-2026-06-04.json`

## Source index

| ID | URL / local evidence | source_class | freshness | accessed | confidence | Notes |
|---|---|---:|---:|---:|---:|---|
| S1 | `research/eth-mainnet-usdat/onchain-admin.md` and raw snapshot | onchain | current | 2026-06-04 | high | Exact token controls: whitelist enabled, pause/freeze/forced-transfer roles, proxy/admin state. |
| S2 | `research/eth-mainnet-usdat/issuer-backing-security.md` | issuer_docs / onchain | current | 2026-06-04 | medium/high | USDat mechanism/backing/security context. |
| S3 | `https://saturncredit.gitbook.io/saturn-docs/solution/usdat-overview` | issuer_docs | current | 2026-06-04 | medium | Official USDat docs: permissioned access, mint/redeem with USDC or `$M`, redemptions return USDC. |
| S4 | `https://saturncredit.gitbook.io/saturn-docs/operations-and-governance/transparency-and-audits` | issuer_docs | current | 2026-06-04 | medium | USDat capital held in smart contract; audit links. |
| S5 | `research/eth-mainnet-usdat/raw/dexscreener-usdat-2026-06-04.json` | market_data | current | 2026-06-04 | medium | DEXScreener snapshot fetched during operator recovery: USDat/USDC venues and point-in-time liquidity. |
| S6 | `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/methodology.md` | unknown | current | 2026-06-04 | high | Methodology labels and missing-data behavior. |

## Agent-context summary

USDat is transferable as an ERC-20-like token only inside a permissioned/compliance-controlled envelope. Saturn docs say only onboarded addresses can mint, redeem, or hold USDat. The live contract has whitelist enabled and explicit freeze, forced-transfer, pause, whitelist-management, and upgrade controls. Primary redemption is an issuer/interface pathway returning USDC, not a permissionless vault withdrawal available to any address. Secondary DEX liquidity exists in a USDat/USDC Curve pair, but a live position exit still requires fresh route quotes and checks for whitelist/freeze/pause state.

## 6. Transferability, redemption, and liquidity

### 6.1 Transfer restrictions and eligibility / KYC requirements

- Official docs: USDat is permissioned; only addresses that completed Saturn onboarding can mint, redeem, or hold USDat. Source: S3 medium.
- Onchain state: `isWhitelistEnabled=true` and `paused=false` at the snapshot block. Source: S1 high.
- Verified source: whitelist manager can enable/disable whitelist and add/remove accounts. Whitelist hooks enforce requirements around wrapping/unwrapping. Source: S1 high.
- Compliance roles: `0x10D59F776db12b4B271b2609CB8b7Ddd0A82703B` can pause, freeze/unfreeze, forced-transfer from frozen accounts, and manage whitelist. Source: S1 high.

Field record:

```text
transfer_restrictions: permissioned token; whitelist currently enabled; pause/freeze/forced-transfer controls present
eligibility_kyc: Saturn onboarding required for mint/redeem/hold per official docs
source_class: onchain + verified_source + issuer_docs
freshness: current for onchain; current docs as accessed
confidence: high for contract controls; medium for offchain onboarding process
missing_behavior: review_required for user-specific eligibility and redemption assumptions
```

### 6.2 Freeze, blacklist, forced-transfer, registry mechanics

- USDat source uses a whitelist, Freezable, ForcedTransferable, and Pausable components rather than a purely free ERC-20 transfer path. Source: S1 high.
- `FREEZE_MANAGER_ROLE` and `FORCED_TRANSFER_MANAGER_ROLE` are both held by EOA `0x10D59...03B`. Source: S1 high.
- Forced transfer exists for frozen accounts through the inherited `ForcedTransferable` component. Existing-holder impact is direct for affected frozen accounts. Source: S1 high.
- The exact list of frozen/whitelisted accounts was not fully enumerated in this card. `missing_behavior: review_required` for production eligibility checks.

Field record:

```text
freeze_blacklist: account freeze and whitelist gating present; current token paused=false
forced_transfer: yes, from frozen accounts through FORCED_TRANSFER_MANAGER_ROLE
registry_mechanics: internal USDat whitelist plus inherited freeze/forced-transfer controls; no complete account-state inventory in this pass
source_class: onchain + verified_source
freshness: current snapshot
confidence: high for control existence; medium for current affected-account coverage
missing_behavior: review_required before compliance-sensitive automation
```

### 6.3 Primary redemption path and settlement process

- Saturn docs say USDat can be minted by depositing USDC or `$M` through the Saturn interface and redemptions return USDC to the user's wallet. Source: S3 medium.
- Because USDat is permissioned, primary mint/redeem access depends on Saturn onboarding/whitelist state and cannot be assumed available for arbitrary holders. Source: S3 medium, S1 high.
- This pass did not run a live Saturn UI/API redemption preview, verify per-user onboarding, or inspect pending issuer-side redemption queues. `missing_behavior: block_automation` for real exit execution without Preview/eligibility checks.

Field record:

```text
primary_redemption_path: Saturn interface / issuer pathway; USDat -> USDC per official docs
cooldown_queue_settlement: no contract-level holder queue identified in this USDat-only pass; offchain/interface settlement not tested
claim_token_receipt: none identified for USDat itself
claim_readiness: depends on whitelist/onboarding, pause/freeze state, interface availability, and issuer liquidity
source_class: issuer_docs + onchain controls
freshness: current docs/onchain snapshot
confidence: medium for process description; low/unknown for user-specific SLA
missing_behavior: review_required for eligibility; block_automation for live exits without Preview
```

### 6.4 Secondary liquidity venues and size-dependent exit caveats

DEXScreener snapshot saved in S5 showed these Ethereum venues for USDat at extraction time:

| Chain | DEX | Pair | priceUsd | liquidity_usd | volume_24h_usd | Evidence |
|---|---|---|---:|---:|---:|---|
| Ethereum | Curve | `0xF4d0CF32908b2C7f1021339c43Df0F77f06896d7` USDat/USDC | `1.00010` | `16,520,157.99` | `7,372,297.26` | S5 medium |
| Ethereum | Balancer | pool id beginning `0x32d4c5Bb...` USDat/USDC | `0.8513` | `1,193.01` | `221.79` | S5 medium |

Liquidity caveats:

- API liquidity/volume are point-in-time market data and not executable quotes.
- The Balancer result is tiny relative to the Curve venue and should not dominate pricing assumptions.
- For any live exit or liquidation, use route-level Preview/quotes, not this report's static snapshot. `missing_behavior: block_automation` for state-changing exit without live route quote.

Field record:

```text
secondary_liquidity: Curve USDat/USDC primary venue in saved DEXScreener snapshot; tiny Balancer venue also listed
current_depth: about $16.52m Curve liquidity at extraction; point-in-time only
historical_depeg_discount: not established in this bounded pass
eligible_liquidator_depth: unknown for permissioned holder constraints; DEX route may not solve issuer redemption eligibility
source_class: market_data
freshness: current point-in-time
confidence: medium for current venues; low for stress/historical liquidity
missing_behavior: block_automation for real exits without fresh route quote
```

## 7. Oracle and pricing methodology

### 7.1 Primary price / oracle source

- USDat itself does not expose a dedicated holder-facing Chainlink-style price feed in the reviewed token source. Contract behavior is token/accounting/control logic. Source: S1 high.
- Official docs describe a 1:1 USD peg, collateralized by `$M`, and USDC redemption. Source: S3 medium.
- For risk reasoning, this means the practical price source is a combination of issuer peg/NAV claim, redemption access, and market price, not an intrinsic oracle in the USDat token contract. Source: S1/S3/S5.

Field record:

```text
primary_price_source: issuer 1:1 peg / redemption framing plus external market quotes; no token-native price oracle found in this pass
oracle_follows: issuer/redeemability and market price, not automatic contract NAV
source_class: issuer_docs + market_data + onchain
freshness: current
confidence: medium
missing_behavior: review_required before using as Credit Account collateral oracle methodology
```

### 7.2 Cadence, staleness, and dependencies

- No token-native staleness window was identified for USDat price; the contract does not solve reserve/NAV freshness by itself. Source: S1 high.
- Dependencies include Saturn onboarding/whitelist, USDat pause/freeze/forced-transfer state, `$M` reserve quality/liquidity, Saturn interface availability, USDC redemption capacity, and DEX liquidity. Sources: S1/S3/S5.
- The transparency page states USDat capital is verifiable onchain, but this pass did not build an automated reserve/NAV reconciler. Source: S4 medium.

Field record:

```text
update_cadence: unknown for issuer reserve/NAV proof; continuous for onchain role/state if rechecked by RPC
staleness_window: none found for token-native price; DEX and reserve data require freshness checks
composite_dependencies: whitelist/onboarding, compliance controls, $M backing, USDC redemption route, DEX liquidity
source_class: onchain + issuer_docs + market_data
freshness: current point-in-time
confidence: medium
missing_behavior: review_required for reserve/NAV freshness; block_automation if execution depends on stale route/state
```

### 7.3 Market-vs-NAV mismatch risk

- DEXScreener Curve USDat/USDC price was close to $1 at extraction (`1.00010`), but this is market data, not proof of issuer redemption availability. Source: S5 medium.
- A user can face a market/NAV mismatch if issuer redemption is permission-blocked, if whitelist/freeze/pause state changes, if `$M` liquidity is impaired, or if DEX depth is insufficient for the position size. Sources: S1/S3/S5.
- Because USDat is permissioned, eligible-liquidator depth and holder eligibility are material for automation. `missing_behavior: review_required` / `block_automation` without a live route and compliance-state check.

## 8. Governance / change-feed watchlist

Current watch items:

- ProxyAdmin owner and USDat `DEFAULT_ADMIN_ROLE` state, especially whether `0x610182...6820` remains an immediate admin/upgrade path. Source: S1.
- SaturnTimelock and AssetCapTimelock scheduled operations, min delay, proposer/canceller state, and pending role migrations. Source: S1.
- Compliance EOA `0x10D59...03B` role changes and any pause/freeze/forced-transfer/whitelist events. Source: S1.
- `isWhitelistEnabled`, per-account whitelist/freeze state for any user/account/route under analysis. Source: S1/S3.
- `$M` reserve/custody/redemption state and Saturn transparency updates. Source: S3/S4.
- DEX route liquidity and market price for USDat/USDC. Source: S5.
- Audit/report scope updates and incident/postmortem publications. Source: S4.

## Highest-impact unknowns

| Unknown / caveat | Why it matters | missing_behavior | Confidence |
|---|---|---|---|
| User-specific onboarding/whitelist and freeze state were not enumerated. | Permissioned token; ability to hold/redeem/transfer is account-specific. | `review_required`; `block_automation` for live action | high |
| Live executable quotes for a specific size were not generated. | DEX liquidity is point-in-time and size-dependent. | `block_automation` | high |
| Token-native price oracle was not found. | Collateral valuation needs external oracle/redeemability logic. | `review_required` | high |
| `$M` reserve/NAV update cadence was not independently reconciled. | Backing freshness affects peg/redeemability confidence. | `review_required` | high |
| Pending role/timelock state can change after the snapshot. | Admin speed and control assumptions may drift. | `review_required` | high |

## Minimal handoff

USDat has a visible Curve USDat/USDC market and issuer docs describe 1:1 USDC redemption, but it remains a permissioned, issuer-controlled token. Transfers/redemptions require whitelist/onboarding assumptions, and compliance/admin controls can directly freeze, forced-transfer, pause, or change whitelist state. Pricing should be treated as issuer peg plus market-route evidence, not token-native oracle truth. Any live exit, liquidation, or collateral action must refresh whitelist/freeze/pause/admin state and route quotes before execution.
