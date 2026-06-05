# apyx apyUSD — onchain/admin research

Report date: 2026-06-04 UTC
Analyst: Hermes operator recovery after Kanban worker provider-preflight overflow
Task scope: MVP mining pipeline sections 1 and 4 only — identity/token semantics and contract admin/multisigs/sensitive actions.
Input asset: Ethereum mainnet (`chain_id: 1`), `0x38EEb52F0771140d10c4E9A9a72349A329Fe8a6A`, symbol `apyUSD`, intended use unknown.
Output type: objective source-linked facts, not token selection, ranking, suitability, suitability verdict, or investment recommendation.

Raw evidence produced for this card:

- `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/eth-mainnet-apyusd/raw/onchain-admin-snapshot-2026-06-04.json`
- `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/eth-mainnet-apyusd/raw/onchain-market-snapshot-2026-06-04.json`

## Source index

| ID | URL / local evidence | source_class | freshness | accessed | confidence | Notes |
|---|---|---:|---:|---:|---:|---|
| S1 | `https://ethereum-rpc.publicnode.com` plus raw snapshot `research/eth-mainnet-apyusd/raw/onchain-admin-snapshot-2026-06-04.json` | onchain | current | 2026-06-04 | high | Direct Ethereum mainnet RPC calls at block `25243724` for apyUSD, its AccessManager, and Safe-compatible role holder. |
| S2 | `https://etherscan.io/address/0x38EEb52F0771140d10c4E9A9a72349A329Fe8a6A` | onchain | current | 2026-06-04 | high | Etherscan contract/token page; shows Apyx apyUSD token and verified proxy/source with implementation `0xfD616567...7315bB112`. |
| S3 | `https://app.dedaub.com/ethereum/address/0x38eeb52f0771140d10c4e9a9a72349a329fe8a6a` | onchain | current | 2026-06-04 | medium | Secondary contract explorer corroborating EIP-1967 proxy with logic address and ERC-20 metadata. |
| S4 | `https://github.com/apyx-labs/evm-contracts` | issuer_docs | current | 2026-06-04 | medium | Public Apyx EVM contracts repository; local clone/extract used for `src/ApyUSD.sol`, `src/exts/ERC20DenyListUpgradable.sol`, and role/source context. Current GitHub listing showed latest commit `89ff20e...` from 2026-04-28. |
| S5 | `https://docs.apyx.fi/product-overview/apyusd-overview` | issuer_docs | current | 2026-06-04 | medium | Official apyUSD docs: ERC-4626 savings token for apxUSD, non-rebasing exchange-rate accrual, permissionless vault access, flexible redemption / Unlock Receipt description. |
| S6 | `https://docs.apyx.fi/product-overview/apxusd-overview` | issuer_docs | current | 2026-06-04 | medium | Official apxUSD docs: apxUSD mechanism and collateral/redemption context for the apyUSD underlying asset. |
| S7 | `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/methodology.md` | unknown | current | 2026-06-04 | high | Methodology labels and missing-data behavior used by this artifact. |

## Concise facts summary

- `apyUSD` is deployed on Ethereum mainnet at `0x38EEb52F0771140d10c4E9A9a72349A329Fe8a6A`; direct RPC returns `name="apyUSD"`, `symbol="apyUSD"`, `decimals=18`, `paused=false`. Sources: S1 high, S2 high.
- The token is an ERC-20 / ERC-20Permit / ERC-4626-style non-rebasing vault share over `asset() = 0x98A878b1Cd98131B271883B390f68D2c90674665` (`apxUSD`). Official docs describe apyUSD as the savings token for apxUSD; users deposit apxUSD into a permissionless vault and receive apyUSD, with yield accruing through the exchange rate rather than rebasing balances. Sources: S1 high, S4 medium, S5 medium.
- The contract is an ERC-1967 proxy with a UUPS implementation: implementation slot points to `0xfd616567eCc1607F61073951A1e822f7315bb112`, EIP-1967 admin slot is zero, and the implementation returns the standard UUPS `proxiableUUID`. Sources: S1 high, S2 high, S3 medium.
- The live authority is OpenZeppelin-style AccessManager `0xe167330E2Eac88666de253E9607C6d9Ae0cA2824`. The AccessManager has `target_admin_delay_apyUSD=259200` seconds / 3 days, `expiration=604800` seconds / 7 days, and `minSetback=432000` seconds / 5 days. Source: S1 high.
- Non-admin operational roles for apyUSD functions are held by Safe-compatible contract `0xf9862EfC1704aC05e687f66E5cD8c130E5663CE2`, whose `getThreshold()` returns `3` and `getOwners()` returns 6 owners. Source: S1 high.
- The AccessManager `ADMIN_ROLE` (`role=0`) is held by EOA `0xabdd8c8ee69e5F5180EB9352AeFFc5CeEAd65e96` in the sampled state. This EOA is not the direct callable holder for most token config functions, but AccessManager admin authority is a material control surface because it can change access configuration. Source: S1 high.
- Sensitive direct controls include pause, unpause, deny-list replacement, unlock-receipt rotation, vesting contract rotation, vault unlocking-fee and fee-wallet changes, UUPS upgrade, CCIP admin rotation, and restricted burn-with-assets functions. Sources: S1 high, S4 medium.

