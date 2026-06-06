# Workflow safe parallelization Kanban

Created: 2026-06-06T14:00:35Z

This board plans a metadata-only safe parallelization scheme for the `Analyze → Propose` workflow harness. It is intentionally frozen in `blocked` status so the dispatcher cannot start implementation before the plan is reviewed. Unblock `M0` deliberately when ready.

## Board

- Slug: `front-kb-safe-parallelization`
- Name: `Front KB Safe Parallelization`
- DB path: `/Users/ilya/.hermes/kanban/boards/front-kb-safe-parallelization/kanban.db`
- Workspace for cards: `dir:/Users/ilya/Documents/Codex/front-knowledge-base`
- Assignee: `default`
- Creation status snapshot: `blocked=10`, `todo=0`, `ready=0`, `running=0`, `done=0`
- Recovery snapshot: 2026-06-06T14:04Z — `t_00a1fab0` was briefly auto-claimed by the dispatcher, then reclaimed and re-blocked with reason `Plan-only board: keep blocked until explicit human unblock`; board returned to `blocked=10`, `running=0`.
- Safety posture: no implementation card is runnable until a human explicitly unblocks it.

## Commands

```bash
hermes kanban boards list --json
hermes kanban --board front-kb-safe-parallelization stats
hermes kanban --board front-kb-safe-parallelization list --json
hermes kanban --board front-kb-safe-parallelization show --json <task-id>
hermes kanban --board front-kb-safe-parallelization unblock t_00a1fab0
hermes kanban --board front-kb-safe-parallelization dispatch
```

## Dependency graph

- `t_00a1fab0` — M0: Freeze current verification baseline and non-regression contract
  - Root baseline card.
  - Captures current verification behavior before any graph/parallelization changes.
  - Required checks: `python3 dev/tools/run_fixture_checks.py` and `python3 -m pytest dev/tools/workflow_harness/tests -q`.

- `t_7601c139` — M1: Design metadata-only execution graph contract
  - Parent: `t_00a1fab0`.
  - Designs `.workflow/execution-graph.json`, `ready_packets`, and compatibility rules.
  - Explicit non-goal: no scheduler and no subagent launch.

- `t_467fc8a6` — M2: Add pre-implementation regression tests for current harness behavior
  - Parent: `t_7601c139`.
  - Locks current serial/verification behavior before implementation.
  - Protects `first_packet`, registry order, launcher payload invariance, validation exit semantics, and prompt budget.

- `t_2f4999dc` — M3: Generate execution-graph metadata without changing task execution
  - Parent: `t_467fc8a6`.
  - Adds graph metadata in scaffold output while preserving current plan, registry, packet, and next-action compatibility.

- `t_2c1f4d1f` — M4: Expose ready packet waves while retaining first-packet compatibility
  - Parent: `t_2f4999dc`.
  - Adds `ready_packets`, `blocked_packets`, and `parallel_waves` while retaining `first_packet` for old agents.

- `t_cffed450` — M5: Add safe delegation hints to packets and handoff without subagent orchestration
  - Parent: `t_2c1f4d1f`.
  - Adds advisory delegation metadata and references subagent prompt paths without embedding long prompts or launching workers.

- `t_a663b8c8` — M6: Add graph/parallelization regression fixture matrix
  - Parent: `t_cffed450`.
  - Covers safe parallel waves, skipped stages, run-level serial stages, blocked downstream stages, oracle dynamic primitive limits, and write-scope conflicts.

- `t_77021842` — M7: Add execution-graph validation and diagnostics without blocking legacy runs
  - Parent: `t_a663b8c8`.
  - Validates graph integrity only when graph schema is present and preserves legacy graph-absent validation behavior.

- `t_41b41772` — M8: Run end-to-end dry runs and compare against baseline verification
  - Parent: `t_77021842`.
  - Runs scaffold/validate dry runs and writes a compatibility report before rollout.

- `t_4f408414` — M9: Document guarded rollout and production enablement criteria
  - Parent: `t_41b41772`.
  - Documents usage, enablement gates, and rollback path.

## Board-level definitions of done

- Existing verification flow remains green before and after the change.
- `.workflow/registry.json`, packet paths, and `next-action.first_packet` remain backward-compatible.
- The harness emits only metadata; it does not schedule, spawn, or orchestrate subagents.
- Parallel waves are generated only when dependency and artifact-write-scope checks prove they are safe.
- Missing/ambiguous dependency metadata degrades to serial/blocking behavior.
- Run-level synthesis, underwriting, final verification, and parent proposal composition stay serial.
- Older graph-absent runs continue to validate through the legacy path.
- Rollout docs include a rollback path: ignore/delete `.workflow/execution-graph.json` and use registry order.

## Production enablement gate

Do not treat the safe parallelization scheme as production-ready until M0–M9 are done and the rollout reviewer accepts the final dry-run report in `dev/implementation/workflow-harness/safe-parallelization-dry-run-report.md`.

Production enablement requires all of these conditions at the same gate:

- `python3 dev/tools/run_fixture_checks.py` exits `0`;
- `python3 -m pytest dev/tools/workflow_harness/tests -q` exits `0` in an environment with pytest installed;
- repository-local docs/link policy checks, if present at implementation time, exit `0`;
- the graph-enabled scaffold/validate path has no validator status, exit-code, validator-report tuple, or finding-count regression versus the legacy graph-absent baseline;
- no automatic subagent, worker, scheduler, retry, queue, Kanban-card creation, LLM invocation, or process-launch path exists in the harness;
- old consumers that read only `.workflow/next-action.json.first_packet` and `.workflow/registry.json` remain supported;
- `first_packet` keeps its legacy shape and registry-order meaning, even when graph-ready packets are also present;
- graph metadata does not change parent proposal-gate semantics and cannot unblock Preview / Execute.

## Rollback path

Rollback is data-only and reversible. Ignore or delete `.workflow/execution-graph.json` in the affected run root and ignore `ready_packets`, `blocked_packets`, and `parallel_waves` in `.workflow/next-action.json`.

After rollback, operate exactly as the legacy path does: read `.workflow/next-action.json.first_packet`, execute `.workflow/registry.json` in serial registry order, then run the normal validation command. Validators must keep graph-absent runs on the legacy path, so the rollback must not require code changes, fixture rewrites, or artifact migration.
