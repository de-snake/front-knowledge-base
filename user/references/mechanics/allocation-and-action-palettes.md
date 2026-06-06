# Allocation and action palette mechanics

Stable decision palettes for selecting allocation, monitoring actions, Credit Account actions, emergency handling, and route-selection classes. These mechanics explain the action vocabulary; they do not perform opportunity diligence.

## Drill — IC decision palette

**Source boundary.** This is a product allocation rubric, not a Gearbox protocol object. Protocol state can say which candidates are possible; the IC rubric decides whether to fund one, split, skip, or hold reserve.

The Investment Committee chooses among these palette items per allocation pass; the chosen palette item determines how the per-candidate `AllocationDecision` rows + the top-level `reserve_usd` are filled:

- **Fund one candidate fully** — pick the strongest memo and deploy all available capital there. `decisions[i].action = "deposit"` for the chosen candidate; all others `"skip"`. `reserve_usd = 0`.
- **Split across multiple candidates (diversification)** — distribute available capital across several memos. Multiple `decisions[i].action = "deposit"` with positive `amount_usd`. Total deployed ≤ available capital.
- **Skip individual candidates** — a candidate that's fine in isolation but redundant given existing positions, or where the memo's risk verdict is too soft. `decisions[i].action = "skip"`. Skipped candidates do not claim capital.
- **Hold capital back (reserve)** — deploy less than all available capital. `reserve_usd > 0`. The reserve is not a candidate-level decision; it is the residual at the `AllocationDecision` level.
- **No-op (full reserve)** — no candidate clears the bar today. All `decisions[i].action = "skip"`; `reserve_usd = available capital`.

**Invariant.** `total_deployed_usd + reserve_usd = available capital`. (Skipped candidates do not consume capital and are not counted in either side of the equation.)

## Drill — LP action-class palette

Pool monitoring Stage 3 (Action Committee) chooses among three action classes for one existing position. Distinct from Pool deposit Stage 3's [[Pool deposit#Stage 3 · Propose (Pool) — Investment Committee|Investment Committee]]: the IC allocates *across multiple candidates* with a reserve concept; the Action Committee acts on *one existing position* with no reserve.

- **Top-up.** `position_thesis_verdict: 'holds'` + LP wants more exposure → `action_class: "top_up"`. Sized within concentration cap.
- **Partial exit.** `position_thesis_verdict: 'weakened'` → `action_class: "partial_exit"`. Largest size that still clears Q2 exit-feasibility thresholds.
- **Full exit.** `position_thesis_verdict: 'broken'` → `action_class: "full_exit"`. Full `LpPosition.shares`.

