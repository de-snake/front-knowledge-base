# Saturn sUSDat — onchain/admin research

Access date: 2026-06-04
Scope supplied by kanban card: Ethereum mainnet (`chain_id=1`), `sUSDat`, `0xd166337499e176bbc38a1fbd113ab144e5bd2df7`.
Pipeline coverage: methodology sections 1 and 4 only.
Do not treat this as an investment recommendation or suitability verdict.

## Concise facts summary

- `sUSDat` is deployed on Ethereum mainnet at `0xD166337499E176bbC38a1FBd113Ab144e5bd2Df7` and returns `name=Staked USDat`, `symbol=sUSDat`, `decimals=18` from direct RPC calls.
- The token is an ERC-20 / ERC-20Permit / ERC-4626-style share token. `asset()` is USDat at `0x23238F20B894f29041f48d88Ee91131c395aAA71` (`USDat`, 6 decimals). Standard ERC-4626 `withdraw` and `redeem` are disabled; exits use `requestRedeem` and the withdrawal queue at `0x4Bc9FEC04F0F95e9b42a3EF18F3C96fB57923D2e`.
- The sUSDat implementation is UUPS-upgradeable behind an ERC-1967 proxy. The current EIP-1967 implementation slot points to `0x2005E0CA201A37694125fF267aE57872bEa0a0Ce`; the EIP-1967 admin slot is zero, consistent with UUPS rather than Transparent proxy admin control.
- sUSDat `DEFAULT_ADMIN_ROLE` is currently held by both an EOA (`0x610182581C93687Ca03F4a8E7f124f8cEC616820`) and a Saturn timelock (`0xfD5782E3BFF366601da3973aE30C583dE4F08A67`). Because the EOA still holds the role, default-admin actions are immediate today even though a 5-day timelock path also exists.
- A pending timelock operation is scheduled to revoke `DEFAULT_ADMIN_ROLE` from `0x610182581C93687Ca03F4a8E7f124f8cEC616820` on sUSDat, USDat, the STRC oracle, and the withdrawal queue. As of the RPC snapshot used here, all four operations had `OperationState=1` (`Waiting`) with ready timestamps on 2026-06-08 UTC; the EOA role should be rechecked after that time.
- No Safe multisig was identified among current sUSDat role holders. The timelock has a 432,000 second / 5 day minimum delay, open executor role (`address(0)`), and an EOA proposer/canceller (`0x610182581C93687Ca03F4a8E7f124f8cEC616820`).
- Most sensitive controls are AccessControl roles rather than Ownable: default admin/upgrader/rescue/unpause/fee/tolerance/rewards settings; processor conversion/reward/withdrawal processing; compliance blacklist/pause/seizure. Existing holder impact is not purely future-issuance-only: blacklist, pause, redistribution of blacklisted balances, forced transfer/seizure of underlying or withdrawal claims, and upgrades can affect existing holders.

## 1. Identity and token semantics

### 1.1 Pinned identity

