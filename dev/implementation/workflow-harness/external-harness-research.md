# External harness research — task-specific workflow compliance

Task: R2 external research for `front-kb-workflow-harness`.

Scope: deterministic, local-first harness patterns for `front-knowledge-base` token and oracle workflows. This document addresses formal workflow compliance only: file shape, manifests, required fields, links, stage gates, validation credibility, and fixtures. It does not evaluate token economic quality.

Web access: used. Source links are included in each pattern and summarized at the end.

## Local failure classes to target

The harness should make these failures mechanically visible before an external agent claims completion:

1. Missing required files declared by `output-structure.md`, such as run-level final verification files or per-token oracle artifacts.
2. Manifest/path drift, including `run-manifest.json` entries that point to missing or wrongly nested paths.
3. Required fields omitted instead of explicitly marked `null`, `not_in_scope`, or `skipped_due_to_missing_input`.
4. Required sections present as broad prose but missing machine-checkable labels, especially quantitative underwriting fields and oracle side-specific conclusion fields.
5. Broken relative links, especially nested artifact links pointing to sibling run folders with the wrong `../` depth.
6. Final verification overclaim, where a verification file reports `pass` or `review_required` without checking the actual required fields and paths.
7. Missing post-Analyze Propose handoff: after Discover and Analyze, unresolved gates must produce `request_more_inputs`; Preview and Execute must remain blocked.
8. Universal oracle or asset verdicts that collapse side-specific required fields into one generic safe/unsafe conclusion.

## Pattern 1 — Contract-as-code schemas for manifests and stage envelopes

Use JSON Schema or Pydantic models as the first validation layer for machine-readable files: `run-manifest.json`, per-token `scope.json`, per-scope oracle `scope.json`, stage envelopes, and the validator's own report schema.

External pattern signal:

- JSON Schema is designed to declaratively validate JSON structure, constraints, and data types: https://json-schema.org/docs
- Python `jsonschema` exposes direct validation APIs, and `check-jsonschema` provides a local CLI / pre-commit hook: https://python-jsonschema.readthedocs.io/en/latest/validate/ and https://check-jsonschema.readthedocs.io/en/latest/
- Pydantic models validate typed data at model instantiation and can generate JSON Schema from models: https://pydantic.dev/docs/validation/latest/concepts/models/ and https://pydantic.dev/docs/validation/latest/concepts/json_schema/

Local implementation:

- Add `dev/tools/validate_workflow_run.py` as the single CLI entrypoint.
- Add `dev/tools/workflow_harness/schemas/` with schemas or Pydantic models for:
  - `asset-investment-diligence-v1` manifest;
  - `oracle-analysis-v1` manifest;
  - combined Analyze→Propose run index;
  - validator output report.
- Require exact workflow IDs and allowed statuses: `pass`, `review_required`, `blocked` for workflow artifacts; `request_more_inputs`, `ready_for_preview`, `blocked` for Propose gate output.
- Require explicit nullable fields where workflow contracts require them. Do not allow absent fields when the contract says unknown values must remain present as `null`.

Failure mapping:

- Catches omitted `final_verification`, missing `scopes` / `tokens`, absent `position_side` / `token_role`, missing `status`, and silent deletion of unknown inputs.
- Turns the formal critic's repeated “missing fields, not explicit null markers” finding into a deterministic P0/P1 report.

Concrete check IDs:

- `manifest.required_fields`
- `manifest.workflow_id.allowed`
- `manifest.status.allowed`
- `scope.unknowns_explicit`
- `validator_report.schema_valid`

## Pattern 2 — Filesystem shape rules generated from the workflow contracts

Build a deterministic file-tree validator from the two `output-structure.md` contracts. The validator should derive expected paths from manifest entries rather than using hardcoded token names.

External pattern signal:

- Pytest supports parametrized tests, which fits a matrix of workflow type × fixture run × expected status: https://docs.pytest.org/en/7.1.x/example/parametrize.html
- Pytest `tmp_path` gives each test its own temporary directory, which is useful for copying and mutating fixture runs without touching real artifacts: https://docs.pytest.org/en/stable/how-to/tmp_path.html

