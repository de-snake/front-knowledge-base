# Gearbox Product Docs Vault

This vault is the primary source for Gearbox front/product knowledge: user-facing decision flows, agent-facing reasoning rules, UI primitive inputs, and the data gaps that must be solved before implementation.

Canonical loop: `Discover → Analyze → Propose → Preview → Execute → Monitor`.

## Agent workflow routing

For fresh Gearbox collateral, asset diligence, oracle/feed analysis, Credit
Account opening analysis, or `Analyze → Propose` research, agents should route
the human request through the workflow harness instead of writing an ad hoc
report. Start from the operating contract (`AGENTS.md` / `CLAUDE.md`), then use
`dev/implementation/workflow-entrypoint/run-workflow-usage.md` to scaffold a
temporary run and follow the generated `.workflow/agent-handoff.md`.

Users do not need to provide runner paths or harness commands when the intent is
clear; the repository instructions are responsible for routing the agent.

The vault now separates runtime user / agent knowledge from development context:

- `user/` contains the canonical material an agent needs to reason about user funds and position management.
- `dev/` contains product/design lineage, implementation gaps, UI primitive drafts, and archived planning material.

Standalone tokenized-security leverage is not a canonical flow. Tokenized securities, issuer-controlled assets, redemption-window assets, and compliance-gated assets are handled as conditional branches inside Credit Account opening and Credit Account management.

## User / runtime knowledge

### Foundations

| Document | Description |
| --- | --- |
| [Basic info and definitions](user/foundations/Basic%20info%20and%20definitions.md) | Defines core Gearbox concepts, yield sources, the canonical six-stage loop, and shared stage handoff rules. |
| [Personas and audience](user/foundations/Personas%20and%20audience.md) | Defines the LP and Credit Account operator personas, loss vectors, and agent-as-reader assumptions. |
| [Position risk and monitoring](user/foundations/Position%20risk%20and%20monitoring.md) | Explains why positions need monitoring, how asset properties affect risk, and how agents should derive or request thresholds instead of applying universal defaults. |

### Decision axes

| Document | Description |
| --- | --- |
| [Entry points](user/decision/Entry%20points.md) | Explains session modes, agent reader behavior, and the Preview / Execute approval boundary. |
| [Three-layer progressive disclosure](user/decision/Three-layer%20progressive%20disclosure.md) | Defines the Glance / Analyze / Act hierarchy for screens and agent responses. |

### Canonical flows

| Document | Description |
| --- | --- |
| [Pool deposit](user/flows/Pool%20deposit.md) | LP entry flow from opportunity discovery through deposit execution and monitor handoff. |
| [Pool monitoring](user/flows/Pool%20monitoring.md) | LP ownership flow: recurring checks, drift routing, action proposal, Preview, and Execute. |
| [Credit Account opening](user/flows/Credit%20Account%20opening.md) | Credit Account entry flow from strategy discovery through leveraged-position execution and monitor handoff. Includes issuer-controlled collateral checks as a conditional branch. |
| [Credit Account management](user/flows/Credit%20Account%20management.md) | Credit Account ownership flow: safety, yield, rule changes, operational mechanics, oracle / issuer-controlled collateral drift, emergency routing, and action execution. |

### References

| Document | Description |
| --- | --- |
| [Mechanics index](user/references/mechanics/) | Stable product mechanics that are neither router pages nor executable workflows. Covers oracle / liquidity risk, token and curator risk, allocation and action palettes, Credit Account risk controls, and agent continuity logs. |
| [Oracle analysis — reference workflow](user/references/workflows/oracle-analysis/) | End-agent executable oracle workflow: recursive feed graph, Gearbox-specific price-feed parsing, source-primitive audits, Steakhouse-style market / fundamental / NAV / hardcoded tradeoffs, and side-specific protocol-fit memo. |
| [Asset investment diligence — reference workflow](user/references/workflows/asset-investment-diligence/) | End-agent executable diligence workflow for token / PT opportunities: stage graph, worker contracts, subagent prompts, context controls, and verification. |

## Development context

| Path | Description |
| --- | --- |
| [Data requirements and to-dos](dev/implementation/Data%20requirements%20and%20to-dos.md) | Backend / MCP data architecture: deterministic read methods, core entities, source/freshness envelopes, traceability from product flows, implementation gaps, and build order. |
| [Workflow entrypoint runner](dev/implementation/workflow-entrypoint/run-workflow-usage.md) | Supported Analyze → Propose runner command, generated run-root shape, validation semantics, and agent handoff rules. |
| [Workflow harness](dev/implementation/workflow-harness/) | Deterministic validators, fixtures, quality gates, safe-parallelization metadata, and demo run records for asset diligence / oracle Analyze → Propose workflows. |
| [UI primitives](dev/ui-primitives/) | Word-based component drafts. These follow the canonical flow docs; they do not define product logic independently. |
| [Foundation planning archive](dev/planning/foundation/) | Historical planning and merge artifacts. These may mention old folders, fixed benchmark tables, or standalone tokenized-security leverage; they are not current canonical docs. |
