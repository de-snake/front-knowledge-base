# Final oracle verification

Status: review_required.

Validator command: `python3 dev/tools/validate_workflow_run.py --workflow oracle-analysis --run-root dev/implementation/workflow-harness/fixtures/oracle-valid-no-market-no-route --format json`.

The no-market/no-route proof is deliberately synthetic and generalized. It proves that the Gearbox protocol adapter accepts `investigated_no_result` only when registry, API/contract, network, and raw evidence-path proof classes are present. It does not authorize Preview or Execute.
