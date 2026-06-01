# Data contracts

This document is the product-level contract registry for the Gearbox front / agent experience.

It answers: **what shape of information must exist for each stage of the loop to work?**

It does not replace [[Data requirements and to-dos]]. This file names the product contract and interpretation rules. [[Data requirements and to-dos]] stays the backend-facing punch list with implementation hints and exact source names.

## Contract principles

1. **Each stage owns its handoff.** A stage should pass only the minimal object needed by the next stage, not a full data dump.
2. **Protocol state is not the same as product judgment.** Protocol-readable facts can say what is executable. Product contracts decide whether the result is acceptable for a user.
3. **External data must be labelled.** Rewards, issuer state, governance history, curator history, oracle methodology labels, and user policy are not silently treated as protocol facts.
4. **Preview is mandatory before execution.** Any action that changes user state must produce a Preview contract before it can move to Execute.
5. **RWA fields are extensions, not a separate universe.** RWA pools and RWA-backed Credit Accounts reuse the Pool / Credit Account contracts with extra issuer, compliance, redemption, and liquidation fields.

## Stage contract ladder

| Stage | Product contract | Job | Handoff |
| --- | --- | --- | --- |
| Discover | `OpportunityCandidate` | Find candidate pools and strategies that satisfy coarse user filters. | Candidate ids and reason for inclusion. |
| Analyze | `ResearchMemo` | Explain whether each candidate is viable and why. | Ranked candidates with evidence, caveats, and missing-data labels. |
| Propose | `ProposedAction` | Convert the selected thesis into one or more concrete actions. | Action intent, amount, route class, constraints, and fallback. |
| Preview | `TransactionPreview` | Simulate the exact action package and classify warnings. | Pass/fail verdict plus before/after state and raw execution package. |
| Execute | `ExecutionReceipt` | Submit the approved previewed action. | Confirmation, failure reason, or monitor handoff. |
| Monitor | `MonitoringSnapshot` / `MonitorAlert` | Check whether the thesis still holds and route material drift. | No-op, focused Analyze rerun, proposed action, or emergency path. |

## Core contracts

### `OpportunityCandidate`

Used by Stage 1 Discover.

Minimum fields:

| Field | Meaning | Source status |
| --- | --- | --- |
| `id` | Stable candidate handle used by later stages. | Required. |
| `kind` | Pool opportunity or Credit Account strategy opportunity. | Required. |
| `chain` | Network where the candidate lives. | Required. |
| `asset_class` | User-visible asset class or collateral family. | Product taxonomy. |
| `headline_yield` | Comparable headline yield for initial ranking. | Requires yield composition source. |
| `access_status` | Whether the user can access the candidate. | Protocol + compliance / app policy. |
| `sizing_fit` | Whether candidate capacity fits the requested size. | Protocol + liquidity / indexer data. |
| `reason_for_inclusion` | Short human-readable reason the candidate survived discovery. | Product reasoning. |

### `ResearchMemo`

Used by Stage 2 Analyze.

Minimum fields:

| Field | Meaning | Source status |
| --- | --- | --- |
| `candidate_id` | Candidate being analyzed. | From Discover. |
| `headline_verdict` | Keep / reject / needs more data. | Product judgment. |
| `economics` | Yield, borrow cost, quota cost, incentives, and breakeven. | Protocol + rewards / market data. |
| `risk_profile` | Asset, oracle, curator, liquidity, and operational risks. | Mixed sources. |
| `exit_feasibility` | Whether the user can exit at size and under what timing assumptions. | Protocol + liquidity / withdrawal data. |
| `change_watch` | Pending or recent changes that could alter the thesis. | Governance / config event feed. |
| `missing_data` | Explicit list of unknowns that block a confident verdict. | Product policy. |
| `evidence_links` | Links to source docs, dashboards, or internal data references. | Required when available. |

### `ProposedAction`

Used by Stage 3 Propose.

Minimum fields:

| Field | Meaning | Source status |
| --- | --- | --- |
| `action_class` | Deposit, withdraw, open Credit Account, add collateral, reduce leverage, close, claim, no-op, or emergency variant. | Product action vocabulary. |
| `user_goal` | What user problem the action solves. | Product reasoning. |
| `amount` | Amount or sizing rule. | User input or product sizing. |
| `target` | Pool, Credit Manager, Credit Account, or route target. | Protocol handle. |
| `constraints` | Max slippage, HF floor, APY floor, timing, allowed assets. | User policy + product defaults. |
| `fallback` | What to do if Preview fails. | Product policy. |
| `requires_human_approval` | Whether Execute must be human-in-the-loop. | Execution boundary policy. |

