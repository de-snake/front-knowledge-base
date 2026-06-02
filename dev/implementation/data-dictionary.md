# Data dictionary

This dictionary names the logical fields implied by the canonical product flows. It is implementation-neutral: names are stable enough for API / schema design, but do not prescribe the physical database.

Conventions:

- `source_class`: `protocol`, `indexer`, `issuer_compliance`, `product_policy`, `user_agent_policy`, `computed_projection`, or `human_authored_copy`.
- `temporal_shape`: `snapshot`, `history`, `event_log`, `scheduled_change`, `policy_input`, `computed_projection`, or `command_result`.
- `unknown_state`: `not_applicable`, `unknown_non_blocking`, `unknown_review_required`, or `blocking`.
- Requirement IDs come from [[traceability-matrix]].

## Shared field envelope

All decision-driving facts should be returned with the shared metadata below, either at the object level or per field when freshness/source differs.

| Field | Type | Required | Source class | Temporal shape | Validation / semantics | Unknown state | Used by |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `as_of` | ISO datetime | yes | indexer / protocol / issuer_compliance | snapshot | Timestamp of the fact or aggregate. | `blocking` when absent on safety-critical facts. | all requirements |
| `source_class` | enum | yes | product_policy | snapshot | Provenance class for the fact. | `blocking` if omitted for verdict-driving fields. | all requirements |
| `source_ref` | string / URL / tx hash | conditional | protocol / indexer / issuer_compliance / human_authored_copy | snapshot | Raw source pointer where available. | `unknown_review_required` if unavailable for external diligence. | all requirements |
| `freshness_sla` | duration | conditional | product_policy | policy_input | Maximum tolerated age before field is stale. | `unknown_review_required` unless execution safety needs it, then `blocking`. | all Preview / Execute requirements |
| `confidence` | enum | conditional | product_policy | snapshot | `canonical`, `derived`, `external_attested`, `human_authored`, `unknown`. | `unknown_review_required`. | all requirements |

## Policy input fields

These are runtime inputs from the user, mandate, or representative agent. They are not Gearbox-side persistent state unless a separate user-profile product is explicitly scoped.

| Field | Type | Required | Source class | Temporal shape | Validation / semantics | Unknown state | Used by |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `user_policy.floor_apy` | decimal percent | conditional | user_agent_policy | policy_input | Minimum acceptable APY; LP uses composite at Discover, organic / incentive split at Analyze; CA uses net APY. | `blocking` for yield-gated funding; `unknown_review_required` for monitoring display. | `DR-LP-DISC-001`, `DR-LP-AN-Q1`, `DR-CA-DISC-001`, `DR-CA-AN-Q1` |
| `user_policy.hurdle_rate` | decimal percent | conditional | user_agent_policy | policy_input | CA net-return threshold. | `unknown_review_required`; do not classify CA returns as acceptable without it. | `DR-CA-AN-Q1`, `DR-CA-MON-Q2` |
| `user_policy.hf_floor` | decimal | conditional | user_agent_policy | policy_input | Minimum acceptable HF after open / action. | `blocking` before CA Preview readiness if absent. | `DR-CA-AN-Q2`, `DR-CA-PRE-001`, `DR-CA-MON-Q1` |
| `user_policy.emergency_hf_floor` | decimal | conditional | user_agent_policy | policy_input | Emergency routing floor. | `unknown_review_required`; emergency can still be manual if raw HF danger is visible. | `DR-CA-MON-Q1`, `DR-CA-MON-PROP-001` |
| `user_policy.hold_horizon` | duration | conditional | user_agent_policy | policy_input | Used for breakeven, LT-ramp, expiration, redemption windows, withdrawal queues. | `unknown_review_required`; `blocking` when action depends on horizon. | LP / CA Analyze and Monitor |
| `user_policy.accepted_oracle_methodologies[]` | enum[] | conditional | user_agent_policy | policy_input | User / mandate-accepted oracle categories. | `unknown_review_required`; blocks oracle-methodology verdict. | `DR-LP-MON-Q6`, `DR-CA-AN-Q2`, `DR-CA-MON-Q5` |
| `user_policy.concentration_caps` | object | conditional | user_agent_policy | policy_input | Max per pool, per strategy, per token, or per portfolio exposure. | `unknown_review_required`; no hidden default. | `DR-LP-PROP-001`, `DR-CA-PROP-001` |
| `user_policy.change_tolerance` | object | conditional | user_agent_policy | policy_input | Tolerance for material change frequency / severity. | `unknown_review_required`; material changes still shown. | `DR-LP-AN-Q5`, `DR-LP-MON-Q4`, `DR-CA-AN-Q5`, `DR-CA-MON-Q3` |
| `user_policy.issuer_control_policy` | object | conditional | user_agent_policy | policy_input | Accepted issuer / eligibility / liquidator-depth conditions. | `blocking` for automation on controlled assets. | RWA / compliance requirements |
| `user_policy.bot_policy` | object | conditional | user_agent_policy | policy_input | Scoped bot execution permissions. | `blocking` for bot Execute. | all Execute requirements |

