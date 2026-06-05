# Saturn sUSDat — issuer/backing/security research

Report date: 2026-06-04 UTC
Analyst: Hermes operator recovery after worker provider-preflight overflow
Task scope: methodology sections 2, 3, and 5 only — issuer/protocol/business model; backing/NAV/exposure; audits/formal verification/incidents.
Input asset: Ethereum mainnet (`chain_id: 1`), `0xd166337499e176bbc38a1fbd113ab144e5bd2df7`, symbol `sUSDat`, intended use unknown.
Output type: objective source-linked facts, not token selection, ranking, suitability verdict, or investment recommendation.

Related evidence:

- `research/eth-mainnet-susdat/onchain-admin.md`
- `research/eth-mainnet-susdat/raw/onchain-admin-snapshot-2026-06-04.json`
- `research/eth-mainnet-susdat/raw/dexscreener-saturn_susdat-2026-06-04.json`

## Source index

| ID | URL / local evidence | source_class | freshness | accessed | confidence | Notes |
|---|---|---:|---:|---:|---:|---|
| S1 | `research/eth-mainnet-susdat/onchain-admin.md` and raw snapshot | onchain | current | 2026-06-04 | high | Direct RPC/source summary for exact sUSDat address, USDat asset, withdrawal queue, roles, STRC oracle, pending timelock operations. |
| S2 | `https://saturncredit.gitbook.io/saturn-docs/solution/susdat-overview` | issuer_docs | current | 2026-06-04 | medium | sUSDat overview: ERC-4626 vault token, USDat underlying, STRC yield, 30-day reward vest, properties. |
| S3 | `https://saturncredit.gitbook.io/saturn-docs/solution/susdat-overview/digital-credit-strategy` | issuer_docs | current | 2026-06-04 | medium | STRC exposure description, monthly dividends, liquidation-preference framing, rate-adjustment model. |
| S4 | `https://saturncredit.gitbook.io/saturn-docs/solution/susdat-overview/susdat-dynamic-reserve` | issuer_docs | current | 2026-06-04 | medium | Dynamic reserve allocation between Treasuries and digital credit based on Strategy LTV. |
| S5 | `https://saturncredit.gitbook.io/saturn-docs/solution/susdat-overview/staking-and-unstaking-process` | issuer_docs | current | 2026-06-04 | medium | Deposit, yield, withdrawal queue, NFT receipt, oracle validation, secondary-market path. |
| S6 | `https://saturncredit.gitbook.io/saturn-docs/operations-and-governance/transparency-and-audits` | issuer_docs | current | 2026-06-04 | medium | Transparency/audit page: USDat onchain capital; sUSDat STRC reserves requiring additional verification; listed audit PDFs. |
| S7 | `https://app.saturn.credit/insights` | issuer_docs | current | 2026-06-04 | medium | App data snapshot: TVL, APY, reserve ratio, sUSDat collateral split. |
| S8 | `research/eth-mainnet-susdat/raw/dexscreener-saturn_susdat-2026-06-04.json` | market_data | current | 2026-06-04 | medium | DEX market data saved only for context; not used as backing proof. |
| S9 | `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/methodology.md` | unknown | current | 2026-06-04 | high | Report labels and missing-data behavior. |

## Agent-context summary

Saturn sUSDat is a non-rebasing ERC-4626-style share token over USDat. Saturn docs state that deposited USDat is used to acquire STRC exposure and that yield from STRC dividends is passed through to sUSDat holders via a rising sUSDat-to-USDat exchange rate, with rewards vesting linearly over 30 days. The backing/NAV path is not pure onchain stablecoin collateral: sUSDat reserves include offchain digital credit holdings (STRC), and Saturn states those require additional verification via Accountable / Chainlink NAV work. Exact sUSDat token admin/queue/oracle controls are covered in the companion onchain/admin artifact; because those controls include processor, compliance, whitelist/freeze, queue, oracle, and pending timelock transitions, issuer/backing conclusions remain `review_required` before treating sUSDat as clean ordinary collateral.

## 2. Issuer / protocol and business model

### Mechanism

Saturn describes sUSDat as its yield-bearing ERC-4626 vault token. Users deposit USDat into the vault and receive sUSDat shares representing proportional ownership of the vault. Saturn uses deposited USDat to acquire STRC, described in the docs as Strategy's preferred equity instrument / digital credit exposure. As STRC yield flows into the vault, the sUSDat-to-USDat exchange rate increases; holders do not need to claim or compound for share value to accrue. Sources: S2 medium, S3 medium, S5 medium, S1 high for exact onchain asset/queue mechanics.

### Business/yield source

- Yield source: Saturn docs state target sUSDat yield is `11%+`, derived from digital credit dividends; at launch, digital-credit exposure is described as `100%` allocated to STRC. Source: S2/S3 medium.
- Reward timing: Saturn docs state rewards vest linearly over 30 days to reduce front-running. Verified onchain/admin snapshot for the exact token observed a current `vestingPeriod=259200` seconds / 3 days, which differs from the docs' 30-day prose; this is a material current-state drift and should be resolved by the onchain value for contract reasoning while retaining docs as issuer-intent/history. Sources: S1 high, S2/S5 medium. `missing_behavior: review_required` for any claim about the live vesting period beyond the snapshot.
- Backing dependencies: sUSDat depends on USDat, STRC, a STRC oracle, withdrawal-queue processing, and issuer/operator activity to convert backing assets and process redemptions. Sources: S1 high, S5 medium.
- Offchain dependencies: Saturn's transparency page states sUSDat reserves include offchain digital credit holdings (STRC) that require additional verification, and that Saturn is working with Accountable and Chainlink on proof-of-reserves/NAV publishing. Source: S6 medium.

### Control and redemption access summary

