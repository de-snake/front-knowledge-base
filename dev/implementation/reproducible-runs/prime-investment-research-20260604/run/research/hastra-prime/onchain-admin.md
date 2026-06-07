# Hastra PRIME — onchain/admin research

Report date: 2026-06-04 UTC
Analyst: Hermes kanban worker
Task scope: MVP mining pipeline sections 1 and 4 only — identity/token semantics and contract admin/multisigs/sensitive actions.
Input asset: Ethereum mainnet (`chain_id: 1`), `0x19ebb35279A16207Ec4ba82799CC64715065F7F6`, symbol `PRIME`, intended use unknown.
Output type: objective source-linked facts, not token selection, ranking, suitability, or investment advice.

Raw evidence produced in this run:

- `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/hastra-prime/raw/onchain-admin-snapshot-2026-06-04.json`
- `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/hastra-prime/raw/feed-verifier-snapshot-2026-06-04.json`

## Source index

| ID | URL / local evidence | source_class | freshness | accessed | confidence | Notes |
|---|---|---:|---:|---:|---:|---|
| S1 | `https://ethereum.publicnode.com` plus raw snapshot `onchain-admin-snapshot-2026-06-04.json` | onchain | current | 2026-06-04 | high | Direct Ethereum mainnet RPC calls at snapshot block `25243587` for PRIME and associated contracts. |
| S2 | `https://repo.sourcify.dev/contracts/full_match/1/0x19ebb35279A16207Ec4ba82799CC64715065F7F6/metadata.json` | onchain | current | 2026-06-04 | high | Sourcify full-match metadata for the PRIME proxy. |
| S3 | `https://repo.sourcify.dev/contracts/full_match/1/0x90fd843c68db38e2de0618AcBB39341CbA5A5abD/metadata.json` | onchain | current | 2026-06-04 | high | Sourcify full-match metadata for PRIME implementation `StakingVault`. |
| S4 | `https://repo.sourcify.dev/contracts/full_match/1/0x90fd843c68db38e2de0618AcBB39341CbA5A5abD/sources/contracts/StakingVault.sol` | onchain | current | 2026-06-04 | high | Verified implementation source for role and sensitive-function inspection. |
| S5 | `https://github.com/provenance-io/hastra-eth-vault/blob/main/deployment_mainnet.json` | issuer_docs | current | 2026-06-04 | medium | Official public deployment file, cloned at HEAD `1b91d4eb0eca9bd71b1284cd7d0cb05279e2affd`; corroborated by on-chain/Sourcify. |
| S6 | `https://github.com/provenance-io/hastra-eth-vault/blob/main/docs/ROLES.md` | issuer_docs | current | 2026-06-04 | medium | Official role reference; used as documentation of intended role meanings, not as sole evidence of current holders. |
| S7 | `https://github.com/provenance-io/hastra-eth-vault/blob/main/docs/KEY_MANAGEMENT.md` | issuer_docs | current | 2026-06-04 | medium | Official key-management intent; current holders verified on-chain. |
| S8 | `https://hastra.io/terms` | legal_terms | dated | 2026-06-04 | medium | Terms page, last updated 2025-12-03; used for issuer/protocol and PRIME semantic claims. |
| S9 | `https://hastra.io/` | issuer_docs | current | 2026-06-04 | medium | Official site; used for live product/category statements. |
| S10 | `https://hastra.io/proof-of-reserves` | issuer_docs | current | 2026-06-04 | medium | Official reserve/NAV page; used only as context for PRIME/wYLDS semantics in this section-scope report. |
| S11 | `https://ethereum.publicnode.com` plus raw snapshot `feed-verifier-snapshot-2026-06-04.json` | onchain | current | 2026-06-04 | high | Direct Ethereum mainnet RPC calls at snapshot block `25243627` for FeedVerifier roles/state. |
| S12 | `https://repo.sourcify.dev/contracts/full_match/1/0xdF4ab20fA7752Be52E41e42F1FD667f37964d6a3/metadata.json` | onchain | current | 2026-06-04 | high | Sourcify full-match metadata for FeedVerifier proxy. |
| S13 | `https://repo.sourcify.dev/contracts/full_match/1/0xbC6023cb49F8E8cA6cef563d5FD97ba4C6A5D937/metadata.json` | onchain | current | 2026-06-04 | high | Sourcify full-match metadata for FeedVerifier implementation. |
| S14 | `https://repo.sourcify.dev/contracts/full_match/1/0xbC6023cb49F8E8cA6cef563d5FD97ba4C6A5D937/sources/contracts/FeedVerifier.sol` | onchain | current | 2026-06-04 | high | Verified FeedVerifier implementation source. |
| S15 | `https://github.com/provenance-io/hastra-eth-vault/blob/main/chainlink-hub/docs/FeedVerifier.md` | issuer_docs | current | 2026-06-04 | medium | Official FeedVerifier operational/role doc; current state verified on-chain. |

