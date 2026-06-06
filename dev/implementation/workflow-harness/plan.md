# Workflow harness and staged prompt upgrade plan

Purpose: design a deterministic harness for formal workflow compliance in `front-knowledge-base` runs. This plan is intentionally implementation-only planning: it does not judge token economics, oracle correctness, investment conclusions, or user suitability.

Inputs used:

- `CLAUDE.md`.
- `dev/implementation/workflow-harness/internal-audit.md`.
- `dev/implementation/workflow-harness/external-harness-research.md`.
- `user/references/workflows/asset-investment-diligence/*`.
- `user/references/workflows/oracle-analysis/*`.
- Gearbox/front-kb workflow references loaded for runtime workflow placement and post-Discover `Analyze -> Propose` artifact shape.

## 1. Target implementation shape

Add one script entry point plus a small importable harness package:

```text
dev/tools/validate_workflow_run.py
dev/tools/workflow_harness/
  __init__.py
  cli.py
  models.py
  paths.py
  manifests.py
  markdown.py
  checks/
    asset.py
    oracle.py
    flow.py
    catalog.py
  fixtures/
    good/
    bad/
  tests/
```

The script is the only supported CLI. The package exists so tests can call checks directly without shelling out.

Implementation should stay local-first and dependency-light. Use Python standard library for path and Markdown checks. Use `jsonschema` or Pydantic only if the repository already accepts the dependency or the implementer adds it with an explicit dependency decision. Do not add remote LLM graders.

## 2. Validator CLI interface

Primary command:

```bash
python3 dev/tools/validate_workflow_run.py \
  --workflow <asset-investment-diligence|oracle-analysis|combined-analyze-propose> \
  --run-root <path> \
  --format <json|markdown|json,markdown> \
  [--report-dir <path>] \
  [--write-verification] \
  [--strict-warnings] \
  [--fixtures-root dev/tools/workflow_harness/fixtures]
```

Required arguments:

- `--workflow`: selects the check set.
- `--run-root`: path to the workflow run root. For combined runs, this is the parent root that contains `asset-investment-diligence/`, `oracle-analysis/`, and `agentic-flow/`.
- `--format`: one or both of `json` and `markdown`.

Optional arguments:

- `--report-dir`: writes reports outside the run root. If absent, reports print to stdout unless `--write-verification` is set.
- `--write-verification`: writes a harness report under `<run-root>/verification/` without creating or overwriting the workflow's canonical final verification file.
- `--strict-warnings`: exits nonzero for P2 findings.
- `--fixtures-root`: lets tests run against copied fixtures without hardcoded absolute paths.

Exit codes:

- `0`: no P0 or P1 findings. P2 warnings are allowed unless `--strict-warnings` is set.
- `1`: one or more P1 findings, or P2 findings with `--strict-warnings`.
- `2`: one or more P0 structural findings, invalid CLI input, invalid JSON, unreadable run root, or missing declared final verification.

Example commands:

```bash
python3 dev/tools/validate_workflow_run.py \
  --workflow asset-investment-diligence \
  --run-root dev/implementation/asset-diligence-2026-06-05-sample-base-token-sample-vault-token \
  --format json,markdown

python3 dev/tools/validate_workflow_run.py \
  --workflow oracle-analysis \
  --run-root dev/implementation/oracle-analysis-2026-06-05-sample-base-token-sample-vault-token \
  --format json,markdown

python3 dev/tools/validate_workflow_run.py \
  --workflow combined-analyze-propose \
  --run-root dev/implementation/sample-base-token-sample-vault-token-agentic-analyze-propose-2026-06-05 \
  --format json,markdown \
  --write-verification
```

## 3. JSON report schema

The validator must emit a stable JSON object. The object is a validator report, not a financial or oracle-quality verdict.

