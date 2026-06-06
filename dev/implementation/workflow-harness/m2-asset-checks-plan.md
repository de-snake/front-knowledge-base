# M2 implementation brief — asset-investment-diligence harness checks

Purpose: implement the asset-workflow validation slice from the hardened workflow-harness plan. This slice adds deterministic checks for `asset-investment-diligence` run artifacts only. It must not assess token economics, oracle correctness, allocation suitability, or whether the reports are persuasive.

This brief is intentionally narrow. It specifies exactly what the implementation task may edit, which checks must be added, and which commands prove the slice is complete.

## Grounded inputs

Implementation must treat these files as the asset workflow contract:

- `CLAUDE.md`.
- `user/references/workflows/asset-investment-diligence/output-structure.md`.
- `user/references/workflows/asset-investment-diligence/stage-contracts.md`.
- `user/references/workflows/asset-investment-diligence/runbook.md`.
- `dev/implementation/workflow-harness/hardened-plan.md`.
- `dev/implementation/workflow-harness/internal-audit.md`.
- `dev/implementation/workflow-harness/plan-review.md`.

## Edit boundary

The implementation slice may edit exactly these paths:

1. `dev/tools/validate_workflow_run.py`
   - Create the file if it does not exist.
   - Keep this slice self-contained in the single script; do not add a package tree unless a later task explicitly authorizes it.

2. Optional fixture metadata only, if the implementer wants stable acceptance fixtures:
   - `dev/implementation/workflow-harness/fixtures/asset-good-token-only/metadata.json`
   - `dev/implementation/workflow-harness/fixtures/asset-bad-manifest-entry-drift/metadata.json`
   - `dev/implementation/workflow-harness/fixtures/asset-bad-missing-token-file/metadata.json`
   - `dev/implementation/workflow-harness/fixtures/asset-bad-missing-s6-calculation-fields/metadata.json`
   - `dev/implementation/workflow-harness/fixtures/asset-bad-missing-skipped-pt-social-markers/metadata.json`
   - `dev/implementation/workflow-harness/fixtures/asset-bad-missing-final-verification/metadata.json`

Do not edit workflow source docs, existing run artifacts, README/navigation files, or non-asset oracle/combined harness logic in this slice. If the validator needs reusable helpers, define them inside `dev/tools/validate_workflow_run.py` for now.

## CLI contract

`dev/tools/validate_workflow_run.py` must support at minimum:

```bash
python3 dev/tools/validate_workflow_run.py \
  --workflow asset-investment-diligence \
  --run-root dev/implementation/<run-slug> \
  --format json
```

Required behavior:

- Exit `0` when no findings with severity `error` or `blocker` are present.
- Exit `1` when non-blocking `warning` findings are present and no `error` / `blocker` findings are present.
- Exit `2` when any `error` or `blocker` finding is present.
- `--format json` prints one JSON object to stdout with this shape:

```json
{
  "workflow": "asset-investment-diligence",
  "run_root": "dev/implementation/<run-slug>",
  "status": "pass | warning | fail",
  "findings": [
    {
      "severity": "blocker | error | warning",
      "check_id": "asset.manifest.required_field",
      "path": "run-manifest.json",
      "field": "tokens[0].artifact_dir",
      "expected": "tokens/<token_slug>",
      "actual": "...",
      "fix_hint": "..."
    }
  ]
}
```

The report should store concise path/field evidence only. Do not dump raw source evidence or report bodies.

## Required checks

### 1. Manifest schema and path reconciliation

Parse `<run-root>/run-manifest.json` and validate the asset contract.

Top-level required fields:

- `workflow_id`: must equal `asset-investment-diligence-v1`.
- `run_id`: non-empty string.
- `run_artifact_root`: non-empty string that normalizes to the supplied `--run-root` when both are resolved from the vault root.
- `tokens`: array, non-empty for this M2 slice.
- `pt_markets`: array, may be empty.
- `x_research_scopes`: array, may be empty.
- `final_index`: must resolve under `--run-root`; expected default is `index.md`.
- `final_verification`: must resolve under `--run-root`; expected default is `verification/final-investment-analysis-verification.md`.

