# Stage packet — S6_quantitative_underwriting — run

Launcher: Codex: use this packet as the complete task brief; write only to the declared run root, then return the envelope.

## Scope

- Workflow: `asset-investment-diligence-v1`
- Child run root: `dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/run/asset-investment-diligence`
- Artifact directory: `investment-analysis`
- Objective: Should USDat or sUSDat be treated as acceptable Gearbox Credit Account collateral candidates on Ethereum mainnet when borrowing USDC at a 9% borrow-rate assumption?

## Known inputs

Input paths:
- `tokens`
- `pt-markets/index.md`
- `x-research/index.md`

Optional references:
- `user/references/workflows/asset-investment-diligence/workflow.json`
- `user/references/workflows/asset-investment-diligence/output-structure.md`

## Blocking unknowns

- `oracle.eth-mainnet-usdat-gearbox-oracle.market_or_credit_manager` — `input_missing` from `oracle_scopes[0].market_or_credit_manager`; Name the evaluated Gearbox market/Credit Manager/pool, or record a deterministic not_applicable rule.
- `oracle.eth-mainnet-usdat-gearbox-oracle.position_size` — `input_missing` from `oracle_scopes[0].position_size`; Provide a size/scenario range or preserve input_missing before route, liquidity, or liquidation conclusions.
- `oracle.eth-mainnet-susdat-gearbox-oracle.market_or_credit_manager` — `input_missing` from `oracle_scopes[1].market_or_credit_manager`; Name the evaluated Gearbox market/Credit Manager/pool, or record a deterministic not_applicable rule.
- `oracle.eth-mainnet-susdat-gearbox-oracle.position_size` — `input_missing` from `oracle_scopes[1].position_size`; Provide a size/scenario range or preserve input_missing before route, liquidity, or liquidation conclusions.
- `run.run.position_size` — `input_missing` from `constraints`; Provide a size/scenario range or preserve input_missing before route, liquidity, or liquidation conclusions.
- `run.run.target_leverage` — `input_missing` from `constraints`; Provide target leverage/scenario leverage before quantitative proposal readiness.
- `run.run.hold_horizon` — `input_missing` from `constraints`; Provide hold horizon before risk/return conclusions.
- `run.run.user_risk_policy` — `input_missing` from `constraints`; Provide user HF floor/risk policy before Preview/Execute readiness.

## Protocol investigation adapter

- none

## Analyze-only scenario contract

Contract: `asset-s6-analyze-only-scenario-band-v1`

- Scenario needed: `True`
- Scenario allowed: `True`
- Missing scenario inputs: `hold_horizon, position_size, target_leverage, user_risk_policy`
- Inputs preventing scenarios: `none`
- Reason: only scenario-eligible Analyze inputs are missing
- Proposal gate: Missing user inputs stay propagated to combined.Propose as request_more_inputs.
- Preview/Execute gate: Analyze-only scenarios must not set Preview or Execute to ready/pass.

Required bands when allowed:
- `conservative` — axes: holding horizon band, position size / notional band, leverage band, risk-policy / HF-floor band; include: assumption values with units and source/derivation notes, gross ROI and simple/compound annualized return, risk-adjusted ROI/annualized return and expected loss, exit cost, liquidation/oracle stress, and break-even logic
- `base` — axes: holding horizon band, position size / notional band, leverage band, risk-policy / HF-floor band; include: assumption values with units and source/derivation notes, gross ROI and simple/compound annualized return, risk-adjusted ROI/annualized return and expected loss, exit cost, liquidation/oracle stress, and break-even logic
- `upside` — axes: holding horizon band, position size / notional band, leverage band, risk-policy / HF-floor band; include: assumption values with units and source/derivation notes, gross ROI and simple/compound annualized return, risk-adjusted ROI/annualized return and expected loss, exit cost, liquidation/oracle stress, and break-even logic

When allowed:
- Produce labelled conservative/base/upside scenario bands instead of skipping all S6 calculations.
- Mark every band non-executable and assumption-bound.
- Ask for exact missing sizing/leverage/horizon/risk-policy inputs before Proposal, Preview, or Execute readiness.