## `PoolOpportunity`

| Field | Type | Required | Source class | Temporal shape | Validation / semantics | Unknown state | Used by |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `pool_id` | string | yes | protocol / indexer | snapshot | Stable pool identifier. | `blocking` | LP requirements |
| `chain` | enum / string | yes | protocol / indexer | snapshot | Chain where the pool lives. | `blocking` | `DR-LP-DISC-001` |
| `underlying_token` | token ref | yes | protocol | snapshot | Lend / withdraw token. | `blocking` | `DR-LP-DISC-001` |
| `title` | string | yes | human_authored_copy / indexer | snapshot | Human-readable label for shortlist. | `unknown_non_blocking` | `DR-LP-DISC-001` |
| `curator_id` | string | conditional | indexer | snapshot | Links to `CuratorProfile`. | `unknown_review_required` | `DR-LP-AN-Q4` |
| `yield.composite.current` | decimal percent | yes | indexer / computed_projection | snapshot | Headline current APY. | `blocking` for shortlist / yield verdict. | `DR-LP-DISC-001`, `DR-LP-AN-Q1`, `DR-LP-MON-Q1` |
| `yield.composite.90d_series` | decimal series | yes | indexer | history | Daily 90d APY trend. | `unknown_review_required` | `DR-LP-AN-Q1`, `DR-LP-MON-Q1` |
| `yield.organic.supply_rate.current` | decimal percent | yes | protocol / indexer | snapshot | Organic supply rate excluding incentives. | `unknown_review_required` | `DR-LP-AN-Q1` |
| `yield.organic.supply_rate.90d_series` | decimal series | conditional | indexer | history | Daily 90d organic history. | `unknown_review_required` | `DR-LP-AN-Q1` |
| `yield.incentive_layers[]` | `IncentiveLayer[]` | conditional | indexer / human_authored_copy | snapshot + history | Incentive components. Empty means no incentives, not unknown. | `unknown_review_required` when composite depends on incentives. | `DR-LP-AN-Q1`, `DR-LP-MON-Q1` |
| `available_liquidity` | token amount | yes | protocol / indexer | snapshot | Current withdrawable liquidity. | `blocking` for exit / Preview. | `DR-LP-AN-Q3`, `DR-LP-MON-Q2` |
| `expected_liquidity` | token amount | yes | protocol / indexer | snapshot | Expected pool liquidity / TVL denominator. | `blocking` | `DR-LP-AN-Q3` |
| `total_borrowed` | token amount | yes | protocol / indexer | snapshot | Current borrowed amount. | `blocking` | `DR-LP-AN-Q3` |
| `utilisation.current` | decimal percent | yes | computed_projection / indexer | snapshot | `total_borrowed / expected_liquidity`. | `blocking` | `DR-LP-AN-Q3`, `DR-LP-MON-Q2` |
| `utilisation.90d_series` | decimal series | conditional | indexer | history | Daily utilisation history. | `unknown_review_required` | `DR-LP-AN-Q3`, `DR-LP-MON-Q2` |
| `withdrawal_fee` | decimal percent | conditional | protocol | snapshot | Fee to withdraw. | `unknown_review_required` | `DR-LP-AN-Q3`, `DR-LP-MON-Q2`, LP Preview |
| `irm` | `InterestRateModel` | yes | protocol | snapshot | U / slope parameters. | `unknown_review_required`; current borrow economics may be incomplete. | `DR-LP-AN-Q3`, `DR-CA-AN-Q1` |
| `credit_managers[]` | `CreditManagerEnvelope[]` | yes | protocol / indexer | snapshot | CMs that can borrow from the pool. | `blocking` for exposure trace. | `DR-LP-AN-Q2`, `DR-LP-MON-Q3` |
| `quoted_token_exposures[]` | `TokenExposure[]` | yes | indexer / computed_projection | snapshot | Current and max exposure by token. | `unknown_review_required`; `blocking` when exposure verdict is required. | `DR-LP-AN-Q2`, `DR-LP-MON-Q3` |
| `insurance_fund_balance` | token / USD amount | conditional | protocol / indexer | snapshot + history | First-loss buffer. | `unknown_review_required` | `DR-LP-AN-Q2`, `DR-LP-MON-Q5`, RWA checks |
| `share_price.current` | decimal | yes | protocol / indexer | snapshot | Pool share price / exchange rate. | `unknown_review_required`; `blocking` before LP Preview if bad-debt canary cannot be checked. | `DR-LP-MON-Q5`, LP Preview |
| `share_price.90d_series` | decimal series | conditional | indexer | history | Daily share-price trend. | `unknown_review_required` | `DR-LP-MON-Q5` |

