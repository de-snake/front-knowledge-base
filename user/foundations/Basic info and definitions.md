# Basic info and definitions

## Credit Account

CA operator opens an isolated on-chain Credit Account, borrows the pool's underlying, swaps into a target collateral, and runs a leveraged strategy inside a whitelisted adapter set.

## Collateral

Collateral is the yield-generating token inside of the Credit Account.

## Underlying token

Underlying token is token being borrowed to take leverage. We assume the underlying token is also the pnl denominator

During Credit Account opening, underlying token is swapped to the **collateral** of the strategy.

Underlying token should be used in any PnL / Revenue estimations (e.g. how much USDC I made in the mEdge strategy?) and is the target token for the withdrawal from the Credit Account.

## IRM

Interest rate model

utilization = borrowed amount / supply

![[telegram-cloud-photo-size-2-5409340258404472434-y.jpg]]

## Sources of yield

| # | Source | Description |
| --- | --- | --- |
| 1 | **Pools (passive lending)** | the LP deposits a base asset (USDC, WETH, etc.) into a curated pool and earns yield from borrowers plus incentives. No leverage, no liquidation. |
| 2 | **Credit Accounts (leveraged positions)** | the CA operator opens an isolated on-chain Credit Account, borrows the pool's underlying, swaps into a target collateral, and runs a leveraged strategy inside a whitelisted adapter set. |

## Canonical loop

`Discover → Analyze → Propose → Preview → Execute → Monitor`

The same six stages apply to both Pool and Credit Account flows. This is the organising spine of the rest of the vault.

This section defines the shared purpose and handoff shape only. The canonical flow docs in `user/flows/` own the exact `Inputs / Compute / Outputs` for each stage and action class.

| # | Stage | Purpose | Expected input | Expected output |
| --- | --- | --- | --- | --- |
| 1 | **Discover** | Find candidate pools and strategies that satisfy coarse user filters. | User mandate, asset class / chain / access filters, size, and the current opportunity universe. | 1–3 `PoolOpportunity` / `StrategyOpportunity` candidates with stable ids and reasons for inclusion. |
| 2 | **Analyze** | Decide whether each candidate is viable and why. | Discover candidates, user thesis / constraints, protocol state, market history, and labelled external data. | Evidence-backed ranking or keep / reject verdict, with caveats and missing-data labels. |
| 3 | **Propose** | Convert the selected thesis or monitoring drift into a concrete action. | Selected candidate or existing position, user constraints, current drift reason, and action-class palette. | Specific action intent: amount, target, route class, constraints, fallback, or explicit no-op. |
| 4 | **Preview** | Simulate the exact action package and classify whether it can proceed. | Proposed action plus fresh protocol, backend, issuer / compliance, and user-policy inputs needed for that action class. | Pass / fail verdict, before/after state, warning list, approval mode, and the exact execution package. |
| 5 | **Execute** | Submit only the approved previewed package. | Approved Preview handoff, signer or scoped bot authorization, and matching execution package. | Transaction status, failure reason, or post-action state handed to Monitor. |
| 6 | **Monitor** | Check whether the position thesis still holds and route material drift. | Existing position, current state, user thesis / policy, and user / agent-side continuity log. | No-op, focused Analyze rerun, ProposedAction, Emergency path, or alert. |

**Stage 1 unification.** The user's Discover question is "find me yield"; the agent searches across both `PoolOpportunity` and `StrategyOpportunity` with the same hard filters (asset class, chain, access) and the same ranking surface (composite or maxLeverage yield, operational health, sizing fit). Coarse reasoning may differ slightly between the two surfaces (strategies have a leverage axis; pools do not), but the candidate filtering is mostly identical. Stage 2 is where the path forks — pool candidates flow into [[Pool deposit]]'s LP due-diligence Q-set; strategy candidates flow into [[Credit Account opening]]'s CA due-diligence Q-set.

**Shared handoff rules.**

- Each stage owns its handoff and passes the minimum object needed by the next stage, not a full data dump.
- Protocol-readable facts, indexer facts, issuer / compliance facts, product judgment, and user / agent policy inputs must be labelled separately.
- External data such as rewards, issuer state, governance history, curator history, oracle methodology labels, and user policy must not be silently treated as protocol state.
- Unknown or unavailable data must surface as an unknown or blocking condition when it affects the verdict.
- Every state-changing action must pass Preview before Execute. Execute may only submit the package that Preview produced and the user or scoped bot policy approved.
- If a material input changes between Preview and Execute, the action returns to Preview or Propose.
- Issuer-controlled collateral fields are extensions to the Pool / Credit Account flow contracts, not a separate universe: issuer, eligibility, freeze, redemption, and liquidation fields attach to the same stage handoffs where relevant.

## Credit Account vocabulary

Terms used by Credit Account flows and the CA operator persona. Keep this section as the single source of truth — canonical flow docs should wikilink here rather than re-define.

