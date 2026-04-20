> **When I** own a leveraged Credit Account,  
> **I want to** verify in under a minute that I'm safe, that I'm still making money, that nothing has changed on me, and that I know what I'd do if it had,  
> **so I can** leave confident, or act on a specific corrective step without losing time searching for the right control.

**Five ownership questions** (explicit, binding, in priority order — risk first, returns second, composition third, options fourth, history fifth):

| #   | Question                      | Minimum evidence to answer                                                                                                                                                                                                                         | Notes for agent / UI                                                                                                                                                                                                                                           |
| --- | ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **Am I safe?**                | HF (number + plain-language label), liquidation distance in plain terms ("X asset must drop Y % for liquidation"),<br><br>time-to-liquidation, <br><br>LT-ramp status, <br><br>forbidden-tokens overlap                                            | Must be answerable in < 3 s of session. <br>HF always has a plain-language interpretation attached.<br><br>==note: what interpretation? need a concrete example==                                                                                              |
| 2   | **Am I making money?**        | Net APY (after borrow + quota + fees), <br><br>total return in underlying + %, <br><br>30d account-value sparkline = ==PNL==                                                                                                                       | Must be answerable in < 5 s.                                                                                                                                                                                                                                   |
| 3   | **What's inside my account?** | Per-token balances + USD value, <br><br>debt breakdown (principal + interest + quota + fees), <br><br>current leverage <br><br>active strategy description in plain language<br><br>==note: our own description / written with help of a curator== |                                                                                                                                                                                                                                                                |
| 4   | **What can I do?**            | Contextual next-step recommendations based on HF and opportunity state: <br><br>"Add collateral" / <br>"Reduce leverage" / <br>"Increase leverage" / <br>"Claim X rewards" / <br>"Enter farm Y"                                                    | Max 2–3 recommendations. Every recommendation is paired with a before/after preview before signing.<br><br>==note: every recommendation would go through the propose & preview stages of [[Credit Account — User flow (CA operator)#Stage 3 · Propose (CA)]]== |
| 5   | **What happened?**            | Chronological action log with HF deltas, reward claims, governance events that affected this CM, bot triggers                                                                                                                                      | Needed monthly, not daily — but when needed, absence destroys trust.                                                                                                                                                                                           |

**Plain-language principle for agents.** Every raw metric should be served with a translation. Raw value for machines and advanced users; translation for the glance.

- `HF 1.036` → "Low — your position liquidates if HF drops below 1.0."
- `Liquidation Price 1.04 ETH+/WETH` → "Liquidation if ETH+ drops ~4 % vs WETH."
- `Time to liquidation 38 mo` → "At current borrow-rate accrual with no price movement: ~38 months. This is an extrapolation."

==note: virtual liquidations here?==

**Emergency-path contract.** When HF enters the danger zone (< 1.1), the user's path from awareness to signed remediation must be ≤ 2 clicks / tool calls. The screen must surface a danger banner; the agent must surface a top-line danger line and a single concrete proposed action (Add Collateral or Reduce Leverage, with amount and before/after).

### Sub-jobs (ownership job map)

| #   | Sub-job                   | Success looks like                                                                                                                                             |
| --- | ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Glance at safety          | HF with plain-language label, liquidation-distance in plain terms ("X asset must drop Y % for liquidation"), time-to-liquidation, visible in < 3 s.            |
| 2   | Glance at returns         | Net APY after borrow + quota + fees, total return in underlying + %, 30d sparkline, visible in < 5 s.                                                          |
| 3   | Understand composition    | Per-token balances + values, debt breakdown, explicit leverage ratio ("9.8×"), plain-language strategy description.                                            |
| 4   | Attribute HF movement     | When HF moves, know _why_: price vs LT ramp vs interest accrual vs quota vs forbidden-token safe pricing vs oracle staleness.<br><br>==note: seems redundant== |
| 5   | Detect LT ramp            | Know if any held collateral has an active LT ramp and what the final LT + time remaining are.                                                                  |
| 6   | Detect oracle risk        | Freshness per token, divergence between main and reserve, recent anomalies in 90d.                                                                             |
| 7   | Detect curator change     | LT reductions, forbidden-token additions, IRM changes — past and queued.                                                                                       |
| 8   | Track pending withdrawals | Phantom tokens and delayed-withdrawal queues with `claimableAt` timestamps, claim-when-ready calldata.                                                         |
| 9   | Track rewards             | Claimable amount, attribution to the CA (including merkle rewards that accrue to the owner wallet, not the CA itself).                                         |
| 10  | Decide add collateral     | Amount needed to reach target HF, before/after preview, fee estimate.                                                                                          |
| 11  | Decide reduce leverage    | Amount to repay to reach target leverage, before/after preview, swap impact estimate.                                                                          |
| 12  | Decide increase leverage  | Additional borrow to reach target leverage, resulting HF, resulting net APY.                                                                                   |
| 13  | Decide change strategy    | Current farm vs alternatives with HF impact per option, swap cost per switch.                                                                                  |
| 14  | Decide partial exit       | Amount withdrawable without crossing HF floor; resulting equity change.                                                                                        |
| 15  | Decide full exit          | Estimated equity returned, total cost (swap + fees + gas), time to settle (including any delayed withdrawals).                                                 |
| 16  | Handle emergency          | One-click path to Add Collateral or Reduce Leverage with pre-filled amount; HF floor enforced in preview.                                                      |
| 17  | RWA compliance check      | Own frozen status, KYC validity, investor-registry status, next redemption window.                                                                             |

### Edge cases & known failure modes

- **LT ramp cliff.** The user opens at HF 1.4 assuming a stable LT. An active ramp schedule reduces LT over the next 14 days; HF drops to 1.05 with no price movement. User must deleverage or exit on schedule.
- **Quota rate bleed.** High quota rate on the target token means the position loses money on flat prices. Breakeven was computed at current quota; quota rate rises; strategy turns uneconomical.
- **Safe-pricing kick-in.** A held token becomes forbidden. Safe pricing (`min(main, reserve)`) applies on close; exit HF is materially lower than the snapshot HF. User takes unexpected loss on exit.
- **Delayed-withdrawal clog.** Position includes a phantom token with a 5-day unstaking queue. User needs to exit on day 2; only swap path available; price impact eats the thesis.
- **CM expiration surprise.** Expirable strategy reaches expiration; position is liquidatable regardless of HF with a reduced premium. User did not plan the exit.
- **RWA freeze.** Securitize admin calls `setFrozenStatus()` on the user's CA. No exit, no rebalance, no repay. User waits indefinitely.
- **KYC revocation.** KYC expires or is revoked; user cannot receive RWA tokens back during withdrawal; must resolve KYC before any exit.
- **Oracle staleness at the wrong moment.** A token's oracle hasn't updated in > staleness window; the next update drops price significantly and triggers immediate liquidation.

----
> from other doc by Tim: 
# Core JTBDs (action-centered)

## 1. Avoid liquidation / fix risk

* User sees health factor is low, wants to avoid liquidation, and achieves it by **adding collateral**

* User sees health factor is low, wants to reduce risk without adding funds, and achieves it by **repaying part of the debt (decrease leverage)**

* User sees health factor is low, wants fastest recovery, and achieves it by **combining add funds + repay (single rescue flow)**

* User sees health factor is borderline, wants a safer buffer, and achieves it by **decreasing leverage**

* User expects volatility, wants to preempt liquidation, and achieves it by **decreasing leverage before market moves**

---

## 2. Automate risk management

* User sees health factor requires constant monitoring, wants to avoid manual management, and achieves it by **enabling automated protection**

* User uses protection but wants tighter or looser control, and achieves it by **adjusting HF thresholds for auto-deleverage**

* User sees protection is too aggressive or expensive, wants manual control, and achieves it by **disabling automated protection**

---

## 3. Improve returns (same strategy)

* User sees APY is lower than expected, wants higher returns, and achieves it by **increasing leverage**

* User sees borrow cost eating yield, wants to reduce drag, and achieves it by **decreasing leverage**

* User sees returns are good but can be amplified, wants to scale gains, and achieves it by **increasing leverage**

---

## 4. Improve returns (change strategy)

* User sees APY is low relative to alternatives, wants better yield with same base asset, and achieves it by **switching to a higher-yield strategy**

* User sees better opportunities elsewhere, wants to reallocate capital, and achieves it by **moving funds to another strategy**

---

## 5. Scale position (when satisfied)

* User sees position performing well, wants to increase exposure, and achieves it by **adding more funds**

* User adds funds, wants to keep same risk profile, and achieves it by **adding funds with proportional leverage**

* User adds funds, wants to be more aggressive, and achieves it by **adding funds + increasing leverage**

---

## 6. Take profit / extract capital

* User sees profit, wants to take some money out, and achieves it by **partial withdrawal**

* User wants to lock in gains but keep position open, and achieves it by **repaying part of debt + withdrawing freed collateral**

* User wants to reduce exposure gradually, and achieves it by **withdrawing funds and/or decreasing leverage**

---

## 7. Exit completely

* User no longer wants exposure, wants to fully exit, and achieves it by **closing the credit account**

* User tries to close but cannot (slippage / constraints), wants to exit anyway, and achieves it by **step-by-step unwind: decrease leverage → withdraw → close**

---

## 8. Rebalance / adjust position

* User sees position composition is suboptimal, wants to adjust allocation, and achieves it by **swapping assets inside the account**

* User wants to change exposure without changing size, and achieves it by **rebalancing assets**

---

## 9. Manage rewards

* User sees accumulated rewards, wants to realize them, and achieves it by **claiming rewards**

---

## 10. Handle system constraints (critical UX gap)

* User tries to increase leverage but cannot, wants to proceed, and achieves it by **choosing alternative actions: reduce size or switch strategy**

* User tries to withdraw but is blocked by risk limits, wants to extract funds, and achieves it by **repaying debt first, then withdrawing**

* User sees actions are restricted, wants to understand options, and achieves it by **following available safe actions: add collateral, repay, reduce leverage, or close**

---

## 11. Explore / optimize (opportunistic)

* User sees suggestion of higher-yield options, wants better performance, and achieves it by **switching strategy**

* User reviews available farms, wants to optimize capital allocation, and achieves it by **moving funds between strategies**