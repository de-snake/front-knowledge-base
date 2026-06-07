# Apyx apxUSD — onchain/admin research

Report date: 2026-06-04 UTC
Analyst: Hermes operator recovery after repeated Kanban worker crashes
Task scope: methodology sections 1 and 4 only — identity/token semantics and contract admin/multisigs/sensitive actions.
Input asset: Ethereum mainnet (`chain_id: 1`), `0x98A878b1Cd98131B271883B390f68D2c90674665`, symbol `apxUSD`, intended use unknown.
Output type: objective source-linked facts, not token selection, ranking, suitability verdict, or investment recommendation.

Raw evidence used for this recovery:

- `research/eth-mainnet-apxusd/raw/onchain-admin-snapshot-2026-06-04.json`
- `research/eth-mainnet-apxusd/raw/evm-contracts/src/ApxUSD.sol`
- `research/eth-mainnet-apxusd/raw/evm-contracts/src/MinterV0.sol`
- `research/eth-mainnet-apxusd/raw/evm-contracts/src/Roles.sol`
- `research/eth-mainnet-apxusd/raw/evm-contracts/src/exts/ERC20DenyListUpgradable.sol`
- `research/eth-mainnet-apxusd/raw/safe-pending-2026-06-04.json`

## Source index

| ID | URL / local evidence | source_class | freshness | accessed | confidence | Notes |
|---|---|---:|---:|---:|---:|---|
| S1 | `research/eth-mainnet-apxusd/raw/onchain-admin-snapshot-2026-06-04.json` | onchain | current | 2026-06-04 | high | Direct Ethereum RPC snapshot at block `25245413`: token identity, proxy slots, AccessManager roles, Safe-like holders, minter state. |
| S2 | `research/eth-mainnet-apxusd/raw/evm-contracts/src/ApxUSD.sol` | onchain | current | 2026-06-04 | medium/high | Public Apyx contract source used for token semantics, UUPS, supply cap, pause, deny-list, mint and admin functions. |
| S3 | `research/eth-mainnet-apxusd/raw/evm-contracts/src/MinterV0.sol` | onchain | current | 2026-06-04 | medium/high | Public Apyx contract source used for signed mint order and rate-limit mechanics. |
| S4 | `research/eth-mainnet-apxusd/raw/evm-contracts/src/Roles.sol` | onchain | current | 2026-06-04 | medium/high | Public Apyx role definitions and function-role assignment helpers. |
| S5 | `research/eth-mainnet-apxusd/raw/evm-contracts/src/exts/ERC20DenyListUpgradable.sol` | onchain | current | 2026-06-04 | medium/high | Deny-list transfer hook mechanics. |
| S6 | `research/eth-mainnet-apxusd/raw/safe-pending-2026-06-04.json` | governance | current | 2026-06-04 | medium | Safe Transaction Service snapshot of pending/unexecuted Safe transactions. |
| S7 | `https://docs.apyx.fi/product-overview/apxusd-overview` | issuer_docs | current | 2026-06-04 | medium | Official apxUSD mechanism and collateral/redemption context. |
| S8 | `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/methodology.md` | unknown | current | 2026-06-04 | high | Methodology labels and missing-data behavior. |

## Concise facts summary

- apxUSD is deployed on Ethereum mainnet at `0x98A878b1Cd98131B271883B390f68D2c90674665`; direct RPC returned `name="apxUSD"`, `symbol="apxUSD"`, `decimals=18`, `paused=false`, `supplyCap=750,000,000 apxUSD`, and total supply about `466.229m apxUSD` at block `25245413`. Source: S1 high.
- The token is an ERC-1967 UUPS proxy. The implementation slot points to `0xdd71fd677fde2ed2579a3c45204f41a11016ccb4`; EIP-1967 admin and beacon slots are zero; implementation `proxiableUUID` returned the ERC-1967 implementation slot. Source: S1 high.
- Source `ApxUSD.sol` describes apxUSD as a stablecoin backed by off-chain preferred shares with dividend yields; it implements ERC-20, permit, pausable, deny-list, burnable, AccessManager-controlled UUPS upgradeability, and a supply cap. Source: S2 medium/high.
- Live authority is AccessManager `0xe167330E2Eac88666de253e9607C6d9ae0cA2824`. Admin-like operational roles are primarily held by Safe-like contract `0xf9862EfC1704aC05e687f66E5cD8c130E5663CE2` (3-of-6), while AccessManager `ADMIN_ROLE` is held by Safe-like contract `0xabdd8c8ee69e5F5180EB9352AeFFc5CeEAd65e96` (4-of-6). Source: S1 high.
- Minting is not arbitrary token-level minting by an EOA. Token `mint(address,uint256,uint256)` is AccessManager role `4` with MinterV0 `0x2c36e1adfaa80ee0324b04cc814f5207bb7ba76e` as the callable candidate and an observed 14,400 second / 4-hour delay. MinterV0 separately validates signed orders, nonces, maximum mint amount, and a 24-hour rate limit. Sources: S1/S3 high.
- Direct holder-impact controls include pause, deny-list replacement, supply-cap changes, minting, UUPS upgrade, AccessManager authority rotation, CCIP admin rotation, and minter parameter changes. Source: S1/S2/S3.

