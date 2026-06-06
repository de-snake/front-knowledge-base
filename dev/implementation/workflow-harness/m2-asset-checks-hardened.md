# M2 hardened execution brief — asset-investment-diligence harness checks

Purpose: final implementation brief for the M2 `asset-investment-diligence` workflow harness slice after formal review. This brief is limited to formal workflow compliance. It does not assess token economic quality, oracle correctness, allocation suitability, or whether a specific report conclusion is persuasive.

This file is the only mutation for the hardening task. The future implementation slice must stay inside the edit boundary below.

## Inputs reviewed

- `CLAUDE.md`.
- `dev/implementation/workflow-harness/m2-asset-checks-plan.md`.
- `dev/implementation/workflow-harness/m2-asset-checks-review.md`.
- `dev/implementation/workflow-harness/m1-validator-core-plan.md`.
- `dev/implementation/workflow-harness/hardened-plan.md`.
- `dev/implementation/workflow-harness/internal-audit.md`.
- `dev/implementation/workflow-harness/plan-review.md`.
- `user/references/workflows/asset-investment-diligence/output-structure.md`.
- `user/references/workflows/asset-investment-diligence/stage-contracts.md`.
- `user/references/workflows/asset-investment-diligence/runbook.md`.
- Gearbox front-knowledge-base runtime workflow placement and formal workflow critic references.

## Review blockers incorporated

The future implementation must close every blocker from `m2-asset-checks-review.md`:

1. Align the M2 CLI report, finding fields, severities, status, and exit-code behavior with the M1 validator-core contract.
2. Add one deterministic positive acceptance case so an always-failing validator, or a validator that still emits `validator.workflow_checks_deferred`, cannot pass M2.
3. State exactly when `validator.workflow_checks_deferred` is removed or scoped away for `asset-investment-diligence`.
4. Add deterministic S7 coverage for cross-link resolution, workspace-validation evidence, and `README.md` / `index.md` content contracts.
5. Require `Compound annualized return` as a deterministic S6 field with either a numeric value or an allowed non-numeric value state plus reason.
6. State that M2 intentionally includes asset Markdown/content checks even though the original hardened-plan milestone split described those as a later generic Markdown contract slice.

## Slice goal

Add deterministic `asset-investment-diligence` validation to `dev/tools/validate_workflow_run.py` so the harness can reject formally incomplete asset diligence runs without judging the economic correctness of the diligence.

The validator must cover these formal contract classes:

1. Manifest schema and manifest-to-token scope reconciliation.
2. Run-root path containment and declared path safety.
3. Required root files and per-token file sets.
4. S1 required fact-slot presence with explicit unknown/blocker handling.
5. S2 analyst-report section coverage.
6. Explicit skipped-stage markers for absent PT and social scopes.
7. S6 exact quantitative fields with value-state and reason checks.
8. S7 final-verification credibility, cross-link resolution, workspace-validation evidence, and top-level `README.md` / `index.md` handoff sections.
9. No unsupported execution-ready or allocation-ready claim when unresolved live inputs, issuer eligibility, feed support, route support, or user-policy blockers remain.

This M2 slice intentionally reslices part of the earlier generic Markdown-contract plan into the asset-specific milestone. The asset validator cannot honestly return a production `pass` unless the asset run's own S1, S2, S6, and S7 content contracts are checked.

## Exact files to edit in the future implementation slice

Required code edit:

- `dev/tools/validate_workflow_run.py`

Required fixture edits for acceptance coverage:

- `dev/implementation/workflow-harness/fixtures/asset-bad-manifest-entry-drift/**`
- `dev/implementation/workflow-harness/fixtures/asset-bad-missing-token-file/**`
- `dev/implementation/workflow-harness/fixtures/asset-bad-missing-final-verification/**`
- `dev/implementation/workflow-harness/fixtures/asset-bad-missing-s1-slot/**`
- `dev/implementation/workflow-harness/fixtures/asset-bad-missing-s2-section/**`
- `dev/implementation/workflow-harness/fixtures/asset-bad-missing-skipped-pt-social-markers/**`
- `dev/implementation/workflow-harness/fixtures/asset-bad-missing-s6-calculation-fields/**`
- `dev/implementation/workflow-harness/fixtures/asset-bad-s6-heading-only-overclaim/**`
- `dev/implementation/workflow-harness/fixtures/asset-bad-final-verification-overclaim/**`
- `dev/implementation/workflow-harness/fixtures/asset-bad-missing-s7-crosslink-workspace-readme-index/**`

The positive fixture is generated inside the exact acceptance command below. It does not need to be committed as a permanent fixture unless the implementer prefers to keep a small stable copy.

Do not edit workflow source contracts, prompt files, `CLAUDE.md`, existing historical run artifacts, README/navigation files outside fixture directories, oracle-analysis checks, combined Analyze→Propose checks, or token diligence semantics in this slice.

