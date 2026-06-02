# Credit Account opening — reference

Drill sections referenced from [[Credit Account opening]] table rows. Each drill is a self-contained explanatory unit; the calling row carries only the verdict-level summary plus a wikilink. Topic names are flow-agnostic where possible — flow-agnostic curator and oracle drills live in [[Pool deposit - reference]] and are wikilinked from CA opening directly.

**Source boundary.** These drills deliberately separate observable protocol mechanics from product judgement and external diligence. IRM, debt limits, quotas, LT, expiration, and safe-pricing are protocol-observable inputs. Yield projections, leverage comfort, issuer calendars, liquidity assumptions, and accept/reject thresholds are product, user-policy, or external-data judgements and should be labelled that way in the calling row.

## Drill — IRM curve sensitivity

**Why this matters at Stage 2 Q1.** Pool IRM is piecewise-linear: shallow slope below `U1`, steeper between `U1` and `U2`, penalty slope above `U2`. Leveraged net APY is `(collateralYield × leverage) − borrowRate − …`; small movements in `borrowRate` are amplified by `leverage`, so the **derivative** of borrowRate with respect to utilisation is the load-bearing fragility metric — not just the current rate.

**How the agent computes sensitivity.**
1. Read current utilisation `U` and `Pool.IRM.{U1, U2, Rbase, Rslope1, Rslope2, Rslope3}`.
2. Project borrow rate at `U + 10 pp` using the appropriate slope (`Rslope1` if still below U1, `Rslope2` if crossing into U1–U2, `Rslope3` if crossing U2).
3. Compute leveraged-net-APY at projected rate and compare to current.
4. Threshold: if the +10 pp projection drops net APY by more than X bps OR flips negative, the position is **fragile**.

**Failure shape.** A pool that's fine today at U = 75 % can lose its economics if U rises to 85 % (steeper slope kicks in). LP withdrawals, new borrows, or quota saturation can drive U upward without any user action. Leverage amplifies the impact.

## Drill — Structural risk taxonomy

**At Stage 2 Q2.** Two structural risks the user takes on by entering a CM, distinct from collateral-specific risk:

- **Withdrawal-queue mechanics.** Some collateral has a native withdrawal queue (LSTs, cooldown vaults). The CA holds the position via a phantom token; exit requires either swapping (price-impact at size) or waiting through the queue (`claimableAt` timestamp). Position-side: the user must plan exits around queue duration; agent monitors `claimableAt` per token.
- **Expiration mechanic.** Expirable CMs become liquidatable regardless of HF after `expirationTimestamp`, with a reduced liquidation premium. Surprise expiration is a known failure mode — the user must plan exit before expiration.