## 1. Identity and token semantics

### 1.1 Pinned identity

| Field | Value | Evidence |
|---|---:|---|
| Chain | Ethereum mainnet | task scope; S1 high |
| Token/proxy address | `0x98A878b1Cd98131B271883B390f68D2c90674665` | task scope; S1 high |
| Name | `apxUSD` | direct `name()` call, S1 high |
| Symbol | `apxUSD` | direct `symbol()` call, S1 high |
| Decimals | `18` | direct `decimals()` call, S1 high |
| Current implementation | `0xdd71fd677fde2ed2579a3c45204f41a11016ccb4` | EIP-1967 implementation slot, S1 high |
| Proxy type | ERC-1967 proxy with UUPS implementation | implementation slot + zero admin/beacon + `proxiableUUID`, S1 high |
| Authority / AccessManager | `0xe167330E2Eac88666de253e9607C6d9ae0cA2824` | Minter and role snapshot, S1 high |
| Current paused status | `false` | direct `paused()` call, S1 high |
| Deny-list contract | `0x2c271ddF484aC0386d216eB7eB9Ff02D4Dc0F6AA` | direct `denyList()` call, S1 high |
| Current supply cap | `750,000,000 apxUSD` | direct `supplyCap()` call, S1 high |
| Current total supply | about `466,229,030.895898820992229055 apxUSD` | direct `totalSupply()` call, S1 high |
| Current remaining cap | about `283,770,969.104101179007770945 apxUSD` | direct `supplyCapRemaining()` call, S1 high |
| CCIP admin | `0xf9862EfC1704aC05e687f66E5cD8c130E5663cE2` | direct `getCCIPAdmin()` call, S1 high |

### 1.2 Token standard and behavior

- `ApxUSD.sol` inherits `ERC20Upgradeable`, `ERC20PermitUpgradeable`, `ERC20PausableUpgradeable`, `ERC20DenyListUpgradable`, `ERC20BurnableUpgradeable`, `AccessManagedUpgradeable`, and `UUPSUpgradeable`. Source: S2 medium/high.
- The source describes key features as supply cap, authorized minting contracts, pausing, deny-list compliance, and UUPS upgradeability. Source: S2 medium/high.
- `ERC20DenyListUpgradable._update` checks both `from` and `to` through the active AddressList before transfers/mints/burns; `ApxUSD._update` composes that hook with pausing. Source: S5/S2 medium/high.
- Official docs describe apxUSD as Apyx's synthetic dollar backed by a basket of preferred shares issued by Digital Asset Treasuries, with eligible whitelisted participants able to mint/redeem through designated pathways and general users able to acquire apxUSD through external liquidity pools. Source: S7 medium.

### 1.3 Asset classification for later agent use

| Dimension | Classification | Evidence / missing behavior |
|---|---|---|
| Asset type | issuer-controlled synthetic-dollar stablecoin backed by offchain preferred-share/DAT exposure | S7 official docs; S2 source comments. Full backing proof remains `review_required`. |
| Token behavior | non-rebasing ERC-20 with supply cap, permit, burnable path, pause and deny-list gates | S1/S2/S5. |
| Mint model | AccessManager-delayed MinterV0 signed-order / rate-limited mint path | S1/S3. |
| Ordinary transferability | ERC-20 transfer path exists but can be paused and deny-listed | S1/S2/S5. |
| Transition-stage asset possibility | apxUSD is the underlying for apyUSD and can be intermediate in redemption/receipt flows | Companion apyUSD research; S7. |

## 4. Contract admin, multisigs, and sensitive actions

### 4.1 Proxy / implementation / upgradeability status

| Field | Finding | Evidence |
|---|---|---|
| Proxy/token address | `0x98A878b1Cd98131B271883B390f68D2c90674665` | S1 high |
| Current implementation | `0xdd71fd677fde2ed2579a3c45204f41a11016ccb4` | S1 high |
| Proxy admin | EIP-1967 admin slot is zero | S1 high |
| Beacon | EIP-1967 beacon slot is zero | S1 high |
| Upgrade pattern | UUPS | implementation `proxiableUUID` returned ERC-1967 slot; S1 high |
| Upgrade authorization | `ApxUSD._authorizeUpgrade` is `restricted` | S2 high |
| Current upgrade executor path | AccessManager role `24`, Safe-like `0xf986...3CE2`, observed delay `259200` seconds / 3 days | S1 high |