## Nested LP / pool types

| Field | Type | Required | Source class | Temporal shape | Validation / semantics | Unknown state | Used by |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `IncentiveLayer.source` | enum / string | yes | indexer | snapshot | `merkl`, protocol-specific, partner campaign, etc. | `unknown_review_required` | LP yield requirements |
| `IncentiveLayer.current_apy` | decimal percent | yes | indexer | snapshot | Current incentive contribution. | `unknown_review_required` | LP yield requirements |
| `IncentiveLayer.90d_series` | decimal series | conditional | indexer | history | Incentive trend. | `unknown_review_required` | LP yield requirements |
| `IncentiveLayer.expiry` | ISO datetime / null | conditional | indexer / human_authored_copy | scheduled_change | Campaign expiry; `null` means no known expiry. | `unknown_review_required` when material. | `DR-LP-AN-Q1`, `DR-LP-MON-Q1` |
| `IncentiveLayer.reference_url` | URL / null | conditional | human_authored_copy | snapshot | Campaign evidence. | `unknown_review_required` when material. | LP yield T2 |
| `TokenExposure.token` | token ref | yes | indexer | snapshot | Quoted / collateral token. | `blocking` | LP exposure requirements |
| `TokenExposure.current_exposure_usd` | decimal | yes | indexer / computed_projection | snapshot | Pool capital currently lent against this token. | `unknown_review_required` until derivation is confirmed. | `DR-LP-AN-Q2`, `DR-LP-MON-Q3` |
| `TokenExposure.max_exposure_usd` | decimal | yes | computed_projection | snapshot | `min(pool max debt; token quota limit; sum relevant CM debt limits)`. | `unknown_review_required` | `DR-LP-AN-Q2` |
| `TokenExposure.quota_limit` | token amount | yes | protocol | snapshot | Token quota cap. | `blocking` for max exposure. | `DR-LP-AN-Q2`, `DR-LP-MON-Q3` |
| `TokenExposure.quota_used` | token amount | yes | protocol / indexer | snapshot | Used quota. Verify whether equivalent to collateral-attributable debt. | `unknown_review_required` | `DR-LP-AN-Q2` |
| `TokenExposure.quota_rate` | decimal percent | conditional | protocol | snapshot + history | Rate charged for quota. | `unknown_review_required` | LP change feed, CA economics |

