# Centrifuge deSPXA — MVP asset risk dossier

Report date: 2026-06-04 UTC
Analyst: Hermes kanban synthesis worker
Display: Centrifuge deSPXA
Chain: Base (`chain_id: 8453`)
Token address: `0x9c5C365e764829876243d0b289733B9D2b729685`
Symbol: `deSPXA`
Intended use: unknown

This dossier is an objective, source-linked asset context artifact. It does not advise token selection, position sizing, position fit, investment action, or execution.

Citation format: inline source IDs resolve in Section 13 to URL or local evidence path, source class, access date, and confidence. Material rows also state source class/access/confidence inline where the source is especially important.

## 1. Agent-context summary

deSPXA is a verified Base `ShareToken` at `0x9c5C365e764829876243d0b289733B9D2b729685`, with contract name `DeFi Janus Henderson Anemoy S&P500® Fund Token`, symbol `deSPXA`, 18 decimals, and no proxy implementation reported in the parent Blockscout snapshot [R1/O1/O6, onchain, 2026-06-04, high]. Centrifuge materials describe deSPXA as the freely transferable DeFi-distribution token/wrapper for SPXA, the Janus Henderson Anemoy S&P 500 Index Fund exposure built under license from S&P Dow Jones Indices and distributed through Centrifuge on Base [D1/D2/D3, issuer_docs, 2026-06-04, medium]. The exact token is not an ordinary unrestricted ERC-20 in all contexts: ordinary transfers use a `FreelyTransferable` hook that allows non-frozen accounts, while deposit/redeem request paths require member/Authorized Participant eligibility and an ERC-7540 async vault flow [R1/R3/O2/O3, onchain, 2026-06-04, high; D1/D5, issuer_docs/governance, 2026-06-04, medium/low]. The main missing fields for downstream reasoning are Root ward identities/thresholds, holder-specific member/AP eligibility, fund legal/custody/audit documents, full Chronicle feed details, and live executable liquidity; these are marked `review_required` or `block_automation` below instead of being treated as absence of risk.

## 2. One-paragraph mechanism

Centrifuge deSPXA is a Base share token connected to an `AsyncVault` whose immediate asset is Base USDC and whose economic exposure is described by Centrifuge as SPXA / Janus Henderson Anemoy S&P 500 Index Fund exposure; non-US Authorized Participants can mint/redeem at NAV, while ordinary DeFi holders should be modeled as secondary-market holders unless member/AP eligibility is confirmed [R2/R3/D1/D2/D3/D5, mixed issuer_docs/onchain/governance, 2026-06-04, medium-high]. The exact vault uses ERC-7540-style asynchronous deposit and redemption requests, manager-provided price-per-share accounting, and a transfer hook that separates ordinary non-frozen token transfers from member-gated primary request and claim paths [R1/R3/O2/O3/O5/O6, onchain, 2026-06-04, high].

## 3. Identity and token semantics

| Field | Value | Source |
|---|---|---|
| Canonical chain | Base | User-supplied scope corroborated by parent Base Blockscout/RPC snapshot [R1/O6, onchain, 2026-06-04, high] |
| chain_id | `8453` | User-supplied scope and parent onchain snapshot [R1/O6, onchain, 2026-06-04, high] |
| Token address | `0x9c5C365e764829876243d0b289733B9D2b729685` | User-supplied scope, Base Blockscout token/source evidence, and parent snapshot [R1/O1/O6, onchain, 2026-06-04, high] |
| Verified contract name | `ShareToken` | Base Blockscout/source evidence summarized in parent onchain artifact [R1/O1/O6, onchain, 2026-06-04, high] |
| Proxy status | Not a proxy in the parent Blockscout metadata; no implementation list was reported | Parent Blockscout summary [R1/O1/O6, onchain, 2026-06-04, high] |
| `name()` | `DeFi Janus Henderson Anemoy S&P500® Fund Token` | Parent RPC/Blockscout snapshot [R1/O6, onchain, 2026-06-04, high] |
| `symbol()` | `deSPXA` | Parent RPC/Blockscout snapshot [R1/O6, onchain, 2026-06-04, high] |
| `decimals()` | `18` | Parent RPC/Blockscout snapshot and verified source summary [R1/O1/O6, onchain, 2026-06-04, high] |
| Total supply raw in snapshot | `4236891729691416512194` | Parent RPC/Blockscout snapshot [R1/O6, onchain, 2026-06-04, high] |
| Standards / interfaces | ERC-20 with ERC-1404-style transfer restriction checks delegated to a hook | Verified `ShareToken` source summarized in parent onchain/transfer artifacts [R1/R3/O1/O3, onchain, 2026-06-04, high] |
| Transfer hook | `0x2a9B9C14851Baf7AD19f26607C9171CA1E7a1A61`, verified as `FreelyTransferable` | Parent RPC/source snapshot [R1/R3/O3/O6, onchain, 2026-06-04, high] |
| Linked Base USDC vault | `0x2dA40F061536c2f3a8f95f23a5f4c133d07D393a`, verified as `AsyncVault` | Parent RPC/source snapshot [R1/R3/O2/O6, onchain, 2026-06-04, high] |
| Vault asset | Base USDC `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` | Parent vault read/source summary [R1/R3/O2/O6, onchain, 2026-06-04, high] |
| Root/admin hub | `0x7Ed48C31f2fdC40d37407cBaBf0870B2b688368f` | Parent root/ward-state reconstruction [R1/O4/O6, onchain, 2026-06-04, high/medium] |
| Async request manager | `0xF48256AbDDf96EcDDc4B3DbD23E8C1921f9761Ae` | Parent vault/manager source summary [R1/R3/O5/O6, onchain, 2026-06-04, high] |
| Asset type | Tokenized-fund / issuer-NAV DeFi wrapper for SPXA exposure, not a stablecoin or ordinary cash-equivalent ERC-20 | Centrifuge launch/recap and S&P DJI press context [R2/D1/D2/D3, issuer_docs, 2026-06-04, medium] |
| Token behavior | Non-rebasing share token / receipt-like share with async primary request flows; ordinary ERC-20 transfers remain hook-checked | Parent source summaries [R1/R3/O1/O2/O3, onchain, 2026-06-04, high] |
| Transition-stage behavior | A holder can enter a pending deposit/redeem/request/claim state through the ERC-7540 async vault path; preview functions revert by design | Parent `AsyncVault` source summary [R3/O2/O5, onchain, 2026-06-04, high] |