```json
{
  "schema_version": "workflow-harness-report-v1",
  "generated_at": "2026-06-05T00:00:00Z",
  "workflow": "asset-investment-diligence-v1 | oracle-analysis-v1 | combined-analyze-propose-v1",
  "run_root": "dev/implementation/<run-slug>",
  "status": "pass | review_required | fail",
  "exit_code": 0,
  "summary": {
    "P0": 0,
    "P1": 0,
    "P2": 0,
    "files_checked": 0,
    "json_files_parsed": 0,
    "links_checked": 0,
    "declared_paths_checked": 0
  },
  "inputs": {
    "workflow_contracts": [
      "user/references/workflows/<workflow>/workflow.json",
      "user/references/workflows/<workflow>/output-structure.md",
      "user/references/workflows/<workflow>/stage-contracts.md"
    ],
    "manifest": "run-manifest.json",
    "final_index": "index.md",
    "final_verification": "verification/<canonical-final-verification>.md"
  },
  "findings": [
    {
      "id": "verification.declared_file_exists",
      "severity": "P0",
      "workflow": "oracle-analysis-v1",
      "path": "verification/final-oracle-analysis-verification.md",
      "field": "final_verification",
      "expected": "declared file exists under run root",
      "actual": "missing",
      "message": "Manifest declares final verification path but the file is absent.",
      "fix_hint": "Create the run-level final verification or mark the run incomplete before reporting completion."
    }
  ],
  "checks": [
    {
      "id": "manifest.json_valid",
      "severity": "P0",
      "result": "pass | fail | skipped",
      "path": "run-manifest.json",
      "message": "run-manifest.json parsed successfully"
    }
  ],
  "generated_files": [
    "verification/workflow-harness-verification.md"
  ]
}
```

Required report rules:

- `status=fail` if any P0 exists.
- `status=review_required` if no P0 exists and at least one P1 exists.
- `status=pass` only when P0 and P1 counts are zero.
- Every finding must include `id`, `severity`, `path`, `message`, and `fix_hint`.
- Findings must reference paths and missing labels. They must not include raw evidence dumps.
- Check IDs must be stable because fixtures and prompts will cite them.

## 4. Markdown verification generation

Default mode is read-only. The validator prints reports to stdout and does not mutate the run.

When `--write-verification` is set:

- Asset run: write `<run-root>/verification/workflow-harness-verification.md`.
- Oracle run: write `<run-root>/verification/workflow-harness-verification.md`.
- Combined run: write `<run-root>/verification/combined-analyze-propose-verification.md`.
- If `--report-dir` is also set, write the same Markdown and JSON there with deterministic filenames.
- Never create or overwrite the canonical workflow final verification files:
  - `verification/final-investment-analysis-verification.md`.
  - `verification/final-oracle-analysis-verification.md`.

The generated Markdown must contain:

````text
# Workflow harness verification

- Workflow: ...
- Run root: ...
- Status: pass | review_required | fail
- Generated at: ...
- Validator command: ...
- Exit code: ...

## Summary

| Severity | Count |
|---|---:|
| P0 | 0 |
| P1 | 0 |
| P2 | 0 |

## Findings

| Severity | Check ID | Path | Message | Fix hint |
|---|---|---|---|---|

## Checks run

| Check ID | Result | Path | Message |
|---|---|---|---|

## JSON report

```json
{...compact report...}
```
````

Workflow final verification prompts should be updated so agents run the validator and paste or link the harness report summary inside the canonical final verification file. The harness report itself is evidence; it is not the canonical final verification and cannot hide a missing canonical verification file.

## 5. Required asset workflow checks

Apply these checks when `--workflow asset-investment-diligence` is selected.

P0 structural checks:

1. `manifest.json_valid`: `run-manifest.json` parses as JSON.
2. `manifest.workflow_id_asset`: `workflow_id` equals `asset-investment-diligence-v1`.
3. `manifest.required_fields_asset`: manifest includes `run_id`, `run_artifact_root`, `tokens`, `pt_markets`, `x_research_scopes`, `final_index`, and `final_verification`.
4. `paths.final_index_exists`: manifest `final_index` resolves under the run root.
5. `paths.final_verification_exists`: manifest `final_verification` resolves under the run root.
6. `layout.asset_root_files_exist`: `README.md`, `run-manifest.json`, and `index.md` exist.
7. `layout.asset_token_files_exist`: every token in `tokens[]` has the required files from `output-structure.md`.
8. `layout.asset_pt_files_exist_or_skipped`: every PT market in scope has required files, or `pt_markets` is an empty array with an explicit skipped marker in `index.md` or final verification.
9. `layout.asset_social_files_exist_or_skipped`: every social scope in scope has required files, or `x_research_scopes` is an empty array with an explicit skipped marker.
10. `links.local_paths_resolve`: local Markdown links and code-spanned artifact paths that look like run-local paths resolve.