## `StrategyOpportunity`

| Field | Type | Required | Source class | Temporal shape | Validation / semantics | Unknown state | Used by |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `strategy_id` | string | yes | indexer | snapshot | Stable strategy identifier. | `blocking` | CA requirements |
| `credit_manager_id` | string | yes | protocol / indexer | snapshot | Owning Credit Manager. | `blocking` | CA requirements |
| `pool_id` | string | yes | protocol / indexer | snapshot | Funding pool. | `blocking` | CA economics / exit |
| `target_collateral[]` | token ref[] | yes | protocol / indexer | snapshot | Planned collateral set. | `blocking` | `DR-CA-AN-Q2` |
| `plain_language_description` | string | conditional | human_authored_copy | snapshot | Curator/platform description, surfaced verbatim with authorship. | `unknown_non_blocking` | `DR-CA-MON-Q3` |
| `max_leverage_yield` | decimal percent | conditional | computed_projection | snapshot | Headline leveraged yield for ranking. | `unknown_review_required` | `DR-CA-DISC-001` |
| `best_base_yield` | decimal percent | conditional | computed_projection | snapshot | Unleveraged comparison yield. | `unknown_non_blocking` | `DR-CA-DISC-001` |
| `collateral_yield.current` | decimal percent | yes | indexer / partner protocol | snapshot | Strategy collateral yield. | `blocking` for CA economics. | `DR-CA-AN-Q1`, `DR-CA-MON-Q2` |
| `borrow_apy.current` | decimal percent | yes | protocol / indexer | snapshot | Current borrow rate. | `blocking` | `DR-CA-AN-Q1`, `DR-CA-MON-Q2` |
| `quota_rates[]` | rate by token | conditional | protocol | snapshot + history | Quota cost per enabled token. | `blocking` when token quota affects economics. | `DR-CA-AN-Q1`, `DR-CA-MON-Q2` |
| `entry_cost` | object | conditional | computed_projection | snapshot | Swap impact, quota increase fee, gas. | `blocking` before Preview readiness. | `DR-CA-AN-Q1`, `DR-CA-PRE-001` |
| `exit_cost` | object | conditional | computed_projection | snapshot + history | Exit swap / unwind friction. | `unknown_review_required`; blocking for exit Preview. | `DR-CA-AN-Q1`, `DR-CA-AN-Q3` |
| `breakeven_horizon` | duration | conditional | computed_projection | snapshot | `(entry + exit cost) / daily net yield`. | `unknown_review_required` | `DR-CA-AN-Q1` |
| `net_apy_projection` | decimal percent | yes | computed_projection | snapshot | `(collateralYield × leverage) − borrowRate − quotaRate − fees`. | `blocking` for funding decision. | `DR-CA-AN-Q1`, `DR-CA-PROP-001` |

## `CreditManagerEnvelope`