Material caveat: non-proxy source verification does not make behavior immutable. `ShareToken` has admin-gated `file("hook")`, `updateVault`, `authTransferFrom`, `mint`, `burn`, and hook-data surfaces; Root and warded contracts can change key behavior [R1/O1/O4/O6, onchain, 2026-06-04, high].

## 4. Issuer / protocol and business model

| Topic | Facts | Source |
|---|---|---|
| Protocol / infrastructure | Centrifuge V3 / Centrifuge infrastructure is the onchain distribution and vault context for deSPXA | Centrifuge launch/recap plus exact-token source state [R1/R2/D1/D2/O1/O2, mixed issuer_docs/onchain, 2026-06-04, medium-high] |
| Underlying fund context | S&P DJI announced collaboration with Centrifuge, Anemoy Capital, and Janus Henderson around an onchain S&P 500 index fund; Centrifuge materials describe SPXA as Janus Henderson Anemoy S&P 500 Index Fund exposure | S&P DJI press release and Centrifuge materials [D1/D2/D3, issuer_docs, 2026-06-04, medium] |
| Mechanism | deSPXA is the DeFi-distribution/freely transferable wrapper for SPXA exposure on Base | Centrifuge launch and Q1 recap [D1/D2, issuer_docs, 2026-06-04, medium] |
| Value source | The value source is fund/NAV exposure to SPXA / S&P 500 index exposure, not protocol fee revenue or staking yield from the token contract itself | Parent issuer/backing synthesis and Centrifuge/S&P context [R2/D1/D2/D3, issuer_docs/local research, 2026-06-04, medium] |
| Offchain dependencies | Fund/legal entity, manager/sub-advisor, index license, custody/accounting, NAV reporting, AP/KYC/eligibility process, and oracle/data providers | Parent issuer/backing synthesis [R2/D1/D2/D3/D4/D6, mixed, 2026-06-04, medium] |
| Mint/redeem control | Centrifuge launch material says non-US Authorized Participants can mint/redeem at NAV; Moonwell proposal says retail holders interact through secondary markets and KYC'd participants can redeem into USDC | Centrifuge launch and Moonwell proposal [D1, issuer_docs, 2026-06-04, medium; D5, governance, 2026-06-04, low] |
| Onchain administrators | Centrifuge-style `Auth` / `wards` and Root control token/vault/hook/manager surfaces; active Root ward contracts are not identified as named governance or Safe thresholds in the parent recovery | Parent onchain/admin artifact [R1/O4/O6, onchain, 2026-06-04, medium-high] |

Business-model caveat: primary issuer/fund terms, audited fund financial statements, full service-provider list, income/distribution treatment, and ordinary-holder legal redemption rights were not retrieved from primary legal/fund documents in the parent artifacts. `missing_behavior: review_required` for issuer-controlled-asset acceptance and `cannot_rank_cleanly` for any ranking use [R2/METH, local research/methodology, 2026-06-04, high].

## 5. Backing, NAV, and exposure map

`nav_model: issuer NAV / tokenized fund wrapper / async vault`

