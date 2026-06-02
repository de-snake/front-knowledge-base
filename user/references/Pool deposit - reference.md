# Pool deposit — reference

Drill sections referenced from [[Pool deposit]] table rows. Each drill is the deeper material for a row whose default-scope cell only carries the verdict-level summary. Drills are flow-agnostic where possible so future flow docs (e.g., Credit Account opening, monitoring) can link to the same anchors.

## Drill — Oracle types and LP risk shapes

The LP carries a different failure mode depending on the oracle's category, even when the feed is working:

- **Market price** (Chainlink real-time feeds, Pyth, on-chain TWAPs) → **liquidity-cascade risk.** Liquidations fire on time, but in thin markets or gapping conditions, forced sales can execute below collateral value (bad debt), and the cascade itself spikes pool utilisation — throttling LP withdrawals exactly when they want out.
- **NAV / fundamental** (`ERC4626.convertToAssets`, NAV attestations on staking derivatives or tokenised funds) → **liquidity-trap risk.** Sustained depegs may be invisible to the feed: borrowers over-borrow at a stale valuation, liquidations don't fire, and bad debt accumulates behind un-liquidatable positions that lock LP capital.
- **Hardcoded** (e.g., 1 USDT = 1 USDC fixed) → same trap as NAV with no surfacing mechanism for a depeg at all.
- **Hybrid / MetaOracle** — composite feeds (e.g., `cp0xLRT/wstETH * wstETH/stETH * stETH/USD`) inherit risk shapes of all underlying components; failure mode dominates by the weakest link.

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
  - **Oracle** — covered separately in [[#Drill — Oracle types and LP risk shapes]].
  - **Liquidity** — primary redemption, secondary DEX depth, slippage at relevant trade sizes.
  - **Price Fluctuation** — collateral / loan-asset volatility (annualised realised 30/90d), correlation, depegging history.
  - **LLTV + Credit Enhancement** — LLTV step bonus rule (max 94.5% per Steakhouse): Adjusted Asset Rating shifts up where LLTV calibration provides margin.
- **Platform layer** — for tokens issued via a custodian / compliance overlay (e.g., Securitize-issued RWAs):
  - **Issuer** of the platform itself (separate from the asset issuer).
  - **Operational** capacity of the platform (whitelist management, freeze/unfreeze mechanics, redemption windows).

## Drill — Collateral-induced liquidity risk by oracle type

**Why utilisation spikes — the underlying mechanics.** A successful liquidation by itself *reduces* U: debt is repaid, cash returns to the pool. The cascade-induced spike is a second-order effect with two compounding mechanisms:

1. **Withdrawal-vs-repayment race.** With `U = Borrowed / (Cash + Borrowed)`, an LP withdrawal of $X reduces `Cash` and `TVL` by X (`Borrowed` unchanged) → U *rises*. A liquidation-repayment of $Y reduces `Borrowed` by Y and adds Y to `Cash` → U *falls*. During a cascade, LPs see the event and withdraw immediately; liquidators are bottlenecked by thin DEX depth. The race favours the withdrawal side, so U trends up while the cascade is in flight.
2. **Stuck-debt pinning.** Liquidations that can't clear at all (slippage > liquidation premium → no liquidator wants the trade) leave the position open. `Borrowed` doesn't fall as expected; the self-cleaning property of liquidations stops working. Even without an LP run, U doesn't naturally retrace.

**Two oracle-driven failure shapes:**

- **Market oracle + thin liquidity = liquidation-cascade risk.** Forced sales execute below collateral value, generating bad debt. Mechanically, U spikes during the cascade because LP withdrawal pressure outpaces liquidator repayments — the cash side of the pool empties faster than the debt side. Without the LP-run leg, repayments would *reduce* U; the cascade signature is specifically the withdrawal-vs-repayment race. Historical anchor: stETH June 2022 (Aave WETH market).
- **NAV / hardcoded oracle + persistent depeg = liquidity-trap risk.** Oracle stays silent, liquidations don't fire, un-liquidatable positions inflate utilisation indefinitely. No cascade required — the trap forms quietly. Historical anchor: Aave-CRV Nov 2022 (Eisenberg's CRV short couldn't be liquidated cleanly at all; debt stayed put and U pinned high without an LP run needed).

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

## Drill — IC decision palette

**Source boundary.** This is a product allocation rubric, not a Gearbox protocol object. Protocol state can say which candidates are possible; the IC rubric decides whether to fund one, split, skip, or hold reserve.

The Investment Committee chooses among these palette items per allocation pass; the chosen palette item determines how the per-candidate `AllocationDecision` rows + the top-level `reserve_usd` are filled:

- **Fund one candidate fully** — pick the strongest memo and deploy all available capital there. `decisions[i].action = "deposit"` for the chosen candidate; all others `"skip"`. `reserve_usd = 0`.
- **Split across multiple candidates (diversification)** — distribute available capital across several memos. Multiple `decisions[i].action = "deposit"` with positive `amount_usd`. Total deployed ≤ available capital.
- **Skip individual candidates** — a candidate that's fine in isolation but redundant given existing positions, or where the memo's risk verdict is too soft. `decisions[i].action = "skip"`. Skipped candidates do not claim capital.
- **Hold capital back (reserve)** — deploy less than all available capital. `reserve_usd > 0`. The reserve is not a candidate-level decision; it is the residual at the `AllocationDecision` level.
- **No-op (full reserve)** — no candidate clears the bar today. All `decisions[i].action = "skip"`; `reserve_usd = available capital`.

**Invariant.** `total_deployed_usd + reserve_usd = available capital`. (Skipped candidates do not consume capital and are not counted in either side of the equation.)