## 1. Identity and token semantics

### 1.1 Canonical identity

| Field | Value | Evidence |
|---|---|---|
| Chain | Ethereum mainnet, `chain_id: 1` | Input scope; S1 high. |
| Token/proxy address | `0x38EEb52F0771140d10c4E9A9a72349A329Fe8a6A` | Input scope; direct code/state snapshot S1 high; Etherscan token/contract page S2 high. |
| Name | `apyUSD` | Direct `name()` call, S1 high. |
| Symbol | `apyUSD` | Direct `symbol()` call, S1 high. |
| Decimals | `18` | Direct `decimals()` call, S1 high. |
| Current implementation | `0xfd616567eCc1607F61073951A1e822f7315bb112` | EIP-1967 implementation slot, S1 high; Etherscan implementation link S2 high. |
| Proxy type | ERC-1967 proxy with UUPS implementation | EIP-1967 implementation slot nonzero, admin slot zero, implementation `proxiableUUID()` returns ERC-1967 implementation slot, S1 high; Dedaub proxy classification S3 medium. |
| Authority / access manager | `0xe167330E2Eac88666de253E9607C6d9Ae0cA2824` | Direct `authority()` call, S1 high. |
| Current paused status | `false` | Direct `paused()` call, S1 high. |
| Underlying asset | `0x98A878b1Cd98131B271883B390f68D2c90674665` (`apxUSD`) | Direct `asset()` call, S1 high; official apyUSD docs S5 medium. |
| Deny-list contract | `0x2c271ddF484aC0386d216eB7eB9Ff02D4Dc0F6AA` | Direct `denyList()` call, S1 high. |
| Unlock receipt contract | `0x9bf51F33955EC70f87C4b5C49441815589043237` | Direct `receipt()` call, S1 high. |
| Vesting contract | `0x0D62B4cC02b4B51Ed19DDF41D7a7979CF394C99f` | Direct `vesting()` call, S1 high. |
| Vault-side unlocking fee | `1000000000000000` = `0.001e18` / 10 bps | Direct `unlockingFee()` call, S1 high; source max-fee constant and comments S4 medium. |
| Fee wallet | `0x6F93635F2A1C19b4F7f1BD9BA655F6A073C629Dc` | Direct `feeWallet()` call, S1 high. |
| CCIP admin | `0xf9862EfC1704aC05e687f66E5cD8c130E5663CE2` | Direct `getCCIPAdmin()` call, S1 high. |
| Snapshot `totalAssets()` | `233786308355629929225483777` raw apxUSD units | Direct RPC at block `25243724`, S1 high. |
| Snapshot `totalSupply()` | `170104409453165089753438983` raw apyUSD units | Direct RPC at block `25243724`, S1 high. |

RPC freshness note: current values above were checked against Ethereum public RPC at block `25243724` on 2026-06-04. A raw replay/evidence snapshot is stored at `research/eth-mainnet-apyusd/raw/onchain-admin-snapshot-2026-06-04.json`.

### 1.2 Token standard and behavior