## 1. Identity and token semantics

### Canonical identity

| Field | Value | Evidence |
|---|---|---|
| Chain | Ethereum mainnet, `chain_id: 1` | Input scope; S1 high. |
| Token/proxy address | `0x19ebb35279A16207Ec4ba82799CC64715065F7F6` | Input scope; code/state verified on S1 high and S2 high. |
| Name | `Hastra PRIME` | Direct `name()` call, S1 high. |
| Symbol | `PRIME` | Direct `symbol()` call, S1 high. |
| Decimals | `6` | Direct `decimals()` call, S1 high. |
| Current implementation | `0x90fd843c68db38e2de0618AcBB39341CbA5A5abD` | EIP-1967 implementation slot, S1 high; Sourcify full match, S3 high. |
| Proxy type | OpenZeppelin `ERC1967Proxy` | Sourcify compilation target, S2 high. |
| Proxy admin slot | EIP-1967 admin slot is zero; beacon slot is zero | Raw EIP-1967 storage snapshot, S1 high. |
| Upgrade pattern | UUPS-style implementation with `UPGRADE_INTERFACE_VERSION() = "5.0.0"`; upgrade authorization is AccessControl `UPGRADER_ROLE` | S1 high; verified `StakingVault.sol` `_authorizeUpgrade(... ) onlyRole(UPGRADER_ROLE)`, S4 high. |
| First observed proxy code block | `24901862` | Binary-search RPC evidence in raw snapshot, S1 high. |

### Token standard and behavior

- PRIME is an upgradeable ERC-4626 vault-share token over underlying asset `0x6aD038cA6C04e885630851278ca0a856Ad9a66Cc` (`Hastra wYLDS`, 6 decimals), because the verified `StakingVault` implementation inherits/overrides ERC-4626 deposit, mint, redeem, withdraw, `asset()`, `totalAssets()`, `convertToShares`, and `convertToAssets`; the on-chain `asset()` and `yieldVault()` both return `0x6aD038cA6C04e885630851278ca0a856Ad9a66Cc`. Sources: S1 high, S4 high.
- PRIME is not an ordinary fixed-balance ERC-20 exposure: it is a non-rebasing ERC-4626 share token whose share/asset conversions use a NAV feed (`getVerifiedNav()`) instead of the default ERC-4626 total-assets/total-supply ratio. Sources: S1 high, S4 high.
- The official terms describe PRIME as a liquid staking token received by staking wYLDS, representing participation in Figure Democratized Prime HELOC lending pools; PRIME accrues wYLDS based on the performance of Figure's Democratized Prime HELOC lending operations. Source: S8 medium.
- The official site describes PRIME as live on Solana and Ethereum and as liquid staking to earn against Figure HELOCs. Source: S9 medium.

### Current on-chain token state at snapshot block `25243587`

