# Credit Account management (CA × Monitoring)

**Persona:** [[Personas and audience#CA operator (leveraged user)]]
**Lifecycle scope:** Ongoing monitoring. Stage 6 of the canonical loop, with conditional back-edges to Analyze (Stage 2 of [[Credit Account opening]]) and Propose-tail (Stages 3–5) when the user decides to act. Initial open lives in [[Credit Account opening]].
**Session mode:** [[Entry points|Monitoring]] (Stage 6 entry; five branches — Confirmation, Analysis, Action, Exit, **Emergency** — per [[Entry points#Mapping to ownership-lifecycle session types]]). Unlike LP, the CA operator has an Emergency branch (HF danger zone) with a ≤ 2-clicks contract.
**Entry conditions:** Credit Account already open.

## Job statement

> **When I** own a leveraged Credit Account,
> **I want to** verify in under a minute that I'm safe, that I'm still making money, that nothing has changed on me, and that I know what I'd do if it had,
> **so I can** leave confident, or act on a specific corrective step without losing time searching for the right control.

## Cost of doing nothing

Unlike a passive pool deposit where "do nothing" is cost-free, a Credit Account bleeds value on autopilot:

| Cost | Description |
| --- | --- |
| **Borrow interest** | accrues continuously against the underlying debt. |
| **Quota interest** | accrues on enabled collateral. |
| **Unclaimed rewards** | rewards that aren't claimed don't compound. |
| **HF drift** | HF drifts as LT ramps execute and price moves. |
| **Expirable CMs** | expirable CMs creep toward forced exit. |

This flips the usual DeFi default: the "no action" baseline is a position slowly losing money. UI and agents should surface this — daily borrowing cost in plain language, unclaimed reward amount, days-to-expiration for expirable CMs — as a recurring gentle push, not a one-time disclosure.

## Functional / emotional / social dimensions

| Dimension | Description |
| --- | --- |
| **Functional.** | Detect material drift in safety (HF), returns (net APY), composition, governance, operational state, oracle health, and issuer-controlled collateral conditions when present. Surface a single concrete corrective action when drift is detected. Emergency path applies when the position breaches the user-approved danger condition or an asset-specific blocker makes ordinary management unsafe. |
| **Emotional.** | Sleep at night. When HF moves, know _why_ within one cycle — was it price, interest accrual, LT ramp, quota, forbidden-token safe-pricing kick-in, or oracle staleness — without digging. |
| **Social.** | For structured-product desks and funds: produce a defensible monthly check-in artefact (HF over time, attribution of HF deltas, parameter changes since last check, and issuer / eligibility state when relevant). |

## Stage 6 · Monitor (CA)

**Sub-jobs satisfied here:**
- **Glance at safety** — HF + plain-language label, liquidation-distance, time-to-liquidation, LT-ramp status, forbidden-tokens overlap, leverage delta. Visible in < 3 s. _(Q1)_
- **Glance at returns** — net APY (after borrow + quota + fees), total return in underlying + %, 30d account-value sparkline, unclaimed rewards push. Visible in < 5 s. _(Q2)_
- **Detect HF movement attribution** — when HF moves, name the cause: price, interest, LT ramp, quota, forbidden-token safe-pricing, oracle staleness, composition shift. _(Q1 T2)_
- **Detect borrow-vs-yield spread compression** — when borrow + quota costs are eating strategy yield. _(Q2 T2)_
- **Detect rule changes** — pending governance, recent parameter changes (LT, oracle, IRM, forbidden-tokens, CM pause). _(Q3)_
- **Detect operational state changes** — CM expiration creep, facade pause, pending delayed withdrawals, phantom-token positions. _(Q4)_
- **Detect oracle drift** — per-token freshness, divergence, methodology change. _(Q5 — drill, not default)_
- **Detect issuer-controlled collateral drift** (conditional) — own frozen status, eligibility / KYC validity, investor registry, redemption windows, and claim readiness when the position contains tokenized-security or other issuer-controlled collateral. _(Q6)_

**Exit gate:** every default Q (Q1–Q4; Q6 if the position contains issuer-controlled collateral) is acceptable under the user policy. A user-approved emergency floor, projected floor breach, frozen account, blocked redemption path, or other asset-specific blocker overrides the normal exit gate and sends Stage 6 directly to Stage 3, skipping broad Analyze. This is a product / agent routing policy for a dangerous account state, not a protocol-enforced state transition. Q5 (oracle, P2) is a drill — fires only when triggered. Threshold selection logic: [[Position risk and monitoring#Credit Account position management|Position risk and monitoring]].

**User's goal:** "Confirm in under a minute that I'm safe, still making money, and nothing has changed; act decisively if it has."

### Inputs (what enters this stage)

| Input | Description |
| --- | --- |
| Position id | Credit Account address / position handle — handle to the user's specific CA. The agent re-fetches the rich position state per call. |
| User thesis / criteria | Forward-looking gates: `hfFloor`, `hurdleRate`, `targetLeverage`, `holdHorizon`, `acceptedOracleMethodologies`, `holdHorizonRemaining`, and action / automation permissions. The thesis is the gate — entry-time conditions are not. If a required policy is missing, the agent marks the affected verdict as review-required instead of applying a hidden default. |

### Compute (agent-side)

**Default loop:** Q1 → Q4 every call (each addresses a P1 CA loss vector with at least one T1 sub-Q); Q6 every call only when the position contains issuer-controlled collateral. **Q5 is a drill** — oracle is P2 in [[Personas and audience#CA operator (leveraged user)|Personas]] and excluded from the [[Three-layer progressive disclosure|Glance set]], so all Q5 sub-Qs are T2 and Q5 fires only when triggered (see Q5 framing). **Emergency override:** if Q1 breaches the user-approved emergency condition, or Q6 detects a blocker such as own-account freeze or blocked redemption path, Stage 6 emits `recommended_next: 'emergency'` and skips Stage 2. Treat this as a product safety rule: the protocol exposes the account state; the agent chooses routing, copy, and the fastest safe action target. Session-type refinement (Confirmation / Analysis / Action / Exit / Emergency) follows the verdict mix per [[Entry points#Mapping to ownership-lifecycle session types]].

**Data sources beyond the inputs.**
- **Position current state** — backend / Gearbox MCP, re-fetched per call: health factor, total value, TWV/debt, debt breakdown, token balances/quotas, leverage, HF history, and total-value history (==note: TWV USD as a standalone display value seems unnecessary — useful for HF derivation but not for the user-facing surface==); executed-change feed; pending governance-change queue.
- **Agent continuity log** — user / agent-side state for delta detection: `agentLog.previousCheck.{asOf, hf, totalValueUsd, perTokenBalances, leverage, parameterSet, oracleSet, debtBreakdown, incidentIds, frozenAccountIds, claimableAtTimestamps, ...}`. Sunk-cost-blind by design — record of *what changed since I last looked*, not of *what the user opened with*. [[Credit Account management - reference#Drill — Agent continuity log mechanics for CA|drill ↗]] covers schema, per-Q usage, first-call rule, and the persistence boundary.

**Sub-Q scope tiers.** Same `T1` / `T2` system as [[Credit Account opening#Stage 2 · Analyze — CA due diligence|CA opening Stage 2]] — `T1` runs unconditionally inside a firing Q; `T2` fires when the user is sophisticated, a `T1` verdict flipped, or a known structural risk warrants persistent coverage.

Q-level deep-dives below.

### Q1 · Am I safe?

**Exit gate:** "HF clears user floor with margin; no LT ramp crosses floor in horizon; no forbidden-token overlap with held collateral that would force safe-pricing exit HF below floor; leverage within tolerance of target; HF movement since last check has a known cause. **Q6 own-frozen status (issuer-controlled collateral position only) overrides everything** — frozen = no action possible; safety cannot be acceptable if frozen, regardless of HF."

**Why this matters.** Liquidation is a P1 CA loss vector ([[Personas and audience#CA operator (leveraged user)|Personas]]) — the existential risk. Multiple drift drivers: collateral price moves, LT changes, interest accrual, quota accrual, oracle updates. Q1 is the **Glance verdict** ([[Three-layer progressive disclosure]]) — visible in < 3 s.

**Plain-language principle.** Every raw metric is paired with a translation. Examples:

| Raw | Translation |
| --- | --- |
| `HF 1.036` | "Low — your position liquidates if HF drops below 1.0." |
| `Liquidation Price 1.04 ETH+/WETH` | "Liquidation if ETH+ drops ~ 4 % vs WETH." |
| `Time to liquidation 38 mo` | "At current borrow-rate accrual with no price movement: ~ 38 months. Extrapolation." |

**What the agent computes:**

| Sub-question | Tier | What the agent does | Data retrieved |
| --- | --- | --- | --- |
| HF vs floor + plain-language label | T1 | Compare current `healthFactor` to the user-approved floor and emergency floor. If the floor is missing, show the raw HF and require policy review before recommending leverage changes. Pair raw HF with translation. | Current health factor; user HF floor / emergency floor if supplied. |
| Liquidation distance + time-to-liquidation | T1 | Liquidation price per dominant collateral ("X must drop Y % for liquidation"); time-to-liquidation under flat-prices interest accrual. | Current HF, TWV, and debt; per-token oracle prices; per-token LT; current borrow rate + quota rate. |
| LT-ramp status on held tokens | T1 | Active downward ramps on held collateral; project HF cross-date against the user-approved floor at flat prices. If cross-date falls inside the user horizon or no floor exists, escalate to focused analysis / review. | Per-token LT-ramp schedule (start, end, final LT); held collateral; user horizon and floor. |
| Forbidden-token overlap + safe-pricing | T1 | Overlap between forbidden-token status and held collateral. If overlap exists, recompute exit HF under safe pricing (`min(main, reserve)` for the forbidden token); flag if exit HF < floor. | Forbidden-token status; held-token balances; main/reserve oracle prices. |
| Leverage delta vs target | T1 | Current leverage vs `userThesis.targetLeverage` and allowed drift tolerance. Price moves change effective leverage even with debt static. The HF attribution sub-Q below catches the upstream cause; this row catches "is my strategy still my strategy" independent of HF. | Current leverage; target leverage; user drift tolerance if supplied. |
| HF movement attribution since last check | T2 | Decompose HF delta across price / interest / quota / LT change / forbidden-token / oracle / **composition shift** (a held token's balance changed since last check). Surface the dominant driver. Use the protocol's canonical HF calculation as the grounding source before applying any simplified attribution model. [[Credit Account management - reference#Drill — HF movement attribution|drill ↗]] | Previous-check snapshot; current account state; canonical HF calculation source. |
| **Synthesis** | — | T1 verdict on HF, distance, ramp, forbidden overlap, and **leverage delta** drives the safety Glance. T2 attribution fires when the safety verdict changes or when the user wants the breakdown on every check. **Emergency override:** breach of the user-approved emergency condition or an action-blocking collateral state jumps directly to Stage 3 with `action_class: emergency_*`, skipping Stage 2. Drift (non-emergency) → back-edge to [[Credit Account opening#Q2 · How safe is my collateral? What could force liquidation?\|CA opening Q2]]. | — |

### Q2 · Am I making money?

**Exit gate:** "Net APY clears hurdle; account-value 30d trend acceptable; borrow-rate-vs-collateral-yield spread positive; unclaimed rewards visible (push to claim)."

**Why this matters.** Yield decay is a P1 CA loss vector ([[Personas and audience#CA operator (leveraged user)|Personas]]) — leverage amplifies decay. Distinct from Q1 (safety) — yield can compress to negative even with HF healthy. Q2 is the **second Glance verdict** — visible in < 5 s.

**What the agent computes:**

| Sub-question | Tier | What the agent does | Data retrieved |
| --- | --- | --- | --- |
| Net APY vs hurdle | T1 | `(collateralYield × leverage) − borrowRate − quotaRate − annualizedFees` vs `userThesis.hurdleRate` and any watch band the user supplied. If no hurdle exists, report net APY as analysis but do not classify it as acceptable. **Plain-language pair:** `Net APY 4.3 %` → "You are earning 4.3 % per year on your equity after costs." | Per-token `collateralYield.current`; `Pool.borrowRate.current`; per-token `quotaRate`; current leverage; user `hurdleRate`. |
| Account-value 30d trend (PnL sparkline) | T1 | Total return in underlying + %, 30d account-value series. ==30d account-value sparkline = PnL.== **Plain-language pair:** `Total return +2.1 % over 30d (≈ +$840 underlying)` → "Up 2.1 % since a month ago." | 30d daily account-value history. |
| Borrow-rate-vs-collateral-yield spread | T1 | If `borrowRate + quotaRate > collateralYield`, the position bleeds on flat prices — adding leverage makes it worse, not better. Evaluate against the user hurdle and current thesis. **Plain-language pair:** `Spread −0.4 %` → "Your strategy currently bleeds 0.4 % per year on flat prices — borrow + quota costs exceed collateral yield. Consider reducing leverage." | `Pool.borrowRate`; per-token `quotaRate`; per-token `collateralYield`. |
| Unclaimed rewards push | T1 | Claimable amount + attribution to the CA (including Merkl rewards that accrue to the owner wallet, not the CA itself). Surface as money-on-the-table — unclaimed rewards don't compound. | Per-CM rewards endpoint; Merkl rewards endpoint per owner wallet. |
| Net APY decomposition | T2 | Show why the spread is what it is — borrow-rate trend, quota-rate trend, collateral-yield trend over 30 / 90d. Triggered when Q2 T1 becomes unacceptable or review-required, or when the user asks for the breakdown. | 30 / 90d daily series for `borrowRate`, per-token `quotaRate`, `collateralYield`. |
| **Synthesis** | — | T1 verdict on net APY, account-value trend, spread, and rewards push drives the returns Glance. T2 fires when economics compressed — surfaces which leg of the spread is the cause. Drift → back-edge to [[Credit Account opening#Q1 · Will the economics survive?\|CA opening Q1]]. | — |

### Q3 · Has anyone changed the rules?

**Exit gate:** "Pending governance queue is empty or non-material on held tokens; recent parameter-change pace is acceptable under the user / mandate policy; no LT reductions or oracle changes pending on dominant collateral."

**Why this matters.** Silent curator changes is a P1 CA loss vector ([[Personas and audience#CA operator (leveraged user)|Personas]]) — read here from the change-feed angle. CA-specific severity: LT reductions and oracle changes drive HF directly (no price movement required). Deep-dive: [[Credit Account opening#Q5 · What could change between now and exit?|CA opening Q5]].

**What the agent computes:**

| Sub-question | Tier | What the agent does | Data retrieved |
| --- | --- | --- | --- |
| Pending governance queue | T1 | Pending Safe-TX / timelock items affecting this CM. Each item: classification (material vs cosmetic) + execution time. Material change queued within the user horizon requires review / action. ==if present== — surface only when non-empty. | pending governance-change queue filtered to this CM. |
| Recent parameter-change log | T1 | Material changes executed since `agentLog.previousCheck.asOf`. Evaluate frequency, clustering, and severity against the user / mandate change-tolerance policy. The user correlates LT reductions with HF movements (cross-ref Q1 attribution). | Executed parameter-change feed filtered to this CM since the previous check. |
| Material vs cosmetic classification | T2 | Apply CA opening Q5's change-classification table. LT reductions, oracle changes, IRM tweaks (esp. `Rslope2`), forbidden-token additions, **delayed-withdrawal enabled on a held token** (changes exit horizon), CM pause: all material with HF / economics / exit impact. ==could add our severity position on each point — is it critical or not?== | Per-item `eventType`, `parameter`, `oldValue`, `newValue`; classification logic from [[Credit Account opening#Q5 · What could change between now and exit?\|CA opening Q5]]. |
| **Synthesis** | — | T1 surfaces pending + recent at verdict-level. T2 fires when activity warrants per-item classification. Drift → back-edge to [[Credit Account opening#Q5 · What could change between now and exit?\|CA opening Q5]]. | — |

### Q4 · Are operational mechanics intact?

**Exit gate:** "CM not paused; expiration date (if expirable) leaves > 1 month margin or matches hold horizon; pending delayed withdrawals on schedule; phantom-token positions tracked with `claimableAt` visible; no abnormal CM mode (emergency-liquidator flag, loss-policy active)."

**Why this matters.** Two converging P1 loss vectors: **expiration** ([[Personas and audience#CA operator (leveraged user)|Personas]] — past expiration the position is liquidatable regardless of HF with reduced premium) and **limited enter / exit liquidity** (delayed withdrawal queues, phantom tokens that auto-withdraw via adapter on exit).

**What the agent computes:**

| Sub-question | Tier | What the agent does | Data retrieved |
| --- | --- | --- | --- |
| CM expiration creep | T1 (expirable CMs only) | Days remaining vs hold horizon and exit margin. Escalate when expiration can arrive before the user can safely exit; keep quiet when expiration is not present or clearly outside the user horizon. ==I would only display this info if facade is paused / expiration date exists and is soon== — keep quiet otherwise. | CM expiration timestamp; user hold horizon remaining. |
| Facade pause + emergency-liquidator status | T1 | Facade paused blocks ordinary operation. Emergency-liquidator flag signals abnormal CM mode without full pause. ==note: real-world scenario?== ==note: take from permissionless==. **Emergency state bundle** — facade paused + forbidden tokens affecting position + loss-policy status + emergency-liquidator active checked as a unit. | Facade pause status; emergency-liquidator status; loss-policy status; forbidden-token set. |
| Pending delayed withdrawals | T1 (fires if any in queue) | Per-token expected amount + `claimableAt` timestamp; surface a clear claim prompt when matured. Compare queue timing to the user horizon and planned action path; overdue or blocked claims require action / review. | Product withdrawal-status feed: supported withdrawal assets, current queue state, claim-ready assets, and blocking reasons. Backend wiring belongs in [[Data requirements and to-dos#Data requirements and to-dos]]. |
| Phantom-token positions | T1 (fires if any held) | List phantom tokens (staked Convex, Infrared vault, Midas redemption) — non-transferable position wrappers that auto-withdraw via adapter on exit. Track for exit planning. | Per-token phantom-status flag; per-token adapter set. |
| Partial-exit feasibility under `minDebt` | T1 | If `currentDebt − maxRepayInOnePartialExit < minDebt`, partial exit is **gated to zero or full exit** — the user's only choices are full unwind or no action. Surface this constraint at Stage 6 so it's not a Stage 3 sizing surprise. | Per-CM `minDebt`; current total debt; partial-exit sizing math from [[Credit Account opening#Q3 · Can I exit at size when I need to?\|CA opening Q3]] iterative-unwind. |
| Active bots audit | T2 | Active bots with permissions: expected = partial-liquidation bot. ==unexpected: unknown bot with `EXTERNAL_CALLS_PERMISSION`== — surface as anomaly for manual review. | Per-CA bot registry; bot permission scopes. |
| **Synthesis** | — | T1 catches operational state at verdict-level — quiet by default, surfaces only abnormal states or imminent expiration / queue maturity. T2 fires when bot registry has unexpected entries. Drift → back-edge varies: expiration / pause → [[Credit Account opening#Q4 · Who manages this CM, and is the envelope stable?\|CA opening Q4]]; delayed withdrawals → [[Credit Account opening#Q3 · Can I exit at size when I need to?\|CA opening Q3]]. | — |

### Q5 · Are oracles fresh? *(drill, not default)*

**Exit gate (when Q5 fires):** "Per-token oracle freshness within the relevant staleness window; main-vs-reserve divergence acceptable under the user thesis; no oracle methodology change for held tokens since last check that violates user thesis."

**Why this matters.** Oracle manipulation / staleness / configuration / safe-pricing is a **P2** CA loss vector ([[Personas and audience#CA operator (leveraged user)|Personas]]) — upstream cause of liquidation events when it fires. Q5 fires only when triggered — see [[Credit Account management - reference#Drill — Q5 oracle drill triggers for CA|drill ↗]]. Deep-dive in [[Credit Account opening#Q2 · How safe is my collateral? What could force liquidation?|CA opening Q2]] (oracle methodology + safe pricing).

**What the agent computes (when Q5 fires):**

| Sub-question | Tier | What the agent does | Data retrieved |
| --- | --- | --- | --- |
| Per-token freshness | T2 | `now − lastUpdate < stalenessWindow` for each held token. Treat age near or past the staleness window as a reason to review / act because the next update can change HF abruptly. | Oracle last-update timestamp and staleness window per held token. |
| Main-vs-reserve divergence | T2 | Compare main and reserve oracle prices per held token. Classify the divergence by its effect on exit HF and on the user floor, not by a universal percentage. | Main/reserve oracle prices per held token; user floor. |
| Oracle methodology change since last check | T2 | Detect any `oracleChanged` event affecting a held token between `agentLog.previousCheck.asOf` and now — main → reserve swap is permissionless without timelock. Triggers acceptability gate below. | Current oracle category/methodology; previous-check oracle set; executed oracle-change events. |
| Methodology acceptable under user thesis | T2 | For each held token, check current oracle category against `userThesis.acceptedOracleMethodologies`. Category shifts can flip cascade-vs-trap risk shape ([[Pool deposit - reference#Drill — Oracle types and LP risk shapes\|drill ↗]]). | Current oracle category/methodology; user accepted-methodology list. |
| **Synthesis** | — | Q5 doesn't run on every monitoring call — fires only on the triggers documented in the drill. When fired: sub-Qs run cheapest-first (freshness → divergence → methodology delta → acceptability). Drift → back-edge to [[Credit Account opening#Q2 · How safe is my collateral? What could force liquidation?\|CA opening Q2]] (oracle methodology + safe pricing). | — |

### Q6 · Is the issuer-controlled collateral branch drifting? *(conditional)*

**Exit gate:** "Own frozen status = unfrozen; eligibility / KYC valid where required; investor registry status = active; next redemption or claim path compatible with planned exit; eligible-liquidator depth acceptable under the user / product policy."

**Why this matters.** Issuer intervention is a **P1** CA loss vector for the CA operator ([[Personas and audience#CA operator (leveraged user)|Personas]]) whenever the Credit Account directly holds issuer-controlled collateral. Freeze, eligibility revocation, blocked redemption, or transfer restriction can prevent exit, rebalance, repayment, or liquidation even when HF looks acceptable. Deep-dive: [[Credit Account opening#Q2 · How safe is my collateral? What could force liquidation?|CA opening Q2]] issuer-controlled collateral lens.

**What the agent computes:**

| Sub-question | Tier | What the agent does | Data retrieved |
| --- | --- | --- | --- |
| Own frozen status | T1 | If frozen, **no action is possible** — no deposits, no withdrawals, no borrowing, no repaying, no liquidation. Critical check; frozen status sends Q6 to blocked / issuer-resolution handling regardless of HF. | Issuer / platform endpoint per CA address. |
| Eligibility / KYC validity | T1 | Check whether required eligibility remains valid and whether expiry is relevant to the user horizon. Expired / revoked eligibility can block receiving tokens back during withdrawal; resolve before exit. ==note: seems unnecessary in form of a value — would make sense as an alert / notification.== | Issuer / platform eligibility status. |
| Investor registry status | T1 | Investor-reassignment risk + current investor binding. Surface only on change since last check. | Issuer / platform investor-registry. |
| Next redemption window + notice deadline | T1 | When can the user actually convert the asset back to cash or claim proceeds? Notice deadline drives planned exits. | Issuer / platform redemption schedule. |
| Eligible-liquidator depth delta | T2 | Liquidator set contracted or below policy → user may sit liquidatable longer; expanded set is informational unless it changes the user thesis. | Issuer / platform eligible-liquidator endpoint. |
| **Synthesis** | — | T1 directly measures issuer / eligibility health on the user's own CA when the position contains issuer-controlled collateral. Frozen or blocked state overrides all other Qs because ordinary actions may be unavailable. T2 fires for sophisticated users or when an external regulatory event is known. Drift → back-edge to [[Credit Account opening#Q2 · How safe is my collateral? What could force liquidation?\|CA opening Q2]] issuer-controlled collateral branch. | — |

### Outputs (the hand-off)

`MonitoringSnapshot` — verdict per Q + drift list + recommended next step. CA-specific: includes `is_emergency` flag and richer `verdicts.q1_safety` payload (HF + plain-language + attribution).

```
MonitoringSnapshot {
  position_id, as_of,
  verdicts: {
    q1_safety: { verdict, hf, hf_label, distance, time_to_liq, ramp_status, forbidden_overlap, leverage_delta, attribution? },
    q2_returns: { verdict, net_apy, account_value_30d, spread, unclaimed_rewards },
    q3_governance,
    q4_operational,
    q5_oracle?,    // present only when Q5 fired (drill triggered); absent on default Confirmation calls
    q6_issuer_controlled?, // present only when held collateral has issuer / eligibility / redemption controls
  },
  drift_signals: string[],
  recommended_next: 'end' | 'analyze' | 'add_collateral' | 'reduce_leverage' | 'increase_leverage' | 'partial_exit' | 'full_exit' | 'change_strategy' | 'rebalance' | 'claim_rewards' | 'emergency',
  is_emergency: boolean,    // true when user emergency policy or an action-blocking collateral state triggers the fast safety path
  next_check_eta,
}
```

**Hand-off branches.**
- **All verdicts acceptable under user policy** → `recommended_next: 'end'`. Confirmation session ends in under a minute.
- **Any review / act verdict (non-emergency)** → `recommended_next: 'analyze'`. Hand off to [[#Stage 2 · Analyze (CA) — focused re-run|Stage 2]] for the focused CA-opening-Q re-run.
- **Thesis-broken or new-thesis intent** → `recommended_next: 'add_collateral' | 'reduce_leverage' | … | 'claim_rewards'`. Hand off to [[#Stage 3 · Propose (CA) — Action Committee|Stage 3]] (skipping Stage 2 — Action / Exit shape).
- **Emergency (`is_emergency: true`)** → `recommended_next: 'emergency'`. Hand off **directly to Stage 3 with the ≤ 2-clicks contract**, skipping Stage 2. The thesis is pre-known ("reduce risk now"); the constraint is speed. [[Credit Account management - reference#Drill — Emergency mode contract|drill ↗]].

No Stage-6 composite score is required. Stage 6 returns the per-question verdict mix and drift signals; Stage 2 is the Analyst pass that re-assesses the affected questions; Stage 3 is the Action Committee pass that aggregates those assessments into one action decision (`add_collateral`, `reduce_leverage`, `partial_exit`, `full_exit`, `claim_rewards`, `emergency`, etc.). HF and net APY remain first-class verdict inputs, not a separate portfolio-wide score.

## Stage 2 · Analyze (CA) — focused re-run

**Sub-jobs satisfied here:**
- **Re-validate the affected CA-opening Q(s)** based on which Stage-6 verdict flipped.
- **Decide thesis-holds vs thesis-broken** under current conditions.

**Exit gate:** focused re-run produces a verdict. If all conclude "still acceptable" → return to Stage 6 Confirmation cadence next cycle. If any concludes "no longer acceptable" → escalate to Stage 3 with `recommended_action`.

**User's goal:** "Re-run only what changed; don't redo the full pre-open due diligence."

### Inputs (what enters this stage)

| Input | Description |
| --- | --- |
| `MonitoringSnapshot` | From Stage 6. `drift_signals[]` and per-Q `verdicts` drive which CA-opening Q(s) get re-run. |
| User thesis / criteria | Carried — same forward-looking gates as Stage 6. |

### Compute (agent-side — focused re-run)

For each review-required or action-required Q-verdict in `MonitoringSnapshot.verdicts`, re-run the mapped CA-opening Q. Deep-dives live in [[Credit Account opening#Stage 2 · Analyze — CA due diligence|CA opening Stage 2]] and are not duplicated here.

| Monitoring drift | CA opening Q to re-run | Effect of the re-run |
| --- | --- | --- |
| Q1 safety drift (HF / ramp / forbidden / leverage delta) | [[Credit Account opening#Q2 · How safe is my collateral? What could force liquidation?\|Q2]] | Re-run HF feasibility + LT-ramp horizon + forbidden-mask + safe-pricing exit HF. If leverage drift is the dominant Q1 signal: also re-run [[Credit Account opening#Q1 · Will the economics survive?\|Q1]] (leverage compression compresses net APY). |
| Q2 returns drift (net APY / spread compression) | [[Credit Account opening#Q1 · Will the economics survive?\|Q1]] | Net APY decomposition + breakeven re-eval; IRM sensitivity T2 likely needed. |
| Q3 governance change | [[Credit Account opening#Q5 · What could change between now and exit?\|Q5]] | Re-classify executed / pending changes; pace lens updates curator-volatility read. |
| Q4 operational drift (expiration / pause / queue) | [[Credit Account opening#Q4 · Who manages this CM, and is the envelope stable?\|Q4]] + [[Credit Account opening#Q3 · Can I exit at size when I need to?\|Q3]] | CM operational envelope + exit-feasibility re-eval. |
| Q5 oracle drift (when Q5 fired) | [[Credit Account opening#Q2 · How safe is my collateral? What could force liquidation?\|Q2]] | Oracle methodology + safe-pricing exit HF re-run. |
| Q6 issuer-controlled collateral drift | [[Credit Account opening#Q2 · How safe is my collateral? What could force liquidation?\|Q2]] | Issuer / eligibility / redemption branch re-eval (freeze, eligibility, redemption, claim readiness). |
| **Synthesis** | — | Targeted Q re-run — no fresh Discover, no re-traversal of Qs that remain acceptable. Each re-run Q produces "still acceptable" or "no longer acceptable"; aggregated into `position_thesis_verdict`. **Emergency override does not pass through Stage 2** — emergency hands off directly to Stage 3. | — |

### Outputs (the hand-off)

```
FocusedAnalyzeReport {
  position_id, as_of,
  re_run_qs: Array<{ ca_opening_q, verdict, reasoning }>,
  position_thesis_verdict: 'holds' | 'weakened' | 'broken',
  recommended_action: 'none' | 'add_collateral' | 'reduce_leverage' | 'increase_leverage' | 'partial_exit' | 'full_exit' | 'change_strategy' | 'rebalance' | 'claim_rewards',
}
```

**Hand-off branches.**
- **`thesis_verdict: 'holds'`** → return to Stage 6 Confirmation cadence next cycle. Agent records re-run Q's clean verdict in `agentLog.previousCheck` so the same signal isn't re-flagged on the next call.
- **`thesis_verdict: 'weakened' | 'broken'`** → hand off to [[#Stage 3 · Propose (CA) — Action Committee|Stage 3]] with `recommended_action`.

## Stage 3 · Propose (CA) — Action Committee

**Sub-job (part 1 of Commit action):** decide the action class and size it. CA's action-class palette is much richer than LP's — see [[Credit Account management - reference#Drill — CA action-class palette|drill ↗]].

**Exit gate:** action class chosen, amount / target sized, route picked (if action involves a swap leg), rationale captured. Hand off to Stage 4. **Emergency exit gate:** ≤ 2-clicks contract — pre-filled amount, single concrete proposed action (Add Collateral or Reduce Leverage), HF floor enforced in preview.

**User's goal:** "Decide what to actually do — and in Emergency mode, do it fast."

### Inputs (what enters this stage)

| Input | Description |
| --- | --- |
| `FocusedAnalyzeReport` | From Stage 2 (or directly from Stage 6 in Action / Exit / **Emergency** session shapes — when the user arrives with a known action thesis and skips Analyze). |
| Position state | Current rich Credit Account state. |
| Available capital | Used for `add_collateral` / `increase_leverage` actions; carried in session config. |
| Emergency flag | `MonitoringSnapshot.is_emergency` — when `true`, Stage 3 collapses to ≤ 2-clicks contract. |

### Compute (agent-side — Action Committee)

The Action Committee for the CA operator chooses among **8 action classes plus emergency variants** — distinct from Pool monitoring's 3-action palette and from CA opening's IC (which allocates across new candidates with route selection).

| Decision class | Tier | What the agent does | Data retrieved |
| --- | --- | --- | --- |
| Action class selection | T1 | Map `position_thesis_verdict` + LP intent + Q-verdict mix to action class. [[Credit Account management - reference#Drill — CA action-class palette\|drill ↗]] | `FocusedAnalyzeReport.recommended_action`; user-level intent (top-up / reduce / claim / exit / change strategy). |
| Sizing per action class | T1 | For `add_collateral`: amount needed to reach target HF. For `reduce_leverage`: amount to repay to reach target leverage. For `increase_leverage`: additional borrow under maxLeverage(LT) and HF floor. For `partial_exit`: amount withdrawable without crossing HF floor **AND** without violating `minDebt` (residual debt ≥ `minDebt` post-action; otherwise the action degrades to `full_exit`). For `full_exit`: full unwind. For `claim_rewards`: claimable amount + matured `claimableAt` timestamps. For `change_strategy` / `rebalance`: source + destination + swap path. | Current HF, leverage, token balances, and debt; per-CM `minDebt`; user `targetLeverage`, `hfFloor`; per-token rewards / claimable schedule. |
| Route selection (swap-leg actions) | T1 | For `change_strategy`, `rebalance`, `partial_exit`, `full_exit` — pick adapter set, slippage tolerance, max-price-impact budget. Same shape as CA opening Stage 3 route selection. | Available adapters per CM; price-impact estimates at intended size. |
| Cross-position dedup | T2 | If the user holds correlated Credit Accounts or idle collateral on Gearbox, avoid over-correcting one position when a portfolio-level reallocation is cleaner — e.g., funding `add_collateral` (including Emergency) from another idle Credit Account's collateral rather than fresh outside capital. Flag the multi-CA reallocation case as cross-position work outside this flow. | Cross-position retrieval; idle collateral inventory. |
| Emergency-mode override | T1 (fires when `is_emergency`) | Collapse to ≤ 2-clicks contract: pre-filled `add_collateral` OR `reduce_leverage` with computed amount; HF floor enforced; surface a single concrete proposed action with before / after preview. [[Credit Account management - reference#Drill — Emergency mode contract\|drill ↗]] | `MonitoringSnapshot.is_emergency`, `verdicts.q1_safety`. |
| **Synthesis** | — | Output `ActionDecision { action_class, amount_*, target_*, route?, rationale, is_emergency }`. Action-class mapping, no-Emergency-for-LP contrast, automation interactions (bot enable / disable / threshold-tune), and cross-strategy reallocation out-of-scope rule: [[Credit Account management - reference#Drill — CA action-class palette\|drill ↗]]. | — |

### Outputs (the hand-off to Stage 4)

```
ActionDecision {
  position_id,
  action_class: 'add_collateral' | 'reduce_leverage' | 'increase_leverage' | 'partial_exit' | 'full_exit' | 'change_strategy' | 'rebalance' | 'claim_rewards' | 'enable_bot' | 'disable_bot' | 'adjust_bot_threshold',
  amount_usd?,
  target_leverage?,
  target_collateral?,
  route?: { adapter_set, slippage_bps, max_price_impact_bps },
  rationale,
  is_emergency: boolean,
  source: 'focused_analyze' | 'direct_user_intent' | 'emergency',
}
```

Hand off to [[#Stage 4 · Preview (CA) — Execution Desk pre-trade|Stage 4]].

## Stage 4 · Preview (CA) — Execution Desk pre-trade

**Sub-job (part 2 of Commit action):** validate the proposed action against current chain state by simulating the exact multicall.

**Exit gate:** simulation matches proposal. HF after action ≥ user floor (Emergency: HF after ≥ pre-action HF + δ); actual leverage / unwind matches target within tolerance; swap impact ≤ Stage-3 estimate; no deviation flags fire (`borrowableLiquidity dropped > 40 % since Stage 3`, `oracle drift`, `forbidden-token addition during simulation`); gas acceptable.

**User's goal:** "Will this exact multicall produce the position I expect, against current chain state?"

### Inputs (what enters this stage)

| Input | Description |
| --- | --- |
| `ActionDecision` | From Stage 3 — `action_class`, sizing, route, `is_emergency`. |
| Current chain state | Re-fetched per `position_id`. |

### Compute (agent-side — Execution Desk pre-trade)

Per `ActionDecision.action_class`, simulate the multicall via SDK router:

- **`add_collateral`** — `addCollateral` simulation; HF after; gas; deviation flags.
- **`reduce_leverage`** — `repayDebt` + (optional) `withdrawCollateral` multicall; HF after; effective leverage after; swap impact if a swap leg is needed; gas.
- **`increase_leverage`** — `borrow` + entry-swap multicall; HF after; swap impact; deviation flags (esp. `borrowableLiquidity`).
- **`partial_exit`** — partial unwind multicall (`repayDebt` + `withdrawCollateral` + optional swap); intermediate HF (must stay above floor at every step); swap impact; equity returned.
- **`full_exit`** — full unwind multicall (`repayAllDebt` + `withdrawAllCollateral` + close); total cost (swap + fees + gas); time to settle (incl. delayed withdrawals); equity returned.
- **`change_strategy`** — exit current strategy + open new strategy multicall; intermediate HF; total swap cost; HF after at new strategy.
- **`rebalance`** — internal swap (asset A → asset B inside the CA); HF after; swap impact.
- **`claim_rewards`** — `claim` multicall; check `claimableAt` matured; gas.
- **`enable_bot` / `disable_bot` / `adjust_bot_threshold`** — bot-permission update; no swap leg; gas only.

**Emergency mode:** Stage 4 returns the same `TransactionPreviewReport` shape but with `is_emergency: true` and an enforced HF-improvement gate — preview fails if post-action HF ≤ pre-action HF (the action must improve safety, not merely change leverage). **Exception for partial-liquidation-bot path:** when the bot path is selected (cheaper than user-initiated unwind), the bot reserves its premium as user loss in a single small step; the gate accepts a smaller HF improvement than δ if the action is bot-assisted. The check becomes `post_action_hf > pre_action_hf` (strictly greater) rather than `post_action_hf > pre_action_hf + δ`.

### Outputs (the hand-off to Stage 5)

```
TransactionPreviewReport {
  position_id, action_class, is_emergency,
  hf_after,
  effective_leverage_after,
  position_value_after_usd,
  equity_returned_usd?,         // exit only
  swap_impact_bps?,             // swap-leg actions
  intermediate_hf_min?,         // partial_exit / change_strategy multi-step
  time_to_settle?,              // exit incl. delayed withdrawals
  deviation_flags,
  gas_estimate_usd,
  warnings: string[],
  multicall_data,               // ready to sign
}
```

**On failure.** Loop returns to **Stage 3** for that action — re-size, lower leverage, change route. Thesis can still hold.

## Stage 5 · Execute (CA) — Execution Desk trade

**Sub-job (part 3 of Commit action):** sign and submit the previewed multicall, with an integrity gate. KYC-gated CMs use the compliance-gated execution path; bots are blocked at that layer. See [[Credit Account opening - reference#Drill — KYC-gated execution path|drill ↗]].

**Exit gate:** signed bytes match what Preview validated; multicall confirms on-chain.

**User's goal:** "Sign and submit, with a guarantee that the bytes I signed are the bytes Preview validated."

### Inputs (what enters this stage)

| Input | Description |
| --- | --- |
| `TransactionPreviewReport` | From Stage 4 — with validated multicall data. |
| Signer context | HITL wallet OR scoped bot signer. **Bot blocked for KYC-gated CMs** and for **Emergency** actions on first-time users. |

### Compute (agent-side — Execution Desk trade)

Same two modes as [[Pool deposit#Stage 5 · Execute (Pool) — Execution Desk trade|Pool deposit Stage 5]] / [[Credit Account opening#Stage 5 · Execute (CA) — Execution Desk trade|CA opening Stage 5]]:

| Mode | Description |
| --- | --- |
| **Human-in-the-loop** | Agent encodes the preview into a verifier flow; the human signs in their wallet. Verifier UI shows the same multicall data Preview produced — divergence breaks the integrity gate. Required for Emergency on first-time users. |
| **Bot** | Scoped bot signer executes within on-chain permissions. Bot must verify multicall hash matches Preview output before submitting. **Not available** for KYC-gated CMs or for Emergency actions on first-time users. |

### Outputs (the hand-off back to Stage 6)

```
TransactionConfirmation {
  position_id, action_class, is_emergency,
  txHash, blockNumber,
  hf_after_actual,
  effective_leverage_after_actual,
  position_value_after_actual_usd,
  equity_returned_actual_usd?,
  gas_paid_usd,
}
```

**Hand-off back to Stage 6.** Agent updates `agentLog.previousCheck` to reflect post-action state. Next monitoring cycle resumes Stage 6 from this baseline. **Emergency follow-up:** after an Emergency action, the next Stage 6 call should re-verify HF clears the user floor with margin; if not, the agent surfaces a continuation prompt for the next Emergency action.

## Edge cases & known failure modes

| Scenario | Description |
| --- | --- |
| **LT ramp cliff.** | User opens at HF 1.4 assuming stable LT. Active ramp reduces LT over 14 days; HF drops to 1.05 with no price movement. Caught by **Q1** (LT-ramp status T1 + HF attribution T2). User must deleverage or exit on schedule. |
| **Quota rate bleed.** | High quota rate on the target token means position loses money on flat prices. Breakeven was computed at current quota; quota rate rises; strategy turns uneconomical. Caught by **Q2** (net APY decomposition T2 fires when spread compresses). |
| **Safe-pricing kick-in.** | A held token becomes forbidden. Safe pricing (`min(main, reserve)`) applies on close; exit HF is materially lower than snapshot HF. Caught by **Q1** (forbidden-token overlap T1 + safe-pricing recompute) and **Q3** (forbidden-token-added classified material). |
| **Delayed-withdrawal clog.** | Position includes phantom token with 5-day unstaking queue. User needs to exit on day 2; only swap path available; price impact eats the thesis. Caught by **Q4** (phantom-token positions T1 + delayed-withdrawal compatibility note from CA opening Q3). |
| **CM expiration surprise.** | Expirable strategy reaches expiration; position is liquidatable regardless of HF with reduced premium. Caught by **Q4** (CM expiration creep T1) — surfaces at < 30 days remaining. |
| **Issuer freeze.** | Issuer/admin freezes the user's Credit Account through the issuer-controlled collateral branch. No exit, no rebalance, no repay. Caught by **Q6** (own frozen status T1) — overrides all other Qs. |
| **Eligibility / KYC revocation.** | Eligibility expires or is revoked; user may be unable to receive controlled tokens back during withdrawal and must resolve eligibility before exit. Caught by **Q6** (eligibility / KYC validity T1). |
| **Oracle staleness at the wrong moment.** | Token's oracle hasn't updated in > staleness window; next update drops price significantly and triggers immediate liquidation. Caught by **Q5** when triggered (per-token freshness T2) — but the Q5 drill triggers must fire first; in practice **Q1** (HF + attribution) catches the realised loss faster than Q5 catches the upstream cause. |