Per-token required fields for each `tokens[]` entry:

- `token_slug`: non-empty string.
- `chain`: non-empty string.
- `symbol`: non-empty string.
- `address`: `0x` EVM address, case-insensitive.
- `artifact_dir`: must equal `tokens/<token_slug>` unless the workflow contract is updated.
- `status`: one of `pass`, `review_required`, `blocked`.

Path and identity reconciliation:

- Every manifest path must stay inside the supplied `--run-root`; reject absolute paths, `..` escapes, and sibling-run paths for required artifact fields.
- `tokens[].artifact_dir` must resolve to an existing directory under `--run-root`.
- The folder basename must equal `tokens[].token_slug`.
- `<artifact_dir>/scope.json` must parse as JSON.
- `scope.json` must reconcile with the manifest token entry:
  - `symbol` equals `scope.json.symbol`.
  - manifest `address` equals `scope.json.token_address` or `scope.json.address`, case-insensitive.
  - manifest `chain` equals `scope.json.chain` or `scope.json.chain_name` when either field is present.
  - if `scope.json.scope_slug` is present, it equals `token_slug`.

Required check IDs:

- `asset.manifest.json_parse`
- `asset.manifest.required_field`
- `asset.manifest.workflow_id`
- `asset.manifest.run_root_reconciles`
- `asset.manifest.token_entry_schema`
- `asset.manifest.artifact_dir_reconciles`
- `asset.manifest.path_inside_run_root`
- `asset.scope.json_parse`
- `asset.scope.identity_reconciles`

### 2. Required root files and token file sets

Required run-root files:

- `README.md`.
- `run-manifest.json`.
- `index.md`.
- `investment-analysis/quantitative-underwriting-methodology.md`.
- `investment-analysis/investment-analyst-report-points-pt-risk-return.md`.
- `investment-analysis/index.md`.
- `verification/final-investment-analysis-verification.md`.

Required per-token files under every `tokens[].artifact_dir`:

- `scope.json`.
- `research/onchain-admin.md`.
- `research/issuer-backing-security.md`.
- `research/transfer-liquidity-oracle-governance.md`.
- `technical-report.md`.
- `analyst-report.md`.
- `verification.md`.

Required check IDs:

- `asset.root.required_file_exists`
- `asset.token.required_file_exists`
- `asset.token.required_research_file_exists`

### 3. S1 required facts

Check S1 at the per-token level. The validator should scan `scope.json`, the three `research/*.md` files, and `technical-report.md` as a combined S1 evidence surface. It should not judge whether the facts are economically correct; it only checks that the required fact slots are present with non-empty values, explicit `unknown`, `not_found`, `not_in_scope`, or `blocked` markers.

Required S1 fact slots:

- token identity.
- decimals.
- implementation/proxy status.
- issuer/protocol entity.
- backing/NAV model.
- transfer restrictions.
- mint/redeem access.
- freeze, blacklist, pause, forced-transfer, or admin-control surface.
- liquidity venues and current depth.
- oracle/accounting method.
- audits/incidents.
- missing fields and decision effect.

Implementation guidance:

- Accept either exact heading text, normalized label text, or a small JSON/frontmatter field if present.
- Treat a broad heading such as `Risk overview` as insufficient for these slots unless the matching slot label appears under it.
- A token may be `review_required` with unknown fields, but the unknowns must be named and tied to a decision effect.

Required check IDs:

- `asset.s1.required_fact_slot_present`
- `asset.s1.unknown_has_decision_effect`

### 4. S2 required report sections

Check each token `analyst-report.md` for the required report sections from `stage-contracts.md`.

Required S2 sections:

- `Executive view`.
- `What the token represents`.
- `Main risk implications`.
- `Backing and NAV quality`.
- `Liquidity and exit risk`.
- `Controls, governance, and legal restrictions`.
- `Pricing/oracle risk in plain language`.
- `What must be checked before live use`.
- `Evidence quality`.
- `Source map`.
- `Technical appendix pointer`.