| Field | Raw value | Human-scale note | Evidence |
|---|---:|---:|---|
| `totalSupply()` | `129096016382551` | `129,096,016.382551 PRIME` | S1 high. |
| `totalAssets()` | `134374638283899` | `134,374,638.283899 wYLDS` | S1 high. |
| `getVerifiedNav()` | `1040904685772521320` | `1.040904685772521320 wYLDS / PRIME` | S1 high. |
| `getTotalValueAtNav()` | `139871190638698` | `139,871,190.638698` units at NAV-adjusted 6-decimal scale | S1 high. |
| `paused()` | `false` | Vault was not paused at snapshot. | S1 high. |
| `navOracle()` | `0xdF4ab20fA7752Be52E41e42F1FD667f37964d6a3` | FeedVerifier proxy. | S1 high. |
| `navFeedId()` | `0x0007c8ed155d952e003b1e15ce7666fea785cfbe216577d578fce3920e997271` | Current NAV Data Streams feed ID used by PRIME. | S1 high. |
| `rewardPeriodSeconds()` | `3540` | Minimum seconds between `distributeRewards` calls. | S1 high. |
| `maxRewardPercent()` | `7500000000000000` | `0.75%` max per distribution by current managed assets. | S1 high; S4 high. |
| `maxPeriodRewards()` | `1000000000000` | `1,000,000.000000 wYLDS` per call cap. | S1 high; S4 high. |
| `maxTotalRewards()` | `10000000000000` | `10,000,000.000000 wYLDS` lifetime reward cap. | S1 high; S4 high. |
| `totalRewardsDistributed()` | `222666313185` | `222,666.313185 wYLDS` distributed to vault accounting. | S1 high. |
| `lastRewardDistributedAt()` | `1780570019` | `2026-06-04T10:46:59Z`. | S1 high. |

### Asset classification for later agent use

| Dimension | Classification | Evidence / missing behavior |
|---|---|---|
| Asset type | issuer-controlled asset / RWA-linked liquid-staking vault share | S4 high for vault-share mechanics; S8 medium and S9 medium for Figure HELOC/real-world asset mechanism. Missing deeper issuer/backing analysis is outside this card; `missing_behavior: review_required` before treating as ordinary liquid collateral. |
| Token behavior | non-rebasing ERC-4626 vault share using external NAV feed for conversion | S1 high, S4 high. |
| Ordinary ERC-20 transferability | ERC-20 transfer path exists, but `_update` reverts if sender or receiver is frozen; pause does not wrap `_update` in the verified code. | S4 high. Frozen-address enumeration is non-enumerable; no `AccountFrozen`/`AccountThawed` events were observed from first code block to snapshot; S1 high. |
| Transition-stage asset possibility | Not a claim token or NFT receipt in the verified PRIME contract; it is a share token whose redeem/withdraw path depends on vault pause/freeze status and a non-stale NAV feed. | S4 high; missing sections 6/7 mean `missing_behavior: review_required` for execution decisions. |

## 4. Contract admin, multisigs, and sensitive actions

### PRIME proxy and upgradeability

| Field | Finding | Evidence |
|---|---|---|
| Proxy/implementation | Proxy `0x19ebb...F7F6`; implementation `0x90fd...5abD`. | S1 high, S2 high, S3 high. |
| Proxy admin | No transparent proxy admin address in EIP-1967 admin slot; no beacon. | S1 high. |
| Upgrade gate | UUPS implementation `_authorizeUpgrade(address)` is restricted to `onlyRole(UPGRADER_ROLE)`. | S4 high. |
| Current upgrader | `0x8D358B8aE881F8ea92C3d07783aBCA21727C6309` only. | S1 high; holders reconstructed from all RoleGranted/RoleRevoked logs and checked with `hasRole()`. |
| Holder type | Gnosis Safe v1.4.1, threshold `4`, owners `7`, modules list empty in `getModulesPaginated` probe. | S1 high. |
| Timelock | No timelock contract was identified as a current role holder; the Safe can execute after threshold is met. | S1 high. `missing_behavior: review_required` for any action that assumes delayed execution. |

### Current PRIME role holders

All role holders below are current as of snapshot block `25243587`; each holder was derived from `RoleGranted`/`RoleRevoked` event history and verified with `hasRole()` where listed in the raw snapshot. Source: S1 high.