Local implementation:

- Implement path checks in `dev/tools/workflow_harness/file_shape.py`.
- For asset runs, derive required files from manifest `tokens[]`, `pt_markets[]`, and expected run-level folders:
  - `README.md`, `run-manifest.json`, `index.md`;
  - `tokens/<token_slug>/scope.json`;
  - token research/report/verification files;
  - `investment-analysis/*`;
  - `verification/final-investment-analysis-verification.md`.
- For oracle runs, derive required files from manifest `scopes[]` and `artifact_dir`:
  - per-scope `oracle/scope.md`, `feed-graph.md`, `node-classification.md`, `source-primitive-audit.md`, `stress-tradeoff-analysis.md`, `protocol-fit-memo.md`;
  - `raw/feed-probes.json` and `raw/source-evidence/`;
  - per-scope and run-level verification.
- Treat optional folders as explicit by contract: if `pt-markets/index.md` is required as a run-level summary, report it when missing even when there are no PT scopes.

Failure mapping:

- Catches oracle runs whose `index.md` points to `verification/final-oracle-analysis-verification.md` when that file is absent.
- Catches flat output folders that skip per-token / per-PT nesting.
- Catches a token appearing in the manifest but not in the physical tree.

Concrete check IDs:

- `files.run_root.required`
- `files.asset.token_tree.required`
- `files.oracle.scope_tree.required`
- `files.declared_paths.exist`
- `files.optional_summary_policy`

## Pattern 3 — Markdown contract checks for required sections and field labels

Use a lightweight Markdown parser / heading scanner plus regular expressions for required labels. Do not rely on “the topic is discussed somewhere” as passing evidence; require named sections or fields that downstream agents can locate.

External pattern signal:

- Promptfoo's deterministic assertion model separates exact/contains/regex/JSON/Javascript checks from model-graded evaluation. The local lesson is to translate rubrics into deterministic assertions first: https://www.promptfoo.dev/docs/configuration/expected-outputs/deterministic/ and https://www.promptfoo.dev/docs/configuration/expected-outputs/

Local implementation:

- Add `dev/tools/workflow_harness/markdown_contracts.py`.
- Represent each contract as data, not scattered code:
  - `dev/tools/workflow_harness/checks/asset_sections.yaml`
  - `dev/tools/workflow_harness/checks/oracle_sections.yaml`
  - `dev/tools/workflow_harness/checks/agentic_flow_sections.yaml`
- Checks should support:
  - required heading exists;
  - required table column exists;
  - required phrase/label exists;
  - each listed manifest scope has a corresponding section or row;
  - `null` / `not_in_scope` / `skipped_due_to_missing_input` markers exist for unresolved required fields.

Required local checks to encode first:

- Asset S6 report includes labels for Gross ROI, Simple annualized return, Compound annualized return when relevant, Points EV, Points ROI, Points annualized return, Expected loss, Exit cost, Risk-adjusted ROI, Risk-adjusted annualized return, Break-even points ROI, Break-even terminal drawdown, and Price-stability certainty score.
- Oracle protocol-fit memo includes side-specific verdicts for borrower / Credit Account operator, pool LP / lender, liquidator, and curator/operator, or explicit `not_in_scope` markers.
- Oracle final conclusions include position side, token role, stress direction, and loss bearer.
- Run `index.md` includes scope table, artifact map, blockers, and validation result.

Failure mapping:

- Catches reports that include “risk-adjusted” in prose but omit required underwriting fields.
- Catches oracle memos that discuss “safe” or “risky” globally without the required side split.
- Catches status summaries that do not expose final verification status.

Concrete check IDs:

- `md.asset.s6_quant_fields`
- `md.oracle.side_verdicts`
- `md.oracle.conclusion_quad`
- `md.index.artifact_map`
- `md.unknown_markers.explicit`

