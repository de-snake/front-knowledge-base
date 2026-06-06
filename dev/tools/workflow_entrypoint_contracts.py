#!/usr/bin/env python3
"""Static contracts for the front-knowledge-base workflow entrypoint.

The runner intentionally imports this declarative module instead of parsing
Markdown workflow runbooks at runtime. Keep this file standard-library only.
"""

from __future__ import annotations

SCHEMA_VERSION = "workflow-entrypoint-input-v1"
PLAN_SCHEMA_VERSION = "workflow-entrypoint-plan-v1"
PACKET_SCHEMA_VERSION = "workflow-stage-packet-v1"
NEXT_ACTION_SCHEMA_VERSION = "workflow-entrypoint-next-action-v1"
RESULT_SCHEMA_VERSION = "workflow-entrypoint-result-v1"
EXECUTION_GRAPH_SCHEMA_VERSION = "workflow-entrypoint-execution-graph-v1"

COMMAND = "analyze-propose"
SUPPORTED_AGENTS = ("generic", "codex", "claude-code", "hermes")

WORKFLOW_IDS = {
    "asset": "asset-investment-diligence-v1",
    "oracle": "oracle-analysis-v1",
    "combined": "combined-analyze-propose",
}

CHILD_DIRECTORIES = {
    "asset": "asset-investment-diligence",
    "oracle": "oracle-analysis",
}

GENERATED_PARENT_FILES = (
    "README.md",
    "index.md",
    "run-manifest.json",
    "agentic-flow/analyze-and-propose.md",
    ".workflow/input.normalized.json",
    ".workflow/plan.json",
    ".workflow/execution-graph.json",
    ".workflow/tasks.json",
    ".workflow/registry.json",
    ".workflow/agent-handoff.md",
    ".workflow/next-action.json",
    ".workflow/next-action.md",
)

INPUT_FATAL_ERROR_IDS = {
    "WE_SCHEMA_VERSION",
    "WE_COMMAND",
    "WE_OBJECTIVE_QUESTION",
    "WE_ASSETS",
    "WE_ORACLE_SCOPE",
    "WE_PATH_ESCAPE",
    "WE_RUN_ROOT_EXISTS",
    "WE_INPUT_HASH_MISMATCH",
}

STABLE_ERROR_IDS = tuple(sorted(INPUT_FATAL_ERROR_IDS | {"WE_LIVE_FIELD_MISSING"}))

STATUS_EXIT_CODES = {
    "pass": 0,
    "ready": 0,
    "scaffolded": 0,
    "review_required": 1,
    "blocked": 2,
    "input_error": 2,
}

VALIDATOR_EXIT_STATUS = {
    0: "pass",
    1: "review_required",
    2: "blocked",
}

AGENT_LAUNCHERS = {
    "generic": "Read this packet and write only to the declared run root.",
    "codex": "Codex: use this packet as the complete task brief; write only to the declared run root, then return the envelope.",
    "claude-code": "Claude Code: open the packet, make only the declared artifact writes, run the listed validation command, and return the envelope.",
    "hermes": "Hermes: execute the packet as a bounded workflow stage; do not ask for extra prompt context unless a blocking unknown requires human input.",
}

REQUIRED_PACKET_HEADINGS = (
    "Scope",
    "Delegation metadata",
    "Known inputs",
    "Blocking unknowns",
    "Protocol investigation adapter",
    "Analyze-only scenario contract",
    "Fact results to produce",
    "Work to perform",
    "Required outputs",
    "Validation command",
    "Return envelope",
)

COMMON_DO_NOT = (
    "Do not write outside the run root.",
    "Do not invent missing addresses, prices, APRs, or oracle verdicts.",
    "Do not claim economic suitability or execution readiness.",
)

OPTIONAL_REFERENCES = {
    "asset": (
        "user/references/workflows/asset-investment-diligence/workflow.json",
        "user/references/workflows/asset-investment-diligence/output-structure.md",
    ),
    "oracle": (
        "user/references/workflows/oracle-analysis/workflow.json",
        "user/references/workflows/oracle-analysis/output-structure.md",
        "user/references/workflows/oracle-analysis/gearbox-price-feed-parsing.md",
    ),
}

MANDATORY_REFERENCES: tuple[str, ...] = ()

ASSET_STAGES = {
    "S1_general_asset_mining": {
        "title": "General asset mining",
        "scope": "asset",
        "artifact_dir_template": "tokens/{scope_slug}",
        "input_paths_template": ("tokens/{scope_slug}/scope.json",),
        "required_outputs_template": (
            "tokens/{scope_slug}/research/onchain-admin.md",
            "tokens/{scope_slug}/research/issuer-backing-security.md",
            "tokens/{scope_slug}/research/transfer-liquidity-oracle-governance.md",
            "tokens/{scope_slug}/technical-report.md",
        ),
    },
    "S2_asset_risk_analyst_report": {
        "title": "Asset-risk analyst report",
        "scope": "asset",
        "artifact_dir_template": "tokens/{scope_slug}",
        "input_paths_template": ("tokens/{scope_slug}/scope.json", "tokens/{scope_slug}/technical-report.md"),
        "required_outputs_template": ("tokens/{scope_slug}/analyst-report.md", "tokens/{scope_slug}/verification.md"),
    },
    "S6_quantitative_underwriting": {
        "title": "Quantitative underwriting and decision memo",
        "scope": "run",
        "artifact_dir_template": "investment-analysis",
        "input_paths_template": ("tokens", "pt-markets/index.md", "x-research/index.md"),
        "required_outputs_template": (
            "investment-analysis/quantitative-underwriting-methodology.md",
            "investment-analysis/investment-analyst-report-points-pt-risk-return.md",
            "investment-analysis/index.md",
        ),
    },
    "S7_final_verification": {
        "title": "Final verification",
        "scope": "run",
        "artifact_dir_template": "verification",
        "input_paths_template": ("run-manifest.json", "index.md", "investment-analysis/index.md"),
        "required_outputs_template": ("verification/final-investment-analysis-verification.md",),
    },
}

