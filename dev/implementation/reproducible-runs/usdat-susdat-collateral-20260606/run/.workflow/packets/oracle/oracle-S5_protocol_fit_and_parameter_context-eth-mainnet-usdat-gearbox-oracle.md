# Stage packet — S5_protocol_fit_and_parameter_context — eth-mainnet-usdat-gearbox-oracle

Launcher: Codex: use this packet as the complete task brief; write only to the declared run root, then return the envelope.

## Scope

- Workflow: `oracle-analysis-v1`
- Child run root: `dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/run/oracle-analysis`
- Artifact directory: `tokens/eth-mainnet-usdat-gearbox-oracle`
- Objective: Should USDat or sUSDat be treated as acceptable Gearbox Credit Account collateral candidates on Ethereum mainnet when borrowing USDC at a 9% borrow-rate assumption?

## Known inputs

Input paths:
- `tokens/eth-mainnet-usdat-gearbox-oracle/oracle/stress-tradeoff-analysis.md`

Optional references:
- `user/references/workflows/oracle-analysis/workflow.json`
- `user/references/workflows/oracle-analysis/output-structure.md`
- `user/references/workflows/oracle-analysis/gearbox-price-feed-parsing.md`

## Blocking unknowns

- `oracle.eth-mainnet-usdat-gearbox-oracle.market_or_credit_manager` — `input_missing` from `oracle_scopes[0].market_or_credit_manager`; Name the evaluated Gearbox market/Credit Manager/pool, or record a deterministic not_applicable rule.
- `oracle.eth-mainnet-usdat-gearbox-oracle.position_size` — `input_missing` from `oracle_scopes[0].position_size`; Provide a size/scenario range or preserve input_missing before route, liquidity, or liquidation conclusions.

## Protocol investigation adapter

Adapter: `gearbox.oracle-market-parameter-context.v1` (Gearbox v1.0.0)

Purpose: Require reusable Gearbox market, credit-manager, oracle, PFS, allowed-token, liquidation-threshold, and route investigation facts before an Analyze -> Propose workflow can treat a market or route as absent.

Required fact states:
- `found`
- `not_applicable`
- `input_missing`
- `not_investigated`
- `investigated_no_result`
- `source_unavailable`
- `source_inconclusive`
- `contradicted`

Required no-result proof classes:
- `registry_checked`
- `api_or_contract_query_attempted`
- `network_context_named`
- `evidence_path_present`

No-market/no-route semantics:
- A missing Gearbox market/credit manager or execution/liquidation route is valid only as state=investigated_no_result and only when the proof names the registry checked, API or contract query attempted, network/context, and a run-local evidence path. If the worker did not investigate, the state is not_investigated, never investigated_no_result.

Protocol-required facts:
- `gearbox.market_or_credit_manager` — Market or Credit Manager
  - discovery: Check Gearbox market / Credit Manager registries for the asset and chain.; Query configured protocol APIs or contracts when a registry does not resolve the fact.; Record the chain/network and evidence artifact path for every positive or negative result.
  - negative search: Registry lookup by token and chain.; Protocol API or on-chain contract query for supported market / Credit Manager entries.
  - no-result proof required: yes
  - no-result semantics: No market is not an omission: record investigated_no_result only after registry, API/contract, network/context, and evidence-path proof.
- `gearbox.oracle_feed` — Oracle / main feed path
  - discovery: Resolve Gearbox oracle / price feed path for the market or Credit Manager context.; Unwrap child/source primitives instead of stopping at a top-level label.
  - negative search: not specified
  - no-result proof required: no
  - no-result semantics: Use the adapter-level no-market/no-route semantics when this fact is absent.
- `gearbox.reserve_feed` — Reserve feed path
  - discovery: Check whether an alternate/reserve feed exists for the resolved oracle context.
  - negative search: not specified
  - no-result proof required: no
  - no-result semantics: Use the adapter-level no-market/no-route semantics when this fact is absent.
