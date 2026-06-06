# M3 verification — oracle-analysis harness checks

Result: PASS.

Scope: formal workflow-harness compliance only. This verification does not assess oracle quality, token economics, allocation suitability, or whether any oracle conclusion is substantively correct.

Workspace: `/Users/ilya/Documents/Codex/front-knowledge-base`.

Verification timestamp: `2026-06-05 21:16:49 UTC`.

## Files changed

- `dev/implementation/workflow-harness/m3-oracle-checks-verification.md` — this verification record.

No validator, fixture, workflow-contract, or runtime documentation files were edited.

## Commands and results

### 1. Validator syntax check

Command:

```bash
python3 -m py_compile dev/tools/validate_workflow_run.py
```

Result: exit `0`.

### 2. Direct oracle-analysis fixture matrix

Command shape:

```bash
python3 - <<'PY'
# Runs dev/tools/validate_workflow_run.py --workflow oracle-analysis --format json
# against oracle-good-minimal and each oracle-bad-* fixture below.
# Assertion reads finding["id"] with finding["check_id"] fallback because
# the current report schema emits finding ids as `id`.
PY
```

Result: exit `0`.

Output:

```text
oracle-good-minimal: exit=0 status=pass findings=0
oracle-bad-missing-manifest-scope-field: exit=2 status=fail matched=['oracle.manifest_schema']
oracle-bad-noncanonical-final-verification: exit=2 status=fail matched=['oracle.canonical_final_verification_path']
oracle-bad-missing-final-verification: exit=2 status=fail matched=['oracle.required_files_present']
oracle-bad-root-status-contradiction: exit=1 status=review_required matched=['oracle.run_status_reconciles']
oracle-bad-missing-per-scope-file: exit=2 status=fail matched=['oracle.required_files_present']
oracle-bad-missing-index-section: exit=1 status=review_required matched=['oracle.index_contract_sections']
oracle-bad-missing-readme-section: exit=1 status=review_required matched=['oracle.readme_handoff_sections']
oracle-bad-missing-source-evidence: exit=1 status=review_required matched=['oracle.source_primitive_audit_present']
oracle-bad-weak-source-audit: exit=1 status=review_required matched=['oracle.source_primitive_audit_present']
oracle-bad-missing-formula: exit=1 status=review_required matched=['oracle.pricing_formula_present']
oracle-bad-side-verdict-fields: exit=1 status=review_required matched=['oracle.conclusion_quad_present']
oracle-bad-no-cascade-trap: exit=1 status=review_required matched=['oracle.stress_tradeoff_fields']
oracle-bad-missing-gearbox-fields: exit=1 status=review_required matched=['oracle.gearbox_fields_present']
oracle-bad-top-level-label-only: exit=1 status=review_required matched=['oracle.no_top_level_only_verdict']
oracle-bad-broken-source-evidence-link: exit=1 status=review_required matched=['oracle.source_primitive_audit_present']
M3_ORACLE_HARDENED_ACCEPTANCE_PLUS_LINK: PASS
```

Interpretation:

- Known good oracle fixture passes with zero findings.
- Missing final verification is rejected by `oracle.required_files_present`.
- Noncanonical final verification path is rejected by `oracle.canonical_final_verification_path`.
- Missing explicit verdict fields are rejected by `oracle.conclusion_quad_present`.
- Missing cascade/trap terms are rejected by `oracle.stress_tradeoff_fields`.
- Broken source-audit raw evidence pointer is rejected by `oracle.source_primitive_audit_present` with a missing `raw/source-evidence/...` pointer.
- Missing Gearbox protocol-fit fields are rejected by `oracle.gearbox_fields_present`.

### 3. Task-specific detail probes

Command:

```bash
python3 - <<'PY'
# Prints selected findings from the targeted negative fixtures.
PY
```

Result: exit `0`.

Output:

```text
oracle-bad-missing-gearbox-fields: exit=1 status=review_required
  id= oracle.gearbox_fields_present
  field= gearbox_protocol_fit_fields
  expected= Gearbox PFS, Instance Owner, add/update, LT, safe-pricing, feed-swap/timelock, staleness/bounds, and delayed-withdrawal/forbidden-token/issuer branch fields covered
  actual= ramp, timestamp, delayed-withdrawal, forbidden-token, issuer-controlled
oracle-bad-no-cascade-trap: exit=1 status=review_required
  id= oracle.stress_tradeoff_fields
  field= cascade_vs_trap
  expected= liquidity-cascade and liquidity-trap tradeoff branches covered
  actual= liquidity-cascade, liquidity-trap
oracle-bad-side-verdict-fields: exit=1 status=review_required
  id= oracle.conclusion_quad_present
  field= side_specific_verdict_matrix
  expected= position_side, token_role, stress_direction, and loss_bearer named for each relevant side
  actual= position_side; token_role; stress_direction; loss_bearer; missing side verdicts: credit_account_borrower, liquidator, curator_operator
  id= oracle.gearbox_fields_present
  field= gearbox_protocol_fit_fields
  expected= Gearbox PFS, Instance Owner, add/update, LT, safe-pricing, feed-swap/timelock, staleness/bounds, and delayed-withdrawal/forbidden-token/issuer branch fields covered
  actual= main feed path, reserve feed path, safe-pricing, exit health factor, liquidation threshold, ramp, max leverage, staleness, bounds, timestamp, feed swap, timelock, delayed-withdrawal, forbidden-token, issuer-controlled, pfs, instance owner, add/update
  id= oracle.no_top_level_only_verdict
  field= feed_depth
  expected= verdict reaches child/source primitives rather than stopping at a top-level feed label
  actual= top-level feed label only
oracle-bad-missing-readme-section: exit=1 status=review_required
  id= oracle.readme_handoff_sections
  field= sections
  expected= README includes operator handoff sections
  actual= final validation status
oracle-bad-broken-source-evidence-link: exit=1 status=review_required
  id= oracle.source_primitive_audit_present
  field= raw_evidence_pointer
  expected= all raw/source-evidence/... pointers resolve within the scope folder
  actual= raw/source-evidence/missing-sample-token-a-feed.md
```

Interpretation:

- The current validator contract still requires delayed-withdrawal and forbidden-token coverage through `oracle.gearbox_fields_present`; the negative fixture fails and reports both missing fields explicitly.
- The broken sibling/source-evidence pointer fails as a formal raw evidence pointer error, not as an economic or oracle-quality judgement.

### 4. README manifest pointer negative smoke

Command:

```bash
python3 - <<'PY'
# Copies oracle-good-minimal to a temporary directory, removes the README Manifest
# section and `run-manifest.json` pointer, then validates the temporary copy.
PY
```

Result: exit `0` for the assertion wrapper. Inner validator result:

```text
README_MANIFEST_POINTER_NEGATIVE: PASS
exit=1 status=review_required id=oracle.readme_handoff_sections actual=manifest, run-manifest.json
```

Interpretation: the validator rejects a README that omits the manifest pointer and `run-manifest.json` reference.

### 5. Combined fixture regression suite

Command:

```bash
python3 -m pytest dev/tools/workflow_harness/tests/test_fixtures.py -q
```

Result: exit `0`.

Output:

```text
.....                                                                    [100%]
5 passed in 0.55s
```

### 6. No economic/oracle-quality judgement guard

Command:

```bash
python3 - <<'PY'
from pathlib import Path
checks = {
    'dev/tools/validate_workflow_run.py': [
        'does not assess token economics, oracle quality, or',
        'investment suitability',
    ],
    'dev/tools/workflow_harness/tests/test_fixtures.py': [
        'do not',
        'judge token quality, oracle quality, allocation suitability, or execution merit',
    ],
}
for path, phrases in checks.items():
    text = Path(path).read_text()
    missing = [p for p in phrases if p not in text]
    assert not missing, (path, missing)
    print(f'{path}: no-economic-judgement guard phrases present')
print('NO_ECONOMIC_QUALITY_JUDGEMENT_GUARD: PASS')
PY
```

Result: exit `0`.

Output:

```text
dev/tools/validate_workflow_run.py: no-economic-judgement guard phrases present
dev/tools/workflow_harness/tests/test_fixtures.py: no-economic-judgement guard phrases present
NO_ECONOMIC_QUALITY_JUDGEMENT_GUARD: PASS
```

### 7. Diff whitespace check for implementation slice paths

Command:

```bash
git diff --check -- dev/tools/validate_workflow_run.py dev/implementation/workflow-harness/fixtures/oracle-*
```

Result: exit `0`.

### 8. Full diff whitespace check

Command:

```bash
git diff --check
```

Result: exit `0`.

## Acceptance conclusion

Acceptance is satisfied.

The validator fails the required external bad oracle cases for formal compliance gaps, including missing final verification, missing side-specific verdict fields, missing cascade/trap framing, broken source-audit raw evidence pointer, README manifest pointer omission, and delayed-withdrawal/forbidden-token omissions while those fields remain in the validator contract.

The known good direct oracle fixture passes with zero findings.

No oracle quality or economic judgement was made in this verification.