| Field | Value | Source / confidence |
|---|---:|---|
| Chain | Ethereum mainnet | user-supplied scope + RPC, high |
| chain_id | `1` | user-supplied scope, high |
| Token address | `0xD166337499E176bbC38a1FBd113Ab144e5bd2Df7` | user-supplied scope + Etherscan token page + RPC, high |
| Etherscan label | `Saturn: sUSDat Token`; token tracker `Staked USDat (sUSDat)` | Etherscan, onchain explorer, high |
| `name()` | `Staked USDat` | direct RPC call, onchain, high |
| `symbol()` | `sUSDat` | direct RPC call, onchain, high |
| `decimals()` | `18` | direct RPC call + verified source line, onchain, high |
| Share/token standard | ERC-20, ERC-20Permit, ERC-4626-style vault share token | verified source imports/inheritance and function behavior, onchain, high |
| ERC-4626 `asset()` | `0x23238F20B894f29041f48d88Ee91131c395aAA71` (`USDat`, 6 decimals) | direct RPC call + USDat RPC, onchain, high |
| Withdrawal queue | `0x4Bc9FEC04F0F95e9b42a3EF18F3C96fB57923D2e` | `getWithdrawalQueue()` RPC + verified source, onchain, high |
| STRC oracle dependency | `0x5f7EcD0D045C393DA6CB6C933C671AC305a871BF` | `getStrcOracle()` RPC + verified source, onchain, high |
| Current paused status | `false` | `paused()` RPC, onchain, high |
| Current deposit fee | `0` bps; `feeRecipient=0x3dc0aa75A6Fd01C3dcf9f6FdAF08308B6489f5B5` | `depositFeeBps()` / `feeRecipient()` RPC, onchain, high |
| Current tolerance | `2000` bps | `toleranceBps()` RPC, onchain, high |
| Current max rewards | `250` bps of `totalAssets` | `maxRewardsBps()` RPC + source, onchain, high |
| Current vesting period | `259200` seconds / 3 days | `vestingPeriod()` RPC, onchain, high |

RPC freshness note: values above were checked against Ethereum public RPC around block `25,243,633-25,243,686` on 2026-06-04. A raw replay/evidence snapshot is stored at `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/eth-mainnet-susdat/raw/onchain-admin-snapshot-2026-06-04.json`.

### 1.2 Mechanism and token semantics

- Official Saturn site describes USDat as a non-yielding stablecoin backed 100% by tokenized U.S. treasuries and sUSDat as the staked version of USDat backed 100% by digital credit / STRC; it states that as digital credit dividends accrue, sUSDat price increases. Source class: issuer_docs, accessed 2026-06-04, confidence medium because this is website prose rather than contract state.
- Saturn app insights reported sUSDat TVL, APY, and sUSDat collateral split as `USDat: $8.0M / 8.3%` and `STRC: $88.5M / 91.7%`, updated every hour. Source class: issuer_docs / app data, accessed 2026-06-04, confidence medium.
- Verified `StakedUSDat` source implements `totalAssets()` as internally tracked `usdatBalance + _strcTotalAssets()`. `_strcTotalAssets()` prices vested STRC using `STRC_ORACLE.getPrice()`; unvested STRC rewards vest over `vestingPeriod`. Source class: onchain verified source, confidence high.
- Deposits/mints accept USDat and mint sUSDat shares. `previewDeposit`/`previewMint` account for the deposit fee. `depositWithPermit` and `mintWithPermit` variants support EIP-2612 / EIP-1271 permit flows. Source class: onchain verified source, confidence high.
- Standard ERC-4626 `withdraw` and `redeem` revert with `OperationNotAllowed`; holder exits use `requestRedeem`, which escrows sUSDat shares into the withdrawal queue and mints a withdrawal request NFT. Claims are routed through the queue. Source class: onchain verified source, confidence high.
- sUSDat has blacklist checks on `transfer`, `transferFrom`, deposits, and withdrawal request creation. The withdrawal queue additionally checks both sUSDat blacklist and USDat frozen status for relevant claim/seizure flows. Source class: onchain verified source, confidence high.

## 4. Contract admin, multisigs, and sensitive actions

### 4.1 Proxy / implementation / upgradeability status

