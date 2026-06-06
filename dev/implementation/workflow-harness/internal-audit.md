# Internal audit — workflow contracts and good/bad run artifacts

Purpose: bounded internal research for workflow-harness validator design. This audit checks formal workflow compliance only. It does not assess token economics, oracle correctness, or investment quality.

## Inspected inputs

Workflow contracts:

- `CLAUDE.md`
- `user/references/workflows/asset-investment-diligence/output-structure.md`
- `user/references/workflows/asset-investment-diligence/stage-contracts.md`
- `user/references/workflows/asset-investment-diligence/runbook.md`
- `user/references/workflows/asset-investment-diligence/workflow.json`
- `user/references/workflows/oracle-analysis/output-structure.md`
- `user/references/workflows/oracle-analysis/stage-contracts.md`
- `user/references/workflows/oracle-analysis/runbook.md`
- `user/references/workflows/oracle-analysis/workflow.json`

Run artifacts:

- Known good combined run: `/Users/ilya/ai-assistant/projects/front-knowledge-base/dev/implementation/sample-base-token-sample-vault-token-agentic-analyze-propose-2026-06-05`
- External asset run: `dev/implementation/asset-diligence-2026-06-05-sample-base-token-sample-vault-token`
- External oracle run: `dev/implementation/oracle-analysis-2026-06-05-sample-base-token-sample-vault-token`

## Formal requirements extracted from contracts

### Vault-level requirements

- `CLAUDE.md` splits runtime knowledge and implementation lineage: `user/` is runtime knowledge and `dev/` is design lineage / implementation gaps / historical artifacts (`CLAUDE.md:9-14`).
- The canonical flow is `Discover → Analyze → Propose → Preview → Execute → Monitor` (`CLAUDE.md:14`). A run that completes Analyze but leaves live gates unresolved still needs a Propose handoff; it must not jump to Preview or Execute.
- Executable runtime workflows live under `user/references/workflows/`, including `oracle-analysis/` and `asset-investment-diligence/` (`CLAUDE.md:46-50`). One-off run artifacts stay under `dev/implementation/<run-slug>/`.
- Vault validation expectations include `git diff --check` and `git status --short` from the vault after moved/renamed/navigation changes, and monorepo sync/policy checks from `~/ai-assistant` when workspace-level generated files are affected (`CLAUDE.md:327-354`).

### Shared workflow-run requirements

- Every workflow run returns one artifact folder, not loose reports (`asset-investment-diligence/output-structure.md:1-4`, `oracle-analysis/output-structure.md:1-4`).
- Every run must include `README.md`, `run-manifest.json`, `index.md`, and a run-level final verification file (`asset-investment-diligence/output-structure.md:7-43`, `oracle-analysis/output-structure.md:7-50`).
- Unknown scope fields must remain present and be set to `null`, not silently deleted (`asset-investment-diligence/runbook.md:72`, `oracle-analysis/runbook.md:61-63`).
- Parent responses should return artifact paths, status, blockers, and validation result; they should not paste raw evidence dumps (`asset-investment-diligence/output-structure.md:151-176`, `oracle-analysis/output-structure.md:159-182`).
- Final verification must validate required files, cross-links, required sections/fields, and workspace checks, not merely the existence of broad headings (`asset-investment-diligence/stage-contracts.md:314-341`, `oracle-analysis/runbook.md:242-265`).

### Asset-investment-diligence requirements

Root files required by `output-structure.md`:

- `README.md`
- `run-manifest.json`
- `index.md`
- `pt-markets/index.md` when PTs are absent or summarized
- `x-research/index.md` when social scopes are absent or summarized
- `investment-analysis/quantitative-underwriting-methodology.md`
- `investment-analysis/investment-analyst-report-points-pt-risk-return.md`
- `investment-analysis/index.md`
- `verification/final-investment-analysis-verification.md`

Per-token files required by `output-structure.md`:

- `tokens/<token-slug>/scope.json`
- `tokens/<token-slug>/research/onchain-admin.md`
- `tokens/<token-slug>/research/issuer-backing-security.md`
- `tokens/<token-slug>/research/transfer-liquidity-oracle-governance.md`
- `tokens/<token-slug>/technical-report.md`
- `tokens/<token-slug>/analyst-report.md`
- `tokens/<token-slug>/verification.md`