| Role | Role hash | Current holder(s) | Holder type | Admin role | Notes |
|---|---|---|---|---|---|
| `DEFAULT_ADMIN_ROLE` | `0x0000000000000000000000000000000000000000000000000000000000000000` | `0x8D358B8aE881F8ea92C3d07783aBCA21727C6309` | Safe 4-of-7 | self-admin | Can grant/revoke all roles and call default-admin setters. |
| `UPGRADER_ROLE` | `0x189ab7a9244df0848122154315af71fe140f3db0fe014031783b0946b8c9d2e3` | `0x8D358B8aE881F8ea92C3d07783aBCA21727C6309` | Safe 4-of-7 | `DEFAULT_ADMIN_ROLE` | Authorizes UUPS upgrades. |
| `PAUSER_ROLE` | `0x65d7a28e3265b37a6474929f336521b332c1681b933f6cb9f3376673440d862a` | `0xA8C3CF6183D49d5D372f8FC149BD2cb5CFC0faCd` | EOA | `DEFAULT_ADMIN_ROLE` | Can pause/unpause. |
| `FREEZE_ADMIN_ROLE` | `0x543dd7347cde3308f4ca610f3d5b513c0c1ce692b559bf3b9637d9557d3aede9` | `0xA8C3CF6183D49d5D372f8FC149BD2cb5CFC0faCd` | EOA | `DEFAULT_ADMIN_ROLE` | Can freeze/thaw accounts. |
| `REWARDS_ADMIN_ROLE` | `0x5b1d514dc7939e180020b5e45c6b4b0b997babf2832f415121a45e9091b5b54b` | `0xA8C3CF6183D49d5D372f8FC149BD2cb5CFC0faCd` | EOA | `DEFAULT_ADMIN_ROLE` | Can distribute rewards into the staking vault. |
| `NAV_ORACLE_UPDATER_ROLE` | `0x8c05f61760c0f173f6ac4249c7cb7cb780b3447e46ec8c842d5198905761e0cf` | none | none | `DEFAULT_ADMIN_ROLE` | No current holder; `DEFAULT_ADMIN_ROLE` can grant it. |

Safe details for `0x8D358B8aE881F8ea92C3d07783aBCA21727C6309`: `VERSION()` returned `1.4.1`; `getThreshold()` returned `4`; `getOwners()` returned 7 owners; `getModulesPaginated(0x0000000000000000000000000000000000000001,10)` returned an empty module list. Source: S1 high.

The operational EOA `0xA8C3CF6183D49d5D372f8FC149BD2cb5CFC0faCd` has no bytecode at snapshot, so it is classified as EOA. Source: S1 high.

### PRIME sensitive action matrix