| Contract | Address | Pattern | Current implementation / admin | Upgrade authority | Source / confidence |
|---|---:|---|---|---|---|
| sUSDat | `0xD166337499E176bbC38a1FBd113Ab144e5bd2Df7` | ERC-1967 proxy + UUPS implementation | implementation slot: `0x2005E0CA201A37694125fF267aE57872bEa0a0Ce`; admin slot: zero | `StakedUSDat._authorizeUpgrade` is `onlyRole(DEFAULT_ADMIN_ROLE)` | EIP-1967 storage RPC + verified source, high |
| WithdrawalQueueERC721 | `0x4Bc9FEC04F0F95e9b42a3EF18F3C96fB57923D2e` | ERC-1967 proxy + UUPS implementation | implementation slot: `0x256fA0ba1b6dFB50EE883955c5a99D3C1b017Fd5`; admin slot: zero | `WithdrawalQueueERC721._authorizeUpgrade` is `onlyRole(DEFAULT_ADMIN_ROLE)` | EIP-1967 storage RPC + verified source, high |
| STRC oracle | `0x5f7EcD0D045C393DA6CB6C933C671AC305a871BF` | non-proxy `StrcPriceOracle` AccessControl contract | no proxy slot used in this report; source exact-match verified | default admin can update wrapped oracle, staleness, price bounds | Etherscan verified source + RPC, high |
| USDat underlying asset | `0x23238F20B894f29041f48d88Ee91131c395aAA71` | TransparentUpgradeableProxy | implementation slot: `0x17cAC25c6D6BBcB592837FEA083A5c8Eb4D1E52E`; proxy admin slot: `0xcf1072DA5f0D127AEf99136489BAd08bFa3D1A7D`; ProxyAdmin owner: `0x610182581C93687Ca03F4a8E7f124f8cEC616820` | ProxyAdmin owner EOA for implementation changes; AccessControl roles for business controls | EIP-1967 storage RPC + ProxyAdmin `owner()` + verified source, high |

Recent implementation changes observed for sUSDat:

- `Upgraded` at block `24629457` to `0x02e8E482eb836Cdf58B94AD5C3c5Fe18088287A00`.
- `Upgraded` at block `24742253` to `0x167db384014444CBd3b59c9132C1AbF0ef59aC6e`.
- `Upgraded` at block `24778165` to current `0x2005E0CA201A37694125fF267aE57872bEa0a0Ce`.

Recent implementation changes observed for the withdrawal queue:

- `Upgraded` at block `24629457` to `0xe7aE41677085Ef1472E9c7B947868924695D857e`.
- `Upgraded` at block `24742311` to current `0x256fA0ba1b6dFB50EE883955c5a99D3C1b017Fd5`.

### 4.2 Current role holders and holder types

#### sUSDat roles

| Role | Current holder(s) | Holder type | Sensitive powers | Source / confidence |
|---|---|---|---|---|
| `DEFAULT_ADMIN_ROLE` | `0x610182581C93687Ca03F4a8E7f124f8cEC616820`; `0xfD5782E3BFF366601da3973aE30C583dE4F08A67` | EOA; Timelock contract | grants/revokes roles; UUPS upgrades; `redistributeLockedAmount`; `rescueTokens`; `setVestingPeriod`; `setDepositFee`; `setFeeRecipient`; `setTolerance`; `setMaxRewardsBps`; `unpause` | RoleGranted/RoleRevoked logs reconstructed, source, RPC code checks, high |
| `PROCESSOR_ROLE` | `0x09D6E34cE24D54890fF0BC6a090b5f880F8C729f` | EOA | `convertFromUsdat`, `convertFromStrc`, `transferInRewards` | Role logs + verified source, high |
| `COMPLIANCE_ROLE` | `0x10D59F776db12b4B271b2609CB8b7Ddd0A82703B` | EOA | blacklist/unblacklist; pause | Role logs + verified source, high |
| Separate owner / minter / burner / oracle reporter role | none identified in sUSDat verified source | n/a | sUSDat mints via ERC-4626 deposit; burns through queue-limited functions; oracle dependency is immutable `STRC_ORACLE` | verified source, high |
| Proxy admin | none for sUSDat UUPS proxy; EIP-1967 admin slot is zero | n/a | upgrades are implementation-authorized by `DEFAULT_ADMIN_ROLE` | storage RPC + source, high |

sUSDat role-change history observed:

- Deployment/init block `24629457`: grants default admin to `0x610182...`, compliance and processor to `0x8CBA689B49f15E0a3c8770496Df8E88952d6851d`.
- Block `24786279`: grants processor to `0x09D6E34c...`.
- Block `24786285`: grants compliance to `0x10D59F77...`.
- Blocks `24792544-24792545`: revokes old compliance/processor `0x8CBA689B...`.
- Block `25233263`: grants default admin to timelock `0xfD5782...`.

#### Withdrawal queue roles

| Role | Current holder(s) | Holder type | Sensitive powers | Source / confidence |
|---|---|---|---|---|
| `DEFAULT_ADMIN_ROLE` | `0x610182581C93687Ca03F4a8E7f124f8cEC616820`; `0xfD5782E3BFF366601da3973aE30C583dE4F08A67` | EOA; Timelock contract | UUPS upgrades; role admin; `unpause` | Role logs + source, high |
| `PROCESSOR_ROLE` | `0x09D6E34cE24D54890fF0BC6a090b5f880F8C729f` | EOA | lock/unlock withdrawal requests; process requests; supply USDat and trigger sUSDat queued-share burn | Role logs + source, high |
| `COMPLIANCE_ROLE` | `0x10D59F776db12b4B271b2609CB8b7Ddd0A82703B` | EOA | `seizeRequests`, `seizeBlacklistedFunds`, `pause` | Role logs + source, high |
| `STAKED_USDAT_ROLE` | `0xD166337499E176bbC38a1FBd113Ab144e5bd2Df7` | sUSDat contract | add requests; claim-for-user helpers | Role logs + source, high |

Current queue state checked by RPC: `paused=false`; `pendingCount=65`. Source class: onchain, confidence high.

#### STRC oracle roles and parameters

| Field / role | Value | Holder type / meaning | Source / confidence |
|---|---|---|---|
| Oracle contract | `0x5f7EcD0D045C393DA6CB6C933C671AC305a871BF` | `StrcPriceOracle` verified source | Etherscan source + sUSDat `getStrcOracle()`, high |
| Wrapped price oracle | `0xf4d2076277FFf631eFC4385AB36b1f7734218d23` | Chainlink-compatible source called by `getPrice()` | RPC `getOracle()`, high |
| `DEFAULT_ADMIN_ROLE` | `0x610182581C93687Ca03F4a8E7f124f8cEC616820`; `0xfD5782E3BFF366601da3973aE30C583dE4F08A67` | EOA; Timelock | Role logs, high |
| Max staleness | `93600` seconds / 26 hours from `maxPriceStaleness()` | bounded by `MAX_STALENESS=36 hours` | RPC + source, high |
| Price bounds | min `20e8`, max `150e8`; latest `getPrice()` returned `(94.72e8, 8 decimals)` | bounds on STRC price used by sUSDat accounting and queue processing | RPC + source, high |
| Oracle reporter role | no reporter role identified in `StrcPriceOracle`; default admin can update the wrapped oracle and validation bounds | n/a | verified source, high |

#### Timelock details

| Timelock | Value | Source / confidence |
|---|---|---|
| Address | `0xfD5782E3BFF366601da3973aE30C583dE4F08A67` | role holder + Etherscan verified `SaturnTimelock`, high |
| Contract type | SaturnTimelock over OpenZeppelin `TimelockController` | verified source, high |
| Minimum delay | `432000` seconds / 5 days | `getMinDelay()` RPC, high |
| Default admin | timelock self (`hasRole(DEFAULT_ADMIN_ROLE, timelock)=true`) | RPC `hasRole`, high |
| Proposer | `0x610182581C93687Ca03F4a8E7f124f8cEC616820` | RPC `hasRole(PROPOSER_ROLE)`, high |
| Canceller | `0x610182581C93687Ca03F4a8E7f124f8cEC616820` | RPC `hasRole(CANCELLER_ROLE)`, high |
| Executor | `address(0)` open executor sentinel | RPC `hasRole(EXECUTOR_ROLE, address(0))`, high |
| Safe threshold / owners | none found; no Safe multisig role holder identified for sUSDat admin roles | code checks + role holders, medium |

