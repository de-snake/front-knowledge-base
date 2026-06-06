# M3 implementation brief — oracle-analysis harness checks

Purpose: define the narrow M3 implementation slice for deterministic oracle-analysis workflow validation. This brief is formal workflow compliance only. It does not assess oracle economic quality, token investment quality, or whether a particular oracle conclusion is correct.

This file is the only mutation for this planning task. The future implementation slice must stay inside the edit boundary below.

## Inputs reviewed

- `CLAUDE.md`.
- `dev/implementation/workflow-harness/hardened-plan.md`.
- `dev/implementation/workflow-harness/plan-review.md`.
- `dev/implementation/workflow-harness/internal-audit.md`.
- `user/references/workflows/oracle-analysis/output-structure.md`.
- `user/references/workflows/oracle-analysis/stage-contracts.md`.
- `user/references/workflows/oracle-analysis/gearbox-price-feed-parsing.md`.
- Gearbox front-knowledge-base runtime workflow placement and formal workflow critic references.

## Slice goal

Add oracle-analysis checks for these formal contract classes:

1. Manifest schema and manifest-to-scope reconciliation.
2. Run-level final verification existence and credibility.
3. Required per-scope folder and file structure.
4. Required source evidence directories and feed probe registry.
5. Side-specific verdict fields.
6. Liquidity-cascade and liquidity-trap stress framing.
7. Gearbox-required protocol-fit fields.
8. Source primitive audit coverage.
9. No conclusion that stops at a top-level oracle label.

## Exact files to edit in the future implementation slice

Required code edit:

- `dev/tools/validate_workflow_run.py`

Optional fixture metadata edits, only if needed to prove the checks:

- `dev/implementation/workflow-harness/fixtures/oracle-good-minimal/**`
- `dev/implementation/workflow-harness/fixtures/oracle-bad-missing-manifest-scope-field/**`
- `dev/implementation/workflow-harness/fixtures/oracle-bad-missing-final-verification/**`
- `dev/implementation/workflow-harness/fixtures/oracle-bad-missing-per-scope-file/**`
- `dev/implementation/workflow-harness/fixtures/oracle-bad-missing-source-evidence/**`
- `dev/implementation/workflow-harness/fixtures/oracle-bad-side-verdict-fields/**`
- `dev/implementation/workflow-harness/fixtures/oracle-bad-no-cascade-trap/**`
- `dev/implementation/workflow-harness/fixtures/oracle-bad-missing-gearbox-fields/**`
- `dev/implementation/workflow-harness/fixtures/oracle-bad-top-level-label-only/**`

Do not edit workflow contracts, prompt files, docs navigation, `CLAUDE.md`, or asset-investment-diligence checks in this slice.

## Validator behavior

### CLI scope

The M3 code path should run when the validator is called with:

```bash
python3 dev/tools/validate_workflow_run.py \
  --workflow oracle-analysis \
  --run-root <run-root> \
  --format json
```

The report should stay compact and evidence-based:

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

Exit-code policy:

- `0` when no findings remain.
- `1` when only P1/P2 review findings remain.
- `2` when any P0 structural blocker remains.

### P0 structural checks

#### `oracle.manifest_schema`

Parse `<run-root>/run-manifest.json` and require:

- `workflow_id` equals `oracle-analysis-v1`.
- `run_id` is present.
- `run_artifact_root` is present and normalizes to the supplied `--run-root` or an explicitly accepted workspace-relative equivalent.
- `scopes` is a non-empty list unless the run is explicitly marked blocked before scope discovery.
- `final_index` is present and resolves to an existing `index.md` under the run root.
- `final_verification` is present and resolves to `verification/final-oracle-analysis-verification.md` or another declared run-level final verification file under the run root.

Each `scopes[]` entry must include:

- `scope_id`.
- `scope_slug`.
- `scope_type` with value `token` or `pt_market`.
- `chain`.
- `asset_symbol`.
- `asset_address` or an explicit `null` with a blocker reason.
- `protocol`.
- `position_sides` as a list, or explicit `null` only for neutral inventory runs that stop before protocol-fit verdicts.
- `token_roles` as a list, or explicit `null` only for neutral inventory runs that stop before protocol-fit verdicts.
- `artifact_dir`.
- `status` with value `pass`, `review_required`, or `blocked`.

#### `oracle.manifest_entry_reconciles_scope`

For each manifest scope:

- `artifact_dir` must resolve under the run root and must not be absolute or parent-escaping.
- `artifact_dir` must match `tokens/<scope_slug>` for `scope_type: token`.
- `artifact_dir` must match `pt-markets/<scope_slug>` for `scope_type: pt_market`.
- `<artifact_dir>/scope.json` must exist and parse as JSON.
- `scope.json` identity fields must reconcile with the manifest entry: scope id or slug, chain, protocol, asset symbol, asset address when known, position sides, token roles, and status.

