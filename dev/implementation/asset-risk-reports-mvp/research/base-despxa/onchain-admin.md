# Centrifuge deSPXA — onchain/admin research

Report date: 2026-06-04 UTC
Analyst: Hermes operator recovery after worker protocol crashes
Task scope: methodology sections 1 and 4 only — identity/token semantics and contract admin/multisigs/sensitive actions.
Input asset: Base (`chain_id: 8453`), `0x9c5C365e764829876243d0b289733B9D2b729685`, symbol `deSPXA`, intended use unknown.
Output type: objective source-linked facts, not token selection, ranking, suitability verdict, or investment recommendation.

Raw evidence:

- `research/base-despxa/raw/blockscout-read-contract-summary.json`
- `research/base-despxa/raw/blockscout-smart-contract-token.json`
- `research/base-despxa/raw/root-logs-blockscout-2026-06-04.json`
- `research/base-despxa/raw/root-ward-state-2026-06-04.txt`
- `research/base-despxa/raw/sources/src__core__spoke__ShareToken.sol`
- `research/base-despxa/raw/sources/src__vaults__AsyncVault.sol`
- `research/base-despxa/raw/sources/src__vaults__BaseVaults.sol`
- `research/base-despxa/raw/sources/blockscout-hook-FreelyTransferable.sol`
- `research/base-despxa/raw/sources/blockscout-root-Root.sol`
- `research/base-despxa/raw/sources/blockscout-manager-AsyncRequestManager.sol`

## Source index

| ID | URL / local evidence | source_class | freshness | accessed | confidence | Notes |
|---|---|---:|---:|---:|---:|---|
| S1 | Base Blockscout/RPC summary: `raw/blockscout-read-contract-summary.json` | onchain | current | 2026-06-04 | high | Exact token/vault/hook/root/manager reads and address metadata. |
| S2 | `raw/sources/src__core__spoke__ShareToken.sol` | onchain | current | 2026-06-04 | high | Verified token source: ERC20, hook, ERC1404, admin `file`, `updateVault`, `authTransferFrom`. |
| S3 | `raw/sources/src__vaults__AsyncVault.sol` and `src__vaults__BaseVaults.sol` | onchain | current | 2026-06-04 | high | Verified vault source: ERC-7540 async deposit/redeem and admin manager setters. |
| S4 | `raw/sources/blockscout-hook-FreelyTransferable.sol` | onchain | current | 2026-06-04 | high | Verified hook source: ordinary non-frozen transfers allowed; deposit/redeem paths require member state. |
| S5 | `raw/sources/blockscout-root-Root.sol` and `src__misc__Auth.sol` | onchain | current | 2026-06-04 | high | Verified admin/auth model: `wards`, Root delay, pause, endorsements, `relyContract`/`denyContract`. |
| S6 | `raw/sources/blockscout-manager-AsyncRequestManager.sol` | onchain | current | 2026-06-04 | high | Verified manager source: request/claim/callback functions and `file` setters gated by `auth`. |
| S7 | `raw/root-logs-blockscout-2026-06-04.json` | onchain | current | 2026-06-04 | medium | Blockscout Root event scan and derived current Root ward state. |
| S8 | `https://centrifuge.io/blog/despxa-on-base` | issuer_docs | current | 2026-06-04 | medium | Product context: deSPXA, non-US AP mint/redeem, Chainlink/LayerZero/Keyrock/Chronicle references. |
| S9 | `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/methodology.md` | unknown | current | 2026-06-04 | high | Report labels and missing-data behavior. |

## Concise facts summary

- deSPXA is a verified Base ERC-20 / ERC-1404-style Centrifuge `ShareToken`, not a proxy, at `0x9c5C365e764829876243d0b289733B9D2b729685`.
- The token returns name `DeFi Janus Henderson Anemoy S&P500® Fund Token`, symbol `deSPXA`, decimals `18`, and totalSupply raw `4236891729691416512194` in the raw read snapshot.
- Linked vault for Base USDC is `AsyncVault` `0x2dA40F061536c2f3a8f95f23a5f4c133d07D393a`; vault asset is Base USDC `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`; vault share is the deSPXA token.
- Current hook is verified `FreelyTransferable` at `0x2a9B9C14851Baf7AD19f26607C9171CA1E7a1A61`. It allows ordinary transfers for non-frozen accounts but requires membership for deposit/redeem request and claim paths.
- Admin is Centrifuge-style `Auth` / `wards`, not OpenZeppelin AccessControl. No proxy admin, UUPS upgrader, Safe, or DAO governor was identified for the exact token/vault/hook in the inspected sources; however Root and warded contracts can still change key behavior.
- Root `0x7Ed48C31f2fdC40d37407cBaBf0870B2b688368f` is a ward on token, vault, manager, and hook. Root delay read as `172800` seconds / 2 days and `paused=false`; Root source says pausing can happen instantaneously, while adding new Root wards uses a delay.
- Derived current Root wards from Blockscout event scan are four unverified contracts: `0xCEb7eD5d5B3bAD3088f6A1697738B60d829635c6`, `0x1E70530e9555711f8DF4838Ab940b97c039B4037`, `0xf837a22883e004f705E0D7e1deE08e295Df30B27`, and `0x97cc7e9Dafdd725Cc23B25eeBC93c4384B4Fe30A`. Their identities/thresholds were not resolved in this pass; `missing_behavior: review_required`.

