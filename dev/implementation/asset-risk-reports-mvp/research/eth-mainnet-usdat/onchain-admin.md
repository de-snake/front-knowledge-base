# Saturn USDat — onchain/admin research

Report date: 2026-06-04 UTC
Analyst: Hermes operator recovery after repeated Kanban worker crashes
Task scope: methodology sections 1 and 4 only — identity/token semantics and contract admin/multisigs/sensitive actions.
Input asset: Ethereum mainnet (`chain_id: 1`), `0x23238F20B894f29041f48d88Ee91131c395aAA71`, symbol `USDat`, intended use unknown.
Output type: objective source-linked facts, not token selection, ranking, suitability verdict, or investment recommendation.

Raw evidence used for this recovery:

- `research/eth-mainnet-usdat/raw/usdat-onchain-admin-snapshot-2026-06-04.json`
- `research/eth-mainnet-usdat/raw/source/USDatImplementation__src__USDat.sol`
- `research/eth-mainnet-usdat/raw/source/USDatImplementation__lib__m-extensions__src__components__freezable__Freezable.sol`
- `research/eth-mainnet-usdat/raw/source/USDatImplementation__lib__m-extensions__src__components__forcedTransferable__ForcedTransferable.sol`
- `research/eth-mainnet-usdat/raw/source/USDatImplementation__lib__m-extensions__src__components__pausable__Pausable.sol`
- `research/eth-mainnet-usdat/raw/source/USDatProxyAdmin__lib__openzeppelin-contracts__contracts__proxy__transparent__ProxyAdmin.sol`

## Source index

| ID | URL / local evidence | source_class | freshness | accessed | confidence | Notes |
|---|---|---:|---:|---:|---:|---|
| S1 | `research/eth-mainnet-usdat/raw/usdat-onchain-admin-snapshot-2026-06-04.json` | onchain | current | 2026-06-04 | high | Direct Ethereum RPC snapshot at block `25245745`: identity, proxy slots, role checks, ProxyAdmin owner, timelock role state. |
| S2 | `https://etherscan.io/address/0x23238F20B894f29041f48d88Ee91131c395aAA71` | onchain | current | 2026-06-04 | high | Etherscan token/proxy page for USDat. |
| S3 | local verified/source extracts under `research/eth-mainnet-usdat/raw/source/` | onchain | current | 2026-06-04 | high | Verified implementation and component source for whitelist, freeze, forced-transfer, pause, asset-cap, and proxy-admin mechanics. |
| S4 | `https://saturncredit.gitbook.io/saturn-docs/solution/usdat-overview` | issuer_docs | current | 2026-06-04 | medium | Official USDat product docs: fully collateralized stablecoin, $M backing, permissioned access, mint/redeem framing. |
| S5 | `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/methodology.md` | unknown | current | 2026-06-04 | high | Methodology labels and missing-data behavior. |

## Concise facts summary

- USDat is deployed on Ethereum mainnet at `0x23238F20B894f29041f48d88Ee91131c395aAA71`; direct RPC returned `name="USDat"`, `symbol="USDat"`, `decimals=6`, `paused=false`, and `isWhitelistEnabled=true`. Source: S1 high.
- The token is a TransparentUpgradeableProxy. The EIP-1967 implementation slot points to `0x17cAC25c6D6BBcB592837FEA083A5c8Eb4D1E52E`; the EIP-1967 admin slot points to ProxyAdmin `0xcf1072DA5f0D127AEf99136489BAd08bFa3D1A7D`; the ProxyAdmin owner is `0x610182581C93687Ca03F4a8E7f124f8cEC616820`. Source: S1 high.
- Verified `USDat` source inherits `JMIExtension` and `ForcedTransferable`. The implementation adds an internal whitelist and grants `WHITELIST_MANAGER_ROLE` to the compliance address at initialization. Sources: S1/S3 high.
- Current AccessControl role checks show `DEFAULT_ADMIN_ROLE` on USDat is held by both EOA `0x610182581C93687Ca03F4a8E7f124f8cEC616820` and SaturnTimelock `0xfD5782E3BFF366601da3973aE30C583dE4F08A67`. Because the EOA also owns the ProxyAdmin, USDat still has an immediate EOA-controlled upgrade path in this snapshot. Source: S1 high.
- Compliance powers are concentrated in EOA `0x10D59F776db12b4B271b2609CB8b7Ddd0A82703B`, which holds `PAUSER_ROLE`, `FREEZE_MANAGER_ROLE`, `FORCED_TRANSFER_MANAGER_ROLE`, and `WHITELIST_MANAGER_ROLE`. Source: S1 high.
- `ASSET_CAP_MANAGER_ROLE` is held by `0x7D343D17896D2cd87A49b4fB8872298A883f78f7`, a timelock contract with 432,000 second / 5-day minimum delay. Source: S1 high.