| Field | Current facts | Source |
|---|---|---|
| Immediate vault asset | Base USDC `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` is the `AsyncVault.asset()` | Parent vault/RPC/source snapshot [R1/R3/O2/O6, onchain, 2026-06-04, high] |
| Share token | deSPXA is the `AsyncVault.share()` | Parent vault/RPC/source snapshot [R1/R3/O2/O6, onchain, 2026-06-04, high] |
| Pool ID | `poolId=281474976710668` in the parent snapshot | Parent transfer/oracle artifact [R3/O2/O6, onchain, 2026-06-04, high] |
| Contract price-per-share | `pricePerShare = 763973338`, interpreted by parent research as about `763.973338` USDC per share using USDC 6 decimals | Parent issuer/transfer artifacts [R2/R3/O2/O6, onchain, 2026-06-04, high] |
| Price timestamp | `priceLastUpdated = 1780401600` (`2026-06-02T12:00:00Z` conversion) | Parent RPC snapshot plus local timestamp conversion [R2/R3/O6, onchain, 2026-06-04, high] |
| Total assets | `totalAssets = 3236872318793` raw USDC units in the parent snapshot | Parent issuer/transfer artifacts [R2/R3/O2/O6, onchain, 2026-06-04, high] |
| Economic exposure | Centrifuge describes deSPXA/SPXA as S&P 500 index fund exposure managed/sub-advised by Janus Henderson / Anemoy under S&P DJI license | Centrifuge and S&P materials [R2/D1/D2/D3, issuer_docs, 2026-06-04, medium] |
| Third-party RWA data | RWA.xyz showed SPXA total asset value, NAV, management fee, investor eligibility, primary-market fields, base assets USDC, daily subscription/redemption, and minimum investment `500,000 USDC` in the parent recovery; this is secondary data, not primary legal proof | RWA.xyz page summarized in parent issuer artifact [R2/D4, market_data/risk_assessment, 2026-06-04, low] |
| Primary redemption path | Non-US AP / member-gated NAV mint/redeem through Centrifuge async vault mechanics; holder-specific eligibility was not established | Centrifuge launch plus exact `AsyncVault`/hook source [R2/R3/D1/O2/O3, mixed, 2026-06-04, medium-high] |
| NAV vs secondary-market price | Parent DEX snapshot showed top-pool market prices around `$752.59-$754.14`, while manager price-per-share was about `$763.97`; point-in-time NAV/manager price and DEX exit price can diverge | Parent market snapshot and vault read [R2/R3/M1/O2/O6, mixed onchain/market_data, 2026-06-04, medium-high] |
| Principal exposure categories | Fund/NAV reporting, AP/member eligibility, async request processing, manager/Chronicle price updates, freeze/member state, Root/ward admin changes, and secondary-market liquidity/slippage | Synthesized from parent artifacts [R1/R2/R3, local research, 2026-06-04, medium-high] |

Missing-data behavior for backing/NAV: fund holdings/replication/cash buffers, custody/service providers, audited financial statements, legal offering terms, primary redemption documentation, and independent reserve/NAV reports were not fully obtained from primary issuer/fund documents in the parent artifacts. For explanation-only use, record unknown and continue; for ranking, collateral admission, or automated execution, use `review_required`; for a concrete exit, use `block_automation` until holder eligibility, request state, and live quote/Preview are available [R2/R3/METH, mixed, 2026-06-04, high].

## 6. Contract admin, multisigs, and sensitive actions

### 6.1 Admin architecture

| Contract | Address | Pattern / current admin state | Key admin surfaces | Source |
|---|---|---|---|---|
| ShareToken / deSPXA | `0x9c5C365e764829876243d0b289733B9D2b729685` | Non-proxy verified contract; Root observed as ward among checked relevant addresses | `file(hook)`, `file(name/symbol)`, `updateVault`, `authTransferFrom`, `mint`, `burn`, `setHookData` | Parent onchain artifact [R1/O1/O6, onchain, 2026-06-04, high] |
| AsyncVault | `0x2dA40F061536c2f3a8f95f23a5f4c133d07D393a` | Non-proxy verified contract; Root and manager observed as wards among checked relevant addresses | `file(manager)`, `file(asyncRedeemManager)`, endorsed operator, request/claim processing | Parent onchain/transfer artifacts [R1/R3/O2/O6, onchain, 2026-06-04, high] |
| FreelyTransferable hook | `0x2a9B9C14851Baf7AD19f26607C9171CA1E7a1A61` | Non-proxy verified hook; Root ward-state check shows Root control | Non-frozen transfers allowed; member-gated deposit/redeem request and claim paths; freeze/member behavior from hook stack | Parent onchain/transfer artifacts [R1/R3/O3/O6, onchain, 2026-06-04, high/medium] |
| Root | `0x7Ed48C31f2fdC40d37407cBaBf0870B2b688368f` | Non-proxy verified contract; active wards derived from event scan are four unverified contracts | `pause`/`unpause`, delay, endorse/veto, schedule/execute Root wards, `relyContract`/`denyContract` on child contracts | Parent onchain/admin artifact [R1/O4/O6, onchain, 2026-06-04, medium-high] |
| AsyncRequestManager | `0xF48256AbDDf96EcDDc4B3DbD23E8C1921f9761Ae` | Non-proxy verified contract; Root observed as ward | `file(spoke)`, `file(balanceSheet)`, callbacks/trusted calls, claim paths gated by `auth` | Parent onchain artifact [R1/O5/O6, onchain, 2026-06-04, high] |

Root state from parent recovery: `delay() = 172800` seconds / 2 days and `paused() = false`; Root source says `pause()`/`unpause()` are immediate for an authorized ward, while adding new Root wards uses the delay path [R1/O4/O6, onchain, 2026-06-04, medium-high].

