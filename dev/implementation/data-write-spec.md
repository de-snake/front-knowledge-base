# Data write spec

This spec isolates state-changing behavior from read data. The product docs use the same loop everywhere:

```text
Propose → Preview → Execute → Monitor
```

Read models can explain risk. Write models must prove that the exact action package approved by the user is the package submitted for execution, and that blocked / stale / unknown states cannot silently proceed.

## Source inventory

| Source ID | Source | Write relevance |
| --- | --- | --- |
| `SRC-DEC-001` | [[Entry points]] | Agent execution boundary, approval modes, emergency session shape, bot policy filter. |
| `SRC-FOUND-001` | [[Basic info and definitions]] | Canonical loop, Preview / Execute invariants, stage handoff rules. |
| `SRC-LP-ENTRY` | [[Pool deposit]] | LP deposit proposal, Preview, Execute, Monitor handoff. |
| `SRC-LP-MON` | [[Pool monitoring]] | LP top-up / partial-exit / full-exit action classes. |
| `SRC-CA-ENTRY` | [[Credit Account opening]] | Credit Account open, route selection, multicall Preview, Execute. |
| `SRC-CA-MON` | [[Credit Account management]] | Add collateral, reduce leverage, increase leverage, claim, rebalance, close, emergency-mode actions. |
| `SRC-REF-CA-MGMT` | [[Credit Account management - reference]] | CA action-class palette, emergency mode, bot interactions. |
| `SRC-REF-CA-OPEN` | [[Credit Account opening - reference]] | Multicall Preview mechanics, adapter constraints, compliance-gated execution. |

## Execution boundary

| Mode | Allowed without human signature? | Required data state |
| --- | --- | --- |
| Read / Analyze / Monitor | Yes | Read freshness rules from [[data-read-spec]]. |
| Propose | Yes | Current enough facts to size and explain a candidate action. |
| Preview | Yes | Deterministic simulation package, warning set, before/after state, and expiry. |
| Execute with human approval | Only after user approval | `TransactionPreview.status = pass` or user explicitly accepts non-blocking warnings. |
| Execute with scoped bot policy | Only if pre-authorized | Bot policy covers action class, size, threshold, route, expiry, and issuer/compliance branch. |
| Emergency action | Human approval or scoped emergency bot policy | Single concrete stabilizing action; Preview integrity still required. |

Issuer-controlled collateral, frozen status, invalid eligibility, missing execution-package integrity, stale oracle data for execution, or missing user policy for a safety-critical action blocks automation.

## Command model

### Shared `ActionDecision`

`ActionDecision` is the final non-transactional proposal. It is not executable until Preview binds it to concrete transactions.

| Field | Meaning |
| --- | --- |
| `action_decision_id` | Stable ID for the proposal. |
| `position_id` / `candidate_id` | Position or opportunity being acted on. |
| `action_class` | Product action class. |
| `amounts` | Deposit, withdrawal, collateral, repay, borrow, or claim amounts. |
| `target_state` | Target HF, leverage, exposure, position size, or exit state. |
| `route` | Adapter set or pool route chosen by Stage 3 when applicable. |
| `rationale` | Decision story from the product docs. |
| `policy_inputs_used[]` | User / mandate policies used for thresholds and sizing. |
| `source_snapshots[]` | Required read facts and `as_of` timestamps. |
| `blocking_gaps[]` | Empty before Preview; otherwise Preview must fail. |

### LP commands

| Command | Source action classes | Preconditions | Writes / effects |
| --- | --- | --- | --- |
| `preview_pool_deposit` | LP entry `deposit` | Selected `PoolResearchMemo` passes due diligence; user amount known; no blocking gaps. | Creates `TransactionPreview` for deposit. |
| `preview_pool_top_up` | LP monitor `top_up` | Existing LP position; concentration cap supplied or reviewed. | Creates Preview for additional deposit. |
| `preview_pool_partial_exit` | LP monitor `partial_exit` | Withdrawable amount and policy margin known; position size known. | Creates Preview for partial withdrawal. |
| `preview_pool_full_exit` | LP monitor `full_exit` | Exit route available; blocking issuer / oracle / liquidity state absent or explicitly handled. | Creates Preview for full withdrawal. |
| `execute_pool_action` | Any approved LP Preview | Preview not expired; submitted package hash matches approved package hash. | Submits transaction package; emits `ExecutionReceipt`; refreshes monitoring baseline. |

