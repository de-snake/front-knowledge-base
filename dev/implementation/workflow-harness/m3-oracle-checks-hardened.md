# M3 hardened execution brief — oracle-analysis harness checks

Purpose: final implementation brief for the M3 oracle-analysis workflow harness slice after formal review. This brief is limited to formal workflow compliance. It does not assess oracle economic quality, token investment quality, or whether a specific oracle conclusion is correct.

This file is the only mutation for the hardening task. The future implementation slice must stay inside the edit boundary below.

## Inputs reviewed

- `CLAUDE.md`.
- `dev/implementation/workflow-harness/m3-oracle-checks-plan.md`.
- `dev/implementation/workflow-harness/m3-oracle-checks-review.md`.
- `dev/implementation/workflow-harness/plan-review.md`.
- `dev/implementation/workflow-harness/internal-audit.md`.
- `dev/implementation/workflow-harness/hardened-plan.md`.
- `user/references/workflows/oracle-analysis/output-structure.md`.
- `user/references/workflows/oracle-analysis/stage-contracts.md`.
- `user/references/workflows/oracle-analysis/gearbox-price-feed-parsing.md`.
- Gearbox front-knowledge-base runtime workflow placement and formal workflow critic references.

## Review blockers incorporated

The future implementation must close every blocker from `m3-oracle-checks-review.md`:

1. Require canonical `verification/final-oracle-analysis-verification.md`; do not accept an arbitrary replacement final verification path.
2. Reconcile root, scope, index, per-scope verification, and final-verification statuses.
3. Validate required `index.md` and `README.md` top-level handoff sections.
4. Check formula evidence directly in `oracle/feed-graph.md` and `oracle/node-classification.md`.
5. Strengthen source-primitive audit checks beyond one-marker presence.
6. Require Gearbox Price Feed Store (PFS), Instance Owner, and PFS add/update availability-control fields.
7. Add negative fixtures for noncanonical final verification, status contradiction, missing top-level handoff section, missing formula, and weak source audit.

## Slice goal

Add deterministic oracle-analysis validation to `dev/tools/validate_workflow_run.py` so the harness can reject formally incomplete oracle-analysis runs without judging the economic correctness of the analysis.

The validator must cover these formal contract classes:

1. Manifest schema and manifest-to-scope reconciliation.
2. Canonical run-level final verification pathing.
3. Root, scope, index, and verification status reconciliation.
4. Required per-scope folder and file structure.
5. Required root `index.md` and `README.md` handoff sections.
6. Required source evidence directories and feed probe registry.
7. Direct feed formula evidence in graph and classification artifacts.
8. Side-specific verdict fields.
9. Liquidity-cascade and liquidity-trap stress framing.
10. Gearbox-required protocol-fit, PFS, and Instance Owner fields.
11. Strong source primitive audit coverage.
12. No conclusion that stops at a top-level oracle label.

## Exact files to edit in the future implementation slice

Required code edit:

- `dev/tools/validate_workflow_run.py`

Required or optional fixture edits, only to prove the checks below:

- `dev/implementation/workflow-harness/fixtures/oracle-good-minimal/**`
- `dev/implementation/workflow-harness/fixtures/oracle-bad-missing-manifest-scope-field/**`
- `dev/implementation/workflow-harness/fixtures/oracle-bad-noncanonical-final-verification/**`
- `dev/implementation/workflow-harness/fixtures/oracle-bad-missing-final-verification/**`
- `dev/implementation/workflow-harness/fixtures/oracle-bad-root-status-contradiction/**`
- `dev/implementation/workflow-harness/fixtures/oracle-bad-missing-per-scope-file/**`
- `dev/implementation/workflow-harness/fixtures/oracle-bad-missing-index-section/**`
- `dev/implementation/workflow-harness/fixtures/oracle-bad-missing-readme-section/**`
- `dev/implementation/workflow-harness/fixtures/oracle-bad-missing-source-evidence/**`
- `dev/implementation/workflow-harness/fixtures/oracle-bad-weak-source-audit/**`
- `dev/implementation/workflow-harness/fixtures/oracle-bad-missing-formula/**`
- `dev/implementation/workflow-harness/fixtures/oracle-bad-side-verdict-fields/**`
- `dev/implementation/workflow-harness/fixtures/oracle-bad-no-cascade-trap/**`
- `dev/implementation/workflow-harness/fixtures/oracle-bad-missing-gearbox-fields/**`
- `dev/implementation/workflow-harness/fixtures/oracle-bad-top-level-label-only/**`