## Validator behavior

### CLI scope

The M2 code path must run when the validator is called with:

```bash
python3 dev/tools/validate_workflow_run.py \
  --workflow asset-investment-diligence \
  --run-root <run-root> \
  --format json
```

The CLI may accept `asset-investment-diligence` as an alias, but the JSON report must normalize `workflow` to `asset-investment-diligence-v1`.

### M1 report contract

M2 must preserve the M1 report schema. Do not introduce a second asset-only report dialect.

Required report fields:

```json
{
  "schema_version": "workflow-harness-report-v1",
  "generated_at": "2026-06-05T00:00:00Z",
  "workflow": "asset-investment-diligence-v1",
  "run_root": "dev/implementation/<run-slug>",
  "status": "pass | review_required | fail",
  "exit_code": 0,
  "summary": {
    "P0": 0,
    "P1": 0,
    "P2": 0,
    "checks_passed": 0,
    "checks_failed": 0,
    "checks_skipped": 0,
    "files_checked": 0,
    "json_files_parsed": 0,
    "links_checked": 0,
    "declared_paths_checked": 0
  },
  "inputs": {
    "manifest": "run-manifest.json",
    "final_index": "index.md",
    "final_verification": "verification/final-investment-analysis-verification.md",
    "parent_return": null
  },
  "findings": [],
  "checks": [],
  "generated_files": [],
  "rendered_outputs": {}
}
```

Finding shape must use `id`, not `check_id`:

```json
{
  "id": "asset.s6.required_field_present",
  "severity": "P1",
  "workflow": "asset-investment-diligence-v1",
  "path": "investment-analysis/investment-analyst-report-points-pt-risk-return.md",
  "field": "risk_adjusted_roi",
  "expected": "explicit field with value state",
  "actual": "missing",
  "message": "Required S6 field is absent.",
  "fix_hint": "Add a labeled row or field for risk-adjusted ROI with a numeric value, or an allowed non-numeric state plus reason."
}
```

Check-result shape must use `id`, `severity`, and `result`:

```json
{
  "id": "asset.manifest.json_parse",
  "severity": "P0",
  "result": "pass | fail | skipped",
  "path": "run-manifest.json",
  "message": "run-manifest.json parsed successfully"
}
```

Do not emit `status: warning`, severities `blocker | error | warning`, or `finding.check_id` in M2.

### Severity and exit-code policy

Preserve the M1 status policy:

- `P0`: structural failure. Report `status="fail"`; exit `2`.
- `P1`: contract failure or false-pass risk. Report `status="review_required"` when no P0 exists; exit `1`.
- `P2`: hardening warning. Report can stay `status="pass"`; exit `0` unless `--strict-warnings` is set, then exit `1`.

M2 severity mapping:

| Class | Severity | Exit effect |
| --- | --- | --- |
| Malformed JSON, missing run root, missing manifest, unsafe path, parent-escaping path, absolute declared path, missing declared required file, missing declared artifact directory, manifest token identity/path drift | `P0` | exit `2` |
| Missing S1 fact slot, unnamed unknown, missing S2 section, missing skipped-stage marker, missing S6 exact field, non-numeric S6 field without reason, heading-only false pass, final-verification overclaim, unsupported execution-ready claim, missing S7 cross-link/workspace-validation/README/index evidence | `P1` | exit `1` |
| Full PT/social validation explicitly out of scope while scopes are non-empty and no pass is claimed | `P2` | exit `0` unless strict warnings |

If the implementation chooses to treat a specific content omission as P0, it must update the fixture expected exit code and justify why the omission makes the run structurally unreadable rather than review-required. Do not silently change all content-contract findings to P0.

### Deferred-check clearing

M1 emits `validator.workflow_checks_deferred` for otherwise valid runs. M2 must remove or scope away this finding for `asset-investment-diligence-v1` only after all M2 asset checks listed in this brief are implemented and covered by acceptance.

Required behavior after M2:

- For `--workflow asset-investment-diligence`, a good asset run with all required M2 checks satisfied exits `0`, reports `status="pass"`, and has no `validator.workflow_checks_deferred` finding.
- For workflows not completed by the current milestone, `validator.workflow_checks_deferred` may remain until their own check catalog is implemented.
- If M2 leaves `validator.workflow_checks_deferred` active for `asset-investment-diligence`, M2 is not complete even if all negative cases fail as expected.

## Required checks

### 1. `asset.manifest_schema`

Parse `<run-root>/run-manifest.json` and require:

- `workflow_id` equals `asset-investment-diligence-v1`.
- `run_id` is a non-empty string.
- `run_artifact_root` is present and normalizes to the supplied `--run-root` when both are resolved from the vault root.
- `tokens` is a non-empty list for M2.
- `pt_markets` is a list and may be empty.
- `x_research_scopes` is a list and may be empty.
- `final_index` equals `index.md` after normalization and resolves under the run root.
- `final_verification` equals `verification/final-investment-analysis-verification.md` after normalization and resolves under the run root.

Each `tokens[]` entry must include:

- `token_slug`.
- `chain`.
- `symbol`.
- `address` as a `0x` EVM address.
- `artifact_dir` exactly `tokens/<token_slug>`.
- `status` with value `pass`, `review_required`, or `blocked`.

Path rules:

- Every declared artifact path must stay inside the supplied `--run-root`.
- Reject absolute paths, `..` escapes, sibling-run paths, and symlinks that resolve outside the run root.
- Do not silently normalize unsafe paths into a passing state.

Required check IDs:

- `asset.manifest.json_parse`
- `asset.manifest.required_field`
- `asset.manifest.workflow_id`
- `asset.manifest.run_root_reconciles`
- `asset.manifest.final_index_canonical`
- `asset.manifest.final_verification_canonical`
- `asset.manifest.token_entry_schema`
- `asset.manifest.path_inside_run_root`

### 2. `asset.manifest_entry_reconciles_scope`

For each manifest token entry:

- `tokens[].artifact_dir` must resolve to an existing directory under `--run-root`.
- The folder basename must equal `tokens[].token_slug`.
- `<artifact_dir>/scope.json` must exist and parse as JSON.
- `scope.json` must reconcile with the manifest token entry:
  - `symbol` equals `scope.json.symbol`.
  - manifest `address` equals `scope.json.token_address` or `scope.json.address`, case-insensitive.
  - manifest `chain` equals `scope.json.chain` or `scope.json.chain_name` when either field is present.
  - if `scope.json.scope_slug` is present, it equals `token_slug`.

Required check IDs:

- `asset.manifest.artifact_dir_reconciles`
- `asset.scope.json_parse`
- `asset.scope.identity_reconciles`

### 3. `asset.required_files_present`

Required run-root files:

- `README.md`
- `run-manifest.json`
- `index.md`
- `pt-markets/index.md` when `pt_markets` is empty, or one per-PT folder plus run-level index when non-empty.
- `x-research/index.md` when `x_research_scopes` is empty, or one social report plus run-level index when non-empty.
- `investment-analysis/quantitative-underwriting-methodology.md`
- `investment-analysis/investment-analyst-report-points-pt-risk-return.md`
- `investment-analysis/index.md`
- `verification/final-investment-analysis-verification.md`

Required per-token files under every `tokens[].artifact_dir`:

- `scope.json`
- `research/onchain-admin.md`
- `research/issuer-backing-security.md`
- `research/transfer-liquidity-oracle-governance.md`
- `technical-report.md`
- `analyst-report.md`
- `verification.md`

Required check IDs:

- `asset.root.required_file_exists`
- `asset.token.required_file_exists`
- `asset.token.required_research_file_exists`

### 4. `asset.s1_required_fact_slots`

Check S1 at the per-token level. The validator should scan `scope.json`, the three `research/*.md` files, and `technical-report.md` as a combined S1 evidence surface.

Do not judge whether the facts are economically correct. Only check that each required fact slot is present with either a non-empty value or an explicit state: `unknown`, `not_found`, `not_in_scope`, or `blocked`.

Required S1 fact slots:

- Token identity.
- Decimals.
- Implementation/proxy status.
- Issuer/protocol entity.
- Backing/NAV model.
- Transfer restrictions.
- Mint/redeem access.
- Freeze, blacklist, pause, forced-transfer, or admin-control surface.
- Liquidity venues and current depth.
- Oracle/accounting method.
- Audits/incidents.
- Missing fields and decision effect.

Rules:

- Accept exact heading text, normalized label text, Markdown table rows, JSON/frontmatter fields, or colon labels.
- A broad heading such as `Risk overview` is insufficient unless the required slot label appears under it.
- A token may be `review_required` with unknown fields, but the unknowns must be named and tied to a decision effect.

Required check IDs:

- `asset.s1.required_fact_slot_present`
- `asset.s1.unknown_has_decision_effect`

### 5. `asset.s2_required_report_sections`

Check each token `analyst-report.md` for the required S2 report sections from `stage-contracts.md`:

- `Executive view`
- `What the token represents`
- `Main risk implications`
- `Backing and NAV quality`
- `Liquidity and exit risk`
- `Controls, governance, and legal restrictions`
- `Pricing/oracle risk in plain language`
- `What must be checked before live use`
- `Evidence quality`
- `Source map`
- `Technical appendix pointer`

Rules:

- Normalize heading case, punctuation, and `and` / `&` variants.
- Do not accept a source-map mention inside prose as the `Source map` section; require a heading or explicit labeled block.
- Do not require token comparison sections. Cross-token ranking belongs to S6, not S2.

