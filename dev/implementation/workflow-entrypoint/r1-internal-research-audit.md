# R1 internal research — workflow entrypoint audit

Task: `t_04fe3f60`

## Scope inspected

Required files existed and were inspected:

- `CLAUDE.md`
- `dev/tools/validate_workflow_run.py`
- `dev/implementation/workflow-harness/final-verification.md`
- `user/references/workflows/asset-investment-diligence/{README.md,workflow.json,runbook.md,output-structure.md,stage-contracts.md,subagent-prompts.md}`
- `user/references/workflows/oracle-analysis/{README.md,workflow.json,runbook.md,output-structure.md,stage-contracts.md,subagent-prompts.md,gearbox-price-feed-parsing.md}`

Verification executed from the vault root:

```bash
python3 -m py_compile dev/tools/validate_workflow_run.py dev/tools/workflow_harness/tests/test_fixtures.py && python3 -m pytest dev/tools/workflow_harness/tests/test_fixtures.py -q
```

Result: `5 passed in 0.50s`.

## Current entrypoints and limitations

Current entrypoints are validator- and prompt-oriented, not workflow-runner-oriented:

1. Manual agent workflow packages under `user/references/workflows/{asset-investment-diligence,oracle-analysis}/`.
   - `README.md`, `runbook.md`, `workflow.json`, `stage-contracts.md`, `output-structure.md`, and `subagent-prompts.md` describe how an agent should run the workflow.
   - Limitation: the parent agent still has to read the package, define scope, choose stages, create artifact folders, fill prompt placeholders, spawn workers, maintain a registry, reconcile blockers, and run validation.
2. Post-hoc validator CLI:
   - `python3 dev/tools/validate_workflow_run.py --workflow {asset-investment-diligence|oracle-analysis|combined-analyze-propose} --run-root <run_artifact_root> [--format json,markdown] [--report-dir ...] [--write-verification]`.
   - Limitation: it requires an already-created run root. It does not accept a single workflow scope, create folders, write manifests/indexes, generate stage packets, execute/delegate stages, or synthesize reports.
3. Combined Analyze → Propose validator mode.
   - It checks parent-run handoff shape and child workflow-harness reports.
   - Limitation: it validates a parent flow artifact after child reports exist; it does not run child workflows recursively or create the parent handoff.
4. Fixture tests in `dev/tools/workflow_harness/tests/test_fixtures.py`.
   - They prove deterministic false-pass coverage for the current harness.
   - Limitation: they exercise validator behavior only, not one-command execution.

## What the harness already enforces

`dev/tools/validate_workflow_run.py` is useful and should be preserved as the compliance layer. It currently enforces:

- Common checks: CLI args, run-root existence, `run-manifest.json` existence/JSON validity for child workflows.
- Asset investment diligence:
  - manifest fields, workflow ID, run-root reconciliation, declared path resolution, canonical path declaration;
  - token entries, artifact-dir reconciliation, token scope identity;
  - required root files, per-token files, S1 research artifacts;
  - S1 fact slots and unknown-decision-effect notes;
  - S2 required sections, source map, technical appendix pointer;
  - skipped PT/social stages have indexes, skipped markers, and reasons;
  - S6 quantitative fields are present, not heading-only, and non-numeric values carry reasons;
  - final verification exists and names status, required file checks, field checks, skipped-stage checks, cross-link checks, workspace validation, overclaim detection, and unsupported execution-ready claims;
  - README handoff sections, index contract sections, run-status reconciliation, and local path resolution.
- Oracle analysis:
  - manifest schema and canonical final verification path;
  - required files and index/README handoff sections;
  - source primitive audit, pricing formula, node classification, stress-tradeoff fields;
  - side-specific conclusion quad: position side, token role, stress direction, loss bearer;
  - Gearbox-specific fields and rejection of top-level-feed-label-only verdicts;
  - run-status reconciliation.
- Combined Analyze → Propose:
  - required `agentic-flow/analyze-and-propose.md` handoff;
  - Discover/Analyze/Propose/Preview/Execute/Monitor status table parsing;
  - child report status reconciliation;
  - unresolved gates block Preview/Execute;
  - no unsupported execution recommendation;
  - requested next checks are named;
  - parent index maps child artifacts and local paths resolve.

The final verification explicitly states the harness is formal workflow compliance only. It does not assess token economic quality, oracle correctness, allocation suitability, or live execution merit.

## Work still pushed into prompts/manual parent behavior

The durable gap is not validation coverage; it is execution orchestration. These responsibilities are still embedded in runbooks and subagent prompts instead of being compiled from one input:

- Scope and file management:
  - create a scope object;
  - preserve unknown fields as `null`;
  - choose deterministic slugs;
  - create `run-manifest.json`, `README.md`, `index.md`, `tokens/`, `pt-markets/`, `x-research/`, `investment-analysis/`, `oracle/`, `raw/`, and `verification/` paths;
  - maintain a parent run registry;
  - update final index and manifest statuses.