LP actions do not have a special emergency shortcut by default. The product docs intentionally contrast LP exit/action routing with Credit Account emergency behavior.

### Credit Account commands

| Command | Source action classes | Preconditions | Writes / effects |
| --- | --- | --- | --- |
| `preview_open_credit_account` | CA entry `open_ca` | `CreditAccountResearchMemo` passes; target leverage / HF policy known or reviewed; route selected. | Creates multicall Preview for account open and entry route. |
| `preview_add_collateral` | CA monitor `add_collateral` / emergency action | Current HF, target HF, accepted collateral, and amount available. | Creates Preview for collateral add. |
| `preview_reduce_leverage` | CA monitor `reduce_leverage` / emergency action | Repay source, target leverage / HF, route, and min-debt constraints known. | Creates Preview for repayment / deleverage route. |
| `preview_increase_leverage` | CA monitor `increase_leverage` | HF floor, max leverage, net APY, route, and borrow liquidity known. | Creates Preview for additional borrow + route. |
| `preview_change_strategy` | CA monitor `change_strategy` / `rebalance` | Exit and entry routes known; adapter set selected; price-impact budget approved. | Creates Preview for route multicall. |
| `preview_partial_exit` | CA monitor `partial_exit` | Partial-exit feasibility under `minDebt`, route, and withdrawal queue state known. | Creates Preview for partial unwind. |
| `preview_full_exit` | CA monitor `full_exit` / emergency exit | Exit route, safe-pricing HF, issuer / eligibility branch, and withdrawal claims known. | Creates Preview for close / unwind package. |
| `preview_claim` | CA monitor `claim` | Claimable rewards / withdrawals known and attributable to CA or owner wallet. | Creates Preview for claim transaction(s). |
| `execute_credit_account_action` | Any approved CA Preview | Preview not expired; package hash matches; no blocking issuer / oracle / policy gap emerged since Preview. | Submits transaction package; emits `ExecutionReceipt`; refreshes monitoring baseline. |

## `TransactionPreview`

Preview is the highest-leverage missing type family. It is the integrity gate between analysis and money movement.

| Field | Meaning |
| --- | --- |
| `preview_id` | Stable preview identifier. |
| `action_decision_id` | Proposal this Preview implements. |
| `position_id` / `candidate_id` | Affected position or candidate. |
| `action_class` | Product action class. |
| `status` | `pass`, `pass_with_review_warnings`, `fail_blocking`, `expired`. |
| `created_at`, `expires_at` | Preview validity window. |
| `read_snapshot_hash` | Hash of decision-driving read facts and policy inputs. |
| `execution_package_hash` | Hash of the exact transaction package to be approved. |
| `approval_mode` | `human_signature`, `scoped_bot_policy`, `emergency_human`, `emergency_bot_policy`. |
| `raw_txs[]` | Chain transaction objects with target, calldata, value, chain, signer context. |
| `route[]` | Adapter / pool route legs where relevant. |
| `before_after` | Human-readable and machine-readable current → projected values. |
| `warnings[]` | Severity, source, blocking flag, user-facing text, required acknowledgement. |
| `simulation` | Pass/fail, expected state deltas, failure reason, gas, revert classification. |
| `issuer_compliance_checks` | Eligibility / freeze / transfer / redemption checks where relevant. |
| `oracle_freshness_checks` | Execution-time freshness and staleness checks. |
| `policy_checks` | User / bot policy thresholds used for approval. |

### Before / after contract

| Position type | Required before / after fields |
| --- | --- |
| LP deposit / top-up | Shares, deposit amount, pool exposure, utilisation, withdrawable liquidity, composite APY. |
| LP exit | Shares, withdrawal amount, remaining value, withdrawal fee, expected received asset. |
| CA open | Equity, debt, leverage, HF, liquidation distance, net APY, collateral composition, entry fees. |
| CA add collateral / reduce leverage | HF, leverage, debt, equity, liquidation distance, target floor, emergency flag when relevant. |
| CA increase leverage / rebalance | HF, leverage, net APY, collateral composition, route price impact, quota / borrow rate. |
| CA partial / full exit | Debt, equity, route, safe-pricing exit HF, min-debt feasibility, expected received assets, claim readiness. |
| Claim | Claimable amount, receiving wallet, reward source, post-claim pending state. |

