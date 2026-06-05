# Centrifuge deSPXA — issuer/backing/security research

Report date: 2026-06-04 UTC
Analyst: Hermes operator recovery after worker timeout
Task scope: methodology sections 2, 3, and 5 only — issuer/protocol/business model; backing/NAV/exposure; audits/formal verification/incidents.
Input asset: Base (`chain_id: 8453`), `0x9c5C365e764829876243d0b289733B9D2b729685`, symbol `deSPXA`, intended use unknown.
Output type: objective source-linked facts, not token selection, ranking, suitability verdict, or investment recommendation.

Related evidence:

- `research/base-despxa/transfer-liquidity-oracle-governance.md`
- `research/base-despxa/raw/blockscout-read-contract-summary.json`
- `research/base-despxa/raw/sources/src__core__spoke__ShareToken.sol`
- `research/base-despxa/raw/sources/src__vaults__AsyncVault.sol`
- `research/base-despxa/raw/sources/blockscout-hook-FreelyTransferable.sol`

## Source index

| ID | URL / local evidence | source_class | freshness | accessed | confidence | Notes |
|---|---|---:|---:|---:|---:|---|
| S1 | `research/base-despxa/raw/blockscout-read-contract-summary.json` and verified local source extracts | onchain | current | 2026-06-04 | high | Exact deSPXA token/vault/hook/manager state and verified source snippets. |
| S2 | `https://centrifuge.io/blog/despxa-on-base` | issuer_docs | current | 2026-06-04 | medium | Centrifuge launch post: deSPXA, SPXA exposure, Janus Henderson, S&P DJI license, non-US AP mint/redeem, DeFi venues. |
| S3 | `https://centrifuge.io/blog/centrifuge-q1-2026-recap` | issuer_docs | current | 2026-06-04 | medium | Centrifuge recap: deSPXA freely transferable wrapper of SPXA; V3.1 deployed, V3.2 in audit, Chronicle primary oracle partner. |
| S4 | `https://press.spglobal.com/2025-07-01-S-P-Dow-Jones-Indices-Collaborates-with-Centrifuge-to-Bring-the-S-P-500-Index-Onchain,-Expanding-Access-to-the-Worlds-Most-Widely-Recognized-Benchmark` | issuer_docs | dated | 2026-06-04 | medium | S&P DJI press release: S&P 500 licensing collaboration with Centrifuge, Anemoy Capital, Janus Henderson. |
| S5 | `https://app.rwa.xyz/assets/SPXA` | market_data / risk_assessment | current | 2026-06-04 | low | Secondary RWA.xyz asset page: SPXA total asset value, NAV, investor eligibility, primary-market fields. Not a primary issuer proof. |
| S6 | `https://forum.moonwell.fi/t/proposal-to-add-despxa-market-to-moonwell-on-base/2163` | governance | current | 2026-06-04 | low | Moonwell proposal submitted by Centrifuge team; useful for deSPXA/SPXA structure and retail/AP path hints, not primary legal source. |
| S7 | `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/methodology.md` | unknown | current | 2026-06-04 | high | Report labels and missing-data behavior. |

## Agent-context summary

deSPXA is Centrifuge's freely transferable Base-native DeFi wrapper/debt instrument linked to SPXA, the Janus Henderson Anemoy S&P 500 Index Fund. Official Centrifuge materials describe SPXA as exposure to the Anemoy S&P 500 Index Fund, built under license from S&P Dow Jones Indices and managed by Janus Henderson, and deSPXA as the DeFi-distribution asset on Base. Primary creation/redemption at NAV is described for non-US Authorized Participants, while ordinary DeFi holders should be modeled as secondary-market holders unless eligibility is verified. Backing/NAV is therefore issuer/fund/manager/oracle dependent; not an ordinary stablecoin or cash-equivalent ERC-20.

## 2. Issuer / protocol and business model

### Mechanism

Centrifuge's launch post states deSPXA gives non-US users tokenized exposure to the Anemoy S&P 500 Index Fund (SPXA), built under license from S&P Dow Jones Indices and managed by Janus Henderson, live on Base. deSPXA is intended to make the exposure tradeable and usable across DeFi venues such as Morpho, Euler, Aerodrome, Definitive, Multipli, Steakhouse, and Clearstar. Source: S2 medium.

Centrifuge's Q1 2026 recap describes deSPXA as the freely transferable wrapper of the Janus Henderson Anemoy S&P 500 Index Fund (SPXA), built under license from S&P Dow Jones Indices and managed by Janus Henderson. Source: S3 medium.

### Parties / issuer dependencies

- Tokenization/distribution infrastructure: Centrifuge V3 / Centrifuge Labs ecosystem. Sources: S2/S3 medium; exact onchain V3 token/vault state S1 high.
- Underlying fund context: S&P DJI press release says S&P DJI collaborated with Centrifuge; Anemoy Capital was licensed by S&P DJI, with Janus Henderson as sub-advisor for the Janus Henderson Anemoy S&P 500 Index Fund Segregated Portfolio, planned subject to regulatory approval. Source: S4 medium.
- Fund manager/exposure: Centrifuge materials state managed by Janus Henderson; RWA.xyz describes the strategy as passively managed and led by Janus Henderson Investors UK and Anemoy Capital. Sources: S2/S5.
- Compliance/eligibility: official launch says deSPXA can be minted/redeemed at NAV by non-US Authorized Participants; Moonwell proposal says deSPXA is redeemable into USDC only by KYC'd participants and retail holders interact through secondary markets. Sources: S2 medium, S6 low.

