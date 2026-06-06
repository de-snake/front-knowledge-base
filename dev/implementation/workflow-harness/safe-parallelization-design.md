# Safe parallelization design

M1 objective: design a metadata-only execution graph for the `Analyze -> Propose` workflow harness. The graph exposes which generated packets are independent enough to work in parallel, but it does not schedule work, launch subagents, change Preview / Execute gates, or change existing validation semantics.

This document is an implementation contract for later cards. It is reviewable without code changes.

## Source baseline

Grounded files and contracts:

- `dev/implementation/workflow-harness/safe-parallelization-baseline.md`.
- `dev/implementation/workflow-entrypoint/run-workflow-usage.md`.
- `dev/tools/workflow_entrypoint.py`.
- `dev/tools/workflow_entrypoint_contracts.py`.
- `dev/tools/validate_workflow_run.py`.
- `user/references/workflows/asset-investment-diligence/workflow.json`.
- `user/references/workflows/oracle-analysis/workflow.json`.

Current generated behavior that must remain compatible:

- `.workflow/plan.json`, `.workflow/tasks.json`, and `.workflow/registry.json` list stage packets in deterministic serial registry order.
- `.workflow/next-action.json.first_packet` names one packet with `task_id`, `json`, `markdown`, and `blocking_unknowns`.
- `.workflow/agent-handoff.md` tells generic agents to execute packets in registry order.
- Validation imports asset, oracle, and combined reports and maps status/exit codes independently of packet scheduling.
- Parent proposal-gate semantics separate formal validation, semantic review, workflow decision readiness, and Preview / Execute blocking.

## Design principle

The execution graph is declarative metadata over the existing packet registry.

It may say: these packets have no unmet packet dependencies, write to disjoint artifact scopes, and are safe candidates for parallel human or external-agent execution.

It must not say: start these workers now, allocate this worker identity, retry this task, call an LLM, spawn a subagent, or advance a proposal gate.

If graph metadata is absent, malformed, or ignored, the harness must continue to work exactly as it does today: execute `.workflow/registry.json` in order, use `.workflow/next-action.json.first_packet` as the single next packet, and validate with the existing validators.

## Generated artifact contract

Later implementation may add one new generated parent file:

```text
.workflow/execution-graph.json
```

Later implementation may add two additive fields to the existing next-action file:

```text
.workflow/next-action.json.ready_packets
.workflow/next-action.json.blocked_packets
```

These are additive fields only. Existing consumers that read `first_packet`, `validation`, `children`, or `agent_handoff` must not need to know the graph exists.

`first_packet` remains present and keeps the current shape. It remains the first packet in legacy serial registry order. When graph metadata is present and the serial first packet is ready, `ready_packets[0]` should reference the same `task_id` as `first_packet`. If the serial first packet is blocked, `first_packet` still reports that legacy blocker while graph-aware consumers may inspect `ready_packets` for other safe candidates.

## `.workflow/execution-graph.json` schema

Proposed top-level shape:

```json
{
  "schema_version": "workflow-entrypoint-execution-graph-v1",
  "command": "analyze-propose",
  "run_root": "dev/implementation/<run-root>",
  "input_sha256": "<normalized-input-sha256>",
  "plan_schema_version": "workflow-entrypoint-plan-v1",
  "packet_schema_version": "workflow-stage-packet-v1",
  "registry_source": ".workflow/registry.json",
  "graph_status": "metadata_only",
  "fallback_behavior": "serial_registry_order",
  "tasks": [
    {
      "task_id": "asset.S1_general_asset_mining.<scope_slug>",
      "workflow_key": "asset",
      "stage_id": "S1_general_asset_mining",
      "scope_id": "<input scope id>",
      "scope_slug": "<filesystem-safe scope slug>",
      "registry_index": 0,
      "packet_json": ".workflow/packets/<task_id>.json",
      "packet_markdown": ".workflow/packets/<task_id>.md",
      "depends_on_task_ids": [],
      "parallel_group_id": "asset.S1_general_asset_mining.token",
      "parallel_unit": "token",
      "delegate_to_subagent": true,
      "recommended_max_concurrent": 3,
      "artifact_write_scope": {
        "mode": "exclusive_prefixes",
        "write_roots": ["asset-investment-diligence/tokens/<scope_slug>"],
        "required_outputs": [
          "asset-investment-diligence/tokens/<scope_slug>/research/onchain-admin.md",
          "asset-investment-diligence/tokens/<scope_slug>/research/issuer-backing-security.md",
          "asset-investment-diligence/tokens/<scope_slug>/research/transfer-liquidity-oracle-governance.md",
          "asset-investment-diligence/tokens/<scope_slug>/technical-report.md"
        ],
        "shared_write_roots": [],
        "read_roots": ["asset-investment-diligence/tokens/<scope_slug>/scope.json"]
      },
      "ready_after_validation": {
        "type": "dependency_artifacts",
        "required_task_ids": [],
        "required_artifacts": [],
        "required_statuses": []
      },
      "safety_rationale": "Independent token-level evidence collection writes only to its token directory and has no upstream packet dependency."
    }
  ],
  "parallel_groups": [
    {
      "parallel_group_id": "asset.S1_general_asset_mining.token",
      "parallel_unit": "token",
      "task_ids": ["asset.S1_general_asset_mining.<scope_slug>"],
      "recommended_max_concurrent": 3,
      "artifact_write_scope_policy": "disjoint_write_roots_required",
      "delegate_to_subagent": true,
      "safety_rationale": "One token per isolated artifact directory."
    }
  ],
  "serial_sections": [
    {
      "id": "asset.underwriting",
      "task_ids": ["asset.S6_quantitative_underwriting.run"],
      "reason": "Run-level underwriting compares all asset evidence and writes one decision surface."
    }
  ],
  "compatibility": {
    "first_packet_preserved": true,
    "legacy_serial_registry_supported": true,
    "validators_require_execution_graph": false,
    "proposal_gate_requires_execution_graph": false
  },
  "non_goals": [
    "scheduler",
    "subagent_launch",
    "dynamic_oracle_primitive_fan_out_before_source_artifacts_exist",
    "preview_or_execute_gate_changes"
  ]
}
```

The shape above is a contract, not a JSON Schema implementation. Later code should generate it deterministically from the already generated plan/registry plus static workflow metadata.

## Task field definitions

### `depends_on_task_ids`

Array of generated `task_id` strings that must be completed before this packet is considered ready.

The field expresses packet-level dependencies, not abstract stage IDs. For example, a token-level S2 packet depends on the same token's generated S1 packet, not on every S1 packet in the run.

If source workflow metadata is missing or ambiguous, the generator must use the safe fallback: depend on the previous task in serial registry order. If the whole graph is missing, consumers must use the current serial registry behavior.

Skipped optional stages must not appear as dangling dependencies. If a stage is skipped by input shape, downstream dependencies must resolve to the nearest concrete upstream packet or be marked as satisfied by `skipped_stage` metadata.

### `parallel_group_id`

Stable string grouping packets that may be considered together for parallel execution. It is advisory metadata for humans and graph-aware launchers.

Recommended format:

```text
<workflow_key>.<stage_id>.<parallel_unit>
```

Examples:

- `asset.S1_general_asset_mining.token`.
- `asset.S2_asset_risk_analyst_report.token`.
- `oracle.S1_feed_inventory_and_graph.scope`.
- `oracle.S3_source_primitive_audit.scope` in v1, because primitive-level fan-out is not known at scaffold time.

Serial packets set `parallel_group_id` to `null` or to a serial section id only for reporting. A non-null group is not permission to run if dependencies, validation gates, or write scopes are unsafe.

### `parallel_unit`

Human-readable unit of safe independence.

Allowed v1 values should be small and explicit:

- `token` for one asset token directory.
- `pt_market` only when PT market scopes are already present in the normalized input.
- `social_scope` only when social scopes are already present in the normalized input.
- `oracle_scope` for one feed tree / token scope.
- `source_primitive_candidate` only as blocked metadata after a node-classification artifact enumerates primitives; not generated as runnable v1 scaffold packets.
- `run` for serial run-level synthesis, underwriting, parent composition, and final verification.

If the unit cannot be named, the packet is serial.

### `delegate_to_subagent`

Boolean advisory flag copied from workflow design only after the generator confirms the packet has bounded inputs, bounded outputs, and an exclusive artifact write scope.