Required check IDs:

- `asset.s2.required_section_present`
- `asset.s2.source_map_present`
- `asset.s2.technical_appendix_pointer_present`

### 6. `asset.skipped_pt_social_markers`

M2 does not implement full PT-market or X/social validation. It must prevent silent omission when those stages are out of scope.

If `pt_markets` is empty:

- Require `pt-markets/index.md`.
- Require an explicit skipped marker for `S3_pt_market_economics` in `run-manifest.json.skipped_stages` or `pt-markets/index.md`.
- The marker must include a reason, for example `No PT market was supplied in this run scope.`

If `x_research_scopes` is empty:

- Require `x-research/index.md`.
- Require explicit skipped markers for `S4_x_social_mining` and `S5_x_social_synthesis` in `run-manifest.json.skipped_stages` or `x-research/index.md`.
- Each marker must include a reason.

If `pt_markets` or `x_research_scopes` is non-empty:

- M2 may emit `asset.pt_social.full_validation_out_of_scope` as P2 when it clearly states full validation is deferred.
- Escalate to P1 if the run, index, or final verification claims PT/social validation passed without actual validation.

Required check IDs:

- `asset.skipped_pt.index_exists`
- `asset.skipped_pt.marker_present`
- `asset.skipped_pt.reason_present`
- `asset.skipped_social.index_exists`
- `asset.skipped_social.marker_present`
- `asset.skipped_social.reason_present`
- `asset.pt_social.full_validation_out_of_scope`

### 7. `asset.s6_required_quantitative_fields`

Check S6 across these files:

- `investment-analysis/quantitative-underwriting-methodology.md`
- `investment-analysis/investment-analyst-report-points-pt-risk-return.md`
- `investment-analysis/index.md`

Required S6 fields:

- `Gross ROI` / `gross_roi`
- `Simple annualized return` / `simple_annualized_return`
- `Compound annualized return` / `compound_annualized_return`
- `Points EV` / `points_ev`
- `Points ROI` / `points_roi`
- `Points annualized return` / `points_annualized_return`
- `Expected loss` / `expected_loss`
- `Exit cost` / `exit_cost`
- `Risk-adjusted ROI` / `risk_adjusted_roi`
- `Risk-adjusted annualized return` / `risk_adjusted_annualized_return`
- `Break-even points ROI` / `break_even_points_roi`
- `Break-even terminal drawdown` / `break_even_terminal_drawdown`
- `Price-stability certainty score` / `price_stability_certainty_score`

Deterministic relevance rule:

- `Compound annualized return` is always required.
- If compounding is not relevant, the field must still appear with `not_in_scope`, `skipped_due_to_missing_input`, `unknown`, or `blocked` plus a reason.

No false-pass rule:

- A heading such as `Gross return stack`, `Risk-adjusted return stack`, `Points valuation`, or `Price-stability certainty` does not satisfy the exact field requirement by itself.
- Each field must have a machine-readable or explicitly labeled value state: numeric value, `null`, `not_in_scope`, `skipped_due_to_missing_input`, `unknown`, or `blocked`.
- If the value state is not numeric, the same row, object, or labeled block must include a reason.
- If the final verification says a broad calculation group passed while exact fields are absent, emit a final-verification overclaim finding.

Required check IDs:

- `asset.s6.required_field_present`
- `asset.s6.required_field_has_value_state`
- `asset.s6.non_numeric_value_has_reason`
- `asset.s6.heading_only_false_pass`

### 8. `asset.s7_final_verification_credibility`

Validate the canonical file:

```text
<run-root>/verification/final-investment-analysis-verification.md
```

The final verification must contain direct evidence that S7 checked:

- Required root files.
- Required per-token and per-PT folder structure.
- Manifest paths and declared artifact paths.
- Cross-link resolution for local Markdown links and Obsidian links under the run root.
- Required S1, S2, and S6 sections/fields.
- Skipped-stage checks when PT/social scopes are absent.
- No source artifact gives unsupported allocation conclusions.
- Workspace validation commands passed or unrelated failures were isolated with command text and exit status.
- `README.md` handoff sections.
- `index.md` artifact map and final verification status.

Required status and claim rules:

- The final verification file must contain a status marker: `pass`, `review_required`, `blocked`, or `fail`.
- It must record command evidence with command text and exit status, or an explicit `PASS` / `FAIL` marker tied to a command.
- It must not claim `pass` for required content checks when the validator detects absent required fields.
- It must not claim the run is execution-ready or allocation-ready if unresolved live inputs, issuer eligibility, feed support, route support, user-policy blockers, or other live-use blockers are named elsewhere in the run.

Required check IDs:

- `asset.final_verification.file_exists`
- `asset.final_verification.status_present`
- `asset.final_verification.required_file_checks_present`
- `asset.final_verification.required_field_checks_present`
- `asset.final_verification.skipped_stage_checks_present`
- `asset.final_verification.cross_links_checked`
- `asset.final_verification.workspace_validation_present`
- `asset.final_verification.overclaim`
- `asset.final_verification.no_unsupported_execution_ready_claim`

### 9. `asset.top_level_handoff_sections`

Validate the run-level handoff files from `output-structure.md`.

`README.md` must state:

- what was analyzed;
- where the manifest is;
- where each token / PT folder is;
- which files to read first;
- final validation status.

`index.md` must state:

- tokens analyzed;
- PT markets analyzed, or explicit none/skipped marker;
- headline risk / return findings;
- missing data and blockers;
- artifact map;
- final verification status.

Rules:

- A heading without concrete body content is insufficient.
- A generic project README is insufficient.
- If the final validation status in `README.md`, `index.md`, manifest status fields, and final verification contradict each other, emit a P1 finding unless a named item is explicitly out of final-validation scope.

Required check IDs:

- `asset.readme_handoff_sections`
- `asset.index_contract_sections`
- `asset.run_status_reconciles`

## Minimal fixture matrix

Use small synthetic fixture folders instead of copying large real runs. Each fixture should contain only the files needed to exercise the check path.

| Fixture | Expected exit | Required finding ID(s) |
| --- | ---: | --- |
| Generated temporary good run | `0` | none; also no `validator.workflow_checks_deferred` |
| `asset-bad-manifest-entry-drift` | `2` | `asset.manifest.artifact_dir_reconciles` or `asset.scope.identity_reconciles` |
| `asset-bad-missing-token-file` | `2` | `asset.token.required_file_exists` or `asset.token.required_research_file_exists` |
| `asset-bad-missing-final-verification` | `2` | `asset.final_verification.file_exists` or `asset.root.required_file_exists` |
| `asset-bad-missing-s1-slot` | `1` | `asset.s1.required_fact_slot_present` |
| `asset-bad-missing-s2-section` | `1` | `asset.s2.required_section_present` |
| `asset-bad-missing-skipped-pt-social-markers` | `1` | `asset.skipped_pt.marker_present` or `asset.skipped_social.marker_present` |
| `asset-bad-missing-s6-calculation-fields` | `1` | `asset.s6.required_field_present` |
| `asset-bad-s6-heading-only-overclaim` | `1` | `asset.s6.heading_only_false_pass` or `asset.final_verification.overclaim` |
| `asset-bad-final-verification-overclaim` | `1` | `asset.final_verification.overclaim` |
| `asset-bad-missing-s7-crosslink-workspace-readme-index` | `1` | `asset.final_verification.cross_links_checked`, `asset.final_verification.workspace_validation_present`, `asset.readme_handoff_sections`, or `asset.index_contract_sections` |

Do not claim manifest drift, missing-token-file, missing-final-verification, S1, S2, skipped-stage, S6, or S7 coverage without one of these fixtures or an equivalent inline temporary-fixture assertion in the implementation handoff.

## Exact acceptance command for the implementation slice

Run from `/Users/ilya/Documents/Codex/front-knowledge-base` after implementing M2:

```bash
python3 -m py_compile dev/tools/validate_workflow_run.py
python3 - <<'PY'
import json
import shutil
import subprocess
import textwrap
from pathlib import Path

BASE = Path("dev/implementation/workflow-harness/fixtures")
TMP_GOOD = Path("dev/implementation/workflow-harness/tmp-asset-good-minimal")
VALIDATOR = [
    "python3",
    "dev/tools/validate_workflow_run.py",
    "--workflow",
    "asset-investment-diligence",
    "--format",
    "json",
]

TOKEN_SLUG = "ethereum-good-11111111"
TOKEN_ADDRESS = "0x1111111111111111111111111111111111111111"
TOKEN_DIR = f"tokens/{TOKEN_SLUG}"


def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).strip() + "\n")


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def build_good_fixture(root: Path):
    shutil.rmtree(root, ignore_errors=True)
    token = root / TOKEN_DIR
    write_json(
        root / "run-manifest.json",
        {
            "workflow_id": "asset-investment-diligence-v1",
            "run_id": "asset-good-minimal",
            "run_artifact_root": str(root),
            "tokens": [
                {
                    "token_slug": TOKEN_SLUG,
                    "chain": "Ethereum mainnet",
                    "symbol": "GOOD",
                    "address": TOKEN_ADDRESS,
                    "artifact_dir": TOKEN_DIR,
                    "status": "pass",
                }
            ],
            "pt_markets": [],
            "x_research_scopes": [],
            "skipped_stages": [
                {"stage_id": "S3_pt_market_economics", "reason": "No PT market was supplied in this run scope."},
                {"stage_id": "S4_x_social_mining", "reason": "No X/social scope was supplied in this run scope."},
                {"stage_id": "S5_x_social_synthesis", "reason": "No X/social scope was supplied in this run scope."},
            ],
            "final_index": "index.md",
            "final_verification": "verification/final-investment-analysis-verification.md",
        },
    )
    write_json(
        token / "scope.json",
        {
            "scope_slug": TOKEN_SLUG,
            "chain": "Ethereum mainnet",
            "symbol": "GOOD",
            "token_address": TOKEN_ADDRESS,
            "status": "pass",
        },
    )

    write(
        root / "README.md",
        f"""
        # Asset good minimal fixture

        ## What was analyzed
        One synthetic token scope, GOOD on Ethereum mainnet.

        ## Manifest
        The manifest is [run-manifest.json](run-manifest.json).

        ## Token and PT folders
        Token folder: [{TOKEN_DIR}]({TOKEN_DIR}/).
        PT markets: none supplied; see [pt-markets/index.md](pt-markets/index.md).

        ## Read first
        Read [index.md](index.md), [{TOKEN_DIR}/analyst-report.md]({TOKEN_DIR}/analyst-report.md), and [verification/final-investment-analysis-verification.md](verification/final-investment-analysis-verification.md).

        ## Final validation status
        pass
        """,
    )
    write(
        root / "index.md",
        f"""
        # Asset good minimal index

        ## Tokens analyzed
        - GOOD — [{TOKEN_DIR}]({TOKEN_DIR}/).

        ## PT markets analyzed
        None. S3_pt_market_economics skipped because no PT market was supplied in this run scope.

        ## Headline risk / return findings
        Synthetic fixture only; no economic conclusion is asserted.

        ## Missing data and blockers
        None for fixture validation.

        ## Artifact map
        - Manifest: [run-manifest.json](run-manifest.json)
        - Token analyst report: [{TOKEN_DIR}/analyst-report.md]({TOKEN_DIR}/analyst-report.md)
        - Investment analysis: [investment-analysis/index.md](investment-analysis/index.md)
        - Final verification: [verification/final-investment-analysis-verification.md](verification/final-investment-analysis-verification.md)

        ## Final verification status
        pass
        """,
    )
    write(
        root / "pt-markets/index.md",
        """
        # PT market index

        Status: skipped.
        Stage: S3_pt_market_economics.
        Reason: No PT market was supplied in this run scope.
        """,
    )
    write(
        root / "x-research/index.md",
        """
        # X/social research index

        Status: skipped.
        Stage: S4_x_social_mining — skipped. Reason: No X/social scope was supplied in this run scope.
        Stage: S5_x_social_synthesis — skipped. Reason: No X/social scope was supplied in this run scope.
        """,
    )

    s1_surface = """
    # S1 evidence

    | Fact slot | Value | Decision effect |
    | --- | --- | --- |
    | Token identity | GOOD token at 0x1111111111111111111111111111111111111111 | pass |
    | Decimals | 18 | pass |
    | Implementation/proxy status | non-proxy fixture contract | pass |
    | Issuer/protocol entity | synthetic fixture issuer | pass |
    | Backing/NAV model | fixture NAV equals 1.00 | pass |
    | Transfer restrictions | none in fixture | pass |
    | Mint/redeem access | not_in_scope | fixture has no live mint/redeem |
    | Freeze, blacklist, pause, forced-transfer, or admin-control surface | none in fixture | pass |
    | Liquidity venues and current depth | synthetic venue with USD 1,000,000 depth | pass |
    | Oracle/accounting method | fixed fixture accounting method | pass |
    | Audits/incidents | not_in_scope | synthetic fixture has no live audit scope |
    | Missing fields and decision effect | none | pass |
    """
    write(token / "research/onchain-admin.md", s1_surface)
    write(token / "research/issuer-backing-security.md", s1_surface)
    write(token / "research/transfer-liquidity-oracle-governance.md", s1_surface)
    write(token / "technical-report.md", s1_surface)
    write(
        token / "analyst-report.md",
        """
        # GOOD analyst report

        ## Executive view
        Synthetic fixture passes formal report-section coverage.

        ## What the token represents
        GOOD represents a synthetic token used only for harness validation.

        ## Main risk implications
        No economic risk conclusion is asserted.

        ## Backing and NAV quality
        Fixture backing is explicitly synthetic.

        ## Liquidity and exit risk
        Liquidity is synthetic and exists only as a labeled field.

        ## Controls, governance, and legal restrictions
        No live controls are assessed.

        ## Pricing/oracle risk in plain language
        The fixture uses a fixed accounting value.

        ## What must be checked before live use
        Not applicable; this fixture is not a live asset.

        ## Evidence quality
        Fixture evidence is self-contained.

        ## Source map
        - technical appendix: technical-report.md
        - on-chain admin: research/onchain-admin.md

        ## Technical appendix pointer
        See technical-report.md.
        """,
    )
    write(token / "verification.md", "# Token verification\n\nStatus: pass. Required S1 and S2 checks present.")

    s6_fields = """
    | Field | Value state | Reason |
    | --- | --- | --- |
    | Gross ROI | 0.0100 | fixture numeric value |
    | Simple annualized return | 0.1200 | fixture numeric value |
    | Compound annualized return | not_in_scope | no compounding interval was supplied for the fixture |
    | Points EV | 0.0000 | fixture numeric value |
    | Points ROI | 0.0000 | fixture numeric value |
    | Points annualized return | 0.0000 | fixture numeric value |
    | Expected loss | 0.0000 | fixture numeric value |
    | Exit cost | 0.0000 | fixture numeric value |
    | Risk-adjusted ROI | 0.0100 | fixture numeric value |
    | Risk-adjusted annualized return | 0.1200 | fixture numeric value |
    | Break-even points ROI | 0.0000 | fixture numeric value |
    | Break-even terminal drawdown | 0.0100 | fixture numeric value |
    | Price-stability certainty score | 1.0000 | fixture numeric value |
    """
    write(root / "investment-analysis/quantitative-underwriting-methodology.md", "# Quantitative underwriting methodology\n\n" + s6_fields)
    write(root / "investment-analysis/investment-analyst-report-points-pt-risk-return.md", "# Points/PT risk-return report\n\n" + s6_fields)
    write(root / "investment-analysis/index.md", "# Investment analysis index\n\n" + s6_fields)

    write(
        root / "verification/final-investment-analysis-verification.md",
        f"""
        # Final investment-analysis verification

        Status: pass.

        ## Required file checks
        PASS — required root files, per-token files, and skipped PT/social index files exist.

        ## Per-token and per-PT folder structure
        PASS — token folder `{TOKEN_DIR}` follows `output-structure.md`; no PT folders are in scope.

        ## Manifest paths and artifact paths
        PASS — `run-manifest.json`, token `artifact_dir`, `final_index`, and `final_verification` resolve inside the run root.

        ## Cross-link resolution
        PASS — local Markdown links in README.md, index.md, investment-analysis/index.md, and this verification file resolve inside the run root.

        ## Required sections and quantitative fields
        PASS — S1 fact slots, S2 sections, and exact S6 quantitative fields were checked, including Compound annualized return.

        ## Skipped-stage checks
        PASS — S3_pt_market_economics, S4_x_social_mining, and S5_x_social_synthesis are skipped with explicit reasons.

        ## Unsupported allocation conclusions
        PASS — no source artifact gives an execution-ready or allocation-ready claim.

        ## Workspace validation
        PASS — command evidence recorded for fixture validation.
        Command: python3 dev/tools/validate_workflow_run.py --workflow asset-investment-diligence --run-root {root} --format json
        Exit status: 0

        ## README and index handoff sections
        PASS — README.md and index.md include manifest path, token folder, read-first paths, artifact map, blockers, and final validation status.
        """,
    )


def run_validator(run_root: Path):
    proc = subprocess.run(
        VALIDATOR + ["--run-root", str(run_root)],
        text=True,
        capture_output=True,
    )
    try:
        report = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError((str(run_root), "invalid json", proc.returncode, proc.stdout, proc.stderr)) from exc
    return proc, report


def finding_ids(report):
    return {finding.get("id") for finding in report.get("findings", [])}

try:
    build_good_fixture(TMP_GOOD)
    proc, report = run_validator(TMP_GOOD)
    assert proc.returncode == 0, ("generated-good", proc.returncode, report, proc.stderr)
    assert report.get("exit_code") == 0, report
    assert report.get("status") == "pass", report
    assert report.get("workflow") == "asset-investment-diligence-v1", report
    assert not report.get("findings"), report.get("findings")
    assert "validator.workflow_checks_deferred" not in finding_ids(report), report

    cases = [
        ("asset-bad-manifest-entry-drift", 2, {"asset.manifest.artifact_dir_reconciles", "asset.scope.identity_reconciles"}),
        ("asset-bad-missing-token-file", 2, {"asset.token.required_file_exists", "asset.token.required_research_file_exists"}),
        ("asset-bad-missing-final-verification", 2, {"asset.final_verification.file_exists", "asset.root.required_file_exists"}),
        ("asset-bad-missing-s1-slot", 1, {"asset.s1.required_fact_slot_present"}),
        ("asset-bad-missing-s2-section", 1, {"asset.s2.required_section_present"}),
        ("asset-bad-missing-skipped-pt-social-markers", 1, {"asset.skipped_pt.marker_present", "asset.skipped_social.marker_present"}),
        ("asset-bad-missing-s6-calculation-fields", 1, {"asset.s6.required_field_present"}),
        ("asset-bad-s6-heading-only-overclaim", 1, {"asset.s6.heading_only_false_pass", "asset.final_verification.overclaim"}),
        ("asset-bad-final-verification-overclaim", 1, {"asset.final_verification.overclaim"}),
        (
            "asset-bad-missing-s7-crosslink-workspace-readme-index",
            1,
            {
                "asset.final_verification.cross_links_checked",
                "asset.final_verification.workspace_validation_present",
                "asset.readme_handoff_sections",
                "asset.index_contract_sections",
            },
        ),
    ]

    for fixture, expected_exit, expected_any in cases:
        run_root = BASE / fixture
        assert run_root.exists(), f"missing fixture: {run_root}"
        proc, report = run_validator(run_root)
        assert proc.returncode == expected_exit, (fixture, proc.returncode, expected_exit, report, proc.stderr)
        assert report.get("exit_code") == expected_exit, (fixture, report)
        found = finding_ids(report)
        assert found & expected_any, (fixture, expected_any, found, report)
        assert all("check_id" not in finding for finding in report.get("findings", [])), (fixture, report)

    print("M2_ASSET_HARDENED_ACCEPTANCE: PASS")
finally:
    shutil.rmtree(TMP_GOOD, ignore_errors=True)
PY

git diff --check -- dev/tools/validate_workflow_run.py dev/implementation/workflow-harness/fixtures/asset-*
git status --short -- dev/tools/validate_workflow_run.py dev/implementation/workflow-harness/fixtures/asset-*
```

