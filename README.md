# Gearbox Product Docs Vault

This vault is the primary source for Gearbox front/product knowledge: user research, decision flows, agent-facing reasoning rules, UI primitive inputs, and the data gaps that must be solved before implementation.

Canonical loop: `Discover → Analyze → Propose → Preview → Execute → Monitor`.

Canonical flow docs live in `user-flows/`. The legacy `JTBDs/` and `User flows/` folders have been removed; use git history or planning artifacts only if old source material is needed for archaeology.

Current product-flow coverage is sufficient to move into the data-requirements compilation pass: Pool deposit, Pool monitoring, Credit Account opening, Credit Account monitoring, and the RWA leverage overlay are canonical. A cross-position / Portfolio flow is intentionally deferred until there is a complete draft; it is not a blocker for compiling Gearbox-side data requirements from the current product docs.

## Foundations

| Document | Description |
| --- | --- |
| [Basic info and definitions](Basic%20info%20and%20definitions.md) | Defines core Gearbox concepts, yield sources, and the canonical six-stage loop. |
| [Personas and audience](Personas%20and%20audience.md) | Defines the LP and Credit Account operator personas, loss vectors, and agent-as-reader assumptions. |
| [Benchmarks and tresholds for metrics](Benchmarks%20and%20tresholds%20for%20metrics.md) | Sets green/yellow/red operating thresholds for pool and Credit Account monitoring. |
| [Data requirements and to-dos](Data%20requirements%20and%20to-dos.md) | Backend-facing punch list for feeds, endpoints, implementation hints, and unresolved data gaps. |

## Decision axes

| Document | Description |
| --- | --- |
| [Entry points](Entry%20points.md) | Explains session modes: first-time decision, routine monitoring, and emergency response. |
| [Three-layer progressive disclosure](Three-layer%20progressive%20disclosure.md) | Defines the Glance / Analyze / Act hierarchy for screens and agent responses. |

## Build-facing contract bridge

| Document | Description |
| --- | --- |
| [Data contracts](Data%20contracts.md) | Product-level contract registry: what each stage must hand off, which data is protocol-backed, and which fields require indexer / issuer / user-policy sources. |
| [Preview contract](Preview%20contract.md) | Defines Preview as the hard execution gate: before/after state, warnings, pass/fail rules, and handoff to Execute. |
| [Agent execution boundaries](Agent%20execution%20boundaries.md) | Defines what the agent can read, propose, preview, execute with human approval, automate, or never do. |

## Canonical user flows

| Document | Description |
| --- | --- |
| [Pool deposit](user-flows/Pool%20deposit.md) | LP entry flow from opportunity discovery through deposit execution and monitor handoff. |
| [Pool deposit — reference](user-flows/Pool%20deposit%20-%20reference.md) | Drill material for Pool deposit: oracle types, curator diligence, risk layers, and IC decision palette. |
| [Pool monitoring](user-flows/Pool%20monitoring.md) | LP ownership flow: recurring checks, drift routing, action proposal, preview, and execution. |
| [Pool monitoring — reference](user-flows/Pool%20monitoring%20-%20reference.md) | Drill material for LP action classes, oracle triggers, and agent continuity log mechanics. |
| [Credit Account opening](user-flows/Credit%20Account%20opening.md) | Credit Account entry flow from strategy discovery through leveraged-position execution and monitor handoff. |
| [Credit Account opening — reference](user-flows/Credit%20Account%20opening%20-%20reference.md) | Drill material for IRM, structural risk, RWA compliance, route selection, and multicall preview mechanics. |
| [Credit Account monitoring](user-flows/Credit%20Account%20monitoring.md) | Credit Account ownership flow: safety, yield, rule changes, operational mechanics, oracle / RWA drift, emergency routing, and action execution. |
| [Credit Account monitoring — reference](user-flows/Credit%20Account%20monitoring%20-%20reference.md) | Drill material for CA action classes, emergency mode, HF attribution, oracle triggers, and agent continuity. |
| [RWA leverage](user-flows/RWA%20leverage.md) | RWA-specific overlay for Credit Account opening and monitoring. Treats tokenized securities as a CA variant with issuer, redemption, and compliance constraints. |

## UI primitives

| Folder | Description |
| --- | --- |
| [ui-primitives](ui-primitives/) | Word-based component drafts. These follow the canonical flow docs; they do not define product logic independently. |

## Planning artifacts

| Folder | Description |
| --- | --- |
| [.planning/foundation](.planning/foundation/) | Archived foundation planning and merge artifacts. These files may mention pre-merge `JTBDs/`, `User flows/`, Tier 4 user-flow, or Tier 5 UI-primitive structures as historical source state; they are not current canonical docs. |
