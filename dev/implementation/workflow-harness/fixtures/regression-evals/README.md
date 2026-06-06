# Quality-gate regression evals

This directory stores the M9 regression seed suite for generalized workflow quality gates. The fixtures are synthetic and assert durable failure modes, not live token recommendations or asset-specific policy.

## Local replay commands

Run the no-pytest smoke wrapper:

```bash
python3 dev/tools/run_fixture_checks.py
```

Run the full pytest suite:

```bash
python3 -m pytest dev/tools/workflow_harness/tests -q
```

Replay the low-quality semantic form-fill critic fixture directly:

```bash
python3 dev/tools/semantic_critic_runner.py \
  --packet dev/implementation/workflow-harness/fixtures/regression-evals/semantic-low-quality-form-fill/packet.json \
  --output dev/implementation/workflow-harness/fixtures/regression-evals/semantic-low-quality-form-fill/stage-output.md \
  --validator-summary dev/implementation/workflow-harness/fixtures/regression-evals/semantic-low-quality-form-fill/validator-summary.json \
  --critic-command "python3 dev/tools/workflow_harness/tests/semantic_fixture_critic_stub.py dev/implementation/workflow-harness/fixtures/regression-evals/semantic-low-quality-form-fill/critic-response.json"
```

## Suite files

- `quality-gate-regression-suite.json` is the canonical eval manifest. It links deterministic validator cases, semantic critic cases, and the replay seed policy.
- `latest-quality-gate-seed.json` is the compact seed for replaying the latest suite without encoding token-specific remediation policy.
- `semantic-low-quality-form-fill/` contains a deterministic semantic critic fixture where the formal validator summary passes but the critic returns `semantic.low_quality_form_fill`.

## Covered generalized modes

- Well-investigated positive facts with replayable raw evidence.
- `investigated_no_result` facts with adequate negative evidence.
- `not_investigated` facts that masquerade as unknown/no-result states.
- Protocol adapter no-market/no-route conclusions after a valid negative search.
- Low-quality semantic form-fill artifacts that satisfy headings but omit decision-grade evidence mapping.
- Quantitative Analyze scenario fallback versus empty skipped calculations.
- Parent `request_more_inputs` proposal gates with actionable blocker acceptance criteria.