ASSET_SKIPPED_STAGES_WHEN_EMPTY = {
    "pt_markets": ("S3_pt_market_economics",),
    "social_scopes": ("S4_x_social_mining", "S5_x_social_synthesis"),
}

ORACLE_STAGES = {
    "S0_scope_and_acceptance": {
        "title": "Scope and acceptance policy",
        "scope": "oracle",
        "artifact_dir_template": "tokens/{scope_slug}",
        "input_paths_template": ("tokens/{scope_slug}/scope.json",),
        "required_outputs_template": ("tokens/{scope_slug}/oracle/scope.md",),
    },
    "S1_feed_inventory_and_graph": {
        "title": "Feed inventory and dependency graph",
        "scope": "oracle",
        "artifact_dir_template": "tokens/{scope_slug}",
        "input_paths_template": ("tokens/{scope_slug}/oracle/scope.md",),
        "required_outputs_template": ("tokens/{scope_slug}/oracle/feed-graph.md", "tokens/{scope_slug}/raw/feed-probes.json"),
    },
    "S2_node_classification": {
        "title": "Node classification and math reconstruction",
        "scope": "oracle",
        "artifact_dir_template": "tokens/{scope_slug}",
        "input_paths_template": ("tokens/{scope_slug}/oracle/feed-graph.md", "tokens/{scope_slug}/raw/feed-probes.json"),
        "required_outputs_template": ("tokens/{scope_slug}/oracle/node-classification.md",),
    },
    "S3_source_primitive_audit": {
        "title": "Source primitive audit",
        "scope": "oracle",
        "artifact_dir_template": "tokens/{scope_slug}",
        "input_paths_template": ("tokens/{scope_slug}/oracle/node-classification.md",),
        "required_outputs_template": ("tokens/{scope_slug}/oracle/source-primitive-audit.md", "tokens/{scope_slug}/raw/source-evidence/"),
    },
    "S4_stress_tradeoff_analysis": {
        "title": "Stress and tradeoff analysis",
        "scope": "oracle",
        "artifact_dir_template": "tokens/{scope_slug}",
        "input_paths_template": ("tokens/{scope_slug}/oracle/feed-graph.md", "tokens/{scope_slug}/oracle/source-primitive-audit.md"),
        "required_outputs_template": ("tokens/{scope_slug}/oracle/stress-tradeoff-analysis.md",),
    },
    "S5_protocol_fit_and_parameter_context": {
        "title": "Protocol fit and parameter context",
        "scope": "oracle",
        "artifact_dir_template": "tokens/{scope_slug}",
        "input_paths_template": ("tokens/{scope_slug}/oracle/stress-tradeoff-analysis.md",),
        "required_outputs_template": ("tokens/{scope_slug}/oracle/protocol-fit-memo.md",),
    },
    "S6_final_verification": {
        "title": "Final verification",
        "scope": "oracle",
        "artifact_dir_template": "tokens/{scope_slug}",
        "input_paths_template": ("tokens/{scope_slug}/oracle/protocol-fit-memo.md",),
        "required_outputs_template": (
            "tokens/{scope_slug}/verification/oracle-analysis-verification.md",
            "verification/final-oracle-analysis-verification.md",
            "index.md",
        ),
    },
}

VALIDATOR_COMMANDS = {
    "asset": (
        "python3",
        "dev/tools/validate_workflow_run.py",
        "--workflow",
        "asset-investment-diligence",
        "--run-root",
        "{asset_run_root}",
        "--format",
        "json,markdown",
        "--report-dir",
        "{asset_report_dir}",
        "--write-verification",
    ),
    "oracle": (
        "python3",
        "dev/tools/validate_workflow_run.py",
        "--workflow",
        "oracle-analysis",
        "--run-root",
        "{oracle_run_root}",
        "--format",
        "json,markdown",
        "--report-dir",
        "{oracle_report_dir}",
        "--write-verification",
    ),
    "combined": (
        "python3",
        "dev/tools/validate_workflow_run.py",
        "--workflow",
        "combined-analyze-propose",
        "--run-root",
        "{run_root}",
        "--parent-return",
        "agentic-flow/analyze-and-propose.md",
        "--format",
        "json,markdown",
        "--report-dir",
        "{combined_report_dir}",
        "--write-verification",
    ),
}