- `gearbox.safe_pricing_rule` — Safe-pricing rule
  - discovery: Identify whether Gearbox applies conservative source selection or other safe-pricing rules.
  - negative search: not specified
  - no-result proof required: no
  - no-result semantics: Use the adapter-level no-market/no-route semantics when this fact is absent.
- `gearbox.exit_health_factor` — Exit Health Factor implication
  - discovery: Explain borrower exit-HF sensitivity for the feed / parameter context.
  - negative search: not specified
  - no-result proof required: no
  - no-result semantics: Use the adapter-level no-market/no-route semantics when this fact is absent.
- `gearbox.liquidation_threshold` — Liquidation Threshold
  - discovery: Resolve LT/LTV-style protocol parameter context from the market, Credit Manager, or collateral config.; Do not infer missing LT from generic token data.
  - negative search: not specified
  - no-result proof required: no
  - no-result semantics: Use the adapter-level no-market/no-route semantics when this fact is absent.
- `gearbox.liquidation_threshold_ramp` — Liquidation Threshold ramp
  - discovery: Check whether LT is static, ramping, or governed by a scheduled parameter update.
  - negative search: not specified
  - no-result proof required: no
  - no-result semantics: Use the adapter-level no-market/no-route semantics when this fact is absent.
- `gearbox.max_leverage` — Max leverage implied by LT
  - discovery: If LT is known, state the implied max leverage or mark the dependency unresolved.
  - negative search: not specified
  - no-result proof required: no
  - no-result semantics: Use the adapter-level no-market/no-route semantics when this fact is absent.
- `gearbox.staleness_bounds_timestamp` — Staleness, bounds, and timestamp controls
  - discovery: Check stale-report, bound, and timestamp handling for the feed/source context.
  - negative search: not specified
  - no-result proof required: no
  - no-result semantics: Use the adapter-level no-market/no-route semantics when this fact is absent.
- `gearbox.feed_swap_timelock` — Feed swap / reserve / timelock status
  - discovery: Identify update authority, reserve path, feed swap path, and timelock/governance delay where available.
  - negative search: not specified
  - no-result proof required: no
  - no-result semantics: Use the adapter-level no-market/no-route semantics when this fact is absent.
- `gearbox.delayed_withdrawal_branch` — Delayed-withdrawal branch interaction
  - discovery: Check whether delayed withdrawals change the oracle or liquidation risk branch.
  - negative search: not specified
  - no-result proof required: no
  - no-result semantics: Use the adapter-level no-market/no-route semantics when this fact is absent.
- `gearbox.allowed_token_status` — Allowed-token / forbidden-token status
  - discovery: Check allowed-token / forbidden-token collateral status for the market or Credit Manager context.; Do not treat generic ERC-20 transferability as protocol allowlisting.
  - negative search: not specified
  - no-result proof required: no
  - no-result semantics: Use the adapter-level no-market/no-route semantics when this fact is absent.
- `gearbox.issuer_controlled_branch` — Issuer-controlled branch interaction
  - discovery: Check freeze, blacklist, reassignment, issuer-control, or RWA control branches where relevant.
  - negative search: not specified
  - no-result proof required: no
  - no-result semantics: Use the adapter-level no-market/no-route semantics when this fact is absent.
- `gearbox.pfs_availability` — PFS chain / token availability and update status
  - discovery: Check Price Feed Store chain/token availability and add/update status for the asset context.
  - negative search: not specified
  - no-result proof required: no
  - no-result semantics: Use the adapter-level no-market/no-route semantics when this fact is absent.
- `gearbox.feed_update_authority` — Instance Owner or feed-update authority
  - discovery: Identify Instance Owner, feed-update authority, or owner-controlled update path when available.
  - negative search: not specified
  - no-result proof required: no
  - no-result semantics: Use the adapter-level no-market/no-route semantics when this fact is absent.
- `gearbox.route_availability` — Route / quote availability
  - discovery: Check route/quote availability for expected liquidation, unwind, or execution path on the named network.; Preserve router/API/contract evidence for every route result.
  - negative search: Query route/quote APIs or contracts for the asset/network context.; Check protocol-specific route registries or allowed-router configuration when available.
  - no-result proof required: yes
  - no-result semantics: No route is valid only as investigated_no_result with route registry/API/contract, network/context, and evidence-path proof.

