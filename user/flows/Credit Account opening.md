# Credit Account opening (CA × Entry)

**Persona:** [[Personas and audience#CA operator (leveraged user)]]
**Lifecycle scope:** Entry. Stages 1–5 of the canonical loop. Stage 6 (ongoing) is owned by [[Credit Account management]].
**Session mode:** [[Entry points|Decision]] (full traversal Discover → Execute).

## Job statement

> **When I** have capital in a base asset and a target yield floor (with or without a specific collateral thesis),
> **I want to** amplify the return through leverage inside an isolated, adapter-gated account whose safety envelope (LT, oracle, quota, liquidation) is transparent and whose exit path is proven,
> **so I can** earn a leveraged net yield on whatever strategy clears my analysis bar — without having to commit to a specific collateral upfront — while keeping continuous visibility into what's moving my HF and what could force me out.

The user may arrive with a specific collateral in mind (LST, stablecoin carry, LP position, tokenised security) — but is equally well-served by "show me strategies on USD-stables that clear 8 % net APY at acceptable risk." Stage 1 surfaces candidates regardless; Stage 2's analysis is what gates the open.

## Functional / emotional / social dimensions

| Dimension | Description |
| --- | --- |
| **Functional.** | Run a leveraged strategy where every parameter that affects survival is queryable: LT, LT ramp, oracle type and staleness, quota rate, IRM curve, `minDebt`/`maxDebt`, delayed-withdrawal support, forbidden-tokens mask, pending governance. |
| **Emotional.** | Sleep at night. When HF moves, the user wants to know _why_ within one monitoring cycle — was it price, was it interest, was it LT ramp, was it a forbidden-token safe-pricing kick-in. |
| **Social.** | For structured-product desks and funds: explain the position (and its exit plan) to colleagues or investors, with receipts. |

## Stage 1 · Discover (CA)

**Sub-jobs satisfied here:**
- **Define the yield mandate** — user names asset class and floor APY. _(user-config — no backend surface)_
- **Locate candidate strategies** — 1–3 strategies that clear the floor on the right asset class surface in under a minute.

**Exit gate:** "I have a 1–3 shortlist of strategies that match my asset class and clear my floor APY."

**User's goal:** "Give me strategies whose base collateral and economics are in my target band — I'll pick what passes Stage 2's analysis."

Stage 1 is unified across pools and strategies — see [[Basic info and definitions#Canonical loop|Canonical loop]] (Stage 1 unification). This doc covers the strategy-candidate path; pool candidates flow into [[Pool deposit#Stage 1 · Discover (Pool)|Pool deposit Stage 1]].

### Inputs (what the user brings to this stage)

| Input | Description |
| --- | --- |
| Asset class | What the user holds and wants to deploy — USD-stable, ETH, BTC, EUR-stable, etc. The system maps class → set of underlying tokens; both pools and strategies on those underlyings are candidates. |
| Floor APY | Minimum acceptable net annualized rate (composite, including any leverage premium for strategies). The leverage / HF-floor / hold-horizon / position-size that satisfy this floor are **agent-derived at Stage 2** based on candidate properties — not user-supplied at Stage 1. |

### Compute (agent-side)

Backend hard filters on `chain`, `access` (`permissionless` / `kycRequired` / `agent-whitelist`), and the underlying / collateral token family. Soft filters / ranking on the candidate set use post-response data — same shape as [[Pool deposit#Stage 1 · Discover (Pool)|Pool deposit Stage 1]] with one strategy-specific extension (leverage-yield as the headline economic metric):

1. **Headline economics** — rank by composite or leveraged headline yield. For pools: `PoolOpportunity.yield.composite.current`. For strategies: `StrategyOpportunity.maxLeverageYield` at the strategy's `maxLeverage`. Surface `bestBaseYield` (un-leveraged floor) alongside for strategies — useful when CMs / curators differ across the same strategy.
2. **Operational health** — drop `isPaused`; flag `hasDelayedWithdrawal` (does not exclude).
3. **Sizing fit** — for strategies, flag when intended position size (typically agent-derived from available capital, not asked here) falls outside `[min(CM[minDebt]), max(CM[maxDebt])]`.
4. **Borrowable-liquidity headroom** — for strategies, flag low / zero `borrowableLiquidity` (would block leverage adjustments).
5. **Chain / token preference** — restrict to chain(s) and specific tokens the user actually holds.

==resolved_note: minDebt / maxDebt — different CMs in the same strategy have different bounds; the sizing-fit check uses `min(CM[minDebt])` and `max(CM[maxDebt])` across the strategy's CM set.==

==resolved_note: bestBaseYield — useful when the same strategy aggregates multiple CMs / curators; surface the spread to let the user pick the best CM at Stage 2.==

==resolved_note: 0 strategies / pools available on the user's chain — agent surfaces a bridge-or-swap suggestion at Analyze stage (only for same-asset bridging via a partner protocol; "Bridge through {partner}. Note that Gearbox does not operate this partner protocol service.").==

### Outputs (the hand-off to Stage 2)

A 1–3 candidate shortlist (mix of `PoolOpportunity.id[]` and `StrategyOpportunity.id[]`). For the strategy-side candidates that flow into this doc's Stage 2: identifier + carried floor APY. Per-candidate rich data is re-fetched in Stage 2; target leverage, HF floor, hold horizon, and position size are **agent-derived at Stage 2** as part of the per-candidate analysis.

**Hand-off to Stage 2.** Strategy identifiers + floor APY. Stage 2 owns its own retrieval and derives the rest.

## Stage 2 · Analyze — CA due diligence

**Sub-jobs satisfied here:**
- **Validate net economics** — net yield clears hurdle, breakeven < horizon, IRM curve not fragile to utilisation drift. _(Q1)_
- **Validate collateral safety + oracle** — asset properties, Gearbox params (LT / LT-ramp / forbidden / quota), oracle methodology, safe-pricing exit HF, structural-risk disclosure, issuer-controlled collateral branch when applicable. _(Q2)_
- **Verify exit feasibility** — price impact at size, iterative-unwind feasibility, borrowable-liquidity headroom, delayed-withdrawal compatibility, adapter routing constraints. _(Q3)_
- **Assess curator + CM envelope** — curator identity / track record, CM operational envelope (paused, expiration, debt-limit), compliance-gated routing when applicable, LT calibration discipline. _(Q4)_
- **Classify pending changes** — what's queued in governance, recent change pace; LT ramps and oracle changes carry the highest priority. _(Q5)_

**Exit gate:** every Q below answers Yes (or "acceptable to me"). The user has chosen a winner from the shortlist, or explicitly aborts.

**User's goal:** "Answer five questions with evidence before I open the position."

### Inputs (what enters this stage)

| Input | Description |
| --- | --- |
| Candidate identifiers | 1–3 `StrategyOpportunity.id[]` from Stage 1's hand-off. |
| Floor APY | Carried from Stage 1; gates Q1's net-APY check. |
| Risk / return tolerance | User- or mandate-supplied policy: `hfFloor`, `holdHorizon`, accepted oracle methodologies, and how much LT-ramp / leverage / liquidity risk the user is willing to carry. If policy is missing, the agent records a recommended policy and routes the decision to user review; it does not silently apply a default. |
| Available capital | The amount the user wants to deploy this session — feeds Q3 exit-price-impact at the candidate-specific position size. Per [[Personas and audience#CA operator (leveraged user)|Personas]] preference for minimalist user input, position size is normally `available capital` directly; sub-allocation across multiple strategies happens at Stage 3. |

### Compute (agent-side)

Per candidate, run Q1 → Q5. The agent **derives target leverage** per candidate as part of Q1 / Q2 analysis — picking a leverage that clears the `floorAPY` while staying inside `hfFloor` margin given the candidate's `LT`, oracle methodology, and LT-ramp schedule. Cross-candidate ranking happens at the end (highest net APY among acceptable candidates wins; ties broken by curator + CM safety scores).

**Scope tiers.** Same `T1` / `T2` system as [[Pool deposit#Stage 2 · Analyze — LP due diligence|Pool deposit Stage 2]]. CA-specific drills live in [[mechanics/README|mechanics index]]; flow-agnostic drills (oracle types, Steakhouse layers, curator pillars) are reused from [[mechanics/README|mechanics index]].

**Source boundary.** Protocol state tells the agent what the account can do; product policy decides whether that state is acceptable for this user. Keep debt limits, expiration, quotas, LT, and safe-pricing as observable risk inputs. Treat user suitability, route quality, warning thresholds, and final recommendation copy as product decisions.

Q1–Q5 deep-dives below.

### Q1 · Will the economics survive?

**Exit gate:** "Net APY (after borrow + quota + entry / exit friction) clears hurdle; breakeven < hold horizon; IRM curve not fragile to utilisation drift in T2 stress."

**Why this matters.** Yield decay is a P1 CA loss vector ([[Personas and audience#CA operator (leveraged user)|Personas]]) — leverage amplifies the gap between expected and realised yield. Liquidation via interest accrual is a secondary path: if borrow rate spikes (utilisation jump), interest can drag HF below floor without any price movement.

**What the agent computes:**

| Sub-question | Tier | What the agent does | Data retrieved |
| --- | --- | --- | --- |
| Net APY decomposition | T1 | `(collateralYield × leverage) − borrowRate − quotaRate − annualizedFees − amortizedExitFriction`. Compare to user `hurdleRate`. Gate fails if below. Show `quotaIncreaseFee` + total entry fees alongside (UX: ==Show: quotaIncreaseFee, Total fees==). | `StrategyOpportunity.maxLeverageYield`; `StrategyOpportunity.{borrowApy, collateralYield}.{current, 90dSeries}`; per-token `quotaRate`; `Pool.quotaIncreaseFee`; entry- and exit-swap impact estimates. ==note: showing oracle-based price might be a bad idea — we don't collect real market price; in Collateral details we might show real market price vs oracle price.== |
| Breakeven horizon check | T1 | `(entryCost + amortizedExitCost) / dailyNetYield`. Gate fails if breakeven > user's `holdHorizon`. Entry-swap impact on the underlying → collateral leg ==can be 2–3 weeks of yield== at moderate sizes. Exit cost matters: a "profitable" position must net out exit friction. ==note: is that true? example?== ==note: again, is this a reasonable concern to consider? does that happen?== | Aggregated `entryCost` (entry swap impact + `quotaIncreaseFee` + gas); estimated `exitCost`; `dailyNetYield` derived from net APY. |
| Utilisation headroom + borrow-rate trend | T1 | Current pool utilisation `U` + 30d trend; flag if pool is operating at or above `U_optimal` (typical 80–90 %) where slope2 kicks in — borrow rate is one LP withdrawal away from a step-up. Combined with leverage, small `borrowRate` moves are amplified into the user's net APY. Cross-ref [[#Q5 · What could change between now and exit?\|Q5]] IRM tweaks. | `Pool.{utilisation.current, utilisation.30dSeries}`; `Pool.IRM.{U1, U2}`. |
| IRM curve sensitivity | T2 | If +10 pp utilisation jump moves borrow rate >X bps, economics fragile — leveraged net APY can flip negative under modest pool-side shifts. Drill goes deeper than the headroom check above. [[credit-account-risk-controls#Drill — IRM curve sensitivity\|drill ↗]] | `Pool.IRM.{U1, U2, Rbase, Rslope1, Rslope2, Rslope3}`; current utilisation; sensitivity computation. |
| Liquidation-cost framing | T2 | Show **deleverage-bot info** instead of liquidation specifics — ==deleverage info seems much more appropriate than liquidation specifics since they rarely happen==. The bot prevents a bad outcome rather than describing one. Liquidation premium / discount values surfaced only when the user explicitly asks. | Deleverage-bot availability per CM; `liquidationPremium`, `liquidationDiscount` (per-CM, on demand). |
| **Synthesis** | — | T1 gates on net APY ≥ hurdle (incl. exit friction), breakeven < horizon, and utilisation-headroom margin. T2 fires when borrow utilisation is already elevated and leverage × IRM-slope makes the position fragile, or when the user is sophisticated and wants liquidation-cost detail. | — |

### Q2 · How safe is my collateral? What could force liquidation?

**Exit gate:** "Post-open HF clears floor at target leverage; no LT ramp crosses floor within hold horizon; oracle methodology fits the asset's market structure; safe-pricing exit HF acceptable; issuer-controlled collateral branch (if applicable) clears trust."

**Why this matters.** Multiple P1 CA loss vectors converge here: liquidation (HF drift, LT ramp, oracle move), collateral exposure (token-specific properties), issuer intervention (freeze, eligibility / KYC, redemption). Oracle is P2 standalone but is the upstream cause when liquidation fires unexpectedly.

**What the agent computes — four lenses:**

| Dimension | Lens | Tier | What the agent does | Data retrieved |
| --- | --- | --- | --- | --- |
| Asset properties | Asset | T1 | Issuer, asset type (native / wrapped / LST / LP / tokenized security / issuer-controlled / stablecoin / synthetic), native lock-up / withdrawal queue, underlying yield source, ==90d volatility==. | Per-token metadata; external (issuer docs, project pages); price history (90d daily). |
| HF + LT feasibility at target leverage | Gearbox config | T1 | Compute post-open HF at target leverage; compare it to the user-approved floor or mandate. If no floor exists, derive a recommended floor from asset properties and route the decision to review before Preview / Execute. `maxLeverage = 1 / (1 − LT)`. [[credit-account-risk-controls#Drill — Deriving safe HF margin from asset-specific risk\|drill ↗]] | Per-CM `LT`; user target leverage; user-approved or recommended `hfFloor`. |
| LT ramp horizon check | Gearbox config | T1 | If the LT schedule is moving downward: project final LT and the date HF would cross user floor at flat prices. Gate fails if cross-date < hold horizon. | Per-CM LT-ramp schedule: start, end, final LT. |
| Forbidden mask + delayed-withdrawal coverage | Gearbox config | T1 | Forbidden-tokens (current + pending) over the user's intended collateral set; delayed-withdrawal support per token as available withdrawal paths, expected queue time, and claim readiness. | Forbidden-token status (current + governance queue); product withdrawal-status feed. |
| Oracle methodology fit | Oracle | T1 | Per-token methodology fit for the Credit Account borrower side (no oracle type is "good" or "bad" in isolation — market can liquidate borrowers on temporary dislocation; hardcoded / NAV can protect borrowers during temporary dislocation but can hide persistent divergence from LPs); freshness vs staleness window; main-vs-reserve divergence within tolerance. Use the mechanics drill for simple feeds and the [oracle analysis workflow](../references/workflows/oracle-analysis/README.md) for composite, bounded, ERC4626, Curve TWAP, Pendle, or main/reserve setups. | Oracle methodology, freshness, staleness window, and main/reserve prices. |
| Safe-pricing exit HF | Oracle | T1 | Compute exit HF under `min(main, reserve)` per held / planned-held token. Gate fails if exit HF < user floor — this is the worst-case exit valuation per [[Basic info and definitions#Credit Account vocabulary\|Safe pricing]] and applies anytime a held token becomes forbidden, has delayed-withdrawal disabled, or close happens at the curator's discretion. | Main/reserve oracle prices per held token; per-CM safe-pricing rule. |
| Oracle 90d history | Oracle | T2 | Recent anomalies, historical main + reserve daily — main for most cases, check main + reserve on partial withdrawal. ==note: showing oracle-based price might be a bad idea. we do not collect real market price. In Collateral details we might show real market price vs oracle price.== | External daily oracle history. |
| Structural risk disclosure | Structural | T2 | Bad-debt-socialisation note, withdrawal-queue mechanics, expiration mechanic per CM. Borrow-rate-history from Q1 also a liquidation signal — extreme rate spikes can liquidate via interest accrual. [[credit-account-risk-controls#Drill — Structural risk taxonomy\|drill ↗]] | Per-CM expiration + delayed-withdrawal config; cross-ref Q1 `borrowApy.90dSeries`. |
| Issuer-controlled collateral branch | Platform (conditional) | T1 | If the collateral is a tokenized security, issuer-controlled asset, redemption-window asset, or otherwise compliance-gated asset, check transfer restrictions, freeze authority + capability, eligibility state, investor reassignment risk, eligible-liquidator depth, redemption / claim timing, and secondary-market liquidity. If issuer or eligibility state is missing, do not treat the collateral as ordinary liquid collateral. [[credit-account-risk-controls#Drill — issuer-controlled collateral branch\|drill ↗]] | Issuer / platform endpoint per CM or asset program; product data feed for eligible-liquidator depth and redemption state. |
| Per-token 3-layer risk profile | Steakhouse | T2 | Asset / Platform / Market layer pillar grades. [[token-and-curator-risk#Drill — Per-token 3-layer risk profile (Steakhouse)\|drill ↗]] | Curator / Credora / Steakhouse external publications; per-token issuer attestations. |
| **Synthesis** | — | — | T1 across the lenses gates the open: HF feasibility, LT-ramp horizon, oracle methodology fit + safe-pricing exit HF, and any collateral-specific branch. T2 adds structural-historical context for sophisticated users or when a T1 verdict is borderline. The dominant-risk lens varies per asset class — for LSTs it is oracle methodology + depeg history; for issuer-controlled collateral it is eligibility / freeze / redemption state; for LP tokens it is underlying-component risk + DEX liquidity. | — |

### Q3 · Can I exit at size when I need to?

**Exit gate:** "Price impact at position size acceptable today and across 90d worst; iterative-unwind feasible without violating `minDebt`; borrowable-liquidity leaves headroom for at least one leverage adjustment; delayed-withdrawal queues compatible with hold horizon."

**Why this matters.** Limited enter / exit liquidity is a P1 CA loss vector ([[Personas and audience#CA operator (leveraged user)|Personas]]). The user can only route through CM-approved adapters, not the full DEX market — so adapter-set composition is the gate.

**What the agent computes:**

| Sub-question | Tier | What the agent does | Data retrieved |
| --- | --- | --- | --- |
| Exit price impact at position size | T1 | Adapter-accessible liquidity at exit; current + 90d worst slippage. Compare to entry-swap impact (Q1) — exit is rarely cheaper than entry. | Adapter set per CM; DEX subgraphs / adapter route quotes at the user's intended position size. |
| Iterative-unwind feasibility | T1 | Can the user reduce size in steps without crossing `minDebt`? Floor: `unwoundDebt ≥ minDebt` at each step. | Per-CM `minDebt`; intended position size; partial-unwind step plan. |
| Borrowable-liquidity headroom | T1 | Post-open headroom for one round of leverage adjustment; flag if low or zero (==could be an alert if low or 0, otherwise redundant==). | `Pool.borrowableLiquidity` post-open. |
| Delayed-withdrawal compatibility | T2 | Fires if the strategy holds tokens with delayed-withdrawal queues (Convex / Infrared / Midas redemption). Queue duration vs hold horizon: a 5-day unstake at hold-horizon 7d leaves 2 days of margin — narrow. | Product withdrawal-status feed: supported withdrawal assets, expected queue duration, claim mechanism, claim readiness, and blocking reasons. If unavailable, mark delayed-withdrawal compatibility as an unresolved live-data gate. |
| Adapter routing constraints | T2 | Gearbox router may give worse offers than 1inch / CoW at certain sizes / asset pairs. Compare adapter route to external aggregator quote on a sample size; surface the spread. [[credit-account-risk-controls#Drill — Adapter routing constraints\|drill ↗]] ==note: when any operation happens (e.g. swap during account opening), we use our own router. Our router might provide worse swap offers compared to 1inch / CoWswap, for example. Idea: fetch DEXs and compare to our own router.== | Adapter route quote vs 1inch / CoW quote at sample sizes. |
| **Synthesis** | — | T1 gates on exit price impact, iterative-unwind, and borrowable-liquidity headroom. T2 fires when delayed withdrawals are present or when adapter-vs-aggregator routing spread is material. The dominant exit-risk concern varies — for LST collateral it's adapter-route depth at size; for delayed-withdrawal collateral it's queue duration vs horizon. | — |

### Q4 · Who manages this CM, and is the envelope stable?

**Exit gate:** "Curator clears the user's trust criteria; CM not paused; not near expiration for the user's horizon; no hostile pending governance; new-debt-per-block cap non-zero; compliance-gated routing, if present, is acceptable to the user."

**Why this matters.** Silent curator changes (P1) and expiration (P1) are two distinct loss vectors that converge at the curator + CM envelope level. The curator chose the parameters; the CM is the immediate operational container that can become un-borrowable, expirable, or paused.

**What the agent computes:**

| Sub-section | Aggregation | Tier | What the agent does | Data retrieved |
| --- | --- | --- | --- | --- |
| Curator identity & governance | best-of | T1 | Identity & legitimacy; decentralisation of authority; technical surface. ==note: add more info about the curator, e.g. from DefiLlama and info about bad debt — check other aggregators; maybe ChatGPT with weekly updates about incidents and bad debt.== [[token-and-curator-risk#Drill — Curator identity & governance\|drill ↗]] | `Curator.identity`; `Curator.governanceMechanism`; external (DefiLlama / GitHub / X / governance forums). |
| CM operational envelope | worst-of | T1 | Paused status, per-block borrow capacity (zero means no new borrows allowed → skip), current debt-limit utilisation, facade pause. [[credit-account-risk-controls#Drill — CM operational envelope\|drill ↗]] | CM operational state: pause status, per-block borrow capacity, current debt, debt limit, and facade pause. |
| CM expiration horizon | n/a | T1 (expirable CMs only) | For expirable CMs: `expirationTimestamp − now` vs `userThesis.holdHorizon + buffer`. Gate fails if expiration falls before horizon — forced exit at reduced premium is a known failure mode. The legacy decision-criterion 5 carries this as a top-level "good open" gate, and so does this row. | CM expiration timestamp; user hold horizon. |
| KYC-gated CM operational | conditional | T1 (compliance-gated) | Operations require compliance-gated execution; bot delegation is blocked; the user must remain in a human-in-the-loop management path. [[credit-account-risk-controls#Drill — KYC-gated execution path\|drill ↗]] | Per-CM compliance-gated execution flag; bot-delegation policy. |
| Operational track record | worst-of | T2 | Lindy, process maturity, transparency (`cumulativeBadDebtUsd`, `totalAumUsd`, prior incidents). [[token-and-curator-risk#Drill — Curator operational track record\|drill ↗]] | `Curator.{firstOperationDate, cumulativeBadDebtUsd, badDebtIncidents[]}`. |
| LT calibration discipline | n/a | T2 | Does curator's per-token LT match observable risk? Does `maxLeverage = 1 / (1 − LT)` align with the asset's true depeg / liquidation-cascade exposure? [[token-and-curator-risk#Drill — Curator design discipline\|drill ↗]] | `Pool.parameters` per-token LT; cross-ref Q2 per-token risk profiles. |
| **Synthesis** | — | — | T1 gates on identity (best-of pillar), CM operational envelope (worst-of), and KYC-gated routing (if applicable). T2 fires for sophisticated LPs or when a T1 verdict is borderline. The CM expiration check is binary for non-expirable CMs and a horizon-comparison for expirable ones. | — |

### Q5 · What could change between now and exit?

**Exit gate:** "Pending governance acceptable; recent change pace acceptable; no LT ramp scheduled that crosses HF floor within hold horizon; no oracle change queued for held tokens."

**Why this matters.** Same loss vectors as Q4 read from the change-feed angle. CA-specific: LT changes and oracle changes are P1-equivalent severity (drive liquidation directly), distinct from Pool deposit Q5 where LT-ramps are one of several material change types.

**Changes the agent classifies — material gates the open; cosmetic / stable changes are noted but don't gate.**

| Change type | Classification | Re-evaluates / effect | Scope | Source signal |
| --- | --- | --- | --- | --- |
| LT reduced (immediate) | material | [[#Q2 · How safe is my collateral? What could force liquidation?\|Q2]] HF feasibility — direct HF impact. | T1 | LT-parameter change signal |
| LT ramp scheduled | material | [[#Q2 · How safe is my collateral? What could force liquidation?\|Q2]] LT-ramp horizon — HF drops on schedule with zero price movement. | T1 | LT-schedule change signal |
| Forbidden-token added on a held collateral | material | [[#Q2 · How safe is my collateral? What could force liquidation?\|Q2]] safe-pricing — exit HF computed under `min(main, reserve)` for the forbidden token. Historical example: rsETH was previously added; the curator may forbid borrowing against rsETH later, which shrinks the user's exit routes. | T1 | Forbidden-token update |
| Delayed-withdrawal enabled on a held token | material | [[#Q3 · Can I exit at size when I need to?\|Q3]] — exit horizon shifts; queue duration vs hold horizon must be re-checked. Distinct from a forbidden-token addition: the token is still usable but exit timing changes. | T1 | Withdrawal-path update |
| Oracle changed for a held / dominant token | material | [[#Q2 · How safe is my collateral? What could force liquidation?\|Q2]] methodology fit — main → reserve swap is permissionless without timelock. | T1 | Oracle-methodology update |
| Token quota raised approaching saturation | material if approaches limit | [[#Q1 · Will the economics survive?\|Q1]] economics — quota rate increases are passed through to the user. | T1 | Quota update |
| IRM tweaks (especially the steep part of the curve) | material | [[#Q1 · Will the economics survive?\|Q1]] IRM sensitivity — borrow rate spike risk. | T1 | Rate-model update |
| CM paused | material | [[#Q3 · Can I exit at size when I need to?\|Q3]] — exit blocked while paused. | T1 | CM pause update |
| Liquidation-premium / -discount changed | material | [[#Q2 · How safe is my collateral? What could force liquidation?\|Q2]] liquidation haircut — affects worst-case loss size. | T2 | Liquidation-terms update |
| LT raised | info-only | not gated | info | LT-parameter change signal |
| Curator metadata updates | info-only | not gated | info | Curator-profile update |
| **Synthesis** | — | Two lenses. **Pace** — frequency and clustering of material changes relative to the user's horizon and change-tolerance policy. **Queue** — pending changes evaluated against thesis. LT ramps and oracle changes carry the highest CA-specific severity because they can affect HF without price movement. ==note: severity should be policy-backed, not a universal fixed threshold.== | — | — |

> Все это непонятно и требует пояснений на примере

**Retrieval contracts.** Executed CM-change feed (filtered by CM, fields per the `Event source` column) drives the Pace lens; pending governance-change queue drives the Queue lens; CM change-frequency summary is a new aggregate to add (counts by change type over 30d / 90d / 365d).

### Outputs (the hand-off to Stage 3)

Per-candidate `ResearchMemo` — same contract as the LP side, with CA-specific fields.

```
ResearchMemo {
  candidate_id, candidate_name,
  recommendation: "strong" | "acceptable" | "risky" | "reject",
  one_liner,
  profit: { net_apy, apy_decomposition, breakeven_days, irm_sensitivity_score },
  risk: { summary, hf_at_target_leverage, lt_ramp_horizon, oracle_health, exit_feasibility, curator_trust, pending_changes, issuer_controls? },
  constraints: { min_position_usd, max_position_usd, max_leverage, hf_floor_required },
}
```

==note: overall risk score / cross-protocol comparable rating — Credora? или где еще его брать==

Each evidence field is a **computed summary backed by raw numbers, not a label** (per the staged-agent-architecture memo standard).

**Hand-off to Stage 3.** `ResearchMemo[]` — array of memos, one per analyzed candidate.

## Stage 3 · Propose (CA) — Investment Committee + Route Selection

**Sub-jobs satisfied here:**
- **Allocate across the analyzed candidates** — fund / skip per memo, sized within `[minDebt, maxDebt]` and concentration cap.
- **Select target leverage** — under `maxLeverage(LT)` and above HF floor at target.
- **Select entry route** — adapter set, slippage tolerance, max-price-impact budget for the entry swap. CA-specific extension over Pool deposit Stage 3 (where route is trivial).
- **Commit allocation** — output `AllocationDecision[]` with `reserve_usd` for any held-back capital.

**Sub-job (part 1 of Commit position):** allocate across the analyzed candidates AND select the entry route (swap leg + multicall assembly).

**Exit gate:** "I have an allocation decision per candidate (deploy with target leverage + route, or skip), plus a reserve. Total deployed + reserve = my available capital. The route is chosen and slippage tolerance set."

**User's goal:** "Decide what to actually open, what target leverage, which route, and how much capital to hold back."

### Inputs (what enters this stage)

| Input | Description |
| --- | --- |
| Per-candidate research memos | `ResearchMemo[]` from Stage 2 — each carries an agent-derived target leverage and HF margin per candidate. |
| Available capital | Total amount the user wants to deploy this session. |
| Risk / return tolerance | Session-level config (`hfFloor`, `holdHorizon`, accepted oracle methodologies) — same as carried into Stage 2. The IC re-confirms target leverage per funded candidate against these gates and may adjust if cross-candidate diversification or sizing constraints shift the math. |

### Compute (agent-side — IC + Route Selection)

The agent acts as an Investment Committee with a **route-selection mandate** absent in Pool deposit (Pool deposit defers route to Stage 4 because the wallet → underlying → pool path is trivial; CA opening's underlying → collateral via adapter set is non-trivial — zaps, multi-hop, slippage budget).

| Decision class | Tier | What the agent does | Data retrieved |
| --- | --- | --- | --- |
| Per-candidate fund / skip | T1 | Classify each `ResearchMemo` → `open_ca` / `skip` based on risk verdict + capital availability + user's already-open positions. | `ResearchMemo[]`; available capital; current portfolio state. |
| Sizing per funded candidate | T1 | Within `[minDebt, maxDebt]`, available capital, and per-CM concentration cap. ==note: add info about credit manager potential / suggested== | Per-candidate `min_position_usd` / `max_position_usd` / `max_leverage` from memo; available capital. |
| Target-leverage selection | T1 | Below `maxLeverage(LT)`; post-open HF > user floor; check that net APY at chosen leverage still clears hurdle. | Per-candidate `max_leverage`, `hf_floor_required`; user thesis. |
| Route selection | T1 | Adapter set, slippage tolerance, max-price-impact budget for the entry swap (underlying → target collateral). Stage 3 sets the user-approved budget; Stage 4 gates on `simulated swap impact ≤ budget`. [[allocation-and-action-palettes#Drill — IC decision palette + route selection\|drill ↗]] | Available adapters per CM; price-impact estimates from Q3 retrieval; user / mandate slippage tolerance. |
| Cross-candidate diversification | T2 | Concentration / correlation budgets across the funded set. If the user has not supplied these budgets, surface the proposed budget for review instead of applying a hidden threshold. | User / mandate concentration policy; current portfolio state. |
| Existing-portfolio dedup | T2 | Reduce / skip candidates whose exposure overlaps existing positions. | Cross-position retrieval. |
| **Synthesis** | — | Output `AllocationDecision[]` per candidate with `route` field. Palette extends Pool deposit's IC palette with snake_case action values: `open_ca`, `adjust_leverage` (existing CA), `rebalance` (within-position composition shift), `skip`, `no_op`. Invariant: `total_deployed_usd + reserve_usd = available capital`. [[allocation-and-action-palettes#Drill — IC decision palette + route selection\|drill ↗]] | — |

> Вот тут непонятно: если мы изначально подбирали стратегии под доступные балансы на кошельке, то какие могут быть варианты?

### Outputs (the hand-off to Stage 4)

```
AllocationDecision {
  decisions: Array<{
    candidate_id,
    action,                    // "open_ca" | "adjust_leverage" | "rebalance" | "skip"
    amount_usd,
    target_leverage,
    target_collateral,
    route: { adapter_set, slippage_bps, max_price_impact_bps },
    rationale,
  }>,
  total_deployed_usd,
  reserve_usd,
  committee_notes,
}
```

**Hand-off to Stage 4.** Stage 4 takes each `decision` with `action: "open_ca"` (or other active actions), simulates the multicall against current chain state, and produces calldata + warnings.

## Stage 4 · Preview (CA) — Execution Desk pre-trade

**Sub-jobs satisfied here:**
- **Simulate the multicall** against current chain state.
- **Gate on HF, leverage, swap impact, deviation flags** — pass / fail per `decision`.
- **Produce ready-to-sign multicall data** for each passing `decision`.

**Sub-job (part 2 of Commit position):** validate the `AllocationDecision` against current chain state by simulating the exact multicall — open CA + borrow + entry swap.

**Exit gate:** "Simulation matches proposal: HF after open ≥ the approved user floor; actual leverage remains inside the user-approved tolerance; swap impact ≤ Stage 3 max-price-impact budget; no material deviation flags fire; gas acceptable." If no user-approved safety floor or execution tolerance exists, Preview may simulate but cannot mark the package ready to execute.

**User's goal:** "Will this exact multicall produce the position I expect, against current chain state?"

### Inputs (what enters this stage)

| Input | Description |
| --- | --- |
| `AllocationDecision` | From Stage 3. |
| Current chain state | Re-fetched per `decision.candidate_id`. |

### Compute (agent-side — Execution Desk pre-trade)

For each `decision` with active `action`, simulate the multicall via SDK router and collect:

- **Simulated HF after open** — gate: HF exceeds the user-approved floor. If the floor is missing, Preview reports the simulated HF but requires user review before Execute.
- **Position value (USD)** — sanity check against proposal sizing.
- **Actual leverage** — may differ from target due to swap impact. Compare the result to the Stage 3 leverage tolerance and max-price-impact budget; do not classify it against a hidden default.
- **Swap impact (bps)** — compare to entry-cost estimate from Analyze. Significantly worse = abort.
- **Token balances after open** — full composition post-open.
- **Deviation flags** — material drops in borrowable liquidity since Analyze, HF below user floor, or swap impact worse than the Stage 3 budget.
- **Gas estimate (USD).**
- **Warnings array** — free-text UX strings.
- **Multicall data** — ready to sign.

[[credit-account-risk-controls#Drill — Multicall preview mechanics|drill ↗]] covers the SDK router simulation surface and what each check is sensitive to.

### Outputs (the hand-off to Stage 5)

```
TransactionPreviewReport {
  candidate_id, action,
  hf_after_open,
  position_value_usd,
  actual_leverage,
  swap_impact_bps,
  token_balances_after,
  deviation_flags: { borrowable_liquidity_change_pct, hf_vs_floor, swap_impact_delta_bps },
  gas_estimate_usd,
  warnings: string[],
  multicall_data,           // ready to sign
}
```

**On failure.** If Preview fails for a candidate, the loop returns to **Stage 3** for that candidate (re-size, lower leverage, change route), not back to Stage 2 — the thesis can still hold even if execution-time parameters need adjustment.

## Stage 5 · Execute (CA) — Execution Desk trade

**Sub-jobs satisfied here:**
- **Sign and submit** each previewed multicall (HITL or scoped bot).
- **Verify integrity gate** — signed bytes match validated bytes.
- **Confirm post-open state** matches preview.

**Sub-job (part 3 of Commit position):** sign and submit each previewed multicall, with an integrity guarantee that signed bytes match validated bytes.

**Exit gate:** "Signed bytes match what Preview validated; the multicall confirms on-chain; post-open state matches the preview."

**User's goal:** "Sign and submit, with a guarantee that the bytes I signed are the bytes Preview validated."

### Inputs (what enters this stage)

| Input | Description |
| --- | --- |
| `TransactionPreviewReport[]` | From Stage 4 — each with validated multicall data. |
| Signer context | HITL wallet OR scoped bot signer. **For KYC-gated CMs:** execution uses the compliance-gated path, and bots are blocked — see [[credit-account-risk-controls#Drill — KYC-gated execution path|drill ↗]]. |

### Compute (agent-side — Execution Desk trade)

| Mode | Description |
| --- | --- |
| **Human-in-the-loop** | Agent encodes the preview into a verifier flow; the human signs in their wallet. Verifier UI shows the same multicall data Preview produced — divergence breaks the integrity gate. |
| **Bot** | Scoped bot signer executes within on-chain permissions. Bot must verify multicall hash matches Preview output before submitting. **Not available** for KYC-gated CMs — bot permissions are blocked by the compliance-gated execution path. |

### Outputs (the hand-off to Stage 6)

```
TransactionConfirmation {
  candidate_id, action,
  ca_address,                // newly opened Credit Account address
  txHash, blockNumber,
  hf_after_open_actual,
  actual_leverage_actual,
  position_value_actual_usd,
  gas_paid_usd,
}
```

**Hand-off to Stage 6.** A `TransactionConfirmation[]` per executed open. Stage 6 ([[Credit Account management]]) picks up monitoring from these confirmations. The agent records the post-open state as the initial `agentLog.previousCheck` for the new CA.

## Stage 6 · Monitor (handoff)

Ongoing monitoring is a separate, recurring job. See [[Credit Account management]].