Current active Root ward holders derived from the parent Blockscout event scan are four unverified contracts: `0xCEb7eD5d5B3bAD3088f6A1697738B60d829635c6`, `0x1E70530e9555711f8DF4838Ab940b97c039B4037`, `0xf837a22883e004f705E0D7e1deE08e295Df30B27`, and `0x97cc7e9Dafdd725Cc23B25eeBC93c4384B4Fe30A` [R1/O4/O6, onchain, 2026-06-04, medium]. Their named identities, owner sets, Safe thresholds, and offchain control policies were not resolved; `missing_behavior: review_required` before assuming governance safety or execution speed beyond Root's explicit new-ward delay [R1/METH, local research/methodology, 2026-06-04, high].

### 6.2 Sensitive action classification

| Sensitive action | Existing-holder impact | Execution speed in parent snapshot | Source / missing behavior |
|---|---|---|---|
| Replace transfer hook through `ShareToken.file("hook", address)` | `direct_freeze` / `unknown`, because hook controls transfer/member/freeze rules | Immediate for current authorized child ward path; new Root ward addition has 2-day Root delay | Source summaries [R1/R3/O1/O3/O4, onchain, 2026-06-04, high]. Full replacement policy: `review_required`. |
| `authTransferFrom` forced transfer | `direct_transfer` | Immediate for authorized token ward | Verified `ShareToken` source summary [R1/O1, onchain, 2026-06-04, high]. |
| Admin `mint` / `burn` | `direct_dilution` / `direct_transfer` depending use | Immediate for authorized token ward | Verified `ShareToken` source summary [R1/O1, onchain, 2026-06-04, high]. Business flow usually goes through vault/manager, but admin surface exists. |
| `updateVault(asset, vault)` | `indirect` / possible `direct_redemption_block` | Immediate for authorized token ward | Verified `ShareToken` source summary [R1/O1, onchain, 2026-06-04, high]. |
| Set hook data or freeze/member state | `direct_freeze`, `direct_redemption_block`, or `indirect` | Immediate for hook/token ward path | Hook and token source summaries [R1/R3/O1/O3, onchain, 2026-06-04, high/medium]. Full member/frozen set not enumerated: `review_required`. |
| Change vault manager / async redeem manager | `direct_redemption_block` / `unknown` | Immediate for vault ward | `AsyncVault`/manager source summaries [R1/R3/O2/O5, onchain, 2026-06-04, high]. |
| Root `pause()` / `unpause()` | `direct_redemption_block` / `unknown`, depending downstream path | Immediate for active Root ward | Root source/state summary [R1/O4, onchain, 2026-06-04, high/medium]. Downstream exact effects not fully traced: `review_required`. |
| Root `relyContract` / `denyContract` on child contracts | `unknown`; can add/remove child admin rights | Immediate for active Root ward | Root source summary [R1/O4, onchain, 2026-06-04, high]. |
| Root `scheduleRely` / `executeScheduledRely` for new Root wards | `unknown` | 2-day timelock for new Root ward | Root state/source [R1/O4/O6, onchain, 2026-06-04, high/medium]. |
| Root `file("delay")` | `indirect` | Immediate for active Root ward | Root source summary [R1/O4, onchain, 2026-06-04, high]. |
| Endorse/veto trusted operators | `indirect` / possible request-path effects | Immediate for active Root ward | Root/vault source summaries [R1/R3/O2/O4, onchain, 2026-06-04, medium-high]. |
| Proxy upgrade implementation | None found for exact token/vault/hook/root/manager in parent Blockscout metadata | n/a | Parent onchain artifact [R1/O1/O2/O3/O4/O5, onchain, 2026-06-04, high]. Non-proxy does not remove Root/ward mutability. |
| Safe multisig / timelock owner | Unknown | Unknown | Parent probes did not resolve Safe threshold/owner data for active Root wards [R1/O6, onchain, 2026-06-04, medium]. `missing_behavior: review_required`. |

## 7. Audits, formal verification, and incidents

| Item | Facts found | Source / confidence |
|---|---|---|
| Verified source | Exact token, vault, hook, Root, and manager sources were recovered/verified through parent Blockscout/source evidence | Parent onchain/transfer artifacts [R1/R3/O1/O2/O3/O4/O5/O6, onchain, 2026-06-04, high] |
| Audit reports for exact deployment | No public final audit report URL was matched in the parent recovery to the exact deSPXA token, `AsyncVault`, `FreelyTransferable` hook, Root/manager configuration, and current Base deployment | Parent issuer/backing/security artifact [R2, local research, 2026-06-04, high]. `missing_behavior: review_required`. |
| Centrifuge V3 audit status signal | Centrifuge Q1 recap says V3.1 was deployed across ten chains and V3.2 was in audit | Centrifuge Q1 recap [D2, issuer_docs, 2026-06-04, medium]. This is not exact deployed-scope audit coverage. |
| Formal verification | No formal-verification report or invariant set for this exact deployed configuration was located in parent artifacts | Parent issuer/security artifact [R2, local research, 2026-06-04, medium]. `missing_behavior: review_required`. |
| Bug bounty | A bug-bounty program/scope for this exact token/deployment was not located in parent artifacts | Parent issuer/security artifact [R2, local research, 2026-06-04, medium]. `missing_behavior: review_required` for security acceptance; `continue` for descriptive context. |
| Incidents | No confirmed exploit, NAV break, freeze incident, redemption delay, oracle failure, or emergency governance postmortem for exact deSPXA was identified in the bounded parent sources | Parent issuer/security artifact [R2, local research, 2026-06-04, medium]. Absence of found incident is not proof none occurred; `missing_behavior: continue` for explanation and `review_required` for production acceptance. |
| Material admin events | Parent Root event scan observed historical `Rely`, `Deny`, `RelyContract`, and `DenyContract` events, including recent Root ward schedule/rely/deny activity around 2026-06-01 to 2026-06-04 | Parent onchain/admin artifact [R1/O4/O6, onchain, 2026-06-04, medium]. |