**Not a CA structural risk: bad-debt socialisation.** Cascade liquidations exceeding the insurance fund socialise losses to LPs of the underlying pool — **not** to the CA operator. CA operators bear collateral-specific liquidation losses and the haircut from `liquidationPremium`, but not LP-side socialised losses. A depleted insurance fund is at most an *upstream* signal that may bring CM-level interventions (LT cuts, forbidden-token additions, pool pause) — those are caught at [[Credit Account opening#Q4 · Who manages this CM, and is the envelope stable?|Q4]] curator activity / [[Credit Account opening#Q5 · What could change between now and exit?|Q5]] change-feed, not as a Q2 structural risk.

**Cross-reference.** Q1 borrow-rate-history is also a liquidation-risk signal: extreme rate spikes can liquidate via rapid interest accrual on the user's debt, not via price movement.

## Drill — Deriving safe HF margin from asset-specific risk

**At Stage 2 Q2 (Gearbox config lens).** The user or mandate should provide the binding HF floor. If it is missing, the agent derives an **asset-specific recommended floor** from the candidate's actual tail-risk profile and routes it for review before Preview / Execute.

This is a reasoning task, not a formula. The agent looks at the inputs below, applies the reasoning directions, and produces a recommendation per candidate. Specific numerical weights are the agent's call — they depend on the candidate's properties, current market regime, and user risk context.

### What the agent considers

**Realised volatility of the dominant collateral (90d, annualised).** Higher vol means larger headroom is needed before normal drift breaches the floor. Leverage amplifies the impact — the same Δ price moves HF more at higher leverage. The agent reads vol from price history and sizes the margin so that a bad-case tail drift over the user's hold horizon doesn't cross the floor. The mapping from vol to margin is the agent's call given the candidate's other properties and user context.

**Asset class.** Different classes have different tail behaviours that vol alone doesn't capture:
- **LSTs** carry de-peg history (e.g., stETH June 2022; smaller events on cbETH / rETH). The agent considers prior depeg magnitude, whether the validator-set or slashing surface has changed since, and weights the floor wider when those signals indicate latent tail risk.
- **LP tokens** compose risks of their underlying components — the agent uses the worst component's vol, not the average, and adds margin for impermanent-loss and depeg-of-component-vs-component risk.
- **Issuer-controlled / tokenized-security collateral** carries freeze-probability and redemption-window-mismatch risk — un-liquidatable freeze risk requires extra margin because the user cannot exit reactively. Tighter redemption windows imply more margin; wider windows or active secondary markets imply less.
- **Stablecoins** carry a de-peg tail; algo-stable or yield-bearing wrappers add further tail risk.
- **Synthetics** inherit risks of all upstream components; the floor is conservatively set above the worst of them.

**Liquidation premium + discount.** Already baked into `LT`, but informs how far HF can fall before a liquidator captures premium beyond the user's collateral. A higher premium means more user value taken at liquidation, which justifies a wider buffer.

**User risk tolerance.** Session or mandate config. The agent never silently overrides the user's stated tolerance — see "When to override" below.

### Cross-checks the agent applies

- **LT-ramp horizon.** If the candidate has an active downward LT schedule that lowers `LT` before the user's hold horizon ends, the recommended floor should be computed at the **post-ramp `LT`**, not the current `LT` — the position must clear the floor at the worst `LT` it'll see while held. Cross-ref Q2's LT ramp horizon check.
- **Oracle category.** NAV / hardcoded oracles on the dominant collateral mean the oracle won't catch a real depeg — the user's actual safety margin is smaller than the modeled HF suggests. The agent widens the floor to account. Cross-ref [[Pool deposit - reference#Drill — Oracle types and LP risk shapes|Oracle types drill]].
- **Adapter routing depth.** Thin adapter routing on the dominant collateral (Q3 T2 finding) compounds slippage at exit / liquidation. The agent widens the floor when exit-side liquidity is fragile.

### Output

Per-candidate `recommended_hf_floor` is carried into the `ResearchMemo.constraints.hf_floor_required` field when the user floor is missing or the asset profile suggests more headroom than the mandate supplied. Stage 3 sizes target leverage against the reviewed floor. The agent should also surface its reasoning trail (which factors drove the recommendation, with raw values where available) in the memo — not just the number.

### When to override

If the user explicitly accepts a tighter floor for a high-confidence asset (e.g., institutional running a USDC carry with deep adapter liquidity), the recommended floor may be relaxed below the agent default. Surface as an explicit override gate at Stage 3 — never silently below the recommendation.

## Drill — issuer-controlled collateral branch

**At Stage 2 Q2 (conditional branch).** Issuer / eligibility risks per tokenized-security or issuer-controlled token in the CM:

| Risk | Description |
| --- | --- |
| **Transfer restriction type** | DS Token Protocol, ERC-3643, or custom — a compliance layer that can block transactions based on whitelist / KYC state. |
| **Freeze capability** | If the CM uses a compliance-gated path, the issuer/admin can freeze the user's Credit Account. When frozen: no deposits, no withdrawals, no borrowing, no repaying, no liquidation. The position is effectively suspended. |
| **Freeze authority** | The specific address / entity that holds the freeze power. The user must identify and accept this authority before opening. |
| **Investor reassignment risk** | The issuer / investor registry can reassign the CA to a different investor (intended for estate settlement / lost keys, but structurally the capability exists and could be misused). |
| **Eligible-liquidator depth** | From the CA perspective: few eligible liquidators mean the user may sit in a liquidatable state longer. The feed lives in [[Data requirements and to-dos]]; interpretation depends on user / product policy, not a universal threshold. |
| **Redemption windows + secondary-market liquidity** | When can the user actually convert the asset back to cash. Affects exit planning at Q3. |

**Failure modes (cross-reference Edge cases in [[Credit Account management]]).** Issuer freeze cascade, KYC revocation mid-position, redemption-window mismatch with hold horizon.

## Drill — Adapter routing constraints

**At Stage 2 Q3 (T2).** The CA can only swap through CM-approved adapters, not the full DEX market. This creates two visible spreads:

1. **Adapter-vs-aggregator spread on entry** — Gearbox's router may give worse offers than 1inch / CowSwap / Paraswap at certain sizes / asset pairs. Pull a sample quote from each at the user's intended position size; surface the spread.
2. **Adapter-vs-aggregator spread on exit** — same comparison at exit size; in practice the spread is asymmetric (entry size, exit size, market depth all differ).

**Surface note.** ==Idea: fetch DEXs and compare to our own router.== Show the user where their entry and exit costs sit relative to best-available; do not block (the user may still choose Gearbox-route for atomicity), but make the spread visible.

## Drill — CM operational envelope

**At Stage 2 Q4.** Five operational levers a CM exposes:

- **Pause status.** Per-CM. When paused: no new positions, no liquidations. Existing positions accrue interest but can't be unwound until unpause.
- **Expiration timestamp.** For expirable CMs only. After expiration, all positions become liquidatable regardless of HF, with a reduced premium. Hold horizon must end before expiration with margin.
- **New-debt-per-block cap.** Caps new debt per block. Zero means no new borrows allowed — the user **skips** the CM at Stage 2.
- **Current debt-limit utilisation.** `currentDebt / debtLimit`. Approaching 100 % means new opens may be blocked even before pause; flag at 80 %+.
- **Facade pause.** Distinct from CM pause — the credit facade contract itself can be paused, blocking the entry path even for an otherwise-healthy CM.

**Surface UX.** ==I would only display this info if facade is paused / expiration date exists and is sooner than 1 month== — keep the operational surface quiet by default; surface only abnormal states or imminent expiration.

## Drill — KYC-gated execution path

**At Stage 2 Q4 + Stage 5.** Some CMs route actions through a compliance wallet/factory layer before the Credit Account operation is accepted.

- **Operation routing.** The action must clear KYC validity, freeze status, and investor-registry checks before it reaches the Credit Account. Product copy should show this as **compliance-gated execution**, not as a normal one-click CA operation.
- **Bot delegation blocked.** Scoped bot signers cannot manage these positions; the user must remain in a human-in-the-loop execution path.
- **Implication for Stage 3 / Stage 5.** When picking a KYC-gated CM at Stage 3, the user must accept HITL-only execution (no bot delegation). Surface this constraint at Stage 3 so it's not a Stage 5 surprise.

## Drill — IC decision palette + route selection

**Source boundary.** This is a product route-selection rubric, not protocol enforcement. Protocol state can say which routes are executable; the IC rubric chooses the route, sizing, fallback, or no-op based on user suitability and risk/return quality.

**At Stage 3.** The IC chooses among palette items per allocation pass; each palette item maps to per-candidate `decisions[]` entries plus `route` selection.

- **Open one CA fully** — pick the strongest memo and deploy all available capital there at the chosen target leverage. `decisions[i].action = "openCA"` for the chosen candidate; route picked from adapter set; all others `"skip"`. `reserve_usd = 0`.
- **Split across multiple CAs (diversification)** — distribute across several memos, each with its own target leverage and route. Multiple `decisions[i].action = "openCA"`. Total deployed ≤ available capital.
- **Adjust an existing CA** — instead of opening, `action = "adjustLeverage"` modifies an existing CA's leverage / collateral. Route applies if the adjustment requires a swap leg.
- **Rebalance an existing CA** — within-position composition shift (e.g., swap one collateral for another inside the same CA). `action = "rebalance"`; route covers the internal swap.
- **Skip individual candidates** — fine in isolation but redundant given existing positions, or risk verdict too soft. `action = "skip"`. Skipped candidates do not claim capital.
- **Hold capital back (reserve)** — deploy less than all available capital. `reserve_usd > 0`. Reserve is `AllocationDecision`-level, not candidate-level.
- **No-op (full reserve)** — no candidate clears the bar today. All `decisions[i].action = "skip"`; `reserve_usd = available capital`.

**Route-selection sub-decisions per non-skip action.**
- **Adapter set.** Which CM-approved adapters route the entry swap (or the rebalance swap). Pick the set with best price-at-size from Q3 retrieval.
- **Slippage tolerance.** User- or mandate-supplied. The user can widen for fragile / thin-route assets or narrow for atomic-swap assets; the agent should not apply a hidden default.
- **Max price-impact budget.** A hard cap that aborts the multicall in Stage 4 Preview if exceeded. Distinct from slippage (which absorbs noise) — price-impact budget caps the structural cost of entering at this size.

**Invariant.** `total_deployed_usd + reserve_usd = available capital`. Skipped candidates do not consume capital and are not counted in either side of the equation.

## Drill — Multicall preview mechanics

**At Stage 4.** What the SDK router simulation actually checks, in order:

1. **Multicall assembly.** Concatenate: `openCA` (mint CA NFT) + `addCollateral` (deposit underlying) + `borrow` (mint debt) + `swapExactInput` (entry swap leg, via adapter set + slippage from Stage 3) into a single atomic batch.
2. **Pre-state read.** Borrowable liquidity, current oracle prices (main + reserve), per-CM debt-limit utilisation, active LT-ramps.
3. **Simulation.** Apply the multicall against pre-state; compute post-state HF using `min(main, reserve)` for forbidden / safe-priced tokens.
4. **Gate checks.** HF exceeds the user-approved floor; actual leverage remains inside the Stage 3 tolerance; swap impact is within the approved budget; no material deviation flags.
5. **Calldata bundling.** Output ready-to-sign multicall bytes. Stage 5 must verify hash equality post-signing.

**Failure modes.** Stage 4 typically fails not because the thesis is wrong but because chain state shifted between Stage 2 (Analyze) and Stage 4 (Preview): borrowable liquidity dropped, utilisation rose, oracle drifted. Loop returns to Stage 3 (re-size or re-route), not Stage 2 (re-analyze).