| Term | Definition | Used in |
| --- | --- | --- |
| **HF** (Health Factor) | The ratio `TWV / debt`. HF > 1 = solvent; HF ≤ 1 = liquidatable. Drift drivers: collateral price moves, LT changes, interest accrual, quota accrual, oracle updates. | All CA monitoring and emergency surfaces. |
| **LT** (Liquidation Threshold) | Per-token risk parameter set by the curator. Determines how much of each collateral counts toward TWV. Lower LT = more conservative. | CA Opening criteria; CA monitoring. |
| **LT ramp** | A scheduled, gradual change to LT over a window of blocks/time. Active downward ramps shrink HF without any price movement. | CA monitoring sub-job "Detect LT ramp"; CA Opening criterion 3. |
| **Quota / quota rate** | Gearbox-specific exposure cap per (token × CM). Quota rate is an additional collateral-specific borrow rate paid continuously to the pool, on top of the underlying borrow rate. | CA returns (eats yield); CA monitoring; pool composition. |
| **Safe pricing** | Pricing rule `min(main_oracle, reserve_oracle)` used to value forbidden tokens at close and to gate certain token-level block/allow decisions. **Not** an automatic fallback: the protocol does not auto-switch to the reserve oracle if the main one fails. The only path by which the reserve becomes the active oracle is an explicit curator action — a manual swap of main → reserve, which is permissionless without timelock but still deliberate. Exit HF computed under safe pricing is the worst-case exit. | CA Opening criterion 5; "Safe-pricing kick-in" edge case. |
| **Phantom token** | Receipt token issued for a position with a delayed-withdrawal queue (e.g. unstaking). Held in the CA but not directly tradable. | CA monitoring sub-job "Track pending withdrawals". |
| **Delayed withdrawal** | Multi-block / multi-day exit mechanism for collateral that cannot be redeemed atomically (LSTs, cooldown vaults). Surfaces as a `claimableAt` timestamp. | CA exit planning; CA monitoring. |
| **CM** (Credit Manager) | Contract that holds and accounts a family of Credit Accounts within a single pool, with its own adapter set, LT table, forbidden tokens, and IRM. | Everywhere CA-related. |
| **CM expiration** | Some CMs are expirable: at expiration all positions inside become liquidatable regardless of HF, with a reduced premium. | CA Opening criterion 5; "CM expiration surprise" edge case. |
| **minDebt / maxDebt** | Pool-level constraints on per-CA debt size. A partial close that would violate `minDebt` is rejected. | Strategy filtering at Discover; partial-exit logic. |
| **Oracle (main vs reserve)** | Each priced asset has a primary oracle and a reserve oracle. Main is used in normal operation; reserve participates in safe pricing. Divergence between the two is a signal. | CA Opening criteria 4–5; CA monitoring sub-job "Detect oracle risk". |
| **TWV** (Total Weighted Value) | Sum across enabled collateral of `min(balance × price, quota) × LT` — i.e., the quota-capped USD value of each token, weighted by its LT. A balance above the quota does not increase TWV; quota headroom above the actual balance does not increase TWV either. Numerator of HF. | HF derivation. |
| **Forbidden tokens / forbidden-tokens mask** | Tokens the curator has marked non-borrowable. Existing CAs may continue holding them but with additional CA-level restrictions on what operations remain allowed (the exact set is configured per-CM, and may include limits on debt increases, swaps, and adapter calls). Their TWV contribution is computed under safe pricing. The user is expected to unwind. | CA monitoring; "Safe-pricing kick-in" edge case. |
| **Liquidation premium** | Bonus the liquidator captures at liquidation, parameterised as a **percentage of the liquidated account's collateral value** (per `CreditConfiguratorV3.sol`: "Percentage of liquidated account value that can be taken by liquidator"). Pre-baked into the underlying-as-collateral LT — `LT = 100% − liquidationPremium − feeLiquidation` — so the haircut is reserved in TWV from the moment the CM is configured. At liquidation: the liquidator repays the CA's debt; the protocol takes `feeLiquidation`; the liquidator captures `liquidationPremium`; both are slices of the seized collateral. The companion `liquidationDiscount` is the residual: `liquidationDiscount = PERCENTAGE_FACTOR − liquidationPremium`. Reduced to `liquidationPremiumExpired` for forced exits of expired CMs. | CA Opening; emergency reasoning. |
| **Multicall** | Atomic batched execution primitive that lets a CA open / adjust / close in a single transaction, including the swap leg. | Stage 4 Preview, Stage 5 Execute. |
| **IRM bands (U1, U2, Rbase, Rslope1, Rslope2)** | The interest rate model is piecewise-linear. Below U1: shallow slope. Between U1 and U2: steeper. Above U2: penalty slope (or hard cap, depending on configuration). Each segment is parameterised by a base rate and a slope. | Pool deposit Stage 2 yield analysis; CA monitoring of borrow cost. |

## Pool vocabulary

Terms used by Pool flows and the Pool LP persona.

| Term | Definition | Used in |
| --- | --- | --- |
| **Insurance fund** | Pool-level loss-absorption pot that takes the first hit on bad debt before LP shares are written down. A material decline or approaching zero is a Priority-2 LP signal. | Pool deposit Stage 2; Pool monitoring Q5. |
| **Bad-debt canary / share-price canary** | The pool share price is the canonical indicator that bad debt has been realised against LPs. Any drop between checks (other than from a known incident) is a canary. | Pool monitoring Q5 / sub-job "Detect bad-debt event". |
| **Organic vs incentive APY** | Yield decomposition. *Organic* APY comes from borrower interest paid into the pool. *Incentive* APY comes from external rewards (Merkl, protocol-specific emissions) that may expire. The deposit thesis must hold on organic alone. | Pool deposit Q1; Pool monitoring Q1. |