## 8. Transferability, redemption, and liquidity

| Field | Current facts | Source |
|---|---|---|
| Ordinary transferability | The exact token uses a `FreelyTransferable` hook; parent source review says any non-frozen account can receive and transfer tokens | Hook/source summary [R3/O3, onchain, 2026-06-04, high] |
| Freeze / blacklist / registry mechanics | Hook source supports freezing accounts, which blocks transfers to and from the frozen account; member state is required for deposit/redeem request and claim flows | Hook/source summary [R1/R3/O3, onchain, 2026-06-04, high] |
| ERC-1404 checks | `ShareToken` delegates `detectTransferRestriction` and `messageForTransferRestriction` to the hook | Token source summary [R1/R3/O1/O3, onchain, 2026-06-04, high] |
| Holder-specific restriction state | Parent sample/random permission checks returned `false` for sample addresses; this supports member-gating for request flows but does not enumerate a given holder's state | Parent transfer artifact [R3/O6, onchain, 2026-06-04, high/medium]. `missing_behavior: review_required` for any holder-specific claim. |
| Primary deposit path | `requestDeposit` transfers assets to manager/global escrow and emits `DepositRequest`; later `deposit` or `mint` claims executed requests | `AsyncVault` source summary [R3/O2/O5, onchain, 2026-06-04, high] |
| Primary redeem path | `requestRedeem` sends shares into manager flow and emits `RedeemRequest`; later `withdraw`/`redeem` claims executed redemption requests through the manager | `AsyncVault` source summary [R3/O2/O5, onchain, 2026-06-04, high] |
| Preview semantics | ERC-7540 preview functions revert by design; standard synchronous ERC-4626 preview assumptions do not apply | `AsyncVault`/`BaseVault` source summary [R3/O2, onchain, 2026-06-04, high] |
| Primary NAV redemption eligibility | Official Centrifuge launch says deSPXA can be minted/redeemed at NAV by non-US Authorized Participants; Moonwell proposal says retail holders interact through secondary markets | Centrifuge launch and Moonwell proposal [D1, issuer_docs, 2026-06-04, medium; D5, governance, 2026-06-04, low] |
| Claim readiness semantics | Claim readiness depends on async request execution, member/AP eligibility, manager state, and price/accounting updates; a specific account's readiness was not enumerated | Parent transfer/oracle artifact [R3/O2/O5/O6, onchain, 2026-06-04, medium-high]. `missing_behavior: review_required`; `block_automation` for automatic redemption execution. |

Saved Dexscreener market-data snapshot from parent research:

| Chain | DEX | Pair | priceUsd | liquidity_usd | volume_24h_usd | Source |
|---|---|---|---:|---:|---:|---|
| Base | Uniswap | `0xD08f1fb797BfaCdeD23323178672557034c64CfA` | `752.59` | `3,692,816.33` | `1,939,581.32` | [R3/M1, market_data, 2026-06-04, medium] |
| Base | Aerodrome | `0xf840346faFEdc1c0466216F3A899A599E6D03E75` | `752.73` | `40,666.24` | `83,702.25` | [R3/M1, market_data, 2026-06-04, medium] |
| Base | Aerodrome | `0x7AE311B9cB94635dD4De5f42220469F6f5501d54` | `752.82` | `10,778.53` | `112,827.12` | [R3/M1, market_data, 2026-06-04, medium] |
| Base | PancakeSwap | `0x46070EE625BEb75AC1CcC496553a596a9d24B4b4` | `752.86` | `1,244.68` | `495.48` | [R3/M1, market_data, 2026-06-04, medium] |
| Base | Hydrex | `0xa3C25d3f65e11008465F477665CF2303A420CfB2` | `754.14` | `52.06` | `34.43` | [R3/M1, market_data, 2026-06-04, medium] |

Liquidity caveat: saved API liquidity is point-in-time market data and not an executable route quote. For any position-specific exit, `missing_behavior: block_automation` until Preview/live quotes confirm route depth, slippage, recipient eligibility, and current freeze/member/request state [R3/M1/METH, market_data/methodology, 2026-06-04, high].

## 9. Oracle and pricing methodology