- Verified source / public repo source for `ApyUSD` imports and inherits `ERC20Upgradeable`, `ERC20PermitUpgradeable`, `ERC20PausableUpgradeable`, `ERC20DenyListUpgradable`, `AccessManagedUpgradeable`, `UUPSUpgradeable`, `ReentrancyGuardTransient`, and `ERC4626Upgradeable`. This makes apyUSD an upgradeable ERC-4626 vault-share token with ERC-20 / permit transfer surface rather than a fixed-balance ordinary ERC-20. Sources: S2 high, S4 medium.
- Official docs describe apyUSD as the savings token for apxUSD, built using ERC-4626. Users deposit apxUSD into a permissionless vault and receive apyUSD; token balances do not rebase, and yield accrues through an increasing exchange rate. Source: S5 medium.
- Source comments describe withdrawals/redeems as deliberately deviating from immediate ERC-4626 exits: `withdraw` / `redeem` charge a vault-side upfront fee, then mint an `UnlockReceipt` NFT to the owner/receiver for the post-fee assets; the receipt later supports `claim` or `cancel`. Sources: S4 medium, S5 medium.
- Official docs describe flexible redemptions: new redemptions receive an on-chain Unlock Receipt NFT; redemptions become claimable after 3 days with an early-redemption fee declining from 3.5% to 0.1%. Source: S5 medium.
- The source enforces deny-list checks on both sender and receiver through `ERC20DenyListUpgradable._update`; `_deposit` adds deny-list checks on caller and receiver, and `_withdraw` checks caller, receiver, and owner. Sources: S1 high for current deny-list address, S4 medium for source behavior.
- The source includes `pause()` / `unpause()` and uses `ERC20PausableUpgradeable`, so a pause affects ERC-20 transfer/update paths and vault entry/exit operations. Sources: S1 high for current `paused=false`; S4 medium for source behavior.

### 1.3 Asset classification for later agent use

| Dimension | Classification | Evidence / missing behavior |
|---|---|---|
| Asset type | issuer-controlled synthetic-dollar savings/vault share over apxUSD | S5/S6 medium for official mechanism; S1/S4 for vault mechanics. Full issuer/backing analysis is outside this card and remains `review_required` before treating as ordinary liquid collateral. |
| Token behavior | non-rebasing ERC-4626 share token with asynchronous receipt-based redemption path | S4/S5. |
| Ordinary ERC-20 transferability | Transfer path exists but is pause- and deny-list-sensitive | S4 source behavior and S1 current deny-list/paused state. |
| Transition-stage asset possibility | apyUSD itself is a share token, but exits can produce an Unlock Receipt NFT / pending claim state | S4/S5. For execution or liquidation reasoning, receipt/claim state belongs to section 6 and is `review_required` outside this card. |

## 4. Contract admin, multisigs, and sensitive actions

### 4.1 Proxy / implementation / upgradeability status

| Field | Finding | Evidence |
|---|---|---|
| Proxy / token address | `0x38EEb52F0771140d10c4E9A9a72349A329Fe8a6A` | S1 high, S2 high. |
| Current implementation | `0xfd616567eCc1607F61073951A1e822f7315bb112` | EIP-1967 implementation slot, S1 high. |
| Proxy admin | EIP-1967 admin slot is zero | S1 high. |
| Beacon | no beacon slot evidence used in this card | S1 high for proxy/admin slots; beacon not separately relied on. |
| Upgrade pattern | UUPS: implementation `proxiableUUID()` returned `0x360894a13...d382bbc`, the ERC-1967 implementation slot | S1 high. |
| Upgrade authorization | `_authorizeUpgrade(address)` is `restricted`; live AccessManager maps `upgradeToAndCall(address,bytes)` to role `24` | S1 high for role mapping; S4 medium for source `restricted` modifier. |
| Current upgrade executor path | Safe-compatible role holder `0xf9862E...3CE2` has role `24` with `259200` seconds / 3-day execution delay for `upgradeToAndCall` | S1 high. |

### 4.2 Current role holders and holder types

#### AccessManager and role holders

| Role / authority | Current holder(s) | Holder type | Sensitive powers observed in this card | Source / confidence |
|---|---|---|---|---|
| AccessManager `ADMIN_ROLE` / role `0` | `0xabdd8c8ee69e5F5180EB9352AeFFc5CeEAd65e96` | EOA | AccessManager administration; in the sampled token function map can directly call `burnWithAssets` / `burnWithAssetsFrom` because those selectors are assigned role `0`; likely can alter role/target configuration through AccessManager admin functions. | S1 high for role access; medium for broader AccessManager admin semantics not exhaustively enumerated here. |
| Role `21` | `0xf9862EfC1704aC05e687f66E5cD8c130E5663CE2` | Safe-compatible contract, 3-of-6 | `pause()`, `setUnlockReceipt(address)` with zero delay | S1 high. |
| Role `22` | `0xf9862EfC1704aC05e687f66E5cD8c130E5663CE2` | Safe-compatible contract, 3-of-6 | `unpause()` with 14,400 second / 4-hour delay | S1 high. |
| Role `23` | `0xf9862EfC1704aC05e687f66E5cD8c130E5663CE2` | Safe-compatible contract, 3-of-6 | `setDenyList(address)` and `setUnlockingFee(uint256)` with 86,400 second / 1-day delay | S1 high. |
| Role `24` | `0xf9862EfC1704aC05e687f66E5cD8c130E5663CE2` | Safe-compatible contract, 3-of-6 | `setVesting(address)`, `setFeeWallet(address)`, `upgradeToAndCall(address,bytes)` with 259,200 second / 3-day delay | S1 high. |
| Role `25` | `0xf9862EfC1704aC05e687f66E5cD8c130E5663CE2` | Safe-compatible contract, 3-of-6 | `setCCIPAdmin(address)` with 604,800 second / 7-day delay | S1 high. |