## 1. Identity and token semantics

### 1.1 Pinned identity

| Field | Value | Evidence |
|---|---:|---|
| Chain | Ethereum mainnet | task scope; S1 high |
| Token/proxy address | `0x23238F20B894f29041f48d88Ee91131c395aAA71` | task scope; S1/S2 high |
| Name | `USDat` | direct `name()` call, S1 high |
| Symbol | `USDat` | direct `symbol()` call, S1 high |
| Decimals | `6` | direct `decimals()` call, S1 high |
| Current paused status | `false` | direct `paused()` call, S1 high |
| Whitelist status | `isWhitelistEnabled=true` | direct call, S1 high |
| Proxy pattern | TransparentUpgradeableProxy | EIP-1967 admin + implementation slots, S1/S3 high |
| Current implementation | `0x17cAC25c6D6BBcB592837FEA083A5c8Eb4D1E52E` | EIP-1967 implementation slot, S1 high |
| ProxyAdmin | `0xcf1072DA5f0D127AEf99136489BAd08bFa3D1A7D` | EIP-1967 admin slot, S1 high |
| ProxyAdmin owner | `0x610182581C93687Ca03F4a8E7f124f8cEC616820` | ProxyAdmin `owner()`, S1 high |

### 1.2 Token standard and behavior

- USDat is an upgradeable ERC-20-style Saturn/M0 extension token, not an immutable ordinary ERC-20. The verified implementation inherits `JMIExtension` and `ForcedTransferable`; inherited components add AccessControl, pausing, freezing, forced-transfer, asset-cap, and yield-recipient mechanics. Sources: S1/S3 high.
- The local `USDat.sol` source defines whitelist storage and `WHITELIST_MANAGER_ROLE`; `enableWhitelist`, `disableWhitelist`, `whitelist`, and `removeFromWhitelist` are `onlyRole(WHITELIST_MANAGER_ROLE)`. It enforces whitelist checks before wrapping and unwrapping. Source: S3 high.
- Official Saturn docs describe USDat as Saturn's fully collateralized stablecoin backed by M0's `$M` tokenized U.S. Treasuries product. They also describe USDat as permissioned: only addresses that completed Saturn onboarding can mint, redeem, or hold USDat. Source: S4 medium.
- This means USDat should be handled as an issuer-controlled / permissioned stablecoin with whitelist, freeze, forced-transfer, pause, and upgrade controls, not as a free-transfer, immutable stablecoin. Missing behavior for ordinary-collateral assumptions: `review_required`.

## 4. Contract admin, multisigs, and sensitive actions

### 4.1 Proxy / implementation / upgradeability status