## Current hardening-task validation commands

For this planning task only, validate this brief with:

```bash
python3 - <<'PY'
from pathlib import Path
p = Path('dev/implementation/workflow-harness/m2-asset-checks-hardened.md')
text = p.read_text()
required = [
    'M1 report contract',
    'finding fields, severities, status, and exit-code behavior with the M1 validator-core contract',
    'validator.workflow_checks_deferred',
    'asset.final_verification.cross_links_checked',
    'asset.final_verification.workspace_validation_present',
    'asset.readme_handoff_sections',
    'asset.index_contract_sections',
    'Compound annualized return is always required',
    'Generated temporary good run',
    'asset-bad-missing-s7-crosslink-workspace-readme-index',
    'M2_ASSET_HARDENED_ACCEPTANCE: PASS',
]
missing = [item for item in required if item not in text]
assert not missing, missing
for forbidden in [
    'finding[' + '"check_id"' + ']',
    'severity"' + ': "blocker | error | warning"',
    'status"' + ': "pass | warning | fail"',
]:
    assert forbidden not in text, forbidden
assert '"id": "asset.s6.required_field_present"' in text
assert '"workflow": "asset-investment-diligence-v1"' in text
print(f'M2_ASSET_CHECKS_HARDENED_SELF_CHECK: PASS bytes={len(text.encode())} lines={text.count(chr(10)) + 1}')
PY

rc=0
git diff --no-index --check /dev/null dev/implementation/workflow-harness/m2-asset-checks-hardened.md || rc=$?
# `git diff --no-index --check /dev/null <new-file>` returns exit 1 for a clean new-file diff.
# Treat exit 1 as pass; any other non-zero exit indicates a real diff/check error.
if [ "$rc" -ne 0 ] && [ "$rc" -ne 1 ]; then
  exit "$rc"
fi

git status --short -- dev/implementation/workflow-harness/m2-asset-checks-hardened.md
```

## Definition of done for the future implementation slice

- `dev/tools/validate_workflow_run.py` implements the asset-investment-diligence checks listed above.
- The implementation preserves the M1 report schema, uses `finding.id`, uses severities `P0` / `P1` / `P2`, and reports only `pass` / `review_required` / `fail`.
- A generated good asset run exits `0`, reports `status="pass"`, and has no `validator.workflow_checks_deferred` finding.
- Every required negative asset fixture is asserted by the acceptance wrapper and produces an expected finding ID.
- `Compound annualized return` is always checked as an exact S6 field, with an allowed non-numeric state plus reason when not relevant.
- Final-verification checks cover required files, folders, cross-links, required sections, exact quantitative fields, skipped stages, unsupported allocation claims, workspace validation, and `README.md` / `index.md` handoff sections.
- Missing exact S6 fields or heading-only S6 overclaims cannot pass as broad calculation groups.
- Empty PT/social scope cannot pass without explicit skipped markers and reasons.
- The implementation does not mutate workflow semantics, runtime docs, prompt text, existing historical run artifacts, oracle checks, or combined Analyze→Propose checks.
- Final handoff reports files changed, commands run, exit codes, and validation output.