## 1. Identity and token semantics

### Canonical identity

| Field | Value | Evidence |
|---|---|---|
| Chain | Base | Input scope + S1 high |
| chain_id | `8453` | S1 high |
| Token address | `0x9c5C365e764829876243d0b289733B9D2b729685` | Input + S1 high |
| Verified contract name | `ShareToken` | S1/S2 high |
| Proxy status | Not a proxy in Blockscout metadata; no implementations list | S1 high |
| `name()` | `DeFi Janus Henderson Anemoy S&P500® Fund Token` | S1 high |
| `symbol()` | `deSPXA` | S1 high |
| `decimals()` | `18` | S1/S2 high |
| Total supply raw | `4236891729691416512194` | S1 high |
| Token standard/behavior | ERC-20 plus ERC-1404 transfer restriction checks via external hook | S2 high |
| Transfer hook | `0x2a9B9C14851Baf7AD19f26607C9171CA1E7a1A61` (`FreelyTransferable`) | S1/S4 high |
| Linked vault for Base USDC | `0x2dA40F061536c2f3a8f95f23a5f4c133d07D393a` | S1 high |
| Vault asset | Base USDC `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` | S1/S3 high |
| Root | `0x7Ed48C31f2fdC40d37407cBaBf0870B2b688368f` | S1/S5 high |
| Async manager | `0xF48256AbDDf96EcDDc4B3DbD23E8C1921f9761Ae` | S1/S6 high |

### Token/vault semantics

- `ShareToken` is an ERC-20 with balances extended by hook data and an external transfer hook. `transfer`, `transferFrom`, `mint`, and `burn` call `_onTransfer`; `detectTransferRestriction` delegates to the hook. Source: S2 high.
- `authTransferFrom(sender, from, to, value)` is admin-gated by `auth` and performs `_transferFrom` followed by hook `onERC20AuthTransfer` if set. Source: S2 high. This is an administrative forced-transfer surface if a ward is granted.
- `updateVault(asset, vault_)` is admin-gated and can update the share token's asset→vault mapping. Source: S2 high.
- `file("hook", address)` is admin-gated and can replace the transfer hook. Source: S2 high.
- The linked vault is an ERC-7540-style `AsyncVault`: deposit and redemption are request/claim flows rather than synchronous ERC-4626 previewed flows; preview functions revert by design. Source: S3 high.
- Official Centrifuge context: deSPXA is the DeFi distribution token for SPXA/S&P 500 exposure; non-US Authorized Participants can mint/redeem at NAV. Source: S8 medium.

## 4. Contract admin, multisigs, and sensitive actions

### Admin architecture

| Contract | Address | Proxy / upgrade status | Current direct ward(s) observed | Key admin surfaces | Evidence |
|---|---|---|---|---|---|
| ShareToken | `0x9c5C...9685` | non-proxy verified contract | Root only among checked relevant addresses | `file(hook)`, `file(name/symbol)`, `updateVault`, `authTransferFrom`, `mint`, `burn`, `setHookData` | S1/S2 high |
| AsyncVault | `0x2dA4...393a` | non-proxy verified contract | Root and manager among checked relevant addresses | `file(manager)`, `file(asyncRedeemManager)`, endorsed operator, request/claim events | S1/S3 high |
| FreelyTransferable hook | `0x2a9B...1A61` | non-proxy verified contract | Root (by root ward-state check) | freeze/member behavior inherited from hook stack; exact full base hook source not fully present | S4/S5/S7 medium-high |
| Root | `0x7Ed4...368f` | non-proxy verified contract | four active unverified contracts derived from logs | pause/unpause, delay, endorse/veto, schedule/execute Root wards, rely/deny wards on child contracts | S5/S7 high/medium |
| AsyncRequestManager | `0xF482...61Ae` | non-proxy verified contract | Root | `file(spoke)`, `file(balanceSheet)`, callbacks/trusted calls/claim paths gated by `auth` | S1/S6 high |

Root state:

- `delay() = 172800` seconds / 2 days.
- `paused() = false`.
- Root source: `pause()` / `unpause()` are `auth` and immediate; `scheduleRely(target)` schedules a new Root ward after `delay`; `executeScheduledRely(target)` grants Root ward after the schedule is ready; `relyContract(target,user)` and `denyContract(target,user)` can change ward state on contracts where Root is a ward. Sources: S5/S7 high-medium.

Current Root ward holders from derived event state (all unverified contracts, holder type = contract unknown):

- `0xCEb7eD5d5B3bAD3088f6A1697738B60d829635c6`
- `0x1E70530e9555711f8DF4838Ab940b97c039B4037`
- `0xf837a22883e004f705E0D7e1deE08e295Df30B27`
- `0x97cc7e9Dafdd725Cc23B25eeBC93c4384B4Fe30A`

