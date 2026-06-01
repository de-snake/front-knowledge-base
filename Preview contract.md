# Preview contract

Preview is the execution gate between **Propose** and **Execute**.

A proposed action is not executable until the system has simulated the exact action package, compared current state to projected state, classified warnings, and produced a pass/fail verdict the user can approve.

## Core rule

**Execute may only submit the package that Preview produced and the user approved.**

If any material input changes between Preview and Execute, the action returns to Preview or Propose.

## Preview jobs

Preview must answer four questions:

1. **What will be submitted?** The action class, target, amount, route, and execution package.
2. **What changes?** Before/after state for the fields the user cares about.
3. **What can go wrong?** Warnings, blocking reasons, and unknowns.
4. **Can this proceed?** Pass/fail verdict and required approval mode.

## Universal `TransactionPreview`

| Field | Meaning |
| --- | --- |
| `preview_id` | Stable handle for this preview. |
| `created_at` | Time the preview was generated. |
| `expires_at` | Time after which the preview must be refreshed. |
| `action_class` | Product action being previewed. |
| `target` | Pool, Credit Account, or route target. |
| `amount` | User amount or computed action size. |
| `before_state` | Relevant current state before action. |
| `after_state` | Simulated state after action. |
| `warnings` | User-facing warning list with severity and blocking status. |
| `unknowns` | Missing data that limits confidence. |
| `pass_fail` | `pass`, `pass_with_warnings`, or `fail`. |
| `approval_mode` | Human approval, bot allowed, or blocked. |
| `execution_package` | Exact package to submit if approved. |
| `integrity_hash` | Binding between approved preview and execution package. |

## Severity model

| Severity | Meaning | Result |
| --- | --- | --- |
| Info | Does not change the decision; useful context only. | Can proceed. |
| Warning | User should notice and approve knowingly. | Can proceed only as `pass_with_warnings`. |
| Blocking | Violates a user constraint, protocol constraint, or product safety rule. | Cannot proceed. |
| Unknown | Required data is missing. | Cannot proceed unless explicitly allowed for that action class. |

## Pool preview requirements

Pool deposit, top-up, partial withdrawal, and full withdrawal previews must show:

| Area | Required before/after or explanation |
| --- | --- |
| Amount | Input amount, expected shares, expected received asset, and any fee / slippage. |
| Liquidity | Whether the pool can accept or return the requested amount at current conditions. |
| Yield | Expected current yield composition and whether incentives are assumed. |
| Exposure | Resulting user exposure and concentration, if user limits are known. |
| Exit feasibility | Withdrawal route, expected delay, blocking reason, or claim readiness. |
| Warnings | Paused state, liquidity pressure, stale data, RWA conditions, or missing external feed. |

Pool preview passes only when the requested action is executable, required data is fresh enough for the action, and user constraints are not violated.

## Credit Account preview requirements

Credit Account opening, add collateral, reduce leverage, increase leverage, rebalance, partial exit, full exit, and claim previews must show:

| Area | Required before/after or explanation |
| --- | --- |
| Health Factor | Current HF, projected HF, liquidation distance, and whether the action improves or worsens safety. |
| Debt and leverage | Debt, equity, leverage, and quota / borrow-cost impact. |
| Route and price impact | Entry / exit route class, price impact, slippage budget, and fallback if the route fails. |
| Collateral composition | Token balances, dominant exposures, forbidden-token or delayed-withdrawal status. |
| Position economics | Net APY or cost impact, including borrow and quota costs. |
| Operational envelope | Pause, expiration, minDebt / maxDebt, LT-ramp schedule, oracle freshness, and pending changes. |
| Warnings | Liquidation risk, stale oracle, route degradation, unsupported partial exit, or missing external data. |

Credit Account preview fails when projected HF or another safety invariant violates the user's configured floor, protocol constraints prevent the action, or required current state is unknown.

## Emergency preview requirements

Emergency actions are time-sensitive but still require Preview.

Minimum emergency preview fields:

| Field | Meaning |
| --- | --- |
| `emergency_reason` | Why this bypasses focused Analyze and goes directly to action sizing. |
| `pre_action_hf` | Current safety state. |
| `post_action_hf` | Projected safety state after the emergency action. |
| `safety_delta` | Whether the action improves the safety state. |
| `residual_risk` | What remains unsafe after action. |
| `next_required_step` | Whether another action is required after execution. |

Emergency preview should optimize for speed and clarity, not exhaustive due diligence. It still cannot submit bytes that differ from the approved preview.

## RWA / compliance preview extension

For RWA-related pools and Credit Accounts, Preview must add:

| Area | Required explanation |
| --- | --- |
| Eligibility | Whether the user and relevant position path are currently eligible. |
| Freeze state | Whether any relevant account, asset, or program is frozen or restricted. |
| Redemption state | Whether exit depends on a redemption window or claim readiness. |
| Liquidation feasibility | Whether eligible liquidator depth appears sufficient for the risk being taken. |
| Execution mode | Whether the action is human-only, bot-allowed, or blocked. |
| Blocking reason | User-readable reason when compliance or issuer state prevents action. |

RWA Preview should surface issuer / compliance unknowns as unknowns. Do not present missing issuer data as protocol-confirmed safety.

## Execute handoff

Preview hands Execute exactly:

| Field | Purpose |
| --- | --- |
| `preview_id` | Identifies the approved preview. |
| `execution_package` | Exact package to submit. |
| `integrity_hash` | Detects mismatch between approved and submitted package. |
| `approval_mode` | Determines whether a human signer is required. |
| `post_execute_monitor_target` | Position or account to monitor after confirmation. |

If Execute cannot prove that the submitted package matches the approved preview, it must stop and ask for a new Preview.

## Failure routing

| Failure point | Route |
| --- | --- |
| Proposal cannot be previewed | Back to Propose. |
| Preview simulation fails | Back to Propose with blocking reason. |
| Preview passes with warnings | Ask for user approval; do not auto-execute unless policy allows that warning class. |
| Input changed after Preview | Refresh Preview. |
| Execution fails on-chain | Return to Monitor if state changed; otherwise return to Propose with failure reason. |

## Acceptance checklist

A Preview contract is implementation-ready when:

- the before/after fields are sufficient for the user to understand the action;
- every warning has severity, source, and blocking status;
- stale, missing, or external-only data is visible;
- pass/fail rules are deterministic;
- execution cannot drift from approved bytes silently;
- emergency and RWA paths still preserve the Preview gate.