Safe-compatible role holder details for `0xf9862EfC1704aC05e687f66E5cD8c130E5663CE2`:

- `getThreshold()` returned `3`.
- `getOwners()` returned 6 owners: `0xb51F89DEA7Df709cEbb4809B40c6431361e61d0d`, `0x5db416BcFc1a8b5b921f55C1E078d1F39194e99F`, `0xD6bB3f9718D4f30ed2851c713275dEf7529D1411`, `0xcFCF3C9Ed3d97DB54c99BDd197E59952a0973f6e`, `0xB98cD8C868cf00cEA934977dBE4AC090E808fb87`, `0xd66a0Fc924fAb7476D35aFe5941856ef76BA0839`.
- The contract responded to Safe-like `getThreshold` / `getOwners`; module/guard/pending-transaction state was not exhaustively checked in this card.

Source: S1 high for returned threshold/owners; missing module/guard check has `missing_behavior: continue` for this section, `review_required` before relying on full Safe operational policy.

### 4.3 Function-role mapping and delays

| Function | Selector | AccessManager role | Current callable holder / delay | Existing-holder relevance | Evidence |
|---|---:|---:|---|---|---|
| `pause()` | `0x8456cb59` | `21` | Safe-compatible `0xf986...3CE2`; `canCall=true`, delay `0` | Can block transfer/vault flows while paused | S1 high. |
| `unpause()` | `0x3f4ba83a` | `22` | Safe-compatible `0xf986...3CE2`; delay `14,400s` | Unblocks after pause | S1 high. |
| `setDenyList(address)` | `0x0de2731d` | `23` | Safe-compatible `0xf986...3CE2`; delay `86,400s` | Can replace deny-list contract used by transfer/deposit/withdraw checks | S1 high. |
| `setUnlockingFee(uint256)` | `0xd2bcb953` | `23` | Safe-compatible `0xf986...3CE2`; delay `86,400s` | Changes future withdrawal/redeem fee; source caps fee at 1% | S1 high, S4 medium. |
| `setUnlockReceipt(address)` | `0x6e182040` | `21` | Safe-compatible `0xf986...3CE2`; `canCall=true`, delay `0` | Rotates receipt contract for new exits; old receipts remain governed by old contract per source comments | S1 high, S4 medium. |
| `setVesting(address)` | `0x6f6ff3bc` | `24` | Safe-compatible `0xf986...3CE2`; delay `259,200s` | Changes vesting/yield source used in `totalAssets()` | S1 high, S4 medium. |
| `setFeeWallet(address)` | `0x90d49b9d` | `24` | Safe-compatible `0xf986...3CE2`; delay `259,200s` | Redirects upfront vault fee; affects future withdrawals/redeems | S1 high, S4 medium. |
| `upgradeToAndCall(address,bytes)` | `0x4f1ef286` | `24` | Safe-compatible `0xf986...3CE2`; delay `259,200s` | Implementation upgrade can change token/admin behavior | S1 high. |
| `setCCIPAdmin(address)` | `0xa8fa343c` | `25` | Safe-compatible `0xf986...3CE2`; delay `604,800s` | Rotates Chainlink CCIP token-admin registration authority; no ordinary ERC-20 balance effect identified by this card | S1 high, S4 medium. |
| `burnWithAssets(uint256)` | `0xaf2657aa` | `0` | EOA `0xabdd...5e96`; delay `0` | Restricted burn of caller-owned shares and backing apxUSD; no forced burn without allowance identified in source | S1 high, S4 medium. |
| `burnWithAssetsFrom(address,uint256)` | `0x794a40a8` | `0` | EOA `0xabdd...5e96`; delay `0` | Burns an account's shares plus backing only if allowance is spent when `account != spender`; not a unilateral forced-transfer in the inspected source | S1 high, S4 medium. |

