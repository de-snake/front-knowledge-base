# Analyze → Propose parent return

## Stage status

- Discover: complete by user premise
- Analyze: complete
- Propose: ready for preview
- Preview: ready
- Execute: ready
- Monitor: not started

## Status block

This malformed fixture intentionally includes a status block that requests more inputs while the stage table incorrectly claims Preview and Execute readiness.

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
    "status": "ready"
  },
  "preview_gate": {
    "status": "ready"
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
    "Execute": "ready",
    "Monitor": "not started",
    "Preview": "ready",
    "Propose": "ready for preview"
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