`true` means a human or external orchestrator may choose to delegate the packet. It does not cause the harness to call `delegate_task`, start a process, create a Kanban card, or invoke an LLM.

`false` is required for run-level synthesis, underwriting, final verification, parent proposal composition, Preview, and Execute gates.

### `recommended_max_concurrent`

Positive integer advisory cap for a `parallel_group_id`.

Use the minimum of the source workflow recommendation and the local harness cap. The current workflow design usually recommends `3` for independent token/feed lanes.

For serial packets the value must be `1`. Missing values default to `1`, never to unbounded concurrency.

### `artifact_write_scope`

Object declaring what a packet may write.

Required fields:

```json
{
  "mode": "exclusive_prefixes",
  "write_roots": ["<run-relative directory or file prefix>"],
  "required_outputs": ["<run-relative file or directory>"],
  "shared_write_roots": [],
  "read_roots": ["<run-relative path>"]
}
```

Rules:

- Paths are run-relative and must not be absolute or parent-escaping.
- Two packets can be in the same ready wave only when their `write_roots` and `required_outputs` are disjoint, except for explicitly allowed append/summary roots.
- `shared_write_roots` should be empty in v1 unless the implementation adds a deterministic merge artifact. Shared indexes such as `index.md`, child `run-manifest.json`, and final verification files are serial by default.
- A packet cannot write `.workflow/`, parent `agentic-flow/`, Preview artifacts, Execute artifacts, or another packet's scope.

This field is the primary safety check that keeps parallel metadata from corrupting shared run artifacts.

### `ready_after_validation`

Object describing the readiness condition for the packet.

Proposed fields:

```json
{
  "type": "dependency_artifacts",
  "required_task_ids": ["<task_id>"],
  "required_artifacts": ["<run-relative path>"],
  "required_statuses": ["pass", "review_required"]
}
```

Allowed `type` values:

- `none`: no extra gate beyond static graph checks.
- `dependency_artifacts`: upstream required outputs must exist before this packet is ready.
- `child_validation_status`: a child validator status must exist before a run-level packet is ready.
- `parent_validation_status`: parent combined validation must exist before final reporting, not before child work.
- `blocked_pending_source_artifacts`: dynamic fan-out candidate exists conceptually but source artifacts do not yet enumerate concrete units.

This field is metadata for `ready_packets` / `blocked_packets`. Existing validators must not require it. Parent proposal gates must not read it as decision readiness.

### `safety_rationale`

Short string explaining why the task is safe or why it remains serial/blocked.

The rationale should name the dependency condition and artifact-write-scope condition. It should not repeat generic claims such as "parallelizable" without explaining why.

## Safe v1 graph derivation

Generate tasks from the existing `plan.tasks` / `registry` entries, not from a separate scheduler model.

For each generated packet:

1. Preserve current `task_id`, packet paths, required outputs, validation command, and registry index.
2. Attach dependency metadata derived from workflow stage `depends_on`, current input shape, skipped-stage metadata, and scope identity.
3. Attach parallel metadata only when both source workflow design and generated artifacts prove independence.
4. Attach an artifact write scope from the packet's existing `required_outputs` and stage artifact directory.
5. Mark run-level and shared-output packets serial even if upstream workflow prose is ambiguous.

Do not generate new packets solely because a workflow JSON mentions a parallel unit. Packet count remains equal to the existing plan/registry count unless a later reviewed implementation card explicitly changes packet generation.

## Initial ready/blocked calculation

At scaffold time, the graph-aware next action can compute ready packets by static metadata only:

- ready when `depends_on_task_ids` is empty, write scopes do not conflict with other ready packets, and packet-level blocking unknowns do not require human input before any work can start;
- blocked when dependency tasks are not yet complete, required upstream artifacts do not exist, blocking unknowns apply to that scope, or the only safe condition is a future validation status;
- serial fallback when graph metadata is missing or invalid.

After a validate/resume pass, the same metadata can be recomputed from existing artifacts and validator summaries. It still must not launch work.

## `.workflow/next-action.json.ready_packets`

Proposed shape:

```json
"ready_packets": [
  {
    "task_id": "asset.S1_general_asset_mining.<scope_slug>",
    "json": ".workflow/packets/<task_id>.json",
    "markdown": ".workflow/packets/<task_id>.md",
    "parallel_group_id": "asset.S1_general_asset_mining.token",
    "parallel_unit": "token",
    "delegate_to_subagent": true,
    "recommended_max_concurrent": 3,
    "artifact_write_scope": {
      "write_roots": ["asset-investment-diligence/tokens/<scope_slug>"],
      "required_outputs": ["asset-investment-diligence/tokens/<scope_slug>/technical-report.md"]
    },
    "depends_on_task_ids": [],
    "ready_reason": "No upstream packet dependency and exclusive token write scope."
  }
]
```

Rules:

- Sort by current registry order for deterministic output.
- Include only packets that can be started without violating dependencies or write-scope isolation.
- Do not include more than `recommended_max_concurrent` packets from the same group when a cap is present.
- Do not include run-level synthesis, underwriting, final verification, or parent proposal packets until their upstream artifacts and validation statuses are available.

## `.workflow/next-action.json.blocked_packets`

Proposed shape:

```json
"blocked_packets": [
  {
    "task_id": "asset.S2_asset_risk_analyst_report.<scope_slug>",
    "json": ".workflow/packets/<task_id>.json",
    "markdown": ".workflow/packets/<task_id>.md",
    "blocked_by_task_ids": ["asset.S1_general_asset_mining.<scope_slug>"],
    "missing_artifacts": ["asset-investment-diligence/tokens/<scope_slug>/technical-report.md"],
    "blocking_unknowns": [],
    "ready_after_validation": {
      "type": "dependency_artifacts",
      "required_task_ids": ["asset.S1_general_asset_mining.<scope_slug>"],
      "required_artifacts": ["asset-investment-diligence/tokens/<scope_slug>/technical-report.md"],
      "required_statuses": []
    },
    "blocked_reason": "Token analyst report needs the token technical report first."
  }
]
```

Rules:

- Sort by current registry order.
- Include concrete blocker evidence: task ids, missing artifacts, blocking unknowns, or validation status prerequisites.
- Do not treat a blocked packet as a failed packet. It is only not ready yet.
- Do not require `blocked_packets` for legacy graph-absent runs.

## Compatibility with `first_packet`

`first_packet` remains the compatibility anchor.

Legacy agent behavior:

1. Read `.workflow/next-action.json.first_packet`.
2. Read `.workflow/registry.json`.
3. Execute registry order serially.
4. Run validation.

Graph-aware agent behavior:

1. Read `.workflow/execution-graph.json` if present.
2. Read `.workflow/next-action.json.ready_packets` if present.
3. Execute only listed ready packets, respecting advisory concurrency caps and artifact write scopes.
4. Fall back to `first_packet` / registry order when the graph is absent, invalid, or too strict.

The graph-aware path is an optimization hint. It is never required for correctness.

## Serial sections that must stay serial

### Asset run-level synthesis and underwriting

`asset.S6_quantitative_underwriting.run` stays serial.

It depends on all relevant token analyst reports, optional PT economics reports when PT markets are in scope, optional social synthesis when social scopes are in scope, and any required oracle protocol-fit outputs needed for the requested decision surface.

It writes shared run-level files under `asset-investment-diligence/investment-analysis/`, so it cannot run concurrently with token mining/report packets or final verification.

### Asset final verification

`asset.S7_final_verification.run` stays serial.

It depends on the completed asset decision surface and writes `asset-investment-diligence/verification/final-investment-analysis-verification.md`. Verification must observe the final artifact set after all writes.

### Oracle scope synthesis and verification

Oracle `S2_node_classification`, `S4_stress_tradeoff_analysis`, `S5_protocol_fit_and_parameter_context`, and `S6_final_verification` stay serial within each oracle scope unless a later reviewed design splits them into concrete independent units.

`S3_source_primitive_audit` is not dynamically fanned out in v1. The source primitive list only exists after feed inventory and node classification artifacts are written. Before those source artifacts exist, graph metadata may record a blocked `source_primitive_candidate` note but must not generate runnable primitive packets.

### Parent synthesis, underwriting import, and proposal gate

Parent `agentic-flow/analyze-and-propose.md`, combined validation import, final status summary, and proposal gate stay serial.

