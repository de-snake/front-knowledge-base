# M10 verification — quality-gated Analyze → Propose

Generated: 2026-06-06 12:16:11 UTC
Workspace: `/Users/ilya/Documents/Codex/front-knowledge-base`
Kanban task: `t_4395c3a8`

## Verdict

PASS for the reusable workflow-harness quality-gate path.

The run-workflow usage docs now document deterministic validation, semantic critic gates, the reusable investigation-result taxonomy, and parent proposal-gate statuses. The generalized fixture suite passes, the low-quality semantic form-fill fixture is rejected, `investigated_no_result` and `not_investigated` are distinguished by direct validator reports, and the board-specific Kanban DB was used without switching the global Hermes active board.

This verification does not assess live token economics, oracle correctness, allocation suitability, Preview readiness, Execute readiness, or live external-agent output quality.

## Files and report artifacts

Updated documentation:

- `dev/implementation/workflow-entrypoint/run-workflow-usage.md`

Verification artifact:

- `dev/implementation/workflow-harness/m10-quality-gated-analyze-propose-verification.md`

Generated report artifacts:

- `dev/implementation/workflow-harness/tmp/m10-verification/good-combined/workflow-harness-report.json`
- `dev/implementation/workflow-harness/tmp/m10-verification/good-combined/workflow-harness-verification.md`
- `dev/implementation/workflow-harness/tmp/m10-verification/oracle-valid-no-market-no-route/workflow-harness-report.json`
- `dev/implementation/workflow-harness/tmp/m10-verification/oracle-valid-no-market-no-route/workflow-harness-verification.md`
- `dev/implementation/workflow-harness/tmp/m10-verification/oracle-bad-not-investigated-as-no-result/workflow-harness-report.json`
- `dev/implementation/workflow-harness/tmp/m10-verification/oracle-bad-not-investigated-as-no-result/workflow-harness-verification.md`
- `dev/implementation/workflow-harness/tmp/m10-verification/semantic-low-quality-request.json`
- `dev/implementation/workflow-harness/tmp/m10-verification/semantic-low-quality-report.json`
- `dev/implementation/workflow-harness/tmp/m10-e2e-sample-complete/.workflow/validation/summary.json`
- `dev/implementation/workflow-harness/tmp/m10-e2e-sample-complete/.workflow/validation/summary.md`
- `dev/implementation/workflow-harness/tmp/m10-e2e-sample-complete/.workflow/next-action.json`
- `dev/implementation/workflow-harness/tmp/m10-e2e-sample-complete/.workflow/next-action.md`

## Commands run

### 1. Generalized fixture smoke wrapper

Command:

```bash
python3 dev/tools/run_fixture_checks.py
```

Exit code: `0`

Observed result:

```text
fixture matrix: ran 13, failures 0
evidence ledger schema: ran 5, failures 0
semantic critic runner: ran 3, failures 0
regression eval suite: ran 4, failures 0
workflow entrypoint: exit 0
```

This covers deterministic validator replay, evidence-ledger schema, semantic-critic runner behavior, generalized regression evals, and entrypoint tests.

### 2. Full workflow-harness pytest suite

Command:

```bash
python3 -m pytest dev/tools/workflow_harness/tests -q
```

Exit code: `0`

Observed result:

```text
39 passed in 3.88s
```

### 3. Direct combined Analyze → Propose known-good fixture

Command:

```bash
python3 dev/tools/validate_workflow_run.py \
  --workflow combined-analyze-propose \
  --run-root dev/implementation/workflow-harness/fixtures/good/good-agentic-sample-assets \
  --parent-return agentic-flow/analyze-and-propose.md \
  --format json,markdown \
  --report-dir dev/implementation/workflow-harness/tmp/m10-verification/good-combined
```

Exit code: `0`

Report paths:

- `dev/implementation/workflow-harness/tmp/m10-verification/good-combined/workflow-harness-report.json`
- `dev/implementation/workflow-harness/tmp/m10-verification/good-combined/workflow-harness-verification.md`

Observed report summary:

```text
status=pass
exit_code=0
findings=0
```

### 4. Direct positive `investigated_no_result` fixture

Command:

```bash
python3 dev/tools/validate_workflow_run.py \
  --workflow oracle-analysis \
  --run-root dev/implementation/workflow-harness/fixtures/oracle-valid-no-market-no-route \
  --format json,markdown \
  --report-dir dev/implementation/workflow-harness/tmp/m10-verification/oracle-valid-no-market-no-route \
  --write-verification
```

Exit code: `0`

Report paths:

- `dev/implementation/workflow-harness/tmp/m10-verification/oracle-valid-no-market-no-route/workflow-harness-report.json`
- `dev/implementation/workflow-harness/tmp/m10-verification/oracle-valid-no-market-no-route/workflow-harness-verification.md`

Observed report summary:

```text
status=pass
exit_code=0
findings=0
```

This proves a no-market/no-route conclusion can pass when it is recorded as `investigated_no_result` with the required negative-search evidence bundle.

### 5. Direct negative `not_investigated` fixture

Command:

```bash
python3 dev/tools/validate_workflow_run.py \
  --workflow oracle-analysis \
  --run-root dev/implementation/workflow-harness/fixtures/oracle-bad-not-investigated-as-no-result \
  --format json,markdown \
  --report-dir dev/implementation/workflow-harness/tmp/m10-verification/oracle-bad-not-investigated-as-no-result \
  --write-verification
```

Exit code: `1`

Report paths:

- `dev/implementation/workflow-harness/tmp/m10-verification/oracle-bad-not-investigated-as-no-result/workflow-harness-report.json`
- `dev/implementation/workflow-harness/tmp/m10-verification/oracle-bad-not-investigated-as-no-result/workflow-harness-verification.md`