Pending timelock operations observed on 2026-06-04:

| Target | Intended call | Operation id prefix | State | Ready timestamp | Existing-holder relevance |
|---|---|---:|---|---|---|
| sUSDat `0xD166...2Df7` | `revokeRole(DEFAULT_ADMIN_ROLE, 0x610182...)` | `e60ba7c4` | `Waiting` | `2026-06-08T01:00:59Z` | would remove immediate EOA path for sUSDat default-admin actions if executed |
| USDat `0x2323...AA71` | `revokeRole(DEFAULT_ADMIN_ROLE, 0x610182...)` | `b659b081` | `Waiting` | `2026-06-08T00:56:23Z` | would remove immediate EOA path for USDat AccessControl default admin if executed |
| STRC oracle `0x5f7E...71BF` | `revokeRole(DEFAULT_ADMIN_ROLE, 0x610182...)` | `a9cd5bd6` | `Waiting` | `2026-06-08T01:03:11Z` | would remove immediate EOA path for oracle admin if executed |
| Withdrawal queue `0x4Bc9...3D2e` | `revokeRole(DEFAULT_ADMIN_ROLE, 0x610182...)` | `fb99c6de` | `Waiting` | `2026-06-08T01:04:59Z` | would remove immediate EOA path for queue admin if executed |

`OperationState=1` follows OpenZeppelin TimelockController enum ordering `Unset=0, Waiting=1, Ready=2, Done=3`. Source class: onchain logs + RPC, confidence high. Missing behavior: recheck after the ready timestamps before relying on current execution-speed classifications.

#### USDat underlying asset controls relevant to sUSDat

USDat is outside the exact sUSDat token address but is `asset()` for sUSDat and is checked by the withdrawal queue (`USDAT.isFrozen(account)`), so its freeze/proxy controls can affect sUSDat entry and exit flows.

| Control | Current holder(s) / status | Holder type | Sensitive powers | Source / confidence |
|---|---|---|---|---|
| USDat proxy admin | ProxyAdmin `0xcf1072DA5f0D127AEf99136489BAd08bFa3D1A7D`; owner `0x610182581C93687Ca03F4a8E7f124f8cEC616820` | ProxyAdmin contract owned by EOA | upgrade USDat Transparent proxy implementation | storage RPC + ProxyAdmin `owner()`, high |
| USDat `DEFAULT_ADMIN_ROLE` | `0x610182581C93687Ca03F4a8E7f124f8cEC616820`; `0xfD5782E3BFF366601da3973aE30C583dE4F08A67` | EOA; Timelock | AccessControl role admin | USDat role logs, high |
| `FREEZE_MANAGER_ROLE` | `0x10D59F776db12b4B271b2609CB8b7Ddd0A82703B` | EOA | freeze/unfreeze accounts through inherited extension | role logs + source, high |
| `FORCED_TRANSFER_MANAGER_ROLE` | `0x10D59F776db12b4B271b2609CB8b7Ddd0A82703B` | EOA | forced transfer from frozen accounts | role logs + USDat `_forceTransfer` source, high |
| `PAUSER_ROLE` | `0x10D59F776db12b4B271b2609CB8b7Ddd0A82703B` | EOA | pause USDat | role logs + RPC `paused=false`, high |
| `WHITELIST_MANAGER_ROLE` | `0x10D59F776db12b4B271b2609CB8b7Ddd0A82703B` | EOA | enable/disable whitelist, whitelist/remove accounts | source + RPC `isWhitelistEnabled=true`, high |
| `YIELD_RECIPIENT_MANAGER_ROLE` | `0x09D6E34cE24D54890fF0BC6a090b5f880F8C729f` | EOA | yield recipient management in inherited extension | role logs, medium because inherited source not fully expanded here |
| `ASSET_CAP_MANAGER_ROLE` | `0x7D343D17896D2cd87A49b4fB8872298A883f78f7` | Timelock contract, 5 day delay | asset cap management in inherited extension | role logs + `getMinDelay()`, medium |

