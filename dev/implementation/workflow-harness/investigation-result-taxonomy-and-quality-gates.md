# Generalized investigation-result taxonomy and quality-gate architecture

Status: design note.

Purpose: define reusable quality gates for Analyze -> Propose workflows so the harness distinguishes missing inputs, missing investigation, source failure, no-result investigation, inconclusive evidence, contradictions, and true non-applicability. This is intentionally workflow-general; token-specific runs are fixtures only.

## Grounding

This design is grounded in the current harness and contracts:

- `dev/tools/run_workflow.py` is only the CLI wrapper for `workflow_entrypoint.main`.
- `dev/tools/workflow_entrypoint_contracts.py` defines runner status/exit mappings, required packet headings, stage lists, and child validator commands.
- `dev/tools/workflow_protocol_adapters.py` defines reusable protocol investigation adapters. Adapters declare required facts, discovery methods, negative-search methods, no-market/no-route semantics, and required proof classes for `investigated_no_result`.
- `dev/tools/workflow_entrypoint.py` normalizes inputs, collects blocking unknowns, builds the stage plan, renders packets, writes the parent Analyze -> Propose return, runs child/combined validators, and writes next-action state.
- `dev/tools/validate_workflow_run.py` validates formal run compliance, imports child findings/status, parses parent handoff statuses, rejects unsupported Preview/Execute recommendations, and maps P0/P1 findings to formal status.
- `user/references/workflows/asset-investment-diligence/stage-contracts.md` and `user/references/workflows/oracle-analysis/stage-contracts.md` define current stage envelopes with `status`, `blocking_unknowns`, `validation`, required outputs, required facts, and parent completion rules.
- Non-normative example fixture: `dev/implementation/workflow-harness/tmp/runs/usdat-susdat-collateral-analyze-propose/`. Its latest validation shows formal harness pass while the parent still carries unresolved proposal gates. Do not derive token-specific rules from that run.

## Problem statement

The current contracts give every stage a small envelope with `status`, `artifact_paths`, `blocking_unknowns`, and `validation`, but they do not yet require every required fact to carry a precise investigation-result state. This lets a stage satisfy headings while leaving a required fact as vague prose such as `unknown`, `not found`, `not_available`, or a blank placeholder.

That failure mode creates three conflations:

1. A required fact that was never investigated can look the same as a required fact that was deeply investigated but genuinely produced no result.
2. Formal validator pass can be misread as business/proposal readiness.
3. Parent flow state can hide whether a child is blocked by user input, source outage, inconclusive evidence, contradiction, or missing work.

The fix is a generalized fact-level taxonomy plus separate gates for formal validation, workflow decision, and proposal readiness.

## Design principles

1. Every required or material fact slot must have an explicit `state` from the taxonomy below.
2. `investigated_no_result` is a positive claim. It requires replayable negative evidence.
3. `not_investigated` is never a successful placeholder for a required fact.
4. Deterministic validators judge schemas, evidence envelopes, paths, declared commands, and state/evidence consistency. They do not judge economic quality or oracle quality.
5. Semantic critic gates may later judge adequacy, usefulness, and reasoning quality, but their result must remain separate from deterministic validation.
6. Protocol-specific questions live behind adapters, not validator internals. Validators consume adapter declarations; they should not contain token-specific addresses or one-off protocol prose checks.
7. Proposal readiness is downstream of validation and workflow decisions. A formal `pass` is necessary but not sufficient for `ready_for_preview`.

## Core object model

Add a fact-result envelope to packets, stage artifacts, validator reports, and parent synthesis.

```json
{
  "fact_id": "oracle.main_feed",
  "scope_id": "chain-scope-slug",
  "required_by": ["oracle.S1_feed_inventory_and_graph", "oracle.S5_protocol_fit_and_parameter_context"],
  "state": "investigated_no_result",
  "decision_effect": "review_required",
  "summary": "No protocol-level reserve feed was found in the adapter-defined registry/source set.",
  "evidence": [
    {
      "artifact_path": "tokens/<scope>/raw/source-evidence/feed-registry-query.json",
      "source_type": "rpc_or_registry_probe",
      "timestamp_utc": "2026-06-06T00:00:00Z",
      "result": "negative"
    }
  ],
  "no_result_proof_id": "oracle.main_feed.no_result.v1",
  "requested_input": null,
  "validator_check_ids": ["facts.required_state_valid", "facts.no_result_proof_present"]
}
```

Recommended durable locations:

- Per-stage Markdown may embed this as fenced JSON for human readability.
- Each stage should also write a parseable sidecar, for example `stage-results/<stage_id>.facts.json`, or a stage-local `fact-results.json`.
- Raw or bulky evidence stays in `raw/` or `research/`; the fact result stores paths, source metadata, timestamps, and concise findings.

## Investigation-result taxonomy

| State | Meaning | Required evidence | Allowed stage/workflow status | May pass deterministic validation? | Proposal-gate effect |
| --- | --- | --- | --- | --- | --- |
| `not_applicable` | The fact slot does not apply to this scope by a declared contract, adapter rule, or user-requested scope boundary. | `applicability_rule_id`; scope fields used by the rule; short reason; artifact path proving the scope; no raw source search required unless the applicability rule itself depends on a source lookup. | `pass` when the fact is truly out of scope; `review_required` if a human must accept the applicability rule; `skipped` for whole skipped stages. | Yes, if the rule is deterministic and recorded. No, if it is asserted only in prose. | No gate if non-applicability is deterministic. `request_more_inputs` or `blocked` if scope/applicability itself is ambiguous. |
| `input_missing` | The workflow cannot answer the fact because required user, operator, or live-system input was not supplied. | Input schema key; path to normalized input; expected input; why defaults would be unsafe; `requested_input` label; decision effect. | `review_required` when the stage can still produce scenario analysis; `blocked` when the stage cannot produce a safe artifact without the input. | Yes for formal validation if the missing input is explicitly represented and the artifact does not claim the missing fact. No if a required field is silently blank. | Usually `request_more_inputs`. `blocked` if safe Analyze output is impossible. Never `ready_for_preview`. |
| `not_investigated` | A required/material fact was not attempted or the artifact lacks proof that it was attempted. This is a failure state, not an acceptable unknown. | No positive evidence is required; validators may infer it from absence of a fact result, absence of evidence, or stale placeholder markers. If explicitly declared, it must name the missing investigation. | `blocked` for required facts; `review_required` only for optional/material-but-nonblocking facts. | No for required facts. Deterministic validation should emit at least P1, often P0 if the contract requires the fact for safe completion. | `blocked` until investigation is performed or the fact is reclassified with evidence. |
| `investigated_no_result` | The stage performed the adapter-defined investigation and found no source/fact/result in the searched space. | No-result proof: source plan, sources queried, exact queries/probes/endpoints, timestamps, negative result artifacts, retry/error handling where relevant, coverage statement, freshness window, and why additional sources are not required for this stage. | `pass` if the adapter says absence is an acceptable result for this fact; `review_required` if the fact matters but absence can be reviewed; `blocked` if the workflow cannot continue safely without the fact. | Yes if the no-result proof satisfies the stage/adapter minimum. No if it only says `not found` without replayable search evidence. | Depends on decision effect: no gate for acceptable absence; `request_more_inputs` if operator input can resolve; `blocked` if safety-critical absence remains. |
| `source_unavailable` | A known required source exists but was inaccessible, down, rate-limited, paywalled, permission-gated, or failed in a way that prevented evaluation. | Source identity; access method; timestamp; exact error/status; retry count or retry rationale; alternate sources tried; whether cached/stale sources were used; decision effect. | `blocked` when the source is authoritative and no substitute is acceptable; `review_required` when alternate evidence can support a cautious Analyze result; `pass` only for optional facts explicitly marked nonblocking. | Formal validation may pass the envelope, but the run status should be `review_required` or `blocked` for required facts. It must not pass as if the fact were known. | Usually `blocked` or `request_more_inputs` depending on whether a human/source credential can resolve it. |
| `source_inconclusive` | Sources were reachable and searched, but they do not determine the fact or are too ambiguous/stale/partial to support a conclusion. | Sources read; extracted statements/values; reason each is insufficient; freshness/coverage limits; follow-up needed; confidence/degradation marker. | `review_required` for most material facts; `blocked` for safety-critical facts; `pass` only when the fact is optional or the adapter allows conservative fallback. | Yes for formal evidence completeness, but should usually produce formal `review_required` when the fact is required. No if the artifact turns inconclusive evidence into a definitive claim. | `request_more_inputs` if additional input/source can resolve; otherwise `blocked` or conservative no-proposal state. |
| `contradicted` | Two or more credible sources disagree on the fact, or current and historical evidence conflict. | Conflicting source list; values/claims; timestamps; source authority ranking; reconciliation rule if one is accepted; unresolved conflict statement when no rule resolves it. | `review_required` if a reconciliation rule can be reviewed; `blocked` if no safe conclusion can be drawn; `pass` only when a deterministic hierarchy resolves the contradiction and the losing evidence remains recorded. | Yes only if conflict handling is explicit and a deterministic authority rule resolves it. Otherwise formal validation should be `review_required` or `fail` if the contradiction is hidden. | Never `ready_for_preview` while material contradiction is unresolved. |