| Contract | Address | Pattern | Current admin / owner | Existing-holder relevance | Evidence |
|---|---:|---|---|---|---|
| USDat proxy | `0x23238F20B894f29041f48d88Ee91131c395aAA71` | TransparentUpgradeableProxy | ProxyAdmin `0xcf1072...1A7D`; owner `0x610182...6820` | Implementation upgrade can change all token behavior | S1/S3 high |
| USDat implementation | `0x17cAC25c6D6BBcB592837FEA083A5c8Eb4D1E52E` | verified implementation | n/a | Current logic includes whitelist, freeze, forced transfer, pause | S1/S3 high |
| SaturnTimelock | `0xfD5782E3BFF366601da3973aE30C583dE4F08A67` | TimelockController-derived | 5-day minimum delay, open executor | Holds USDat default admin but does not remove immediate ProxyAdmin owner path | S1/S3 high |
| AssetCapTimelock | `0x7D343D17896D2cd87A49b4fB8872298A883f78f7` | TimelockController-derived | 5-day minimum delay | Holds asset-cap manager role | S1 high |

### 4.2 Current role holders and holder types

| Role / control | Current holder(s) | Holder type | Sensitive powers | Source / confidence |
|---|---|---|---|---|
| ProxyAdmin owner | `0x610182581C93687Ca03F4a8E7f124f8cEC616820` | EOA | upgrades the Transparent proxy implementation | S1 high |
| `DEFAULT_ADMIN_ROLE` | `0x610182581C93687Ca03F4a8E7f124f8cEC616820`; `0xfD5782E3BFF366601da3973aE30C583dE4F08A67` | EOA; timelock | grants/revokes roles and controls AccessControl admin surface | S1 high |
| `PAUSER_ROLE` | `0x10D59F776db12b4B271b2609CB8b7Ddd0A82703B` | EOA | pause/unpause token flows | S1/S3 high |
| `FREEZE_MANAGER_ROLE` | `0x10D59F776db12b4B271b2609CB8b7Ddd0A82703B` | EOA | freeze/unfreeze accounts | S1/S3 high |
| `FORCED_TRANSFER_MANAGER_ROLE` | `0x10D59F776db12b4B271b2609CB8b7Ddd0A82703B` | EOA | forced transfer from frozen accounts | S1/S3 high |
| `WHITELIST_MANAGER_ROLE` | `0x10D59F776db12b4B271b2609CB8b7Ddd0A82703B` | EOA | enable/disable whitelist and add/remove accounts | S1/S3 high |
| `YIELD_RECIPIENT_MANAGER_ROLE` | `0x09D6E34cE24D54890fF0BC6a090b5f880F8C729f` | EOA | yield-recipient management in inherited extension | S1/S3 medium |
| `ASSET_CAP_MANAGER_ROLE` | `0x7D343D17896D2cd87A49b4fB8872298A883f78f7` | timelock | asset-cap management in inherited JMI extension | S1/S3 medium |

No Safe multisig role holder was identified in the current USDat role snapshot. Safe owner/threshold is therefore not applicable for the exact role holders found. Source: S1 high for code-length checks and role checks; missing_behavior: `continue` for this card, `review_required` if offchain operational policy claims a Safe path.

### 4.3 Timelock details

| Timelock | Address | Minimum delay | Role state observed | Evidence |
|---|---:|---:|---|---|
| SaturnTimelock | `0xfD5782E3BFF366601da3973aE30C583dE4F08A67` | 432,000 seconds / 5 days | self default admin; proposer and canceller `0x610182...6820`; executor `address(0)` open | S1 high |
| AssetCapTimelock | `0x7D343D17896D2cd87A49b4fB8872298A883f78f7` | 432,000 seconds / 5 days | self default admin; executor `address(0)` open; no proposer found among checked addresses in the bounded snapshot | S1 medium |

A companion Saturn recovery artifact observed pending timelock revocation of the immediate EOA default-admin path for USDat, ready around 2026-06-08 UTC. That operation is not proof of execution. Recheck current role state before relying on timelocked-only classification after that timestamp. Source class: onchain companion evidence; confidence medium/high.

### 4.4 Sensitive action classification