### 4.3 Sensitive action classification

Methodology labels used:
`existing_holder_impact: none | indirect | direct_freeze | direct_transfer | direct_dilution | direct_redemption_block | unknown`
`execution_speed: immediate | timelocked | governance_vote | unknown`

Because sUSDat default admin is held by both an EOA and a timelock, default-admin action speed is classified as `immediate` until the pending EOA revocations are executed. If the revocations execute and no other immediate admin remains, those actions should be reclassified as `timelocked` for the timelock path.

| Sensitive action | Contract / role | Existing holder impact | Execution speed | Notes / source |
|---|---|---|---|---|
| UUPS upgrade sUSDat implementation | sUSDat `DEFAULT_ADMIN_ROLE` | `unknown` | `immediate` today; potentially `timelocked` after pending revocation | Upgrade can change semantics; current source gates `_authorizeUpgrade` by default admin. |
| UUPS upgrade withdrawal queue | Queue `DEFAULT_ADMIN_ROLE` | `unknown` | `immediate` today; potentially `timelocked` after pending revocation | Queue controls withdrawal request processing and claim NFT logic. |
| Upgrade USDat implementation | USDat ProxyAdmin owner `0x610182...` | `unknown` | `immediate` | Transparent proxy admin is ProxyAdmin owned by EOA; separate from USDat AccessControl timelock grant. |
| Add/remove sUSDat blacklist | sUSDat `COMPLIANCE_ROLE` | `direct_freeze` | `immediate` | Blacklisted addresses cannot transfer, deposit, or request withdrawals; admin addresses cannot be blacklisted by source guard. |
| Pause sUSDat | sUSDat `COMPLIANCE_ROLE` | `direct_redemption_block` | `immediate` | Paused state makes max deposit/mint zero, max redeem zero, blocks transfers through `_update`, and disables request flows. |
| Unpause sUSDat | sUSDat `DEFAULT_ADMIN_ROLE` | `none` / unblocks | `immediate` today | Default admin only. |
| Redistribute locked amount | sUSDat `DEFAULT_ADMIN_ROLE` | `direct_transfer` | `immediate` today | Burns a blacklisted holder's full sUSDat balance and leaves value to other holders; requires target already blacklisted and totalSupply greater than target balance. |
| Rescue tokens | sUSDat `DEFAULT_ADMIN_ROLE` | `indirect` | `immediate` today | For USDat asset, source only allows rescue of excess over internally tracked `usdatBalance`; other accidentally sent tokens can be transferred. |
| Set deposit fee / recipient | sUSDat `DEFAULT_ADMIN_ROLE` | `indirect` | `immediate` today | Fee affects future deposits/mints; max fee 500 bps. Current fee is 0 bps. |
| Set vesting period | sUSDat `DEFAULT_ADMIN_ROLE` | `indirect` | `immediate` today | Affects timing of STRC rewards becoming counted in assets; bounded by max 90 days; cannot change while rewards still vesting. |
| Set tolerance / max rewards bps | sUSDat `DEFAULT_ADMIN_ROLE` | `indirect` | `immediate` today | Affects oracle tolerance and rewards validation used by processor flows. |
| Convert USDat to/from STRC | sUSDat `PROCESSOR_ROLE` | `indirect` | `immediate` | Changes backing mix and internal balances; guarded by oracle/tolerance validation. |
| Transfer in rewards | sUSDat `PROCESSOR_ROLE` | `indirect` / possible dilution timing effects | `immediate` | Adds STRC rewards with vesting; bounded by `maxRewardsBps`. |
| Request redemption processing / locking | Withdrawal queue `PROCESSOR_ROLE` | `direct_redemption_block` | `immediate` | Processor locks/unlocks request NFTs and finalizes processed withdrawals; users cannot standard ERC-4626 withdraw/redeem directly. |
| Queue seizure of blacklisted requests/funds | Withdrawal queue `COMPLIANCE_ROLE` | `direct_transfer` | `immediate` | `seizeRequests` and `seizeBlacklistedFunds` operate only when owner is blacklisted/frozen per source checks. |
| Pause withdrawal queue | Withdrawal queue `COMPLIANCE_ROLE` | `direct_redemption_block` | `immediate` | Blocks queue operations and NFT movement; unpause by default admin. |
| Update STRC oracle address | STRC oracle `DEFAULT_ADMIN_ROLE` | `indirect` | `immediate` today; potentially `timelocked` after pending revocation | sUSDat totalAssets and queue processing depend on oracle price. |
| Set STRC oracle staleness / price bounds | STRC oracle `DEFAULT_ADMIN_ROLE` | `indirect` / possible redemption-processing block if invalid | `immediate` today | `getPrice()` reverts if stale, non-positive, or outside bounds. |
| USDat freeze / forced transfer | USDat freeze / forced-transfer roles | `direct_freeze` / `direct_transfer` | `immediate` | USDat freeze status is checked by the withdrawal queue and affects claims/seizures involving sUSDat exits. |
| USDat whitelist enable/disable and account whitelisting | USDat `WHITELIST_MANAGER_ROLE` | `direct_redemption_block` or `indirect` depending path | `immediate` | USDat source enforces whitelist on wrapping/unwrapping when enabled; current `isWhitelistEnabled=true`. |
| USDat pause | USDat `PAUSER_ROLE` | `direct_redemption_block` / `indirect` | `immediate` | Underlying asset pause can affect USDat operations used around sUSDat. Current `paused=false`. |
| Governance vote | none identified | `unknown` | `unknown` | No DAO governor or Safe threshold found in current role holders; timelock proposer is an EOA. |