## Evidence requirements by state family

### States that prove scope or input boundaries

`not_applicable` and `input_missing` are boundary states. They do not require broad source searches, but they do require exact linkage to the scope/input contract.

Required fields:

- `fact_id`.
- `state`.
- `scope_id`.
- `required_by`.
- `decision_effect`.
- `applicability_rule_id` or `input_schema_key`.
- Human-readable reason.
- Path to normalized input, scope file, or stage contract artifact.

### States that prove investigation happened

`investigated_no_result`, `source_unavailable`, `source_inconclusive`, and `contradicted` are investigation states. They require an evidence ledger.

Required fields:

- `investigation_plan_id` identifying the stage/adapter source plan.
- `sources_required` and `sources_attempted`.
- Per-attempt `source_type`, `source_id`, `method`, `query_or_endpoint`, `timestamp_utc`, `artifact_path`, and `result`.
- Coverage statement: what search space was covered and what was intentionally excluded.
- Freshness statement: when the evidence was collected and how stale data is treated.
- Decision effect and parent gate recommendation.

### Failure state

`not_investigated` is either explicit or inferred. Validators should emit it when any required fact lacks a fact-result entry, when a required state has no required evidence, or when stale placeholders are present.

Placeholder markers that should be treated as unproven unless wrapped in a valid fact-result envelope include:

- `unknown`
- `not found`
- `not_available`
- `TBD`
- `none`
- blank required table cells
- generic `missing input` prose with no `input_schema_key`

## How a stage proves deep-enough no-result investigation

A no-result claim is acceptable only when the stage provides a proof bundle. The bundle is adapter-defined but must include these common elements:

1. Fact target: exact `fact_id`, scope, stage, and why the fact is required or material.
2. Investigation plan: source classes and minimum search/probe requirements for the stage. Examples of source classes are RPC reads, verified contract source, protocol registries, issuer documentation, governance/timelock records, market/liquidity providers, or social/search APIs.
3. Query/probe log: exact endpoints, contract calls, search strings, registry keys, or document paths queried; timestamps; tool or command used; artifact path for the raw result.
4. Negative evidence: saved artifacts showing empty results, null fields, reverted calls, missing registry entries, no matching docs, or unavailable markets. Do not rely on unsaved terminal prose.
5. Alternative/fallback search: at least one independent source class when the adapter requires corroboration, or a documented reason why the authoritative source alone is sufficient.
6. Coverage limit: explicit statement of the search boundary, for example chain, protocol, registry, block/time window, market universe, docs domain, or social time window.
7. Freshness: timestamp and maximum acceptable age for the fact class.
8. Decision effect: whether absence is acceptable, review-required, or blocking.
9. Validator mapping: check IDs that can replay path existence, JSON shape, required source classes, and required attempt counts.

A stage may write a compact `no_result_proofs` array:

```json
{
  "no_result_proofs": [
    {
      "proof_id": "protocol.market_absence.v1",
      "fact_id": "market.supported_route",
      "required_source_classes": ["protocol_registry", "router_or_market_probe", "docs_or_governance_reference"],
      "attempts": [
        {"source_class": "protocol_registry", "artifact_path": "raw/registry-query.json", "result": "negative"},
        {"source_class": "router_or_market_probe", "artifact_path": "raw/router-probe.json", "result": "negative"},
        {"source_class": "docs_or_governance_reference", "artifact_path": "research/support-search.md", "result": "negative"}
      ],
      "coverage": "Named chain/protocol/scope only; no cross-chain inference.",
      "freshness_utc": "2026-06-06T00:00:00Z",
      "decision_effect": "review_required"
    }
  ]
}
```

The deterministic validator does not decide whether the protocol should support a route. It verifies that the required no-result proof exists, references replayable artifacts, satisfies the adapter's minimum source classes, and is consistent with the declared workflow/proposal gate.

## Formal validation status vs workflow decision status vs proposal gate

Keep these surfaces separate in generated JSON, Markdown, and parent synthesis.

### 1. Formal deterministic validation status

Current source: `validate_workflow_run.py` report `status` and `exit_code`.

Allowed values:

- `pass`: schema, required files, paths, fact-result envelopes, no-result proofs, child reports, parent handoff, and deterministic consistency checks passed.
- `review_required`: no P0 structural failures, but at least one P1 issue remains, or a required fact is explicitly inconclusive/unavailable/contradicted and policy says a reviewer may decide.
- `fail`: P0 structural failure, missing required artifacts, invalid JSON, unproven required fact, hidden contradiction, invalid status propagation, or unsafe Preview/Execute recommendation.