### 4.4 Sensitive action matrix

Methodology labels used:
`existing_holder_impact: none | indirect | direct_freeze | direct_transfer | direct_dilution | direct_redemption_block | unknown`
`execution_speed: immediate | timelocked | governance_vote | unknown`

Execution-speed note: AccessManager returns a delay for many functions. This report classifies zero-delay Safe-compatible execution as `immediate`; nonzero AccessManager delays as `timelocked` because the AccessManager enforces a schedule/wait/execute flow. Safe threshold signing is separate from the AccessManager delay.

| Sensitive action | Current authorized path | Holder type | existing_holder_impact | execution_speed | Evidence / notes |
|---|---|---|---|---|---|
| Pause apyUSD | Role `21` / Safe-compatible `0xf986...3CE2` | 3-of-6 Safe-compatible contract | `direct_redemption_block` and `direct_freeze`-like transfer block while paused | `immediate` | Source uses `ERC20PausableUpgradeable`; role delay 0. S1/S4. |
| Unpause apyUSD | Role `22` / Safe-compatible `0xf986...3CE2` | 3-of-6 Safe-compatible contract | `none` / unblocks | `timelocked` / 4 hours | S1. |
| Replace deny-list contract | Role `23` / Safe-compatible `0xf986...3CE2` | 3-of-6 Safe-compatible contract | `direct_freeze` / `direct_redemption_block` depending deny-list contents | `timelocked` / 1 day | Deny-list checks sender/receiver/caller/owner on transfer/deposit/withdraw flows. S1/S4. |
| Rotate unlock receipt | Role `21` / Safe-compatible `0xf986...3CE2` | 3-of-6 Safe-compatible contract | `direct_redemption_block` or `unknown` for new exits if misconfigured; old receipts remain separate | `immediate` | Source says new receipt is required before withdraw/redeem succeeds and old receipts remain claimable through old contract. S1/S4. |
| Set vault unlocking fee | Role `23` / Safe-compatible `0xf986...3CE2` | 3-of-6 Safe-compatible contract | `indirect` for future exits; fee is non-refundable in source comments | `timelocked` / 1 day | Current fee 10 bps; source caps at 1%. S1/S4. |
| Set fee wallet | Role `24` / Safe-compatible `0xf986...3CE2` | 3-of-6 Safe-compatible contract | `indirect` for future exit-fee routing | `timelocked` / 3 days | S1/S4. |
| Set vesting contract | Role `24` / Safe-compatible `0xf986...3CE2` | 3-of-6 Safe-compatible contract | `indirect`; can affect `totalAssets()` / yield accounting path | `timelocked` / 3 days | `totalAssets()` includes vested yield from vesting. S1/S4. |
| Upgrade implementation | Role `24` / Safe-compatible `0xf986...3CE2` | 3-of-6 Safe-compatible contract | `unknown` | `timelocked` / 3 days | Implementation upgrade can change semantics. S1/S4. |
| Set CCIP admin | Role `25` / Safe-compatible `0xf986...3CE2` | 3-of-6 Safe-compatible contract | `indirect` / cross-chain admin path only in this card | `timelocked` / 7 days | Source comments say CCIP admin can register/configure token pool and has no other special powers in the token contract. S1/S4. |
| AccessManager role/target reconfiguration | AccessManager `ADMIN_ROLE` / EOA `0xabdd...5e96` | EOA | `unknown` to `direct_*` depending reconfiguration | `immediate` unless AccessManager itself imposes delay not checked here | Role 0 holder verified in S1. Full AccessManager admin-operation history was not exhaustively reconstructed; `missing_behavior: review_required`. |
| Restricted burn with assets | AccessManager role `0` / EOA `0xabdd...5e96` | EOA | `none` to `indirect` if caller burns own/allowanced shares; no unilateral holder seizure identified | `immediate` | Source requires allowance when burning from another account and burns backing apxUSD proportionally. S1/S4. |
| Direct minter role | none identified on apyUSD contract | n/a | n/a | n/a | apyUSD shares mint via ERC-4626 deposit/mint flows; no separate arbitrary mint role identified in inspected source. S4. |
| Direct blacklister role on token | no direct add/remove function on apyUSD; token points to external deny-list contract | deny-list admin outside this card | `direct_freeze` possible through deny-list state | `unknown` for deny-list contract administration | This card checked `denyList()` address and token behavior, not the deny-list contract's full admin surface. S1/S4. |
| Oracle reporter role | none identified in apyUSD token | n/a | n/a | n/a | apyUSD uses ERC-4626/share accounting over apxUSD and vesting; dedicated oracle reporter role not found in token source. S4. |
| Rescue role | none identified on apyUSD token | n/a | n/a | n/a | No general rescue function was identified in inspected `ApyUSD.sol`; fee and vesting setters exist. S4. |
| Governance vote | none identified | unknown | `unknown` | `unknown` | No DAO governor was identified as a current role holder in this card. |

