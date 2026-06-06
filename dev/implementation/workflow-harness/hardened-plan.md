# Hardened execution plan — workflow harness

Purpose: convert the reviewed harness plan into an execution-ready implementation brief. This document incorporates the formal review blockers from `plan-review.md` and keeps the scope limited to deterministic workflow-compliance validation for `front-knowledge-base` artifacts.

This brief does not implement validator code. It specifies the final milestones, edit boundaries, validator checks, fixtures, safety rules, acceptance commands, and definition of done for the implementation task.

## Inputs and scope

Inputs reviewed:

- `CLAUDE.md`.
- `dev/implementation/workflow-harness/plan.md`.
- `dev/implementation/workflow-harness/plan-review.md`.
- `dev/implementation/workflow-harness/internal-audit.md`.
- `dev/implementation/workflow-harness/external-harness-research.md`.
- `user/references/workflows/asset-investment-diligence/output-structure.md`.
- `user/references/workflows/asset-investment-diligence/stage-contracts.md`.
- `user/references/workflows/oracle-analysis/output-structure.md`.
- `user/references/workflows/oracle-analysis/stage-contracts.md`.

Scope boundary:

- Validate formal workflow compliance only: manifests, folder shape, declared paths, required fields, final-verification credibility, parent-return/status consistency, fixture failures, and post-Analyze stage gates.
- Do not grade token economic quality, oracle correctness, investment suitability, or live execution quality.
- Do not fetch live RPC, explorers, X, Dune, web pages, or remote LLM reviewers inside the validator.
- Do not rewrite workflow meaning or historical run artifacts to make fixtures pass.

## Final milestone list and edit boundaries

Each milestone may edit only the files listed for that milestone. If implementation needs another source file, update this brief or get review before adding it.

### M1 — CLI, report model, and exit-code contract

Goal: create the stable validator entry point and report schema before adding workflow-specific checks.

May edit:

- `dev/tools/validate_workflow_run.py`
- `dev/tools/workflow_harness/__init__.py`
- `dev/tools/workflow_harness/cli.py`
- `dev/tools/workflow_harness/models.py`
- `dev/tools/workflow_harness/reports.py`
- `dev/tools/workflow_harness/checks/catalog.py`
- `dev/tools/workflow_harness/tests/test_cli_report.py`

Acceptance commands:

```bash
python3 -m pytest dev/tools/workflow_harness/tests/test_cli_report.py -q
python3 dev/tools/validate_workflow_run.py --help
python3 - <<'PY'
import subprocess
proc = subprocess.run(["python3", "dev/tools/validate_workflow_run.py", "--workflow", "bad", "--run-root", ".", "--format", "json"], text=True, capture_output=True)
assert proc.returncode == 2, proc.stdout + proc.stderr
PY
```

M1 acceptance: `--help` is available; invalid CLI input exits `2`; generated JSON reports contain `schema_version`, `workflow`, `run_root`, `status`, `exit_code`, `summary`, `findings`, and `checks`.

### M2 — Manifest schema, path normalization, and artifact reconciliation

Goal: close the manifest/path false-pass gap identified in review finding P1-1.

May edit:

- `dev/tools/workflow_harness/paths.py`
- `dev/tools/workflow_harness/manifests.py`
- `dev/tools/workflow_harness/checks/asset.py`
- `dev/tools/workflow_harness/checks/oracle.py`
- `dev/tools/workflow_harness/checks/catalog.py`
- `dev/tools/workflow_harness/tests/test_manifest_paths.py`
- `dev/tools/workflow_harness/fixtures/bad/missing-final-oracle-verification/**`
- `dev/tools/workflow_harness/fixtures/bad/broken-relative-link/**`
- `dev/tools/workflow_harness/fixtures/bad/missing-parent-return-status/**`

Acceptance commands:

```bash
python3 -m pytest dev/tools/workflow_harness/tests/test_manifest_paths.py -q
python3 - <<'PY'
import json
import subprocess
cmd = [
    "python3", "dev/tools/validate_workflow_run.py",
    "--workflow", "oracle-analysis",
    "--run-root", "dev/tools/workflow_harness/fixtures/bad/missing-final-oracle-verification",
    "--format", "json",
]
proc = subprocess.run(cmd, text=True, capture_output=True)
assert proc.returncode == 2, proc.stdout + proc.stderr
report = json.loads(proc.stdout)
ids = {finding["id"] for finding in report["findings"]}
assert "paths.final_verification_exists" in ids or "verification.declared_file_exists" in ids
PY
```