Formal validation answers: `Is the artifact set structurally valid and honestly labelled?`

It does not answer: `Is this a good investment?`, `Is the oracle safe?`, `Should a user execute?`, or `Is the parent proposal ready?`

### 2. Workflow decision status

Current surfaces: stage envelopes in stage contracts, child report status, and parent `stage_status` for Discover/Analyze/Propose/Preview/Execute/Monitor.

Recommended stage/workflow values:

- `pass`: stage completed its required contract and all required facts are known, not applicable, or accepted no-result with nonblocking decision effect.
- `review_required`: stage produced a useful artifact but contains material `input_missing`, `investigated_no_result`, `source_unavailable`, `source_inconclusive`, or `contradicted` states that require human/critic review before proposal readiness.
- `blocked`: stage cannot safely complete because required input, source access, investigation, or conflict resolution is missing.
- `skipped`: whole stage is out of scope by deterministic plan, with `not_applicable` fact/stage evidence.

Workflow decision answers: `What can the workflow safely do next?`

### 3. Proposal gate

Current source: parent `agentic-flow/analyze-and-propose.md` and `.workflow/next-action.*`.

Recommended values:

- `ready_for_preview`: formal validation is pass, semantic critic gate is pass if configured, no material unresolved fact has a blocking/review-required decision effect, and the parent has a concrete Analyze -> Propose recommendation. Preview/Execute may still require separate human authorization.
- `request_more_inputs`: formal artifacts are honest enough to preserve, but missing user/operator/live inputs or reviewable unknowns prevent a concrete proposal. The parent must list exact requested inputs by `fact_id`/`input_schema_key`.
- `blocked`: formal validation fails, required investigation is missing, authoritative sources are unavailable with no substitute, safety-critical contradictions remain, or the artifact recommends unsupported execution.

Proposal gate answers: `Can the parent produce an actionable proposal for human Preview, or must it request more work/input?`

### Required parent synthesis fields

Parent outputs should emit this shape:

```json
{
  "formal_validation": {
    "status": "pass | review_required | fail",
    "reports": ["asset-investment-diligence/verification/workflow-harness-report.json"]
  },
  "semantic_quality": {
    "status": "not_run | pass | review_required | fail",
    "reports": []
  },
  "workflow_decision": {
    "Discover": "complete_by_user_premise | complete_by_agent | blocked",
    "Analyze": "pass | review_required | blocked",
    "Propose": "ready_for_preview | request_more_inputs | blocked",
    "Preview": "blocked | ready | complete",
    "Execute": "blocked | ready | complete",
    "Monitor": "not_started | blocked | active"
  },
  "proposal_gate": {
    "status": "ready_for_preview | request_more_inputs | blocked",
    "blocking_fact_ids": [],
    "requested_inputs": []
  },
  "fact_state_summary": {
    "not_applicable": 0,
    "input_missing": 0,
    "not_investigated": 0,
    "investigated_no_result": 0,
    "source_unavailable": 0,
    "source_inconclusive": 0,
    "contradicted": 0
  }
}
```

## Deterministic validation rules

Add generalized validator checks before adding token- or stage-specific checks:

1. `facts.required_inventory_present`: every required fact slot for the stage/scope appears exactly once in the stage fact results.
2. `facts.state_enum_valid`: every fact uses one of the seven taxonomy states.
3. `facts.state_required_evidence_present`: state-specific evidence fields are present.
4. `facts.required_not_not_investigated`: required facts cannot remain `not_investigated`.
5. `facts.no_result_proof_present`: `investigated_no_result` facts reference a proof bundle.
6. `facts.no_result_source_classes_satisfied`: proof bundle includes adapter-required source classes and attempt artifacts.
7. `oracle.protocol_adapter_required_facts_present`: every adapter-declared oracle protocol-fit fact is represented in the protocol-fit artifact.
8. `oracle.protocol_adapter_no_result_proof_bundle`: adapter no-result/no-market states include the required proof markers, including registry/API-or-contract probe, network context, and evidence path.
9. `oracle.protocol_adapter_not_investigated_not_no_result`: artifacts cannot label unperformed investigation as `investigated_no_result`; they must use `not_investigated`.
10. `facts.source_unavailable_has_error`: `source_unavailable` includes source identity, error/status, timestamp, and retry/alternative-source notes.
11. `facts.inconclusive_has_reason`: `source_inconclusive` states explain why sources did not decide the fact.
12. `facts.contradiction_explicit`: `contradicted` states include both sides and a reconciliation status.
13. `facts.decision_effect_consistent`: fact states with blocking/review decision effect are reflected in stage status and parent proposal gate.
14. `facts.no_placeholder_without_state`: placeholder words in required fields are invalid unless backed by a fact-result envelope.
15. `parent.formal_status_not_proposal_gate`: parent `formal_validation.status=pass` must not imply `proposal_gate=ready_for_preview` when unresolved fact states remain.

