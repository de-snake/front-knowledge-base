# Analyze → Propose parent return

## Stage status

- Discover: complete by user premise
- Analyze: complete
- Propose: request_more_inputs
- Preview: blocked
- Execute: blocked
- Monitor: not started

## Status block

Formal validation is pending this parent validator; semantic review was not run in this fixture; workflow decision is review_required because the child reports must be reconciled before parent proposal readiness. The proposal is a request_more_inputs gate, not a decision-grade pass.

## Analyze artifacts

- asset child report: [asset-investment-diligence/verification/workflow-harness-report.json](../asset-investment-diligence/verification/workflow-harness-report.json)
- oracle child report: [oracle-analysis/verification/workflow-harness-report.json](../oracle-analysis/verification/workflow-harness-report.json)

## Requested next checks

- asset/oracle workflow status reconciliation — rerun or update child reports with explicit workflow_decision/status_block metadata before treating the parent proposal as ready.

```json
{
  "analyze_artifacts": {
    "asset_child_report": "asset-investment-diligence/verification/workflow-harness-report.json",
    "oracle_child_report": "oracle-analysis/verification/workflow-harness-report.json"
  },
  "execute_gate": {
    "status": "blocked"
  },
  "preview_gate": {
    "status": "blocked"
  },
  "proposal_gate": {
    "blockers": [
      {
        "acceptance_criteria": "Child report statuses and workflow_decision/status_block metadata are reconciled before Preview.",
        "method": "Rerun the affected child validators and import their current workflow reports.",
        "owner": "parent_flow_owner",
        "requested_input": "child workflow status reconciliation",
        "source": "child.workflow_decision_status",
        "status": "review_required"
      }
    ],
    "explanation": "Child workflow status must be reconciled before a parent proposal can be ready for preview.",
    "status": "review_required",
    "type": "request_more_inputs"
  },
  "schema_version": "agentic-analyze-propose-v1",
  "stage_status": {
    "Analyze": "complete",
    "Discover": "complete by user premise",
    "Execute": "blocked",
    "Monitor": "not started",
    "Preview": "blocked",
    "Propose": "request_more_inputs"
  },
  "status_block": {
    "explanation": "Formal validation checks artifact structure; semantic review and child workflow decisions determine proposal readiness.",
    "formal_validation_status": "pending_parent_validator",
    "proposal_gate": {
      "blockers": [
        {
          "acceptance_criteria": "Child report statuses and workflow_decision/status_block metadata are reconciled before Preview.",
          "method": "Rerun the affected child validators and import their current workflow reports.",
          "owner": "parent_flow_owner",
          "requested_input": "child workflow status reconciliation",
          "source": "child.workflow_decision_status",
          "status": "review_required"
        }
      ],
      "explanation": "Child workflow status must be reconciled before a parent proposal can be ready for preview.",
      "status": "review_required",
      "type": "request_more_inputs"
    },
    "semantic_review_status": "not_run",
    "workflow_decision_status": "review_required"
  },
  "unresolved_gates": [
    {
      "gate": "child.workflow_decision_status",
      "requested_input": "child workflow status reconciliation"
    }
  ]
}
```

## Broken link fixture

- [missing local artifact](agentic-flow/missing-local-artifact.md)