| Field | Current facts | Source |
|---|---|---|
| Primary vault/NAV source | Vault conversions use manager-provided price-per-share from the most recent Centrifuge epoch; actual conversion can change between order submission and execution | `BaseVault`/`AsyncVault` source summary [R3/O2/O5, onchain, 2026-06-04, high] |
| Current price snapshot | `pricePerShare = 763973338`; `priceLastUpdated = 1780401600` | Parent RPC/vault snapshot [R2/R3/O2/O6, onchain, 2026-06-04, high] |
| Price update provider | Centrifuge launch material says Chronicle delivers real-time, verifiable pricing data for underlying assets | Centrifuge launch and Chronicle source hint [D1, issuer_docs, 2026-06-04, medium; D6, issuer_docs, 2026-06-04, low] |
| Update cadence / staleness | Exact Chronicle feed address, update cadence, staleness window, and reporter/manager policy were not expanded in parent artifacts | Parent transfer/oracle artifact [R3, local research, 2026-06-04, high]. `missing_behavior: review_required`. |
| Market/NAV divergence | Saved DEX prices around `$752.59-$754.14` differed from vault price-per-share around `$763.97`; this is point-in-time evidence of possible divergence, not a historical depeg analysis | Parent vault read and Dexscreener snapshot [R2/R3/O2/O6/M1, mixed onchain/market_data, 2026-06-04, medium-high] |
| Oracle blind spots | Manager/NAV price can miss DEX liquidity stress, member/AP eligibility restrictions, freeze state, async request latency, issuer/compliance controls, redemption delay, or fund/NAV impairment | Synthesized from parent artifacts and methodology [R1/R2/R3/METH, mixed, 2026-06-04, high] |
| Gearbox-specific oracle notes | Parent artifacts did not identify an active Gearbox main/reserve oracle configuration for exact deSPXA | Parent artifacts [R1/R2/R3, local research, 2026-06-04, medium]. `missing_behavior: review_required` if used as Credit Account collateral. |

## 10. Governance / change-feed watchlist

Track these fields before reusing the dossier for live reasoning:

| Watch item | Why it matters | Source / missing behavior |
|---|---|---|
| Root active ward identities, verification status, owner sets, thresholds, and timelocks | Active Root wards can operate Root and child ward surfaces; named governance/Safe assumptions are unresolved | Parent Root event/ward recovery [R1/O4/O6, onchain, 2026-06-04, medium]. `review_required`. |
| Root `delay`, `paused`, `scheduleRely`, `relyContract`, and `denyContract` activity | Admin execution speed and child-contract control can change | Root source/event summary [R1/O4/O6, onchain, 2026-06-04, medium-high]. |
| Transfer hook address and hook source | Hook replacement or hook-state changes can affect transferability, membership, freeze state, and redemption requests | Token/hook source summaries [R1/R3/O1/O3, onchain, 2026-06-04, high]. |
| Vault manager / async redeem manager / request manager | Manager changes can alter request processing, claim availability, and conversion paths | Vault/manager source summaries [R1/R3/O2/O5, onchain, 2026-06-04, high]. |
| Member/AP/KYC eligibility policy and per-holder member/frozen state | Primary NAV mint/redeem may be unavailable for ordinary holders, and frozen/member state can block transfers or requests | Hook/source and issuer docs [R3/D1/D5/O3, mixed, 2026-06-04, medium-high]. `review_required`; `block_automation` for redemption. |
| Chronicle feed address, update cadence, staleness, and price reporter/manager policy | Price freshness affects NAV/share accounting and async conversions | Parent oracle artifact [R3/D1/D6, mixed, 2026-06-04, medium]. `review_required`. |
| Manager price-per-share and `priceLastUpdated` | Stale or changed NAV data can diverge from market exit value | Parent vault snapshot [R2/R3/O2/O6, onchain, 2026-06-04, high]. |
| DEX liquidity and price vs manager NAV | Secondary exit depth is size- and route-dependent; liquidity can move from the saved snapshot | Dexscreener snapshot [R3/M1, market_data, 2026-06-04, medium]. `block_automation` until live quote/Preview. |
| Fund/NAV reports, legal terms, custody/service providers, and audited financial statements | Backing quality and redemption rights are offchain/legal-dependent | Parent issuer/security artifact [R2/D1/D2/D3/D4, mixed, 2026-06-04, low-medium]. `review_required`. |
| Audit report publication and deployed-scope matching | Source verification is not audit coverage, and V3.2 audit status did not establish exact deSPXA coverage | Parent issuer/security artifact and Centrifuge recap [R2/D2, local research/issuer_docs, 2026-06-04, medium]. `review_required`. |
| Incident/postmortem discovery | No incident was found in bounded parent sources, but this does not prove none occurred | Parent issuer/security artifact [R2, local research, 2026-06-04, medium]. `continue` for explanation, `review_required` for acceptance. |

## 11. Data quality and missing-data behavior