Recommended severity mapping:

- P0: missing fact inventory, invalid JSON, missing required artifact, required `not_investigated`, hidden contradiction, unsupported execution recommendation.
- P1: required source unavailable/inconclusive/contradicted but honestly represented; no-result proof insufficient; decision-effect/status mismatch.
- P2: evidence quality metadata weak but nonblocking, stale-but-declared optional facts, missing convenience links.

## Migration impacts

### Packets

Current packet headings are useful but too generic. Generated packets should add a required `Fact results to produce` section and a machine-readable template.

Packet additions:

- `required_fact_slots`: generated from the stage contract and adapter.
- `allowed_states`: the seven taxonomy states, with state-specific evidence instructions.
- `investigation_plan`: required source classes and minimum probes/searches for each fact family.
- `no_result_template`: exact fields required for `investigated_no_result`.
- `do_not`: explicit ban on unbacked `unknown`, `not found`, `not_available`, or blank required fields.
- `return_envelope`: must include `fact_state_summary`, `blocking_fact_ids`, and artifact paths to fact-result JSON.

Packets should force investigation, not form filling. If the worker cannot investigate, it must return `not_investigated`/`blocked` rather than inventing or omitting facts.

### Stage artifacts

Stage outputs should preserve current human-readable Markdown, but add parseable fact outputs.

Artifact additions:

- Stage-level `fact-results.json` or fenced JSON block containing all required fact results.
- `raw-evidence-ledger.json` or per-source raw evidence artifacts referenced by fact results.
- `no-result-proofs.json` for negative investigation claims.
- `stage_status` derived from fact decision effects, not manually typed independent prose.
- `decision_effect` for every missing/unknown/non-applicable fact.

Existing required Markdown files can continue to hold narrative analysis. Validators should treat them as presentation plus source summaries, not as the only machine-readable truth.

### Validators

Validator migration should be layered:

1. Load stage contract/adapters to compute required fact slots for each scope.
2. Parse fact-result sidecars or fenced JSON.
3. Validate state enum and state-specific evidence.
4. Validate path existence and raw evidence artifact presence.
5. Validate no-result proof source-class coverage.
6. Derive stage status from fact decision effects and compare it to declared status.
7. Import child fact summaries into the combined parent report.
8. Keep formal report status separate from workflow/proposal gate status.

Do not add token-specific validator checks except fixtures/examples. Protocol-specific checks should live in adapters named by workflow/stage/fact family, not by token symbol.

### Parent result synthesis

Parent synthesis should aggregate child facts, not only child report statuses.

Required parent behavior:

- Import child formal validation reports.
- Import child `fact_state_summary` and unresolved fact IDs.
- Compute `workflow_decision` from child stage statuses and decision effects.
- Compute `proposal_gate` from formal validation, semantic quality, unresolved facts, and unsupported-execution checks.
- Render requested next checks as exact `fact_id`, `input_schema_key`, source credential, or stage artifact, not broad prose.
- Allow formal validation `pass` with proposal gate `request_more_inputs` when all unknowns are honestly proven but business/proposal readiness is not reached.

## Fixture and regression implications

Use the latest tmp run only as a labelled example fixture for status separation: formal harness checks can pass while the parent still blocks Preview/Execute and requests more inputs. Do not hardcode its symbols, addresses, markets, or conclusions.

Future fixtures should cover generalized cases:

- Positive known fact with raw evidence.
- `not_applicable` by deterministic scope rule.
- `input_missing` with exact requested input.
- Required `not_investigated` rejection.
- Valid `investigated_no_result` with replayable negative evidence.
- Weak `not found` prose rejected as unproven.
- `source_unavailable` with authoritative source outage.
- `source_inconclusive` with partial evidence.
- `contradicted` with and without deterministic reconciliation.
- Parent formal pass plus proposal `request_more_inputs`.
- Parent formal fail plus proposal `blocked`.

## Non-goals

- No token-specific decision logic.
- No claim that deterministic validation can judge investment quality, oracle safety, liquidity quality, or execution readiness.
- No Preview/Execute bypass. Analyze -> Propose can request inputs or prepare a proposal, but Preview and Execute remain separate gated stages.
