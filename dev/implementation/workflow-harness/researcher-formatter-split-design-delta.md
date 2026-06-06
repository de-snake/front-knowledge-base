# Researcher → formatter split design delta

Status: M0 frozen design delta for `front-kb-research-formatter-split`.

Purpose: add the smallest workflow-harness delta that prevents formally complete external-agent artifacts from being useless for collateral, listing, underwriting, or proposal decisions. The split is evidence-first: raw research must pass quality gates before any formatted memo can become a user-facing Analyze → Propose result.

This note is a scope reconciliation document only. It does not change code, schemas, validators, fixtures, or generated artifacts.

## Current baseline to preserve

Adjacent boards are complete and define this board's boundaries:

- `front-kb-safe-parallelization`: `done=10`. It owns metadata-only execution graph behavior, ready packet surfaces, parallel waves, delegation hints, artifact write scopes, and scheduler-facing packet metadata.
- `front-kb-workflow-quality-gates`: `done=11`. It owns the current investigation-result taxonomy, raw evidence ledger schema, protocol investigation adapters, deterministic unknown/no-result checks, semantic critic runner, parent proposal/status propagation, and quality-gate fixture baseline.

Current reusable quality-gate artifacts are the base, not replacement targets:

- `dev/implementation/workflow-harness/investigation-result-taxonomy-and-quality-gates.md`
- `dev/implementation/workflow-harness/evidence-ledger-schema.md`
- `dev/implementation/workflow-harness/contracts/evidence-ledger.schema.json`
- `dev/implementation/workflow-harness/semantic-critic-rubric-v1.md`
- `dev/implementation/workflow-harness/fixtures/regression-evals/quality-gate-regression-suite.json`
- `dev/tools/workflow_protocol_adapters.py`
- `dev/tools/validate_workflow_run.py`
- `dev/tools/semantic_critic_runner.py`

The split must extend those contracts with stricter role boundaries and traceability. It must not fork or duplicate the taxonomy.

## Non-overlap: do not rework safe parallelization

This board must not modify the execution/scheduling layer owned by `front-kb-safe-parallelization`.

Do not change semantics, schema versions, or compatibility behavior for:

- `contracts.EXECUTION_GRAPH_SCHEMA_VERSION`
- `.workflow/execution-graph.json`
- `plan.execution_graph`
- `.workflow/next-action.json` scheduler surfaces: `ready_packets`, `blocked_packets`, `parallel_waves`, and `first_packet`
- `.workflow/registry.json` packet-discovery surfaces
- `workflow_entrypoint.py` functions that build or validate scheduling metadata: `build_execution_graph`, `validate_execution_graph`, `build_parallel_waves`, `ready_packet_summary`, `blocked_packet_summary`, `build_next_action`, and `artifact_write_scope`
- packet metadata fields owned by scheduling: `depends_on_task_ids`, `parallel_group_id`, `parallel_unit`, `delegate_to_subagent`, `subagent_prompt_reference`, `recommended_max_concurrent`, `artifact_write_scope`, and `return_contract`

If later cards must touch files that also contain safe-parallelization logic, the allowed change shape is additive and role-scoped: add researcher/formatter payload or validation fields under new split-specific keys without changing graph readiness, packet order, delegation recommendations, artifact write-scope enforcement, or first-packet compatibility.

Regression tests for later cards must prove the safe-parallelization dry-run contract is unchanged. This M0 note makes no such code change.

## Problem statement from the latest external-agent run

The latest USDat/sUSDat run is the concrete negative benchmark:

- Run root: `dev/implementation/workflow-harness/tmp/usdat-susdat-collateral-fresh-20260606T133313Z`
- Parent validation summary: `.workflow/validation/summary.md` reports `Status: pass`, semantic review disabled, and zero findings.
- Parent run index: `index.md` reports `Status: review_required`, unresolved market/credit-manager, sizing, leverage, horizon, risk-policy, wallet eligibility, and route/liquidation blockers.
- Parent return: `agentic-flow/analyze-and-propose.md` reports `Propose: request_more_inputs`, `Preview: blocked`, `Execute: blocked`, semantic review not run, and workflow decision readiness `review_required`.
- Combined report: `verification/workflow-harness-report.json` has formal validation `pass`, semantic review `not_run`, workflow decision `review_required`, and proposal gate `request_more_inputs` / `review_required`.
- Asset child report currently mirrors formal validation into `workflow_decision.status=pass` when no separate workflow-decision metadata exists.
- Oracle child report correctly surfaces missing or inconclusive Gearbox facts and keeps workflow decision `review_required`.

