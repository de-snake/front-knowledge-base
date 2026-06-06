# Pool monitoring (LP × Monitoring)

**Persona:** [[Personas and audience#Pool LP (passive lender)]]
**Lifecycle scope:** Ongoing monitoring. Stage 6 of the canonical loop, with conditional back-edges to Analyze (Stage 2 of [[Pool deposit]]) and Propose-tail (Stages 3–5) when the user decides to act. Initial deposit lives in [[Pool deposit]].
**Session mode:** [[Entry points|Monitoring]] (Stage 6 entry; four branches — Confirmation, Analysis, Action, Exit — per [[Entry points#Mapping to ownership-lifecycle session types]]).
**Entry conditions:** position already exists.

## Job statement

> **When I** hold a Gearbox pool position,
> **I want to** confirm in under a minute that yield is holding, exit is still open, and nothing has silently changed in my exposure,
> **so I can** either leave reassured, or act deliberately before the change costs me money.

After the deposit is made, the LP spends the vast majority of their Gearbox time in this mode — checking that the thesis still holds. This is a separate, smaller job that recurs on every return visit.

## Functional / emotional / social dimensions

| Dimension | Description |
| --- | --- |
| **Functional.** | Detect material drift in yield, exit feasibility, exposure, governance, bad-debt canary, and oracle freshness within one monitoring cycle. Surface a single concrete corrective action when drift is detected. |
| **Emotional.** | Leave reassured most days. When something does move, want to know _why_ within one cycle — was it incentive expiry, utilisation rise, curator action, oracle staleness — without having to dig. |
| **Social.** | For institutional LPs: produce a defensible monthly check-in artefact (current verdict, why it changed, and the curator change log since last check). |

## Stage 6 · Monitor (Pool)

**Sub-jobs satisfied here:**
- **Glance at yield** — net APY visible in one view, broken into organic vs incentive, with a 30d trend line and the user's floor APY marked as the gate.
- **Glance at exit feasibility** — current utilisation vs the user's position size — "you can exit X % today." Withdrawal fee surfaced.
- **Detect yield drift** — composite APY drift vs floor; incentive layer expiry. _(Q1)_
- **Detect composition drift** — per-token quota composition today vs last check; new CMs added or existing ones materially expanded. _(Q3)_
- **Detect governance change** — pending Safe-TX / timelock items + historical parameter-change log. _(Q4)_
- **Detect bad-debt event** — share-price drop vs previous check (canary); insurance-fund balance delta. _(Q5)_
- **Detect oracle drift** — per-token freshness, main-vs-reserve divergence, methodology delta + acceptability gate. _(Q6 — drill, not default)_
- **Detect issuer-controlled collateral drift** (conditional) — frozen-accounts delta, frozen-debt delta, eligible-liquidator changes. _(Q7)_

**Exit gate:** every default Q (Q1–Q5; Q7 if issuer-controlled collateral is material) is acceptable under the user thesis. If any Q becomes review-required or action-required, the session escalates from Confirmation to a focused Analyze re-run on the affected [[Pool deposit#Stage 2 · Analyze — LP due diligence|Pool deposit Q]] (see [[#Back-edge · Analyze (focused re-run)|back-edge below]]). Q6 (oracle, P2) is a drill — it does not gate by default; it fires only when triggered. Threshold selection logic lives in [[Position risk and monitoring#Pool position monitoring|Position risk and monitoring]].

**User's goal:** "Confirm in under a minute that yield is holding, exit is still open, and nothing has silently changed in my exposure."

### Inputs (what enters this stage)

| Input | Description |
| --- | --- |
| Position id | `LpPosition.id` — handle to the LP's specific position. The agent re-fetches the rich position state (`shares, sharePrice, depositedUsd, currentValueUsd, ...`) per call. |
| User thesis / criteria | Forward-looking gates against which Q-verdicts are computed: `floorApy`, accepted oracle methodologies, accepted curator profile, comfort tolerances, hold horizon. Set at deposit time; carried session-to-session. The thesis is the gate — entry-time pool conditions are not. |

### Compute (agent-side)

**Default loop:** Q1 → Q5 every call (each addresses a P1 LP loss vector with at least one T1 sub-Q); Q7 every call if issuer-controlled collateral exposure is material. **Q6 is a drill** — oracle is P2 in [[Personas and audience#Pool LP (passive lender)|Personas]] and excluded from the [[Three-layer progressive disclosure|Glance set]], so all Q6 sub-Qs are T2 and Q6 fires only when triggered (see Q6 framing). Session-type refinement (Confirmation / Analysis / Action / Exit) follows the verdict mix per [[Entry points#Mapping to ownership-lifecycle session types]].

**Source boundary.** Pool/oracle state can show freshness, reserve divergence, share-price movement, utilisation, and current accepted collateral. Issuer freeze state, eligible-liquidator health, issuer updates, and regulatory context need issuer or indexer feeds; if absent, the UI should label them as unknown instead of protocol-confirmed.

**Data sources beyond the inputs.**
- **Pool current state** — backend / Gearbox MCP, re-fetched per call: `Pool.{availableLiquidity, utilisation, expectedLiquidity, sharePrice, insuranceFundBalance, quotedTokens[], parameters}`, recent executed-change feed, pending governance-change queue.
- **Agent continuity log** — user / agent-side state for delta detection: `agentLog.previousCheck.{asOf, sharePrice, insuranceFundBalance, parameterSet, oracleSet, quotaComposition, incidentIds, ...}`. Sunk-cost-blind by design — record of *what changed since I last looked*, not of *what the LP entered with*. [[agent-continuity-log#Drill — Agent continuity log mechanics|drill ↗]] covers schema, per-Q usage, first-call rule, and the persistence boundary.

**Sub-Q scope tiers.** Same `T1` / `T2` system as [[Pool deposit#Stage 2 · Analyze — LP due diligence|Pool deposit Stage 2]] — `T1` runs unconditionally inside a firing Q; `T2` fires when the LP is sophisticated, a `T1` verdict flipped, or a known structural risk warrants persistent coverage.

### Q1 · Am I earning what I expected?

**Exit gate:** "Composite APY clears the floor and the 30d trend is acceptable; any near-term incentive layer expiry is acceptable to the LP."

**Why this matters.** Yield decay is a P1 LP loss vector ([[Personas and audience#Pool LP (passive lender)|Personas]]) — silent erosion of the rate the LP signed up for is the loss. Monitoring catches the decay early; the deep-dive lives in [[Pool deposit#Q1 · Where does the yield come from, and is it sustainable?|Pool deposit Q1]]. The gate is forward-looking — what the LP would accept entering today, not what they entered with. Incentive-dependence (organic-alone-below-floor) was sized at entry inside Pool deposit Q1's yield-decomposition sub-Q; monitoring does not re-gate that, it only watches the durability of the incentive layers the LP is depending on.

**What the agent computes:**

| Sub-question | Tier | What the agent does | Data retrieved |
| --- | --- | --- | --- |
| Composite APY vs floor + 30d trend | T1 | Compare composite APY and 30d trend to the user floor and watch band. The 30d trend is a property of the pool series, anchored to the rolling window — not to the LP's entry. | `PoolOpportunity.yield.composite.{current, 30dSeries}`; `userThesis.floorApy`. |
| Incentive layer expiry | T2 | Per non-null-`expiry` or non-null-`referenceUrl` layer: read campaign expiry / renewal status. *Material* if disappearance would drop composite below floor before the LP's intended hold horizon. | `PoolOpportunity.yield.incentive: IncentiveLayer[]` each `{source, currentApy, expiry, referenceUrl}`; `userThesis.holdHorizon`; external campaign pages per `referenceUrl`. |
| **Synthesis** | — | T1 verdict on composite vs floor + 30d trend; T2 fires when an incentive layer is material AND has near-term expiry. Drift → back-edge to [[Pool deposit#Q1 · Where does the yield come from, and is it sustainable?\|Pool deposit Q1]] for fresh sustainability re-evaluation. | — |

### Q2 · Can I still exit at size?

**Exit gate:** "Current withdrawable liquidity covers the LP's position; utilisation 30d trend is flat or declining; no cascade- or trap-shape symptoms on dominant collateral."

**Why this matters.** Locked liquidity / blocked withdrawals is a P1 LP loss vector ([[Personas and audience#Pool LP (passive lender)|Personas]]) — a position can be solvent on paper but un-exitable when utilisation pins high. Deep-dive in [[Pool deposit#Q3 · Can I withdraw when I need to?|Pool deposit Q3]].

**What the agent computes:**

| Sub-question | Tier | What the agent does | Data retrieved |
| --- | --- | --- | --- |
| Withdrawable now vs my position | T1 | `(1 − U) × TVL` vs `LpPosition.currentValueUsd`. Compare withdrawable liquidity to the user position size and policy margin. Withdrawal fee surfaced alongside. | `Pool.{availableLiquidity, expectedLiquidity, utilisation, withdrawalFee}`; `LpPosition.currentValueUsd`. |
| Utilisation 30d trend | T1 | Trend vs 30d series. Evaluate direction and magnitude against the user horizon and exit policy. | `Pool.utilisation.30dSeries`. |
| Cascade- vs trap-shape symptoms on dominant collateral | T2 | Cross-ref the dominant token's current oracle category: NAV / hardcoded → trap symptoms (utilisation pinning without LP-run); market → cascade symptoms (withdrawal-vs-repayment race). [[oracle-and-liquidity-risk#Drill — Collateral-induced liquidity risk by oracle type\|drill ↗]] | Current oracle category/methodology for the dominant token; recent withdraw / liquidate / repay event mix. |
| **Synthesis** | — | T1 gates on withdrawable-vs-position + utilisation trend (the daily check). T2 fires when utilisation is rising or already elevated, to classify the rise as cascade or trap. Drift → back-edge to [[Pool deposit#Q3 · Can I withdraw when I need to?\|Pool deposit Q3]] for full 5-dimension re-eval. | — |

### Q3 · Is the pool still composed the way my thesis expects?

**Exit gate:** "Top-3 collaterals and quota composition unchanged since last check (or any change is acceptable under current thesis); no new CMs added that materially expand exposure; no per-token quota size changes that escalate the max-exposure ceiling."

**Why this matters.** Silent exposure changes by the curator is a P1 LP loss vector ([[Personas and audience#Pool LP (passive lender)|Personas]]). Composition can shift two ways: (a) **curator action** — parameter change, new CM, raised quota; and (b) ==quota-composition shift== — borrowers migrate from token A to token B without any parameter change, the LP's exposure mix changes silently. Both are caught here. The deep-dive on what each shift means for max exposure lives in [[Pool deposit#Q2 · What's my maximum exposure, per token?|Pool deposit Q2]]. The gate splits into two layers: (i) detect drift via the agent log; (ii) re-evaluate acceptability under the current thesis — sunk-cost-blind on entry-time composition.

**What the agent computes:**

| Sub-question | Tier | What the agent does | Data retrieved |
| --- | --- | --- | --- |
| Top-3 collateral delta since last check | T1 | Compare current top-3 quoted-token exposure (by `quotaUsed`) to the agent's last-check snapshot. Classify whether top-3 composition still matches the user thesis. Drift triggers the forward-looking re-eval — "would the LP accept this composition entering today?" | `Pool.quotedTokens[].quotaUsed` (current); `agentLog.previousCheck.quotaComposition`. |
| New CMs added since last check | T1 | List CMs added between `agentLog.previousCheck.asOf` and now; verify each is acceptable under the user's current thesis. ==list of new CMs added to the pool==<br><br>==**note**: is that really necessary?<br>do we sort CMs by date added w/ some threshold for the user position entry?== | `Pool.creditManagers[]` with `addedAt` timestamps; `agentLog.previousCheck.asOf`. |
| Per-token quota size changes | T2 | For each token, compare `quotaLimit` and `quotaRate` to last-check values. A raised limit on a near-saturated token escalates the max-exposure ceiling — re-runs the Pool deposit Q2 `min(...)` formula at the back-edge. | `Pool.quotedTokens[].{quotaLimit, quotaRate, quotaUsed}` (current); `agentLog.previousCheck.quotaParameters`. |
| **Synthesis** | — | T1 catches the quick "did anything change since last look?" check on dominant exposure. T2 fires when composition shifted, to drill which knob moved (curator action vs borrower migration). Drift → back-edge to [[Pool deposit#Q2 · What's my maximum exposure, per token?\|Pool deposit Q2]] (max-exposure formula re-runs with new bounds; per-token risk profile re-evaluated for any new top-3 token). | — |

### Q4 · Has anyone changed the rules?

**Exit gate:** "Pending governance queue is empty or non-material; recent parameter-change log is quiet (≤ 1 material change in 30d) per [[Position risk and monitoring#Pool position monitoring|Position risk and monitoring]]."

**Why this matters.** Same loss vector as Q3 — silent curator changes ([[Personas and audience#Pool LP (passive lender)|Personas]]) — read here from the *change-feed* angle rather than the *composition* angle. Pool deposit Q5 is the deep-dive: [[Pool deposit#Q5 · What could change after I deposit?|Pool deposit Q5]].

**What the agent computes:**

| Sub-question | Tier | What the agent does | Data retrieved |
| --- | --- | --- | --- |
| Pending governance queue | T1 | Read pending Safe-TX / timelock items affecting this pool. Each item: classification (material vs cosmetic) + execution time. Material change queued inside the user monitoring window requires review / action. | pending governance-change queue filtered to this pool. |
| Recent parameter-change log | T1 | Material changes executed since the last monitoring check. Evaluate frequency, clustering, and severity against the user / mandate change-tolerance policy. | Executed pool-change feed since the last monitoring check. |
| Material vs cosmetic classification | T2 | Apply Pool deposit Q5's change-classification table to each event / queued item. ==IRM edits== flagged separately from `Rbase` micro-tweaks; oracle changes on a dominant token always escalate to material. | Per-item `eventType`, `parameter`, `oldValue`, `newValue`; classification logic from [[Pool deposit#Q5 · What could change after I deposit?\|Pool deposit Q5]]. |
| **Synthesis** | — | T1 surfaces pending + recent at verdict-level. T2 fires when there's enough activity to need per-item classification. Multiple queued material changes is itself a curator-volatility signal (cross-ref [[Pool deposit#Q4 · Who manages this pool?\|Pool deposit Q4]] activity log). Drift → back-edge to [[Pool deposit#Q5 · What could change after I deposit?\|Pool deposit Q5]]. | — |

### Q5 · Is the bad-debt canary intact?

**Exit gate:** "Share price has not declined since the last check (or any decline is explained by a known incident); insurance fund stable or growing."

**Why this matters.** Bad debt is a P1 LP loss vector ([[Personas and audience#Pool LP (passive lender)|Personas]]) — the realised-loss case. The pool share price is the canonical canary ([[Basic info and definitions#Pool vocabulary]] · "Bad-debt canary / share-price canary"); insurance-fund delta is the corroborating signal. Deep-dive: [[Pool deposit#Q2 · What's my maximum exposure, per token?|Pool deposit Q2]] (tail-risk re-eval) + [[Pool deposit#Q4 · Who manages this pool?|Pool deposit Q4]] (curator post-mortem).

**What the agent computes:**

| Sub-question | Tier | What the agent does | Data retrieved |
| --- | --- | --- | --- |
| Share price delta since last check | T1 | Any drop = canary trigger (per [[Position risk and monitoring#Pool position monitoring\|Position risk and monitoring]] any unexplained drop is a canary trigger; materiality depends on user / product policy). Distinct from yield accrual, which is reflected in monotonic share-price growth. | `Pool.sharePrice` (current); `agentLog.previousCheck.sharePrice`; pool's known-incidents log if any. |
| Insurance fund balance delta | T1 | ==insurance-fund balance change (only relevant if the buffer was part of the original thesis)==. Evaluate whether the buffer is stable enough for the user thesis; material decline or near-zero balance requires review. | `Pool.insuranceFundBalance` (current); `agentLog.previousCheck.insuranceFundBalance`. |
| Curator incidents log cross-ref | T2 | If share price dropped or the insurance fund moved, cross-ref `Curator.badDebtIncidents[]` and `Curator.liquidityIncidents[]` for new entries since last check. If no new incident matches the canary signal, flag as anomaly for manual review. | `Curator.{badDebtIncidents[], liquidityIncidents[]}`; `agentLog.previousCheck.incidentIds`. |
| **Synthesis** | — | T1 gates on the canary directly (share price + insurance fund). T2 fires when the canary triggers — finds the underlying incident in the curator log, otherwise flags anomaly. Drift → back-edge to [[Pool deposit#Q2 · What's my maximum exposure, per token?\|Pool deposit Q2]] (which token caused the loss) + [[Pool deposit#Q4 · Who manages this pool?\|Pool deposit Q4]] (curator post-mortem — operational pillar / liquidity-incident log). | — |

### Q6 · Are the oracles I depend on fresh?

**Exit gate (when Q6 fires):** "Per-token oracle freshness within staleness window; main-vs-reserve divergence within tolerance; no oracle methodology change for dominant tokens since the agent's last check that violates the user's accepted-methodology list."

**Why this matters.** Oracle manipulation / staleness is a **P2** LP loss vector ([[Personas and audience#Pool LP (passive lender)|Personas]]) — upstream cause of bad-debt and locked-liquidity events when it fires. Q6 fires only when triggered — see [[oracle-and-liquidity-risk#Drill — Q6 oracle drill triggers|drill ↗]]. Deep-dive in [[Pool deposit#Q2 · What's my maximum exposure, per token?|Pool deposit Q2]]; for multi-node feed paths, run the [oracle analysis workflow](../references/workflows/oracle-analysis/README.md). The methodology check splits into two layers: (i) detect change via the agent log; (ii) re-evaluate acceptability under the current thesis.

**What the agent computes (when Q6 fires):**

| Sub-question | Tier | What the agent does | Data retrieved |
| --- | --- | --- | --- |
| Per-token freshness | T2 | `now − lastUpdate < stalenessWindow` for each quoted token. A token approaching or past the staleness window threatens the user thesis. Cheapest sub-Q — runs first when Q6 fires. | Oracle last-update timestamp and staleness window per quoted token. |
| Main-vs-reserve divergence | T2 | Compare `mainOracle` and `reserveOracle` prices per token. Classify divergence by its effect on the pool thesis and exit / bad-debt risk. | Main/reserve oracle prices per quoted token. |
| Oracle methodology change since last check | T2 | Detect any `oracleChanged` event affecting a dominant token between `agentLog.previousCheck.asOf` and now, or any direct mismatch between current current oracle category/methodology and the agent's last-check snapshot. A main → reserve oracle swap is permissionless without timelock — surfaces here. Triggers the acceptability gate below. | Current oracle category/methodology per dominant token; previous-check oracle set; executed oracle-change events. |
| Methodology acceptable under user thesis | T2 | For each dominant token, check current oracle category against the user's accepted-methodology list. A pool that adds a NAV-oracle dominant token where the LP only accepted market oracles fails the gate even without an explicit `oracleChanged` event. Category shifts can flip the cascade-vs-trap risk shape ([[oracle-and-liquidity-risk#Drill — Oracle types and LP risk shapes\|drill ↗]]). | Current oracle category/methodology per dominant token; user accepted-methodology list. |
| **Synthesis** | — | Q6 doesn't run on every monitoring call — fires only on the triggers above. When fired: sub-Qs run cheapest-first (freshness → divergence → methodology delta → acceptability). The methodology split surfaces *what changed* (delta against agent log) separately from *whether current state is acceptable* (forward-looking gate against user thesis). Drift → back-edge to [[Pool deposit#Q2 · What's my maximum exposure, per token?\|Pool deposit Q2]] (live oracle sanity + per-token risk profile). | — |

### Q7 · Is the issuer-controlled collateral branch drifting? *(conditional)*

**Exit gate:** "Frozen-accounts count acceptable under user policy; aggregate frozen debt does not threaten the LP thesis; eligible-liquidator set is stable enough for the current exposure."

**Why this matters.** Frozen accounts and liquidator scarcity are issuer-controlled-collateral LP loss vectors ([[Personas and audience#Pool LP (passive lender)|Personas]] — P2). When the issuer (Securitize, etc.) freezes accounts, those positions can't be liquidated; if their aggregate debt exceeds the insurance fund, the loss socialises to LPs. Deep-dive: [[Pool deposit#Q2 · What's my maximum exposure, per token?|Pool deposit Q2]] Per-token risk profile (Platform layer for issuer-controlled tokens).

**Data boundary.** Gearbox can expose pool exposure and accepted-token state. Frozen-account counts, issuer whitelist changes, liquidator coverage, redemption calendars, and regulatory-event context are issuer/indexer data and should be marked as such.

**What the agent computes:**

| Sub-question | Tier | What the agent does | Data retrieved |
| --- | --- | --- | --- |
| Frozen-accounts delta | T1 | Count of frozen accounts new since `agentLog.previousCheck.asOf` + their aggregate debt. Evaluate count and debt against the insurance fund and user / product policy. | Issuer / platform endpoint (Securitize, etc.): `frozenAccounts[].{address, frozenAt, debtUsd}`; `agentLog.previousCheck.frozenAccountIds`. If the endpoint is unavailable, flag issuer freeze state as an unresolved live-data gate. |
| Eligible-liquidator changes | T2 | ==whitelist changes for liquidators.== Contracted liquidator set can make bad accounts harder to clear; expanded set is usually informational unless it changes the thesis. | Issuer / platform eligible-liquidator endpoint with change history. |
| Issuer status / regulatory action | T2 | Read external — issuer post-mortems, regulatory filings, public freeze announcements — when the on-chain signal alone is insufficient to explain a delta. | External: issuer comms, regulator announcements. |
| **Synthesis** | — | T1 directly measures how much risk has migrated from "active collateral" to "frozen and un-liquidatable". T2 fires when T1 flagged or when an external regulatory event is known. Drift → back-edge to [[Pool deposit#Q2 · What's my maximum exposure, per token?\|Pool deposit Q2]] Per-token risk profile (Platform layer). | — |

### Outputs (the hand-off)

`MonitoringSnapshot` — verdict per Q + drift list + the recommended next step for the session.

```
MonitoringSnapshot {
  position_id, as_of,
  verdicts: { q1_yield, q2_exit, q3_composition, q4_governance, q5_bad_debt, q6_oracle?, q7_issuer_controlled? },
  // each verdict: { status: 'ok'|'watch'|'review'|'act_now', summary, contributing_signals[] }
  // q6_oracle is present only when Q6 fired (drill triggered); absent on default Confirmation calls
  // q7_issuer_controlled is present only when issuer-controlled collateral exposure is material
  drift_signals: string[],   // human-readable summary of any review / action verdicts
  recommended_next: 'end' | 'analyze' | 'top_up' | 'partial_exit' | 'full_exit',
  next_check_eta,
}
```

**Hand-off branches.**
- **All verdicts acceptable under user policy** → `recommended_next: 'end'`. Agent surfaces a single summary line and exits — Confirmation session, in under a minute.
- **Any review / act verdict** → `recommended_next: 'analyze'`. Hand off to [[#Stage 2 · Analyze (Pool) — focused re-run|Stage 2]] for the focused Pool-deposit-Q re-run.
- **Thesis-broken or new-thesis** → `recommended_next: 'top_up' | 'partial_exit' | 'full_exit'`. Hand off to [[#Stage 3 · Propose (Pool) — Action Committee|Stage 3]] (skipping Stage 2 — the Action / Exit session shape per [[Entry points#Mapping to ownership-lifecycle session types]]).

No Stage-6 composite score is required. Stage 6 returns the per-question verdict mix and drift signals; Stage 2 is the Analyst pass that re-assesses the affected questions; Stage 3 is the Action Committee pass that aggregates those assessments into one action decision (`end`, `top_up`, `partial_exit`, or `full_exit`).

## Stage 2 · Analyze (Pool) — focused re-run

**Sub-jobs satisfied here:**
- **Re-validate the affected Pool-deposit Q(s)** based on which Stage-6 verdict flipped.
- **Decide thesis-holds vs thesis-broken** — i.e., whether the drift is acceptable under the current user thesis or the position needs to change.

**Exit gate:** every re-run Pool-deposit-Q produces a verdict. If all conclude "still acceptable" → return to Stage 6 Confirmation cadence next cycle. If any concludes "no longer acceptable" → escalate to Stage 3 with a `recommended_action`.

**User's goal:** "Re-run only what changed; don't redo the full pre-deposit due diligence."

### Inputs (what enters this stage)

| Input | Description |
| --- | --- |
| `MonitoringSnapshot` | From Stage 6. The `drift_signals[]` list and per-Q `verdicts` drive which Pool-deposit Q(s) get re-run. |
| User thesis / criteria | Carried — same forward-looking gates as Stage 6. |

### Compute (agent-side — focused re-run)

For each review-required or action-required Q-verdict in `MonitoringSnapshot.verdicts`, re-run the mapped Pool-deposit Q. Deep-dives live in [[Pool deposit#Stage 2 · Analyze — LP due diligence|Pool deposit Stage 2]] and are not duplicated here.

| Monitoring drift | Pool deposit Q to re-run | Effect of the re-run |
| --- | --- | --- |
| Q1 yield drift | [[Pool deposit#Q1 · Where does the yield come from, and is it sustainable?\|Q1]] | Yield-sustainability re-evaluation; incentive-durability T2 fires if a layer is the cause. |
| Q2 exit feasibility drift | [[Pool deposit#Q3 · Can I withdraw when I need to?\|Q3]] | Re-run all five exit-feasibility dimensions; concentration / cascade-history T2 likely needed. |
| Q3 composition drift | [[Pool deposit#Q2 · What's my maximum exposure, per token?\|Q2]] | Max-exposure formula re-runs with new bounds; per-token risk profile re-evaluated for any new-top-3 token. |
| Q4 governance change | [[Pool deposit#Q5 · What could change after I deposit?\|Q5]] | Re-classify executed / pending changes; the pace lens updates the curator-volatility read. |
| Q5 bad-debt canary | [[Pool deposit#Q2 · What's my maximum exposure, per token?\|Q2]] + [[Pool deposit#Q4 · Who manages this pool?\|Q4]] | Tail-risk re-eval (which token caused the loss) + curator post-mortem (operational pillar / liquidity-incident log). |
| Q6 oracle drift (when Q6 fired) | [[Pool deposit#Q2 · What's my maximum exposure, per token?\|Q2]] | Live oracle sanity + oracle-type-to-risk-shape sub-questions re-run. |
| Q7 issuer-controlled collateral drift | [[Pool deposit#Q2 · What's my maximum exposure, per token?\|Q2]] | Per-token 3-layer risk profile, Platform-layer pillar specifically. |
| **Synthesis** | — | Targeted Q re-run, not full Analyze — no fresh Discover, no re-traversal of Qs that remained acceptable in Stage 6. Each re-run Q produces a "still acceptable" or "no longer acceptable" verdict; aggregated into a position-level `position_thesis_verdict`. | — |

### Outputs (the hand-off)

`FocusedAnalyzeReport` — per-Q thesis verdicts plus the overall position-level thesis verdict.

```
FocusedAnalyzeReport {
  position_id, as_of,
  re_run_qs: Array<{ pool_deposit_q, verdict: 'still_acceptable' | 'no_longer_acceptable', reasoning }>,
  position_thesis_verdict: 'holds' | 'weakened' | 'broken',
  recommended_action: 'none' | 'top_up' | 'partial_exit' | 'full_exit',
}
```

**Hand-off branches.**
- **`position_thesis_verdict: 'holds'`** → return to Stage 6 Confirmation cadence next cycle. Agent records the re-run Q's clean verdict in `agentLog.previousCheck` so the same signal isn't re-flagged on the next call.
- **`position_thesis_verdict: 'weakened' | 'broken'`** → hand off to [[#Stage 3 · Propose (Pool) — Action Committee|Stage 3]] with `recommended_action`.

## Stage 3 · Propose (Pool) — Action Committee

**Sub-job (part 1 of Commit action):** decide the action class (top-up / partial exit / full exit) and size it.

**Exit gate:** action class chosen, amount sized, rationale captured. Hand off to Stage 4.

**User's goal:** "Decide what to actually do about this position, given the new analysis."

### Inputs (what enters this stage)

| Input | Description |
| --- | --- |
| `FocusedAnalyzeReport` | From Stage 2 (or directly from Stage 6 in the Action / Exit session shape — when the LP arrives with a known thesis and skips Analyze). |
| Position state | `LpPosition.{shares, currentValueUsd, ...}` (current). |
| Available capital | Used for `top_up` action only; carried in session config. |

### Compute (agent-side — Action Committee)

The agent acts as the LP's **Action Committee** for this single position: takes the focused-analyze report (or direct LP intent), applies portfolio context, and selects + sizes the action. Distinct from Pool deposit Stage 3's [[Pool deposit#Stage 3 · Propose (Pool) — Investment Committee|Investment Committee]] — the IC allocates *across multiple candidates*; the Action Committee acts on *one existing position*. No reserve concept.

| Decision class | Tier | What the agent does | Data retrieved |
| --- | --- | --- | --- |
| Action class selection | T1 | Map `position_thesis_verdict` to action class: `holds` + LP wants more exposure → top-up; `weakened` → partial exit; `broken` → full exit. | `FocusedAnalyzeReport.position_thesis_verdict`; user-level top-up / exit intent (carried in session). |
| Sizing per action class | T1 | For top-up: decide amount within concentration cap. For partial exit: pick the largest size that still clears Q2 exit-feasibility thresholds (`(1 − U) × TVL` minus margin). For full exit: full `LpPosition.shares`. | `LpPosition.{shares, currentValueUsd}`; available capital (top-up); concentration cap; Q2 exit-feasibility re-run results. |
| Cross-position dedup | T2 | If the LP holds correlated positions in other Gearbox pools, avoid over-correcting one position when a portfolio-level reallocation is cleaner — flag as cross-position work outside this flow. | Cross-position `LpPosition[]`; cross-pool concentration. |
| **Synthesis** | — | Output `ActionDecision { action_class, amount_usd, rationale }`. Action-class mapping, no-Emergency rationale, and cross-pool-reallocation out-of-scope rule: [[allocation-and-action-palettes#Drill — LP action-class palette\|drill ↗]]. | — |

### Outputs (the hand-off to Stage 4)

```
ActionDecision {
  position_id,
  action_class: 'top_up' | 'partial_exit' | 'full_exit',
  amount_usd,
  amount_shares,            // exit only — exact share count to redeem
  rationale,
  source: 'focused_analyze' | 'direct_lp_intent',
}
```

Hand off to [[#Stage 4 · Preview (Pool) — Execution Desk pre-trade|Stage 4]].

## Stage 4 · Preview (Pool) — Execution Desk pre-trade

**Sub-job (part 2 of Commit action):** validate the proposed action against current chain state — simulate the exact transaction, surface deviations from Stage-3-time assumptions, gate on them.

**Exit gate:** simulation matches proposal: expected shares / underlying within tolerance; no deviation flags fire (utilisation / withdraw queue / fee haven't materially shifted since Stage 3); no Preview warnings; gas acceptable.

**User's goal:** "Will this exact transaction do what I expect _right now_, or have conditions changed since the action was decided?"

### Inputs (what enters this stage)

| Input | Description |
| --- | --- |
| `ActionDecision` | From Stage 3 — `action_class`, `amount_usd`, `amount_shares` (exit). |
| Current chain state | Re-fetched per `position_id` to compare against decision-time assumptions. |

### Compute (agent-side — Execution Desk pre-trade)

Per `ActionDecision.action_class`:

- **`top_up`** — same shape as [[Pool deposit#Stage 4 · Preview (Pool) — Execution Desk pre-trade|Pool deposit Stage 4]] (deposit preview, concentration check, deviation flags, gas).
- **`partial_exit` / `full_exit`** — withdrawal-specific previews:
  - `ERC-4626.previewWithdraw` / `previewRedeem` — actual underlying out at the requested size.
  - **Withdrawal fee** — surfaced (current `Pool.withdrawalFee`, ≤ 100 bps).
  - **Price impact at exit size** — when redemption routes through a swap leg, hit DEX subgraph / aggregator.
  - **In-flight rewards forfeited** — incentive-layer pro-rata not yet claimed at exit.
  - **Time-to-fill estimate** — when the pool has a withdraw queue or notice period, surface the expected unlock window.
  - **Deviation flags** — utilisation / fee / queue depth changed since Stage 3 > tolerance.
  - Gas estimate.

### Outputs (the hand-off to Stage 5)

```
TransactionPreviewReport {
  position_id, action_class,
  expected_underlying_out,         // exit
  expected_shares_minted,          // top_up
  share_price_at_preview,
  projected_concentration_pct,     // top_up
  withdrawal_fee_usd,              // exit
  price_impact_pct,                // exit
  in_flight_rewards_forfeited_usd, // exit
  time_to_fill_estimate,           // exit, when queue active
  deviation_flags: { utilisation_change_pp, fee_change_bps, queue_depth_change, apy_change_pct, tvl_change_pct },
  gas_estimate_usd,
  warnings: string[],
  calldata,                        // ready to sign
}
```

**On failure.** If Preview fails (deviation flag fires materially or the action no longer clears the LP's intent), the loop returns to **Stage 3** for that action — not back to Stage 2. The thesis can still hold even if execution-time parameters need adjustment.

## Stage 5 · Execute (Pool) — Execution Desk trade

**Sub-job (part 3 of Commit action):** sign and submit the previewed transaction, with an integrity guarantee that signed bytes match validated bytes.

**Exit gate:** the bytes signed match what Preview validated; the transaction confirms on-chain.

**User's goal:** "Sign and submit, with a guarantee that the bytes I signed are the bytes Preview validated."

### Inputs (what enters this stage)

| Input | Description |
| --- | --- |
| `TransactionPreviewReport` | From Stage 4 — with validated calldata. |
| Signer context | HITL wallet OR scoped bot signer with on-chain permissions. |

### Compute (agent-side — Execution Desk trade)

Same two modes as [[Pool deposit#Stage 5 · Execute (Pool) — Execution Desk trade|Pool deposit Stage 5]]:

| Mode | Description |
| --- | --- |
| **Human-in-the-loop** | Agent encodes the preview into a verifier flow; the human signs in their wallet. The verifier UI shows the same calldata that Preview produced — any divergence (e.g., wallet substituting calldata) breaks the integrity gate. |
| **Bot** | Scoped bot signer executes within on-chain permissions. Bot must verify calldata hash matches Preview output before submitting. |

No new data requirements; this stage consumes the approved transaction and the signer context.

### Outputs (the hand-off back to Stage 6)

```
TransactionConfirmation {
  position_id, action_class,
  txHash, blockNumber,
  actual_underlying_out,    // exit
  actual_shares_minted,     // top_up
  actualSharePrice,
  gasPaidUsd,
}
```

**Hand-off back to Stage 6.** The agent updates `agentLog.previousCheck` to reflect the post-action state (new shares balance, new sharePrice baseline, action recorded in incident log if material). Next monitoring cycle resumes Stage 6 from this baseline.

## Edge cases & known failure modes

| Scenario | Description |
| --- | --- |
| **Incentive-only yield trap.** | Headline APY looks great; organic APY alone is below the floor (sized at entry inside Pool deposit Q1). Incentive campaign expires a month in; net yield collapses. Caught by **Q1 T2** (incentive-layer-expiry fires when material). |
| **Utilisation spike lockout.** | LP tries to exit; utilisation is near full and withdrawal is throttled until borrowers repay. Caught by **Q2** (action-required verdict on withdrawable liquidity + recent trend). |
| **Silent composition shift.** | No governance action, but borrowers migrate to a riskier collateral mix. Exposure the LP signed up for is no longer what they're holding. Caught by **Q3** (T1 top-3 delta + T2 per-token quota changes). |
| **Paused CM with outstanding debt.** | CM is paused (no new positions, but also no liquidations). Underwater positions inside cannot be closed; bad debt accumulates until unpause. Caught by **Q4** (`cmPaused` event in change log, classified material). |
| **Issuer freeze cascade.** | Issuer freezes multiple accounts. Their total debt exceeds the insurance fund. Socialised loss hits LPs. Caught by **Q7** (T1 frozen-accounts delta vs insurance fund) and signalled through **Q5** (share-price drop) once realised.  |