P1 field checks:

1. `asset.scope_identity_fields`: per-token `scope.json` includes chain, symbol, token address, intended use, and status or explicit null/skipped markers.
2. `asset.s1_required_topics`: token technical/research files cover identity, issuer, backing/NAV, transfer restrictions, mint/redeem access, freeze/blacklist/pause/forced-transfer/admin controls, liquidity, oracle/accounting method, audits/incidents, and missing fields.
3. `asset.s2_required_sections`: token `analyst-report.md` contains the required S2 sections and a technical appendix pointer.
4. `asset.s3_pt_calculation_fields`: PT reports, when present, include exact market/PT/SY/YT IDs, maturity, accounting/output assets, PT price, accounting asset price, gross ROI, simple APR, compound APY, break-even accounting-asset drawdown, liquidity snapshot, and inherited-vs-PT-specific risk split.
5. `asset.s4_social_citation_fields`: social artifacts, when present, include query log, source index, source count, and claim-level `citation_degraded` markers where URL/date/handle is missing.
6. `asset.s5_social_synthesis_fields`: social synthesis, when present, covers return models, risk narratives, contradictions, citation degradation, and open threads.
7. `asset.s6_quantitative_fields`: S6 files include exact labels or structured rows for Gross ROI, Simple annualized return, Compound annualized return when relevant, Points EV / ROI / annualized return, Expected loss, Exit cost, Risk-adjusted ROI / annualized return, Break-even points ROI, Break-even terminal drawdown, and Price-stability certainty score. Missing values are allowed only as `null`, `not_in_scope`, or `skipped_due_to_missing_input` with a reason.
8. `asset.verification_credibility`: final verification checks field-level evidence, not only headings or broad prose.
9. `asset.no_upstream_allocation_recommendation`: S1-S5 source reports do not contain unsupported allocation, Preview, Execute, or suitability recommendations.

P2 hardening checks:

1. `asset.command_evidence_present`: final verification includes command, cwd, exit code, and output marker.
2. `asset.status_values_known`: per-scope statuses use `pass`, `review_required`, or `blocked`.
3. `asset.raw_dump_absent_from_index`: top-level index does not paste large raw source dumps.

## 6. Required oracle workflow checks

Apply these checks when `--workflow oracle-analysis` is selected.

P0 structural checks:

1. `manifest.json_valid`: `run-manifest.json` parses as JSON.
2. `manifest.workflow_id_oracle`: `workflow_id` equals `oracle-analysis-v1`.
3. `manifest.required_fields_oracle`: manifest includes `run_id`, `run_artifact_root`, `scopes`, `final_index`, and `final_verification`.
4. `paths.final_index_exists`: manifest `final_index` resolves under the run root.
5. `paths.final_verification_exists`: manifest `final_verification` resolves under the run root.
6. `layout.oracle_root_files_exist`: `README.md`, `run-manifest.json`, and `index.md` exist.
7. `layout.oracle_scope_files_exist`: every scope has `scope.json`, `oracle/scope.md`, `oracle/feed-graph.md`, `oracle/node-classification.md`, `oracle/source-primitive-audit.md`, `oracle/stress-tradeoff-analysis.md`, `oracle/protocol-fit-memo.md`, `raw/feed-probes.json`, `raw/source-evidence/`, and `verification/oracle-analysis-verification.md`.
8. `layout.oracle_comparison_files_exist`: declared comparison files exist when comparisons are in scope.
9. `links.local_paths_resolve`: local Markdown links and code-spanned artifact paths that look like run-local paths resolve.

P1 field checks:

1. `oracle.scope_policy_fields`: per-scope files include asset, protocol, chain, position side or explicit null, token role or explicit null, feed discovery path, and accepted methodology or explicit null.
2. `oracle.feed_graph_recursive`: feed graph identifies the top-level feed and either expands each non-leaf child or records a no-child explanation.
3. `oracle.feed_formula_present`: feed graph or classification reconstructs the pricing formula in human terms.
4. `oracle.feed_probes_json_valid`: `raw/feed-probes.json` parses and references probed nodes.
5. `oracle.node_classification_complete`: every graph node is classified as market, fundamental, NAV, hardcoded, or hybrid/composite.
6. `oracle.leaf_primitives_audited`: every leaf/source primitive named in the graph is covered by source primitive audit.
7. `oracle.staleness_bounds_recorded`: staleness, bounds, skip flags, challenge windows, or explicit unavailable markers are present where exposed.
8. `oracle.stress_tradeoff_fields`: stress analysis covers short-term volatility, long-term depeg, manipulation/TWAP lag, liquidation feasibility, cascade risk, trap risk, and who bears loss.
9. `oracle.conclusion_quad_present`: final verdicts explicitly state position side, token role, stress direction, and loss bearer for each relevant side.
10. `oracle.side_specific_verdicts`: borrower / Credit Account operator, pool LP / lender, liquidator, and curator/operator outcomes are split when relevant.
11. `oracle.gearbox_fields_present`: when protocol is Gearbox, protocol-fit memo includes main and reserve feed paths, safe-pricing rule and exit Health Factor implication, Liquidation Threshold, Liquidation Threshold ramp, max leverage implied by Liquidation Threshold, staleness/bounds, feed swap / reserve / timelock status, delayed-withdrawal branch, forbidden-token branch, and issuer-controlled branch interactions.
12. `oracle.gearbox_parsing_reference_applied`: when protocol is Gearbox, the run cites or records applying `user/references/workflows/oracle-analysis/gearbox-price-feed-parsing.md`.
13. `oracle.no_top_level_only_verdict`: verdict does not stop at labels such as External, Composite, Bounded, or ERC4626.
14. `oracle.verification_credibility`: final verification checks field-level evidence, not only file existence.

P2 hardening checks:

1. `oracle.command_evidence_present`: final verification includes command, cwd, exit code, and output marker.
2. `oracle.raw_dump_absent_from_index`: top-level index does not paste large raw RPC dumps.
3. `oracle.status_values_known`: per-scope statuses use `pass`, `review_required`, or `blocked`.

## 7. Required combined post-Discover Analyze -> Propose checks

Apply these checks when `--workflow combined-analyze-propose` is selected. This is a state-machine harness for the canonical `Discover -> Analyze -> Propose -> Preview -> Execute -> Monitor` loop.

P0 structural checks:

1. `flow.parent_root_exists`: run root exists.
2. `flow.child_asset_root_exists`: `asset-investment-diligence/` exists under the parent root.
3. `flow.child_oracle_root_exists`: `oracle-analysis/` exists under the parent root.
4. `flow.propose_handoff_exists`: `agentic-flow/analyze-and-propose.md` exists.
5. `flow.child_asset_validation_runs`: child asset root passes the asset harness or its P0/P1 findings are imported into the combined report.
6. `flow.child_oracle_validation_runs`: child oracle root passes the oracle harness or its P0/P1 findings are imported into the combined report.
7. `flow.parent_index_maps_children`: parent `index.md` or `README.md` links to asset, oracle, and agentic-flow outputs.
8. `links.local_paths_resolve`: parent and child run-local paths resolve from their actual nesting level.

P1 stage-gate checks:

1. `flow.discover_state_declared`: handoff names whether Discover was supplied by premise, completed by the agent, or blocked.
2. `flow.analyze_artifacts_declared`: handoff names asset and oracle final verification files actually read.
3. `flow.propose_status_declared`: Propose has one of `ready_for_preview`, `request_more_inputs`, or `blocked`.
4. `flow.unresolved_gates_request_more_inputs`: if asset/oracle findings or handoff blockers include unresolved support, eligibility, feed, route/depth, wallet, policy, or live-input gates, Propose must be `request_more_inputs` or `blocked`.
5. `flow.preview_execute_blocked_when_unresolved`: Preview and Execute are blocked unless all support, eligibility, feed, route/depth, wallet, and user-policy gates are resolved or an explicit human override file is present.
6. `flow.no_unsupported_execution_recommendation`: combined handoff does not recommend a live Credit Account opening, allocation, transaction, Preview, or Execute step from Analyze-only evidence.
7. `flow.monitor_not_started_before_execute`: Monitor is not marked started unless Execute is complete.
8. `flow.requested_next_checks_named`: Propose lists concrete next checks rather than vague review language.