| Action / function | Current authorized role | Current holder type | existing_holder_impact | execution_speed | Evidence / notes |
|---|---|---|---|---|---|
| `upgradeToAndCall` / UUPS upgrade | `UPGRADER_ROLE` | Safe 4-of-7 | unknown | immediate | A new implementation can change token/admin behavior; no on-chain timelock observed. S1 high, S4 high. Missing behavior: `review_required` before relying on immutability or delayed execution. |
| `grantRole` / `revokeRole` | role admin, effectively `DEFAULT_ADMIN_ROLE` for listed roles | Safe 4-of-7 | indirect | immediate | Can grant pauser/freezer/upgrader/rewards/oracle roles. S1 high, S4 high. |
| `pause()` | `PAUSER_ROLE` | EOA | direct_redemption_block | immediate | `deposit`, `depositWithPermit`, `mint`, `redeem`, `withdraw`, and `distributeRewards` require `whenNotPaused`; ordinary ERC-20 `_update` is not paused in verified code. S4 high. Pause history: 2 pause and 2 unpause events; current `paused=false`. S1 high. |
| `unpause()` | `PAUSER_ROLE` | EOA | indirect | immediate | Restores paused functions after pause. S1 high, S4 high. |
| `freezeAccount(address)` | `FREEZE_ADMIN_ROLE` | EOA | direct_freeze | immediate | `_update` reverts if `from` or `to` is frozen, blocking transfers involving the frozen account; docs state frozen accounts cannot transfer, receive, deposit, or redeem. S4 high, S6 medium. No `AccountFrozen` events observed from first code block through snapshot. S1 high. |
| `thawAccount(address)` | `FREEZE_ADMIN_ROLE` | EOA | indirect | immediate | Reverses frozen-account state. S4 high. |
| `distributeRewards(uint256)` | `REWARDS_ADMIN_ROLE` | EOA | indirect | immediate | Increases `_totalManagedAssets`, calls `yieldVault.mintRewards(address(this), amount)`, and is constrained by cooldown, per-call cap, lifetime cap, and max percent. S1 high, S4 high. |
| `setMaxRewardPercent(uint256)` | `DEFAULT_ADMIN_ROLE` | Safe 4-of-7 | indirect | immediate | Changes per-distribution percent cap. S1 high, S4 high. No update events observed. S1 high. |
| `setMaxPeriodRewards(uint256)` | `DEFAULT_ADMIN_ROLE` | Safe 4-of-7 | indirect | immediate | Changes per-call absolute reward cap. S1 high, S4 high. No update events observed. S1 high. |
| `setRewardPeriodSeconds(uint256)` | `DEFAULT_ADMIN_ROLE` | Safe 4-of-7 | indirect | immediate | Changes reward-distribution cooldown. S1 high, S4 high. No update events observed. S1 high. |
| `setMaxTotalRewards(uint256)` | `DEFAULT_ADMIN_ROLE` | Safe 4-of-7 | indirect | immediate | Changes lifetime reward ceiling; cannot set below already distributed amount. S4 high. No update events observed. S1 high. |
| `setYieldVault(address)` | `DEFAULT_ADMIN_ROLE` | Safe 4-of-7 | indirect | immediate | Changes the external YieldVault used for reward minting; no `YieldVaultUpdated` events observed. S1 high, S4 high. |
| `setNavOracle(address,bytes32)` | `NAV_ORACLE_UPDATER_ROLE` if granted | none currently | direct_redemption_block | unknown | If set to zero/invalid/stale feed, `getVerifiedNav()` and ERC-4626 conversions can revert, blocking deposit/redeem/withdraw. No current role holder; DEFAULT_ADMIN can grant the role. S1 high, S4 high. |
| Admin PRIME mint/burn | none identified | n/a | none | n/a | No separate admin PRIME minter/burner role was identified in `StakingVault`. PRIME shares are minted/burned through standard ERC-4626 deposit/mint/redeem/withdraw flows. S4 high. |
| Blacklist role | no separate blacklist role; freeze admin exists | EOA freezer | direct_freeze | immediate | Freeze/thaw is the observed restriction mechanism. S4 high, S6 medium. |
| Rescue role | none identified on PRIME `StakingVault` | n/a | none | n/a | No token rescue/withdraw function was identified in verified PRIME implementation. S4 high. |
| Fee setter | none identified on PRIME `StakingVault` | n/a | none | n/a | No PRIME vault fee setter was identified in verified implementation. S4 high. |
| Registry setter | none identified on PRIME `StakingVault` | n/a | none | n/a | No registry setter was identified in verified implementation. S4 high. |

Execution-speed note: `immediate` means no on-chain timelock was found. Safe-controlled actions still require 4-of-7 Safe approval before final execution; once approved, the on-chain execution is not timelocked. Source: S1 high.

### PRIME admin event history

Material admin/config events observed from deployment through snapshot (raw event list in S1):

- Deployment/initialization at block `24901862` (`2026-04-17T20:07:23Z`), tx `0xa0fe19e31a28f06df7d6d515b7b694252558debef305cb0c5fd36c68f42c4a3f`: initial upgrade event to implementation `0x90fd...5abD`; deployer `0x5f134E02dbDd7514E0E166f8D55BB2E6D06659b3` received default admin, pauser, upgrader. Source: S1 high.
- Operational roles were initially granted to deployer during setup, then moved: `PAUSER_ROLE`, `FREEZE_ADMIN_ROLE`, and `REWARDS_ADMIN_ROLE` were granted to `0xA8C3...faCd` on 2026-04-24; deployer operational roles were revoked later. Source: S1 high.
- Safe `0x8D358...6309` received `DEFAULT_ADMIN_ROLE` and `UPGRADER_ROLE` on 2026-04-29; deployer admin/upgrader roles were revoked on 2026-05-05. Source: S1 high.
- `NAV_ORACLE_UPDATER_ROLE` was granted to deployer during setup and revoked on 2026-05-05; no holder remains at snapshot. Source: S1 high.
- `NavOracleUpdated` occurred twice: initial feed `0x000700f43b35146a1cb16373ac6225ad597535e928e6dc4d179c3b4225f2b6d3` on 2026-04-17; current feed `0x0007c8ed155d952e003b1e15ce7666fea785cfbe216577d578fce3920e997271` on 2026-04-23. Source: S1 high.
- Pause windows observed: 2026-05-04 21:51:11Z to 23:55:11Z; 2026-06-02 14:53:47Z to 15:29:47Z. Current state is unpaused. Source: S1 high.
- No `AccountFrozen` or `AccountThawed` events were observed from first code block through snapshot. Source: S1 high.
- `RewardsDistributed` count observed: 712; sample includes latest observed reward at block `25243520`, `2026-06-04T10:46:59Z`, amount `855.162330 wYLDS`. Source: S1 high.