### 4.2 Current role holders and holder types

| Role / authority | Current holder(s) | Holder type | Sensitive powers observed in this card | Source / confidence |
|---|---|---|---|---|
| AccessManager `ADMIN_ROLE` / role `0` | `0xabdd8c8ee69e5F5180EB9352AeFFc5CeEAd65e96` | Safe-like contract, 4-of-6 owners | AccessManager admin role; `cleanMintHistory` on MinterV0; likely role/target configuration surface | S1 high for role holder; medium for full admin-surface enumeration |
| Role `2` | `0xf9862EfC1704aC05e687f66E5cD8c130E5663CE2` | Safe-like contract, 3-of-6 owners | `requestMint`, `executeMint` on MinterV0 with zero observed delay | S1 high |
| Role `4` | MinterV0 `0x2c36e1adfaa80ee0324b04cc814f5207bb7ba76e` | contract | token `mint(address,uint256,uint256)` with 4-hour observed delay | S1/S3 high |
| Role `21` | `0xf986...3CE2` | Safe-like 3-of-6 | `pause()` on apxUSD and MinterV0 with zero observed delay | S1 high |
| Role `22` | `0xf986...3CE2` | Safe-like 3-of-6 | `unpause()` with 4-hour observed delay | S1 high |
| Role `23` | `0xf986...3CE2` | Safe-like 3-of-6 | `setSupplyCap`, `setDenyList`, `setMaxMintAmount` with 1-day observed delay | S1 high |
| Role `24` | `0xf986...3CE2` | Safe-like 3-of-6 | `upgradeToAndCall`, `setRateLimit` with 3-day observed delay | S1 high |
| Role `25` | `0xf986...3CE2` | Safe-like 3-of-6 | `setCCIPAdmin`, `setAuthority` with 7-day observed delay | S1 high |
| Role `31` | `0xf986...3CE2` | Safe-like 3-of-6 | `cancelMint` guardian with zero observed delay | S1 high |

Safe-like holder details from S1:

- `0xabdd8c8ee69e5F5180EB9352AeFFc5CeEAd65e96`: `getThreshold()` returned `4`; `getOwners()` returned six owners.
- `0xf9862EfC1704aC05e687f66E5cD8c130E5663CE2`: `getThreshold()` returned `3`; `getOwners()` returned six owners.
- `0x37b0779a66edc491df83e59a56d485835323a555`: Safe-like 3-of-6 observed in candidate set, but not a current callable holder for the sampled apxUSD/minter roles.
- `0x81f5d98ea5acf65640ce8bb68aa8449b7c304c50`: Safe-like 2-of-3 observed in candidate set, but not a current callable holder for the sampled apxUSD/minter roles.

Safe module/guard/fallback-handler state was not exhaustively inspected. `missing_behavior: review_required` before relying on operational Safe policy beyond threshold/owners.

### 4.3 Function-role mapping and delays

| Function | AccessManager role | Current callable holder / delay | Existing-holder relevance | Evidence |
|---|---:|---|---|---|
| `mint(address,uint256,uint256)` | `4` | MinterV0; `14400s` / 4h | direct dilution if minting exceeds backing quality | S1/S3 |
| `setSupplyCap(uint256)` | `23` | Safe-like `0xf986...3CE2`; `86400s` / 1d | future issuance capacity | S1/S2 |
| `setDenyList(address)` | `23` | Safe-like `0xf986...3CE2`; `86400s` / 1d | changes transfer/settlement eligibility registry | S1/S2/S5 |
| `setCCIPAdmin(address)` | `25` | Safe-like `0xf986...3CE2`; `604800s` / 7d | cross-chain/token-admin integration | S1/S2 |
| `pause()` | `21` | Safe-like `0xf986...3CE2`; zero delay | direct transfer/mint/burn block while paused | S1/S2 |
| `unpause()` | `22` | Safe-like `0xf986...3CE2`; `14400s` / 4h | unblocks | S1/S2 |
| `upgradeToAndCall(address,bytes)` | `24` | Safe-like `0xf986...3CE2`; `259200s` / 3d | implementation can change token semantics | S1/S2 |
| `setAuthority(address)` | `25` | Safe-like `0xf986...3CE2`; `604800s` / 7d | replaces AccessManager authority | S1/S2 |
| `requestMint` / `executeMint` | `2` | Safe-like `0xf986...3CE2`; zero delay on minter functions, token mint itself scheduled through AccessManager | mints new apxUSD subject to order/rate limit/delay | S1/S3 |
| `cancelMint` | `31` | Safe-like `0xf986...3CE2`; zero delay | stops pending mint | S1/S3 |
| `setMaxMintAmount` | `23` | Safe-like `0xf986...3CE2`; `86400s` / 1d | changes per-order mint ceiling | S1/S3 |
| `setRateLimit` | `24` | Safe-like `0xf986...3CE2`; `259200s` / 3d | changes rolling mint capacity | S1/S3 |