| Material field | Current data quality | missing_behavior |
|---|---|---|
| Token identity, chain, address, symbol, name, decimals | High-confidence parent RPC/Blockscout snapshot and verified source summary [R1/O1/O6, onchain, 2026-06-04, high] | `continue` |
| Proxy / implementation status for token/vault/hook/root/manager | High-confidence parent Blockscout metadata says non-proxy for inspected exact contracts [R1/O1/O2/O3/O4/O5, onchain, 2026-06-04, high] | `continue`; do not infer immutability because Root/wards can mutate configuration |
| Root direct state (`delay`, `paused`) | Parent source/RPC/event reconstruction found `delay=172800`, `paused=false` [R1/O4/O6, onchain, 2026-06-04, medium-high] | `continue`; refresh before live decisions |
| Root ward identities / Safe threshold / named governance | Active Root ward contracts were derived but unverified and not mapped to Safe thresholds or named governance [R1/O6, onchain, 2026-06-04, medium] | `review_required` |
| Full inherited hook source and member/frozen address set | Hook behavior summarized, but full inherited source/member/frozen set was not fully enumerated [R1/R3/O3/O6, onchain, 2026-06-04, medium-high] | `review_required` |
| Holder-specific member/AP/KYC eligibility | Official primary mint/redeem path is AP/member-gated; no specific holder eligibility was verified [R2/R3/D1/D5, mixed, 2026-06-04, medium] | `review_required`; `block_automation` for redemption execution |
| Fund legal documents / offering terms / service providers | Not fully retrieved from primary legal/fund documents in parent artifacts [R2/D1/D2/D3, issuer_docs/local research, 2026-06-04, medium] | `review_required` |
| Fund holdings, custody, cash buffers, audited financial statements, NAV reports | Secondary data exists, but primary fund evidence was not fully obtained [R2/D4, market_data/risk_assessment, 2026-06-04, low] | `review_required`; `cannot_rank_cleanly` for ranking |
| Audit and formal-verification scope | No exact deployed-scope report or invariant extraction was found [R2, local research, 2026-06-04, medium] | `review_required` |
| Incident history | No confirmed exact-token incident found in bounded parent sources; absence of evidence is not comprehensive assurance [R2, local research, 2026-06-04, medium] | `continue` for explanation; `review_required` for production acceptance |
| Oracle/feed details | Manager price-per-share was read; Chronicle exact feed address/cadence/staleness were not fully expanded [R3/D1/D6, mixed, 2026-06-04, medium] | `review_required`; `block_automation` for execution relying on stale/fresh price assumptions |
| NAV vs DEX price divergence | Point-in-time vault and market snapshot exists; no historical stress/depeg analysis | Parent vault and Dexscreener snapshots [R2/R3/O6/M1, mixed, 2026-06-04, medium-high] | `review_required` for analysis; `block_automation` for execution without live quote |
| Live executable liquidity / slippage | Dexscreener snapshot is not executable route data | Parent Dexscreener snapshot [R3/M1, market_data, 2026-06-04, medium] | `block_automation` until live route quote / Preview |
| Gearbox-specific oracle or supported-market state | Not identified in parent artifacts | Parent artifacts [R1/R2/R3, local research, 2026-06-04, medium] | `review_required` if the asset is used as Credit Account collateral |
| Ranking / position-fit decision | Out of scope for this dossier by methodology and task | Methodology [METH, unknown, 2026-06-04, high] | `cannot_rank_cleanly` without mandate, position context, live state, and missing-field resolution |

## 12. Highest-impact unknowns

1. Active Root ward contracts are unverified and not mapped to named governance, owners, Safe thresholds, or operating policy; `missing_behavior: review_required` because these contracts appear to control Root and therefore child admin surfaces [R1/O4/O6, onchain, 2026-06-04, medium-high].
2. Holder-specific member/AP/KYC eligibility and current frozen/member state were not established; `missing_behavior: review_required` for reasoning about a specific account and `block_automation` for primary redemption or automated request execution [R3/D1/D5/O3, mixed, 2026-06-04, medium-high].
3. Primary legal/fund terms, custody/service providers, holdings/replication method, cash buffers, audited financial statements, and NAV reports were not fully retrieved from primary fund documents; `missing_behavior: review_required` and `cannot_rank_cleanly` for ranking/backing acceptance [R2/D1/D2/D3/D4, mixed, 2026-06-04, low-medium].
4. Audit/formal-verification coverage for the exact deployed deSPXA token, `AsyncVault`, `FreelyTransferable` hook, Root, manager, and Base configuration was not matched to a public report; `missing_behavior: review_required` before treating source verification as audit coverage [R2/R1/R3, local research, 2026-06-04, medium-high].
5. Chronicle feed address, update cadence, staleness policy, reporter authority, and failure handling were not fully expanded; `missing_behavior: review_required` for pricing analysis and `block_automation` for execution that relies on oracle freshness [R3/D1/D6, mixed, 2026-06-04, medium].
6. Live executable exit depth and size-dependent slippage were not measured; the saved Dexscreener snapshot is not an executable quote. `missing_behavior: block_automation` until live route quote / Preview confirms route depth and recipient/account eligibility [R3/M1/METH, market_data/methodology, 2026-06-04, high].
7. No confirmed exact-token incident was found in bounded parent sources, but this is not comprehensive incident assurance; `missing_behavior: continue` for explanatory use and `review_required` before production acceptance workflows [R2, local research, 2026-06-04, medium].

## 13. Sources