M2 acceptance: manifest entries are validated, `run_artifact_root` normalizes to `--run-root`, per-token/per-scope `artifact_dir` values stay under the run root, manifest identity reconciles with each `scope.json` and folder slug, and absolute or parent-escaping paths fail unless explicitly declared as allowed external references.

### M3 — Asset and oracle Markdown contract checks

Goal: close the heading-only and missing-field false-pass classes.

May edit:

- `dev/tools/workflow_harness/markdown.py`
- `dev/tools/workflow_harness/verification.py`
- `dev/tools/workflow_harness/checks/asset.py`
- `dev/tools/workflow_harness/checks/oracle.py`
- `dev/tools/workflow_harness/checks/catalog.py`
- `dev/tools/workflow_harness/tests/test_markdown_contracts.py`
- `dev/tools/workflow_harness/fixtures/bad/asset-heading-overclaim/**`
- `dev/tools/workflow_harness/fixtures/bad/oracle-side-specific-omission/**`

Acceptance commands:

```bash
python3 -m pytest dev/tools/workflow_harness/tests/test_markdown_contracts.py -q
python3 - <<'PY'
import json
import subprocess
cases = [
    ("asset-investment-diligence", "dev/tools/workflow_harness/fixtures/bad/asset-heading-overclaim", {"asset.s6_quantitative_fields", "asset.verification_credibility"}),
    ("oracle-analysis", "dev/tools/workflow_harness/fixtures/bad/oracle-side-specific-omission", {"oracle.conclusion_quad_present"}),
]
for workflow, root, expected in cases:
    proc = subprocess.run(["python3", "dev/tools/validate_workflow_run.py", "--workflow", workflow, "--run-root", root, "--format", "json"], text=True, capture_output=True)
    assert proc.returncode in (1, 2), proc.stdout + proc.stderr
    report = json.loads(proc.stdout)
    ids = {finding["id"] for finding in report["findings"]}
    missing = expected - ids
    assert not missing, (root, missing, ids)
PY
```

M3 acceptance: broad headings do not satisfy exact required fields; oracle conclusions must expose position side, token role, stress direction, and loss bearer; verification tables that claim `pass` without concrete field checks produce findings.

### M4 — Local links, Obsidian wikilinks, and code-spanned paths

Goal: close broken relative-link failures, including nested sibling-run paths.

May edit:

- `dev/tools/workflow_harness/links.py`
- `dev/tools/workflow_harness/markdown.py`
- `dev/tools/workflow_harness/paths.py`
- `dev/tools/workflow_harness/checks/catalog.py`
- `dev/tools/workflow_harness/tests/test_links.py`
- `dev/tools/workflow_harness/fixtures/bad/broken-relative-link/**`

Acceptance commands:

```bash
python3 -m pytest dev/tools/workflow_harness/tests/test_links.py -q
python3 - <<'PY'
import json
import subprocess
proc = subprocess.run(["python3", "dev/tools/validate_workflow_run.py", "--workflow", "asset-investment-diligence", "--run-root", "dev/tools/workflow_harness/fixtures/bad/broken-relative-link", "--format", "json"], text=True, capture_output=True)
assert proc.returncode == 2, proc.stdout + proc.stderr
report = json.loads(proc.stdout)
ids = {finding["id"] for finding in report["findings"]}
assert "links.local_paths_resolve" in ids or "links.markdown.local_resolve" in ids
PY
```

M4 acceptance: Markdown links, artifact-map paths, manifest paths, code-spanned local paths, and run-local Obsidian wikilinks are resolved from the file where they appear. Repository-wide Obsidian graph validation remains out of scope unless a file under `user/references/workflows/` is edited in M7.

### M5 — Combined Analyze -> Propose state machine and parent-return contract

Goal: close review finding P1-2 by validating parent-return/status reconciliation or explicitly reporting that parent verification is still needed.

May edit:

- `dev/tools/workflow_harness/checks/flow.py`
- `dev/tools/workflow_harness/parent_return.py`
- `dev/tools/workflow_harness/cli.py`
- `dev/tools/workflow_harness/models.py`
- `dev/tools/workflow_harness/reports.py`
- `dev/tools/workflow_harness/checks/catalog.py`
- `dev/tools/workflow_harness/tests/test_combined_flow.py`
- `dev/tools/workflow_harness/fixtures/good/good-agentic-sample-assets/**`
- `dev/tools/workflow_harness/fixtures/bad/missing-propose-handoff/**`
- `dev/tools/workflow_harness/fixtures/bad/ready-for-preview-incorrectly/**`
- `dev/tools/workflow_harness/fixtures/bad/missing-parent-return-status/**`

Acceptance commands:

```bash
python3 -m pytest dev/tools/workflow_harness/tests/test_combined_flow.py -q
python3 dev/tools/validate_workflow_run.py \
  --workflow combined-analyze-propose \
  --run-root dev/tools/workflow_harness/fixtures/good/good-agentic-sample-assets \
  --parent-return dev/tools/workflow_harness/fixtures/good/good-agentic-sample-assets/agentic-flow/parent-return.json \
  --format json,markdown
python3 - <<'PY'
import json
import subprocess
cases = [
    ("dev/tools/workflow_harness/fixtures/bad/missing-propose-handoff", {"flow.propose_handoff_exists"}, 2),
    ("dev/tools/workflow_harness/fixtures/bad/ready-for-preview-incorrectly", {"flow.unresolved_gates_request_more_inputs", "flow.preview_execute_blocked_when_unresolved"}, 1),
    ("dev/tools/workflow_harness/fixtures/bad/missing-parent-return-status", {"parent_return.contract_fields_present", "parent_return.status_reconciles_children"}, 1),
]
for root, expected, min_exit in cases:
    proc = subprocess.run(["python3", "dev/tools/validate_workflow_run.py", "--workflow", "combined-analyze-propose", "--run-root", root, "--format", "json"], text=True, capture_output=True)
    assert proc.returncode >= min_exit, proc.stdout + proc.stderr
    report = json.loads(proc.stdout)
    ids = {finding["id"] for finding in report["findings"]}
    assert expected & ids, (root, expected, ids)
PY
```

M5 acceptance: combined validation imports child asset/oracle failures, requires `agentic-flow/analyze-and-propose.md`, blocks Preview/Execute when unresolved gates remain, and validates `agentic-flow/parent-return.json` when supplied. If no parent-return artifact is supplied, the report must include P1 `parent_return.needs_parent_verification` and must not claim that the parent response was validated.

### M6 — Fixture matrix and regression suite

Goal: promote the review-required negative fixtures into required tests.

May edit:

- `dev/tools/workflow_harness/fixtures/good/good-agentic-sample-assets/**`
- `dev/tools/workflow_harness/fixtures/bad/missing-final-oracle-verification/**`
- `dev/tools/workflow_harness/fixtures/bad/asset-heading-overclaim/**`
- `dev/tools/workflow_harness/fixtures/bad/broken-relative-link/**`
- `dev/tools/workflow_harness/fixtures/bad/oracle-side-specific-omission/**`
- `dev/tools/workflow_harness/fixtures/bad/ready-for-preview-incorrectly/**`
- `dev/tools/workflow_harness/fixtures/bad/missing-propose-handoff/**`
- `dev/tools/workflow_harness/fixtures/bad/missing-parent-return-status/**`
- `dev/tools/workflow_harness/tests/conftest.py`
- `dev/tools/workflow_harness/tests/test_fixtures.py`

Acceptance commands:

```bash
python3 -m pytest dev/tools/workflow_harness/tests/test_fixtures.py -q
python3 -m pytest dev/tools/workflow_harness/tests -q
```

M6 acceptance: the full positive/negative fixture matrix asserts expected exit code, status, severity counts, and expected check IDs. Tests must not snapshot timestamps, absolute paths, or full Markdown reports.

### M7 — Minimal workflow docs and prompt updates

Goal: wire the validator into runtime workflow evidence without changing workflow semantics.