## Pattern 4 — Local link and relative-path resolver

Run a path resolver over every Markdown link, manifest path, and artifact-map path. Treat local path integrity as a first-class harness target, not a generic docs lint afterthought.

External pattern signal:

- `markdown-link-check` can recursively check links in a local Markdown folder: https://github.com/tcort/markdown-link-check
- The same idea can be implemented without a Node dependency by parsing local Markdown links and resolving them from each file's directory.

Local implementation:

- Add `dev/tools/workflow_harness/links.py`.
- Resolve four path classes separately:
  - manifest paths relative to run root;
  - artifact-map paths relative to the current Markdown file;
  - Markdown links with spaces / URL encoding;
  - cross-run references, which should either resolve or be explicitly marked `external_reference` with an absolute path.
- Do not make the harness depend on network availability. External HTTP links can be skipped or warned by default; local file links should be fail-fast.

Failure mapping:

- Catches broken sibling-run links like `../oracle-analysis-.../` from nested `investment-analysis/` folders when the correct depth is different.
- Catches `README.md` or `index.md` pointing to a declared final verification file that does not exist.
- Catches stale references after run folders are moved or archived.

Concrete check IDs:

- `links.markdown.local_resolve`
- `links.manifest.relative_paths`
- `links.artifact_map.resolve`
- `links.cross_run.explicit_external_reference`

## Pattern 5 — Verification credibility cross-check

Final verification documents should be checked against the harness report, not trusted as source of truth. A verification file that says “pass” while required checks were never run or required paths are missing is a formal failure.

External pattern signal:

- OpenAI's agent-eval guidance identifies traces as records of model calls, tool calls, guardrails, and handoffs, and then uses structured criteria to detect workflow-level failures: https://developers.openai.com/api/docs/guides/agent-evals
- Local adaptation: replace cloud trace grading with deterministic evidence traces from artifact manifests, validator reports, and final verification files.

Local implementation:

- The validator should produce `dev/implementation/<run>/verification/workflow-harness-report.json` and optionally `workflow-harness-report.md`.
- Final verification credibility rules:
  - if the harness report has P0/P1 failures, the final status cannot be `pass`;
  - every `pass` row in a verification Markdown table must map to a concrete check ID or be downgraded to `unchecked_claim`;
  - if a required field check is absent, verification status becomes `review_required` or `fail`, not `pass`;
  - if a final verification file is missing while the manifest declares it, report P0 regardless of `index.md` status text.
- Add a generated footer or front matter to future verification files:
  - `generated_by: validate_workflow_run.py`
  - `harness_report: verification/workflow-harness-report.json`
  - `harness_exit_code: 0|1|2`

Failure mapping:

- Catches the current class where a final verification table reports all required checks as pass but only confirms headings / broad presence, not field completeness.
- Catches `index.md` claiming `review_required` with no actual run-level final verification file.

Concrete check IDs:

- `verification.declared_file_exists`
- `verification.pass_rows_have_check_ids`
- `verification.status_matches_harness`
- `verification.generated_report_present`
- `verification.unchecked_claims`

## Pattern 6 — Golden-negative fixture catalog with expected finding IDs

Create small, intentionally bad fixture runs for each failure class. The goal is not broad examples; it is deterministic regression pressure on the validator.

External pattern signal:

- Pytest parametrization supports a simple fixture matrix.
- Syrupy is a pytest snapshot plugin that asserts immutability of computed results: https://syrupy-project.github.io/syrupy/

Local implementation:

- Add fixture roots under `dev/fixtures/workflow-harness/`:
  - `good/asset-minimal-pass-or-review/`
  - `good/oracle-minimal-review/`
  - `bad/missing-final-oracle-verification/`
  - `bad/manifest-path-drift/`
  - `bad/omitted-null-fields/`
  - `bad/missing-s6-quant-fields/`
  - `bad/oracle-universal-verdict/`
  - `bad/broken-relative-link/`
  - `bad/validation-overclaim/`
  - `bad/missing-propose-handoff/`