Required manifest fields:

- `workflow_id`
- `run_id`
- `run_artifact_root`
- `tokens[]` with `token_slug`, `chain`, `symbol`, `address`, `artifact_dir`, and `status`
- `pt_markets[]`
- `x_research_scopes[]`
- `final_index`
- `final_verification`

Required S1 facts include token identity, issuer/protocol entity, backing/NAV model, transfer restrictions, mint/redeem access, freeze/blacklist/pause/forced-transfer/admin controls, liquidity venues/depth, oracle/accounting method, audits/incidents, and missing fields with decision effect (`asset-investment-diligence/stage-contracts.md:64-75`).

Required S2 report sections include executive view, token representation, risk implications, backing/NAV quality, liquidity and exit risk, controls/governance/legal restrictions, pricing/oracle risk, live-use checks, evidence quality, source map, and technical appendix pointer (`asset-investment-diligence/stage-contracts.md:98-110`).

Required S6 quantitative fields are exact validator fields, not optional prose topics (`asset-investment-diligence/stage-contracts.md:272-287`):

- Gross ROI
- Simple annualized return
- Compound annualized return, when relevant
- Points EV
- Points ROI
- Points annualized return
- Expected loss
- Exit cost
- Risk-adjusted ROI
- Risk-adjusted annualized return
- Break-even points ROI
- Break-even terminal drawdown
- Price-stability certainty score

Required S7 checks include required file existence, output structure, cross-link resolution, required sections, quantitative fields, absence of unsupported allocation conclusions, and workspace validation or isolated unrelated failures (`asset-investment-diligence/stage-contracts.md:328-337`).

### Oracle-analysis requirements

Root files required by `output-structure.md`:

- `README.md`
- `run-manifest.json`
- `index.md`
- `verification/final-oracle-analysis-verification.md`

Per-scope files required by `output-structure.md`:

- `tokens/<token-scope-slug>/scope.json` or `pt-markets/<pt-scope-slug>/scope.json`
- `oracle/scope.md`
- `oracle/feed-graph.md`
- `oracle/node-classification.md`
- `oracle/source-primitive-audit.md`
- `oracle/stress-tradeoff-analysis.md`
- `oracle/protocol-fit-memo.md`
- `raw/feed-probes.json`
- `raw/source-evidence/`
- `verification/oracle-analysis-verification.md`

Required manifest fields:

- `workflow_id`
- `run_id`
- `run_artifact_root`
- `scopes[]` with `scope_id`, `scope_slug`, `scope_type`, `chain`, `asset_symbol`, `asset_address`, `protocol`, `position_sides[]`, `token_roles[]`, `artifact_dir`, and `status`
- `final_index`
- `final_verification`

Required oracle workflow invariants:

- Do not produce a protocol-fit conclusion without `position_side` and `token_role`; if the run is neutral inventory, both fields must be `null` and the run must stop before protocol-fit conclusions (`oracle-analysis/runbook.md:61-63`).
- Feed analysis must recurse beyond top-level Gearbox wrapper labels and classify each node as market, fundamental, NAV, hardcoded, or hybrid (`oracle-analysis/runbook.md:96-110`, `oracle-analysis/runbook.md:130-154`).
- Source primitive audits must exist for graph leaves (`oracle-analysis/runbook.md:155-170`).
- Stress analysis must use cascade-vs-trap framing and split borrower / Credit Account operator, pool LP / lender, liquidator, and curator/operator (`oracle-analysis/runbook.md:172-203`).
- Gearbox protocol-fit memos must include LT and max leverage, main and reserve feeds, safe-pricing exit Health Factor implication, staleness and bounds, and delayed-withdrawal or issuer-controlled branch interaction (`oracle-analysis/runbook.md:205-235`).
- Final verification must check required files, graph leaf audits, node classification, formula presence, staleness/bounds/timestamps, protocol-fit linkage to LT/liquidation/safe-pricing, non-top-level conclusions, side-specific conclusions, and Gearbox parsing reference use (`oracle-analysis/runbook.md:242-265`).