May edit only after M1-M6 pass:

- `user/references/workflows/asset-investment-diligence/runbook.md`
- `user/references/workflows/asset-investment-diligence/stage-contracts.md`
- `user/references/workflows/asset-investment-diligence/output-structure.md`
- `user/references/workflows/asset-investment-diligence/subagent-prompts.md`
- `user/references/workflows/asset-investment-diligence/workflow.json`
- `user/references/workflows/oracle-analysis/runbook.md`
- `user/references/workflows/oracle-analysis/stage-contracts.md`
- `user/references/workflows/oracle-analysis/output-structure.md`
- `user/references/workflows/oracle-analysis/subagent-prompts.md`
- `user/references/workflows/oracle-analysis/workflow.json`
- `CLAUDE.md`
- `README.md`

Acceptance commands:

```bash
python3 -m pytest dev/tools/workflow_harness/tests -q
python3 dev/tools/validate_workflow_run.py \
  --workflow combined-analyze-propose \
  --run-root dev/tools/workflow_harness/fixtures/good/good-agentic-sample-assets \
  --parent-return dev/tools/workflow_harness/fixtures/good/good-agentic-sample-assets/agentic-flow/parent-return.json \
  --format json,markdown \
  --write-verification
git diff --check -- \
  dev/tools/validate_workflow_run.py \
  dev/tools/workflow_harness \
  user/references/workflows/asset-investment-diligence \
  user/references/workflows/oracle-analysis \
  CLAUDE.md \
  README.md
```

M7 acceptance: workflow docs require agents to run the validator and include or link the harness report summary in canonical final verification. The docs must preserve stage order, artifact roots, output folder names, and existing workflow meaning.

### M8 — Final implementation acceptance and handoff

Goal: prove the implementation is complete and safe to hand to future agents.

May edit:

- `dev/implementation/workflow-harness/implementation-verification.md`

Acceptance commands:

```bash
python3 -m pytest dev/tools/workflow_harness/tests -q
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
  --parent-return dev/tools/workflow_harness/fixtures/good/good-agentic-sample-assets/agentic-flow/parent-return.json \
  --format json,markdown
python3 -m pytest dev/tools/workflow_harness/tests/test_fixtures.py -q
git diff --check -- \
  dev/tools/validate_workflow_run.py \
  dev/tools/workflow_harness \
  user/references/workflows/asset-investment-diligence \
  user/references/workflows/oracle-analysis \
  CLAUDE.md \
  README.md
git status --short -- \
  dev/tools/validate_workflow_run.py \
  dev/tools/workflow_harness \
  user/references/workflows/asset-investment-diligence \
  user/references/workflows/oracle-analysis \
  CLAUDE.md \
  README.md \
  dev/implementation/workflow-harness/implementation-verification.md
```

If the vault changes affect generated workspace metadata in `/Users/ilya/ai-assistant`, also run from `/Users/ilya/ai-assistant`:

```bash
python3 scripts/workspace_sync.py --check
python3 scripts/workspace_policy_check.py --all
```

M8 acceptance: all fixture tests pass; good fixtures exit `0`; bad fixtures are asserted through pytest or inline subprocess wrappers; the implementation handoff records commands, cwd, exit codes, and relevant output markers.

## Exact validator checks by severity

Severity semantics:

- P0: structural failure. Report status `fail`; exit `2`.
- P1: contract failure or false-pass risk. Report status `review_required` when no P0 exists; exit `1`.
- P2: hardening warning. Report status can remain `pass`; exit `0` unless `--strict-warnings` is set, then exit `1`.

### P0 checks

Common checks:

- `cli.input_valid`: workflow, run root, format, and optional `--parent-return` arguments are valid.
- `manifest.json_valid`: `run-manifest.json` parses as JSON.
- `manifest.workflow_id_asset`: asset manifest `workflow_id` is `asset-investment-diligence-v1`.
- `manifest.workflow_id_oracle`: oracle manifest `workflow_id` is `oracle-analysis-v1`.
- `manifest.required_fields_asset`: asset manifest includes `run_id`, `run_artifact_root`, `tokens`, `pt_markets`, `x_research_scopes`, `final_index`, and `final_verification`.
- `manifest.required_fields_oracle`: oracle manifest includes `run_id`, `run_artifact_root`, `scopes`, `final_index`, and `final_verification`.
- `manifest.run_artifact_root_matches_run_root`: manifest `run_artifact_root` normalizes to the supplied `--run-root` or to an explicitly allowed workspace-relative equivalent.
- `manifest.entry_schema_asset`: every asset token entry includes `token_slug`, `chain`, `symbol`, `address`, `artifact_dir`, and `status`; every PT/social entry follows the workflow contract or is explicitly empty/skipped.
- `manifest.entry_schema_oracle`: every oracle scope entry includes `scope_id`, `scope_slug`, `scope_type`, `chain`, `asset_symbol`, `asset_address`, `protocol`, `position_sides`, `token_roles`, `artifact_dir`, and `status`.
- `manifest.artifact_dir_under_run_root`: every `artifact_dir` resolves under the run root.
- `manifest.entry_identity_matches_scope`: each manifest entry reconciles with the folder slug and the corresponding `scope.json` identity fields.
- `paths.final_index_exists`: manifest `final_index` resolves under the run root and exists.
- `paths.final_verification_exists`: manifest `final_verification` resolves under the run root and exists.
- `paths.no_absolute_parent_escape`: local artifact paths are not absolute, parent-escaping, or sibling-run paths unless explicitly marked as allowed external references.
- `links.local_paths_resolve`: local Markdown links, artifact-map paths, manifest paths, and code-spanned run-local paths resolve from their actual source file.
- `parent_return.json_valid_when_supplied`: `--parent-return` or `agentic-flow/parent-return.json`, when supplied, parses as JSON.

Asset checks:

- `layout.asset_root_files_exist`: asset run has `README.md`, `run-manifest.json`, and `index.md`.
- `layout.asset_token_files_exist`: every token manifest entry has `scope.json`, required research files, `technical-report.md`, `analyst-report.md`, and `verification.md`.
- `layout.asset_pt_files_exist_or_skipped`: PT files exist when PT markets are in scope, or `pt_markets` is empty with an explicit skipped marker in `index.md` or final verification.
- `layout.asset_social_files_exist_or_skipped`: social files exist when X/social scopes are in scope, or `x_research_scopes` is empty with an explicit skipped marker.

Oracle checks:

- `layout.oracle_root_files_exist`: oracle run has `README.md`, `run-manifest.json`, and `index.md`.
- `layout.oracle_scope_files_exist`: every scope has `scope.json`, `oracle/scope.md`, `oracle/feed-graph.md`, `oracle/node-classification.md`, `oracle/source-primitive-audit.md`, `oracle/stress-tradeoff-analysis.md`, `oracle/protocol-fit-memo.md`, `raw/feed-probes.json`, `raw/source-evidence/`, and `verification/oracle-analysis-verification.md`.
- `layout.oracle_comparison_files_exist`: declared comparison files exist when comparisons are in scope.

Combined-flow checks:

- `flow.parent_root_exists`: combined parent root exists.
- `flow.child_asset_root_exists`: `asset-investment-diligence/` exists under the parent root.
- `flow.child_oracle_root_exists`: `oracle-analysis/` exists under the parent root.
- `flow.propose_handoff_exists`: `agentic-flow/analyze-and-propose.md` exists.
- `flow.child_asset_validation_runs`: child asset validation runs and imports any P0/P1 findings.
- `flow.child_oracle_validation_runs`: child oracle validation runs and imports any P0/P1 findings.
- `flow.parent_index_maps_children`: parent `index.md` or `README.md` links to asset, oracle, and agentic-flow outputs.

### P1 checks

Asset checks:

- `asset.scope_identity_fields`: per-token `scope.json` includes chain, symbol, token address, intended use, and status or explicit null/skipped markers.
- `asset.manifest_entry_reconciles_scope`: manifest entry identity, `scope.json`, and folder slug agree.
- `asset.s1_required_topics`: token research files cover identity, issuer, backing/NAV, transfer restrictions, mint/redeem access, freeze/blacklist/pause/forced-transfer/admin controls, liquidity, oracle/accounting method, audits/incidents, and missing fields.
- `asset.s2_required_sections`: token `analyst-report.md` contains the required S2 sections and a technical appendix pointer.
- `asset.s3_pt_calculation_fields`: PT reports, when present, include exact market/PT/SY/YT IDs, maturity, accounting/output assets, PT price, accounting asset price, gross ROI, simple APR, compound APY, break-even accounting-asset drawdown, liquidity snapshot, and inherited-vs-PT-specific risk split.
- `asset.s4_social_citation_fields`: social artifacts, when present, include query log, source index, source count, and claim-level `citation_degraded` markers where URL/date/handle is missing.
- `asset.s5_social_synthesis_fields`: social synthesis, when present, covers return models, risk narratives, contradictions, citation degradation, and open threads.
- `asset.s6_quantitative_fields`: S6 files include exact labels or structured rows for Gross ROI, Simple annualized return, Compound annualized return when relevant, Points EV, Points ROI, Points annualized return, Expected loss, Exit cost, Risk-adjusted ROI, Risk-adjusted annualized return, Break-even points ROI, Break-even terminal drawdown, and Price-stability certainty score. Missing values must be `null`, `not_in_scope`, or `skipped_due_to_missing_input` with a reason.
- `asset.verification_credibility`: final verification checks field-level evidence, not only headings or broad prose.
- `asset.no_upstream_allocation_recommendation`: S1-S5 source reports do not contain unsupported allocation, Preview, Execute, or suitability recommendations.

Oracle checks:

- `oracle.scope_policy_fields`: per-scope files include asset, protocol, chain, position side or explicit null, token role or explicit null, feed discovery path, and accepted methodology or explicit null.
- `oracle.manifest_entry_reconciles_scope`: manifest scope identity reconciles with `scope.json` and folder slug.
- `oracle.feed_graph_recursive`: feed graph identifies the top-level feed and either expands each non-leaf child or records a no-child explanation.
- `oracle.feed_formula_present`: feed graph or classification reconstructs the pricing formula in human terms.
- `oracle.feed_probes_json_valid`: `raw/feed-probes.json` parses and references probed nodes.
- `oracle.node_classification_complete`: every graph node is classified as market, fundamental, NAV, hardcoded, or hybrid/composite.
- `oracle.leaf_primitives_audited`: every graph leaf/source primitive is covered by source primitive audit.
- `oracle.staleness_bounds_recorded`: staleness, bounds, skip flags, challenge windows, or explicit unavailable markers are present where exposed.
- `oracle.stress_tradeoff_fields`: stress analysis covers short-term volatility, long-term depeg, manipulation/TWAP lag, liquidation feasibility, cascade risk, trap risk, and who bears loss.
- `oracle.conclusion_quad_present`: final verdicts explicitly state position side, token role, stress direction, and loss bearer for each relevant side.
- `oracle.side_specific_verdicts`: borrower / Credit Account operator, pool LP / lender, liquidator, and curator/operator outcomes are split when relevant.
- `oracle.gearbox_fields_present`: when protocol is Gearbox, protocol-fit memo includes main and reserve feed paths, safe-pricing rule and exit Health Factor implication, Liquidation Threshold, Liquidation Threshold ramp, max leverage implied by Liquidation Threshold, staleness/bounds, feed swap/reserve/timelock status, delayed-withdrawal branch, forbidden-token branch, and issuer-controlled branch interactions.
- `oracle.gearbox_parsing_reference_applied`: when protocol is Gearbox, the run cites or records applying `user/references/workflows/oracle-analysis/gearbox-price-feed-parsing.md`.
- `oracle.no_top_level_only_verdict`: verdict does not stop at labels such as External, Composite, Bounded, or ERC4626.
- `oracle.verification_credibility`: final verification checks field-level evidence, not only file existence.

Parent-return and status reconciliation checks:

- `parent_return.contract_fields_present`: supplied parent-return artifact includes `status`, `run_artifact_root`, manifest/index/final-verification paths, scope directories, and summary counts required by the relevant workflow contract.
- `parent_return.status_reconciles_children`: parent-return `status` agrees with child P0/P1 findings and child `pass` / `review_required` / `blocked` counts.
- `parent_return.summary_counts_reconcile_children`: `blocked_scopes`, `review_required_scopes`, and dominant blockers agree with child manifests, indexes, and final verification files.
- `parent_return.paths_resolve`: every path returned by the parent artifact resolves under the run root or is explicitly marked as external.
- `parent_return.needs_parent_verification`: no parent-return artifact was supplied, so the local harness cannot claim parent response validation.
- `status.root_reconciles_manifest_index_verification`: root index, manifest entries, final verification status, harness report status, and parent-return status do not disagree silently.