| ID | URL / local evidence | source_class | Accessed | Confidence | Notes |
|---|---|---|---|---|---|
| METH | `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/methodology.md` | unknown | 2026-06-04 | high | Project-specific asset mining pipeline, section requirements, source-priority rules, and missing-data behavior. |
| R1 | `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/base-despxa/onchain-admin.md` | onchain | 2026-06-04 | high | Parent onchain/admin research for identity, verified source, Root/ward state, and sensitive actions. |
| R2 | `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/base-despxa/issuer-backing-security.md` | mixed issuer_docs/onchain/risk_assessment | 2026-06-04 | medium-high | Parent issuer/backing/security research for mechanism, NAV/backing, audits, formal verification, and incidents. |
| R3 | `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/base-despxa/transfer-liquidity-oracle-governance.md` | mixed onchain/issuer_docs/market_data | 2026-06-04 | medium-high | Parent transfer/liquidity/oracle/governance research for hooks, async redemption, Dexscreener snapshot, oracle blind spots, and watchlist. |
| O1 | `https://base.blockscout.com/address/0x9c5C365e764829876243d0b289733B9D2b729685` and local `research/base-despxa/raw/sources/src__core__spoke__ShareToken.sol` | onchain | 2026-06-04 | high | deSPXA `ShareToken` address/source and token semantics. |
| O2 | `https://base.blockscout.com/address/0x2dA40F061536c2f3a8f95f23a5f4c133d07D393a` and local `research/base-despxa/raw/sources/src__vaults__AsyncVault.sol` / `src__vaults__BaseVaults.sol` | onchain | 2026-06-04 | high | Linked Base USDC `AsyncVault`, ERC-7540 async request/claim flow, price-per-share methods. |
| O3 | `https://base.blockscout.com/address/0x2a9B9C14851Baf7AD19f26607C9171CA1E7a1A61` and local `research/base-despxa/raw/sources/blockscout-hook-FreelyTransferable.sol` | onchain | 2026-06-04 | high | Transfer hook, non-frozen transfer behavior, member-gated deposit/redeem paths, freeze behavior. |
| O4 | `https://base.blockscout.com/address/0x7Ed48C31f2fdC40d37407cBaBf0870B2b688368f` and local `research/base-despxa/raw/sources/blockscout-root-Root.sol` | onchain | 2026-06-04 | medium-high | Root source/state, delay, pause, Root ward and child ward operations. |
| O5 | `https://base.blockscout.com/address/0xF48256AbDDf96EcDDc4B3DbD23E8C1921f9761Ae` and local `research/base-despxa/raw/sources/blockscout-manager-AsyncRequestManager.sol` | onchain | 2026-06-04 | high | Async request manager source and request/claim/callback admin surfaces. |
| O6 | `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/base-despxa/raw/blockscout-read-contract-summary.json`, `raw/blockscout-smart-contract-token.json`, `raw/root-logs-blockscout-2026-06-04.json`, and `raw/root-ward-state-2026-06-04.txt` | onchain | 2026-06-04 | high/medium | Local raw Blockscout/RPC snapshot, token/vault/hook/root/manager reads, metadata, and Root event-derived ward state. |
| D1 | `https://centrifuge.io/blog/despxa-on-base` | issuer_docs | 2026-06-04 | medium | Centrifuge launch post for deSPXA on Base, SPXA exposure, non-US Authorized Participants, DeFi venues, Chronicle/LayerZero/Keyrock context. |
| D2 | `https://centrifuge.io/blog/centrifuge-q1-2026-recap` | issuer_docs | 2026-06-04 | medium | Centrifuge recap: deSPXA as freely transferable wrapper of SPXA, V3.1 deployment, V3.2 audit status, Chronicle oracle partner note. |
| D3 | `https://press.spglobal.com/2025-07-01-S-P-Dow-Jones-Indices-Collaborates-with-Centrifuge-to-Bring-the-S-P-500-Index-Onchain,-Expanding-Access-to-the-Worlds-Most-Widely-Recognized-Benchmark` | issuer_docs | 2026-06-04 | medium | S&P DJI collaboration with Centrifuge, Anemoy Capital, and Janus Henderson around onchain S&P 500 index fund access. |
| D4 | `https://app.rwa.xyz/assets/SPXA` | market_data / risk_assessment | 2026-06-04 | low | Secondary SPXA asset page summarized in parent artifact; useful as third-party market/risk data, not primary legal proof. |
| D5 | `https://forum.moonwell.fi/t/proposal-to-add-despxa-market-to-moonwell-on-base/2163` | governance | 2026-06-04 | low | Moonwell proposal by Centrifuge team; secondary/low-confidence support for retail/AP path and deSPXA/SPXA structure. |
| D6 | `https://chroniclelabs.org/blog/raising-the-standard-of-real-world-assets-with-centrifuge-anemoy-and-the-rwa-oracle` | issuer_docs | 2026-06-04 | low | Chronicle RWA oracle integration source hint; parent artifact did not fully extract exact feed address/cadence. |
| M1 | `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/base-despxa/raw/dexscreener-base_despxa-2026-06-04.json` and `https://dexscreener.com/base/0xD08f1fb797BfaCdeD23323178672557034c64CfA` | market_data | 2026-06-04 | medium | Saved Dexscreener API snapshot for Base deSPXA venues, point-in-time prices, liquidity, and 24h volume. |