When not allowed:
- Do not invent fallback scenarios.
- Keep exact underwriting blocked/request_more_inputs with the unresolved input_missing fact IDs.

## Stage contract checklist

Mandatory facts:
- `asset.S6_quantitative_underwriting.run.scope_loaded` — stage scope, input paths, and required outputs are loaded before claims (if unresolved: `not_investigated`)
- `asset.S6_quantitative_underwriting.run.f1_all-quantitative-assumptions-borrow-rate-ltv-lt-` — all quantitative assumptions: borrow rate, LTV/LT, size, leverage, horizon, liquidity, and pricing basis (if unresolved: `not_investigated`)
- `asset.S6_quantitative_underwriting.run.f2_pt-social-market-inputs-are-known-not-applicable` — PT/social/market inputs are known, not_applicable, or proven no-result (if unresolved: `not_investigated`)
- `asset.S6_quantitative_underwriting.run.f3_analyze-only-scenario-bands-when-sizing-leverage` — Analyze-only scenario bands when sizing, leverage, horizon, or risk-policy inputs are missing and scenarios are allowed (if unresolved: `not_investigated`)
- `asset.S6_quantitative_underwriting.run.f4_non-execution-recommendation-gate-from-unresolve` — non-execution recommendation gate from unresolved facts (if unresolved: `not_investigated`)
- `oracle.eth-mainnet-usdat-gearbox-oracle.market_or_credit_manager` — input missing for eth-mainnet-usdat-gearbox-oracle.market_or_credit_manager (if unresolved: `input_missing`)
- `oracle.eth-mainnet-usdat-gearbox-oracle.position_size` — input missing for eth-mainnet-usdat-gearbox-oracle.position_size (if unresolved: `input_missing`)
- `oracle.eth-mainnet-susdat-gearbox-oracle.market_or_credit_manager` — input missing for eth-mainnet-susdat-gearbox-oracle.market_or_credit_manager (if unresolved: `input_missing`)
- `oracle.eth-mainnet-susdat-gearbox-oracle.position_size` — input missing for eth-mainnet-susdat-gearbox-oracle.position_size (if unresolved: `input_missing`)
- `run.run.position_size` — input missing for run.position_size (if unresolved: `input_missing`)
- `run.run.target_leverage` — input missing for run.target_leverage (if unresolved: `input_missing`)
- `run.run.hold_horizon` — input missing for run.hold_horizon (if unresolved: `input_missing`)
- `run.run.user_risk_policy` — input missing for run.user_risk_policy (if unresolved: `input_missing`)

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
- `asset.S3_pt_market_economics.stage_applicability` — `not_applicable`: pt_markets is empty in input (evidence: `.workflow/plan.json`)
- `asset.S4_x_social_mining.stage_applicability` — `not_applicable`: social_scopes is empty in input (evidence: `.workflow/plan.json`)
- `asset.S5_x_social_synthesis.stage_applicability` — `not_applicable`: social_scopes is empty in input (evidence: `.workflow/plan.json`)

## Fact results to produce