Combined-flow stage checks:

- `flow.discover_state_declared`: handoff names whether Discover was supplied by premise, completed by the agent, or blocked.
- `flow.analyze_artifacts_declared`: handoff names asset and oracle final verification files actually read.
- `flow.propose_status_declared`: Propose has one of `ready_for_preview`, `request_more_inputs`, or `blocked`.
- `flow.unresolved_gates_request_more_inputs`: unresolved support, eligibility, feed, route/depth, wallet, policy, or live-input gates force Propose to `request_more_inputs` or `blocked`.
- `flow.preview_execute_blocked_when_unresolved`: Preview and Execute remain blocked unless all support, eligibility, feed, route/depth, wallet, and user-policy gates are resolved or an explicit human override file is present.
- `flow.no_unsupported_execution_recommendation`: combined handoff does not recommend a live Credit Account opening, allocation, transaction, Preview, or Execute from Analyze-only evidence.
- `flow.monitor_not_started_before_execute`: Monitor is not marked started unless Execute is complete.
- `flow.requested_next_checks_named`: Propose lists concrete next checks rather than vague review language.

### P2 checks

- `asset.command_evidence_present`: asset final verification includes command, cwd, exit code, and output marker.
- `asset.status_values_known`: per-scope status prose uses `pass`, `review_required`, or `blocked`.
- `asset.raw_dump_absent_from_index`: top-level asset index cites raw evidence paths instead of pasting large raw dumps.
- `oracle.command_evidence_present`: oracle final verification includes command, cwd, exit code, and output marker.
- `oracle.raw_dump_absent_from_index`: top-level oracle index cites raw evidence paths instead of pasting large raw RPC dumps.
- `oracle.status_values_known`: per-scope status prose uses `pass`, `review_required`, or `blocked`.
- `flow.stage_status_table_present`: combined handoff has a stage-status table for Discover, Analyze, Propose, Preview, Execute, and Monitor.
- `flow.command_evidence_present`: combined verification includes validator command evidence.
- `flow.raw_dump_absent`: parent index and handoff cite child artifact paths rather than raw evidence dumps.
- `links.obsidian_wikilinks_resolve`: run-local or edited-workflow Obsidian wikilinks resolve to existing notes and anchors where practical. Repo-wide Obsidian validation is outside this harness unless M7 edits workflow docs.

## Required fixture paths

Positive fixture:

- `dev/tools/workflow_harness/fixtures/good/good-agentic-sample-assets/`
  - expected combined exit `0`;
  - expected child asset exit `0`;
  - expected child oracle exit `0`;
  - includes `agentic-flow/analyze-and-propose.md` with Propose `request_more_inputs` and Preview/Execute blocked;
  - includes `agentic-flow/parent-return.json` for local parent-return validation.

Negative fixtures:

- `dev/tools/workflow_harness/fixtures/bad/missing-final-oracle-verification/`
  - expected oracle exit `2`;
  - expected P0: `paths.final_verification_exists` or `verification.declared_file_exists`.
- `dev/tools/workflow_harness/fixtures/bad/asset-heading-overclaim/`
  - expected asset exit `1` or `2` according to final severity policy;
  - expected P1: `asset.s6_quantitative_fields` and `asset.verification_credibility`.
- `dev/tools/workflow_harness/fixtures/bad/broken-relative-link/`
  - expected exit `2` when a declared local path is missing;
  - expected P0: `links.local_paths_resolve` or `links.markdown.local_resolve`.
- `dev/tools/workflow_harness/fixtures/bad/oracle-side-specific-omission/`
  - expected oracle exit `1` or `2` according to final severity policy;
  - expected P1: `oracle.conclusion_quad_present` and, when relevant, `oracle.side_specific_verdicts`.