### 4.5 Current state values relevant to admin monitoring

- `paused=false` at block `25243724`. Source: S1 high.
- `denyList=0x2c271ddF484aC0386d216eB7eB9Ff02D4Dc0F6AA`. Source: S1 high.
- `receipt=0x9bf51F33955EC70f87C4b5C49441815589043237`. Source: S1 high.
- `vesting=0x0D62B4cC02b4B51Ed19DDF41D7a7979CF394C99f`. Source: S1 high.
- `unlockingFee=1000000000000000` raw, i.e. 10 bps using the source's `FEE_PRECISION=1e18`. Source: S1 high, S4 medium.
- `feeWallet=0x6F93635F2A1C19b4F7f1BD9BA655F6A073C629Dc`. Source: S1 high.
- `AccessManager.target_admin_delay_apyUSD=259200` seconds / 3 days. Source: S1 high.

## Highest-impact unknowns and missing-data behavior for this card

| Unknown / caveat | Why it matters | missing_behavior | Confidence |
|---|---|---|---|
| Full AccessManager admin-operation history and all role/target configuration changes were not reconstructed. | Role `0` EOA can materially affect the admin surface if it can reconfigure roles/delays/targets. | `review_required` | medium |
| Human/entity identity and operational policy for EOA `0xabdd8c8ee69e5F5180EB9352AeFFc5CeEAd65e96` were not verified from a primary Apyx governance document. | It is the AccessManager admin role holder and has immediate role-0 token-call authority in this snapshot. | `review_required` | medium |
| Safe module/guard/fallback-handler state for `0xf9862E...3CE2` was not exhaustively checked; only Safe-like threshold/owners were read. | Modules/guards can affect execution semantics beyond owner threshold. | `review_required` before relying on Safe operational policy | medium |
| Administration of the external deny-list contract `0x2c271d...F6AA` was not fully expanded in this card. | Deny-list state can block transfers/deposits/withdrawals for existing holders. | `review_required` | medium |
| Unlock Receipt contract admin and outstanding receipt state were not fully expanded in this sections 1/4 artifact. | Exit claims depend on receipt contract behavior and fee curve; exact receipt controls belong to section 6 and a broader admin pass. | `review_required` | medium |
| Underlying apxUSD admin, mint/redeem eligibility, backing, reserve, and legal/issuer controls are outside this card. | apyUSD is a vault over apxUSD; underlying admin and redemption controls can affect practical exit value. | `review_required` | high |
| Audit, formal verification, incident history, liquidity, and oracle/market-pricing methodology are outside this card. | This artifact does not prove audit coverage, clean incident history, secondary-market liquidity, or oracle suitability. | `review_required` | high |

## Minimal handoff summary

- apyUSD at `0x38EEb52F0771140d10c4E9A9a72349A329Fe8a6A` is an Ethereum mainnet ERC-1967/UUPS-upgradeable, non-rebasing ERC-4626-style vault share over apxUSD, not an immutable ordinary ERC-20.
- Current implementation is `0xfd616567eCc1607F61073951A1e822f7315bb112`; the proxy admin slot is zero and the implementation exposes the UUPS `proxiableUUID`.
- The token's live AccessManager is `0xe167330E2Eac88666de253E9607C6d9Ae0cA2824`. Role-controlled token functions are split between a Safe-compatible 3-of-6 contract `0xf9862EfC1704aC05e687f66E5cD8c130E5663CE2` and AccessManager admin EOA `0xabdd8c8ee69e5F5180EB9352AeFFc5CeEAd65e96`.
- Direct current-holder intervention surfaces exist: pause can immediately block transfer/vault flows; deny-list replacement is delayed 1 day; receipt rotation is immediate; vesting/fee-wallet/upgrade actions are delayed 3 days; CCIP admin rotation is delayed 7 days; AccessManager admin role state remains a high-impact review item.
- This card does not clear underlying apxUSD issuer/backing/legal/redemption, deny-list-contract admin, receipt-contract admin, audit/incident, liquidity, or oracle/pricing questions; those stay `review_required` for downstream synthesis.