#### `oracle.required_files_present`

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

### P1 field-level checks

#### `oracle.final_verification_credibility`

The run-level final verification file must do more than claim broad headings or file existence. It must contain explicit evidence that checks were run for:

- required root files;
- required per-scope files;
- manifest paths and declared artifact paths;
- graph leaf source primitive audits;
- node classification;
- pricing formula presence;
- staleness, bounds, timestamps, or explicit unavailable markers;
- protocol-fit fields;
- side-specific conclusion fields;
- Gearbox price-feed parsing reference when protocol is Gearbox;
- terminology or diff validation evidence.

Accept a Markdown checklist/table only if it names concrete check subjects. Prefer a JSON fenced block or frontmatter with command evidence, but do not require a new artifact type in this slice.

#### `oracle.feed_graph_recursive`

`oracle/feed-graph.md` must identify the top-level feed and either:

- list child feeds/source primitives for every non-leaf node; or
- provide an explicit no-child explanation for a true leaf.

This check should fail when the run stops at top-level labels such as `External`, `Composite`, `Bounded`, `ERC4626`, `Pendle`, `Curve`, or `Balancer` without child feed detail or a formula.

#### `oracle.feed_probes_json_valid`

`raw/feed-probes.json` must parse as JSON and contain a registry of probed nodes, source identifiers, or explicit unavailable markers. Missing or invalid JSON is P0 when the file is absent and P1 when the file exists but omits node/source coverage.

#### `oracle.node_classification_complete`

`oracle/node-classification.md` must classify each graph node as one of:

- `market`;
- `fundamental`;
- `NAV`;
- `hardcoded`;
- `hybrid`.

If a node is ambiguous, the file must mark it as `review_required` or equivalent. Do not accept an unclassified node hidden inside prose.

#### `oracle.source_primitive_audit_present`

`oracle/source-primitive-audit.md` must cover every graph leaf/source primitive named in the feed graph or feed probes. For each source primitive, require at least one concrete evidence marker:

- source address or identifier;
- source type;
- update timestamp, reporting cadence, or explicit unavailable marker;
- trust/admin/source-methodology note;
- artifact path or saved raw evidence pointer.

`raw/source-evidence/` must exist. It may be empty only if `source-primitive-audit.md` explicitly says raw snapshots were not saved and gives a reason.

#### `oracle.stress_tradeoff_fields`

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

#### `oracle.conclusion_quad_present`

Every protocol-fit verdict in `oracle/protocol-fit-memo.md` must expose the four conclusion fields:

- position side;
- token role;
- stress direction;
- loss bearer.

Accept snake-case labels (`position_side`, `token_role`, `stress_direction`, `loss_bearer`) or clear Markdown table labels. A single universal verdict such as `safe`, `unsafe`, `good`, or `bad` fails this check.

If a scope is neutral inventory only, protocol-fit verdicts must be absent or explicitly blocked, and `position_sides` / `token_roles` must be `null` with a reason.

#### `oracle.side_specific_verdicts`

When relevant to the market design, `oracle/protocol-fit-memo.md` must split outcomes for:

- Borrower / Credit Account operator.
- pool LP / lender.
- Liquidator.
- curator/operator.

It is acceptable to mark liquidator or curator/operator as `not_in_scope` only when the scope file explains why.

#### `oracle.gearbox_fields_present`

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
- issuer-controlled branch interaction.

#### `oracle.gearbox_parsing_reference_applied`

When protocol is Gearbox, the run must cite or explicitly record applying:

```text
user/references/workflows/oracle-analysis/gearbox-price-feed-parsing.md
```

This is a formal evidence check. It does not judge whether the agent interpreted every feed correctly.

#### `oracle.no_top_level_only_verdict`

A final verdict must not rely only on high-level labels such as `External`, `Composite`, `Bounded`, `ERC4626`, `Curve`, `Pendle`, `Balancer`, or `PFS available`. Require child-source detail, primitive classification, and stress framing before a verdict.

### P2 reporting checks

#### `oracle.command_evidence_present`

The run-level final verification should include command evidence with:

- working directory;
- command;
- exit code;
- output marker or concise result.

This remains P2 unless the final verification claims deterministic validation passed while no evidence is present.

#### `oracle.status_values_known`

Manifest, index, per-scope verification, and final verification statuses should use `pass`, `review_required`, or `blocked`. Unknown status strings are P2 unless they create a root/scope contradiction, in which case use P1.

## Minimal fixture matrix

Use small synthetic fixture folders instead of copying large real runs. Each fixture should contain only the files needed to exercise the check path.