- Add `tests/test_workflow_harness_fixtures.py` that parametrizes these fixtures and asserts expected `finding_id`, `severity`, and `path` values.
- Keep fixtures minimal: a few files each, reduced Markdown, no large raw source dumps.
- Snapshot only the normalized report shape, not timestamps or absolute paths.

Failure mapping:

- Prevents regressions where the validator starts accepting missing run-level final verification files.
- Prevents “field present in prose” from passing when labels are missing.
- Prevents a future agent from deleting the Propose gate and still claiming the end-to-end flow is complete.

Concrete check IDs:

- `fixture.bad.missing_final_verification_fails`
- `fixture.bad.validation_overclaim_fails`
- `fixture.bad.universal_oracle_verdict_fails`
- `fixture.good.minimal_review_passes`

## Pattern 7 — Analyze→Propose state-machine gate

Model the canonical `Discover → Analyze → Propose → Preview → Execute → Monitor` loop as a deterministic state machine. The post-Discover combined run is not complete just because asset and oracle Analyze artifacts exist.

External pattern signal:

- Agent workflow eval guidance focuses on tool choice, handoffs, guardrails, and routing as first-class workflow-level questions: https://developers.openai.com/api/docs/guides/agent-evals
- The local equivalent is a check over declared stage states and handoff artifacts, not a model grader.

Local implementation:

- Add `dev/tools/workflow_harness/flow_gates.py`.
- Expected combined run files:
  - root `index.md` or `README.md` naming supplied Discover state;
  - `asset-investment-diligence/verification/final-investment-analysis-verification.md`;
  - `oracle-analysis/verification/final-oracle-analysis-verification.md`;
  - `agentic-flow/analyze-and-propose.md`.
- Required `agentic-flow/analyze-and-propose.md` fields:
  - Discover state supplied / missing inputs;
  - Analyze artifacts read;
  - Propose status;
  - requested next checks;
  - Preview status;
  - Execute status;
  - explicit non-proposal / non-execution statement.
- If any Analyze artifact is `review_required` or has blockers, Propose must be `request_more_inputs`, Preview must be `blocked`, and Execute must be `blocked` unless an explicit human override file exists.

Failure mapping:

- Catches a run that stops after Analyze and never writes a Propose handoff.
- Catches a run that says `ready_for_preview` while support, eligibility, route/depth, or user-policy gates are unresolved.
- Catches accidental action recommendations from a formal compliance workflow.

Concrete check IDs:

- `flow.discover_state_declared`
- `flow.analyze_artifacts_declared`
- `flow.propose_handoff_exists`
- `flow.unresolved_gates_request_more_inputs`
- `flow.preview_execute_blocked_when_unresolved`

## Pattern 8 — Rubric-to-test compiler for maintainable checks

Turn formal critic bullets and workflow contracts into a local YAML check catalog. This keeps the harness reviewable by docs/product agents while the validator remains deterministic.

External pattern signal:

- Promptfoo's assertion catalog is useful because each evaluation criterion has a concrete assertion type. Do the same locally, but without running a remote LLM judge: https://www.promptfoo.dev/docs/configuration/expected-outputs/
- OpenAI eval datasets reinforce the idea that repeatable evaluation needs fixed test inputs and expected results, even if this repo should keep execution local: https://developers.openai.com/api/docs/guides/evals

Local implementation:

- Add `dev/tools/workflow_harness/checks/*.yaml` with entries like:

```yaml
- id: md.oracle.conclusion_quad
  severity: P1
  applies_to: oracle-analysis-v1
  files:
    - tokens/*/oracle/protocol-fit-memo.md
  assertion: all_terms_present_per_scope
  required_terms:
    - position side
    - token role
    - stress direction
    - loss bearer
```

- Supported assertion types should be small and deterministic:
  - `file_exists`
  - `json_required_fields`
  - `json_enum`
  - `markdown_heading_exists`
  - `markdown_required_labels`
  - `markdown_table_columns`
  - `local_links_resolve`
  - `status_rule`
  - `regex_absent`
  - `declared_path_exists`