This is better than the earlier false-green failure because parent proposal status is conservative, but it still exposes the core split problem: formatted artifacts can appear complete before raw decision evidence has been independently accepted, and child workflow-decision metadata is not uniformly grounded in raw facts.

## Split architecture delta

Add a gated chain inside the existing Analyze → Propose harness:

```text
decision-contract
→ investigation-brief
→ raw research bundle
→ raw quality gate
→ formatter packet
→ formatted legacy artifacts
→ traceability/status gate
→ final proposal gate
```

The chain is sequential in quality authority, not a scheduling rewrite. It can still be surfaced through the existing packet registry and execution graph once implemented by later cards.

### 1. Decision contract

The decision contract defines what the user must be able to decide and which fact families are mandatory before a result can be called decision-ready.

Minimum fields:

- `decision_id`
- `user_question`
- `allowed_terminal_statuses`: domain statuses such as `decision_ready`, `review_required`, `request_more_inputs`, and `cannot_underwrite`
- `decision_grade_success_criteria`
- `required_fact_families`
- `blocking_fact_families`
- `workflow_scope`: asset, oracle, combined, market, borrow asset, chain, position side, and Analyze-only boundary
- `legacy_artifact_paths` that must still be filled by the formatter
- `status_monotonicity_policy`

The contract extends the existing stage-contract envelope; it does not replace `user/references/workflows/*/stage-contracts.md`.

### 2. Investigation brief

The investigation brief converts the decision contract into a worker-facing research assignment.

It should name exact fact slots, acceptable evidence classes, negative-search requirements, freshness windows, calculation/scenario requirements, and terminal blocker semantics. It should reuse protocol adapters such as the Gearbox oracle adapter instead of embedding token-specific logic.

The researcher has no authority to produce final user-facing recommendations beyond raw status fields and blockers.

### 3. Raw research bundle

The raw research bundle is the only source of new facts for the formatter.

Minimum bundle contents:

- evidence ledger entries using `contracts/evidence-ledger.schema.json`
- fact results using the existing fact-state enum: `found`, `not_applicable`, `input_missing`, `not_investigated`, `investigated_no_result`, `source_unavailable`, `source_inconclusive`, `contradicted`
- unresolved gate list with owner, source, method, acceptance criteria, and status
- calculation or scenario bands where the stage contract requires quantitative usefulness
- negative-investigation proof objects for `investigated_no_result`
- raw artifact manifest with paths relative to the run root
- status recommendation limited to the decision contract's allowed terminal statuses

`not_investigated` must remain a failure state. It must never be upgraded into `investigated_no_result` without source-class coverage and raw evidence paths.

### 4. Raw quality gate

The raw quality gate runs before formatting.

It should fail or return `review_required` when required facts are absent, unresolved facts have blocking decision effects, quantitative sections are all skipped, semantic review is configured but unavailable, source evidence is filename-level only, no-result proofs are incomplete, or the raw bundle cannot support the decision contract.

This gate extends the existing deterministic validators and semantic critic path; it does not replace formal validation.

### 5. Formatter packet

The formatter packet receives only:

- the decision contract
- the accepted raw bundle
- the formatting contract
- legacy artifact paths that must be filled

The formatter must not add new facts, upgrade raw statuses, invent evidence, or convert `review_required` / `request_more_inputs` into `pass`. If it needs a new fact, it must emit a formatter blocker that routes back to the researcher/raw gate.

Legacy formatted paths remain compatible unless a later card explicitly proves and documents a migration path.

### 6. Traceability/status gate

The traceability gate verifies every material formatted claim maps to a raw `fact_id` or `evidence_id` and that final statuses are monotonic from the raw bundle.

Minimum checks:

- every material claim in final Markdown has claim-level raw support
- every risk, blocker, calculation, route, oracle fact, liquidation assumption, or eligibility statement maps to a raw fact/evidence id
- formatted status is no better than the raw status unless a documented human override is present
- child workflow decisions are derived from fact summaries, not from formal validation status alone
- parent proposal gate is the conservative rollup of formal validation, semantic quality, raw decision status, and formatted traceability

### 7. Final proposal gate

The final proposal gate answers: what can the workflow safely do next?