| Field | Type | Required | Source class | Temporal shape | Validation / semantics | Unknown state | Used by |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `credit_manager_id` | string | yes | protocol / indexer | snapshot | Stable CM identifier. | `blocking` | CA and LP requirements |
| `paused` | boolean | yes | protocol | snapshot + event_log | CM pause status. | `blocking` | `DR-CA-AN-Q4`, `DR-CA-MON-Q4`, LP change feeds |
| `facade_paused` | boolean | conditional | protocol | snapshot + event_log | Facade operational pause. | `blocking` for ordinary CA action. | `DR-CA-MON-Q4` |
| `per_block_borrow_capacity` | token amount | conditional | protocol | snapshot | Zero means no new borrows. | `unknown_review_required`; `blocking` for open/increase leverage. | `DR-CA-AN-Q4` |
| `current_debt` | token amount | yes | protocol / indexer | snapshot | Current CM debt. | `blocking` | CA / LP exposure requirements |
| `debt_limit` | token amount | yes | protocol | snapshot + event_log | CM debt cap. | `blocking` for exposure / sizing. | LP exposure, CA envelope |
| `expiration_timestamp` | ISO datetime / null | conditional | protocol | scheduled_change | Null for non-expirable CMs. | `unknown_review_required`; blocking if expirable and unknown. | `DR-CA-AN-Q4`, `DR-CA-MON-Q4` |
| `min_debt` | token amount | conditional | protocol | snapshot | Minimum debt after partial unwind. | `blocking` for partial exit Preview. | `DR-CA-AN-Q3`, `DR-CA-MON-Q4`, `DR-CA-MON-PRE-001` |
| `max_debt` | token amount | conditional | protocol | snapshot | Max debt / sizing cap. | `unknown_review_required` | `DR-CA-PROP-001` |
| `compliance_gated_execution` | boolean | yes | protocol / issuer_compliance | snapshot | Whether compliance-gated path is required. | `blocking` for bot eligibility if unknown. | `DR-CA-AN-Q4`, Execute requirements |
| `bot_delegation_allowed` | boolean | conditional | protocol / product_policy | snapshot | Whether bot path is allowed. | `blocking` for bot Execute. | Execute requirements |

## `SafetyEnvelope`

| Field | Type | Required | Source class | Temporal shape | Validation / semantics | Unknown state | Used by |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `lt_by_token[]` | decimal percent by token | yes | protocol | snapshot | Liquidation threshold. | `blocking` for HF / max leverage. | `DR-CA-AN-Q2`, `DR-CA-MON-Q1` |
| `lt_ramp_schedule[]` | schedule[] | conditional | protocol / indexer | scheduled_change | Current LT, target LT, ramp start, ramp duration, direction. | `unknown_review_required`; `blocking` when held/planned token has ramp. | `DR-CA-AN-Q2`, `DR-CA-MON-Q1` |
| `max_leverage` | decimal | yes | computed_projection | snapshot | `1 / (1 − LT)` for relevant token / basket. | `blocking` | `DR-CA-PROP-001` |
| `post_open_hf_projection` | decimal | conditional | computed_projection | snapshot | HF at target leverage. | `blocking` for CA Preview. | `DR-CA-AN-Q2`, `DR-CA-PRE-001` |
| `safe_pricing_exit_hf` | decimal | conditional | computed_projection | snapshot | HF under `min(main, reserve)` for applicable tokens. | `blocking` for exit safety when applicable. | `DR-CA-AN-Q2`, `DR-CA-MON-Q1` |
| `forbidden_tokens[]` | token ref[] | conditional | protocol / indexer | snapshot + event_log | Current and pending forbidden status. | `unknown_review_required`; blocking for affected exit Preview. | `DR-CA-AN-Q2`, `DR-CA-MON-Q1` |
| `delayed_withdrawal_paths[]` | path[] | conditional | protocol / product_policy | snapshot + event_log | Supported withdrawal assets, queue timing, claim mechanism. | `unknown_review_required`; blocking for exit requiring claim. | `DR-CA-AN-Q3`, `DR-CA-MON-Q4` |

## `CreditAccountPosition`

