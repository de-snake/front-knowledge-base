# Credit Account management — reference

Drill sections referenced from [[Credit Account management]]. Each drill is a self-contained explanatory unit; the calling row carries only the verdict-level summary plus a wikilink. Topic names are flow-agnostic where possible; flow-agnostic curator and oracle drills live in [[Pool deposit - reference]].

## Drill — CA action-class palette

The CA Action Committee chooses among **8 first-class action types plus Emergency variants and bot-management actions** — distinct from Pool monitoring's 3-action palette (top-up / partial / full exit) because a leveraged isolated account has many more controls. The table below maps action class to thesis-verdict trigger, sizing logic, and route requirement.

| Action class | Trigger | Sizing logic | Route? |
| --- | --- | --- | --- |
| **add_collateral** | HF below user floor but thesis holds; user wants to fix safety without changing leverage exposure direction. | Amount needed to reach `hf_target = userThesis.hfFloor + safety_margin`. | No swap leg — direct collateral add. |
| **reduce_leverage** | HF eroding relative to the user floor; thesis weakened; or borrow-vs-yield spread compressing on flat prices. | Amount to repay to reach `userThesis.targetLeverage` or `safe_target_leverage`. | Optional — swap leg only if collateral has to be sold to repay. |
| **increase_leverage** | Thesis holds; user wants more exposure; HF clears floor with room. | Additional borrow under `maxLeverage(LT)` and `userThesis.hfFloor`. | Yes — entry-swap from underlying to target collateral. |
| **partial_exit** | Capital need or thesis weakened; user reduces position size without closing. | Largest size that doesn't cross `userThesis.hfFloor` at every step of the unwind multicall (intermediate HF check is non-trivial). | Yes — exit-swap on the withdrawn collateral fraction. |
| **full_exit** | Thesis broken or full reallocation. | Full unwind. | Yes — exit-swap on entire collateral. |
| **change_strategy** | Same base asset, better risk / yield available elsewhere; user moves to another strategy. | Exit current + open new in a single multicall (or two-step with safe intermediate HF). | Yes — both legs (exit + new entry). |
| **rebalance** | Within-position composition shift (e.g., USDe → USDC inside the same CA) without closing. | Source amount + destination token. | Yes — internal swap. |
| **claim_rewards** | Money-on-the-table push from Q2; matured `claimableAt` on delayed-withdrawal claims. | Claimable amount + matured timestamps. | No swap leg — direct claim. |
| **enable_bot** / **disable_bot** / **adjust_bot_threshold** | User wants automated management (partial-liquidation bot, deleverage bot) — or wants to disable / retune existing automation. | Bot-permission update — no funds movement. | No. |
| **emergency_add_collateral** | User emergency floor or projected floor breach. | Pre-filled amount to bring HF above the user-approved safety target; fast safety contract. | No swap leg. |
| **emergency_reduce_leverage** | User emergency floor or projected floor breach, no available collateral to add. | Pre-filled amount to repay; fast safety contract. | Optional swap leg if collateral has to be sold. |

**No Pool-monitoring-style "no Emergency" rule.** CA has Emergency. The closest analogue on the LP side (sudden bad-debt event detected via Q5) escalates to Partial / Full exit but still without Emergency's ≤ 2-clicks contract; CA Emergency does have the ≤ 2-clicks contract because liquidation is real-time and binary.

**Cross-strategy reallocation is out of scope here.** Closing one Credit Account to open another in a different strategy, base asset, or platform is the full-canonical-loop reallocation case (Discover → Analyze → Propose → Preview → Execute across strategies), not a within-CA action.