### 4.4 Sensitive action matrix

| Sensitive action | Current authorized path | Holder type | existing_holder_impact | execution_speed | Evidence / notes |
|---|---|---|---|---|---|
| Pause apxUSD | Role `21` / Safe-like `0xf986...3CE2` | 3-of-6 Safe-like | `direct_freeze` / `direct_redemption_block`-like transfer/mint/burn block while paused | `immediate` | Source composes ERC20Pausable; S1/S2. |
| Unpause apxUSD | Role `22` / Safe-like `0xf986...3CE2` | 3-of-6 Safe-like | `none` / unblocks | `timelocked` / 4h | S1/S2. |
| Replace deny-list | Role `23` / Safe-like `0xf986...3CE2` | 3-of-6 Safe-like | `direct_freeze` / `direct_redemption_block` depending registry contents | `timelocked` / 1d | S1/S2/S5. |
| Mint apxUSD | MinterV0 order flow + token role `4` | contract and Safe-like role holders | `direct_dilution` if not backed; otherwise issuance expansion | `timelocked` / token mint 4h; request/execute zero-delay role observed | Signed order, nonce, max mint and rate limit in MinterV0. S1/S3. |
| Raise/lower supply cap | Role `23` | 3-of-6 Safe-like | `indirect` / changes future issuance capacity | `timelocked` / 1d | S1/S2. |
| Upgrade implementation | Role `24` | 3-of-6 Safe-like | `unknown` | `timelocked` / 3d | UUPS upgrade can change behavior. S1/S2. |
| Rotate AccessManager authority | Role `25` | 3-of-6 Safe-like | `unknown` | `timelocked` / 7d | Replaces core permission manager. S1/S2. |
| Rotate CCIP admin | Role `25` | 3-of-6 Safe-like | `indirect` | `timelocked` / 7d | CCIP admin registration/configuration path. S1/S2. |
| Cancel mint | Role `31` | 3-of-6 Safe-like | `none` / prevents issuance | `immediate` | S1/S3. |
| Burn by ordinary holders | ERC20Burnable path | token holders / allowances | `none` for voluntary holder burn | ordinary ERC-20 action | No special seizure in `ApxUSD.sol`. S2. |
| General forced transfer | none identified in ApxUSD source | n/a | n/a | n/a | Deny-list can block transfers; no USDat-style forced-transfer function identified in `ApxUSD.sol`. S2/S5. |
| Governance vote | none identified | unknown | `unknown` | `unknown` | No DAO governor role holder identified in this card. |

### 4.5 Pending Safe transactions / governance feed caveat

S6 returned unexecuted Safe transactions for `0xabdd...5e96`, including a pending transaction to apxUSD data selector `0x794a40a8` and a large pending multisend setting AccessManager function roles. The bounded recovery did not fully decode every pending payload or determine execution likelihood. Any production action package should refresh Safe Transaction Service and decode pending transactions before relying on this snapshot. `missing_behavior: review_required`.

## Highest-impact unknowns and missing-data behavior for this card

| Unknown / caveat | Why it matters | missing_behavior | Confidence |
|---|---|---|---|
| Full AccessManager admin-operation history and pending Safe payloads were not exhaustively decoded. | Role delays and callable holders can change material controls. | `review_required` | high |
| Human/entity identity and operational policy for Safe-like contracts were not verified from primary Apyx governance docs. | Threshold/owners are known, but policy/process is not. | `review_required` | medium |
| Safe modules/guards/fallback handlers were not checked. | Modules/guards can alter effective execution semantics. | `review_required` before relying on Safe operational policy | medium |
| Deny-list contract administration and current denied accounts were not fully expanded. | Deny-list state can block transfers/mints/burns for existing holders. | `review_required` | high |
| Offchain backing, custody, mint/redeem eligibility, audit scope, liquidity, and oracle methodology are outside this card. | Onchain admin state alone does not prove clean collateral quality. | `review_required` | high |

## Minimal handoff summary

apxUSD at `0x98A878b1Cd98131B271883B390f68D2c90674665` is an ERC-1967/UUPS-upgradeable, 18-decimal synthetic-dollar ERC-20 with supply cap, pause, deny-list, and AccessManager-controlled mint/admin paths. The main operational Safe-like holder for roles 2/21/22/23/24/25/31 is `0xf986...3CE2` (3-of-6); AccessManager admin role is `0xabdd...5e96` (4-of-6). Minting uses MinterV0 signed-order/rate-limit mechanics and a 4-hour token mint delay. Existing-holder controls include immediate pause, timelocked deny-list replacement, timelocked supply-cap/mint parameter changes, timelocked UUPS upgrade, and pending Safe/access-manager change-feed risk.