| Field | Type | Required | Source class | Temporal shape | Validation / semantics | Unknown state | Used by |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `credit_account` | address | yes | protocol | snapshot | Credit Account address. | `blocking` | CA monitor requirements |
| `owner` | address | yes | protocol | snapshot | Owner / signer context. | `blocking` | Execute / rewards attribution |
| `health_factor` | decimal | yes | protocol / computed_projection | snapshot + history | Current HF. | `blocking` for safety / CA Preview. | `DR-CA-MON-Q1` |
| `twv_usd` | decimal | conditional | computed_projection | snapshot | Total weighted value; used for derivation. | `unknown_review_required` | `DR-CA-MON-Q1` |
| `total_debt` | token amount | yes | protocol / indexer | snapshot + history | Current debt. | `blocking` | `DR-CA-MON-Q1`, `DR-CA-MON-Q4` |
| `debt_breakdown[]` | object[] | conditional | indexer | snapshot + history | Borrow / quota / fees by source. | `unknown_review_required` | `DR-CA-MON-Q1`, `DR-CA-MON-Q2` |
| `balances_by_token[]` | token amount[] | yes | protocol / indexer | snapshot + history | Held collateral balances. | `blocking` | CA monitor requirements |
| `leverage` | decimal | yes | computed_projection | snapshot + history | Current leverage. | `blocking` for leverage actions. | `DR-CA-MON-Q1`, `DR-CA-MON-PROP-001` |
| `liquidation_distance` | object | conditional | computed_projection | snapshot | Price move to liquidation per dominant collateral. | `unknown_review_required` | `DR-CA-MON-Q1` |
| `time_to_liquidation_flat_prices` | duration | conditional | computed_projection | snapshot | Interest-only extrapolation. | `unknown_non_blocking` | `DR-CA-MON-Q1` |
| `account_value_30d_series` | decimal series | conditional | indexer | history | PnL sparkline. | `unknown_review_required` | `DR-CA-MON-Q2` |
| `yield_source_decomposition` | object | conditional | computed_projection | snapshot + history | Farming, rewards, appreciation, borrow, quota, fees. | `unknown_review_required` | `DR-CA-MON-Q2` |
| `claimable_rewards[]` | reward[] | conditional | indexer / partner protocol | snapshot | Claimable rewards and source. | `unknown_review_required`; blocking for claim Preview. | `DR-CA-MON-Q2`, `DR-CA-MON-PRE-001` |
| `merkl_owner_wallet_attribution[]` | reward[] | conditional | indexer | snapshot | Rewards accruing to owner wallet, linked to CA. | `unknown_review_required` | `DR-CA-MON-Q2` |
| `phantom_tokens[]` | token ref[] | conditional | protocol / indexer | snapshot | Non-transferable wrappers / unstaking mechanics. | `unknown_review_required` | `DR-CA-MON-Q4` |
| `active_bots[]` | bot permission[] | conditional | protocol / indexer | snapshot | Bot permissions currently active. | `unknown_review_required`; unexpected broad bot is manual review. | `DR-CA-MON-Q4`, Execute requirements |

## `OracleTelemetry`

| Field | Type | Required | Source class | Temporal shape | Validation / semantics | Unknown state | Used by |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `token` | token ref | yes | protocol / indexer | snapshot | Token being priced. | `blocking` | oracle requirements |
| `oracle_category` | enum | conditional | protocol / product_policy | snapshot | `market`, `nav`, `hardcoded`, `hybrid`, etc.; no universal verdict. | `unknown_review_required` | LP / CA oracle requirements |
| `main_oracle` | address / ref | yes | protocol | snapshot + event_log | Main oracle source. | `blocking` for safe pricing / freshness. | oracle requirements |
| `reserve_oracle` | address / ref / null | conditional | protocol | snapshot + event_log | Reserve oracle where present. | `unknown_review_required`; blocking for safe-pricing computation when required. | CA safe-pricing requirements |
| `last_update` | ISO datetime | yes | protocol / indexer | snapshot | Last price update timestamp. | `blocking` for Preview / Execute. | oracle freshness requirements |
| `staleness_window` | duration | yes | protocol / product_policy | snapshot | Max permitted oracle age. | `blocking` | oracle freshness requirements |
| `main_price` | decimal | yes | protocol / indexer | snapshot + history | Main oracle price. | `blocking` | LP / CA oracle and HF requirements |
| `reserve_price` | decimal / null | conditional | protocol / indexer | snapshot + history | Reserve price. | `unknown_review_required`; blocking for safe pricing. | CA safe-pricing requirements |
| `methodology_changed_since` | ISO datetime / null | conditional | event_log | event_log | Change since prior monitor baseline. | `unknown_review_required` | LP Monitor Q6, CA Monitor Q5 |