**No Emergency action class.** LPs have no liquidation / HF danger in the LP role. The closest analogue is a sudden bad-debt event detected via [[Pool monitoring#Q5 · Is the bad-debt canary intact?|Q5]] → escalates to Partial / Full exit at high priority but still without the Emergency-mode ≤ 2-clicks contract.

**Cross-pool reallocation is out of scope here.** Closing one pool to open another is the full-canonical-loop reallocation case (Discover → Analyze → Propose → Preview → Execute across pools), not a within-pool action.

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

## Drill — CA action-class palette

The CA Action Committee chooses among **8 first-class action types plus Emergency variants and bot-management actions** — distinct from Pool monitoring's 3-action palette (top-up / partial / full exit) because a leveraged isolated account has many more controls. The table below maps action class to thesis-verdict trigger, sizing logic, and route requirement.

| Action class | Trigger | Sizing logic | Route? |
| --- | --- | --- | --- |
| **add_collateral** | HF below user floor but thesis holds; user wants to fix safety without changing leverage exposure direction. | Amount needed to reach `hf_target = userThesis.hfFloor + safety_margin`. | No swap leg — direct collateral add. |
| **reduce_leverage** | HF eroding relative to the user floor; thesis weakened; or borrow-vs-yield spread compressing on flat prices. | Amount to repay to reach `userThesis.targetLeverage` or `safe_target_leverage`. | Optional — swap leg only if collateral has to be sold to repay. |
| **increase_leverage** | Thesis holds; user wants more exposure; HF clears floor with room. | Additional borrow under `maxLeverage(LT)` and `userThesis.hfFloor`. | Yes — entry-swap from underlying to target collateral. |
| **partial_exit** | Capital need or thesis weakened; user reduces position size without closing. | Largest size that does not cross `userThesis.hfFloor` at every step of the unwind multicall (intermediate HF check is non-trivial). | Yes — exit-swap on the withdrawn collateral fraction. |
| **full_exit** | Thesis broken or full reallocation. | Full unwind. | Yes — exit-swap on entire collateral. |
| **change_strategy** | Same base asset, better risk / yield available elsewhere; user moves to another strategy. | Exit current + open new in a single multicall (or two-step with safe intermediate HF). | Yes — both legs (exit + new entry). |
| **rebalance** | Within-position composition shift (e.g., USDe → USDC inside the same CA) without closing. | Source amount + destination token. | Yes — internal swap. |
| **claim_rewards** | Money-on-the-table push from Q2; matured `claimableAt` on delayed-withdrawal claims. | Claimable amount + matured timestamps. | No swap leg — direct claim. |
| **enable_bot** / **disable_bot** / **adjust_bot_threshold** | User wants automated management (partial-liquidation bot, deleverage bot) — or wants to disable / retune existing automation. | Bot-permission update — no funds movement. | No. |
| **emergency_add_collateral** | User emergency floor or projected floor breach. | Pre-filled amount to bring HF above the user-approved safety target; fast safety contract. | No swap leg. |
| **emergency_reduce_leverage** | User emergency floor or projected floor breach, no available collateral to add. | Pre-filled amount to repay; fast safety contract. | Optional swap leg if collateral has to be sold. |

**No Pool-monitoring-style "no Emergency" rule.** CA has Emergency. The closest analogue on the LP side (sudden bad-debt event detected via Q5) escalates to Partial / Full exit but still without Emergency's ≤ 2-clicks contract; CA Emergency does have the ≤ 2-clicks contract because liquidation is real-time and binary.

**Cross-strategy reallocation is out of scope here.** Closing one Credit Account to open another in a different strategy, base asset, or platform is the full-canonical-loop reallocation case (Discover → Analyze → Propose → Preview → Execute across strategies), not a within-CA action.

When that reallocation candidate depends on a new token, issuer-controlled collateral, Pendle PT, or points/social return thesis, run the [asset investment diligence reference workflow](../workflows/asset-investment-diligence/README.md) before Stage 3 chooses an action.

**Automation as an action class.** Per [[Personas and audience#CA operator (leveraged user)|Personas]] preferences, the user may want bot-managed risk control (e.g. "if HF drops below X, bot reduces leverage by Y%"). `enable_bot` / `adjust_bot_threshold` actions do not move funds at decision time but configure the on-chain authorisation that lets a bot signer act later. Stage 4 Preview for these actions checks the bot-permission scope; Stage 5 signs the permission update.

**Composite actions and fallback flows.** Some user intents map to multiple action classes executed sequentially or as a single multicall:

- **Add funds + increase leverage (composite scaling).** When the user is satisfied with the strategy and wants to scale exposure proportionally: `add_collateral` followed (in the same multicall) by `increase_leverage` to maintain target leverage. Stage 4 Preview gates on intermediate HF.
- **Step-by-step unwind (when full close fails).** If `full_exit` Preview fails — usually due to slippage, intermediate HF, or `minDebt` boundary — the fallback flow is `reduce_leverage` → `partial_exit` → `full_exit` (or `repay_debt → withdraw → close`) executed across multiple Stage 6 → Stage 3 cycles. Each step lowers leverage / debt enough that the next step is feasible.
- **System-constraint fallback.** When a primary action fails because of system limits (`maxDebt` reached, `borrowableLiquidity` exhausted, partial-exit gated to `minDebt`, forbidden-token mask blocks a swap leg), the user routes to the available safe-action set: typically `add_collateral` (no debt change), `reduce_leverage` (debt down), or `claim_rewards` (no funds movement). The Action Committee surfaces the fallback set when the primary preview fails; the user picks among them.

These composite / fallback flows are not first-class action classes in the `ActionDecision.action_class` enum — they are orchestrations across multiple `ActionDecision` cycles. The agent surfaces them as a single "user intent" but executes through the per-action-class atomic transitions.

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