Implementation guidance:

- Normalize heading case, punctuation, and `and` / `&` variants.
- Do not accept a source-map mention inside prose as the `Source map` section; require a heading or explicit labeled block.
- Do not require token comparison sections. Cross-token ranking belongs to S6, not S2.

Required check IDs:

- `asset.s2.required_section_present`
- `asset.s2.source_map_present`
- `asset.s2.technical_appendix_pointer_present`

### 5. Skipped PT and social markers

This M2 slice does not implement full PT-market or X/social validation. It only prevents silent omission when those stages are out of scope.

If `pt_markets` is empty:

- Require `pt-markets/index.md`.
- Require an explicit skipped marker for `S3_pt_market_economics` either in `run-manifest.json.skipped_stages` or in `pt-markets/index.md`.
- The marker must include a reason, for example `No PT market was supplied in this run scope.`

If `x_research_scopes` is empty:

- Require `x-research/index.md`.
- Require explicit skipped markers for `S4_x_social_mining` and `S5_x_social_synthesis` either in `run-manifest.json.skipped_stages` or in `x-research/index.md`.
- Each marker must include a reason.

If `pt_markets` or `x_research_scopes` is non-empty, this slice may emit a `warning` check that full PT/social validation is not implemented in M2. It must not mark those stages as passed unless their required fields are actually checked by a later slice.

Required check IDs:

- `asset.skipped_pt.index_exists`
- `asset.skipped_pt.marker_present`
- `asset.skipped_pt.reason_present`
- `asset.skipped_social.index_exists`
- `asset.skipped_social.marker_present`
- `asset.skipped_social.reason_present`
- `asset.pt_social.full_validation_out_of_scope`

### 6. S6 required quantitative fields

Check S6 across these files:

- `investment-analysis/quantitative-underwriting-methodology.md`.
- `investment-analysis/investment-analyst-report-points-pt-risk-return.md`.
- `investment-analysis/index.md`.

Required S6 fields:

- `Gross ROI` / `gross_roi`.
- `Simple annualized return` / `simple_annualized_return`.
- `Compound annualized return` / `compound_annualized_return` when relevant.
- `Points EV` / `points_ev`.
- `Points ROI` / `points_roi`.
- `Points annualized return` / `points_annualized_return`.
- `Expected loss` / `expected_loss`.
- `Exit cost` / `exit_cost`.
- `Risk-adjusted ROI` / `risk_adjusted_roi`.
- `Risk-adjusted annualized return` / `risk_adjusted_annualized_return`.
- `Break-even points ROI` / `break_even_points_roi`.
- `Break-even terminal drawdown` / `break_even_terminal_drawdown`.
- `Price-stability certainty score` / `price_stability_certainty_score`.

No false-pass rule:

- A heading such as `Gross return stack`, `Risk-adjusted return stack`, `Points valuation`, or `Price-stability certainty` does not satisfy the exact field requirement by itself.
- Each field must have a machine-readable or explicitly labeled value state: numeric value, `null`, `not_in_scope`, `skipped_due_to_missing_input`, `unknown`, or `blocked`.
- If the value state is not numeric, the same row/object/block must include a reason.
- If the final verification says a broad calculation group passed while exact fields are absent, emit a final-verification overclaim finding.

Required check IDs:

- `asset.s6.required_field_present`
- `asset.s6.required_field_has_value_state`
- `asset.s6.non_numeric_value_has_reason`
- `asset.s6.heading_only_false_pass`

### 7. Required final verification

Validate the file declared by `run-manifest.json.final_verification`.

Required final-verification checks:

- The declared final verification file exists.
- It contains a status marker: `pass`, `review_required`, `blocked`, or `fail`.
- It records required file checks.
- It records required content/field checks, including exact S6 quantitative fields, not only broad headings.
- It records skipped-stage checks when PT/social scopes are absent.
- It records command evidence with command text and exit status or an explicit marker such as `PASS` / `FAIL`.
- It must not claim `pass` for required content checks when validator-detected required fields are absent.
- It must not claim the run is execution-ready if unresolved live inputs, issuer eligibility, feed support, route support, or user-policy blockers are named elsewhere in the run.

