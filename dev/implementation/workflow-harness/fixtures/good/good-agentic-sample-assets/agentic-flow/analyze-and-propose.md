# Analyze → Propose parent return

## Stage status

- Discover: complete by user premise
- Analyze: complete
- Propose: request_more_inputs
- Preview: blocked
- Execute: blocked
- Monitor: not started

## Status block

Formal validation is pending this parent validator; semantic review was not run in this fixture; workflow decision is review_required because the child reports are formal-only synthetic reports and do not yet expose explicit workflow-decision metadata. The proposal is a request_more_inputs gate, not a decision-grade pass.

## Analyze artifacts

- asset child report: [asset-investment-diligence/verification/workflow-harness-report.json](../asset-investment-diligence/verification/workflow-harness-report.json)
- oracle child report: [oracle-analysis/verification/workflow-harness-report.json](../oracle-analysis/verification/workflow-harness-report.json)

## Requested next checks

- asset workflow_decision metadata — rerun or update the asset child report with explicit workflow_decision/status_block metadata before treating the parent proposal as ready.
- oracle workflow_decision metadata — rerun or update the oracle child report with explicit workflow_decision/status_block metadata before treating the parent proposal as ready.

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
        "acceptance_criteria": "Asset child report exposes workflow_decision.status=pass, or parent Propose remains request_more_inputs.",
        "method": "Rerun the asset child validator with explicit workflow_decision/status_block metadata or document why no decision owner can approve it.",
        "owner": "asset_stage_owner",
        "requested_input": "asset workflow_decision metadata",
        "source": "asset.workflow_decision_status",
        "status": "review_required"
      },
      {
        "acceptance_criteria": "Oracle child report exposes workflow_decision.status=pass, or parent Propose remains request_more_inputs.",
        "method": "Rerun the oracle child validator with explicit workflow_decision/status_block metadata or document why no decision owner can approve it.",
        "owner": "oracle_stage_owner",
        "requested_input": "oracle workflow_decision metadata",
        "source": "oracle.workflow_decision_status",
        "status": "review_required"
      }
    ],
    "explanation": "Formal child reports passed, but missing child workflow-decision metadata prevents decision-grade parent readiness.",
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
          "acceptance_criteria": "Asset child report exposes workflow_decision.status=pass, or parent Propose remains request_more_inputs.",
          "method": "Rerun the asset child validator with explicit workflow_decision/status_block metadata or document why no decision owner can approve it.",
          "owner": "asset_stage_owner",
          "requested_input": "asset workflow_decision metadata",
          "source": "asset.workflow_decision_status",
          "status": "review_required"
        },
        {
          "acceptance_criteria": "Oracle child report exposes workflow_decision.status=pass, or parent Propose remains request_more_inputs.",
          "method": "Rerun the oracle child validator with explicit workflow_decision/status_block metadata or document why no decision owner can approve it.",
          "owner": "oracle_stage_owner",
          "requested_input": "oracle workflow_decision metadata",
          "source": "oracle.workflow_decision_status",
          "status": "review_required"
        }
      ],
      "explanation": "Formal child reports passed, but missing child workflow-decision metadata prevents decision-grade parent readiness.",
      "status": "review_required",
      "type": "request_more_inputs"
    },
    "semantic_review_status": "not_run",
    "workflow_decision_status": "review_required"
  },
  "unresolved_gates": [
    {
      "gate": "asset.workflow_decision_status",
      "requested_input": "asset workflow_decision metadata"
    },
    {
      "gate": "oracle.workflow_decision_status",
      "requested_input": "oracle workflow_decision metadata"
    }
  ]
}
```