The parent may read child summaries and reports after child validation, but graph readiness never means proposal readiness. Preview and Execute remain blocked unless separately authorized by the existing workflow gates.

## Non-goals

This design explicitly does not include:

- no scheduler;
- no subagent launch;
- no worker lifecycle, retry, timeout, or queue semantics;
- no dynamic oracle primitive fan-out before source artifacts exist;
- no Preview/Execute changes;
- no change to generated packet bodies beyond additive metadata in later implementation cards;
- no change to Preview / Execute gates;
- no change to validator exit-code mapping;
- no change to parent proposal-gate semantics;
- no requirement that graph-aware behavior exists for old graph-absent runs.

## Regression and validator boundaries

Existing validators must not depend on `.workflow/execution-graph.json`.

Current asset, oracle, and combined validators should continue to validate generated artifacts, reports, status propagation, and proposal gates without reading graph metadata. A future graph validator may validate the graph when the file is present, but graph absence must not create findings for legacy runs.

Parent proposal-gate semantics must not depend on `ready_packets`, `blocked_packets`, `parallel_group_id`, or `delegate_to_subagent`.

A packet being ready means only that it may be worked on. It does not mean formal validation has passed, semantic review has passed, a workflow decision is ready, or Preview / Execute may proceed.

Missing graph metadata degrades to current serial registry behavior:

- no `.workflow/execution-graph.json`: ignore graph and use registry order;
- no `ready_packets`: use `first_packet` only;
- no `blocked_packets`: no graph-aware blocker list is available;
- missing task-level dependency metadata in a present graph: treat that task as serial after its previous registry task or mark the graph invalid and fall back to serial;
- unknown graph schema version: ignore graph and fall back to serial.

## Compatibility risks to name before implementation

1. Strict next-action consumers may reject unknown fields. Mitigation: add `ready_packets` and `blocked_packets` only as top-level additive fields and preserve existing field names/values.

2. `first_packet` semantics could drift if graph-aware code tries to replace it with the first ready packet. Mitigation: keep `first_packet` tied to serial registry order.

3. Dependency IDs can become stale if `task_id` generation changes. Mitigation: generate graph after plan/registry generation and include `input_sha256`, schema versions, and registry index in the graph.

4. Skipped stages can create dangling dependencies. Mitigation: resolve skipped stages during graph generation and record the skip as satisfied or serial-blocked metadata.

5. Artifact write-scope conflicts can corrupt shared indexes or manifests. Mitigation: only parallelize packets with disjoint `write_roots`; keep shared index/manifest/final verification writes serial.

6. Directory-scoped outputs such as `raw/source-evidence/` can hide write conflicts. Mitigation: normalize directories as exclusive prefixes and disallow two ready packets from sharing the same prefix unless an explicit merge contract exists.

7. Advisory `delegate_to_subagent` can be mistaken for an instruction to spawn workers. Mitigation: document and test that no harness code calls a subagent API, process manager, or scheduler.

8. `recommended_max_concurrent` can be mistaken for a quota the harness enforces. Mitigation: state that it is advisory metadata; future external launchers must enforce their own caps.

9. Oracle primitive fan-out can be over-generated before primitives are known. Mitigation: do not generate primitive packets from source workflow prose; require source artifacts first.

10. Graph readiness can be conflated with workflow readiness. Mitigation: keep validators and parent proposal gates independent of graph metadata and preserve status blocks that distinguish formal validation, semantic review, workflow decision, and proposal gate.

11. Resume runs can produce stale graph metadata after artifacts change. Mitigation: recompute graph/ready/blocked fields on scaffold/resume/validate, and fall back to serial when hashes or registry counts mismatch.

12. Legacy fixtures may not contain graph files. Mitigation: graph-absent fixtures must continue to pass or fail exactly as they do under current validator semantics.

## Minimum future acceptance checks

Later implementation cards should prove at least:

- current fixture checks remain green when graph generation is disabled or absent;
- generated `first_packet` remains shape-compatible and registry-order-compatible;
- `ready_packets` is additive and deterministic;
- graph-absent runs validate through the current serial path;
- graph-present invalid metadata does not unblock Preview / Execute or parent proposal gates;
- run-level underwriting, synthesis, final verification, and parent proposal composition are never included in initial ready waves;
- no code path launches subagents or external workers.