- `dev/tools/workflow_harness/fixtures/bad/ready-for-preview-incorrectly/`
  - expected combined exit `1` or `2` according to final severity policy;
  - expected P1: `flow.unresolved_gates_request_more_inputs` and `flow.preview_execute_blocked_when_unresolved`.
- `dev/tools/workflow_harness/fixtures/bad/missing-propose-handoff/`
  - expected combined exit `2`;
  - expected P0: `flow.propose_handoff_exists`.
- `dev/tools/workflow_harness/fixtures/bad/missing-parent-return-status/`
  - expected combined exit `1` or `2` according to final severity policy;
  - expected P1: `parent_return.contract_fields_present` or `parent_return.status_reconciles_children`.

Fixture construction rules:

- Build fixtures from pruned copies. Keep manifests, indexes, final verification files, representative per-token/per-scope files, and only the raw evidence needed for path checks.
- Do not edit historical source runs merely to make fixtures pass.
- Keep all expected nonzero failures inside pytest or inline subprocess assertions. Do not put a raw expected-failure command into a required shell block without wrapping it.
- Fixture assertions should check exit code, report status, severity counts, and check IDs. They should not snapshot absolute paths, timestamps, or full Markdown reports.

## Rollback and safety notes

- Default validator mode is read-only. It prints reports to stdout and must not mutate a run unless `--write-verification` is explicitly set.
- `--write-verification` may write only generated harness reports:
  - `verification/workflow-harness-verification.md` for asset and oracle runs;
  - `verification/combined-analyze-propose-verification.md` for combined runs.
- The harness must never create or overwrite canonical workflow final verification files:
  - `verification/final-investment-analysis-verification.md`;
  - `verification/final-oracle-analysis-verification.md`.
- M7 documentation edits must wait until validator and fixture tests pass. If M7 causes semantic drift, roll back only the M7 docs and keep the validator implementation intact.
- Rollback for M1-M6 is deletion/revert of `dev/tools/validate_workflow_run.py` and `dev/tools/workflow_harness/**`; rollback for M8 is deletion/revert of `dev/implementation/workflow-harness/implementation-verification.md`.
- Do not touch unrelated modified/deleted files currently present in the vault working tree.
- Do not restore or rewrite deleted historical `dev/implementation/asset-risk-reports-mvp/**` files as part of this harness.
- Do not modify one-off run artifacts under `dev/implementation/asset-diligence-2026-06-05-sample-base-token-sample-vault-token/` or `dev/implementation/oracle-analysis-2026-06-05-sample-base-token-sample-vault-token/`; copy/prune them into fixtures instead.
- If workspace-wide generated files drift after M7, run the monorepo validation commands and record whether failures are caused by this change or pre-existing vault state.

## Final definition of done

The implementation is done only when all conditions below are true:

1. `dev/tools/validate_workflow_run.py` supports `asset-investment-diligence`, `oracle-analysis`, and `combined-analyze-propose` workflows.
2. JSON reports use the stable schema and exit-code policy in this brief.
3. P0/P1/P2 check IDs listed above are implemented or explicitly documented as intentionally out of scope before implementation begins.
4. Manifest entry schemas, `artifact_dir` resolution, `run_artifact_root` normalization, and scope/folder identity reconciliation are checked.
5. Parent-return validation is machine-checkable through `agentic-flow/parent-return.json` or `--parent-return`; if absent, the report includes P1 `parent_return.needs_parent_verification` and does not claim parent response validation.
6. Root index, manifest entries, final verification, harness status, and parent-return status cannot disagree silently.
7. Required negative fixtures cover missing final verification, field-credibility overclaim, broken local path, oracle side-specific omission, incorrect Preview/Execute readiness, missing Propose handoff, and missing parent-return/status reconciliation.
8. Positive fixture and all negative fixtures are covered by pytest assertions for exit code, severity counts, status, and expected check IDs.
9. Workflow docs and prompts are updated only after validator tests pass, and only to require validator evidence without changing stage order or artifact semantics.
10. Final implementation evidence records cwd, command, exit code, and output marker for every acceptance command.
11. `git diff --check` passes for touched files.
12. `git status --short` is reported for the touched path set, with unrelated pre-existing vault changes left untouched.