### 4.4 Recent sensitive admin transactions / events

- sUSDat role migration to timelock: `DEFAULT_ADMIN_ROLE` granted to `0xfD5782E3BFF366601da3973aE30C583dE4F08A67` at block `25233263`.
- Withdrawal queue role migration to timelock: `DEFAULT_ADMIN_ROLE` granted to `0xfD5782E3BFF366601da3973aE30C583dE4F08A67` at block `25233217`.
- USDat role migration to timelock: `DEFAULT_ADMIN_ROLE` granted to `0xfD5782E3BFF366601da3973aE30C583dE4F08A67` at block `25233293`.
- STRC oracle role migration to timelock: `DEFAULT_ADMIN_ROLE` granted to `0xfD5782E3BFF366601da3973aE30C583dE4F08A67` at block `25233327`.
- Pending timelock operations then schedule revocation of `DEFAULT_ADMIN_ROLE` from `0x610182...` on all four contracts, ready on 2026-06-08 UTC. Recheck before relying on immediate-admin classification after that timestamp.
- sUSDat deposit fee was updated to `0` at block `24772848`.
- sUSDat vesting period was updated twice, ending at `259200` seconds / 3 days at block `24886377`.
- sUSDat blacklist events were observed for `0x60B77b654aC5c0876Aa9F16A642DC541b5A19aCF` at block `25170727` and `0x7c82cB4b2909C50c7C0F2B696Eee7565E0A23BB8` at block `25170866`; no unblacklist events were found in the scanned range.
- No sUSDat pause/unpause events were found in the scanned range.

## Highest-impact unknowns and missing-data behavior