- Stage orchestration:
  - choose which asset stages run for spot-only, PT, points/social, or evidence-pack scopes;
  - choose which oracle stages run for token, PT, comparison, and Gearbox scopes;
  - batch subagents at max three at a time;
  - fill prompt placeholders with run root, artifact dirs, prior artifact paths, chain/token/PT metadata, and protocol context;
  - decide serial vs delegated execution per stage.
- Section and content contracts:
  - require exact report sections, e.g. S2 executive/source/technical appendix sections, S6 quantitative fields, oracle graph/formula/node/source/stress/protocol-fit sections;
  - require social query angles and citation-degraded markers;
  - require Gearbox-specific oracle parsing rules from `gearbox-price-feed-parsing.md`.
- Verification and blocker handling:
  - write per-scope and final verification artifacts;
  - invoke the validator after outputs exist;
  - carry `workflow_harness_report`, `final_verification`, blocker counts, `commands_run`, `null_fields`, and live-input blockers in compressed handoffs;
  - prevent Preview/Execute recommendations while blockers remain.

## Exact files likely needing change

Smallest durable change: add a thin runner/packet compiler around the existing validator, rather than rewriting the validator.

Likely files:

1. New runner entrypoint:
   - `dev/tools/run_workflow.py` or `dev/tools/workflow_entrypoint.py`.
   - Responsibilities: accept `--workflow` and one scope/input JSON; create run root; validate scope schema; materialize run-manifest/index/README skeletons; generate stage job packets/prompts; track stage status; invoke `validate_workflow_run.py` at stage/final gates.
2. Existing validator as reusable validation layer:
   - `dev/tools/validate_workflow_run.py`.
   - Minimal changes only if the runner needs importable functions or shared path/report helpers instead of subprocess-only use.
3. Runner tests and fixtures:
   - `dev/tools/workflow_harness/tests/test_fixtures.py` or a new `test_workflow_entrypoint.py`.
   - `dev/implementation/workflow-harness/fixtures/` for runner known-good/known-bad fixture roots or input scope fixtures.
4. Workflow contracts:
   - `user/references/workflows/asset-investment-diligence/workflow.json`
   - `user/references/workflows/oracle-analysis/workflow.json`
   - Add machine-readable `input_schema`, stage skip conditions, artifact templates, prompt-template IDs, generated packet paths, and validation gate metadata.
5. Human docs updated to route through the runner:
   - `user/references/workflows/*/runbook.md`
   - `user/references/workflows/*/output-structure.md`
   - `user/references/workflows/*/subagent-prompts.md`
   - Possibly `stage-contracts.md` if the runner formalizes stage-return JSON schema.
6. Navigation/operating contract if the new entrypoint becomes canonical:
   - `README.md`
   - `CLAUDE.md`

## Recommended acceptance checks for a true one-command/single-input interface

Minimum acceptance should prove a user/agent can start from one scope file, not a long prompt:

1. Help/contract check:
   - `python3 dev/tools/run_workflow.py --help` exposes one canonical command with `--workflow`, `--scope`, `--run-root`, and `--mode {plan,dry-run,execute}` or equivalent.
2. Plan/dry-run check:
   - Given one minimal scope JSON, the runner creates or prints a deterministic execution plan: selected stages, dependencies, parallel batches, generated artifact dirs, generated prompt/packet paths, and validation gates.
3. Scaffold check:
   - The runner creates `run-manifest.json`, `README.md`, `index.md`, per-scope directories, and verification directories without manual prompt instructions.
4. Packet-generation check:
   - Stage packets/prompts are materialized with placeholders resolved; no subagent prompt requires the parent to manually infer run root, artifact dir, prior artifact path, or validation path.
5. Validator integration check:
   - Existing command still works and runner invokes it at final gate:
     `python3 dev/tools/validate_workflow_run.py --workflow <workflow> --run-root <run_root> --format json,markdown --report-dir <run_root>/verification --write-verification`.
6. Existing regression check:
   - `python3 -m py_compile dev/tools/validate_workflow_run.py dev/tools/workflow_harness/tests/test_fixtures.py`
   - `python3 -m pytest dev/tools/workflow_harness/tests/test_fixtures.py -q`
7. New runner fixtures:
   - known-good scope fixture produces deterministic plan/scaffold and reaches expected validation status;
   - malformed/missing scope fails with stable finding IDs;
   - path-escape input fails;
   - unresolved blockers prevent Preview/Execute readiness;
   - malformed worker handoff or missing final verification fails with stable IDs.
8. Non-goal guard:
   - The new runner must not claim investment suitability, oracle quality, or execution readiness. It should orchestrate artifacts and validation gates; content quality and live execution remain separate review layers.
