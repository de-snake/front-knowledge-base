# apyx apyUSD — issuer/backing/security research

Report date: 2026-06-04 UTC
Analyst: Hermes operator recovery after worker provider-preflight overflow
Task scope: methodology sections 2, 3, and 5 only — issuer/protocol/business model; backing/NAV/exposure; audits/formal verification/incidents.
Input asset: Ethereum mainnet (`chain_id: 1`), `0x38eeb52f0771140d10c4e9a9a72349a329fe8a6a`, symbol `apyUSD`, intended use unknown.
Output type: objective source-linked facts, not token selection, ranking, suitability verdict, or investment recommendation.

Related evidence:

- `research/eth-mainnet-apyusd/onchain-admin.md`
- `research/eth-mainnet-apyusd/raw/onchain-admin-snapshot-2026-06-04.json`
- `research/eth-mainnet-apyusd/raw/onchain-market-snapshot-2026-06-04.json`

## Source index

| ID | URL / local evidence | source_class | freshness | accessed | confidence | Notes |
|---|---|---:|---:|---:|---:|---|
| S1 | `research/eth-mainnet-apyusd/onchain-admin.md` and raw snapshots | onchain | current | 2026-06-04 | high | Exact token identity, implementation, AccessManager, role holders, pause/deny-list/current totalAssets and totalSupply. |
| S2 | `https://docs.apyx.fi/product-overview/apyusd-overview` | issuer_docs | current | 2026-06-04 | medium | apyUSD mechanism, non-rebasing ERC-4626 vault, apxUSD underlying, redemption/cooldown/flexible redemption. |
| S3 | `https://docs.apyx.fi/product-overview/apxusd-overview` | issuer_docs | current | 2026-06-04 | medium | apxUSD context as underlying stablecoin / protocol asset. |
| S4 | `https://docs.apyx.fi/collateral-and-custody/transparency` | issuer_docs | current | 2026-06-04 | medium | Accountable dashboard, Apyx dashboard, Dune dashboard, Wolf & Company monthly custodian attestations. |
| S5 | `https://docs.apyx.fi/collateral-and-custody/third-party-attestation` | issuer_docs | current | 2026-06-04 | medium | Wolf & Company March/April 2026 attestation links. |
| S6 | `https://docs.apyx.fi/resources/audits` | issuer_docs | current | 2026-06-04 | medium | Official audit page listing Quantstamp, Certora, Zellic reports. |
| S7 | `https://www.certora.com/reports/apyx-apxusd` | audit | dated | 2026-06-04 | medium | Certora final report summary page for Apyx apxUSD/apyUSD protocol. |
| S8 | `https://github.com/apyx-labs/evm-contracts` | onchain / issuer_docs | current | 2026-06-04 | medium | Public Apyx EVM contracts source used with onchain/Etherscan verified source checks. |
| S9 | `https://tidresearch.com/reports/apyusd/` | risk_assessment | current | 2026-06-04 | low | Independent secondary risk report; useful for hints only, not relied on as primary proof. |
| S10 | `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/methodology.md` | unknown | current | 2026-06-04 | high | Report labels and missing-data behavior. |

## Agent-context summary

apyUSD is Apyx's non-rebasing ERC-4626-style savings wrapper over apxUSD. Official docs state that users deposit apxUSD into a permissionless vault and receive apyUSD shares; yield accrues through a rising exchange rate and derives from Apyx's underlying collateral/dividend stack. This makes apyUSD a vault share over an issuer-controlled underlying, not an ordinary immutable ERC-20. Apyx publishes transparency and monthly attestation links, and official docs list Quantstamp, Certora, and Zellic audits; however, this recovery pass did not match every report scope to the current deployed implementation. Backing/attestation/audit evidence is sufficient for dossier synthesis, but `review_required` before clean acceptance or automated execution.

## 2. Issuer / protocol and business model

### Mechanism

Apyx docs describe apyUSD as the savings token for apxUSD, built using the ERC-4626 vault standard. Users deposit apxUSD into a permissionless vault and receive apyUSD; balances do not rebase. Yield accrues through a gradually increasing exchange rate, so each apyUSD can redeem for more apxUSD over time if the system is operating normally. Sources: S2 medium, S1 high for exact contract state.

### Yield / revenue source

- Official docs state apyUSD yield is generated from the protocol's underlying collateral stack and describe the yield source as dividends. Source: S2 medium.
- Certora's public report summary describes Apyx apxUSD as backed by offchain preferred shares that generate dividend yields and describes apyUSD as a yield-bearing ERC-4626 vault wrapper whose yield is distributed through a vesting mechanism. Source: S7 medium.
- Apyx transparency docs state the Accountable dashboard gives near-real-time visibility into assets backing apxUSD, including supply, reserves, and collateral coverage; they also mention dashboards for capital deployment/reserve position and onchain data. Source: S4 medium.

### Dependencies and controls