P2 hardening checks:

1. `flow.stage_status_table_present`: handoff contains a stage-status table covering Discover, Analyze, Propose, Preview, Execute, and Monitor.
2. `flow.command_evidence_present`: combined verification includes validator command evidence.
3. `flow.raw_dump_absent`: parent index and handoff cite child artifact paths rather than pasting raw evidence.

## 8. Fixture strategy

Store fixtures under `dev/tools/workflow_harness/fixtures/`. Keep them small enough to review. Prefer pruned copies that retain manifests, indexes, final verification files, and representative per-token/per-scope artifacts over full raw evidence dumps.

Required positive fixture:

```text
dev/tools/workflow_harness/fixtures/good/good-agentic-sample-assets/
```

Source shape: copy or prune the known-good combined run from the internal audit. Expected result:

- `combined-analyze-propose` returns exit code `0`.
- Child asset and oracle validations return exit code `0`.
- `agentic-flow/analyze-and-propose.md` maps Discover, Analyze, Propose, Preview, Execute, and Monitor.
- Propose is `request_more_inputs`; Preview and Execute are blocked.
- Final verification files include deterministic command evidence.

Required negative fixture:

```text
dev/tools/workflow_harness/fixtures/bad/missing-final-oracle-verification/
```

Source shape: minimal oracle run where `run-manifest.json` and/or `index.md` declare `verification/final-oracle-analysis-verification.md`, but the file is absent. Expected result:

- `oracle-analysis` returns exit code `2`.
- JSON report includes P0 `paths.final_verification_exists` or `verification.declared_file_exists`.
- Markdown report names the missing path and fix hint.

Additional recommended negative fixtures:

- `bad/asset-heading-overclaim/`: S6 headings exist but exact quantitative field labels are missing. Expected P1 `asset.s6_quantitative_fields` and `asset.verification_credibility`.
- `bad/nested-sibling-path-broken/`: nested investment-analysis file references `../oracle-analysis-...` when `../../oracle-analysis-...` is required. Expected P0 or P1 local path finding.
- `bad/oracle-side-labels-missing/`: oracle verdict prose exists but position side, token role, stress direction, loss bearer, or cascade-vs-trap labels are absent. Expected P1 oracle side-field findings.
- `bad/missing-propose-handoff/`: asset and oracle roots exist but no `agentic-flow/analyze-and-propose.md`. Expected P0 `flow.propose_handoff_exists`.
- `bad/ready-for-preview-with-unresolved-gates/`: combined handoff marks Preview or Execute ready while support, eligibility, route/depth, feed, or user-policy gates are unresolved. Expected P1 flow-gate findings.

Fixture tests should assert only check IDs, severity counts, status, and exit code. They should not snapshot large Markdown output unless normalized to remove timestamps and absolute paths.

## 9. Workflow docs and prompts to update

Update docs after the validator exists. Do not change workflow meaning; only make completion evidence stricter and machine-checkable.

Asset workflow files:

- `user/references/workflows/asset-investment-diligence/runbook.md`: add validator command to S7 and make final reporting contingent on P0/P1-free harness status or explicit blockers.
- `user/references/workflows/asset-investment-diligence/stage-contracts.md`: add required stage-envelope fields and exact S6 quantitative field labels / null-marker rules.
- `user/references/workflows/asset-investment-diligence/output-structure.md`: document optional `verification/workflow-harness-verification.md` as generated harness evidence, while preserving canonical final verification.
- `user/references/workflows/asset-investment-diligence/subagent-prompts.md`: strengthen S6 and S7 prompts to require exact labels, command evidence, and validator report summary.
- `user/references/workflows/asset-investment-diligence/workflow.json`: add validator-related validation phrases to S7 without changing stage order.

Oracle workflow files:

- `user/references/workflows/oracle-analysis/runbook.md`: add validator command to S6 and require generated harness report summary in final verification.
- `user/references/workflows/oracle-analysis/stage-contracts.md`: add explicit conclusion quad fields: position side, token role, stress direction, loss bearer, and cascade-vs-trap framing.
- `user/references/workflows/oracle-analysis/output-structure.md`: document optional `verification/workflow-harness-verification.md` as generated harness evidence, while preserving canonical final verification.
- `user/references/workflows/oracle-analysis/subagent-prompts.md`: update optional verifier prompt to call the validator and include exact Gearbox-specific protocol-fit rows.
- `user/references/workflows/oracle-analysis/workflow.json`: add validator-related validation phrases to S6 without changing stage order.

Combined flow docs:

- `CLAUDE.md`: add a short note that post-Discover agentic runs must produce `agentic-flow/analyze-and-propose.md` and pass the combined harness before reporting Preview or Execute readiness.
- `README.md`: add the harness path only if the validator becomes part of documented workflow operations.
- If a dedicated combined-flow prompt is introduced, place it under `user/references/workflows/` only when it is reusable runtime workflow knowledge; otherwise keep implementation design notes under `dev/implementation/workflow-harness/`.

Do not edit old run artifacts merely to make fixtures pass. Copy/prune fixtures under the harness fixture directory and leave historical evidence intact.

## 10. Acceptance commands for implementation task

The implementation task should pass these commands from `/Users/ilya/Documents/Codex/front-knowledge-base`:

```bash
python3 -m pytest dev/tools/workflow_harness/tests

python3 dev/tools/validate_workflow_run.py \
  --workflow asset-investment-diligence \
  --run-root dev/tools/workflow_harness/fixtures/good/good-agentic-sample-assets/asset-investment-diligence \
  --format json,markdown

python3 dev/tools/validate_workflow_run.py \
  --workflow oracle-analysis \
  --run-root dev/tools/workflow_harness/fixtures/good/good-agentic-sample-assets/oracle-analysis \
  --format json,markdown

python3 dev/tools/validate_workflow_run.py \
  --workflow combined-analyze-propose \
  --run-root dev/tools/workflow_harness/fixtures/good/good-agentic-sample-assets \
  --format json,markdown

python3 dev/tools/validate_workflow_run.py \
  --workflow oracle-analysis \
  --run-root dev/tools/workflow_harness/fixtures/bad/missing-final-oracle-verification \
  --format json

git diff --check -- \
  dev/tools/validate_workflow_run.py \
  dev/tools/workflow_harness \
  user/references/workflows/asset-investment-diligence \
  user/references/workflows/oracle-analysis \
  CLAUDE.md \
  README.md
```

If the vault is validated from the parent `ai-assistant` monorepo, also run from `/Users/ilya/ai-assistant`:

```bash
python3 scripts/workspace_sync.py --check
python3 scripts/workspace_policy_check.py --all
```

The negative-fixture command should exit `2`. The test suite should assert that expected nonzero exit code rather than treating it as a failing test.

## 11. Out of scope

- No token economic-quality grading.
- No oracle correctness grading beyond formal field, path, and stage-contract compliance.
- No live RPC, explorer, X, Dune, or web fetches inside the validator.
- No remote LLM reviewer or model-based judge.
- No automatic repair of run artifacts.
- No overwriting canonical final verification files from the harness.
- No changes to the canonical workflow stage order.
- No broad rewrite of workflow docs, README, or CLAUDE beyond validator-specific prompt/check additions.
- No production UI or dashboard.
- No conversion of historical bad runs into passing runs.

## 12. Implementation sequence

1. Add report models and path resolver.
2. Add manifest/file-shape checks for asset and oracle runs.
3. Add required label/section checks for asset S6 and oracle side-specific verdicts.
4. Add local path/link resolver with nested-path awareness.
5. Add Markdown report generation and `--write-verification` behavior.
6. Add fixture tree and pytest coverage for one good combined run and one bad missing-final-oracle run.
7. Add the remaining negative fixtures.
8. Add combined Analyze -> Propose state-machine checks.
9. Update workflow docs and prompts listed above.
10. Run acceptance commands and record output in the implementation task handoff.
