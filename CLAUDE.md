# CLAUDE.md

Operating contract for agents using or editing this public Gearbox product knowledge snapshot.

## Purpose

`front-knowledge-base` contains:

- canonical runtime knowledge for Gearbox user flows and agent reasoning;
- one reproducible Analyze → Propose demo run;
- minimal runner / validator code needed to re-check that demo.

Do not add planning history, Kanban cards, fixture matrices, or internal audit notes to public `main` unless explicitly requested.

## Canonical loop

```text
Discover → Analyze → Propose → Preview → Execute → Monitor
```

Preview and Execute require explicit user intent and sufficient live inputs. Analysis artifacts alone must not imply execution readiness.

## Runtime knowledge layout

- `user/foundations/` — shared terms, personas, monitoring principles.
- `user/decision/` — session modes and display / response hierarchy.
- `user/flows/` — canonical Pool and Credit Account flows.
- `user/references/mechanics/` — reusable mechanics across flows.
- `user/references/workflows/` — executable worker contracts for asset diligence and oracle analysis.

## Reproducible demo

Use the demo package at:

```text
dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/
```

Revalidate from the repository root:

```bash
python3 dev/tools/run_workflow.py analyze-propose \
  --input dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/input.json \
  --run-root dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/run \
  --mode validate \
  --resume \
  --format markdown
```

Expected result: asset, oracle, and combined validation all pass.

## Rules for future additions

- Add runtime-facing knowledge under `user/`.
- Add only minimal reproducibility instructions under `dev/implementation/`.
- Keep one-off scratch inputs and generated temporary runs out of git.
- Keep public result pages concise: result, evidence pointers, reproduction command, and remaining blockers.
- Do not promote internal planning or test fixtures to public `main` unless the user asks for an engineering-audit package.
