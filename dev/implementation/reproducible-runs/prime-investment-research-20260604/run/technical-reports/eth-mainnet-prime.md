# Hastra PRIME — MVP asset risk dossier

Report date: 2026-06-04 UTC
Analyst: Hermes kanban synthesis worker
Methodology: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/methodology.md`

## Report inputs

```text
chain_id: 1
token_address: 0x19ebb35279A16207Ec4ba82799CC64715065F7F6
symbol: PRIME
display: Hastra PRIME
issuer/protocol hint: Hastra
intended_use: unknown
position_context: not supplied
```

This dossier is objective source-linked context for later agent reasoning against a user mandate, position size, horizon, Gearbox state, and Preview results. It does not rank the asset or decide final use.

Source shorthand: every bracketed source ID resolves to a URL/local evidence path, `source_class`, access date, and confidence in [13. Sources](#13-sources).

Parent artifacts synthesized:

- `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/hastra-prime/onchain-admin.md`
- `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/eth-mainnet-prime/issuer-backing-security.md`
- `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/eth-mainnet-prime/transfer-liquidity-oracle-governance.md`

## 1. Agent-context summary

- PRIME is the Ethereum mainnet token at `0x19ebb35279A16207Ec4ba82799CC64715065F7F6`, with on-chain `name() = Hastra PRIME`, `symbol() = PRIME`, and `decimals() = 6`. It is an EIP-1967 proxy whose implementation was `0x90fd843c68db38e2de0618AcBB39341CbA5A5abD` at the research snapshot. [S1], [S2], [S3]
- The verified implementation is an upgradeable ERC-4626-style staking vault over Hastra wYLDS (`asset()` / `yieldVault()` = `0x6aD038cA6C04e885630851278ca0a856Ad9a66Cc`), but conversions use an external NAV/redemption-rate feed instead of only the raw ERC-4626 total-assets/total-supply ratio. [S1], [S3], [S8]
- Hastra terms describe the product chain as USDC to wYLDS to PRIME: wYLDS is described as backed 1:1 by YLDS, and PRIME accrues wYLDS linked to Figure Democratized Prime HELOC lending operations. That makes the economic exposure materially dependent on off-chain issuer, collateral, NAV, and HELOC-operation assumptions. [S4], [S5], [S6]
- Contract conversion pricing uses FeedVerifier `0xdF4ab20fA7752Be52E41e42F1FD667f37964d6a3` and NAV feed ID `0x0007c8ed155d952e003b1e15ce7666fea785cfbe216577d578fce3920e997271`. FeedVerifier had `defaultMaxStaleness = 3600` seconds on-chain; if the feed is absent, stale, invalid, or paused long enough to go stale, PRIME deposit/redeem/mint/withdraw conversions can revert. [S1], [S8]
- Admin control is mutable: Safe `0x8D358B8aE881F8ea92C3d07783aBCA21727C6309` is current DEFAULT_ADMIN and UPGRADER for PRIME and FeedVerifier, with Safe threshold 4-of-7 and no modules observed. Operational EOA `0xA8C3CF6183D49d5D372f8FC149BD2cb5CFC0faCd` holds PRIME pauser/freezer/rewards roles. No on-chain timelock was found. [S1], [S12]
- PRIME transfers are not gated by a transfer whitelist in the reviewed source, but the `_update` path reverts when sender or receiver is frozen. PRIME deposit/mint/redeem/withdraw are blocked when the vault is paused. [S3]
- PRIME redemption returns wYLDS, not USDC. Ultimate wYLDS-to-USDC settlement depends on YieldVault `requestRedeem` / admin `completeRedeem`, redeemVault USDC availability, user not being frozen, and legal/product eligibility. No transferable PRIME claim token, NFT, or receipt was found. [S3], [S4], [S9]
- Secondary Ethereum liquidity identified in the research is Uniswap V3 PRIME/USDC 0.01% pool `0x5B70A1582135BD04e39CA94A6a56Fc3A828e3115`. At the research snapshot it held about `5.511m` PRIME and `3.268m` USDC; quote samples stayed near spot through 3m PRIME but selling 5m PRIME cliffed near visible USDC depth. [S1], [S10], [S11]
- Material unknowns remain: current public smart-contract audit scope, current reserve/custody/attestation reporting, exact off-chain NAV construction, user-specific eligibility/KYC/redemption SLA, and Safe owner operational identity. Missing behavior is mostly `review_required`; real execution that depends on exit settlement or route depth is `block_automation` until refreshed by Preview/quote. [S4], [S6], [S12]

## 2. One-paragraph mechanism

Hastra PRIME is an upgradeable Ethereum vault-share token whose underlying asset is Hastra wYLDS. Hastra terms describe the product flow as USDC to wYLDS to PRIME: wYLDS is described as backed 1:1 by YLDS, and PRIME accrues wYLDS linked to Figure Democratized Prime HELOC lending operations. On-chain, PRIME deposit/redeem/mint/withdraw conversions use a Chainlink Data Streams-style FeedVerifier NAV/redemption-rate value rather than DEX market price or a pure internal vault ratio, and those actions require the vault to be unpaused, the account not to be frozen, and the NAV feed to be valid/non-stale. Redeeming PRIME returns wYLDS; final USDC settlement is a separate YieldVault redemption process with issuer/admin completion and legal/product eligibility dependencies. [S1], [S3], [S4], [S8], [S9]

## 3. Identity and token semantics

| Field | Finding | Source / quality |
|---|---|---|
| Chain | Ethereum mainnet, `chain_id: 1`. | Input scope; [S1] onchain high. |
| Token address | `0x19ebb35279A16207Ec4ba82799CC64715065F7F6`. | Input scope; verified on [S1], [S2]. |
| Name / symbol / decimals | `Hastra PRIME` / `PRIME` / `6`. | Direct contract calls in [S1], high. |
| Current implementation | `0x90fd843c68db38e2de0618AcBB39341CbA5A5abD`. | EIP-1967 implementation slot and verified implementation metadata/source, [S1], [S3], high. |
| Proxy status | OpenZeppelin ERC1967 proxy; EIP-1967 admin and beacon slots were zero in the snapshot. | [S1], [S2], high. |
| Upgrade pattern | UUPS-style implementation; `_authorizeUpgrade` gated by `UPGRADER_ROLE`. | [S1], [S3], high. |
| Token standard / behavior | ERC-4626-style non-rebasing vault share over wYLDS, with NAV-feed conversions. | [S1], [S3], [S8], high for contract behavior. |
| Underlying asset | Hastra wYLDS / YieldVault at `0x6aD038cA6C04e885630851278ca0a856Ad9a66Cc`, 6 decimals. | `asset()` and `yieldVault()` in [S1], high; YieldVault source [S9]. |
| Asset type for agent reasoning | Issuer-controlled / RWA-linked staking-vault share, not an ordinary immutable ERC-20. | On-chain vault/share mechanics [S1], [S3]; terms/site mechanism [S4], [S5]. |
| Transition-stage behavior | PRIME itself is not a claim token/NFT/receipt; however redemption can move the holder into wYLDS and then a YieldVault pending-redemption state. | PRIME source [S3], YieldVault source [S9]; missing_behavior: `review_required` for execution paths. |

Current on-chain token state at the parent on-chain snapshot:

| Field | Snapshot value | Source / quality |
|---|---:|---|
| `totalSupply()` | `129,096,016.382551 PRIME` | [S1], high. |
| `totalAssets()` | `134,374,638.283899 wYLDS` | [S1], high. |
| `getVerifiedNav()` | `1.040904685772521320 wYLDS / PRIME` | [S1], high. |
| `getTotalValueAtNav()` | `139,871,190.638698` 6-decimal units | [S1], high. |
| `paused()` | `false` | [S1], high. |
| `navOracle()` | `0xdF4ab20fA7752Be52E41e42F1FD667f37964d6a3` | [S1], high. |
| `navFeedId()` | `0x0007c8ed155d952e003b1e15ce7666fea785cfbe216577d578fce3920e997271` | [S1], high. |

Missing-data behavior for identity: if the proxy implementation, underlying asset, or NAV feed changes, this dossier should be treated as stale and refreshed before use (`missing_behavior: review_required`; `block_automation` for any state-changing action package depending on the old implementation/feed). [S1], [S3], [S8]

## 4. Issuer / protocol and business model

### Issuer / governing entity

Hastra terms state that the Site and Protocol are provided by Signum Ltd., a British Virgin Islands company, and that Signum Ltd. is a wholly owned subsidiary of Provenance Cayman Foundation. [S4]

### Mechanism and value-accrual model

- Hastra terms describe users locking USDC to receive Solana-based wYLDS representing a claim against fully collateralized assets held by Hastra, and describe users staking wYLDS to receive PRIME. [S4]
- The same terms describe wYLDS as backed 1:1 by YLDS, a yield-bearing stablecoin issued by Figure and registered with the SEC; Hastra states it holds YLDS as collateral for wYLDS but does not issue YLDS and does not make representations about YLDS or associated parties. [S4]
- PRIME is described in Hastra terms as a liquid staking token representing participation in Figure Democratized Prime HELOC lending pools, with PRIME accruing wYLDS based on the performance of Figure's Democratized Prime HELOC lending operations. [S4]
- The exact Ethereum PRIME contract implements the PRIME-to-wYLDS vault-share layer; the broader USDC/wYLDS/YLDS/Figure HELOC layer is off-chain/legal/product context relative to the PRIME token contract. [S1], [S3], [S4]

### Access, eligibility, and off-chain dependencies

- Hastra terms restrict access by U.S. residents, citizens, persons located in the U.S., and sanctioned/illegal jurisdictions, and reserve discretion to request information, verify eligibility, block site/protocol access, or block property interests when required by law. [S4]
- PRIME depends on Hastra/Signum operations, wYLDS/YLDS collateral arrangements, Figure Democratized Prime HELOC operations, FeedVerifier/Chainlink Data Streams reporting, Ethereum admin roles, and secondary market liquidity if the holder exits via DEX rather than primary redemption. [S1], [S4], [S8], [S10], [S12]
- Direct contract redemption of PRIME to wYLDS is available through ERC-4626 `redeem`/`withdraw` only when not paused/frozen and when NAV conversion succeeds; product/legal eligibility and ultimate wYLDS-to-USDC settlement are separate dependencies. [S3], [S4], [S9]

Missing-data behavior: user-specific eligibility/KYC status, issuer operational procedures, and settlement SLAs are not established by these sources. Use `review_required` before treating a user as eligible for mint/redeem/settle flows, and `block_automation` for any real exit execution without current Preview/route/redemption checks. [S4], [S9]

## 5. Backing, NAV, and exposure map

```text
nav_model: staking-share / issuer NAV / RWA-linked HELOC exposure
```

### Backing and NAV facts located

- PRIME's direct on-chain asset is wYLDS, and PRIME conversions use a verified NAV/redemption-rate value from FeedVerifier. [S1], [S3], [S8]
- Hastra terms describe wYLDS as 1:1 backed by YLDS and state that wYLDS/PRIME economic return depends on Figure-related yield-bearing stablecoin and HELOC lending operations. [S4]
- Hastra's proof-of-reserves page displayed wYLDS backing `101.08%`, wYLDS supply `400,776,067.41`, PRIME supply `379,393,659.83`, vaulted wYLDS supply `394,912,638.27`, and PRIME price `$1.0409` when extracted by the parent research. This is issuer web data, not an independently verified audit report body. [S6]
- FeedVerifier snapshot data showed recent active-feed price/timestamp and `defaultMaxStaleness = 3600` seconds on-chain. [S1], [S8]

### Exposure map

| Layer | What PRIME holder is exposed to | Source / quality | Missing behavior |
|---|---|---|---|
| PRIME contract | Upgradeable ERC-4626-like vault share, pause/freeze/NAV-feed conversion behavior. | [S1], [S3], high. | `review_required` if implementation/feed/roles change. |
| wYLDS / YieldVault | PRIME redemption returns wYLDS; wYLDS-to-USDC settlement uses YieldVault request/complete redemption mechanics. | [S1], [S9], high for source mechanics. | `review_required`; `block_automation` for real settlement without Preview. |
| YLDS / Hastra collateral | Terms state wYLDS is backed 1:1 by YLDS held by Hastra; proof page shows issuer metrics. | [S4], [S6], medium. | `cannot_rank_cleanly` and `review_required` until reserve/custody attestations are reconciled. |
| Figure Democratized Prime HELOC operations | Terms state PRIME accrues wYLDS based on Figure Democratized Prime HELOC lending operations. | [S4], medium. | `review_required` for exposure quality/performance assumptions. |
| NAV feed | Contract conversions use FeedVerifier NAV/redemption-rate feed; stale/invalid feed can block conversions. | [S1], [S8], high on-chain; medium for off-chain construction. | `review_required`; `block_automation` if feed freshness is unknown before execution. |
| DEX market | Ethereum PRIME/USDC market price can diverge from NAV and has size-dependent depth. | [S10], [S11], medium/high point-in-time. | `block_automation` for exits without fresh route quote. |

### NAV-versus-market caveat

At the research point, on-chain NAV was about `1.0409`, while DEX/CoinGecko market values were about `$1.040`; observed divergence was small in that sample. This does not remove exit-friction risk: an NAV feed can miss liquidity cliffs, legal eligibility blocks, freeze/pause state, redemption delays, redeemVault USDC shortfalls, underlying YLDS/collateral impairment, or market depeg. [S1], [S3], [S4], [S8], [S10], [S11]

## 6. Contract admin, multisigs, and sensitive actions

### Admin structure

| Contract / surface | Current role / setting | Holder(s) | Holder type | Existing-holder impact | Execution speed | Source / quality |
|---|---|---|---|---|---|---|
| PRIME proxy | UUPS upgrade via `UPGRADER_ROLE` | `0x8D358B8aE881F8ea92C3d07783aBCA21727C6309` | Safe 4-of-7 | unknown/direct via implementation change | immediate after Safe threshold; no on-chain timelock found | [S1], [S3], [S12], high |
| PRIME | `DEFAULT_ADMIN_ROLE` | `0x8D358B8aE881F8ea92C3d07783aBCA21727C6309` | Safe 4-of-7 | indirect/direct via role grants/config | immediate after Safe threshold | [S1], [S12], high |
| PRIME | `PAUSER_ROLE` | `0xA8C3CF6183D49d5D372f8FC149BD2cb5CFC0faCd` | EOA | direct_redemption_block | immediate | [S1], [S3], high |
| PRIME | `FREEZE_ADMIN_ROLE` | `0xA8C3CF6183D49d5D372f8FC149BD2cb5CFC0faCd` | EOA | direct_freeze / direct_redemption_block | immediate | [S1], [S3], high |
| PRIME | `REWARDS_ADMIN_ROLE` | `0xA8C3CF6183D49d5D372f8FC149BD2cb5CFC0faCd` | EOA | indirect via reward distribution accounting/caps | immediate | [S1], [S3], high |
| PRIME | `NAV_ORACLE_UPDATER_ROLE` | none at snapshot among event-identified addresses | none | indirect/direct_redemption_block if re-granted and used | unknown / role must be granted | [S1], [S3], high for absence among reconstructed holders |
| FeedVerifier | `DEFAULT_ADMIN_ROLE` / `UPGRADER_ROLE` | `0x8D358B8aE881F8ea92C3d07783aBCA21727C6309` | Safe 4-of-7 | oracle behavior/upgrade impact | immediate after Safe threshold | [S1], [S8], [S12], high |
| FeedVerifier | `PAUSER_ROLE` | `0xA8C3CF6183D49d5D372f8FC149BD2cb5CFC0faCd` | EOA | indirect; can stop updates and cause stale oracle path | immediate | [S1], [S8], high |
| FeedVerifier | `UPDATER_ROLE` | `0xF0a5baEBF749562fAe5f3d9d2928357ae6cd73cd` | EOA | indirect via NAV update path, bounded by verifier logic | immediate | [S1], [S8], high |
| YieldVault / wYLDS path | Default/upgrader Safe plus EOA operational freeze/rewards/pauser/whitelist/withdrawal roles | Safe `0x8D358...6309`; EOA `0xA8C3...faCd` | Safe 4-of-7 and EOA | redemption/settlement/freeze impact | immediate after role holder action | [S1], [S9], [S12], high for source mechanics/current roles in parent research |

Safe details: Safe `0x8D358B8aE881F8ea92C3d07783aBCA21727C6309` returned version `1.4.1`, threshold `4`, seven owners, and no modules in the probed module list. Parent research also reported no guard. [S1], [S12]

### Sensitive action notes

- `upgradeToAndCall` can change PRIME or FeedVerifier behavior through a new implementation; no on-chain timelock was found for the Safe-controlled upgrade path. `missing_behavior: review_required` before relying on delayed execution or immutability. [S1], [S3], [S8], [S12]
- `pause()` on PRIME blocks deposit, depositWithPermit, mint, redeem, withdraw, and distributeRewards; parent research observed two PRIME pause windows and current `paused=false` at snapshot. [S1], [S3]
- `freezeAccount(address)` on PRIME blocks transfers involving the frozen account and blocks mint/burn paths because `_update` checks sender/receiver. Parent on-chain scan found no PRIME `AccountFrozen` / `AccountThawed` events from first code block through snapshot. [S1], [S3]
- FeedVerifier admin can set allowed feed ID, staleness, per-feed staleness, or upgrade implementation; incorrect/stale settings can block PRIME conversions through `getVerifiedNav()`. [S1], [S8]
- No separate PRIME admin minter/burner, token rescue role, fee setter, registry setter, or forced-transfer function was identified in the verified PRIME `StakingVault` source. Absence is source-review based, so forced-transfer/compliance conclusions remain `review_required` before automation. [S3]

### Recent admin/governance events captured by parent research

- PRIME deployment/initialization occurred at block `24901862` on 2026-04-17; Safe `0x8D358...6309` received DEFAULT_ADMIN and UPGRADER on 2026-04-29; deployer admin/upgrader roles were revoked on 2026-05-05. [S1]
- PRIME NAV feed rotated to the active feed ID `0x0007c8ed155d952e003b1e15ce7666fea785cfbe216577d578fce3920e997271` on 2026-04-23. [S1]
- PRIME pause windows observed: 2026-05-04 21:51:11Z to 23:55:11Z and 2026-06-02 14:53:47Z to 15:29:47Z; current snapshot state was unpaused. [S1]
- Parent Safe research found one unexecuted Safe transaction submitted 2026-06-03 that would change YieldVault role distribution by granting Safe REWARDS_ADMIN/WHITELIST_ADMIN and revoking YieldVault WHITELIST_ADMIN from EOA `0xA8C3...faCd`; it had 1/4 confirmations when checked. [S12]

## 7. Audits, formal verification, and incidents

### Audit / verification status found

- Sourcify full-match metadata/source was located for PRIME proxy/implementation and FeedVerifier proxy/implementation, supporting source-code identity checks. This is source verification, not a third-party audit verdict. [S2], [S3], [S8]
- Hastra's proof-of-reserves page displayed labels `Audit - Nov 25, 2025` and `Audit - Apr 12, 2026`, but the parent extraction did not expose underlying audit report URLs, scopes, or findings. [S6]
- The official public GitHub repository contained stale/conflicting text such as “Not yet deployed - Pending audit and security review” / “Testnet deployment. Not audited,” while parent on-chain/Sourcify evidence confirms deployed mainnet contracts. Treat the repository status text as stale for current deployment status. [S7], [S1], [S2], [S3]
- No final public smart-contract audit report URL for the exact deployed Ethereum PRIME / FeedVerifier implementations was located in the bounded parent research. `missing_behavior: review_required`. [S6], [S7]
- No formal verification report or list of formally verified invariants was located in the bounded parent research. `missing_behavior: review_required` for security posture claims. [S7]

### Incidents / operational events found

- Parent on-chain research observed two PRIME pause windows and current `paused=false`; this is an operational event history item, not by itself evidence of exploit or loss. [S1]
- Parent on-chain scan found no PRIME `AccountFrozen` / `AccountThawed` events through the snapshot. [S1]
- Parent transfer/governance research found two YieldVault accounts currently frozen from observed events/direct checks: `0xe08d97e151473a848c3d9ca3f323cb720472d015` and `0xa0f1c3ad83e07d97b5e7030e177718be175275ea`. This affects the wYLDS/redemption path rather than proving a PRIME-account freeze. [S1], [S9]
- FeedVerifier had no pause/unpause events observed and was `paused=false` at the snapshot. [S1], [S8]
- No confirmed exploit, reserve shortfall, depeg, oracle failure, or redemption-delay postmortem for exact Ethereum PRIME was found in the bounded sources. This absence is not proof that no such event occurred. `missing_behavior: continue` for explanatory context, `review_required` before relying on clean incident history. [S4], [S6], [S7]

## 8. Transferability, redemption, and liquidity

### Transferability and restrictions

| Field | Finding | Source / quality | missing_behavior |
|---|---|---|---|
| Transfer restrictions | PRIME `_update` reverts if sender or receiver is frozen; no PRIME transfer whitelist was found in the reviewed source. | [S3], high for source behavior. | `continue` for explanation; `review_required` for compliance conclusions. |
| Pause effect | PRIME deposit/mint/redeem/withdraw are `whenNotPaused`; ordinary ERC-20 transfer path is not pause-gated in the reviewed source except through freeze checks. | [S3], high. | `review_required` if implementation changes. |
| Eligibility/KYC | Terms exclude U.S. persons/locations and sanctioned/illegal jurisdictions and allow Hastra to verify/block access/interests as required by law. | [S4], high for text, medium for operational process. | `review_required` for user-specific eligibility; `block_automation` for a real primary redemption without eligibility confirmation. |
| Freeze / blacklist | PRIME has account-level freeze/thaw through `FREEZE_ADMIN_ROLE`; YieldVault has similar freeze/thaw effects on the wYLDS path. | [S3], [S9], high for source behavior. | `review_required` for exact user/account status unless checked live. |
| Forced transfer | No PRIME forced-transfer function was found in reviewed `StakingVault` source. | [S3], medium/high. | `review_required` before compliance-action assumptions. |

### Primary redemption path

1. PRIME holder calls PRIME `redeem(shares, receiver, owner)` or `withdraw(assets, receiver, owner)` when the PRIME vault is not paused and the account is not frozen. [S3]
2. PRIME computes conversion with `getVerifiedNav()` from FeedVerifier; stale/invalid/zero/non-positive NAV can revert conversion. [S3], [S8]
3. PRIME redemption returns wYLDS (`0x6aD038cA6C04e885630851278ca0a856Ad9a66Cc`), not USDC. [S1], [S3]
4. wYLDS-to-USDC settlement uses YieldVault mechanics: direct ERC-4626 `withdraw`/`redeem` are disabled, users call `requestRedeem(shares)`, and a `REWARDS_ADMIN_ROLE` account calls `completeRedeem(address user)` to pay USDC from `redeemVault` if sufficient USDC exists and the user is not frozen. [S9]
5. YieldVault `redeemVault()` returned `0xA8C3CF6183D49d5D372f8FC149BD2cb5CFC0faCd` in parent on-chain checks. [S1]

No transferable claim token, NFT, or receipt was found for PRIME redemption. YieldVault uses internal `pendingRedemptions(address)` and events, not a transferable claim object, in the reviewed source. [S9]

Missing behavior: use `review_required` for any primary redemption or settlement assumption; use `block_automation` when a real exit must be executed without a live route quote, redemption preview, account freeze check, FeedVerifier freshness check, and eligibility/settlement confirmation. [S3], [S4], [S8], [S9]

### Secondary Ethereum liquidity

- DEXScreener returned one Ethereum pair for the scoped token: Uniswap V3 PRIME/USDC pool `0x5B70A1582135BD04e39CA94A6a56Fc3A828e3115`, fee tier `100` / 0.01%. [S10]
- Parent on-chain pool checks reported `token0=PRIME`, `token1=USDC`, `fee=100`, pool liquidity `5351230848763709`, pool balances about `5,511,009.164971` PRIME and `3,268,302.323397` USDC. [S1]
- DEXScreener reported about `$9,001,343.47` liquidity and `$11,701,620.17` 24h volume at extraction time. [S10]
- CoinGecko global data reported PRIME price about `$1.04`, 24h volume about `$21.3m`, and multiple exchanges/markets; because those global figures include non-Ethereum/Solana venues, they should not be treated as Ethereum-mainnet exit depth for this token address. [S11]

Parent Uniswap V3 quoter samples:

| Sell size | Quoted USDC out | Effective USDC/PRIME | Caveat | Source |
|---:|---:|---:|---|---|
| 1,000 PRIME | 1,040.18 | 1.040182 | near spot in point-in-time quote | [S1] |
| 10,000 PRIME | 10,401.80 | 1.040180 | near spot in point-in-time quote | [S1] |
| 100,000 PRIME | 104,016.25 | 1.040163 | near spot in point-in-time quote | [S1] |
| 1,000,000 PRIME | 1,039,984.13 | 1.039984 | modest impact in quoted pool | [S1] |
| 3,000,000 PRIME | 3,118,763.86 | 1.039588 | large fraction of visible pool inventory | [S1] |
| 5,000,000 PRIME | 3,268,261.82 | 0.653652 | quote nearly drains visible USDC inventory; cliff risk | [S1] |

Liquidity missing behavior: `block_automation` for any state-changing exit without fresh on-chain route quotes and current pool/liquidity checks; `review_required` for eligible-liquidator depth because legal/product restrictions may matter even when DEX transfer is technically possible. [S1], [S4], [S10]

## 9. Oracle and pricing methodology

### Primary pricing source

- PRIME `_convertToShares` and `_convertToAssets` call `getVerifiedNav()`; no fallback to a raw vault ratio was found when NAV is unavailable. [S3]
- `getVerifiedNav()` reads `IFeedVerifier(navOracle).priceOf(navFeedId)` and rejects non-positive prices. [S3], [S8]
- Current PRIME `navOracle` is `0xdF4ab20fA7752Be52E41e42F1FD667f37964d6a3`, and current `navFeedId` is `0x0007c8ed155d952e003b1e15ce7666fea785cfbe216577d578fce3920e997271`. [S1]
- FeedVerifier source/docs describe a Chainlink Data Streams Schema v7 redemption-rate verifier that stores latest price per feed ID, enforces allowed feed ID, and reverts if the feed has no report, a zero/non-positive price, or stale price. [S8]

```text
primary_price_source: Chainlink Data Streams-style FeedVerifier redemption-rate/NAV feed
oracle_follows: NAV / exchange / redemption rate for PRIME-to-wYLDS conversion
source_class: onchain + issuer source/docs
freshness: current for on-chain snapshot
confidence: high for contract use; medium for off-chain NAV construction details
missing_behavior: review_required before using as Credit Account collateral oracle methodology
```

### Cadence, staleness, and dependencies

- FeedVerifier active feed price at the research check was around `1.040904685772521320` to `1.040906939176726297`, depending on the parent snapshot block/time. [S1]
- FeedVerifier active feed timestamp was near report time, and on-chain `defaultMaxStaleness()` returned `3600` seconds. [S1], [S8]
- FeedVerifier depends on Chainlink VerifierProxy `0x5A1634A86e9b7BfEf33F0f3f3EA3b1aBBc4CC85F`, valid Chainlink Data Streams reports, the FeedVerifier updater EOA, FeedVerifier admin settings, and the active feed ID. [S1], [S8]
- FeedVerifier docs had a staleness-default mismatch in parent research; on-chain/source state should override stale prose for current behavior. [S1], [S8]

### Oracle miss classes

The NAV/redemption-rate feed can be current while practical exit value is impaired by DEX liquidity cliffs, issuer/product eligibility blocks, freeze/pause state, YieldVault redeemVault USDC shortfall, redemption delay, underlying YLDS/collateral impairment, or market depeg. Use `review_required` for production collateral valuation assumptions and `block_automation` for liquidation/exit execution without fresh oracle, account-state, liquidity, and settlement checks. [S1], [S3], [S4], [S8], [S9], [S10]

## 10. Governance / change-feed watchlist

Compare future runs against these fields before treating the dossier as current:

1. PRIME proxy implementation slot: snapshot value `0x90fd843c68db38e2de0618AcBB39341CbA5A5abD`; any change is material. [S1], [S3]
2. YieldVault implementation slot: parent transfer research snapshot value `0xDA962f7a0308e9D4F2F60c5Aab94f173C26d1A1D`; any change is material for wYLDS redemption. [S1], [S9]
3. FeedVerifier implementation slot: snapshot value `0xbC6023cb49F8E8cA6cef563d5FD97ba4C6A5D937`; any change is material for oracle behavior. [S1], [S8]
4. PRIME `navOracle`, PRIME `navFeedId`, FeedVerifier `allowedFeedId`, `defaultMaxStaleness`, per-feed staleness override, active price, and active timestamp. [S1], [S8]
5. Safe `0x8D358B8aE881F8ea92C3d07783aBCA21727C6309` threshold, owners, modules, guard, and pending multisig transactions. [S12]
6. Pending Safe transaction `0x95b5137c13d8a10592d00bae1404dcf05cf25597dc2c88d040ef728524b0895f`, which parent research said would change YieldVault role distribution if executed. [S12]
7. EOA `0xA8C3...faCd` roles on PRIME, YieldVault, and FeedVerifier because it currently has immediate freeze/pause/rewards/withdrawal/whitelist powers across the redemption path. [S1], [S9]
8. FeedVerifier updater EOA `0xF0a5...3cd`; loss, compromise, or revocation affects NAV update freshness. [S1], [S8]
9. PRIME/YieldVault pause/unpause and AccountFrozen/AccountThawed events; parent research observed repeated pauses/unpauses and two YieldVault frozen accounts. [S1], [S9]
10. Hastra Terms changes, especially eligibility, redemption, collateral/backing, fee, or property-blocking language. [S4]
11. Uniswap pool `0x5B70...3115` liquidity, balances, tick/range state, fee tier, and route quotes for any size-sensitive exit. [S1], [S10]
12. Public reserve/NAV reports, YLDS backing/custody attestations, audit reports, bug bounty disclosures, and incident statements if published after this dossier. [S6], [S7]

Change-feed missing behavior: `review_required` for admin/governance/oracle drift; `block_automation` if implementation, role, feed, pending Safe tx, or liquidity state changes after an action package was prepared. [S1], [S8], [S10], [S12]

## 11. Data quality and missing-data behavior

| Material field | Current value / finding | source_class | freshness | confidence | missing_behavior |
|---|---|---|---|---|---|
| Token identity | Hastra PRIME / PRIME / 6 decimals / exact Ethereum address. | onchain | current at 2026-06-04 snapshot | high | continue |
| Proxy / implementation | ERC1967 proxy; implementation `0x90fd...5abD`; UUPS upgrade via `UPGRADER_ROLE`. | onchain | current at snapshot | high | `review_required` if changed |
| Underlying asset | wYLDS YieldVault `0x6aD0...66Cc`. | onchain | current at snapshot | high | `review_required` if changed |
| Token behavior | Non-rebasing ERC-4626-like vault share using external NAV feed. | onchain / issuer source | current at snapshot | high | `review_required` for implementation/feed changes |
| Issuer / governing entity | Signum Ltd.; wholly owned by Provenance Cayman Foundation per terms. | legal_terms | dated terms, accessed 2026-06-04 | medium/high for text | continue for explanation; `review_required` for legal reliance |
| Mechanism | wYLDS described as backed 1:1 by YLDS; PRIME accrues wYLDS from Figure Democratized Prime HELOC operations. | legal_terms / issuer_docs | dated/current | medium | `review_required` for exposure quality |
| Reserve / proof metrics | Hastra proof page displayed backing and supply metrics plus audit labels. | issuer_docs | current when extracted | medium | `cannot_rank_cleanly` / `review_required` without report bodies |
| Current reserve/custody attestation | Not found as a report body in parent research. | unknown | unknown | low | `cannot_rank_cleanly` / `review_required` |
| Legal eligibility | Terms exclude U.S. and sanctioned/illegal jurisdictions and allow verification/blocking. | legal_terms | dated/current | high for text, medium for process | `review_required`; `block_automation` for real primary redemption absent confirmation |
| PRIME transfer restriction | Freeze-based transfer block; no PRIME transfer whitelist found. | onchain / issuer source | current at snapshot | high | continue; `review_required` for compliance conclusions |
| PRIME forced transfer | No PRIME forced-transfer function found in reviewed source. | issuer source | current at snapshot | medium/high | `review_required` before compliance-action assumptions |
| PRIME redemption | Redeem/withdraw returns wYLDS using NAV oracle. | onchain / issuer source | current at snapshot | high | `review_required` for full USDC settlement |
| wYLDS redemption | YieldVault requestRedeem + admin completeRedeem from redeemVault USDC. | issuer source / onchain | current at snapshot | high for mechanics | `block_automation` without live settlement/eligibility checks |
| Claim token / NFT | None found; YieldVault uses internal pending-redemption mapping/events. | issuer source | current at snapshot | medium/high | continue |
| Secondary ETH liquidity | Uniswap V3 PRIME/USDC 0.01% pool with size-dependent quote cliff. | onchain / market_data | current point-in-time | high for pool/quote sample, medium for future depth | `block_automation` without fresh route quote |
| Market history | 30-day CoinGecko sample around 1.034–1.041; longer stress history not established. | market_data | current point-in-time | medium | continue for explanation; `review_required` for stress modeling |
| Oracle source | FeedVerifier Chainlink Data Streams-style NAV/redemption-rate feed. | onchain / issuer source | current at snapshot | high for contract use, medium for off-chain formula | `review_required` |
| Staleness window | `defaultMaxStaleness = 3600` seconds on-chain. | onchain | current at snapshot | high | `review_required` if unset/changed |
| Admin Safe | Safe 4-of-7; no modules observed in parent probe. | governance / onchain | current at snapshot | high | `review_required` if changed |
| Operational EOAs | `0xA8C3...faCd` immediate operational powers; `0xF0a5...3cd` FeedVerifier updater. | onchain | current at snapshot | high for address/role, low for off-chain identity | `review_required` |
| Pending governance | One unexecuted Safe tx affecting YieldVault role split. | governance | current when checked | high | `review_required`; `block_automation` if executed before action |
| Audit/current security review | Exact deployed public audit report not found; proof page labels lacked report body/scope. | issuer_docs / unknown | unknown | low | `review_required` |
| Gearbox support/oracle notes | Not checked/found in this scoped parent research pass. | unknown | unknown | low | continue unless Gearbox integration depends on it, then `review_required` |

## 12. Highest-impact unknowns

| Unknown / caveat | Why it matters | missing_behavior | Source basis / confidence |
|---|---|---|---|
| Exact off-chain NAV/redemption-rate construction for active feed ID was not found. | On-chain use is clear, but the feed's off-chain inputs and controls determine whether NAV tracks practical backing/exit value. | `review_required` for collateral valuation; `block_automation` if feed freshness/construction is required for execution. | On-chain FeedVerifier high [S1], [S8]; off-chain methodology missing, confidence high that missing. |
| Current reserve/custody/attestation report bodies for wYLDS/YLDS backing were not located. | Terms/proof page establish issuer-stated backing, but independent scope and reconciliation are not confirmed. | `cannot_rank_cleanly` and `review_required`. | Terms/proof page medium [S4], [S6]; missing report bodies high. |
| Public audit scope for deployed PRIME / FeedVerifier was not located. | Source verification is not an audit; deployed scope, unresolved highs/criticals, and recency remain unknown. | `review_required`. | Sourcify/source high [S2], [S3], [S8]; audit body missing high [S6], [S7]. |
| User-specific eligibility/KYC/redemption process and SLA were not fully specified. | Primary mint/redeem/settle flows can depend on jurisdiction, information requests, property blocking, admin completion, and redeemVault funds. | `review_required`; `block_automation` for real exit execution without live eligibility/settlement confirmation. | Terms medium/high [S4]; YieldVault mechanics high [S9]. |
| Exact operational identity and off-chain control process for Safe owners and EOA role holders were not established. | On-chain holders can pause, freeze, upgrade, update oracle, and manage settlement path; named governance/process controls are not known. | `review_required`. | On-chain/Safe state high [S1], [S12]; identity/process missing high. |
| Current frozen-account set cannot be globally enumerated from storage without candidate addresses. | Events showed no PRIME freezes and two YieldVault frozen accounts, but arbitrary account status must be checked directly before action. | `continue` for dossier; `block_automation` for acting on a specific account without live freeze checks. | Event scans/direct checks high for observed candidates [S1], [S3], [S9]. |
| Ethereum DEX liquidity can cliff near visible USDC pool inventory. | A nominal NAV/spot price can overstate executable exit value for larger sizes. | `block_automation` for any real exit without fresh route quote. | On-chain quote/pool data high at snapshot [S1], DEXScreener medium/high [S10]. |
| No confirmed exact-token exploit/depeg/oracle-failure/redemption-delay postmortem was found in bounded sources. | Absence of evidence should not be treated as clean incident history. | `continue` for context; `review_required` for acceptance checks that require incident completeness. | Bounded source search missing, confidence medium [S4], [S6], [S7]. |

## 13. Sources

| ID | URL / local evidence | source_class | freshness | accessed | confidence | Notes |
|---|---|---|---|---|---|---|
| S1 | `https://ethereum.publicnode.com` / `https://ethereum-rpc.publicnode.com` plus local raw snapshots `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/hastra-prime/raw/onchain-admin-snapshot-2026-06-04.json` and `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/hastra-prime/raw/feed-verifier-snapshot-2026-06-04.json` | onchain | current at snapshot blocks `25243546` / `25243587` / `25243612` / `25243627` as reported by parent artifacts | 2026-06-04 | high | Direct Ethereum mainnet RPC / Foundry checks for proxy slots, token calls, roles, FeedVerifier state, pause/freeze events, Safe calls, pool balances, and Uniswap quotes. |
| S2 | `https://repo.sourcify.dev/contracts/full_match/1/0x19ebb35279A16207Ec4ba82799CC64715065F7F6/metadata.json` | onchain | current when fetched | 2026-06-04 | high | Sourcify full-match metadata for the PRIME proxy. |
| S3 | `https://repo.sourcify.dev/contracts/full_match/1/0x90fd843c68db38e2de0618AcBB39341CbA5A5abD/metadata.json` and `https://repo.sourcify.dev/contracts/full_match/1/0x90fd843c68db38e2de0618AcBB39341CbA5A5abD/sources/contracts/StakingVault.sol`; mirrored repo URL `https://github.com/provenance-io/hastra-eth-vault/blob/1b91d4eb0eca9bd71b1284cd7d0cb05279e2affd/contracts/StakingVault.sol` | onchain / issuer source | current when fetched | 2026-06-04 | high | Verified PRIME implementation source for ERC-4626/NAV/freeze/pause/upgrade behavior. |
| S4 | `https://hastra.io/terms` | legal_terms | dated terms, last updated 2025-12-03 per parent artifact | 2026-06-04 | medium/high | Official Hastra terms for issuer entity, mechanism, wYLDS/YLDS/PRIME descriptions, eligibility restrictions, and blocking language. |
| S5 | `https://hastra.io/` | issuer_docs | current when fetched | 2026-06-04 | medium | Official Hastra product site for live product/category statements. |
| S6 | `https://hastra.io/proof-of-reserves` | issuer_docs | current when extracted | 2026-06-04 | medium | Official proof-of-reserves page with displayed wYLDS/PRIME/vaulted-wYLDS/backing metrics and audit labels; report bodies/scopes were not exposed in parent extraction. |
| S7 | `https://github.com/provenance-io/hastra-eth-vault`, `https://github.com/provenance-io/hastra-eth-vault/blob/main/deployment_mainnet.json`, `https://github.com/provenance-io/hastra-eth-vault/blob/main/docs/ROLES.md`, `https://github.com/provenance-io/hastra-eth-vault/blob/main/docs/KEY_MANAGEMENT.md`, and docs under commit `1b91d4eb0eca9bd71b1284cd7d0cb05279e2affd` | issuer_docs / source | current repo state when fetched, with some stale README/status text noted | 2026-06-04 | medium | Official public repository and operational docs; use source/docs where corroborated by on-chain state, treat conflicting deployment/audit status prose as stale. |
| S8 | `https://repo.sourcify.dev/contracts/full_match/1/0xdF4ab20fA7752Be52E41e42F1FD667f37964d6a3/metadata.json`, `https://repo.sourcify.dev/contracts/full_match/1/0xbC6023cb49F8E8cA6cef563d5FD97ba4C6A5D937/metadata.json`, `https://repo.sourcify.dev/contracts/full_match/1/0xbC6023cb49F8E8cA6cef563d5FD97ba4C6A5D937/sources/contracts/FeedVerifier.sol`, `https://github.com/provenance-io/hastra-eth-vault/blob/1b91d4eb0eca9bd71b1284cd7d0cb05279e2affd/chainlink-hub/contracts/FeedVerifier.sol`, and `https://github.com/provenance-io/hastra-eth-vault/blob/1b91d4eb0eca9bd71b1284cd7d0cb05279e2affd/chainlink-hub/docs/FeedVerifier.md` | onchain / issuer source / oracle docs | current when fetched | 2026-06-04 | high for source/on-chain behavior, medium for prose docs | FeedVerifier proxy/implementation/source/docs for NAV feed behavior, staleness, allowed feed ID, updater role, and Chainlink Data Streams dependency. |
| S9 | `https://github.com/provenance-io/hastra-eth-vault/blob/1b91d4eb0eca9bd71b1284cd7d0cb05279e2affd/contracts/YieldVault.sol` plus repo compliance docs under `https://github.com/provenance-io/hastra-eth-vault/tree/1b91d4eb0eca9bd71b1284cd7d0cb05279e2affd/docs` | issuer source / issuer_docs | current when fetched | 2026-06-04 | high for source mechanics, medium for operational docs | YieldVault/wYLDS redemption, pendingRedemptions, completeRedeem, freeze/thaw, whitelist/redeemVault mechanics. |
| S10 | `https://api.dexscreener.com/token-pairs/v1/ethereum/0x19ebb35279A16207Ec4ba82799CC64715065F7F6` and `https://dexscreener.com/ethereum/0x5b70a1582135bd04e39ca94a6a56fc3a828e3115` | market_data | point-in-time current | 2026-06-04 | high for reported pair at extraction, medium for future depth | DEXScreener Ethereum PRIME/USDC pair, liquidity, volume, pair creation, and price fields. |
| S11 | `https://www.coingecko.com/en/coins/hastra-prime` and CoinGecko public API `/api/v3/coins/hastra-prime` | market_data | point-in-time current | 2026-06-04 | medium | Global PRIME price/volume/history data; global markets include non-Ethereum venues and should not be used as Ethereum-only exit depth. |
| S12 | `https://safe-transaction-mainnet.safe.global/api/v1/safes/0x8D358B8aE881F8ea92C3d07783aBCA21727C6309/` and related Safe multisig transaction endpoint plus on-chain Safe calls | governance / onchain | current when checked | 2026-06-04 | high | Safe owners/threshold/modules/guard/pending transaction evidence for current admin/upgrader governance surface. |
| P1 | `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/hastra-prime/onchain-admin.md` | onchain synthesis artifact | current local parent artifact | 2026-06-04 | high where backed by listed sources | Parent research for identity/admin/FeedVerifier details; cited original sources above for material claims. |
| P2 | `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/eth-mainnet-prime/issuer-backing-security.md` | synthesis artifact | current local parent artifact | 2026-06-04 | medium/high where backed by listed sources | Parent research for issuer/backing/security details; cited original sources above for material claims. |
| P3 | `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/eth-mainnet-prime/transfer-liquidity-oracle-governance.md` | synthesis artifact | current local parent artifact | 2026-06-04 | medium/high where backed by listed sources | Parent research for transfer/redemption/liquidity/oracle/governance details; cited original sources above for material claims. |
