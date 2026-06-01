# Decision-making loop — Entry points

[[Basic info and definitions#Canonical loop]]

**Purpose.** This Tier 2 doc names the **session-mode axis**: same canonical loop, three different entry shapes depending on what brought the user back. Tier 1 says the loop has six stages; this doc says there are three different ways to enter and walk them. Tier 3 monitoring docs refine Monitoring further into ownership session types.

## Session modes — the same loop, three entry points

The canonical loop is traversed differently depending on what kind of session the user is in. The UI and agent prompts must recognise the mode.

| Mode | Description |
| --- | --- |
| **Decision session (first deposit or new capital).** | Full traversal from Discover through Execute. This is what most technical specs implicitly assume. It is actually the _rarest_ session type by frequency. |
| **Monitoring session (return visit).** | Enters the loop at Stage 6 (Monitor). Most sessions are this — 10–30 seconds, "glance at safety and returns, leave." A meaningful deviation loops the user back to Analyze (and possibly all the way to Discover if they want to switch venues). |
| **Emergency session (pressure event).** | Enters Stage 6 in danger state, then goes directly to Propose → Preview → Execute without re-running Analyze. The thesis is already "reduce risk now"; the constraint is speed. The UI and agent must collapse the path from "awareness of danger" to "signed remediation" to under two clicks. |

Monitoring is not a single shape. It branches:

- **exit cleanly** — most sessions; the user glances and leaves;
- **detect a deviation and loop back to Analyze** — fresh due diligence on what changed;
- **skip Analyze and go straight to act on a known thesis** (`Monitor → Propose → Preview → Execute`) — the user already knows what they want (claim rewards, top up, partial exit) and doesn't need to re-evaluate;
- **go all the way back to Discover to switch venues** (`Monitor → Discover → Analyze → … → Execute`) — full canonical loop, but monitoring-triggered rather than greenfield.

The four branches share the Monitoring entry. What distinguishes them is how far back into the loop the user has to step before acting. None of them carry Emergency's ≤ 2-clicks speed constraint, and none re-enter as a fresh Decision session (no greenfield discovery). See the Mapping section below for the named refinement.

Design implication: the _same_ data fields the agent needs for due diligence are also the fields needed for monitoring and for emergency response — served with a different ranking, surface, and tone. Building one schema for all three modes is the product-engineering lever.

## Mapping to ownership-lifecycle session types

The four Monitoring branches above are named **Confirmation, Analysis, Action, Exit, Reallocation** — five session types backing four distinct loop shapes (Action and Exit share `Monitor → Propose → Preview → Execute` but differ in the action class: optimise vs unwind). Emergency stays as itself.

Cross-position ownership is intentionally not represented by a placeholder flow. This doc names the session-mode axis; the canonical monitoring docs own per-position back-edges until a complete cross-position flow is drafted.

## Agent (LLM) reader

Agents and humans consume the same data schema; only ranking, surface, and tone diverge. [[Personas and audience]] names the agent as a profile sub-type for both Pool LP and CA operator, and [[Three-layer progressive disclosure]] specifies that agents follow the same Glance / Analyze / Act hierarchy.

Default traversal: **Monitoring**. Agents answer the ownership questions on every monitoring call and either end in "no change" or escalate to Analyze (the back-edge contract in [[Pool monitoring]] and [[Credit Account monitoring]]).

Hand-off line: **Execute**, configurable by action class. High-value or first-time actions require a human signature; routine actions can be executed by a scoped on-chain bot signer — a separate primitive: the bot is a deterministic on-chain helper, not the LLM agent.

User preference / thesis state is outside the Gearbox-side persistence boundary. Values such as floor APY, HF floor, hold horizon, accepted oracle methodologies, concentration caps, and notification preferences are supplied by the user or the user's representative agent as `userThesis` / policy input. Gearbox-side product docs can depend on those inputs; they should not assume Gearbox stores or owns them.

Agents may enter **Decision sessions** autonomously when their user mandate allows it: for example, when new capital arrives, a campaign appears, or an existing monitoring session escalates to a full reallocation search. The Gearbox-side requirement is to support both user-triggered and agent-triggered Decision traversal, while keeping Preview / Execute boundaries explicit.

## Emergency scenario

An **Emergency session** starts when protocol or issuer state indicates a high probability that a user loss vector will materialise before a normal Analyze cycle completes. It is not an optimization shortcut.

Examples:

- Credit Account HF enters the danger band or projected HF crosses the user's floor under an active LT ramp;
- a forbidden-token / safe-pricing condition would make ordinary exit unsafe;
- a Credit Manager, facade, or pool enters an abnormal operating state that blocks normal action paths;
- RWA issuer state changes: own account frozen, KYC revoked / expired, redemption path blocked, or liquidator depth collapses;
- pool-side bad-debt or utilisation signals imply elevated risk of socialised loss or blocked exit.

Emergency mode may skip broad Analyze and move directly from Monitor to a safety proposal, but it still goes through Preview and the approval boundary in [[Agent execution boundaries]].

## Agent policy filter vs on-chain bot signer

Do not use one "whitelist" concept for both layers.

- **Agent policy filter** — user / agent-side rules controlling what the agent will search, rank, or surface. Gearbox cannot guarantee the LLM agent behaves well; this is part of the user's agent configuration and mandate.
- **Scoped bot signer** — on-chain permission scope for deterministic execution helpers. This is the Gearbox-relevant enforcement layer: allowed action classes, limits, safety floors, expiry, and stop conditions.

The product docs may consume both layers as inputs, but only the scoped bot signer is a Gearbox-side permission primitive.