## Known-good run invariants

The known-good run demonstrates the shape the harness should accept:

- The parent root exists and has `README.md`, `index.md`, `agentic-flow/analyze-and-propose.md`, `asset-investment-diligence/`, and `oracle-analysis/`.
- The parent index maps all three outputs: asset diligence, oracle analysis, and agentic stage handoff (`/Users/ilya/ai-assistant/projects/front-knowledge-base/dev/implementation/sample-base-token-sample-vault-token-agentic-analyze-propose-2026-06-05/index.md:3-8`).
- The agentic handoff explicitly maps Discover, Analyze, Propose, Preview, Execute, and Monitor. Propose is `request_more_inputs`; Preview and Execute are blocked (`/Users/ilya/ai-assistant/projects/front-knowledge-base/dev/implementation/sample-base-token-sample-vault-token-agentic-analyze-propose-2026-06-05/agentic-flow/analyze-and-propose.md:32-59`).
- Both final verification files record deterministic validation commands and outcomes (`.../asset-investment-diligence/verification/final-investment-analysis-verification.md:28-33`, `.../oracle-analysis/verification/final-oracle-analysis-verification.md:29-34`).

The harness should treat this as the positive fixture, with one caveat: the validation commands are summarized as `python3 <inline run artifact validator>`, so a stricter future harness should prefer a checked-in validator path or a saved script hash.

## External bad/partial run failure classes

### 1. Missing files

Asset run file presence is mostly complete: a local probe found required root files and required per-token files present under `dev/implementation/asset-diligence-2026-06-05-sample-base-token-sample-vault-token`.

Oracle run has a run-level missing file:

- Manifest declares `final_verification`: `verification/final-oracle-analysis-verification.md` (`dev/implementation/oracle-analysis-2026-06-05-sample-base-token-sample-vault-token/run-manifest.json:33-34`).
- Index advertises the same final verification path in the artifact map (`dev/implementation/oracle-analysis-2026-06-05-sample-base-token-sample-vault-token/index.md:39-45`).
- The file does not exist at `dev/implementation/oracle-analysis-2026-06-05-sample-base-token-sample-vault-token/verification/final-oracle-analysis-verification.md`.

Machine-check rule: every path declared in `run-manifest.json.final_verification` and every run-level artifact-map path must resolve relative to the run root.

### 2. Missing fields

Asset S6 reports discuss broad return topics but omit most exact required quantitative fields. A local term probe over:

- `dev/implementation/asset-diligence-2026-06-05-sample-base-token-sample-vault-token/investment-analysis/investment-analyst-report-points-pt-risk-return.md`
- `dev/implementation/asset-diligence-2026-06-05-sample-base-token-sample-vault-token/investment-analysis/quantitative-underwriting-methodology.md`
- `dev/implementation/asset-diligence-2026-06-05-sample-base-token-sample-vault-token/investment-analysis/index.md`

found these required labels missing:

- `Gross ROI`
- `Simple annualized return`
- `Compound annualized return`
- `Points ROI`
- `Points annualized return`
- `Expected loss`
- `Risk-adjusted ROI`
- `Risk-adjusted annualized return`
- `Break-even points ROI`
- `Break-even terminal drawdown`
- `Price-stability certainty score`

The report contains headings such as `Gross return stack`, `Risk-adjusted return stack`, `Points valuation`, and `Price-stability certainty` (`.../investment-analyst-report-points-pt-risk-return.md:20-55`), but those headings do not satisfy exact required calculation fields from `stage-contracts.md:272-287`. Unknown or inapplicable calculations should be present as machine-readable `null`, `not_in_scope`, or `skipped_due_to_missing_input` entries with reasons.

Oracle per-scope files also lack machine-checkable conclusion labels even when a side-specific matrix exists. A local term probe over both token protocol-fit/stress/verification files found missing labels for:

- `position side`
- `token role`
- `stress direction`
- `loss bearer`
- `liquidity-cascade`
- `liquidity-trap`
- `delayed withdrawal`
- `forbidden token`