- Offchain dependencies: apyUSD inherits apxUSD backing/custody/dividend assumptions, plus any Accountable/custodian attestation process and offchain collateral-management process. Sources: S4/S5 medium.
- Contract dependencies: live apyUSD uses AccessManager `0xe167330E2Eac88666de253E9607C6d9Ae0cA2824`, deny-list contract `0x2c271d...F6AA`, Unlock Receipt `0x9bf51F...3237`, vesting `0x0D62...C99f`, fee wallet, and CCIP admin. Source: S1 high.
- Direct redemption: official docs describe redemption as asynchronous. The canonical model is request → cooldown (~20 days) → claim; flexible redemption issues an onchain Unlock Receipt NFT and can become claimable after 3 days with a declining early-redemption fee. Source: S2 medium. Exact live receipt contract/admin was only partially covered; `missing_behavior: review_required`.
- Eligibility: docs state access is permissionless with no KYB/KYC requirement, but users in certain jurisdictions are prevented from using the Apyx frontend. Source: S2 medium.

## 3. Backing, NAV, and exposure map

`nav_model: collateralized vault / issuer NAV / dividend-backed underlying`

### Current exact-token values

- Onchain snapshot: apyUSD `asset()` is apxUSD `0x98A878b1Cd98131B271883B390f68D2c90674665`; `totalAssets()` returned `233786308355629929225483777`; `totalSupply()` returned `170104409453165089753438983`; `paused=false`. Source: S1 high.
- The share value is not a fixed $1 value; it is an apxUSD-per-apyUSD vault share exchange rate. Sources: S1 high, S2 medium.

### Backing chain

- Immediate underlying: apyUSD holders are exposed first to apxUSD redemption and value. Source: S1/S2.
- Ultimate backing: official docs and Certora summary point to Apyx's underlying collateral stack / offchain preferred-share dividend process rather than a simple onchain USDC-only reserve. Sources: S2/S4/S7 medium.
- Attestations: Apyx docs list monthly Wolf & Company attestation opinions for March and April 2026 and state that custodians provide monthly attestations validating backing assets exist, remain under custody control, and are valued appropriately. Sources: S4/S5 medium.
- Dashboard transparency: Apyx states Accountable provides independent near-real-time reserve/collateral visibility. This card did not independently validate Accountable's data model or reconcile dashboard values to onchain totals. Source: S4 medium. `missing_behavior: review_required`.

### Exposure caveats

- apyUSD NAV can diverge from secondary market price because vault exchange rate, apxUSD redemption path, receipt/cooldown state, and DEX liquidity are separate mechanisms. Source: S2 medium, S1 high.
- apyUSD redemptions are asynchronous; claim timing and fee path can affect practical exit value. Source: S2 medium.
- The underlying apxUSD issuer/backing, custodian, attestation scope, and offchain preferred-share exposure are material and not fully exhausted in this exact-token card. `missing_behavior: review_required`.

## 5. Audits, formal verification, and incidents

### Security reports located

Official Apyx docs list these security reports:

- Quantstamp — 2026-02. Source: S6 medium.
- Quantstamp — 2026-04. Source: S6 medium.
- Certora — 2026-03. Source: S6 medium.
- Zellic — 2026-03. Source: S6 medium.

Certora's public report summary says its March 2, 2026 manual code review identified 11 issues, including one high-severity issue, and states that the high-severity issue was fixed and confirmed. Source: S7 medium.

Audit-scope caveat: this pass did not download/read every audit PDF body end-to-end and did not map each report's commit/scope to the current apyUSD implementation `0xfd616567eCc1607F61073951A1e822f7315bb112`, AccessManager roles, Unlock Receipt, apxUSD, and backing/custody process. `missing_behavior: review_required` before treating the audits as a clean verdict.

### Incident signals found in bounded pass

- No confirmed public exploit/depeg/freeze/redemption-delay postmortem for the exact apyUSD token was identified in the bounded sources used here. This is not proof of no incident. `missing_behavior: continue` for explanation, `review_required` before acceptance.
- The onchain/admin artifact identifies the upgradeability and sensitive controls that would be relevant to incident monitoring: pause, deny-list replacement, receipt rotation, vesting/fee-wallet changes, UUPS upgrades, AccessManager admin, and role-0 burn-with-assets functions. Source: S1 high.

## Highest-impact unknowns

| Unknown / caveat | Why it matters | missing_behavior | Confidence |
|---|---|---|---|
| Audit PDF scope was not matched to current deployed bytecode and related contracts. | Audit existence is not a deployed-system security guarantee. | `review_required` | high |
| Accountable / custodian attestation values were not independently reconciled against apxUSD/apyUSD onchain totals. | apyUSD inherits offchain backing/custody assumptions. | `review_required` | high |
| Full underlying apxUSD issuer/backing/redemption controls were not expanded here. | apyUSD's immediate underlying is apxUSD. | `review_required` | high |
| Unlock Receipt contract admin/claim mechanics were not fully expanded in this issuer card. | Practical redemption depends on receipt and cooldown/fee mechanics. | `review_required` | medium |
| No incident was found, but incident search was bounded. | Absence of evidence is not a clean incident history. | `continue` / `review_required` for production acceptance | medium |

## Minimal handoff

Use apyUSD as an issuer-controlled, upgradeable ERC-4626 savings-wrapper over apxUSD with dividend-backed/offchain-collateral dependencies. Primary sources support the basic mechanism, attestation/audit existence, and current onchain identity/admin state, but final dossier synthesis must carry forward review-required unknowns around audit scope, Accountable/custodian reconciliation, apxUSD backing, and receipt/redemption mechanics.