### FeedVerifier / NAV oracle admin surface

The PRIME vault reads NAV from FeedVerifier proxy `0xdF4ab20fA7752Be52E41e42F1FD667f37964d6a3` and feed ID `0x0007c8ed155d952e003b1e15ce7666fea785cfbe216577d578fce3920e997271`. Source: S1 high.

FeedVerifier current state at snapshot block `25243627`:

| Field | Value | Evidence |
|---|---|---|
| Proxy | `0xdF4ab20fA7752Be52E41e42F1FD667f37964d6a3` | S11 high. |
| Implementation | `0xbC6023cb49F8E8cA6cef563d5FD97ba4C6A5D937` | S11 high; S13 high. |
| Verified contract | `FeedVerifier` | S13 high, S14 high. |
| `verifierProxy()` | `0x5A1634A86e9b7BfEf33F0f3f3EA3b1aBBc4CC85F` | S11 high. |
| `paused()` | `false` | S11 high. |
| `allowedFeedId()` | `0x0007c8ed155d952e003b1e15ce7666fea785cfbe216577d578fce3920e997271` | S11 high. |
| `defaultMaxStaleness()` | `3600` seconds | S11 high, S14 high. |
| `maxStalenessByFeed(current)` | `0` | Falls back to default 3600 seconds; S11 high. |
| `priceByFeed(current)` | `1040906939176726297` | `1.040906939176726297` NAV price, S11 high. |
| `timestampByFeed(current)` | `1780571081` | `2026-06-04T11:04:41Z`, S11 high. |
| `lastFeedId()` | current feed ID | S11 high. |

FeedVerifier current roles at snapshot block `25243627`:

| Role | Current holder(s) | Holder type | Admin role | Evidence |
|---|---|---|---|---|
| `DEFAULT_ADMIN_ROLE` | `0x8D358B8aE881F8ea92C3d07783aBCA21727C6309` | Safe 4-of-7 | self-admin | S11 high. |
| `UPGRADER_ROLE` | `0x8D358B8aE881F8ea92C3d07783aBCA21727C6309` | Safe 4-of-7 | `DEFAULT_ADMIN_ROLE` | S11 high. |
| `PAUSER_ROLE` | `0xA8C3CF6183D49d5D372f8FC149BD2cb5CFC0faCd` | EOA | `DEFAULT_ADMIN_ROLE` | S11 high. |
| `UPDATER_ROLE` | `0xF0a5baEBF749562fAe5f3d9d2928357ae6cd73cd` | EOA | `DEFAULT_ADMIN_ROLE` | S11 high. |

FeedVerifier sensitive actions:

| Action / function | Current authorized role | Holder type | existing_holder_impact | execution_speed | Evidence / notes |
|---|---|---|---|---|---|
| UUPS upgrade | `UPGRADER_ROLE` | Safe 4-of-7 | unknown | immediate | `_authorizeUpgrade` requires `UPGRADER_ROLE`; no timelock holder found. S11 high, S14 high. |
| `setAllowedFeedId(bytes32)` | `DEFAULT_ADMIN_ROLE` | Safe 4-of-7 | direct_redemption_block | immediate | Restricts accepted reports; wrong/disabled feed can prevent fresh valid NAV and later block PRIME conversions through stale/invalid oracle path. S11 high, S14 high. |
| `setMaxStaleness(uint32)` | `DEFAULT_ADMIN_ROLE` | Safe 4-of-7 | direct_redemption_block | immediate | Sets default staleness; too-low staleness can make `priceOf()` revert after reports age. S11 high, S14 high. |
| `setMaxStalenessByFeed(bytes32,uint32)` | `DEFAULT_ADMIN_ROLE` | Safe 4-of-7 | direct_redemption_block | immediate | Per-feed staleness override. S11 high, S14 high. |
| `pause()` / `unpause()` | `PAUSER_ROLE` | EOA | indirect | immediate | Pausing blocks new `verifyReport` / `verifyBulkReports`; stale price can then block PRIME conversions after staleness limit. S11 high, S14 high. |
| `verifyReport(bytes)` / `verifyBulkReports(bytes[])` | `UPDATER_ROLE` | EOA | indirect | immediate | Updates stored NAV only after Chainlink Data Streams verification; caller is an EOA bot wallet. S11 high, S14 high, S15 medium. |
| `withdrawEth(address)` | `DEFAULT_ADMIN_ROLE` | Safe 4-of-7 | none | immediate | Withdraws ETH held by FeedVerifier for verification fees; no direct PRIME holder balance impact identified. S14 high. |

FeedVerifier admin event highlights: initial deployment at block `24894016` on 2026-04-16; feed ID changed to current `0x0007c8ed...7271` on 2026-04-23; updater moved to `0xF0a5...3cd` on 2026-04-24; Safe received default admin/upgrader on 2026-04-29; deployer default admin/upgrader/pauser revoked by 2026-05-05; no FeedVerifier pause/unpause events observed. Source: S11 high.

## Highest-impact unknowns and missing-data behavior for this card

| Field / question | Current status | missing_behavior | Why |
|---|---|---|---|
| Whether every current Safe owner is controlled by a named entity/team and whether off-chain approvals exist | unknown | review_required | On-chain Safe owner addresses/threshold are known, but owner identity and off-chain governance process are not established by this card. Sources S1/S11 high for addresses, missing identity source. |
| Whether Safe actions are subject to any off-chain delay policy | unknown | review_required | No on-chain timelock was found. Off-chain policy, if any, is not enforceable by the inspected contracts. |
| Frozen account set | no freeze/thaw events observed; mapping is not enumerable | continue | Event scan from first code block showed zero freeze/thaw events; however arbitrary address frozen state cannot be batch-enumerated without a candidate list. |
| Full issuer/backing/redemption/liquidity analysis | outside this card | review_required | Sections 2, 3, 6, 7, and 8 were not in this card scope; PRIME should not be treated as ordinary liquid collateral solely from sections 1 and 4. |
| Audit/incident history | outside this card | review_required | Section 5 was not in scope; no audit verdict is implied here. |
| Exact operational identity of EOA role holders `0xA8C3...faCd` and `0xF0a5...3cd` | unknown | review_required | On-chain type is EOA; role purpose is inferred from role and docs, not from a signed/off-chain identity registry. |

## Minimal handoff summary

- PRIME at `0x19ebb35279A16207Ec4ba82799CC64715065F7F6` is a verified Ethereum mainnet OZ ERC1967/UUPS upgradeable ERC-4626 vault-share token over Hastra wYLDS, not an ordinary immutable ERC-20.
- The main PRIME admin/upgrader is Safe `0x8D358B8aE881F8ea92C3d07783aBCA21727C6309` (`4-of-7`, no modules observed); operational pauser/freezer/rewards roles are EOA `0xA8C3CF6183D49d5D372f8FC149BD2cb5CFC0faCd`; NAV oracle updater currently has no holder.
- Direct current-holder intervention surfaces exist: freeze can block transfers/deposits/redemptions for targeted accounts, pause can block ERC-4626 deposit/mint/redeem/withdraw, and oracle/feed admin can block conversions if NAV becomes unavailable or stale.
- No on-chain timelock was found for PRIME or FeedVerifier admin actions; Safe actions are multisig-thresholded but not timelocked on-chain.