## Integrity binding

Execution must prove that it submits the approved package.

```text
ActionDecision
  → TransactionPreview(read_snapshot_hash, execution_package_hash, expires_at)
  → User approval / bot-policy authorization
  → Execute only if package hash and freshness checks still match
  → ExecutionReceipt(submitted_package_hash, tx_hash, post_state)
```

Execute fails if:

- `preview_id` is unknown or expired;
- `execution_package_hash` differs from the approved package;
- a blocking warning was not acknowledged or cannot be acknowledged;
- a safety-critical source fact is stale at execution time;
- issuer / eligibility / freeze state changed into a blocking state;
- bot policy does not cover this exact action class, amount, route, target, and expiry.

## Error taxonomy

| Tier | Meaning | Examples | Product response |
| --- | --- | --- | --- |
| Actionable | User / agent can change input and retry. | Amount too large, min-debt violation, route price impact exceeds budget, missing approval. | Return corrective proposal or require adjusted Preview. |
| Retryable with different route | Current route failed but another valid route may exist. | Adapter quote stale, route liquidity moved, partner protocol route reverted. | Re-run route selection and Preview. |
| Blocking / escalate | Agent cannot safely fix. | Frozen account, invalid eligibility, stale oracle with no fresh update, unexpected permission state, Preview hash mismatch. | Stop automation; show blocker and escalation path. |
| Infrastructure | Data or execution system failed. | Indexer unavailable, simulation RPC failed, transaction submission unavailable. | Do not infer success; retry read-only or ask for human review. |

## Bot-policy contract

A scoped bot policy must be treated as an approval boundary, not a recommendation.

| Field | Meaning |
| --- | --- |
| `policy_id` | Stable policy identifier. |
| `position_scope` | Position(s), pool(s), or Credit Manager(s) covered. |
| `allowed_action_classes[]` | Exact classes allowed. |
| `amount_limits` | Absolute and relative caps. |
| `target_thresholds` | User-approved HF, leverage, APY, exposure, or exit thresholds. |
| `route_constraints` | Allowed adapters / max price impact / asset paths. |
| `issuer_compliance_constraints` | Whether compliance-gated assets are excluded or human-only. |
| `expires_at` | Policy expiry. |
| `notification_rules` | User-visible notification before / after action. |

Compliance-gated Credit Account management is human-in-the-loop unless the policy explicitly covers that execution path and the issuer/compliance fields are current.

## Execution receipt

| Field | Meaning |
| --- | --- |
| `receipt_id`, `preview_id`, `tx_hash`, `chain`, `submitted_at` | Execution identity. |
| `submitted_package_hash` | Must match approved `execution_package_hash`. |
| `status` | `submitted`, `confirmed`, `failed`, `reverted`, `replaced`. |
| `actual_state_delta` | Machine-readable post-state delta. |
| `actual_transfers[]` | Token movements where available. |
| `failure_reason` | Error taxonomy item when failed. |
| `monitor_baseline_update` | New baseline for the next `MonitoringSnapshot`. |
| `source_refs[]` | Transaction hash, simulation ID, logs. |

## Verification scenarios

| Scenario | Required result |
| --- | --- |
| Preview expires before Execute | Execute rejected with `expired_preview`. |
| Route quote changes after Preview | Execute rejected or new Preview required if package hash / freshness invalid. |
| User approves one package but client submits modified calldata | Execute rejected by hash mismatch. |
| Account becomes frozen between Preview and Execute | Execute blocked; issuer-resolution path shown. |
| Oracle freshness check fails at execution | Execute blocked or fresh oracle update required before new Preview. |
| Emergency add-collateral action | Still has Preview, before/after HF, package hash, and human / scoped policy approval. |
| LP partial exit larger than withdrawable policy margin | Preview fails with actionable sizing correction. |
| CA partial exit would violate `minDebt` | Preview fails with full-exit or no-action alternatives. |