Do not edit workflow contracts, prompt files, docs navigation, `CLAUDE.md`, asset-investment-diligence checks, or token diligence semantics in this slice.

## Validator behavior

### CLI scope

The M3 code path must run when the validator is called with:

```bash
python3 dev/tools/validate_workflow_run.py \
  --workflow oracle-analysis \
  --run-root <run-root> \
  --format json
```

The report must stay compact and evidence-based:

```json
{
  "workflow": "oracle-analysis",
  "run_root": "<run-root>",
  "status": "pass | review_required | blocked | fail",
  "findings": [
    {
      "severity": "P0 | P1 | P2",
      "check_id": "oracle.conclusion_quad_present",
      "path": "tokens/<slug>/oracle/protocol-fit-memo.md",
      "field": "loss_bearer",
      "expected": "explicit field per relevant side",
      "actual": "missing",
      "fix_hint": "Add position side, token role, stress direction, and loss bearer for each verdict."
    }
  ]
}
```

Artifact statuses inside oracle run files must use only `pass`, `review_required`, or `blocked`. The validator report may use `fail` for malformed or unreadable input.

Exit-code policy:

- `0` when no findings remain.
- `1` when only P1/P2 review findings remain.
- `2` when any P0 structural blocker remains.

## P0 structural checks

### `oracle.manifest_schema`

Parse `<run-root>/run-manifest.json` and require:

- `workflow_id` equals `oracle-analysis-v1`.
- `run_id` is present.
- `run_artifact_root` is present and normalizes to the supplied `--run-root` or an explicitly accepted workspace-relative equivalent.
- `scopes` is a non-empty list unless the run is explicitly marked `blocked` before scope discovery.
- `final_index` equals `index.md` and resolves to an existing run-root `index.md` file.
- `final_verification` equals `verification/final-oracle-analysis-verification.md`.

Each `scopes[]` entry must include:

- `scope_id`.
- `scope_slug`.
- `scope_type` with value `token` or `pt_market`.
- `chain`.
- `asset_symbol`.
- `asset_address` or an explicit `null` plus blocker reason.
- `protocol`.
- `position_sides` as a list, or explicit `null` only for neutral inventory runs that stop before protocol-fit verdicts.
- `token_roles` as a list, or explicit `null` only for neutral inventory runs that stop before protocol-fit verdicts.
- `artifact_dir`.
- `status` with value `pass`, `review_required`, or `blocked`.

### `oracle.canonical_final_verification_path`

Require the canonical final verification file and manifest pointer:

```text
<run-root>/verification/final-oracle-analysis-verification.md
```

Rules:

- The manifest `final_verification` value must be exactly `verification/final-oracle-analysis-verification.md` after path normalization.
- The canonical file must exist under the run root.
- Absolute paths, parent-escaping paths, and alternate replacement files fail this check.
- Additional verification files may exist, but they are supplementary and do not replace the canonical file.

### `oracle.manifest_entry_reconciles_scope`

For each manifest scope:

- `artifact_dir` must resolve under the run root and must not be absolute or parent-escaping.
- `artifact_dir` must match `tokens/<scope_slug>` for `scope_type: token`.
- `artifact_dir` must match `pt-markets/<scope_slug>` for `scope_type: pt_market`.
- `<artifact_dir>/scope.json` must exist and parse as JSON.
- `scope.json` identity fields must reconcile with the manifest entry: scope id or slug, chain, protocol, asset symbol, asset address when known, position sides, token roles, and status.

### `oracle.required_files_present`

For every token or PT market scope, require:

```text
<scope-dir>/scope.json
<scope-dir>/oracle/scope.md
<scope-dir>/oracle/feed-graph.md
<scope-dir>/oracle/node-classification.md
<scope-dir>/oracle/source-primitive-audit.md
<scope-dir>/oracle/stress-tradeoff-analysis.md
<scope-dir>/oracle/protocol-fit-memo.md
<scope-dir>/raw/feed-probes.json
<scope-dir>/raw/source-evidence/
<scope-dir>/verification/oracle-analysis-verification.md
```