**Automation as an action class.** Per [[Personas and audience#CA operator (leveraged user)|Personas]] preferences, the user may want bot-managed risk control (e.g. "if HF drops below X, bot reduces leverage by Y%"). `enable_bot` / `adjust_bot_threshold` actions don't move funds at decision time but configure the on-chain authorisation that lets a bot signer act later. Stage 4 Preview for these actions checks the bot-permission scope; Stage 5 signs the permission update.

**Composite actions and fallback flows.** Some user intents map to multiple action classes executed sequentially or as a single multicall:

- **Add funds + increase leverage (composite scaling).** When the user is satisfied with the strategy and wants to scale exposure proportionally: `add_collateral` followed (in the same multicall) by `increase_leverage` to maintain target leverage. Stage 4 Preview gates on intermediate HF.
- **Step-by-step unwind (when full close fails).** If `full_exit` Preview fails — usually due to slippage, intermediate HF, or `minDebt` boundary — the fallback flow is `reduce_leverage` → `partial_exit` → `full_exit` (or `repay_debt → withdraw → close`) executed across multiple Stage 6 → Stage 3 cycles. Each step lowers leverage / debt enough that the next step is feasible.
- **System-constraint fallback.** When a primary action fails because of system limits (`maxDebt` reached, `borrowableLiquidity` exhausted, partial-exit gated to `minDebt`, forbidden-token mask blocks a swap leg), the user routes to the available safe-action set: typically `add_collateral` (no debt change), `reduce_leverage` (debt down), or `claim_rewards` (no funds movement). The Action Committee surfaces the fallback set when the primary preview fails; the user picks among them.

These composite / fallback flows aren't first-class action classes in the `ActionDecision.action_class` enum — they're orchestrations across multiple `ActionDecision` cycles. The agent surfaces them as a single "user intent" but executes through the per-action-class atomic transitions.

## Drill — Emergency mode contract

**When fires.** Stage 6 Q1 breaches the user-approved emergency condition, or a collateral-specific blocker makes ordinary management unsafe. `MonitoringSnapshot.is_emergency = true`.

**Stage flow when Emergency fires.**
- **Stage 6 → Stage 3 direct.** Stage 2 (focused re-run) is **skipped**. The thesis is pre-known: "reduce risk now." Re-running Analyze loses time the position cannot afford.
- **Stage 3 collapses to ≤ 2-clicks.** A single concrete proposed action (`emergency_add_collateral` OR `emergency_reduce_leverage`) with pre-filled amount; HF floor enforced in the preview; before / after preview surfaced on a single screen. No multi-candidate decision; no portfolio dedup; no cross-position rebalance check.
- **Stage 4 Preview gate is stricter.** Post-action HF must clear `pre_action_hf + δ` (the action must improve safety, not merely change leverage). Deviation flags abort.
- **Stage 5 Execute.** HITL required for first-time Emergency users (cannot delegate to a bot the first time). On subsequent Emergency events, a pre-authorised emergency-bot can execute if the user has set it up via `enable_bot`.

**UX contract.** ≤ 2 clicks / tool calls from "awareness of danger" to "signed remediation." Screen surfaces a danger banner; agent surfaces a top-line danger line; single concrete proposed action with amount + before / after; one-click confirm.

**Sizing logic (pre-fill).**
- `emergency_add_collateral`: amount = `(userThesis.hfFloor + safety_margin × debt_value − twv) / dominant_collateral_LT_weighted_price`. Round up to a clean unit.
- `emergency_reduce_leverage`: amount = debt to repay so that resulting HF = `userThesis.hfFloor + safety_margin`. Use partial-liquidation-bot path if available (cheaper than user-initiated unwind); otherwise direct repay multicall.

**Follow-up.** After an Emergency action, the next Stage 6 call re-verifies HF. If HF still < `userThesis.hfFloor`, the agent surfaces a continuation prompt for the next Emergency action — possibly a different action class (e.g., first add collateral, then reduce leverage).

## Drill — HF movement attribution

**At Stage 6 Q1 (T2).** When HF moves between two monitoring checks, name the dominant cause.

### Ground the formula against canonical protocol semantics first

The agent's `HF = TWV / debt` model is **approximate**. Actual chain semantics may include additional terms — fee-accrual ordering, reserve-oracle invocation rules for safe-priced tokens, quota-interest compounding semantics, partial-liquidation-bot premium reservation, truncation in TWV per-token computation, edge cases where `TWV` and `debt` are computed with different price oracles (main vs reserve) on the same token. **Before computing attribution, the agent must ground the formula against the canonical protocol semantics.**

- Identify the current canonical source for the protocol's debt-and-collateral calculation.
- Pull the exact semantics for full collateral, safe pricing, accrued interest/fees, quota interest, and any reserve-price paths.
- Verify the model accounts for every term the chain applies. If the chain applies a term the model doesn't (for example, manager-level fees on top of borrow interest), extend the decomposition with the missing term.
- Re-ground every time the Gearbox Core version changes (semver bump or material PR landing) — the agent should not assume a stale model.

If grounding is skipped, the residual check below will catch the gap — but residual flags are reactive; grounding is preventive.

### Attribution sources to consider

The agent decomposes the HF delta across these sources. The list is categorical — the actual numerical decomposition is the agent's call given the grounded formula and the prev / curr state.

1. **Price movement.** Dominant collateral oracle price changed → TWV changed → HF changed. Continuous.
2. **Interest accrual.** Borrow rate × time → debt grew. Always negative, monotonic between checks.
3. **Quota accrual.** Per-token quota rate × time → debt-equivalent grew. Always negative, monotonic.
4. **LT schedule change.** Curator action or scheduled LT ramp reduces per-token `LT` → TWV recomputed. Discrete: occurs at specific `executedAt` events.
5. **Forbidden-token addition.** Held token becomes forbidden by curator configuration → safe pricing kicks in (`min(main, reserve)`) → exit HF lower than snapshot HF. Discrete: executed parameter-change event.
6. **Oracle update.** Reserve oracle updated and now diverges from main → safe-pricing exit HF lower. Discrete: oracle update event.
7. **Composition shift.** A held token's balance changed since last check (user-initiated rebalance / change_strategy, or partial liquidation by bot). Discrete or continuous depending on cause.

### Reasoning direction

HF is a non-linear ratio of TWV / debt; source decomposition is **path-dependent** in general — the order in which sources are stepped affects per-source marginal sizes. The agent's job is to:

1. Pull `agentLog.previousCheck.{...}` and current state.
2. Step each source from previous → current state, holding all-other-sources at previous values, recording each source's marginal ΔHF using the **canonical-semantics-grounded** formula.
3. Report the **largest absolute marginal contribution** as the dominant driver; flag any source materially close to it as co-dominant.
4. Compute the **residual** between sum-of-modeled-marginals and observed ΔHF. If the residual is non-trivial, the model has missed a term — the agent re-grounds against canonical protocol semantics, extends the source list, and re-runs.

The threshold for "non-trivial residual" and "materially close to dominant" are the agent's call given the magnitude of the move and the user's tolerance for false-positive re-grounding.

For large drifts (HF dropped substantially in one cycle), first-order linearisation may misattribute — the agent falls back to multi-step decomposition (split prev → curr into smaller substeps, sum marginals).

A formal Shapley-style attribution would be order-invariant but is overkill for a routine glance — first-order linearisation names the right cause most of the time. Reserve Shapley for forensic analysis when residuals or co-dominance are unsatisfying.

### Surfacing

- "HF dropped 0.08 since last check — most of the drop from interest accrual, with a smaller contribution from an oracle update on stETH; price contributed mildly positive; no LT changes; residual within tolerance."
- When **price** is dominant and HF still clears the user policy → label routine ("expected fluctuation").
- When HF becomes review-required or action-required → surface dominant cause regardless of magnitude.
- When **residual** is material → flag for re-grounding; surface raw deltas without claiming attribution.

**UX surface.** Q1 attribution sub-Q is T2 — fires only when (a) Q1 T1 verdict becomes review-required or action-required, OR (b) the user wants the breakdown on every check. Routine flat-HF check doesn't surface attribution.

## Drill — Q5 oracle drill triggers for CA

Q5 (oracle freshness / divergence / methodology) is excluded from the CA Glance set in [[Three-layer progressive disclosure]]; oracle is a **P2** CA loss vector in [[Personas and audience#CA operator (leveraged user)|Personas]]. All Q5 sub-Qs are T2; Q5 fires only when one of these triggers fires:

- **Q1 HF attribution flagged oracle as cause** — HF dropped and the dominant attribution component is "oracle update" or "safe-pricing kick-in." Q5 runs to identify whether a stale or methodology-shifted feed caused the drop.
- **Q1 attribution flagged composition shift** — a new token entered the position via rebalance / change_strategy. Q5 verifies the new token's oracle methodology is acceptable under user thesis.
- **User is sophisticated** — institutional, structured-product desk, or issuer-controlled-asset-aware. Persistent T2 coverage on every monitoring call.
- **Known structural oracle risk on held tokens** — position holds a token on a NAV / hardcoded / hybrid feed (cross-ref [[Pool deposit - reference#Drill — Oracle types and LP risk shapes|drill ↗]]). Different from Pool monitoring's *dominant collateral* trigger because CA holds collateral directly — every held token with structural oracle risk is in scope.
- **Issuer-controlled token's oracle methodology shifted** — issuer-controlled tokens often use NAV oracles updated by the issuer; methodology change (NAV → market, or vice versa) reshapes the cascade-vs-trap risk on this specific position.
- **Per-token oracle approaching staleness window** — for any held token, the feed age is approaching its staleness window under the user / product review policy. This is the **proactive trigger** that fires before liquidation — without it, Q5 is purely reactive and the user only learns about staleness after Q1 catches the realised loss.

When none fire, Q5 is skipped and `MonitoringSnapshot.verdicts.q5_oracle` is absent.

## Drill — Agent continuity log mechanics for CA

The agent maintains `agentLog.previousCheck.{...}` across monitoring sessions to drive delta-detection. Sunk-cost-blind by design — the log is the agent's record of *what changed since I last looked*, not of *what the user opened with*.

**Schema (CA-specific extensions over the LP shape).**
`previousCheck.{asOf, hf, totalValueUsd, twvUsd, totalDebtUsd, debtBreakdown, perTokenBalances, perTokenQuota, leverage, hfHistory, totalValueHistory, parameterSet, oracleSet, claimableAtTimestamps, frozenAccountIds, kycStatus, incidentIds, ...}` plus per-Q-specific extensions as needed.

**Per-Q delta usage.**
- Q1 — `previousCheck.{hf, perTokenBalances, oracleSet, parameterSet, leverage}` (HF movement attribution including composition shift; LT-ramp progression; leverage delta vs target).
- Q2 — `previousCheck.{totalValueUsd, debtBreakdown}` (account-value 30d vs sparkline; spread compression detection).
- Q3 — `previousCheck.asOf` (parameter-change log scoped to `executedAt > previousCheck.asOf`).
- Q4 — `previousCheck.{claimableAtTimestamps, expirationStatus}` (delayed-withdrawal queue progression; expiration creep tracking).
- Q5 (when fired) — `previousCheck.oracleSet` (oracle methodology change detection).
- Q6 — `previousCheck.{frozenAccountIds, kycStatus}` (issuer / eligibility delta).

**First-call rule.** First monitoring call after a CA is opened: deltas are vacuously zero; current state is recorded as `previousCheck` for next-call's delta. No special-cased "I just opened" branch — the position is monitored forward-looking from the first call.

**Emergency follow-up.** After an Emergency action confirms on-chain, Stage 5 updates `previousCheck` to reflect the post-action state; the next Stage 6 call computes deltas against the post-Emergency baseline (not the pre-Emergency one), so the agent doesn't double-count the Emergency action as further drift.

**Persistence boundary.** `previousCheck` is user / agent-side state. Gearbox-side systems provide current protocol state, history feeds, and execution constraints; they do not own or mirror the agent's continuity log. If an agent needs cold-start, institutional reporting, or multi-device continuity, the user or the user's representative persists and supplies that state.
