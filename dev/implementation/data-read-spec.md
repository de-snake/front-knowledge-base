# Data read spec

This spec converts the canonical product flows into backend-facing read requirements. It preserves the chain:

```text
user moment → product / agent question → required fact → provenance → temporal shape → read model → missing-data behavior
```

The source of truth for product reasoning remains `user/`. This file only specifies the data surfaces needed to answer those questions safely.

## Source inventory

| Source ID | Source | Canonicality | Used for |
| --- | --- | --- | --- |
| `SRC-FOUND-001` | [[Basic info and definitions]] | canonical runtime | Canonical loop, handoff vocabulary, Credit Account / pool vocabulary, Preview / Execute invariants. |
| `SRC-FOUND-002` | [[Personas and audience]] | canonical runtime | LP and Credit Account operator loss vectors and priority of questions. |
| `SRC-FOUND-003` | [[Position risk and monitoring]] | canonical runtime | Threshold policy, missing-data policy, monitoring output shape. |
| `SRC-DEC-001` | [[Entry points]] | canonical runtime | Session modes, agent execution boundary, emergency routing, bot policy filter. |
| `SRC-DEC-002` | [[Three-layer progressive disclosure]] | canonical runtime | Glance / Analyze / Act grouping for read-model presentation. |
| `SRC-LP-ENTRY` | [[Pool deposit]] | canonical runtime | LP Discover, Analyze, Propose, Preview, Execute, Monitor handoff. |
| `SRC-LP-MON` | [[Pool monitoring]] | canonical runtime | LP ownership monitoring, focused re-run, action routing. |
| `SRC-CA-ENTRY` | [[Credit Account opening]] | canonical runtime | Credit Account Discover, Analyze, Propose, Preview, Execute, Monitor handoff. |
| `SRC-CA-MON` | [[Credit Account management]] | canonical runtime | Credit Account ownership monitoring, focused re-run, action routing, emergency branch. |
| `SRC-REF-*` | `user/references/* - reference.md` | canonical drill | Drill-level evidence and trigger details. |
| `SRC-DEV-GAPS` | [[Data requirements and to-dos]] | dev-side gap register | Existing implementation gaps and unresolved notes. |

Historical `dev/planning/` material is intentionally excluded unless explicitly promoted.

## Source and unknown-state contract

Every field used in ranking, verdicts, Preview, automation, or alerts must carry:

| Attribute | Meaning |
| --- | --- |
| `source_class` | One of `protocol`, `indexer`, `issuer_compliance`, `product_policy`, `user_agent_policy`, `computed_projection`, `human_authored_copy`. |
| `as_of` | Timestamp for the fact or computed projection. |
| `freshness_sla` | Maximum allowed age before the consumer must mark the field stale. |
| `confidence` | `canonical`, `derived`, `external_attested`, `human_authored`, or `unknown`. |
| `unknown_state` | `not_applicable`, `unknown_non_blocking`, `unknown_review_required`, or `blocking`. |
| `used_by` | Requirement IDs from [[traceability-matrix]]. |

### Unknown-state rules

| State | Use when | Product behavior |
| --- | --- | --- |
| `not_applicable` | Field does not apply to this asset / pool / Credit Manager. | Hide or show as not applicable. |
| `unknown_non_blocking` | Field is useful for explanation but not required for the current decision. | Continue, mention missing data only in Analyze. |
| `unknown_review_required` | Field affects confidence but not immediate execution safety. | Continue in read-only / analysis mode, require review before acting. |
| `blocking` | Field affects user funds, execution safety, issuer / eligibility state, or Preview integrity. | Do not recommend or automate the affected action. |

Do not encode hidden defaults for user floors, APY bands, concentration caps, oracle methodology acceptance, leverage tolerance, liquidation distance, or issuer-controlled collateral risk. Model those as explicit `user_agent_policy` inputs or missing-policy blockers.

## Stage handoff artifacts