## Analyze-only scenario contract

- none

## Stage contract checklist

Mandatory facts:
- `oracle.S5_protocol_fit_and_parameter_context.eth-mainnet-usdat-gearbox-oracle.scope_loaded` — stage scope, input paths, and required outputs are loaded before claims (if unresolved: `not_investigated`)
- `oracle.S5_protocol_fit_and_parameter_context.eth-mainnet-usdat-gearbox-oracle.f1_protocol-fit-memo-ties-oracle-facts-to-gearbox-p` — protocol-fit memo ties oracle facts to Gearbox parameter context (if unresolved: `not_investigated`)
- `oracle.S5_protocol_fit_and_parameter_context.eth-mainnet-usdat-gearbox-oracle.f2_unresolved-material-facts-map-to-review-required` — unresolved material facts map to review_required/request_more_inputs/blocked (if unresolved: `not_investigated`)
- `oracle.S5_protocol_fit_and_parameter_context.eth-mainnet-usdat-gearbox-oracle.f3_no-preview-execute-readiness-claim-without-separ` — no Preview/Execute readiness claim without separate parent proposal gate (if unresolved: `not_investigated`)
- `oracle.eth-mainnet-usdat-gearbox-oracle.market_or_credit_manager` — input missing for eth-mainnet-usdat-gearbox-oracle.market_or_credit_manager (if unresolved: `input_missing`)
- `oracle.eth-mainnet-usdat-gearbox-oracle.position_size` — input missing for eth-mainnet-usdat-gearbox-oracle.position_size (if unresolved: `input_missing`)

Required methods:
- Load the input paths and stage scope before writing claims.
- For every material claim, save or cite a source/evidence artifact path under the child run root.
- If a source search finds nothing, fill no_result_proof_template; do not write bare 'not found'.
- If you cannot investigate a required fact, return a fact_result with state=not_investigated and status=blocked/review_required.

Allowed unknown states and evidence:
- `not_applicable` — Record applicability_rule_id, scope/input evidence path, reason, and decision_effect.
- `input_missing` — Record input_schema_key, expected input, why defaults are unsafe, requested_input, and decision_effect.
- `not_investigated` — Failure state for required facts: name the missing investigation and return blocked/review_required.
- `investigated_no_result` — Attach a no_result_proof with methods_tried, sources_checked, negative_evidence_path, coverage, freshness, and residual_decision_effect.
- `source_unavailable` — Record source identity, method, timestamp, exact error/status, retry or alternate-source notes, and decision_effect.
- `source_inconclusive` — Record sources read, insufficient/ambiguous evidence, freshness/coverage limits, follow-up, and decision_effect.
- `contradicted` — Record conflicting sources/values, timestamps, source-authority rule, reconciliation status, and decision_effect.

Minimum source/evidence requirements:
- fact_id, state, scope_id, required_by, decision_effect
- source/evidence artifact path for every known, inconclusive, unavailable, contradicted, or no-result fact
- input_schema_key/requested_input for input_missing facts
- applicability_rule_id/evidence_path for not_applicable facts

Disallowed placeholders:
- `unknown`
- `not found`
- `not_available`
- `TBD`
- `none`
- `blank required fields`

Precomputed not-applicable boundaries:
- none

## Fact results to produce