Allowed statuses:

- `decision_ready`: raw evidence and formatted artifacts satisfy the decision contract; Preview/Execute still require their own gates.
- `review_required`: evidence exists but a human/critic must accept risk, inconclusive sources, or nonblocking no-results.
- `request_more_inputs`: user/run inputs are missing, such as position size, leverage, horizon, wallet eligibility, or policy.
- `cannot_underwrite`: required facts or routes cannot support a safe underwriting/proposal decision.
- `blocked`: source access, investigation, contradiction, or required evidence is unresolved.

Plain `pass` is acceptable only for formal validation or subchecks. It is not enough for final user-facing workflow readiness.

## Board acceptance criteria

The board is done only when all of the following hold:

1. The USDat/sUSDat run root is preserved or copied into an exact negative regression fixture that represents a formally complete but not decision-ready external-agent output.
2. The fixture fails or conservatively reports `review_required` / `request_more_inputs` until raw evidence, semantic review, child workflow decisions, traceability, and parent proposal gate all satisfy the decision contract.
3. `semantic_review_status=not_run` or `semantic_review_unavailable` is never treated as green for a filled external-agent output unless the decision contract explicitly scopes semantic review out and records why.
4. A child workflow with no explicit workflow-decision metadata does not default to decision-grade `pass`; it defaults to `not_evaluated`, `review_required`, or a fact-derived conservative status.
5. Asset S6 cannot be considered decision-useful when required route, size, leverage, horizon, wallet eligibility, issuer, liquidation, exit, or policy assumptions are missing without a scenario-contract fallback and conservative terminal status.
6. Oracle analysis cannot be decision-useful until recursive feed graph facts, source primitive audits, market/Credit Manager context, allowed-token status, exit-health-factor implications, route/liquidation availability, and feed authority/freshness facts are either found, accepted no-result with proof, or correctly blocking.
7. Formatted artifacts can be generated only from an accepted raw research bundle; every material formatted claim maps back to raw `fact_id` / `evidence_id`.
8. Status monotonicity is enforced from raw bundle → formatted artifacts → child workflow decision → parent proposal gate.
9. Existing safe-parallelization tests and dry-run behavior remain unchanged.
10. Existing quality-gate taxonomy, evidence ledger schema, protocol adapters, semantic critic runner, and regression-eval suite remain canonical and are extended rather than duplicated.

## Downstream card boundaries

- M1 should define decision-contract and raw-bundle schemas by extending the existing quality-gate taxonomy and evidence-ledger contract.
- M2 should generate researcher packets that collect facts and raw evidence, not final reports.
- M3 should implement raw quality and decision-usefulness validators that fail weak research before formatting.
- M4 should generate formatter packets and implement traceability/status monotonicity checks without touching scheduler metadata.
- M5 should apply the split to asset-investment-diligence, especially S6 quantitative usefulness and underwriting terminal statuses.
- M6 should apply the split to oracle-analysis, especially recursive primitive coverage and Gearbox protocol-fit facts.
- M7 should make parent proposal and next-action surfaces conservative across formal validation, semantic review, raw decision status, and traceability.
- M8 should add the USDat/sUSDat negative fixture and full matrix proving the old failure mode cannot pass as decision-ready.
- M9 should run the end-to-end dry run, docs update, and rollout checklist.

## Verification for this M0 note

This note is doc-only. Verification should confirm:

- the file exists at `dev/implementation/workflow-harness/researcher-formatter-split-design-delta.md`
- git status shows this note as the only M0-created artifact
- no execution-graph, ready-packet, parallel-wave, delegation, or scheduler code changed
- no existing quality-gate taxonomy file was replaced

Relevant commands for this M0 slice:

```bash
git status --short -- dev/implementation/workflow-harness/researcher-formatter-split-design-delta.md
git diff --name-only -- dev/tools/workflow_entrypoint.py dev/tools/workflow_entrypoint_contracts.py dev/tools/validate_workflow_run.py dev/tools/semantic_critic_runner.py dev/tools/workflow_protocol_adapters.py dev/implementation/workflow-harness/investigation-result-taxonomy-and-quality-gates.md dev/implementation/workflow-harness/evidence-ledger-schema.md dev/implementation/workflow-harness/semantic-critic-rubric-v1.md
```

Full harness tests are intentionally deferred to implementation cards because this M0 slice changes no executable code.