The index has a side-specific verdict matrix (`dev/implementation/oracle-analysis-2026-06-05-sample-base-token-sample-vault-token/index.md:24-30`), but the required conclusion fields need explicit structured rows or field labels per side so a validator can distinguish borrower-friendly, LP-risky, liquidator-risky, and curator/operator-risky conclusions.

### 3. Broken path reference

The asset root README uses a sibling oracle path from the run root, which resolves correctly:

- `dev/implementation/asset-diligence-2026-06-05-sample-base-token-sample-vault-token/README.md:17-19` references `../oracle-analysis-2026-06-05-sample-base-token-sample-vault-token/`.

A nested investment-analysis file repeats the same relative path from a deeper directory, where it resolves incorrectly:

- `dev/implementation/asset-diligence-2026-06-05-sample-base-token-sample-vault-token/investment-analysis/investment-analyst-report-points-pt-risk-return.md:85-89` references `../oracle-analysis-2026-06-05-sample-base-token-sample-vault-token/`.
- From `investment-analysis/`, that resolves to `dev/implementation/asset-diligence-2026-06-05-sample-base-token-sample-vault-token/oracle-analysis-2026-06-05-sample-base-token-sample-vault-token`, which does not exist.
- The correct relative path from that file is `../../oracle-analysis-2026-06-05-sample-base-token-sample-vault-token/`, or the artifact should use a run-root-relative path.

Machine-check rule: validate code-spanned path references as well as Markdown links when they look like local artifact paths.

### 4. Validation overclaim

Asset final verification marks broad content checks as `pass`:

- `Gross return stack present | pass` (`dev/implementation/asset-diligence-2026-06-05-sample-base-token-sample-vault-token/verification/final-investment-analysis-verification.md:21-24`).
- `Points valuation present | pass` and `Price-stability certainty present | pass` (`.../verification/final-investment-analysis-verification.md:25-26`).
- `Sensitivity map present | pass` (`.../verification/final-investment-analysis-verification.md:28`).

Those checks overclaim compliance because exact required S6 fields are absent. A validator must check field-level presence, not just heading-level presence.

Oracle per-scope verification also overclaims relative to the run contract:

- Per-scope verification says `Stress analysis side split present | pass` and `Protocol-fit memo names LT and max leverage | pass` (`dev/implementation/oracle-analysis-2026-06-05-sample-base-token-sample-vault-token/tokens/ethereum-sample-vault-token-22222222/verification/oracle-analysis-verification.md:10-12`).
- The run-level final verification file declared by manifest does not exist.
- Required explicit conclusion fields (`position_side`, `token_role`, `stress_direction`, `loss_bearer`) are absent as machine-checkable labels.

Machine-check rule: any `pass` row must point to concrete field labels or a saved validator result. A run-level `PASS` or `review_required` validation status cannot be accepted if the run-level final verification file is missing.

### 5. Missing Propose handoff

The external run artifacts are separate Analyze roots. They do not include an agentic parent folder or `agentic-flow/analyze-and-propose.md`:

- `dev/implementation/asset-diligence-2026-06-05-sample-base-token-sample-vault-token/agentic-flow/analyze-and-propose.md` is absent.
- `dev/implementation/oracle-analysis-2026-06-05-sample-base-token-sample-vault-token/agentic-flow/analyze-and-propose.md` is absent.

The known-good run includes the missing flow handoff and explicitly blocks Preview/Execute (`/Users/ilya/ai-assistant/projects/front-knowledge-base/dev/implementation/sample-base-token-sample-vault-token-agentic-analyze-propose-2026-06-05/agentic-flow/analyze-and-propose.md:52-59`).

Machine-check rule: when a run claims to simulate or complete an agentic `Analyze → Propose` loop, require a parent artifact with `agentic-flow/analyze-and-propose.md` and explicit statuses for Discover, Analyze, Propose, Preview, Execute, and Monitor.

## Proposed machine-checkable fields

### Manifest schema fields

Common manifest fields:

```json
{
  "workflow_id": "asset-investment-diligence-v1 | oracle-analysis-v1",
  "run_id": "string",
  "run_artifact_root": "dev/implementation/<run-slug>",
  "final_index": "index.md",
  "final_verification": "verification/<file>.md",
  "status": "pass | review_required | blocked",
  "declared_paths": [],
  "cross_run_links": []
}
```

Asset-specific manifest entries:

```json
{
  "tokens": [
    {
      "token_slug": "string",
      "chain": "string",
      "symbol": "string",
      "address": "0x...",
      "artifact_dir": "tokens/<token-slug>",
      "status": "pass | review_required | blocked"
    }
  ],
  "pt_markets": [],
  "x_research_scopes": []
}
```

Oracle-specific manifest entries:

```json
{
  "scopes": [
    {
      "scope_id": "string",
      "scope_slug": "string",
      "scope_type": "token | pt_market",
      "chain": "string",
      "asset_symbol": "string",
      "asset_address": "0x...",
      "protocol": "Gearbox",
      "position_sides": ["credit_account_borrower", "pool_lp", "liquidator", "curator_operator"],
      "token_roles": ["collateral"],
      "artifact_dir": "tokens/<scope-slug>",
      "status": "pass | review_required | blocked"
    }
  ]
}
```

### Stage envelope fields

Every stage output should expose a small parseable envelope, either as JSON frontmatter or a fenced `json` block:

```json
{
  "stage_id": "string",
  "scope_id": "string",
  "status": "pass | review_required | blocked | skipped",
  "artifact_paths": ["relative/path.md"],
  "blocking_unknowns": [],
  "validation": {
    "result": "pass | fail",
    "checks": [
      {"id": "required_files_exist", "result": "pass", "evidence": "path"}
    ]
  }
}
```

Skipped stages should use `status: "skipped"`, `reason`, and `not_in_scope_fields`, rather than deleting files or fields.

### Asset S6 quantitative fields

Use exact keys in `investment-analysis/index.md` or a companion `investment-analysis/underwriting-fields.json`:

```json
{
  "gross_roi": null,
  "simple_annualized_return": null,
  "compound_annualized_return": null,
  "points_ev": 0,
  "points_roi": null,
  "points_annualized_return": null,
  "expected_loss": null,
  "exit_cost": null,
  "risk_adjusted_roi": null,
  "risk_adjusted_annualized_return": null,
  "break_even_points_roi": null,
  "break_even_terminal_drawdown": null,
  "price_stability_certainty_score": null,
  "null_reason": "position size / PT scope / live route not supplied"
}
```

### Oracle protocol-fit fields

Use exact fields per side in `oracle/protocol-fit-memo.md` or `oracle/protocol-fit-fields.json`:

```json
{
  "position_side": "credit_account_borrower | pool_lp | liquidator | curator_operator",
  "token_role": "collateral | borrowed_token | quoted_token | vault_share | lp_token | pt | transition_stage_asset",
  "stress_direction": "temporary_market_discount | persistent_redemption_impairment | upward_depeg | stale_feed",
  "loss_bearer": "borrower | pool_lp | liquidator | curator_operator | unknown",
  "oracle_type_by_node": [],
  "main_feed": null,
  "reserve_feed": null,
  "safe_pricing_rule": null,
  "exit_hf_implication": null,
  "lt": null,
  "lt_ramp": null,
  "max_leverage_implied_by_lt": null,
  "staleness_and_bounds": null,
  "feed_swap_reserve_timelock_status": null,
  "delayed_withdrawal_interaction": null,
  "forbidden_token_interaction": null,
  "issuer_controlled_branch_interaction": null,
  "cascade_vs_trap": "liquidation_cascade | liquidity_trap | hybrid | unknown",
  "conclusion_status": "pass | review_required | blocked"
}
```

### Final verification fields

Run-level final verification should expose machine-checkable command evidence:

```json
{
  "final_verification_status": "pass | review_required | blocked | fail",
  "required_files_exist": true,
  "declared_paths_resolve": true,
  "required_fields_present": true,
  "cross_links_resolve": true,
  "unsupported_execution_recommendation_absent": true,
  "commands_run": [
    {
      "cwd": "/absolute/path",
      "command": "git diff --check -- dev/implementation/<run-slug>",
      "exit_code": 0,
      "stdout_marker": "PASS"
    }
  ]
}
```

