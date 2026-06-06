# Kanban — front-kb-workflow-harness

Board slug: `front-kb-workflow-harness`

Purpose: build deterministic, task-specific harnesses for `front-knowledge-base` token/oracle workflows so formal output-contract failures are caught mechanically before an external agent claims completion.

Workspace: `/Users/ilya/Documents/Codex/front-knowledge-base`

Assignee profile: `default`

Skills force-loaded on worker cards:
- `ai-assistant/project-execution-workflow`
- `ai-assistant/gearbox-doc-workflow`

## Operating rule

This board is about formal compliance only: file/folder shape, required fields, required sections, manifest/path/link checks, stage coverage, skipped-stage markers, final verification credibility, and post-Discover flow gates. It must not judge token economic reasoning quality.

## Dependency graph

- R1 INTERNAL RESEARCH and R2 EXTERNAL RESEARCH run in parallel.
- P1 PLAN waits for R1/R2.
- P2 REVIEW waits for P1.
- P3 HARDEN waits for P2.
- M1-M5 each use explicit `PLAN → REVIEW → HARDEN → IMPLEMENT → VERIFY` chains gated by P3:
  - M1 validator core CLI and machine-readable report schema
  - M2 asset-investment-diligence harness checks
  - M3 oracle-analysis harness checks
  - M4 combined post-Discover Analyze→Propose harness and stage prompts
  - M5 fixtures, runbooks, and external-agent handoff instructions
- FINAL VERIFY waits for all milestone VERIFY cards.

## Task IDs

- R1 internal audit: `t_20ea576c`
- R2 external harness research: `t_2b7f8244`
- P1 plan: `t_c88ca392`
- P2 review: `t_2b593378`
- P3 harden: `t_ac289062`
- Final verify: `t_4f0b136b`

Full task inventory:

```bash
hermes kanban --board front-kb-workflow-harness list
```

Stats:

```bash
hermes kanban --board front-kb-workflow-harness stats --json
```

Dispatch conservatively when ready to run:

```bash
hermes kanban --board front-kb-workflow-harness dispatch --max 1 --json
```

## Definition of done

- `dev/tools/validate_workflow_run.py` exists and validates asset, oracle, and combined post-Discover runs.
- Known-bad external artifacts fail with deterministic P0/P1/P2 findings.
- Known-good/current artifacts pass or only emit intentional warnings.
- Workflow runbooks require the validator before final completion.
- Stage prompts require explicit `null` / `not_in_scope` instead of omitted required fields.
- Final verification is generated from real harness output.