Methodology labels used: `existing_holder_impact: none | indirect | direct_freeze | direct_transfer | direct_dilution | direct_redemption_block | unknown`; `execution_speed: immediate | timelocked | governance_vote | unknown`.

| Sensitive action | Current authorized path | Holder type | existing_holder_impact | execution_speed | Evidence / notes |
|---|---|---|---|---|---|
| Upgrade USDat implementation | ProxyAdmin owner `0x610182...6820` | EOA | `unknown` | `immediate` | Upgrade can change token semantics. S1/S3. |
| Grant/revoke token roles | `DEFAULT_ADMIN_ROLE`: EOA + SaturnTimelock | EOA + timelock | `unknown` to direct depending role | `immediate` today because EOA holds role | S1. |
| Pause USDat | `PAUSER_ROLE` `0x10D59...03B` | EOA | `direct_redemption_block` / transfer block while paused | `immediate` | S1/S3. |
| Freeze accounts | `FREEZE_MANAGER_ROLE` `0x10D59...03B` | EOA | `direct_freeze` | `immediate` | S1/S3. |
| Forced transfer from frozen accounts | `FORCED_TRANSFER_MANAGER_ROLE` `0x10D59...03B` | EOA | `direct_transfer` | `immediate` | S1/S3. |
| Enable/disable whitelist | `WHITELIST_MANAGER_ROLE` `0x10D59...03B` | EOA | `direct_redemption_block` / transferability change for permissioned users | `immediate` | S1/S3. |
| Add/remove whitelisted account | `WHITELIST_MANAGER_ROLE` `0x10D59...03B` | EOA | `direct_redemption_block` for affected account | `immediate` | S1/S3. |
| Set asset cap | `ASSET_CAP_MANAGER_ROLE` AssetCapTimelock | timelock | `indirect` for future mint/wrap capacity | `timelocked` / 5 days | S1/S3. |
| Change yield recipient | `YIELD_RECIPIENT_MANAGER_ROLE` `0x09D6...729f` | EOA | `indirect` | `immediate` | Inherited extension; not fully expanded. S1/S3. |
| Governance vote | none identified | unknown | `unknown` | `unknown` | No DAO governor was found in current role holders. |

## Highest-impact unknowns and missing-data behavior for this card

| Unknown / caveat | Why it matters | missing_behavior | Confidence |
|---|---|---|---|
| Pending timelock role migration was not rechecked after its ready timestamp. | Execution speed may change if EOA roles are revoked, but ProxyAdmin owner path may still remain immediate. | `review_required` | high |
| Human/entity identity and operational policy for EOAs `0x610182...`, `0x10D59...`, and `0x09D6...` were not verified from a primary Saturn governance document. | Those EOAs hold upgrade/admin/compliance/yield controls. | `review_required` | medium |
| Full historical role-change event reconstruction was not completed for every inherited component. | Current role state is known, but change history is incomplete. | `continue` for current-state analysis; `review_required` for governance-monitor baselines | medium |
| Asset-cap and yield-recipient inherited behavior was only partially source-expanded. | These can affect issuance/capacity/economics. | `review_required` | medium |
| Offchain legal, onboarding, and freeze/forced-transfer policy are outside this onchain/admin card. | Contract powers exist; policy/process for using them affects issuer-control risk. | `review_required` | high |

## Minimal handoff summary

USDat at `0x23238F20B894f29041f48d88Ee91131c395aAA71` is a 6-decimal, permissioned, upgradeable Saturn stablecoin backed per issuer docs by `$M`. The live contract has whitelist enabled and exposes immediate compliance controls through EOA `0x10D59...03B`: pause, freeze, forced transfer, and whitelist management. Upgrade/admin control is not timelocked-only in this snapshot because ProxyAdmin owner and USDat `DEFAULT_ADMIN_ROLE` include EOA `0x610182...6820`; SaturnTimelock also holds default admin with 5-day delay. Downstream synthesis must carry issuer-control and permissioned-transfer assumptions, and must recheck role state before live automation.
