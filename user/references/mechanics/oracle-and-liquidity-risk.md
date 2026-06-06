# Oracle and liquidity risk mechanics

Stable mechanics for oracle categories, liquidity-cascade versus liquidity-trap failure shapes, and LP / Credit Account oracle drill triggers. Heavy token-specific research belongs in `../workflows/asset-investment-diligence/`; full oracle feed parsing belongs in the [oracle analysis workflow](../workflows/oracle-analysis/README.md).

## Drill — Oracle types and LP risk shapes

The LP carries a different failure mode depending on the oracle's category, even when the feed is working:

- **Market price** (Chainlink real-time feeds, Pyth, on-chain TWAPs, Pendle market TWAPs) → **liquidity-cascade risk.** Liquidations fire on time, but in thin markets or gapping conditions, forced sales can execute below collateral value (bad debt), and the cascade itself spikes pool utilisation — throttling LP withdrawals exactly when they want out.
- **Fundamental** (primary-market exchange rate, issuer/admin ratio, proof-of-reserves collateralisation ratio, underlying reference used because redemption is expected to hold) → **trust-and-redemption risk.** The feed can match the contractual claim while missing secondary-market stress, eligibility limits, redemption queues, or issuer failure.
- **NAV** (`ERC4626.convertToAssets`, staking-derivative exchange rates, fund NAV reports, tokenized-fund attestations) → **liquidity-trap risk.** Sustained depegs may be invisible to the feed: borrowers over-borrow at a stale valuation, liquidations do not fire, and bad debt accumulates behind un-liquidatable positions that lock LP capital.
- **Hardcoded** (e.g., 1 USDT = 1 USDC fixed) → same trap as NAV with no surfacing mechanism for a depeg at all.
- **Hybrid / MetaOracle / composite** — composite feeds (e.g., `cp0xLRT/wstETH * wstETH/stETH * stETH/USD`), bounded feeds, main/reserve pairs, and primary/backup systems inherit risk shapes of all underlying components; failure mode dominates by the weakest link or by the slowest switching rule.

This drill is LP-centered. For borrower / Credit Account analysis, invert the question before writing a conclusion: market responsiveness can be borrower-unfriendly because it triggers liquidation on temporary dislocations, while hardcoded / NAV / fundamental pricing can be borrower-friendly during a temporary collateral dip and LP-unfriendly during persistent divergence. The final conclusion must therefore state the position side, token role, stress direction, and loss bearer.

## Drill — When to run the oracle analysis workflow

Run the [oracle analysis workflow](../workflows/oracle-analysis/README.md) instead of relying on this mechanics drill when any of the following is true:

- the feed has more than one node or source primitive;
- the feed uses a Gearbox `PRICE_FEED::COMPOSITE`, `PRICE_FEED::BOUNDED`, `PRICE_FEED::ERC4626`, `PRICE_FEED::CURVE_TWAP`, Pendle factory oracle, MetaOracle, main/reserve pair, or safe-pricing branch;
- the asset is issuer-controlled, tokenized-security-like, redemption-window-based, or queue-based;
- a user asks to compare oracle setup risk against another protocol, for example a Gearbox market versus a Morpho market;
- LT / LLTV appears aggressive relative to the complexity of the oracle path.

Workflow invariant: do **not** stop at the top-level `contractType`, UI label, or human-readable feed name. Parse the feed as a dependency DAG, classify every node, audit every source primitive, and only then assess cascade-vs-trap behavior.

## Drill — Collateral-induced liquidity risk by oracle type

**Why utilisation spikes — the underlying mechanics.** A successful liquidation by itself *reduces* U: debt is repaid, cash returns to the pool. The cascade-induced spike is a second-order effect with two compounding mechanisms:

1. **Withdrawal-vs-repayment race.** With `U = Borrowed / (Cash + Borrowed)`, an LP withdrawal of $X reduces `Cash` and `TVL` by X (`Borrowed` unchanged) → U *rises*. A liquidation-repayment of $Y reduces `Borrowed` by Y and adds Y to `Cash` → U *falls*. During a cascade, LPs see the event and withdraw immediately; liquidators are bottlenecked by thin DEX depth. The race favours the withdrawal side, so U trends up while the cascade is in flight.
2. **Stuck-debt pinning.** Liquidations that cannot clear at all (slippage > liquidation premium → no liquidator wants the trade) leave the position open. `Borrowed` does not fall as expected; the self-cleaning property of liquidations stops working. Even without an LP run, U does not naturally retrace.