No Safe threshold/owner data was resolved for these contracts; Gnosis Safe `VERSION()` / `getThreshold()` probes did not return data in this pass. `missing_behavior: review_required`.

### Sensitive action matrix

| Action / function | Authorized surface | Current holder type | existing_holder_impact | execution_speed | Evidence / notes |
|---|---|---|---|---|---|
| Replace transfer hook via `ShareToken.file("hook", address)` | ShareToken ward; Root can grant child wards | Root-controlled contracts | `direct_freeze` / `unknown` | immediate for current child ward; root-ward addition timelocked 2d | Hook controls transfer restrictions. S2/S5/S7. |
| `authTransferFrom` forced transfer | ShareToken ward | Root-controlled contracts if granted or existing ward | `direct_transfer` | immediate for current token ward path | Admin-gated forced transfer surface exists in source. S2. |
| Admin `mint` / `burn` ShareToken | ShareToken ward | Root-controlled contracts if granted or existing ward | `direct_dilution` / `direct_transfer` | immediate for ward | `mint` and `burn` are inherited/admin-gated in ShareToken. S2. Current business flow normally mints/burns through vault/manager. |
| `updateVault(asset,vault)` | ShareToken ward | Root-controlled contracts | `indirect` / `direct_redemption_block` | immediate for ward | Changes vault mapping used by share token integrations. S2. |
| Set hook data for user | ShareToken ward or hook | Root/hook-controlled contracts | `direct_freeze` / `indirect` | immediate | Hook data influences transfer/member/freeze checks. S2/S4. |
| Freeze/member changes in hook | Hook admin/root-controlled surfaces | Root-controlled contracts | `direct_freeze` / `direct_redemption_block` | immediate for current hook ward | FreelyTransferable explicitly supports freezing and member-gated requests. S4. Full base hook source not fully expanded. |
| Change vault manager / async redeem manager | AsyncVault ward | Root and manager | `direct_redemption_block` / `unknown` | immediate for ward | Manager controls request/claim accounting and conversions. S3/S6. |
| Root `pause()` | Root active ward contracts | unverified contracts | `direct_redemption_block` / `unknown` | immediate | Root source says pausing can happen instantaneously; downstream effect on exact token/vault paths not fully traced. S5. |
| Root `relyContract` / `denyContract` | Root active ward contracts | unverified contracts | `unknown` | immediate | Can add/remove wards on child contracts where Root is a ward. S5. |
| Root `scheduleRely` / `executeScheduledRely` | Root active ward contracts | unverified contracts | `unknown` | timelocked 2 days for new Root ward | Root `delay=172800`. S5/S7. |
| Root `file("delay")` | Root active ward contracts | unverified contracts | `indirect` | immediate | Can change delay up to 4 weeks. S5. |
| Endorse/veto trusted operators | Root active ward contracts | unverified contracts | `indirect` / possible request-path effects | immediate | Endorsed users can bypass token restrictions and set ERC-7540 operators. S3/S5. |
| Upgrade implementation | none found | n/a | none identified | n/a | Token, vault, hook, root, manager are non-proxy in inspected Blockscout metadata. S1. |
| Safe multisig / timelock owner | not identified | unknown contracts | unknown | unknown | Root active ward contracts are unverified and not identified as Safe through simple probes. S7. |

### Recent/current admin event notes

- Token/vault deployment observed in Blockscout metadata around 2026-03-16. Source: S1 high.
- Root event scan observed many historical `Rely`, `Deny`, `RelyContract`, and `DenyContract` events, including recent Root ward schedule/rely/deny activity around 2026-06-01 to 2026-06-04. Source: S7 medium.
- The raw event-derived Root ward state has four active unverified contracts. Because these are contracts, not named entities, and thresholds/signers are unresolved, `missing_behavior: review_required` before assuming governance safety or execution delay beyond Root's explicit 2-day new-ward delay.

## Highest-impact unknowns and missing-data behavior

| Unknown / caveat | Why it matters | missing_behavior | Confidence |
|---|---|---|---|
| Root active ward contracts are unverified and not mapped to named governance/thresholds. | They appear to control Root and therefore child contract admin surfaces. | `review_required` | high |
| Full inherited BaseTransferHook source was not fully recovered. | Exact freeze/member setter surfaces and event names need full confirmation. | `review_required` | medium |
| Full current member/frozen address set was not enumerated. | Transfers/request flows can differ per holder. | `review_required` | high |
| No Safe owner/threshold was found for Root wards. | Multisig/timelock assumptions cannot be made. | `review_required` | high |
| No proxy upgrade path was found, but Root can still grant wards and replace hook/manager. | Non-proxy does not imply immutable behavior. | `continue` with admin-risk warnings | high |

## Minimal handoff

For agent reasoning, deSPXA is a verified non-proxy Centrifuge share token with mutable Auth/Root-controlled admin surfaces. Treat ordinary token identity as high-confidence, but treat admin safety as review-required: Root active ward contracts are unverified/unnamed, and Root/child ward paths can change transfer hook, manager, vault mapping, forced transfer, mint/burn, freeze/member behavior, and request processing.