| Artifact | Stage boundary | Read role | Minimal fields |
| --- | --- | --- | --- |
| `OpportunityCandidate` | Discover → Analyze | Identifier-only shortlist; Stage 2 re-fetches current facts. | `id`, `kind`, `title`, `chain`, `underlying`, `currentCompositeApy`, `as_of`. |
| `ResearchMemo` | Analyze → Propose | Evidence-backed due diligence verdict for one candidate. | `candidate_id`, `persona`, `question_verdicts[]`, `blocking_gaps[]`, `risk_summary`, `recommended_target`, `source_refs[]`. |
| `FocusedAnalyzeReport` | Monitor → Propose | Targeted re-run result after drift. | `position_id`, `triggering_monitor_q`, `rerun_question_refs[]`, `position_thesis_verdict`, `recommended_action`, `blocking_gaps[]`. |
| `ProposedAction` | Propose → Preview | Umbrella proposal artifact. Entry flows produce concrete `AllocationDecision` values; ownership / monitoring flows produce concrete `ActionDecision` values. | `action_class`, `amount`, `target_state`, `route`, `rationale`, `policy_inputs_used[]`, `is_emergency`. |
| `TransactionPreview` | Preview → Execute | Covered in [[data-write-spec]]. | Read consumers need `preview_id`, `status`, `warnings[]`, `before_after`, `expires_at`. |
| `ExecutionReceipt` | Execute → Monitor | Execution outcome and monitoring baseline update. | `tx_hash`, `status`, `submitted_package_hash`, `actual_transfers`, `new_position_snapshot`, `monitor_baseline`. |
| `MonitoringSnapshot` | Monitor loop | Current state and drift verdict. | `position_id`, `as_of`, `question_verdicts[]`, `alerts[]`, `is_emergency`, `source_refs[]`. |
| `MonitorAlert` | Monitor → user / Propose | Specific drift or blocker. | `alert_type`, `severity`, `source_question`, `actionability`, `blocking_reason`, `suggested_back_edge`. |

## Core read models

### `PoolOpportunity`

Serves LP Discover and LP Analyze.

| Field group | Fields | Temporal shape | Source class | Consumers |
| --- | --- | --- | --- | --- |
| Identity | `pool_id`, `chain`, `underlying_token`, `title`, `curator_id` | snapshot | protocol / indexer | `DR-LP-DISC-001`, `DR-LP-AN-Q4` |
| Yield | `yield.composite.current`, `yield.composite.90d_series`, `yield.organic.current`, `yield.organic.90d_series`, `yield.incentive_layers[]` | snapshot + history | indexer / human-authored campaign refs | `DR-LP-AN-Q1`, `DR-LP-MON-Q1` |
| Liquidity | `available_liquidity`, `expected_liquidity`, `total_borrowed`, `utilisation`, `withdrawal_fee` | snapshot + history | protocol / indexer | `DR-LP-AN-Q3`, `DR-LP-MON-Q2` |
| Exposure | `credit_managers[]`, `quoted_token_exposures[]`, `dominant_tokens[]`, `insurance_fund_balance` | snapshot + history | indexer | `DR-LP-AN-Q2`, `DR-LP-MON-Q3`, `DR-LP-MON-Q5` |
| Change feed | `pending_changes[]`, `recent_changes[]`, `change_frequency_summary` | event log + aggregate | indexer | `DR-LP-AN-Q5`, `DR-LP-MON-Q4` |
| Oracle dependency | `oracle_telemetry_by_token[]`, `dominant_oracle_categories[]` | snapshot + history + event log | protocol / indexer | `DR-LP-AN-Q2`, `DR-LP-MON-Q6` |
| Issuer branch | `issuer_controlled_exposure`, `frozen_account_delta`, `eligible_liquidator_depth`, `issuer_status` | snapshot + event log | issuer_compliance / indexer | `DR-LP-MON-Q7` |

### `StrategyOpportunity`

Serves Credit Account Discover and Credit Account Analyze.