### Business / value source

- deSPXA's value source is exposure to SPXA / S&P 500 index fund NAV, not protocol revenue. Source: S2/S4/S5.
- It is a tokenized equity-index exposure with DeFi distribution and secondary-market liquidity, not a dividend-yield stablecoin. Income treatment for the underlying fund was not established from primary fund docs in this recovery pass. `missing_behavior: review_required`.

## 3. Backing, NAV, and exposure map

`nav_model: issuer NAV / tokenized fund wrapper / async vault`

### Current exact-token state

From S1 onchain/blockscout snapshot:

- Token name: `DeFi Janus Henderson Anemoy S&P500® Fund Token`.
- Symbol: `deSPXA`; decimals `18`.
- Total supply raw: `4236891729691416512194`.
- Linked vault: `0x2dA40F061536c2f3a8f95f23a5f4c133d07D393a` (`AsyncVault`).
- Vault asset: Base USDC `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`.
- `pricePerShare = 763973338`, i.e. about `763.973338` USDC per share using USDC 6 decimals.
- `priceLastUpdated = 1780401600`.
- `totalAssets = 3236872318793` raw USDC units.

### Backing chain

- Immediate vault accounting uses Base USDC as asset for the AsyncVault and deSPXA as the share token. Source: S1 high.
- Economic exposure is linked to SPXA, which official Centrifuge and S&P materials describe as an S&P 500 index fund exposure licensed by S&P DJI and managed/sub-advised by Janus Henderson / Anemoy. Sources: S2/S3/S4.
- RWA.xyz secondary data described SPXA as a passively managed strategy and showed total asset value `$3,357,954`, NAV `$1.14`, management fee `0.50%`, eligible investor category `Non-U.S. Accredited Investor`, base assets USDC, daily subscription/redemption, and minimum investment `500,000 USDC`. Source: S5 low. Treat as third-party market/risk data, not legal documentation.

### NAV caveats

- Contract price-per-share and market price are separate. The transfer/liquidity companion artifact saved DEX prices around `$752.59-$754.14`, while vault price-per-share was about `$763.97`. This point-in-time difference is evidence that NAV and market exit value can diverge. Sources: S1 high, companion S6 market data medium.
- Primary mint/redeem at NAV is not assumed for ordinary holders. Official text limits NAV mint/redeem to non-US Authorized Participants; Moonwell proposal says retail holders interact through secondary markets. Sources: S2 medium, S6 low.
- Fund-level holdings, replication method, cash buffers, custodian/service providers, and audited financial statements were not obtained from primary fund documents in this pass. `missing_behavior: review_required`.

## 5. Audits, formal verification, and incidents

### Security/audit signals located

- Centrifuge Q1 recap says V3.1 was deployed across ten chains and V3.2 was currently in audit. Source: S3 medium. This is not an audit report for the exact deployed deSPXA token/vault/hook.
- The exact token/vault/hook sources were verified through Blockscout/Sourcify-style local raw evidence in S1/S2/S3/S4 of the companion transfer artifact, but source verification is not equivalent to security audit.
- No public final audit report URL mapping to the exact deSPXA token, `AsyncVault`, `FreelyTransferable` hook, root/manager configuration, and current Base deployment was located in this bounded recovery pass. `missing_behavior: review_required`.

### Incidents / material events found in bounded pass

- No confirmed exploit, NAV break, freeze incident, redemption delay, oracle failure, or emergency governance postmortem for exact deSPXA was identified in the bounded sources used by this card. This is not proof none occurred. `missing_behavior: continue` for explanation, `review_required` before acceptance.
- Known material risk surfaces from companion transfer artifact: member/AP eligibility, freeze state, hook replacement, manager/root/ward changes, Chronicle/manager price updates, and DEX liquidity divergence. Source: companion S1-S6.

## Highest-impact unknowns

| Unknown / caveat | Why it matters | missing_behavior | Confidence |
|---|---|---|---|
| Exact legal issuer/fund documents and service providers were not fully retrieved. | SPXA/deSPXA exposure is fund/legal-entity dependent. | `review_required` | high |
| Exact audit report scope for current deployed deSPXA/Centrifuge V3 components was not located. | Verified source is not audit coverage. | `review_required` | high |
| Holder-specific AP/member/KYC eligibility was not established. | Primary NAV redemption may be unavailable to ordinary DeFi holders. | `review_required`; `block_automation` for redemption | high |
| Fund holdings/replication/custody/audited financial statements were not independently validated. | NAV/backing quality depends on fund operations and custody. | `review_required` | high |
| No incident found in bounded search. | Absence of evidence is not a clean incident history. | `continue` / `review_required` for acceptance | medium |

## Minimal handoff

Use deSPXA as a tokenized-fund / issuer-NAV exposure: a freely transferable Base token linked to SPXA, with primary NAV mint/redeem reserved for eligible non-US/AP/KYC'd participants and ordinary DeFi exit mainly through secondary markets unless eligibility is confirmed. Current source is enough for synthesis, but legal fund docs, audit scope, AP eligibility, custody/holdings, and incident history remain review-required.
