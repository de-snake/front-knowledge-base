# M2 verification — asset-investment-diligence harness checks

Run date: 2026-06-06.

Scope: independent verification of the M2 `asset-investment-diligence` validator slice. This review checks formal workflow compliance only. It does not assess token economic quality, oracle correctness, allocation suitability, or whether report conclusions are persuasive.

## Verdict

Pass.

The validator now surfaces every M2 acceptance topic on the external SampleBaseToken/SampleVaultToken asset run:

- missing S2 technical appendix pointer;
- missing S6 quantitative fields;
- broken/nested oracle run directory link as `links.local_paths_resolve`;
- README manifest/handoff gaps;
- index final-verification-status contract gap as `asset.index_contract_sections`;
- S1 transfer restriction / forced-transfer / incident coverage gaps still required by the workflow contract.

The good combined fixture remains clean, and the fixture regression suite remains green.

## Commands run

From `/Users/ilya/Documents/Codex/front-knowledge-base`:

```bash
python3 -m py_compile dev/tools/validate_workflow_run.py
```

Result: exit code 0.

```bash
python3 -m pytest dev/tools/workflow_harness/tests/test_fixtures.py -q
```

Result:

```text
.....                                                                    [100%]
5 passed in 0.46s
```

```bash
python3 dev/tools/validate_workflow_run.py \
  --workflow combined-analyze-propose \
  --run-root dev/implementation/workflow-harness/fixtures/good/good-agentic-sample-assets \
  --parent-return agentic-flow/analyze-and-propose.md \
  --format json
```

Result from the consolidated acceptance rerun: status `pass`, exit code 0, finding count 0.

```bash
python3 dev/tools/validate_workflow_run.py \
  --workflow asset-investment-diligence \
  --run-root dev/implementation/asset-diligence-2026-06-05-sample-base-token-sample-vault-token \
  --format json
```

Result after the M2 blocker fix:

```text
external rc 2
status fail findings 26
links count 1
index count 1
asset.index_contract_sections index.md final verification status index contract sections are missing
links.local_paths_resolve . README.md -> ../oracle-analysis-2026-06-05-sample-base-token-sample-vault-token/: path escapes run root: ../oracle-analysis-2026-06-05-sample-base-token-sample-vault-token/ README.md -> ../oracle-analysis-2026-06-05-sample-base-token-sample-vault-token/: path escapes run root: ../oracle-analysis-2026-06-05-sample-base-token-sample-vault-token/
```

The external run moved from `review_required` to `fail` because the sibling oracle directory reference is a P0 local-path escape. That is acceptable for this known-bad external run and directly satisfies the nested oracle-link acceptance topic.

```bash
git diff --check -- \
  dev/tools/validate_workflow_run.py \
  dev/tools/workflow_harness/tests/test_fixtures.py \
  dev/implementation/workflow-harness/fixtures \
  dev/implementation/workflow-harness/m2-asset-checks-verification.md
```

Result: exit code 0.

## External bad asset run findings checked

Run root:

`dev/implementation/asset-diligence-2026-06-05-sample-base-token-sample-vault-token`

Detected required topics:

- Missing S2 technical appendix pointer: `asset.s2.technical_appendix_pointer_present`.
- Missing S6 quantitative fields: `asset.s6.required_field_present`, `asset.s6.required_field_has_value_state`, `asset.s6.heading_only_false_pass`.
- Broken/nested oracle run directory link: `links.local_paths_resolve` on `../oracle-analysis-2026-06-05-sample-base-token-sample-vault-token/`.
- README manifest / handoff contract missing: `asset.readme_handoff_sections`.
- Missing explicit index final-verification-status section: `asset.index_contract_sections` with `actual=final verification status`.
- Transfer restriction / forced-transfer / incident coverage still required by contract: `asset.s1.required_fact_slot_present` for missing S1 slots.

## Surgical fixes verified

- `dev/tools/validate_workflow_run.py` now treats code-spanned local directory references ending in `/` as run-artifact paths, so sibling run references like `../oracle-analysis-.../` are checked and rejected when they escape the supplied run root.
- `asset.index_contract_sections` now requires an explicit `final verification status` or `final validation status` phrase instead of passing when unrelated `verification` and generic table `Status` text appear elsewhere in `index.md`.

## Files relevant to this verification

- `dev/tools/validate_workflow_run.py`
- `dev/tools/workflow_harness/tests/test_fixtures.py`
- `dev/implementation/workflow-harness/fixtures/fixture-matrix.json`
- `dev/implementation/workflow-harness/m2-asset-checks-verification.md`
