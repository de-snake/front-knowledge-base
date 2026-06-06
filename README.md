# Gearbox Product Knowledge Base

This public repository is a clean snapshot of the current Gearbox front / agent knowledge base.

It contains:

- the canonical runtime knowledge an agent should use for Gearbox user flows;
- one reproducible Analyze → Propose demo run for USDat / sUSDat collateral review;
- the minimal Python runner and validators needed to re-check that demo locally.

It intentionally does not contain planning history, Kanban cards, fixture matrices, or internal audit notes.

## Current status

Read [`STATUS.md`](STATUS.md) for the short progress summary and the demo result.

## Runtime knowledge

### Foundations

| Document | Description |
| --- | --- |
| [Basic info and definitions](user/foundations/Basic%20info%20and%20definitions.md) | Shared Gearbox vocabulary, yield sources, the six-stage loop, and stage handoff rules. |
| [Personas and audience](user/foundations/Personas%20and%20audience.md) | LP and Credit Account operator personas, loss vectors, and agent-as-reader assumptions. |
| [Position risk and monitoring](user/foundations/Position%20risk%20and%20monitoring.md) | Monitoring logic, asset-property risk, missing-data handling, and threshold policy. |

### Decision model

| Document | Description |
| --- | --- |
| [Entry points](user/decision/Entry%20points.md) | Session modes, agent reader behavior, and the Preview / Execute approval boundary. |
| [Three-layer progressive disclosure](user/decision/Three-layer%20progressive%20disclosure.md) | Glance / Analyze / Act hierarchy for screens and agent responses. |

### Canonical flows

| Document | Description |
| --- | --- |
| [Pool deposit](user/flows/Pool%20deposit.md) | LP entry flow from opportunity discovery through execution and monitor handoff. |
| [Pool monitoring](user/flows/Pool%20monitoring.md) | LP ownership flow: recurring checks, drift routing, proposals, Preview, and Execute. |
| [Credit Account opening](user/flows/Credit%20Account%20opening.md) | Credit Account entry flow, including issuer-controlled collateral checks as conditional branches. |
| [Credit Account management](user/flows/Credit%20Account%20management.md) | Ownership / monitoring flow for safety, yield, governance, operations, oracle drift, issuer drift, and actions. |

### References

| Document | Description |
| --- | --- |
| [Mechanics index](user/references/mechanics/) | Stable product mechanics: oracle/liquidity risk, token/curator risk, action palettes, Credit Account risk controls, and continuity logs. |
| [Oracle analysis workflow](user/references/workflows/oracle-analysis/) | Executable oracle/feed analysis workflow and worker contracts. |
| [Asset investment diligence workflow](user/references/workflows/asset-investment-diligence/) | Executable token / PT diligence workflow and worker contracts. |

## Reproducible demo

The current demo package is:

[`dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/`](dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/)

Revalidate it from the repository root:

```bash
python3 dev/tools/run_workflow.py analyze-propose \
  --input dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/input.json \
  --run-root dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/run \
  --mode validate \
  --resume \
  --format markdown
```

Expected result:

```text
Status: pass
Exit code: 0
asset: pass
oracle: pass
combined: pass
```

## Repository layout

```text
front-knowledge-base/
  README.md
  STATUS.md
  AGENTS.md / CLAUDE.md
  user/                               canonical runtime knowledge
  dev/tools/                          minimal runner + validators
  dev/implementation/workflow-entrypoint/run-workflow-usage.md
  dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/
```
