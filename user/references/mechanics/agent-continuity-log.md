# Agent continuity log mechanics

Stable mechanics for how the agent carries previous-check state across LP and Credit Account monitoring sessions. This is user / agent-side state, not Gearbox protocol state.

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

**Emergency follow-up.** After an Emergency action confirms on-chain, Stage 5 updates `previousCheck` to reflect the post-action state; the next Stage 6 call computes deltas against the post-Emergency baseline (not the pre-Emergency one), so the agent does not double-count the Emergency action as further drift.

**Persistence boundary.** `previousCheck` is user / agent-side state. Gearbox-side systems provide current protocol state, history feeds, and execution constraints; they do not own or mirror the agent's continuity log. If an agent needs cold-start, institutional reporting, or multi-device continuity, the user or the user's representative persists and supplies that state.