- Generate a human-readable checklist from the same YAML so reviewers can see exactly what the harness enforces.

Failure mapping:

- Prevents the harness from becoming another prose-only checklist.
- Makes it easy to add future checks for newly discovered bad fixtures without editing core validator logic.
- Keeps formal workflow compliance separate from token economic judgment.

Concrete check IDs:

- `checks.catalog.schema_valid`
- `checks.catalog.ids_unique`
- `checks.generated_markdown_current`
- `checks.no_economic_quality_assertions`

## Recommended local validator shape

CLI:

```bash
python3 dev/tools/validate_workflow_run.py \
  --workflow asset-investment-diligence \
  --run-root dev/implementation/<asset-run> \
  --format markdown,json

python3 dev/tools/validate_workflow_run.py \
  --workflow oracle-analysis \
  --run-root dev/implementation/<oracle-run> \
  --format markdown,json

python3 dev/tools/validate_workflow_run.py \
  --workflow combined-analyze-propose \
  --run-root dev/implementation/<combined-run> \
  --format markdown,json
```

Exit codes:

- `0`: no P0/P1 failures; warnings allowed.
- `1`: P1/P2 failures; review required.
- `2`: P0 structural failure, such as missing manifest, invalid JSON, missing declared final verification, or unreadable run root.

Report schema:

```json
{
  "workflow": "oracle-analysis-v1",
  "run_root": "dev/implementation/oracle-analysis-2026-06-05-sample-base-token-sample-vault-token",
  "status": "fail | review_required | pass",
  "summary": {"P0": 1, "P1": 3, "P2": 2},
  "findings": [
    {
      "id": "verification.declared_file_exists",
      "severity": "P0",
      "path": "verification/final-oracle-analysis-verification.md",
      "message": "Manifest declares final verification path but file is missing."
    }
  ]
}
```

## Prioritized implementation backlog

1. Implement manifest + file-shape validation for asset and oracle runs.
2. Add golden-negative fixtures for missing final verification, broken manifest path, missing S6 quant fields, universal oracle verdict, and missing Propose handoff.
3. Implement Markdown section/label checks for S6 asset underwriting and oracle side-specific verdicts.
4. Implement local link/path resolver.
5. Implement verification credibility cross-check and generated harness report.
6. Add combined Analyze→Propose state-machine checks.
7. Add YAML rubric-to-test catalog and generated checklist.
8. Add optional snapshot tests for normalized finding reports.

## Source index

- JSON Schema docs — declarative structure/type/constraint validation: https://json-schema.org/docs
- Python jsonschema validation docs: https://python-jsonschema.readthedocs.io/en/latest/validate/
- check-jsonschema local CLI / pre-commit hook: https://check-jsonschema.readthedocs.io/en/latest/
- Pydantic model validation and JSON Schema generation: https://pydantic.dev/docs/validation/latest/concepts/models/ and https://pydantic.dev/docs/validation/latest/concepts/json_schema/
- Pytest parametrization: https://docs.pytest.org/en/7.1.x/example/parametrize.html
- Pytest temporary directories: https://docs.pytest.org/en/stable/how-to/tmp_path.html
- Syrupy pytest snapshot plugin: https://syrupy-project.github.io/syrupy/
- Promptfoo deterministic assertions: https://www.promptfoo.dev/docs/configuration/expected-outputs/deterministic/
- Promptfoo assertion catalog: https://www.promptfoo.dev/docs/configuration/expected-outputs/
- markdown-link-check local Markdown link checker: https://github.com/tcort/markdown-link-check
- OpenAI agent workflow evals, used only as trace/handoff inspiration, not as a dependency: https://developers.openai.com/api/docs/guides/agent-evals
- OpenAI evals guide, used only for dataset/repeatability inspiration, not as a dependency: https://developers.openai.com/api/docs/guides/evals