| Field group | Fields | Temporal shape | Source class | Consumers |
| --- | --- | --- | --- | --- |
| Identity | `strategy_id`, `chain`, `credit_manager_id`, `pool_id`, `target_collateral[]`, `plain_language_description` | snapshot | protocol / human_authored_copy | `DR-CA-DISC-001`, `DR-CA-MON-Q3` |
| Economics | `collateral_yield`, `borrow_rate`, `quota_rates[]`, `entry_fees`, `exit_friction`, `net_apy_projection`, `breakeven_horizon` | snapshot + history | protocol / indexer / computed_projection | `DR-CA-AN-Q1`, `DR-CA-MON-Q2` |
| Safety envelope | `lt_by_token`, `lt_ramp_schedule[]`, `max_leverage`, `health_factor_projection`, `safe_pricing_exit_hf` | snapshot + scheduled changes | protocol / computed_projection | `DR-CA-AN-Q2`, `DR-CA-MON-Q1` |
| Exit feasibility | `adapter_routes[]`, `route_quotes[]`, `min_debt`, `borrowable_liquidity`, `withdrawal_paths[]` | snapshot + history | protocol / indexer / computed_projection | `DR-CA-AN-Q3`, `DR-CA-MON-Q4` |
| Operational envelope | `paused`, `facade_paused`, `per_block_borrow_capacity`, `debt_limit`, `current_debt`, `expiration_timestamp`, `compliance_gated_execution` | snapshot + event log | protocol / indexer | `DR-CA-AN-Q4`, `DR-CA-MON-Q4` |
| Change feed | `pending_cm_changes[]`, `recent_cm_changes[]`, `change_frequency_summary` | event log + aggregate | indexer | `DR-CA-AN-Q5`, `DR-CA-MON-Q3` |
| Issuer branch | `rwa_asset_profile`, `rwa_compliance_profile`, `eligible_liquidator_depth`, `redemption_calendar`, `investor_registry_status` | snapshot + event log | issuer_compliance | `DR-CA-AN-Q2`, `DR-CA-MON-Q6` |

### `LpPosition`

Serves LP monitoring and LP action sizing.

| Field group | Fields | Temporal shape | Source class | Consumers |
| --- | --- | --- | --- | --- |
| Position identity | `position_id`, `owner`, `pool_id`, `shares`, `current_value_usd`, `entry_as_of`, `baseline_thesis` | snapshot | protocol / user_agent_policy | `DR-LP-MON-Q1`, `DR-LP-PROP-001` |
| Returns | `realized_return`, `unrealized_return`, `reward_accruals`, `share_price_series` | snapshot + history | protocol / indexer | `DR-LP-MON-Q1`, `DR-LP-MON-Q5` |
| Exit sizing | `withdrawable_now`, `position_vs_withdrawable_margin`, `withdrawal_fee`, `utilisation_30d_series` | snapshot + history | computed_projection / indexer | `DR-LP-MON-Q2`, `DR-LP-PROP-001` |
| Thesis comparison | `top3_exposure_snapshot`, `top3_delta_since_last_check`, `new_credit_managers_since_last_check`, `policy_inputs_used` | snapshot + event log | indexer / user_agent_policy | `DR-LP-MON-Q3` |
| Continuity | `agent_log.previous_check.as_of`, `previous_question_verdicts[]`, `accepted_risk_notes[]` | event log | user_agent_policy / product_policy | all monitor requirements |

### `CreditAccountPosition`

Serves Credit Account monitoring, emergency routing, and action sizing.

