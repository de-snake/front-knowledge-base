# Semantic low-quality form-fill fixture

This fixture is a generalized critic seed. The deterministic validator summary passes because file shape is present, while the independent critic must return `semantic.low_quality_form_fill` because the output fills generic fields without evidence-to-decision mapping.

Local replay command:

```bash
python3 dev/tools/semantic_critic_runner.py \
  --packet dev/implementation/workflow-harness/fixtures/regression-evals/semantic-low-quality-form-fill/packet.json \
  --output dev/implementation/workflow-harness/fixtures/regression-evals/semantic-low-quality-form-fill/stage-output.md \
  --validator-summary dev/implementation/workflow-harness/fixtures/regression-evals/semantic-low-quality-form-fill/validator-summary.json \
  --critic-command "python3 dev/tools/workflow_harness/tests/semantic_fixture_critic_stub.py dev/implementation/workflow-harness/fixtures/regression-evals/semantic-low-quality-form-fill/critic-response.json"
```