| Unknown / caveat | Why it matters | missing_behavior | Confidence |
|---|---|---|---|
| Human/entity identity and operational controls for EOAs `0x610182...`, `0x09D6...`, and `0x10D5...` were not verified from a primary Saturn governance/source document. | These EOAs currently hold immediate admin, processor, compliance, and/or timelock proposer powers. | `review_required` | medium |
| No Safe multisig was identified for sUSDat role holders; therefore Safe threshold/owners are not applicable from the onchain holders found. | If a Safe exists offchain but is not the role holder, it is not enforceable onchain for these roles. | `continue` | medium |
| Timelock role event reconstruction did not show constructor RoleGranted logs via address logs, so timelock role holders were checked with direct `hasRole` calls instead. | Role state is verified, but full timelock role-change history is less complete than the role state. | `continue` | medium |
| Pending timelock revocations are not yet executed as of the snapshot. | Admin execution speed may change from immediate to timelocked after 2026-06-08 UTC. | `review_required` | high |
| Sourcify full/partial match was not found for sUSDat; Etherscan verified source was used as the primary source. | Independent source verification source unavailable from Sourcify. | `continue` | medium |
| Underlying USDat inherited extension roles were only partially source-expanded in this section. | USDat freeze/whitelist/proxy controls can affect sUSDat exits and claims; full USDat risk belongs in a broader underlying-asset pass. | `review_required` | medium |
| Offchain terms, eligibility restrictions, and legal freeze policy were not part of this onchain/admin-only artifact. | Contract freeze/whitelist powers exist, but policy/process for use requires issuer/legal source review. | `review_required` | medium |

## Source list

| Source | URL | source_class | Accessed | Confidence | Notes |
|---|---|---|---|---|---|
| Methodology | `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/methodology.md` | unknown | 2026-06-04 | high | Labels and missing-data behavior used for this artifact. |
| sUSDat Etherscan address / verified source | `https://etherscan.io/address/0xD166337499E176bbC38a1FBd113Ab144e5bd2Df7` | onchain | 2026-06-04 | high | Verified proxy/source page; source extracted for `StakedUSDat`. |
| Withdrawal queue Etherscan address / verified source | `https://etherscan.io/address/0x4Bc9FEC04F0F95e9b42a3EF18F3C96fB57923D2e` | onchain | 2026-06-04 | high | Verified proxy/source page; source extracted for `WithdrawalQueueERC721`. |
| STRC oracle Etherscan address / verified source | `https://etherscan.io/address/0x5f7EcD0D045C393DA6CB6C933C671AC305a871BF` | onchain | 2026-06-04 | high | Verified exact-match source for `StrcPriceOracle`. |
| Saturn timelock Etherscan address / verified source | `https://etherscan.io/address/0xfD5782E3BFF366601da3973aE30C583dE4F08A67` | onchain | 2026-06-04 | high | Verified exact-match source for `SaturnTimelock`; delay and roles checked by RPC. |
| USDat Etherscan address / verified source | `https://etherscan.io/address/0x23238F20B894f29041f48d88Ee91131c395aAA71` | onchain | 2026-06-04 | high | Underlying asset for sUSDat; Transparent proxy and role state checked because USDat affects sUSDat exits. |
| Ethereum public RPC | `https://ethereum-rpc.publicnode.com` | onchain | 2026-06-04 | high | Used for `eth_call`, EIP-1967 storage slots, event logs, role state, timelock operation state. Raw snapshot persisted at `research/eth-mainnet-susdat/raw/onchain-admin-snapshot-2026-06-04.json`. |
| Saturn official site | `https://saturn.credit/` | issuer_docs | 2026-06-04 | medium | Mechanism prose for USDat and sUSDat. |
| Saturn app insights | `https://app.saturn.credit/insights` | issuer_docs | 2026-06-04 | medium | TVL, APY, collateral split; page says data updates every minute/hour depending widget. |
| Sourcify repository checks | `https://repo.sourcify.dev/contracts/full_match/1/0xd166337499e176bbc38a1fbd113ab144e5bd2df7/metadata.json` and partial-match equivalent | onchain | 2026-06-04 | low | Returned 404 for sUSDat; used only as negative source-availability evidence. |