```json
{
  "blocking_fact_ids": [
    "oracle.eth-mainnet-usdat-gearbox-oracle.market_or_credit_manager",
    "oracle.eth-mainnet-usdat-gearbox-oracle.position_size",
    "oracle.eth-mainnet-susdat-gearbox-oracle.market_or_credit_manager",
    "oracle.eth-mainnet-susdat-gearbox-oracle.position_size",
    "run.run.position_size",
    "run.run.target_leverage",
    "run.run.hold_horizon",
    "run.run.user_risk_policy"
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
      "decision_effect": "request_more_inputs",
      "evidence_path": ".workflow/input.normalized.json",
      "fact_id": "oracle.eth-mainnet-susdat-gearbox-oracle.market_or_credit_manager",
      "input_schema_key": "oracle_scopes[1].market_or_credit_manager",
      "reason": "Required input is absent or is a disallowed placeholder; do not invent it.",
      "requested_input": "Gearbox market, Credit Manager, pool, or explicit not-applicable rule",
      "state": "input_missing"
    },
    {
      "decision_effect": "request_more_inputs",
      "evidence_path": ".workflow/input.normalized.json",
      "fact_id": "oracle.eth-mainnet-susdat-gearbox-oracle.position_size",
      "input_schema_key": "oracle_scopes[1].position_size",
      "reason": "Required input is absent or is a disallowed placeholder; do not invent it.",
      "requested_input": "position size, scenario size range, or input_missing fact with requested input",
      "state": "input_missing"
    },
    {
      "decision_effect": "request_more_inputs",
      "evidence_path": ".workflow/input.normalized.json",
      "fact_id": "run.run.position_size",
      "input_schema_key": "constraints",
      "reason": "Required input is absent or is a disallowed placeholder; do not invent it.",
      "requested_input": "position size, scenario size range, or input_missing fact with requested input",
      "state": "input_missing"
    },
    {
      "decision_effect": "request_more_inputs",
      "evidence_path": ".workflow/input.normalized.json",
      "fact_id": "run.run.target_leverage",
      "input_schema_key": "constraints",
      "reason": "Required input is absent or is a disallowed placeholder; do not invent it.",
      "requested_input": "target leverage or explicit scenario range",
      "state": "input_missing"
    },
    {
      "decision_effect": "request_more_inputs",
      "evidence_path": ".workflow/input.normalized.json",
      "fact_id": "run.run.hold_horizon",
      "input_schema_key": "constraints",
      "reason": "Required input is absent or is a disallowed placeholder; do not invent it.",
      "requested_input": "hold horizon or deterministic not_applicable rule",
      "state": "input_missing"
    },
    {
      "decision_effect": "request_more_inputs",
      "evidence_path": ".workflow/input.normalized.json",
      "fact_id": "run.run.user_risk_policy",
      "input_schema_key": "constraints",
      "reason": "Required input is absent or is a disallowed placeholder; do not invent it.",
      "requested_input": "user HF floor/risk policy or explicit not_applicable rule",
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
  "precomputed_boundary_facts": [
    {
      "applicability_rule_id": "empty-input-stage-skip",
      "decision_effect": "no_gate",
      "evidence_path": ".workflow/plan.json",
      "fact_id": "asset.S3_pt_market_economics.stage_applicability",
      "reason": "pt_markets is empty in input",
      "state": "not_applicable"
    },
    {
      "applicability_rule_id": "empty-input-stage-skip",
      "decision_effect": "no_gate",
      "evidence_path": ".workflow/plan.json",
      "fact_id": "asset.S4_x_social_mining.stage_applicability",
      "reason": "social_scopes is empty in input",
      "state": "not_applicable"
    },
    {
      "applicability_rule_id": "empty-input-stage-skip",
      "decision_effect": "no_gate",
      "evidence_path": ".workflow/plan.json",
      "fact_id": "asset.S5_x_social_synthesis.stage_applicability",
      "reason": "social_scopes is empty in input",
      "state": "not_applicable"
    }
  ]
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
  "proof_id": "asset.S6_quantitative_underwriting.<fact>.no_result.v1",
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

- `investment-analysis/quantitative-underwriting-methodology.md`
- `investment-analysis/investment-analyst-report-points-pt-risk-return.md`
- `investment-analysis/index.md`

## Validation command

```bash
python3 dev/tools/validate_workflow_run.py --workflow asset-investment-diligence --run-root dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/run/asset-investment-diligence --format json,markdown --report-dir dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/run/asset-investment-diligence/verification --write-verification
```

## Return envelope

```json
{
  "artifact_paths": [
    "investment-analysis/quantitative-underwriting-methodology.md",
    "investment-analysis/investment-analyst-report-points-pt-risk-return.md",
    "investment-analysis/index.md"
  ],
  "blockers": "list concrete blockers, empty if pass",
  "blocking_fact_ids": [
    "oracle.eth-mainnet-usdat-gearbox-oracle.market_or_credit_manager",
    "oracle.eth-mainnet-usdat-gearbox-oracle.position_size",
    "oracle.eth-mainnet-susdat-gearbox-oracle.market_or_credit_manager",
    "oracle.eth-mainnet-susdat-gearbox-oracle.position_size",
    "run.run.position_size",
    "run.run.target_leverage",
    "run.run.hold_horizon",
    "run.run.user_risk_policy"
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
