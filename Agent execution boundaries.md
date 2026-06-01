# Agent execution boundaries

This document defines what the Gearbox agent may do by itself, what requires human approval, and what is blocked.

It applies to both UI-driven users and LLM-agent users. The data model is shared; permissions and surfacing differ.

Gearbox-side systems cannot guarantee that a user's LLM agent behaves well. The product boundary is: Gearbox serves protocol state, warnings, previews, and on-chain permission scopes; the user or the user's representative persists preferences and controls the agent's off-chain search / ranking policy.

## Boundary model

| Mode | Agent may do | User approval |
| --- | --- | --- |
| Read-only | Discover, Analyze, Monitor, explain current state, classify alerts. | Not required. |
| Propose-only | Build a proposed action and explain why it fits the user's stated constraints. | Required before Preview / Execute. |
| Preview-without-execute | Simulate a proposed action and show before/after state. | Required before Execute. |
| Human-in-the-loop Execute | Prepare exact transaction package; user signs or explicitly approves submission. | Required. |
| Delegated bot Execute | Execute pre-authorized, narrow maintenance actions inside configured limits. | Prior standing approval required. |
| Blocked | Stop and explain why no action can be prepared or submitted. | New user decision required. |

## Universal rules

1. **The agent can reason freely; it cannot silently change user state.**
2. **Every state-changing action must pass Preview.**
3. **Human approval is the default for Execute.** Bot execution is an explicit exception, not a default.
4. **Bot execution requires a narrow policy envelope.** The envelope must name allowed action classes, sizing limits, safety limits, and stop conditions.
5. **RWA / compliance-gated paths are human-only unless explicitly approved as safe for automation.** Missing issuer or eligibility state blocks automation.
6. **Emergency mode can shorten analysis, not skip Preview.**
7. **The agent must surface unknowns.** Unknown data is not converted into green status.

## Autonomy and policy-state boundary

Agents may autonomously start Discover / Analyze / Propose flows when the user's mandate allows it. A new Decision session can therefore be user-triggered or agent-triggered. The Gearbox-side contract is not to decide when the user's agent should wake up; it is to make every candidate, warning, Preview, and Execute boundary explicit once the session reaches Gearbox data or Gearbox execution.

User preferences and thesis state are user / agent-side state. Examples: APY floor, HF floor, hold horizon, accepted oracle methodologies, concentration limits, notification policy, and off-chain strategy filters. Gearbox docs may treat these as runtime inputs (`userThesis`, policy envelope), but they are not Gearbox-side persistent state.

The only enforceable automation layer Gearbox can rely on is the scoped bot signer or equivalent on-chain permission envelope. An agent policy filter may decide what to surface; an on-chain signer scope decides what can actually execute.

## Action boundary matrix

| Action class | Read / Analyze | Propose | Preview | Execute default | Bot-eligible? |
| --- | --- | --- | --- | --- | --- |
| Pool deposit | Yes | Yes | Yes | Human | Only with explicit allocation policy. |
| Pool top-up | Yes | Yes | Yes | Human | Possible with narrow policy. |
| Pool partial withdrawal | Yes | Yes | Yes | Human | Possible only for pre-approved exit rules. |
| Pool full withdrawal | Yes | Yes | Yes | Human | Usually human. |
| Open Credit Account | Yes | Yes | Yes | Human | No by default. |
| Add collateral | Yes | Yes | Yes | Human | Possible for emergency maintenance if pre-approved. |
| Reduce leverage | Yes | Yes | Yes | Human | Possible for emergency maintenance if pre-approved. |
| Increase leverage | Yes | Yes | Yes | Human | No by default. |
| Rebalance / change strategy | Yes | Yes | Yes | Human | No by default. |
| Partial exit | Yes | Yes | Yes | Human | Possible only inside strict stop-loss / de-risk rules. |
| Full exit / close | Yes | Yes | Yes | Human | Usually human. |
| Claim rewards | Yes | Yes | Yes | Human | Possible if reward claim is side-effect-limited. |
| Enable / disable bot | Yes | Yes | Yes | Human | No; this changes delegation policy. |
| RWA compliance-gated action | Yes | Yes | Yes | Human | Blocked unless explicitly authorized for the exact market and action class. |

## Monitor routing rules

Monitoring may produce four outcomes:

| Outcome | Agent behavior |
| --- | --- |
| Green / no material drift | Explain status and continue monitoring. |
| Yellow / needs focused analysis | Re-run the relevant Analyze question only. |
| Actionable drift | Build a ProposedAction and ask the user whether to Preview. |
| Emergency | Skip broad Analyze, size a safety action, run Preview, and require approval unless a pre-approved emergency bot policy exists. |

## Emergency boundary

Emergency mode is triggered by a material safety breach, not by ordinary optimization.

Emergency mode may:

- reduce the number of alternatives considered;
- focus only on actions that improve safety;
- prioritize Add Collateral, Reduce Leverage, Partial Exit, or Full Exit;
- surface the shortest viable action path.

Emergency mode may not:

- execute without Preview;
- hide residual risk;
- increase leverage;
- switch into a new strategy for yield optimization;
- bypass RWA / compliance gates.

## RWA / compliance boundary

For RWA pools and RWA-backed Credit Accounts, the agent must treat issuer and compliance state as first-class execution constraints.

| Condition | Boundary |
| --- | --- |
| Eligibility unknown | Do not automate; surface unknown. |
| Freeze state unknown | Do not mark safe; surface unknown. |
| Redemption timing unknown | Do not promise exit timing. |
| Eligible-liquidator depth unknown | Do not mark liquidation path healthy. |
| Compliance-gated execution required | Human-in-the-loop by default. |
| Account or asset frozen | Block ordinary optimization actions; route to issue-specific guidance. |

The product docs should call this “compliance-gated execution” and “issuer / redemption state.” Exact implementation names stay in [[Data requirements and to-dos]].

## Bot policy envelope

A delegated bot policy must include:

| Field | Meaning |
| --- | --- |
| `allowed_actions` | Exact action classes the bot may execute. |
| `max_amount` | Per-action and aggregate sizing limits. |
| `safety_floor` | Minimum allowed post-action HF or equivalent safety metric. |
| `slippage_limit` | Maximum allowed slippage or price impact. |
| `cooldown` | Minimum time between bot actions. |
| `stop_conditions` | Conditions that disable automation and require human review. |
| `notification_policy` | What the user sees before and after action. |
| `expiry` | When the delegation must be renewed. |

If a required policy field is missing, the agent can propose and preview but cannot bot-execute.

## User-facing explanation rule

Whenever the agent refuses to execute or automate, it should explain:

1. what it wanted to do;
2. which boundary blocked it;
3. what data or approval is needed next;
4. whether the user can still run the action manually after Preview.

## Acceptance checklist

Execution-boundary logic is ready when:

- every action class has an approval mode;
- Preview is always before Execute;
- RWA / compliance states can block automation;
- emergency mode is fast but not permissionless;
- bot policies are narrow, expiring, and explainable;
- user-facing refusal reasons are clear.