| Field group | Fields | Temporal shape | Source class | Consumers |
| --- | --- | --- | --- | --- |
| Position identity | `credit_account`, `owner`, `credit_manager_id`, `pool_id`, `strategy_id`, `opened_at`, `baseline_thesis` | snapshot | protocol / user_agent_policy | `DR-CA-MON-Q1`, `DR-CA-PROP-001` |
| Health and debt | `health_factor`, `twv_usd`, `total_debt`, `debt_breakdown`, `liquidation_distance`, `time_to_liquidation_flat_prices` | snapshot + history | protocol / indexer / computed_projection | `DR-CA-MON-Q1` |
| Held assets | `balances_by_token[]`, `quota_by_token[]`, `forbidden_overlap[]`, `phantom_tokens[]`, `delayed_withdrawal_queues[]` | snapshot + event log | protocol / indexer | `DR-CA-MON-Q1`, `DR-CA-MON-Q4` |
| Returns and PnL | `account_value_30d_series`, `net_apy`, `yield_source_decomposition`, `claimable_rewards`, `merkl_owner_wallet_attribution` | snapshot + history | indexer / computed_projection | `DR-CA-MON-Q2` |
| Operational state | `expiration_status`, `facade_pause`, `emergency_liquidator_status`, `active_bots[]`, `partial_exit_feasibility` | snapshot + event log | protocol / indexer | `DR-CA-MON-Q4`, `DR-CA-PROP-001` |
| Oracle state | `oracle_telemetry_by_held_token[]`, `oracle_methodology_change_since_last_check` | snapshot + event log + history | protocol / indexer | `DR-CA-MON-Q5` |
| Issuer state | `own_frozen_status`, `eligibility_validity`, `investor_registry_status`, `redemption_window`, `eligible_liquidator_depth_delta` | snapshot + event log | issuer_compliance | `DR-CA-MON-Q6` |

## Shared support models

### `CuratorProfile`

This is currently one of the largest cross-flow gaps.

| Field | Temporal shape | Source class | Used by |
| --- | --- | --- | --- |
| `curator_id`, `display_name`, `legal_or_public_identity`, `profile_url` | snapshot | human_authored_copy / external attestation | LP Q4, CA Q4 |
| `governance_mechanism`, `delegated_authorities`, `safe_or_timelock_scope` | snapshot + event log | protocol / indexer | LP Q4, CA Q4, monitor change feeds |
| `first_operation_date`, `total_aum_usd`, `cumulative_bad_debt_usd` | snapshot + history | indexer | LP Q4, CA Q4 |
| `bad_debt_incidents[]`, `liquidity_incidents[]` | event log | indexer / human-authored postmortem | LP Q4, LP Monitor Q5 |
| `external_references[]` | snapshot | human_authored_copy | explanatory drill only |

Unknown curator identity is `unknown_review_required` for analysis and `blocking` if the user / mandate requires named curator approval before funding.

### `EventFeedItem` / `GovernanceChange`

One stream should serve LP and Credit Account readers.

| Field | Meaning |
| --- | --- |
| `event_id` | Stable ID for dedupe and continuity. |
| `scope` | `pool`, `credit_manager`, `token`, `oracle`, `issuer_program`, `curator_profile`. |
| `change_type` | Domain-specific enum: `cm_added`, `debt_limit_changed`, `quota_rate_changed`, `lt_changed`, `lt_ramp_scheduled`, `irm_changed`, `oracle_changed`, `forbidden_token_changed`, `cm_paused`, `facade_paused`, `withdrawal_path_changed`, `issuer_freeze_delta`, etc. |
| `classification_hint` | `material`, `info_only`, or `needs_policy`; product layer may override based on user policy. |
| `actor_or_source` | Curator, Safe, timelock, issuer, oracle admin, indexer. |
| `effective_at` | When the change applies. |
| `detected_at` | When the feed detected it. |
| `before`, `after` | Typed diff payload where available. |
| `affected_entities[]` | Pools, Credit Managers, tokens, positions. |
| `source_ref` | Transaction hash, Safe tx, timelock item, issuer notice, or indexer source. |

### `HistoricalSeries`

| Series | Granularity | Retention | Consumers | Missing behavior |
| --- | --- | --- | --- | --- |
| Composite APY, organic APY, incentive APY | daily | 90d minimum | LP Q1, LP Monitor Q1 | `unknown_review_required`; do not classify sustainability. |
| Utilisation, TVL, available liquidity, borrowed | daily + current | 90d minimum | LP Q3, LP Monitor Q2 | current missing is `blocking`; history missing is review-required. |
| Borrow rate, quota rate | daily + current | 30d / 90d | CA Q1, CA Monitor Q2 | current missing is `blocking` for open / increase leverage. |
| Oracle main / reserve price, freshness | current + daily | 90d | LP Q2/Q6, CA Q2/Q5 | current freshness missing is `blocking` for controlled execution. |
| Share price | current + daily | 90d | LP Monitor Q5 | current missing is review-required; drop detection unavailable. |
| Account value / PnL | current + daily or per transaction | 30d minimum | CA Monitor Q2 | missing is review-required; returns Glance cannot show PnL. |
| Price impact / route quote samples | current + sampled history | 90d where feasible | CA Q3, Preview | current quote missing is `blocking` for state-changing action. |