Required check IDs:

- `asset.final_verification.file_exists`
- `asset.final_verification.status_present`
- `asset.final_verification.required_file_checks_present`
- `asset.final_verification.required_field_checks_present`
- `asset.final_verification.skipped_stage_checks_present`
- `asset.final_verification.command_evidence_present`
- `asset.final_verification.overclaim`
- `asset.final_verification.no_unsupported_execution_ready_claim`

## Fixture metadata contract, if used

Fixture metadata files are optional, but if the implementation creates them they must be small JSON descriptors, not copied evidence trees. Each metadata file should have this shape:

```json
{
  "name": "asset-bad-missing-s6-calculation-fields",
  "workflow": "asset-investment-diligence",
  "run_root": "dev/implementation/asset-diligence-2026-06-05-sample-base-token-sample-vault-token",
  "expected_exit_code": 2,
  "expected_check_ids": [
    "asset.s6.required_field_present",
    "asset.s6.heading_only_false_pass",
    "asset.final_verification.overclaim"
  ]
}
```

The validator does not need a `--fixture` mode for M2. Acceptance wrappers can read metadata and invoke `--run-root`.

Recommended fixture mapping:

| Metadata file | Run root to point at | Expected result |
|---|---|---|
| `asset-good-token-only/metadata.json` | a known-good asset-only root, preferably the `asset-investment-diligence/` child of the existing agentic good run if available in this checkout | exit `0` |
| `asset-bad-missing-s6-calculation-fields/metadata.json` | `dev/implementation/asset-diligence-2026-06-05-sample-base-token-sample-vault-token` | exit `2`, exact S6 fields absent despite heading-level pass rows |
| `asset-bad-missing-skipped-pt-social-markers/metadata.json` | `dev/implementation/asset-diligence-2026-06-05-sample-base-token-sample-vault-token` | exit `2`, empty PT/social arrays without skipped-stage markers |
| `asset-bad-missing-final-verification/metadata.json` | a temporary or metadata-described copy with `verification/final-investment-analysis-verification.md` absent | exit `2` |
| `asset-bad-manifest-entry-drift/metadata.json` | a temporary or metadata-described copy with stale `tokens[].artifact_dir` or address mismatch | exit `2` |
| `asset-bad-missing-token-file/metadata.json` | a temporary or metadata-described copy with one required token research file absent | exit `2` |

If a stable good root is not present in this checkout, do not fabricate one from memory. Mark the good fixture metadata as unavailable and rely on the negative assertions plus syntax checks until a later fixture-copy task is authorized.

## Acceptance commands

Run from `/Users/ilya/Documents/Codex/front-knowledge-base` after implementing M2.

### 1. Syntax and CLI smoke

```bash
python3 -m py_compile dev/tools/validate_workflow_run.py
python3 dev/tools/validate_workflow_run.py --workflow asset-investment-diligence --run-root dev/implementation/asset-diligence-2026-06-05-sample-base-token-sample-vault-token --format json >/tmp/asset-harness-report.json || test "$?" -eq 2
python3 - <<'PY'
import json
from pathlib import Path
report = json.loads(Path('/tmp/asset-harness-report.json').read_text())
assert report['workflow'] == 'asset-investment-diligence'
assert report['findings'], report
print('ASSET_HARNESS_JSON_SMOKE_PASS')
PY
```

### 2. Existing partial asset run must not false-pass missing S6 fields

```bash
python3 - <<'PY'
import json
import subprocess

cmd = [
    'python3',
    'dev/tools/validate_workflow_run.py',
    '--workflow', 'asset-investment-diligence',
    '--run-root', 'dev/implementation/asset-diligence-2026-06-05-sample-base-token-sample-vault-token',
    '--format', 'json',
]
proc = subprocess.run(cmd, text=True, capture_output=True)
assert proc.returncode == 2, proc.stdout + proc.stderr
report = json.loads(proc.stdout)
check_ids = {finding['check_id'] for finding in report['findings']}
required = {
    'asset.s6.required_field_present',
    'asset.s6.heading_only_false_pass',
    'asset.final_verification.overclaim',
}
missing = required - check_ids
assert not missing, (missing, report)
print('ASSET_BAD_S6_FALSE_PASS_BLOCKED')
PY
```