### `TransactionPreview`

Used by Stage 4 Preview. Detailed rules live in [[Preview contract]].

Minimum fields:

| Field | Meaning | Source status |
| --- | --- | --- |
| `preview_id` | Stable handle tying simulation to the exact action package. | Required. |
| `action_class` | Proposed action being previewed. | From Propose. |
| `before_state` | Relevant current state. | Protocol / backend. |
| `after_state` | Simulated post-action state. | Simulation. |
| `warnings` | Classified warnings with severity and user-facing explanation. | Product policy over simulation. |
| `pass_fail` | Whether this preview can proceed to Execute. | Hard gate. |
| `execution_package` | The exact package that must be signed/submitted if approved. | Backend / wallet layer. |
| `integrity_hash` | Binds the user-approved preview to the execution package. | Required for Execute. |

### `ExecutionReceipt`

Used by Stage 5 Execute.

Minimum fields:

| Field | Meaning | Source status |
| --- | --- | --- |
| `preview_id` | Preview that authorized the action. | Required. |
| `submitted_by` | Human wallet, delegated bot, or system actor. | Execution layer. |
| `tx_hash` | Submitted transaction hash when applicable. | Chain. |
| `status` | Submitted, confirmed, failed, replaced, or cancelled. | Chain / wallet. |
| `post_action_state` | State used to re-enter Monitor. | Backend / protocol. |
| `failure_reason` | User-facing reason when execution fails. | Wallet / simulation / protocol. |

### `MonitoringSnapshot`

Used by Stage 6 Monitor.

Minimum fields:

| Field | Meaning | Source status |
| --- | --- | --- |
| `position_id` | Pool position or Credit Account being monitored. | Required. |
| `verdicts` | Per-question green / yellow / red verdicts. | Product policy over current state. |
| `material_changes` | Changes since last check that matter to the thesis. | Agent log + event feeds. |
| `drift_attribution` | Why a key metric moved. | Protocol + indexer + product logic. |
| `recommended_next_stage` | No-op, focused Analyze, Propose, Preview, Execute, or Emergency. | Product routing. |
| `alerts` | Actionable warnings for the user. | Product policy. |
| `unknowns` | Data missing at monitor time. | Required when incomplete. |

## Extension contracts

### RWA extension

Attach to Pool and Credit Account contracts when the candidate or position has tokenized-securities / issuer-controlled collateral exposure.

| Field | Meaning | Source status |
| --- | --- | --- |
| `issuer_status` | Whether the issuer / asset program is operating normally. | Issuer / indexer. |
| `eligibility_status` | Whether the user is currently eligible for the asset path. | Compliance / issuer source. |
| `freeze_status` | Whether the relevant account, asset, or program is frozen. | Issuer / integration source. |
| `redemption_window` | Next available redemption path and timing. | Issuer / redemption source. |
| `eligible_liquidator_depth` | Whether liquidation can realistically happen if needed. | Product / market data. |
| `execution_mode` | Human-only, bot-allowed, or blocked. | Agent execution policy. |

### Oracle extension

Attach when an asset has non-trivial oracle risk.

| Field | Meaning | Source status |
| --- | --- | --- |
| `methodology_label` | Product-readable oracle category and methodology. | Backend taxonomy. |
| `freshness` | Last update and staleness classification. | Backend / oracle source. |
| `main_reserve_divergence` | Difference between normal and conservative pricing paths. | Protocol / indexer. |
| `on_demand_update_available` | Whether the Preview can include needed price updates. | Backend / execution layer. |

## Open contract gaps

These are the highest-priority gaps to keep aligned with [[Data requirements and to-dos]]:

1. APY / rewards / yield-composition feed.
2. Governance and config event feed.
3. Market risk history.
4. RWA issuer-state feed.
5. Oracle telemetry and methodology feed.
6. Withdrawal queue / claim-readiness feed.
7. User/account policy input store.
8. Health Factor attribution for Credit Account monitoring.

## Acceptance checklist

A contract is ready for implementation when:

- every field has a source owner;
- protocol facts, indexer facts, issuer facts, and product policy are labelled separately;
- unknown / unavailable states have explicit user-facing behavior;
- Preview fields are sufficient to decide whether Execute is allowed;
- Monitor can explain why it routed to no-op, Analyze, Propose, or Emergency.