**Two oracle-driven failure shapes:**

- **Market oracle + thin liquidity = liquidation-cascade risk.** Forced sales execute below collateral value, generating bad debt. Mechanically, U spikes during the cascade because LP withdrawal pressure outpaces liquidator repayments — the cash side of the pool empties faster than the debt side. Without the LP-run leg, repayments would *reduce* U; the cascade signature is specifically the withdrawal-vs-repayment race. Historical anchor: stETH June 2022 (Aave WETH market).
- **NAV / hardcoded oracle + persistent depeg = liquidity-trap risk.** Oracle stays silent, liquidations do not fire, un-liquidatable positions inflate utilisation indefinitely. No cascade required — the trap forms quietly. Historical anchor: Aave-CRV Nov 2022 (Eisenberg's CRV short couldn't be liquidated cleanly at all; debt stayed put and U pinned high without an LP run needed).

## Drill — Q6 oracle drill triggers

Q6 (oracle freshness / divergence / methodology) is excluded from the Pool LP Glance set in [[Three-layer progressive disclosure]]; oracle is a **P2** LP loss vector in [[Personas and audience#Pool LP (passive lender)|Personas]]. All Q6 sub-Qs are T2; Q6 fires only when one of these triggers fires:

- **Q5 canary fires** — share-price drop or insurance-fund delta. Oracle is the prime suspect for the upstream cause; Q6 runs to identify whether a stale or methodology-shifted feed caused the realised loss.
- **Q3 detects a new top-3 collateral** — the new token's oracle is suspect by default until verified against the LP's accepted-methodology list.
- **LP is sophisticated** — institutional, structured-product desk, or issuer-controlled-asset-aware. Persistent T2 coverage on every monitoring call.
- **Known structural oracle risk on dominant collateral** — pool has a dominant collateral on a NAV / hardcoded / hybrid feed. The cascade-vs-trap shape ([[oracle-and-liquidity-risk#Drill — Oracle types and LP risk shapes|drill ↗]]) makes oracle drift a non-cosmetic concern.

When none fire, Q6 is skipped and the `MonitoringSnapshot.verdicts.q6_oracle` field is absent.

## Drill — Q5 oracle drill triggers for CA

Q5 (oracle freshness / divergence / methodology) is excluded from the CA Glance set in [[Three-layer progressive disclosure]]; oracle is a **P2** CA loss vector in [[Personas and audience#CA operator (leveraged user)|Personas]]. All Q5 sub-Qs are T2; Q5 fires only when one of these triggers fires:

- **Q1 HF attribution flagged oracle as cause** — HF dropped and the dominant attribution component is "oracle update" or "safe-pricing kick-in." Q5 runs to identify whether a stale or methodology-shifted feed caused the drop.
- **Q1 attribution flagged composition shift** — a new token entered the position via rebalance / change_strategy. Q5 verifies the new token's oracle methodology is acceptable under user thesis.
- **User is sophisticated** — institutional, structured-product desk, or issuer-controlled-asset-aware. Persistent T2 coverage on every monitoring call.
- **Known structural oracle risk on held tokens** — position holds a token on a NAV / hardcoded / hybrid feed (cross-ref [[oracle-and-liquidity-risk#Drill — Oracle types and LP risk shapes|drill ↗]]). Different from Pool monitoring's *dominant collateral* trigger because CA holds collateral directly — every held token with structural oracle risk is in scope.
- **Issuer-controlled token's oracle methodology shifted** — issuer-controlled tokens often use NAV oracles updated by the issuer; methodology change (NAV → market, or vice versa) reshapes the cascade-vs-trap risk on this specific position.
- **Per-token oracle approaching staleness window** — for any held token, the feed age is approaching its staleness window under the user / product review policy. This is the **proactive trigger** that fires before liquidation — without it, Q5 is purely reactive and the user only learns about staleness after Q1 catches the realised loss.

When none fire, Q5 is skipped and `MonitoringSnapshot.verdicts.q5_oracle` is absent.