### 3. Existing partial asset run must fail skipped PT/social markers

```bash
python3 - <<'PY'
import json
import subprocess

cmd = [
    'python3',
    'dev/tools/validate_workflow_run.py',
    '--workflow', 'asset-investment-diligence',
    '--run-root', 'dev/implementation/asset-diligence-2026-06-05-sample-base-token-sample-vault-token',
    '--format', 'json',
]
proc = subprocess.run(cmd, text=True, capture_output=True)
assert proc.returncode == 2, proc.stdout + proc.stderr
report = json.loads(proc.stdout)
check_ids = {finding['check_id'] for finding in report['findings']}
required = {
    'asset.skipped_pt.marker_present',
    'asset.skipped_social.marker_present',
}
missing = required - check_ids
assert not missing, (missing, report)
print('ASSET_SKIPPED_MARKERS_REQUIRED')
PY
```

### 4. Manifest and token-file checks must be covered by asserted failures

If fixture metadata for manifest drift or missing token files is added, run:

```bash
python3 - <<'PY'
import json
import subprocess
from pathlib import Path

fixtures = [
    Path('dev/implementation/workflow-harness/fixtures/asset-bad-manifest-entry-drift/metadata.json'),
    Path('dev/implementation/workflow-harness/fixtures/asset-bad-missing-token-file/metadata.json'),
    Path('dev/implementation/workflow-harness/fixtures/asset-bad-missing-final-verification/metadata.json'),
]
missing_metadata = [str(path) for path in fixtures if not path.exists()]
assert not missing_metadata, missing_metadata
for path in fixtures:
    meta = json.loads(path.read_text())
    proc = subprocess.run([
        'python3', 'dev/tools/validate_workflow_run.py',
        '--workflow', meta['workflow'],
        '--run-root', meta['run_root'],
        '--format', 'json',
    ], text=True, capture_output=True)
    assert proc.returncode == meta['expected_exit_code'], (path, proc.returncode, proc.stdout, proc.stderr)
    report = json.loads(proc.stdout)
    check_ids = {finding['check_id'] for finding in report['findings']}
    missing = set(meta['expected_check_ids']) - check_ids
    assert not missing, (path, missing, report)
print('ASSET_FIXTURE_METADATA_FAILURES_ASSERTED')
PY
```

If those metadata files are not created in M2, the implementer must instead include equivalent inline temporary-fixture assertions in the task handoff. Do not claim manifest-drift, missing-token-file, or missing-final-verification coverage without one of these two forms of evidence.

### 5. Diff and status evidence

```bash
git diff --check -- dev/tools/validate_workflow_run.py dev/implementation/workflow-harness/fixtures
git status --short -- dev/tools/validate_workflow_run.py dev/implementation/workflow-harness/fixtures
```

If M2 only creates `dev/tools/validate_workflow_run.py` and no fixture metadata, scope the same commands to the script path only.

## Definition of done for M2 implementation

The implementation task is done only when:

- `dev/tools/validate_workflow_run.py` exists and supports the CLI contract above.
- Manifest schema, path reconciliation, required files, token file sets, S1 slots, S2 sections, skipped PT/social markers, S6 exact fields, and final verification checks are implemented for `asset-investment-diligence`.
- The known partial asset run at `dev/implementation/asset-diligence-2026-06-05-sample-base-token-sample-vault-token` exits nonzero and reports missing exact S6 calculation fields instead of passing broad headings.
- Any claimed manifest/token-file/final-verification failure class is backed by fixture metadata or an inline temporary-fixture acceptance assertion.
- No workflow source docs or existing run artifacts are modified.
- The handoff lists commands run, exit codes, and changed files.