## `CuratorProfile`

| Field | Type | Required | Source class | Temporal shape | Validation / semantics | Unknown state | Used by |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `curator_id` | string | yes | indexer | snapshot | Stable curator identifier. | `blocking` when pool/CM has curator. | curator requirements |
| `display_name` | string | conditional | human_authored_copy | snapshot | Human-readable name. | `unknown_review_required` | `DR-LP-AN-Q4`, `DR-CA-AN-Q4` |
| `identity` | object | conditional | human_authored_copy / external_attested | snapshot | Name, URL, socials, regulatory status, doxxed team if source-backed. | `unknown_review_required` | curator requirements |
| `governance_mechanism` | object | conditional | protocol / indexer | snapshot + event_log | EOA / multisig / DAO / timelock / delegated authority. | `unknown_review_required` | curator requirements |
| `first_operation_date` | date | conditional | indexer | snapshot | Lindy / track-record anchor. | `unknown_non_blocking` | T2 curator checks |
| `total_aum_usd` | decimal | conditional | indexer | snapshot + history | Operating breadth. | `unknown_non_blocking` | T2 curator checks |
| `cumulative_bad_debt_usd` | decimal | conditional | indexer | history | Aggregate bad-debt record. | `unknown_review_required` | `DR-LP-AN-Q4`, `DR-CA-AN-Q4` |
| `bad_debt_incidents[]` | incident[] | conditional | indexer / human_authored_copy | event_log | Dated loss incidents. | `unknown_review_required` | `DR-LP-MON-Q5` |
| `liquidity_incidents[]` | incident[] | conditional | indexer / human_authored_copy | event_log | Paper-solvent but unusable events. | `unknown_review_required` | `DR-LP-AN-Q4` |

## `EventFeedItem` / `GovernanceChange`

| Field | Type | Required | Source class | Temporal shape | Validation / semantics | Unknown state | Used by |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `event_id` | string | yes | indexer | event_log | Stable ID for dedupe. | `blocking` for continuity. | change-feed requirements |
| `scope` | enum | yes | indexer | event_log | `pool`, `credit_manager`, `token`, `oracle`, `issuer_program`, `curator_profile`. | `blocking` | change-feed requirements |
| `change_type` | enum | yes | indexer / product_policy | event_log | Domain event type. | `blocking` | change-feed requirements |
| `classification_hint` | enum | conditional | product_policy | computed_projection | `material`, `info_only`, `needs_policy`. | `unknown_review_required` | Analyze / Monitor Q5/Q4/Q3 |
| `actor_or_source` | string | conditional | protocol / issuer_compliance / indexer | event_log | Curator, Safe, timelock, issuer, oracle admin, indexer. | `unknown_review_required` | change-feed requirements |
| `effective_at` | ISO datetime | conditional | protocol / indexer | scheduled_change | When the change applies. | `unknown_review_required`; blocking when queued change affects execution. | change-feed requirements |
| `detected_at` | ISO datetime | yes | indexer | event_log | When feed detected it. | `blocking` | monitor deltas |
| `before` / `after` | typed object | conditional | indexer | event_log | Diff payload. | `unknown_review_required` | material classification |
| `affected_entities[]` | refs[] | yes | indexer | event_log | Pools, CMs, tokens, positions. | `blocking` | filtered feeds |

## `RwaAssetProfile` / `RwaComplianceProfile`

