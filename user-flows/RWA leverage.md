# RWA leverage (CA × RWA variant)

This is not a separate product universe. It is the RWA-specific overlay on [[Credit Account opening]] and [[Credit Account monitoring]].

The base flow remains a Credit Account flow: the user opens or manages an isolated leveraged position. The RWA variant adds issuer, eligibility, redemption, transferability, and liquidation constraints that must be visible before the user commits capital.

## Job statement

> **When I** want leveraged exposure to a tokenized security or issuer-controlled collateral,
> **I want to** see the same Credit Account economics and safety envelope plus the issuer / compliance conditions that can affect transfer, exit, liquidation, and automation,
> **so I can** decide whether the extra yield or exposure is worth the additional operational and compliance risk.

## Applies when

Use this overlay when any candidate pool or Credit Account strategy has material exposure to tokenized securities, issuer-controlled assets, redemption-window assets, or collateral that can be frozen, reassigned, restricted, or redeemed through a non-atomic process.

## What changes vs ordinary CA flow

| Area | Ordinary CA flow | RWA variant |
| --- | --- | --- |
| Eligibility | User can generally enter if protocol route is executable. | User must also satisfy eligibility / compliance state for the asset path. |
| Exit | Exit is mostly route, liquidity, oracle, and adapter feasibility. | Exit may depend on redemption windows, claim readiness, issuer operations, and transfer restrictions. |
| Liquidation | Liquidation depends on HF, collateral value, and available liquidator path. | Liquidation also depends on eligible liquidator depth and whether the collateral can be transferred or claimed. |
| Automation | Bot execution may be allowed for narrow maintenance actions. | Compliance-gated actions are human-in-the-loop by default. |
| Monitoring | Monitor checks HF, APY, rule changes, operations, and oracle state. | Monitor also checks issuer state, freeze state, redemption state, and eligibility drift. |

## Stage overlay

### Stage 1 · Discover

RWA candidates remain part of the unified opportunity surface. They should not be hidden by default, but they must be labelled clearly.

Additional Discover fields:

| Field | What the user needs to know |
| --- | --- |
| Asset program | Which tokenized-security / issuer-controlled asset family is involved. |
| Access label | Whether the user appears eligible, ineligible, or unknown. |
| Redemption label | Whether exit is instant, delayed, windowed, claim-based, or unknown. |
| Automation label | Whether this candidate is human-only or automation-compatible. |

If access or redemption state is unknown, the candidate can still be shown, but it cannot receive a clean “ready to execute” label.

### Stage 2 · Analyze

RWA Analyze extends [[Credit Account opening#Stage 2 · Analyze — CA due diligence]] with an explicit platform-layer risk profile.

| Layer | What the agent checks | Why it matters |
| --- | --- | --- |
| Asset / issuer | Issuer status, terms, redemption process, calendar, and operational history. | The asset can carry risks not visible from protocol state alone. |
| Compliance / eligibility | Whether the user's path is eligible and whether eligibility can drift. | Entry, transfer, exit, and liquidation can fail for non-market reasons. |
| Liquidity / liquidation | Whether there are enough eligible liquidators and credible exit paths under stress. | A technically solvent position can still be hard to unwind. |
| Redemption / claim state | Whether collateral is ordinary transferable collateral, in a redemption process, or claimable. | Exit timing and liquidation path change materially by state. |

Analyze output must separate:

- protocol-observable state;
- issuer / compliance state;
- market / liquidity state;
- user policy judgment.

### Stage 3 · Propose

The proposed action must include an RWA constraint summary.

| Constraint | Required in proposal |
| --- | --- |
| Eligibility | Whether entry appears allowed, blocked, or unknown. |
| Execution mode | Human-only, bot-allowed, or blocked. |
| Exit assumption | Expected exit route and timing class. |
| Liquidation assumption | Whether eligible liquidator depth appears sufficient. |
| Unknowns | Any issuer, eligibility, redemption, or transferability fields missing from the decision. |

If a candidate is attractive economically but has unresolved issuer / eligibility unknowns, the correct proposal can be `skip_for_now` or `manual_review`, not only “open.”

### Stage 4 · Preview

RWA Preview extends [[Preview contract]] with compliance and redemption checks.

Preview must show:

| Area | Required user-facing output |
| --- | --- |
| Entry validity | Whether the action appears allowed for the current user / path. |
| Transferability | Whether the relevant asset can be transferred, held, redeemed, or claimed under current state. |
| Freeze / restriction state | Whether any relevant account or asset path is frozen, restricted, or unknown. |
| Redemption state | Current queue, window, claim readiness, or blocking reason. |
| Liquidation path | Whether liquidation appears feasible under the assumed eligible-liquidator set. |
| Approval mode | Human-only, bot-allowed, or blocked. |

RWA Preview cannot treat unknown issuer or compliance state as safe.

### Stage 5 · Execute

RWA Execute is human-in-the-loop by default.

The user should see:

- what compliance-gated path they are approving;
- which position or action it affects;
- whether the action changes eligibility, redemption, or transferability assumptions;
- what state will be monitored after confirmation.

Bot execution is blocked unless the user has explicitly granted a narrow policy for the exact market, action class, and condition set.

### Stage 6 · Monitor

RWA Monitor extends [[Credit Account monitoring#Stage 6 · Monitor (CA)]] and [[Pool monitoring#Stage 6 · Monitor (Pool)]].

Additional monitoring questions:

| Question | Default outcome |
| --- | --- |
| Is eligibility still valid? | Yellow or red if invalid / unknown. |
| Has freeze or restriction state changed? | Red for affected position paths. |
| Is the redemption window still compatible with the user's plan? | Yellow if delayed; red if incompatible. |
| Is claim readiness moving as expected? | Yellow if delayed; red if blocked. |
| Is eligible-liquidator depth still acceptable? | Yellow or red based on product threshold. |
| Did issuer / regulatory state materially change? | Focused Analyze rerun. |

RWA Monitor should route material drift to focused Analyze or Propose. It should not wait for HF alone to deteriorate.

## Data requirements trace

This overlay depends on these rows in [[Data requirements and to-dos]]:

- RWA / KYC extension;
- RWA issuer-state feed;
- RWA whitelisted-liquidator threshold;
- withdrawal queue / claim-readiness feed;
- KYC-gated execution routing metadata;
- oracle telemetry + methodology feed;
- market risk history.

## Product-language boundary

Use product-facing language in this flow:

- compliance-gated execution;
- issuer state;
- eligibility state;
- redemption window;
- claim readiness;
- eligible liquidator depth;
- transfer restriction;
- freeze state.

Exact contract, function, event, and ABI names belong in [[Data requirements and to-dos]] or implementation notes, not in this user-facing RWA overlay.

## Acceptance checklist

RWA leverage docs are ready when:

- RWA is treated as a Credit Account variant, not a separate flow;
- every issuer / eligibility / redemption unknown is visible;
- Preview blocks on missing required compliance state;
- Execute is human-in-the-loop by default;
- Monitor watches issuer and redemption drift, not only HF;
- data gaps are linked back to [[Data requirements and to-dos]].