At the run root, require:

```text
README.md
run-manifest.json
index.md
verification/final-oracle-analysis-verification.md
```

`comparisons/<comparison>.md` is required only when comparisons are declared, linked, or listed in the manifest/index.

### `oracle.run_status_reconciles`

Normalize status severity as:

```text
blocked > review_required > pass
```

Compare status declarations across:

- manifest root status or declared validation status, when present;
- every `scopes[].status`;
- `index.md` validation result;
- every per-scope `verification/oracle-analysis-verification.md` status;
- run-level `verification/final-oracle-analysis-verification.md` status.

Rules:

- A root artifact must not upgrade unresolved `blocked` or `review_required` scope state to `pass`.
- If any scope or per-scope verification is `blocked`, root/index/final verification must not state `pass`.
- If any scope or per-scope verification is `review_required`, root/index/final verification must not state `pass` unless a named override says the item is outside the final validation scope.
- Unknown or unparseable status is P2 by itself, but becomes P1 when it creates a contradiction with a declared `pass`.
- Missing root status in `index.md` or final verification is covered by `oracle.index_contract_sections` or `oracle.final_verification_credibility`.

## P1 field-level checks

### `oracle.index_contract_sections`

`index.md` must contain concrete sections or tables for:

- scope table by token / PT market;
- feed formulas;
- side-specific verdict matrix covering borrower / Credit Account operator, pool LP / lender, liquidator, and curator/operator, or explicit `not_in_scope` reasons;
- open blockers;
- artifact map;
- validation result.

The check fails when a heading exists but the body has no concrete entry, path, status, or explicit `none` / `not_in_scope` marker.

### `oracle.readme_handoff_sections`

`README.md` must state:

- what was analyzed;
- where the manifest is;
- where each token or PT folder is;
- which files to read first;
- final validation status.

The check fails when the README is only generic project prose or omits the final validation status.

### `oracle.final_verification_credibility`

The run-level final verification file must do more than claim broad headings or file existence. It must contain explicit evidence that checks were run for:

- required root files;
- required per-scope files;
- manifest paths and declared artifact paths;
- canonical final verification path;
- root/scope/index/final status reconciliation;
- `index.md` and `README.md` handoff sections;
- graph leaf source primitive audits;
- node classification;
- pricing formula presence;
- staleness, bounds, timestamps, or explicit unavailable markers;
- protocol-fit fields;
- side-specific conclusion fields;
- Gearbox price-feed parsing reference when protocol is Gearbox;
- terminology or diff validation evidence.

Accept a Markdown checklist/table only if it names concrete check subjects. Prefer a JSON fenced block or frontmatter with command evidence, but do not require a new artifact type in this slice.

### `oracle.feed_graph_recursive`

`oracle/feed-graph.md` must identify the top-level feed and either:

- list child feeds/source primitives for every non-leaf node; or
- provide an explicit no-child explanation for a true leaf.

This check fails when the run stops at top-level labels such as `External`, `Composite`, `Bounded`, `ERC4626`, `Pendle`, `Curve`, `Balancer`, or `PFS available` without child feed detail or a formula.

### `oracle.pricing_formula_present`

Check formula evidence directly in both:

```text
<scope-dir>/oracle/feed-graph.md
<scope-dir>/oracle/node-classification.md
```

Rules:

- `feed-graph.md` must include a human-readable formula or equation that ties the top-level feed to child nodes/source primitives.
- `node-classification.md` must include a `Formula` section or equivalent table row explaining every operation, decimal/scale factor, bound, switch, safe-pricing rule, or fallback that affects the final price.
- A final verification claim that formula coverage passed is not sufficient if these two source artifacts omit the formula.
- If a true leaf has no formula beyond a direct primitive answer, the artifact must say so explicitly and name the primitive answer/source.

### `oracle.feed_probes_json_valid`

`raw/feed-probes.json` must parse as JSON and contain a registry of probed nodes, source identifiers, or explicit unavailable markers. Missing or invalid JSON is P0 when the file is absent and P1 when the file exists but omits node/source coverage.

### `oracle.node_classification_complete`

`oracle/node-classification.md` must classify each graph node as one of:

- `market`;
- `fundamental`;
- `NAV`;
- `hardcoded`;
- `hybrid`.