| Field | Type | Required | Source class | Temporal shape | Validation / semantics | Unknown state | Used by |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `issuer_id` | string | conditional | issuer_compliance | snapshot | Issuer / program identity. | `blocking` for issuer-controlled assets. | RWA requirements |
| `issuer_status` | enum / string | conditional | issuer_compliance | snapshot + event_log | Active, suspended, regulatory event, unknown. | `unknown_review_required`; can be blocking. | RWA requirements |
| `kyc_required` | boolean | conditional | issuer_compliance / protocol | snapshot | Whether KYC is required. | `blocking` if unknown for controlled assets. | CA RWA requirements |
| `eligibility_valid` | boolean | conditional | issuer_compliance | snapshot | User / wallet eligibility. | `blocking` for transfer/exit actions. | `DR-CA-MON-Q6`, Execute |
| `eligibility_expires_at` | ISO datetime / null | conditional | issuer_compliance | scheduled_change | Expiry relevant to hold horizon. | `unknown_review_required`; blocking near action. | RWA requirements |
| `own_frozen_status` | boolean | conditional | issuer_compliance | snapshot + event_log | Whether this account/wallet is frozen. | `blocking` if frozen or unknown for own controlled position. | `DR-CA-MON-Q6` |
| `frozen_account_count` | integer | conditional | issuer_compliance / indexer | history / event_log | Count of frozen accounts. | `unknown_review_required` | `DR-LP-MON-Q7` |
| `aggregate_frozen_debt` | USD / token amount | conditional | issuer_compliance / indexer | history / event_log | Frozen debt exposure. | `unknown_review_required` | `DR-LP-MON-Q7` |
| `investor_registry_status` | enum | conditional | issuer_compliance | snapshot + event_log | Current investor binding / reassignment risk. | `unknown_review_required`; blocking when transfer depends on it. | `DR-CA-MON-Q6` |
| `redemption_windows[]` | schedule[] | conditional | issuer_compliance | scheduled_change | Redemption / notice windows. | `unknown_review_required`; blocking for exit path. | RWA exit requirements |
| `eligible_liquidator_count` | integer | conditional | issuer_compliance | snapshot + history | Liquidator set count. | `unknown_review_required` | LP / CA RWA requirements |
| `eligible_liquidator_depth_usd` | decimal | conditional | issuer_compliance / computed_projection | snapshot + history | Depth of eligible liquidator capacity. | `unknown_review_required`; blocking if policy requires minimum. | LP / CA RWA requirements |

## Write-side artifacts

Detailed semantics are in [[data-write-spec]].

| Field | Type | Required | Source class | Temporal shape | Validation / semantics | Unknown state | Used by |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ActionDecision.action_class` | enum | yes | product_policy / computed_projection | snapshot | `deposit`, `top_up`, `partial_exit`, `full_exit`, `open_ca`, `add_collateral`, `reduce_leverage`, etc. | `blocking` | Propose requirements |
| `ActionDecision.amounts` | object | conditional | computed_projection | snapshot | Sized amounts by action. | `blocking` for Preview. | Propose / Preview |
| `ActionDecision.route` | route object / null | conditional | computed_projection | snapshot | Adapter / route selection. | `blocking` for swap-leg actions. | CA route requirements |
| `TransactionPreview.preview_id` | string | yes | command_result | command_result | Stable Preview ID. | `blocking` | all Preview / Execute |
| `TransactionPreview.status` | enum | yes | command_result | command_result | `pass`, `pass_with_review_warnings`, `fail_blocking`, `expired`. | `blocking` if absent. | all Preview / Execute |
| `TransactionPreview.execution_package_hash` | hash | yes | command_result | command_result | Hash of exact approved tx package. | `blocking` | all Execute |
| `TransactionPreview.raw_txs[]` | tx[] | yes | command_result | command_result | Target, calldata, value, chain, signer context. | `blocking` | all Execute |
| `ExecutionReceipt.submitted_package_hash` | hash | yes | command_result | command_result | Must match Preview hash. | `blocking` if mismatch. | all Execute |
| `ExecutionReceipt.monitor_baseline_update` | object | yes | command_result | command_result | New position baseline for monitoring. | `unknown_review_required` if absent after failed tx; required after success. | Monitor handoff |
