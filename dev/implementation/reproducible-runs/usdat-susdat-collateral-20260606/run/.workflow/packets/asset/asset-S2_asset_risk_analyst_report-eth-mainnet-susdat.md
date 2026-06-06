# Stage packet — S2_asset_risk_analyst_report — eth-mainnet-susdat

Launcher: Codex: use this packet as the complete task brief; write only to the declared run root, then return the envelope.

## Scope

- Workflow: `asset-investment-diligence-v1`
- Child run root: `dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/run/asset-investment-diligence`
- Artifact directory: `tokens/eth-mainnet-susdat`
- Objective: Should USDat or sUSDat be treated as acceptable Gearbox Credit Account collateral candidates on Ethereum mainnet when borrowing USDC at a 9% borrow-rate assumption?

## Known inputs

Input paths:
- `tokens/eth-mainnet-susdat/scope.json`
- `tokens/eth-mainnet-susdat/technical-report.md`

Optional references:
- `user/references/workflows/asset-investment-diligence/workflow.json`
- `user/references/workflows/asset-investment-diligence/output-structure.md`

## Blocking unknowns

- none

## Protocol investigation adapter

- none

## Analyze-only scenario contract

- none

## Stage contract checklist

Mandatory facts:
- `asset.S2_asset_risk_analyst_report.eth-mainnet-susdat.scope_loaded` — stage scope, input paths, and required outputs are loaded before claims (if unresolved: `not_investigated`)
- `asset.S2_asset_risk_analyst_report.eth-mainnet-susdat.f1_s1-source-evidence-imported-without-silent-gaps` — S1 source evidence imported without silent gaps (if unresolved: `not_investigated`)
- `asset.S2_asset_risk_analyst_report.eth-mainnet-susdat.f2_risk-classification-by-admin-issuer-backing-tran` — risk classification by admin, issuer/backing, transferability, liquidity, oracle, and governance axis (if unresolved: `not_investigated`)
- `asset.S2_asset_risk_analyst_report.eth-mainnet-susdat.f3_explicit-unresolved-fact-states-and-decision-eff` — explicit unresolved fact states and decision effects (if unresolved: `not_investigated`)

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
  "blocking_fact_ids": [],
  "fact_results": [
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
  "proof_id": "asset.S2_asset_risk_analyst_report.<fact>.no_result.v1",
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

- `tokens/eth-mainnet-susdat/analyst-report.md`
- `tokens/eth-mainnet-susdat/verification.md`

## Validation command

```bash
python3 dev/tools/validate_workflow_run.py --workflow asset-investment-diligence --run-root dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/run/asset-investment-diligence --format json,markdown --report-dir dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/run/asset-investment-diligence/verification --write-verification
```

## Return envelope

```json
{
  "artifact_paths": [
    "tokens/eth-mainnet-susdat/analyst-report.md",
    "tokens/eth-mainnet-susdat/verification.md"
  ],
  "blockers": "list concrete blockers, empty if pass",
  "blocking_fact_ids": [],
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