If a node is ambiguous, the file must mark it as `review_required` or equivalent. Do not accept an unclassified node hidden inside prose.

### `oracle.source_primitive_audit_present`

`oracle/source-primitive-audit.md` must cover every graph leaf/source primitive named in the feed graph or feed probes.

For each source primitive, require this minimum field set:

- source identity: address, source identifier, report name, or explicit unavailable marker;
- source type: Chainlink/Pyth market feed, Curve/DEX TWAP, Pendle factory oracle, ERC4626/NAV, issuer/fundamental source, hardcoded scalar, or another explicit source type;
- timestamp, update time, reporting cadence, heartbeat, or explicit unavailable marker;
- trust, admin, signer, methodology, or source-control note, or explicit unavailable marker;
- raw evidence pointer, artifact path, or explicit reason raw snapshots were not saved.

Primitive-specific requirements:

- DEX/TWAP entries must include liquidity, pool composition, manipulation surface, TWAP window, or explicit unavailable markers.
- Pendle entries must include market/PT/SY identity, TWAP duration or cardinality readiness, and maturity behavior, or explicit unavailable markers.
- ERC4626/NAV entries must include vault asset, exchange-rate source, withdrawal/executability context, or explicit unavailable markers.
- Issuer/fundamental entries must include issuer/reporting cadence, proof scope, signer/admin/source methodology, or explicit unavailable markers.
- Hardcoded scalar entries must include the invariant assumed and what breaks it.

`raw/source-evidence/` must exist. It may be empty only if `source-primitive-audit.md` explicitly says raw snapshots were not saved and gives a reason.

### `oracle.stress_tradeoff_fields`

`oracle/stress-tradeoff-analysis.md` must explicitly address:

- short-term volatility or temporary market dislocation;
- persistent depeg, insolvency, issuer failure, or redemption impairment;
- thin-liquidity manipulation or TWAP lag;
- stale report, stale external feed, or delayed update;
- liquidation feasibility;
- liquidity-cascade risk;
- liquidity-trap risk;
- who bears first loss.

Both `liquidity-cascade` and `liquidity-trap` framing must appear as explicit labels or clearly equivalent headings.

### `oracle.conclusion_quad_present`

Every protocol-fit verdict in `oracle/protocol-fit-memo.md` must expose the four conclusion fields:

- position side;
- token role;
- stress direction;
- loss bearer.

Accept snake-case labels (`position_side`, `token_role`, `stress_direction`, `loss_bearer`) or clear Markdown table labels. A single universal verdict such as `safe`, `unsafe`, `good`, or `bad` fails this check.

If a scope is neutral inventory only, protocol-fit verdicts must be absent or explicitly blocked, and `position_sides` / `token_roles` must be `null` with a reason.

### `oracle.side_specific_verdicts`

Applicability must be deterministic:

- Require every side listed in manifest `position_sides` or `scope.json`.
- Require borrower / Credit Account operator and pool LP / lender rows when either side is in scope for a lending-market run.
- Require liquidator and curator/operator rows for Gearbox unless `scope.json` explicitly marks them `not_in_scope` with a reason.
- Accept `not_in_scope` only when the scope file names why the side is excluded.

### `oracle.gearbox_fields_present`

When any scope has `protocol: Gearbox`, `oracle/protocol-fit-memo.md` must include explicit rows, labels, or `unknown` markers for:

- main feed path;
- reserve feed path;
- safe-pricing rule;
- exit Health Factor implication;
- Liquidation Threshold;
- Liquidation Threshold ramp;
- max leverage implied by Liquidation Threshold;
- staleness and bounds;
- feed swap / reserve / timelock status;
- delayed-withdrawal branch interaction;
- forbidden-token branch interaction;
- issuer-controlled branch interaction;
- PFS chain / token availability status;
- Instance Owner or feed-update authority;
- PFS add/update status when the feed is new, pending, or unavailable.

This check is formal availability/control coverage only. It must not judge whether the Gearbox oracle setup is economically good or bad.

### `oracle.gearbox_parsing_reference_applied`

When protocol is Gearbox, the run must cite or explicitly record applying:

```text
user/references/workflows/oracle-analysis/gearbox-price-feed-parsing.md
```

This is a formal evidence check. It does not judge whether the agent interpreted every feed correctly.

