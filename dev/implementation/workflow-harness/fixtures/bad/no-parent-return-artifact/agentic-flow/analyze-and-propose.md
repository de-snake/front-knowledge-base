# Analyze → Propose parent return

## Stage status

- Discover: complete by user premise
- Analyze: complete
- Propose: ready for preview
- Preview: blocked
- Execute: blocked
- Monitor: not started

## Analyze artifacts

- asset child report: [asset-investment-diligence/verification/workflow-harness-report.json](../asset-investment-diligence/verification/workflow-harness-report.json)
- oracle child report: [oracle-analysis/verification/workflow-harness-report.json](../oracle-analysis/verification/workflow-harness-report.json)

## Requested next checks

- none; child reports are pass unless this fixture intentionally mutates them.

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
  "schema_version": "agentic-analyze-propose-v1",
  "stage_status": {
    "Analyze": "complete",
    "Discover": "complete by user premise",
    "Execute": "blocked",
    "Monitor": "not started",
    "Preview": "blocked",
    "Propose": "ready for preview"
  },
  "unresolved_gates": []
}
```