### `OracleTelemetry`

| Field | Meaning |
| --- | --- |
| `token`, `oracle_category`, `main_oracle`, `reserve_oracle`, `last_update`, `staleness_window`, `main_price`, `reserve_price`, `divergence`, `methodology_changed_since`, `source_confidence` |

Product interpretation is policy-driven. The feed must not store universal “good oracle” or “bad oracle” verdicts.

### `RwaAssetProfile` and `RwaComplianceProfile`

Applies as an extension to ordinary Pool / Credit Account lifecycle docs, not a standalone product universe.

| Field group | Fields | Missing behavior |
| --- | --- | --- |
| Issuer state | `issuer_id`, `issuer_status`, `program_terms_url`, `regulatory_event_notes` | review-required or blocking depending on exposure. |
| Eligibility | `kyc_required`, `eligibility_valid`, `eligibility_expires_at`, `investor_registry_status` | blocking for actions that require receiving or transferring controlled assets. |
| Freeze / transfer controls | `own_frozen_status`, `frozen_account_count`, `aggregate_frozen_debt`, `transfer_restrictions` | own frozen status unknown is blocking. |
| Redemption / claim | `redemption_windows[]`, `notice_deadline`, `pending_claims[]`, `claimable_at`, `claim_readiness` | blocking for exit route claims. |
| Liquidator depth | `eligible_liquidator_count`, `eligible_liquidator_depth_usd`, `depth_delta_since_last_check` | review-required; blocking if product policy requires minimum depth before exposure. |

## Read-model grouping by user / agent task

| Task | Read model | Primary product source |
| --- | --- | --- |
| LP shortlist | `PoolOpportunitySearchResult` | [[Pool deposit#Stage 1 · Discover (Pool)]] |
| LP due diligence | `PoolResearchMemo` | [[Pool deposit#Stage 2 · Analyze — LP due diligence]] |
| LP monitor | `LpMonitoringSnapshot` | [[Pool monitoring#Stage 6 · Monitor (Pool)]] |
| LP action proposal | `LpActionDecisionInput` | [[Pool monitoring#Stage 3 · Propose (Pool) — Action Committee]] |
| Credit Account shortlist | `StrategyOpportunitySearchResult` | [[Credit Account opening#Stage 1 · Discover (CA)]] |
| Credit Account due diligence | `CreditAccountResearchMemo` | [[Credit Account opening#Stage 2 · Analyze — CA due diligence]] |
| Credit Account monitor | `CreditAccountMonitoringSnapshot` | [[Credit Account management#Stage 6 · Monitor (CA)]] |
| Credit Account action proposal | `CreditAccountActionDecisionInput` | [[Credit Account management#Stage 3 · Propose (CA) — Action Committee]] |
| Preview | `TransactionPreviewReadModel` | [[data-write-spec]] |

## Open read-spec gaps

| Gap | Decision blocked | Priority |
| --- | --- | --- |
| `CuratorProfile` endpoint | LP / Credit Account curator trust and track record | P1 |
| Unified `EventFeedItem` / `GovernanceChange` stream | All “what changed?” monitor questions | P1 |
| `TransactionPreview` read model | Preview / Execute safety | P0; detailed in [[data-write-spec]] |
| PnL / returns endpoint | Credit Account monitoring returns Glance | P1 |
| RWA issuer / eligibility / freeze / redemption state | Tokenized-security exposure and compliance-gated actions | P0 for controlled collateral |
| Oracle telemetry and methodology history | Oracle freshness / methodology fit gates | P1 |
| Withdrawal queue / claim-readiness feed | Credit Account exit feasibility and monitoring claims | P1 |
| Eligible-liquidator depth feed | Issuer-controlled collateral liquidation risk | P1 |