| Fixture | Expected exit | Required finding(s) |
| --- | ---: | --- |
| `oracle-good-minimal` | `0` | none |
| `oracle-bad-missing-manifest-scope-field` | `2` | `oracle.manifest_schema` |
| `oracle-bad-missing-final-verification` | `2` | `oracle.required_files_present` or `oracle.final_verification_credibility` |
| `oracle-bad-missing-per-scope-file` | `2` | `oracle.required_files_present` |
| `oracle-bad-missing-source-evidence` | `1` or `2` by final severity policy | `oracle.source_primitive_audit_present` |
| `oracle-bad-side-verdict-fields` | `1` or `2` by final severity policy | `oracle.conclusion_quad_present` |
| `oracle-bad-no-cascade-trap` | `1` | `oracle.stress_tradeoff_fields` |
| `oracle-bad-missing-gearbox-fields` | `1` | `oracle.gearbox_fields_present` |
| `oracle-bad-top-level-label-only` | `1` | `oracle.no_top_level_only_verdict` |

If the future implementer chooses a severity policy that makes a P1 field omission exit `2`, update the expected wrapper assertions consistently. Do not leave raw failing commands in the acceptance block without asserting their expected nonzero exit.

## Acceptance commands for the implementation slice

Run from `/Users/ilya/Documents/Codex/front-knowledge-base`.

Positive fixture:

```bash
python3 dev/tools/validate_workflow_run.py \
  --workflow oracle-analysis \
  --run-root dev/implementation/workflow-harness/fixtures/oracle-good-minimal \
  --format json
```

Assert required negative fixtures:

```bash
python3 - <<'PY'
import json
import subprocess

cases = [
    ("oracle-bad-missing-manifest-scope-field", {"oracle.manifest_schema"}),
    ("oracle-bad-missing-final-verification", {"oracle.required_files_present", "oracle.final_verification_credibility"}),
    ("oracle-bad-missing-per-scope-file", {"oracle.required_files_present"}),
    ("oracle-bad-missing-source-evidence", {"oracle.source_primitive_audit_present"}),
    ("oracle-bad-side-verdict-fields", {"oracle.conclusion_quad_present"}),
    ("oracle-bad-no-cascade-trap", {"oracle.stress_tradeoff_fields"}),
    ("oracle-bad-missing-gearbox-fields", {"oracle.gearbox_fields_present"}),
    ("oracle-bad-top-level-label-only", {"oracle.no_top_level_only_verdict"}),
]

for fixture, expected_any in cases:
    proc = subprocess.run(
        [
            "python3",
            "dev/tools/validate_workflow_run.py",
            "--workflow",
            "oracle-analysis",
            "--run-root",
            f"dev/implementation/workflow-harness/fixtures/{fixture}",
            "--format",
            "json",
        ],
        text=True,
        capture_output=True,
    )
    assert proc.returncode in (1, 2), (fixture, proc.returncode, proc.stdout, proc.stderr)
    report = json.loads(proc.stdout)
    found = {finding["check_id"] for finding in report.get("findings", [])}
    assert found & expected_any, (fixture, expected_any, found, proc.stdout)
print("M3_ORACLE_NEGATIVE_FIXTURES: PASS")
PY
```

Diff and touched-path checks:

```bash
git diff --check -- dev/tools/validate_workflow_run.py dev/implementation/workflow-harness/fixtures/oracle-*
git status --short -- dev/tools/validate_workflow_run.py dev/implementation/workflow-harness/fixtures/oracle-*
```

## Current planning-task validation commands

For this planning task only, validate the new brief with:

```bash
python3 - <<'PY'
from pathlib import Path
p = Path('dev/implementation/workflow-harness/m3-oracle-checks-plan.md')
text = p.read_text()
required = [
    '## Exact files to edit in the future implementation slice',
    'oracle.manifest_schema',
    'oracle.required_files_present',
    'oracle.final_verification_credibility',
    'oracle.conclusion_quad_present',
    'oracle.stress_tradeoff_fields',
    'oracle.gearbox_fields_present',
    'oracle.no_top_level_only_verdict',
    '## Acceptance commands for the implementation slice',
]
missing = [item for item in required if item not in text]
assert not missing, missing
assert 'dev/tools/validate_workflow_run.py' in text
assert 'Do not edit workflow contracts' in text
print(f'M3_ORACLE_CHECKS_PLAN_SELF_CHECK: PASS bytes={len(text.encode())} lines={text.count(chr(10)) + 1}')
PY

git diff --check -- dev/implementation/workflow-harness/m3-oracle-checks-plan.md
git status --short -- dev/implementation/workflow-harness/m3-oracle-checks-plan.md
```

## Definition of done for the future implementation slice

- `dev/tools/validate_workflow_run.py` implements the oracle-analysis checks listed above.
- Optional synthetic oracle fixtures exist only under `dev/implementation/workflow-harness/fixtures/oracle-*`.
- Good oracle fixture exits `0`.
- Every required negative oracle fixture is asserted by an acceptance wrapper and produces an expected check ID.
- The implementation does not mutate workflow semantics, runtime docs, prompt text, or asset checks.
- Final handoff reports files changed, commands run, exit codes, and validation output.
