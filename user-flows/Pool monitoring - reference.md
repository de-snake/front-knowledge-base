# Pool monitoring — reference

Drill sections referenced from [[Pool monitoring]] table rows and prose. Each drill is a self-contained explanatory unit; the main file's calling row carries only the verdict-level summary plus a wikilink. Topic names are flow-agnostic where possible. These reference blocks are product explanations for why a monitoring branch fires. They may point at protocol primitives, but issuer updates, regulatory context, and methodology acceptance remain data/product policy inputs.

## Drill — LP action-class palette

Pool monitoring Stage 3 (Action Committee) chooses among three action classes for one existing position. Distinct from Pool deposit Stage 3's [[Pool deposit#Stage 3 · Propose (Pool) — Investment Committee|Investment Committee]]: the IC allocates *across multiple candidates* with a reserve concept; the Action Committee acts on *one existing position* with no reserve.

- **Top-up.** `position_thesis_verdict: 'holds'` + LP wants more exposure → `action_class: "top_up"`. Sized within concentration cap.
- **Partial exit.** `position_thesis_verdict: 'weakened'` → `action_class: "partial_exit"`. Largest size that still clears Q2 exit-feasibility thresholds.
- **Full exit.** `position_thesis_verdict: 'broken'` → `action_class: "full_exit"`. Full `LpPosition.shares`.

**No Emergency action class.** LPs have no liquidation / HF danger in the LP role. The closest analogue is a sudden bad-debt event detected via [[Pool monitoring#Q5 · Is the bad-debt canary intact?|Q5]] → escalates to Partial / Full exit at high priority but still without the Emergency-mode ≤ 2-clicks contract.

**Cross-pool reallocation is out of scope here.** Closing one pool to open another is the full-canonical-loop reallocation case (Discover → Analyze → Propose → Preview → Execute across pools), not a within-pool action.

## Drill — Q6 oracle drill triggers

Q6 (oracle freshness / divergence / methodology) is excluded from the Pool LP Glance set in [[Three-layer progressive disclosure]]; oracle is a **P2** LP loss vector in [[Personas and audience#Pool LP (passive lender)|Personas]]. All Q6 sub-Qs are T2; Q6 fires only when one of these triggers fires:

- **Q5 canary fires** — share-price drop or insurance-fund delta. Oracle is the prime suspect for the upstream cause; Q6 runs to identify whether a stale or methodology-shifted feed caused the realised loss.
- **Q3 detects a new top-3 collateral** — the new token's oracle is suspect by default until verified against the LP's accepted-methodology list.
- **LP is sophisticated** — institutional, structured-product desk, or RWA-aware. Persistent T2 coverage on every monitoring call.
- **Known structural oracle risk on dominant collateral** — pool has a dominant collateral on a NAV / hardcoded / hybrid feed. The cascade-vs-trap shape ([[Pool deposit - reference#Drill — Oracle types and LP risk shapes|drill ↗]]) makes oracle drift a non-cosmetic concern.

When none fire, Q6 is skipped and the `MonitoringSnapshot.verdicts.q6_oracle` field is absent.

## Drill — Agent continuity log mechanics

The agent maintains `agentLog.previousCheck.{...}` across monitoring sessions to drive delta-detection. Sunk-cost-blind by design — the log is the agent's record of *what changed since I last looked*, not of *what the LP entered with*.

**Schema.** `previousCheck.{asOf, sharePrice, insuranceFundBalance, parameterSet, oracleSet, quotaComposition, incidentIds, frozenAccountIds, ...}` plus per-Q-specific extensions as needed.

**Per-Q delta usage.**
- Q3 — `previousCheck.{quotaComposition, asOf, quotaParameters}` (top-3 delta, new CMs since, per-token quota changes).
- Q4 — `previousCheck.asOf` (parameter-change log scoped to `executedAt > previousCheck.asOf`).
- Q5 — `previousCheck.{sharePrice, insuranceFundBalance, incidentIds}` (canary delta + curator-incident cross-ref).
- Q6 (when fired) — `previousCheck.oracleSet` (methodology change detection).
- Q7 — `previousCheck.{frozenAccountIds, asOf}` (frozen-accounts and whitelist deltas).

**First-call rule.** First monitoring call after a fresh deposit: deltas are vacuously zero and the agent records current pool state as `previousCheck` for next-call's delta. No special-cased "I just entered" branch — consistent with the sunk-cost-blind philosophy.

**Persistence boundary.** `previousCheck` is user / agent-side state. Gearbox-side systems provide current protocol state and history feeds; they do not own or mirror the agent's continuity log. If an agent needs cold-start or multi-device continuity, the user or the user's representative persists and supplies that state.
