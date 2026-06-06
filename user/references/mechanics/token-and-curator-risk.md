# Token and curator risk mechanics

Stable explanatory rubrics for per-token risk profiles and curator trust / discipline. Use these mechanics to interpret prepared evidence; use workflows for new evidence production.

## Drill — Per-token 3-layer risk profile (Steakhouse)

Reference: [Steakhouse Layers, Pillars and Criteria](https://www.steakhouse.financial/docs/risk-management/collateral/layers-pillars-and-criteria). Aggregation rule of thumb: worst-of across layers; best-of within the Issuer pillar; worst-of within the Operational pillar.

**Source boundary.** This is an external risk rubric, not a Gearbox protocol object. Use it to structure product diligence and explain why a token/curator feels safer or riskier; do not present the score as protocol-proven unless the underlying data feed exists.

- **Asset layer** — three pillars:
  - **Issuer**
    - Social = regulatory status, identity, track record.
    - Decentralisation = governance distribution, top-10 holder %, quorum, dual-governance / guardian mechanisms.
    - Technical = contract immutability, parameter-modification authority, discretionary admin functions.
  - **Credit Risk** — where the agent looks for backing solvency; varies by token class:
    - Issuer attestations (cadence, completeness), reserve-composition reports, recovery rates from prior loss events.
    - Rating agencies' reports (Credora, [Steakhouse](https://www.steakhouse.financial/docs/markets/readme/morpho-v1), etc.).
  - **Operational**
    - Lindy = years operational + TVL.
    - Audits = count, top-tier-firm coverage, code-coverage %, bug-bounty $ tier.
    - Economic Transparency = on-chain observability of `totalAssets` / reserves / NAV.
- **Market layer** — pillars:
  - **Oracle** — covered separately in [[oracle-and-liquidity-risk#Drill — Oracle types and LP risk shapes|Oracle types and LP risk shapes]].
  - **Liquidity** — primary redemption, secondary DEX depth, slippage at relevant trade sizes.
  - **Price Fluctuation** — collateral / loan-asset volatility (annualised realised 30/90d), correlation, depegging history.
  - **LLTV + Credit Enhancement** — LLTV step bonus rule (max 94.5% per Steakhouse): Adjusted Asset Rating shifts up where LLTV calibration provides margin.
- **Platform layer** — for tokens issued via a custodian / compliance overlay (e.g., Securitize-issued RWAs):
  - **Issuer** of the platform itself (separate from the asset issuer).
  - **Operational** capacity of the platform (whitelist management, freeze/unfreeze mechanics, redemption windows).

## Drill — Curator identity & governance

**Source boundary.** Curator-profile rows combine protocol-visible permissions with external due diligence. Contract permissions say what can be changed; identity, operating record, governance quality, and communication reliability come from curated/indexed sources.

- **Identity & legitimacy** — registered entity, doxxed team, social presence, regulatory status (where applicable). One strong dimension can carry the pillar.
- **Decentralisation of authority** — governance mechanism (single-EOA / multisig n-of-m / DAO), top-N signer concentration, dual-governance / guardian mechanisms protecting depositors.
- **Technical surface** — what parameters the curator can change unilaterally vs gated (timelock / DAO vote), upgradeability of curator contracts, presence of admin functions.

## Drill — Curator operational track record

- **Lindy** — first operation date, total months operational, incident-free duration.
- **Process maturity** — published process docs, peer review of parameter changes, post-mortem culture for any incidents.
- **Economic transparency** — `cumulativeBadDebtUsd`, `totalAumUsd`, individual `badDebtIncidents[]` with resolution notes. Does the curator publish their own analyses or stay opaque?

## Drill — Curator liquidity-incident history

- `Curator.liquidityIncidents[]` — pools / events where capital was frozen / withdraw-throttled even without a credit loss (stuck-borrower events, withdraw-queue activations, prolonged utilisation pinning). Distinct from `badDebtIncidents[]` because paper-solvent-but-unusable counts as a curator failure even without a loss.

## Drill — Curator design discipline

- **Oracle methodology fit per dominant token** — for each Q2-flagged dominant collateral, does the curator's chosen oracle type align with the token's market structure? Market oracle on a thin altcoin with no PSM = poor fit; NAV oracle on a stablecoin without redemption depth = poor fit. Curator competence shows up as type-token alignment.
- **3-layer rating rigor** — does the curator publish per-pillar grades, evidence behind them, and update cadence? Or just a top-line letter?
- **Liquidity-management discipline** — quota sizes proportional to the token's observable depth (PSM + DEX); collateral-whitelist excludes single-venue-concentrated tokens; LLTV calibration compensates for any notice-period delays; documented atomic-swap requirements for accepted collateral.
