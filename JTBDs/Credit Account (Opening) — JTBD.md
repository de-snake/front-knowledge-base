### Main job statement

> **When I** have a thesis on a specific yield-bearing collateral (an LST, a stablecoin carry, an LP position, a tokenised security),  
> **I want to** amplify that thesis with leverage inside an isolated, adapter-gated account where the safety envelope (LT, oracle, quota, liquidation) is transparent and the exit path is proven,  
> **so I can** earn a leveraged net yield while keeping full, continuous visibility into what's moving my HF and what could force me out.

### Sub-jobs (job map)

| #   | Sub-job                           | Success looks like                                                                                                      | User flow step                                                                    |
| --- | --------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| 1   | Define the thesis                 | User names the target collateral, target leverage, expected hold horizon, HF floor.                                     |                                                                                   |
| 2   | Locate candidate strategies       | 1–3 strategies on the right collateral at the right leverage ceiling surface in under a minute.                         | [[Credit Account — User flow (CA operator)#Stage 2 · Analyze — CA due diligence]] |
| 3   | Model the economics               | Net yield after quota / fees / entry friction clears the user's hurdle, with breakeven < horizon.                       |                                                                                   |
| 4   | Validate collateral safety        | Asset properties, LT configuration, oracle methodology, exit routing, and — if RWA — compliance layer all check out.    |                                                                                   |
| 5   | Confirm the curator & CM envelope | Curator known, CM not paused, not near expiration, no hostile pending governance.                                       |                                                                                   |
| 6   | Preview exactly                   | Simulated HF, actual leverage, and swap impact match the proposal; warnings are all benign.                             | [[Credit Account — User flow (CA operator)#Stage 4 · Preview (CA)]]               |
| 7   | Open the position                 | Previewed bytes are signed and submitted; post-open state matches the preview.                                          | [[Credit Account — User flow (CA operator)#Stage 5 · Execute (CA)]]               |
| 8   | Hold & maintain                   | Monitor catches HF drift, LT ramp, oracle staleness, governance change, freeze events; user acts or waits deliberately. | [[Credit Account — User flow (CA operator)#Stage 6 · Monitor (CA)]]               |
| 9   | Exit on thesis or pressure        | Delayed-withdrawal queue timed correctly; price impact within tolerance; partial unwind respects `minDebt`.             |                                                                                   |

### Functional / emotional / social dimensions

- **Functional.** Run a leveraged strategy where every parameter that affects survival is queryable: LT, LT ramp, oracle type and staleness, quota rate, IRM curve, `minDebt`/`maxDebt`, delayed-withdrawal support, forbidden-tokens mask, pending governance.
- **Emotional.** Sleep at night. When HF moves, the user wants to know _why_ within one monitoring cycle — was it price, was it interest, was it LT ramp, was it a forbidden-token safe-pricing kick-in.
- **Social.** For structured-product desks and funds: explain the position (and its exit plan) to colleagues or investors, with receipts.

### Decision criteria & "good open" definition

A good CA open satisfies all of:

1. Net yield (after borrow, quota, fees, entry swap) > user's hurdle; breakeven < user's horizon.
2. ~~Target leverage < `maxLeverage(LT)`; post-open HF > user's floor (typically ≥ 1.3).~~
3. No active LT ramp that would cross the user's HF floor within the hold horizon.
4. Oracle methodology appropriate to the asset's market structure; no recent oracle glitches in 90d history.
5. Main-vs-reserve oracle divergence within tolerance (exit HF on `min(main, reserve)` is acceptable).
6. Price impact at position size via adapter-accessible liquidity is acceptable both today and in 90d history.
7. Borrowable liquidity leaves headroom for one round of leverage adjustment.
   
   ==note: could be an alert if low or 0, otherwise redundant
   
8. Curator parameter-change log shows stability or expected drift; no high-impact pending governance during the hold horizon.
9. For RWA CMs: freeze authority identified and accepted; KYC valid; next redemption window compatible with exit plan; whitelisted-liquidator count ==above threshold==.
   
   ==note: once again, what threshold?==
   
1. Entry multicall preview: `HF ≥ target`, `actual leverage within ±5 % of target`, `swap impact ≤ estimate from Analyze`, no warnings.


### Forces of progress — addendum: cost of doing nothing
Unlike a passive pool deposit where "do nothing" is cost-free, a Credit Account bleeds value on autopilot:

- Borrow interest accrues continuously against the underlying debt.
- Quota interest accrues on enabled collateral.
- Rewards that aren't claimed don't compound.
- HF drifts as LT ramps execute and price moves.
- Expirable CMs creep toward forced exit.

This flips the usual DeFi default: the "no action" baseline is a position that is slowly losing money. UI and agents should surface this — daily borrowing cost in plain language, unclaimed reward amount, days-to-expiration for expirable CMs — as a recurring gentle push, not a one-time disclosure.