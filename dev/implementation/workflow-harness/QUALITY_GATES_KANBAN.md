# Workflow quality gates Kanban

Created: 2026-06-06T08:50:10Z

This board generalizes findings from the latest `Analyze → Propose` harness run into reusable workflow-quality improvements. It intentionally avoids token-specific remediation and focuses on patterns: investigation provenance, no-result semantics, semantic critic gates, protocol-investigation adapters, quantitative usefulness, and parent proposal gating.

## Board

- Slug: `front-kb-workflow-quality-gates`
- Name: `Front KB Workflow Quality Gates`
- DB path: `/Users/ilya/.hermes/kanban/boards/front-kb-workflow-quality-gates/kanban.db`
- Workspace for cards: `dir:/Users/ilya/Documents/Codex/front-knowledge-base`
- Assignee: `default`
- Active Hermes board after creation: unchanged (`hermes-core-selective-cleanup` remained current)
- Creation status snapshot: `running=1`, `todo=10`, `done=0`
- Latest orchestrator recovery snapshot: 2026-06-06T09:20Z — `done=3`, `running=3`, `todo=5`, `blocked=0` after accepting M2/M5 review-required completions and dispatching M6.
- Note: the dispatcher auto-claimed the root card after creation; no manual board switch was performed.

## Commands

```bash
hermes kanban boards list --json
hermes kanban --board front-kb-workflow-quality-gates stats
hermes kanban --board front-kb-workflow-quality-gates list --json
hermes kanban --board front-kb-workflow-quality-gates show --json <task-id>
hermes kanban --board front-kb-workflow-quality-gates runs <task-id>
hermes kanban --board front-kb-workflow-quality-gates log <task-id> --tail 120
```

## M9 regression eval replay

Canonical manifest:

- `dev/implementation/workflow-harness/fixtures/regression-evals/quality-gate-regression-suite.json`
- `dev/implementation/workflow-harness/fixtures/regression-evals/latest-quality-gate-seed.json`

Runnable local checks:

```bash
python3 dev/tools/run_fixture_checks.py
python3 -m pytest dev/tools/workflow_harness/tests -q
```

## Dependency graph

- `t_cc831331` — M0: Define generalized quality-gate architecture and investigation-result taxonomy
  - Root architecture card.
  - Defines `not_applicable`, `input_missing`, `not_investigated`, `investigated_no_result`, `source_unavailable`, `source_inconclusive`, `contradicted`.

- `t_a93148c4` — M1: Make generated stage packets force investigation instead of form filling
  - Parent: `t_cc831331`.
  - Ensures packets inline mandatory investigations and no-result proof templates.

- `t_b4ce9842` — M2: Add raw evidence ledger schema for reproducible live/source facts
  - Parent: `t_cc831331`.
  - Defines raw evidence schema for positive and negative investigations.

- `t_6933e264` — M3: Extend deterministic validators to reject unproven unknowns and stale placeholders
  - Parents: `t_a93148c4`, `t_b4ce9842`.
  - Catches not-investigated required facts, weak no-result claims, and stale verification text.

- `t_f330948e` — M4: Generalize protocol-specific investigation adapters and no-market semantics
  - Parent: `t_cc831331`.
  - Makes absence of a market/route valid only when the search itself is proven.

- `t_2385d323` — M5: Build independent semantic critic gate runner for stage quality
  - Parent: `t_cc831331`.
  - Adds LLM/subagent critic gates for quality that deterministic checks cannot judge.

- `t_7e145660` — M6: Author stage-specific critic rubrics for decision-grade outputs
  - Parent: `t_2385d323`.
  - Covers investigation adequacy, evidence sufficiency, asset diligence utility, oracle/protocol fit, quantitative underwriting, and parent proposal quality.

- `t_3e130b3d` — M7: Add Analyze-only scenario fallbacks for missing sizing/horizon inputs
  - Parents: `t_a93148c4`, `t_7e145660`.
  - Prevents empty underwriting when user-specific Preview inputs are missing but safe scenario analysis is possible.

- `t_1e6d0aa8` — M8: Fix status propagation and parent proposal-gate semantics
  - Parents: `t_6933e264`, `t_7e145660`.
  - Separates formal validation, semantic review, workflow decision, and proposal gate.

- `t_15391724` — M9: Build regression eval suite for quality gates and critic findings
  - Parents: `t_6933e264`, `t_f330948e`, `t_3e130b3d`, `t_1e6d0aa8`.
  - Locks generalized failure modes into tests/evals.

- `t_4395c3a8` — M10: Document and verify end-to-end quality-gated Analyze→Propose
  - Parent: `t_15391724`.
  - Final docs and e2e verification.

## Definitions of done for the board

- The harness distinguishes `investigated_no_result` from `not_investigated` with replayable evidence.
- Protocol-specific parameter absence can be accepted only after adapter-defined negative investigation.
- Deterministic validation rejects placeholder unknowns and stale validation text.
- Independent semantic critics can fail artifacts that obey headings but omit decision-making, calculations, investigation, or actionable proposals.
- Quantitative Analyze outputs use labelled scenario bands when exact Preview inputs are missing.
- Parent output reports formal validation separately from semantic/workflow readiness.
- Regression fixtures cover positive investigation, no-result investigation, not-investigated failure, low-quality form fill, scenario fallback, and actionable `request_more_inputs` proposal.