```json
{
  "blocking_fact_ids": [
    "oracle.eth-mainnet-usdat-gearbox-oracle.market_or_credit_manager",
    "oracle.eth-mainnet-usdat-gearbox-oracle.position_size"
  ],
  "fact_results": [
    {
      "decision_effect": "request_more_inputs",
      "evidence_path": ".workflow/input.normalized.json",
      "fact_id": "oracle.eth-mainnet-usdat-gearbox-oracle.market_or_credit_manager",
      "input_schema_key": "oracle_scopes[0].market_or_credit_manager",
      "reason": "Required input is absent or is a disallowed placeholder; do not invent it.",
      "requested_input": "Gearbox market, Credit Manager, pool, or explicit not-applicable rule",
      "state": "input_missing"
    },
    {
      "decision_effect": "request_more_inputs",
      "evidence_path": ".workflow/input.normalized.json",
      "fact_id": "oracle.eth-mainnet-usdat-gearbox-oracle.position_size",
      "input_schema_key": "oracle_scopes[0].position_size",
      "reason": "Required input is absent or is a disallowed placeholder; do not invent it.",
      "requested_input": "position size, scenario size range, or input_missing fact with requested input",
      "state": "input_missing"
    },
    {
      "decision_effect": "blocked",
      "evidence_path": "<stage artifact path showing omission or explicit blocked return>",
      "fact_id": "<required_fact_id_from_stage_contract>",
      "missing_investigation": "<method/source/fact not attempted>",
      "state": "not_investigated"
    }
  ],
  "fact_state_summary": {
    "contradicted": 0,
    "input_missing": 0,
    "investigated_no_result": 0,
    "not_applicable": 0,
    "not_investigated": 0,
    "source_inconclusive": 0,
    "source_unavailable": 0
  },
  "precomputed_boundary_facts": []
}
```

## No-result proof template

Use this only for `investigated_no_result`; fill methods tried, sources checked, negative evidence path, and residual decision effect.

```json
{
  "coverage": "<chain/protocol/registry/time-window/search boundary covered>",
  "fact_id": "<required_fact_id>",
  "freshness_utc": "<YYYY-MM-DDTHH:MM:SSZ>",
  "methods_tried": [
    {
      "artifact_path": "raw/<fact>-negative-evidence.json",
      "method": "<tool/command/API/RPC/search method>",
      "query_or_endpoint": "<exact query, contract call, endpoint, registry key, or document path>",
      "result": "negative",
      "source_class": "<authoritative_registry|contract_probe|docs_or_governance|market_source>",
      "timestamp_utc": "<YYYY-MM-DDTHH:MM:SSZ>"
    }
  ],
  "negative_evidence_path": "raw/<fact>-negative-evidence.json",
  "proof_id": "oracle.S5_protocol_fit_and_parameter_context.<fact>.no_result.v1",
  "residual_decision_effect": "pass|review_required|request_more_inputs|blocked",
  "sources_checked": [
    "<source ids/classes checked>"
  ],
  "state": "investigated_no_result"
}
```

## Work to perform

Fill this stage only. Preserve source evidence in the child run root and return only the envelope fields. Do not expand raw evidence into the parent prompt.

## Required outputs

- `tokens/eth-mainnet-usdat-gearbox-oracle/oracle/protocol-fit-memo.md`

## Validation command

```bash
python3 dev/tools/validate_workflow_run.py --workflow oracle-analysis --run-root dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/run/oracle-analysis --format json,markdown --report-dir dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/run/oracle-analysis/verification --write-verification
```

## Return envelope

```json
{
  "artifact_paths": [
    "tokens/eth-mainnet-usdat-gearbox-oracle/oracle/protocol-fit-memo.md"
  ],
  "blockers": "list concrete blockers, empty if pass",
  "blocking_fact_ids": [
    "oracle.eth-mainnet-usdat-gearbox-oracle.market_or_credit_manager",
    "oracle.eth-mainnet-usdat-gearbox-oracle.position_size"
  ],
  "fact_result_artifact_paths": [
    "<path to fact-results.json or markdown fenced JSON>"
  ],
  "fact_state_summary": {
    "contradicted": 0,
    "input_missing": 0,
    "investigated_no_result": 0,
    "not_applicable": 0,
    "not_investigated": 0,
    "source_inconclusive": 0,
    "source_unavailable": 0
  },
  "no_result_proof_paths": [
    "<path to no-result-proofs.json when any fact is investigated_no_result>"
  ],
  "status": "pass|review_required|blocked",
  "validation_status": "validator status and report path"
}
```