Observed report summary:

```text
status=review_required
exit_code=1
findings=3
finding_ids:
- oracle.protocol_adapter_no_result_evidence_ledger
- oracle.protocol_adapter_not_investigated_not_no_result
- oracle.protocol_adapter_unknown_requires_state
```

This proves the harness rejects a worker that presents an unsearched or unknown fact as a no-result investigation.

### 6. Direct semantic low-quality form-fill fixture

Command:

```bash
python3 dev/tools/semantic_critic_runner.py \
  --packet dev/implementation/workflow-harness/fixtures/regression-evals/semantic-low-quality-form-fill/packet.json \
  --output dev/implementation/workflow-harness/fixtures/regression-evals/semantic-low-quality-form-fill/stage-output.md \
  --validator-summary dev/implementation/workflow-harness/fixtures/regression-evals/semantic-low-quality-form-fill/validator-summary.json \
  --critic-command "python3 dev/tools/workflow_harness/tests/semantic_fixture_critic_stub.py dev/implementation/workflow-harness/fixtures/regression-evals/semantic-low-quality-form-fill/critic-response.json" \
  --request-out dev/implementation/workflow-harness/tmp/m10-verification/semantic-low-quality-request.json \
  --report-out dev/implementation/workflow-harness/tmp/m10-verification/semantic-low-quality-report.json
```

Exit code: `1`

Report paths:

- `dev/implementation/workflow-harness/tmp/m10-verification/semantic-low-quality-request.json`
- `dev/implementation/workflow-harness/tmp/m10-verification/semantic-low-quality-report.json`

Observed report summary:

```text
status=review_required
findings=1
finding_ids:
- semantic.low_quality_form_fill
```

This proves form-compliant but low-quality stage output can be rejected by the semantic critic path even when deterministic validation is satisfied.

### 7. Entrypoint scaffold and validate path

Scaffold command:

```bash
rm -rf dev/implementation/workflow-harness/tmp/m10-e2e-sample-complete
python3 dev/tools/run_workflow.py analyze-propose \
  --input dev/implementation/workflow-harness/fixtures/entrypoint-inputs/sample-assets-complete.json \
  --run-root dev/implementation/workflow-harness/tmp/m10-e2e-sample-complete \
  --mode scaffold \
  --agent generic \
  --format json
```

Exit code: `0`

Validate command:

```bash
python3 dev/tools/run_workflow.py analyze-propose \
  --input dev/implementation/workflow-harness/fixtures/entrypoint-inputs/sample-assets-complete.json \
  --run-root dev/implementation/workflow-harness/tmp/m10-e2e-sample-complete \
  --mode validate \
  --resume \
  --format json
```

Exit code: `2`

Report paths:

- `dev/implementation/workflow-harness/tmp/m10-e2e-sample-complete/.workflow/validation/summary.json`
- `dev/implementation/workflow-harness/tmp/m10-e2e-sample-complete/.workflow/validation/summary.md`
- `dev/implementation/workflow-harness/tmp/m10-e2e-sample-complete/.workflow/next-action.json`
- `dev/implementation/workflow-harness/tmp/m10-e2e-sample-complete/.workflow/next-action.md`

Observed validation summary:

```text
status=blocked
asset validator exit=2
oracle validator exit=2
combined validator exit=2
finding_counts: P0=28, P1=152, P2=1, total=181
semantic_review.enabled=false
```

This is the expected result for a scaffold-only run with no worker-filled child artifacts: the runner creates the deterministic Analyze → Propose structure, and validation blocks instead of false-passing incomplete output.

### 8. Global Hermes active-board check

Command:

```bash
printf 'HERMES_KANBAN_DB=%s\nHERMES_KANBAN_BOARD=%s\nHERMES_KANBAN_TASK=%s\nHERMES_KANBAN_WORKSPACE=%s\n' "$HERMES_KANBAN_DB" "$HERMES_KANBAN_BOARD" "$HERMES_KANBAN_TASK" "$HERMES_KANBAN_WORKSPACE"
if [ -L "$HOME/.hermes/kanban/current" ]; then
  echo "current_is_symlink=yes"
  readlink "$HOME/.hermes/kanban/current"
elif [ -e "$HOME/.hermes/kanban/current" ]; then
  echo "current_exists_not_symlink"
  file "$HOME/.hermes/kanban/current"
else
  echo "current_absent"
fi
```

Exit code: `0`

Observed result:

```text
HERMES_KANBAN_DB=/Users/ilya/.hermes/kanban/boards/front-kb-workflow-quality-gates/kanban.db
HERMES_KANBAN_BOARD=front-kb-workflow-quality-gates
HERMES_KANBAN_TASK=t_4395c3a8
HERMES_KANBAN_WORKSPACE=/Users/ilya/Documents/Codex/front-knowledge-base
current_exists_not_symlink
/Users/ilya/.hermes/kanban/current: ASCII text
```

Content of `~/.hermes/kanban/current`:

```text
hermes-core-selective-cleanup
```

Conclusion: this task used the board-specific DB `front-kb-workflow-quality-gates`, and the global Hermes active-board selector remained `hermes-core-selective-cleanup`; the board-creation process did not switch the global active board.

## Remaining limitations

- The semantic critic proof here uses the deterministic fixture stub, not a live independent LLM critic.
- The scaffold/validate run intentionally stops at generated packets and empty child artifacts; completing a real user run still requires workers to fill child artifacts before validation can pass.
- The harness gates formal structure, evidence states, semantic usefulness, and proposal readiness. It does not certify market truth, oracle economic safety, allocation quality, Preview readiness, or Execute readiness.
- `semantic_review_status: semantic_review_unavailable` remains non-decision-grade unless the operator explicitly scopes semantic review out.