### `oracle.no_top_level_only_verdict`

A final verdict must not rely only on high-level labels such as `External`, `Composite`, `Bounded`, `ERC4626`, `Curve`, `Pendle`, `Balancer`, or `PFS available`. Require child-source detail, primitive classification, formula evidence, and stress framing before a verdict.

## P2 reporting checks

### `oracle.command_evidence_present`

The run-level final verification should include command evidence with:

- working directory;
- command;
- exit code;
- output marker or concise result.

This remains P2 unless the final verification claims deterministic validation passed while no evidence is present.

### `oracle.status_values_known`

Manifest, index, per-scope verification, and final verification statuses should use `pass`, `review_required`, or `blocked`. Unknown status strings are P2 unless they create a root/scope contradiction, in which case use P1.

## Minimal fixture matrix

Use small synthetic fixture folders instead of copying large real runs. Each fixture should contain only the files needed to exercise the check path.

| Fixture | Expected exit | Required finding(s) |
| --- | ---: | --- |
| `oracle-good-minimal` | `0` | none |
| `oracle-bad-missing-manifest-scope-field` | `2` | `oracle.manifest_schema` |
| `oracle-bad-noncanonical-final-verification` | `2` | `oracle.canonical_final_verification_path` |
| `oracle-bad-missing-final-verification` | `2` | `oracle.required_files_present` or `oracle.canonical_final_verification_path` |
| `oracle-bad-root-status-contradiction` | `1` or `2` by final severity policy | `oracle.run_status_reconciles` |
| `oracle-bad-missing-per-scope-file` | `2` | `oracle.required_files_present` |
| `oracle-bad-missing-index-section` | `1` | `oracle.index_contract_sections` |
| `oracle-bad-missing-readme-section` | `1` | `oracle.readme_handoff_sections` |
| `oracle-bad-missing-source-evidence` | `1` or `2` by final severity policy | `oracle.source_primitive_audit_present` |
| `oracle-bad-weak-source-audit` | `1` | `oracle.source_primitive_audit_present` |
| `oracle-bad-missing-formula` | `1` | `oracle.pricing_formula_present` |
| `oracle-bad-side-verdict-fields` | `1` or `2` by final severity policy | `oracle.conclusion_quad_present` |
| `oracle-bad-no-cascade-trap` | `1` | `oracle.stress_tradeoff_fields` |
| `oracle-bad-missing-gearbox-fields` | `1` | `oracle.gearbox_fields_present` |
| `oracle-bad-top-level-label-only` | `1` | `oracle.no_top_level_only_verdict` |

If the future implementer chooses a severity policy that makes a P1 field omission exit `2`, update the expected wrapper assertions consistently. Do not leave raw failing commands in the acceptance block without asserting their expected nonzero exit.

## Exact acceptance command for the implementation slice

Run from `/Users/ilya/Documents/Codex/front-knowledge-base` after implementing M3:

```bash
python3 - <<'PY'
import json
import subprocess
import sys

BASE = "dev/implementation/workflow-harness/fixtures"
VALIDATOR = ["python3", "dev/tools/validate_workflow_run.py", "--workflow", "oracle-analysis", "--format", "json"]

def run_fixture(fixture):
    proc = subprocess.run(
        VALIDATOR + ["--run-root", f"{BASE}/{fixture}"],
        text=True,
        capture_output=True,
    )
    try:
        report = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError((fixture, "invalid json", proc.returncode, proc.stdout, proc.stderr)) from exc
    return proc, report

proc, report = run_fixture("oracle-good-minimal")
assert proc.returncode == 0, ("oracle-good-minimal", proc.returncode, report, proc.stderr)
assert not report.get("findings"), ("oracle-good-minimal", report.get("findings"))

cases = [
    ("oracle-bad-missing-manifest-scope-field", {"oracle.manifest_schema"}),
    ("oracle-bad-noncanonical-final-verification", {"oracle.canonical_final_verification_path"}),
    ("oracle-bad-missing-final-verification", {"oracle.required_files_present", "oracle.canonical_final_verification_path"}),
    ("oracle-bad-root-status-contradiction", {"oracle.run_status_reconciles"}),
    ("oracle-bad-missing-per-scope-file", {"oracle.required_files_present"}),
    ("oracle-bad-missing-index-section", {"oracle.index_contract_sections"}),
    ("oracle-bad-missing-readme-section", {"oracle.readme_handoff_sections"}),
    ("oracle-bad-missing-source-evidence", {"oracle.source_primitive_audit_present"}),
    ("oracle-bad-weak-source-audit", {"oracle.source_primitive_audit_present"}),
    ("oracle-bad-missing-formula", {"oracle.pricing_formula_present"}),
    ("oracle-bad-side-verdict-fields", {"oracle.conclusion_quad_present"}),
    ("oracle-bad-no-cascade-trap", {"oracle.stress_tradeoff_fields"}),
    ("oracle-bad-missing-gearbox-fields", {"oracle.gearbox_fields_present"}),
    ("oracle-bad-top-level-label-only", {"oracle.no_top_level_only_verdict"}),
]

for fixture, expected_any in cases:
    proc, report = run_fixture(fixture)
    assert proc.returncode in (1, 2), (fixture, proc.returncode, report, proc.stderr)
    found = {finding.get("check_id") for finding in report.get("findings", [])}
    assert found & expected_any, (fixture, expected_any, found, report)

print("M3_ORACLE_HARDENED_ACCEPTANCE: PASS")
PY

git diff --check -- dev/tools/validate_workflow_run.py dev/implementation/workflow-harness/fixtures/oracle-*
git status --short -- dev/tools/validate_workflow_run.py dev/implementation/workflow-harness/fixtures/oracle-*
```

## Current hardening-task validation commands

For this planning task only, validate this brief with:

```bash
python3 - <<'PY'
from pathlib import Path
p = Path('dev/implementation/workflow-harness/m3-oracle-checks-hardened.md')
text = p.read_text()
required = [
    'oracle.canonical_final_verification_path',
    'oracle.run_status_reconciles',
    'oracle.index_contract_sections',
    'oracle.readme_handoff_sections',
    'oracle.pricing_formula_present',
    'oracle.source_primitive_audit_present',
    'PFS chain / token availability status',
    'Instance Owner or feed-update authority',
    'oracle-bad-noncanonical-final-verification',
    'oracle-bad-root-status-contradiction',
    'oracle-bad-missing-index-section',
    'oracle-bad-missing-readme-section',
    'oracle-bad-missing-formula',
    'oracle-bad-weak-source-audit',
    'M3_ORACLE_HARDENED_ACCEPTANCE: PASS',
]
missing = [item for item in required if item not in text]
assert not missing, missing
forbidden = 'or another declared run-level ' + 'final verification file'
assert forbidden not in text
assert 'Do not edit workflow contracts' in text
print(f'M3_ORACLE_CHECKS_HARDENED_SELF_CHECK: PASS bytes={len(text.encode())} lines={text.count(chr(10)) + 1}')
PY

git diff --no-index --check /dev/null dev/implementation/workflow-harness/m3-oracle-checks-hardened.md
git status --short -- dev/implementation/workflow-harness/m3-oracle-checks-hardened.md
```

`git diff --no-index --check /dev/null <new-file>` returns exit `1` for a new-file diff even when whitespace is clean; treat absence of whitespace-error output as pass.

## Definition of done for the future implementation slice

- `dev/tools/validate_workflow_run.py` implements the oracle-analysis checks listed above.
- Synthetic oracle fixtures exist only under `dev/implementation/workflow-harness/fixtures/oracle-*`.
- Good oracle fixture exits `0` and has no findings.
- Every required negative oracle fixture is asserted by the acceptance wrapper and produces an expected check ID.
- Canonical `verification/final-oracle-analysis-verification.md` is mandatory and cannot be replaced by an alternate final verification path.
- Root, scope, index, per-scope verification, and final-verification statuses cannot contradict each other.
- `index.md` and `README.md` handoff sections are validated directly.
- Formula evidence is validated in source artifacts, not only in final verification claims.
- Source primitive audits require identity, type, timestamp/cadence, trust/methodology, and primitive-specific evidence or explicit unavailable markers.
- Gearbox runs include PFS availability, Instance Owner/update authority, and PFS add/update status fields or `unknown` markers.
- The implementation does not mutate workflow semantics, runtime docs, prompt text, or asset checks.
- Final handoff reports files changed, commands run, exit codes, and validation output.
