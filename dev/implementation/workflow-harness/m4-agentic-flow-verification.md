# M4 verification — combined post-Discover Analyze → Propose flow harness

Task: independently verify M4 without implementing new features.

Scope: formal workflow compliance only. This verification does not assess token economics, oracle quality, allocation suitability, or whether any asset should be used.

## Verdict

PASS.

Acceptance is satisfied:

1. The combined validator checks a parent run folder with sibling `asset-investment-diligence/`, sibling `oracle-analysis/`, and `agentic-flow/analyze-and-propose.md`.
2. Split external child roots fail the combined-flow check when they are not wrapped by a parent flow artifact.
3. Asset and oracle stage prompts require explicit `null` / `not_in_scope` fields and prohibit handwaved final verification.

## Files changed by this verification task

- `dev/implementation/workflow-harness/m4-agentic-flow-verification.md`

No validator, fixture, or prompt implementation files were edited during this verification task.

## Evidence inspected

- `CLAUDE.md` was read first for the vault contract and validation constraints.
- Parent fixture physical shape was checked:
  - `dev/implementation/workflow-harness/fixtures/good/good-agentic-sample-assets/asset-investment-diligence/verification/workflow-harness-report.json`
  - `dev/implementation/workflow-harness/fixtures/good/good-agentic-sample-assets/oracle-analysis/verification/workflow-harness-report.json`
  - `dev/implementation/workflow-harness/fixtures/good/good-agentic-sample-assets/agentic-flow/analyze-and-propose.md`
- Parent handoff declares all six stages and links both child reports:
  - `Discover: complete by user premise`
  - `Analyze: complete`
  - `Propose: ready for preview`
  - `Preview: blocked`
  - `Execute: blocked`
  - `Monitor: not started`

## Commands and results

### 1. Validator syntax

Command:

```bash
python3 -m py_compile dev/tools/validate_workflow_run.py
```

Result:

```text
exit 0
```

### 2. Wrapped parent combined-flow fixture

Command:

```bash
python3 dev/tools/validate_workflow_run.py --workflow combined-analyze-propose --run-root dev/implementation/workflow-harness/fixtures/good/good-agentic-sample-assets --parent-return agentic-flow/analyze-and-propose.md --format json
```

Result:

```text
exit 0
status: pass
summary: P0=0, P1=0, P2=0, checks_failed=0, checks_passed=22, checks_skipped=1, files_checked=8, json_files_parsed=2
findings: []
```

Interpretation: the validator accepts a valid parent run root containing sibling asset/oracle child reports and the parent `agentic-flow/analyze-and-propose.md` artifact.

### 3. External asset split run without parent wrapper

Command:

```bash
python3 dev/tools/validate_workflow_run.py --workflow combined-analyze-propose --run-root dev/implementation/asset-diligence-2026-06-05-sample-base-token-sample-vault-token --format json
```

Result:

```text
exit 2
status: fail
summary: P0=5, P1=0, P2=0, checks_failed=5, checks_passed=3, checks_skipped=1, json_files_parsed=0
findings:
- flow.child_asset_root_exists
- flow.child_asset_report_json_valid
- flow.child_oracle_root_exists
- flow.child_oracle_report_json_valid
- flow.propose_handoff_exists
```

Interpretation: an asset child run root alone is not accepted as a combined Analyze → Propose parent run.

### 4. External oracle split run without parent wrapper

Command:

```bash
python3 dev/tools/validate_workflow_run.py --workflow combined-analyze-propose --run-root dev/implementation/oracle-analysis-2026-06-05-sample-base-token-sample-vault-token --format json
```

Result:

```text
exit 2
status: fail
summary: P0=5, P1=0, P2=0, checks_failed=5, checks_passed=3, checks_skipped=1, json_files_parsed=0
findings:
- flow.child_asset_root_exists
- flow.child_asset_report_json_valid
- flow.child_oracle_root_exists
- flow.child_oracle_report_json_valid
- flow.propose_handoff_exists
```

Interpretation: an oracle child run root alone is not accepted as a combined Analyze → Propose parent run.

### 5. Fixture regression suite

Command:

```bash
python3 -m pytest dev/tools/workflow_harness/tests/test_fixtures.py -q
```

Result:

```text
exit 0
.....                                                                    [100%]
5 passed in 0.62s
```

The regression suite covers the combined good fixture and bad combined fixtures including missing parent handoff, malformed parent-return status, missing parent-return artifact, child failure propagation, relative-link failure, and unsupported readiness overclaim.

### 6. Prompt contract scan

The prompt scan checked both prompt files for the required stage-worker return fields:

- `status`
- `run_artifact_root`
- `artifact_paths`
- `verification_path`
- `final_verification`
- `workflow_harness_report`
- `blockers`
- `blocked_scopes`
- `review_required_scopes`
- `dominant_blockers`
- `live_input_blockers`
- `preview_execute_relevance`
- `not_in_scope`
- `null_fields`
- `commands_run`

Files checked:

- `user/references/workflows/asset-investment-diligence/subagent-prompts.md`
- `user/references/workflows/oracle-analysis/subagent-prompts.md`

Result:

```text
asset prompt: missing_terms=[], has explicit null=True, has not_in_scope=True, has no-handwave-final-verification=True
oracle prompt: missing_terms=[], has explicit null=True, has not_in_scope=True, has no-handwave-final-verification=True
```

The prompt text explicitly says to use `null` for unknown values, use `not_in_scope` for non-applicable fields, and not handwave final verification without a concrete artifact, command, or blocker.

## Acceptance mapping

| Acceptance requirement | Evidence | Result |
| --- | --- | --- |
| Validator can check parent run with sibling asset/oracle roots and `agentic-flow/analyze-and-propose.md` | Command 2 exited 0 with `status: pass`; fixture contains both child report JSON files and parent handoff | PASS |
| External split runs fail combined-flow check unless wrapped by parent flow artifact | Commands 3 and 4 exited 2 with missing child-root/report and parent-handoff P0 findings; Command 2 shows the wrapped parent passes | PASS |
| Prompts require explicit null/not_in_scope and no handwaved final verification | Command 6 prompt scan found all required terms in both prompt files and the explicit no-handwave instruction | PASS |

## Notes

- The good parent fixture declares `Propose: ready for preview` while `Preview` and `Execute` remain `blocked`; this is accepted because the fixture declares no unresolved gates and does not recommend execution.
- The bad split-root checks intentionally fail at structural P0 level before any economic or oracle-quality assessment.
- Verification was limited to the M4 acceptance surface and fixture regression suite; no implementation changes were made.