- Mint/deposit and exit are contract-mediated through sUSDat and its withdrawal queue; standard ERC-4626 `withdraw`/`redeem` are disabled in the onchain/admin source summary and exits use `requestRedeem` / queue NFT flow. Source: S1 high, S5 medium.
- Ordinary holders can request redemption, but the process depends on queue processing, STRC sale/conversion, oracle validation, blacklists/freeze states, and claim execution. Source: S1 high, S5 medium.
- Compliance/admin powers include blacklisting, pause, queue seizure of blacklisted requests/funds, USDat freeze/forced transfer/whitelist mechanics, processor conversions, and pending/default-admin timelock migration. Source: S1 high.

## 3. Backing, NAV, and exposure map

`nav_model: collateralized vault / issuer NAV / offchain-credit exposure`

### Backing model

- Verified exact-token source summary: sUSDat `asset()` is USDat (`0x23238F20B894f29041f48d88Ee91131c395aAA71`). `totalAssets()` is tracked as USDat balance plus vested STRC balance priced through a STRC oracle. Source: S1 high.
- Official docs: USDat deposits are used to acquire STRC; STRC is presented as a Strategy preferred equity / digital credit instrument with monthly dividend mechanics. Source: S2/S3 medium.
- Dynamic reserve: docs describe allocation between Treasuries and digital credit based on Strategy LTV; lower LTV allows higher digital-credit exposure, while higher LTV shifts toward Treasuries. Source: S4 medium.
- Current app snapshot: Saturn insights showed current USDat TVL `$138,566,486`, sUSDat TVL `$96,556,553`, sUSDat APY `15.9%`, USDat reserve ratio `100.01%`, and sUSDat collateral split `USDat: $8,036,628 / 8.3%` and `STRC: $88,519,925 / 91.7%`. Source: S7 medium. Treat as issuer app data, not independent attestation.

### Redemption / NAV caveats

- Primary exit: sUSDat exits through a three-step queue: request, processing, and claim. The request receives an NFT receipt; Saturn's processor sells corresponding STRC on secondary markets to obtain USDat and submits the results onchain; execution price is validated against the onchain oracle. Source: S5 medium; exact queue/roles from S1 high.
- Secondary market: Saturn docs say holders can use secondary markets for immediate liquidity, with pricing/depth-dependent availability. Source: S5 medium.
- NAV can diverge from market price: onchain share accounting, STRC oracle price, queue state, and secondary-market prices are distinct. DEX market data is therefore an exit/liquidity input, not backing proof. Sources: S1 high, S5/S8 medium.
- Collateral-quality exposure: STRC exposure introduces issuer/preferred-equity/dividend/payment/liquidity risk. This card did not independently verify STRC issuer filings, custodial proof, brokerage statements, or bankruptcy/liquidation claims; `missing_behavior: review_required`.

## 5. Audits, formal verification, and incidents

### Security reports located

Saturn's transparency/audits page lists the following downloadable reports but this recovery pass did not download/read every PDF body end-to-end:

- Three Sigma — Audit #1 PDF. Source: S6 medium.
- Certora — Audit #2 PDF. Source: S6 medium.
- Certora — Audit #3 PDF. Source: S6 medium.
- Certora — Formal Verification PDF. Source: S6 medium.

Audit-scope caveat: the existence of the reports is established from the official Saturn docs, but this card did not verify whether the report commit/scope exactly matches the current deployed sUSDat implementation `0x2005E0CA201A37694125fF267aE57872bEa0a0Ce`, the current queue implementation, the current USDat implementation, and the current STRC oracle. Therefore `audited=true` should not be converted into a clean verdict without report-scope matching. `missing_behavior: review_required`.

### Incident / material event signals found in this pass

- Onchain/admin artifact observed no sUSDat pause/unpause events in the scanned range, but did observe two blacklist events and pending timelock operations to revoke immediate EOA default-admin from sUSDat, USDat, STRC oracle, and withdrawal queue. Source: S1 high.
- The same artifact observed multiple sUSDat/queue implementation upgrades before the current implementation. Source: S1 high.
- No confirmed exploit, depeg, reserve shortfall, oracle-failure postmortem, or emergency governance postmortem for the exact sUSDat token was found in the sources used by this card. This is not proof none occurred; it is only the result of this bounded recovery pass. `missing_behavior: review_required` for production risk acceptance.

## Highest-impact unknowns

| Unknown / caveat | Why it matters | missing_behavior | Confidence |
|---|---|---|---|
| Exact audit report scope versus the currently deployed implementations was not matched. | Security report existence is not enough if deployed bytecode changed after scope. | `review_required` | high |
| Independent STRC custody/valuation/reserve verification was not completed. | sUSDat backing depends heavily on STRC/offchain digital credit exposure. | `review_required` | high |
| Docs say 30-day reward vest; onchain snapshot says 3-day vest. | Current NAV accrual/front-running assumptions differ materially. | `review_required` | high |
| Accountable/Chainlink proof-of-reserves/NAV feed details were not independently read. | Saturn itself says sUSDat reserves require additional verification. | `review_required` | high |
| Full USDat underlying issuer/legal/freeze/whitelist policy was not expanded in this card. | USDat is the sUSDat asset and affects entries/exits. | `review_required` | medium |
| No public incident found in bounded sources. | Absence of evidence is not an incident-history clean bill. | `continue` for explanation, `review_required` for acceptance | medium |

## Minimal handoff

sUSDat's useful framing is: issuer-controlled ERC-4626-style USDat share token whose NAV/exits depend on USDat, STRC exposure, a STRC oracle, and queue processing. Current source-backed facts support continuing dossier synthesis, but not a clean collateral-quality conclusion: backing proof, STRC exposure, audit-scope match, and live admin/timelock state all need explicit review in any final decision path.