## Proposed fixtures

Positive fixture:

- `good-agentic-sample-assets`: copy of `/Users/ilya/ai-assistant/projects/front-knowledge-base/dev/implementation/sample-base-token-sample-vault-token-agentic-analyze-propose-2026-06-05`.
- Expected: passes file layout, manifest parse, path resolution, final verification presence, command-evidence presence, and agentic Propose handoff checks.

Negative fixtures:

- `missing-final-oracle-verification`: copy of `dev/implementation/oracle-analysis-2026-06-05-sample-base-token-sample-vault-token` where manifest/index declare `verification/final-oracle-analysis-verification.md` but the file is absent.
- `asset-heading-overclaim`: copy of `dev/implementation/asset-diligence-2026-06-05-sample-base-token-sample-vault-token` where final verification passes broad headings but exact S6 fields are missing.
- `nested-sibling-path-broken`: file-level fixture from `investment-analysis/investment-analyst-report-points-pt-risk-return.md` with `../oracle-analysis-2026-06-05-sample-base-token-sample-vault-token/` from a nested directory.
- `oracle-side-labels-missing`: copy of the external oracle run where verdict prose exists but `position_side`, `token_role`, `stress_direction`, and `loss_bearer` labels are absent.
- `missing-propose-handoff`: separate Analyze roots with no parent `agentic-flow/analyze-and-propose.md`.
- `validation-overclaim-with-missing-declared-path`: any run where final verification or per-scope verification contains `pass` rows while a declared path does not resolve.

## Prioritized validator checklist

P0 — structural blockers:

1. Parse `run-manifest.json`; fail on invalid JSON.
2. Resolve `run_artifact_root`, `final_index`, `final_verification`, token/scope `artifact_dir`, and every declared artifact path relative to the run root.
3. Fail if any required root file is missing.
4. Fail if any required per-token/per-scope file or directory is missing.
5. Fail if a run-level final verification file is declared but absent.
6. Fail if local Markdown links or code-spanned artifact paths do not resolve.
7. Fail if a claimed agentic Analyze→Propose run lacks `agentic-flow/analyze-and-propose.md` and explicit stage statuses through Preview/Execute.

P1 — field-level compliance:

1. Check exact asset S6 quantitative fields; allow `null`, `not_in_scope`, or `skipped_due_to_missing_input` only with a reason.
2. Check exact oracle side fields: `position_side`, `token_role`, `stress_direction`, `loss_bearer`, and `cascade_vs_trap` per relevant side.
3. Check Gearbox oracle fields: main/reserve feed, safe-pricing rule, exit HF implication, LT, LT ramp, max leverage, staleness/bounds, timelock/feed swap status, delayed-withdrawal branch, forbidden-token branch, and issuer-controlled branch.
4. Check final verification rows against field-level evidence, not just section headings.
5. Check skipped PT/social stages have explicit skipped markers and index files when no scopes were supplied.

P2 — quality and harness hardening:

1. Require final verification command evidence with cwd, command, exit code, and output marker.
2. Require saved validator script path or script hash instead of only `python3 <inline run artifact validator>`.
3. Require no unsupported Preview/Execute recommendation when unresolved support, eligibility, route, feed, or policy gates remain.
4. Produce a compact machine-readable failure report with `severity`, `check_id`, `path`, `field`, `expected`, `actual`, and `fix_hint`.
5. Keep raw source evidence out of the validator report; store only path references and concise failure messages.

## Evidence commands run during this audit

- `git status --short` from `/Users/ilya/Documents/Codex/front-knowledge-base` to check the pre-existing working tree state.
- `search_files` over both workflow contract directories and `dev/implementation/` to enumerate contract and run artifact files.
- `read_file` on the workflow contracts, external run manifests/indexes/final verifications, and known-good agentic handoff/final verification files.
- Inline Python probe from `/Users/ilya/Documents/Codex/front-knowledge-base` to check required file existence, manifest fields, missing field labels, sibling path resolution, and missing agentic handoff presence.
