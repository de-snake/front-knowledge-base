# Reproducible run — USDat / sUSDat collateral Analyze → Propose

This folder contains the public reproducible demo package.

## Contents

- `input.json` — input used by the runner.
- `run/` — filled run artifacts and validation reports.
- `RESULT.md` — concise human-readable result.

## Revalidate

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

The command may refresh validation timestamp/report files inside `run/`.

## Important boundary

This is an Analyze → Propose demo only. Passing validation does not make either asset ready for Preview or Execute.
