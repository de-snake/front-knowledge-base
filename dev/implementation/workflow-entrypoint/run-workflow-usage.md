# Analyze → Propose runner usage

This runner is a deterministic scaffold / validation bridge. It does not perform live research, infer investment suitability, or unlock Preview / Execute.

The public repository keeps only the minimal usage needed to reproduce the included demo run.

## Revalidate the included demo

From the repository root:

```bash
python3 dev/tools/run_workflow.py analyze-propose \
  --input dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/input.json \
  --run-root dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/run \
  --mode validate \
  --resume \
  --format markdown
```

Expected output:

```text
Status: pass
Exit code: 0
asset: pass
oracle: pass
combined: pass
```

The command validates the already-filled run artifacts and refreshes validation outputs under the run root.

## Scaffold a fresh local run

For a new private/local run, create an input JSON with the same schema as the demo input, then run:

```bash
python3 dev/tools/run_workflow.py analyze-propose \
  --input <repo-local-input.json> \
  --mode scaffold \
  --agent generic \
  --format markdown
```

The scaffold command creates a temporary run root under `dev/implementation/` and writes the packet / handoff files that an agent can fill.

Do not commit one-off scratch inputs or generated temporary runs unless the goal is to publish a reproducible result package.

## Validation boundary

A passing validation result means the artifacts satisfy the structural / evidence contract. It does not mean the proposal is decision-ready.

Preview / Execute remain blocked unless the filled artifacts also provide all required live inputs: market / Credit Manager, size, leverage, horizon, risk policy, wallet eligibility, and route / liquidation evidence.
