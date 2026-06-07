# Reproducible run — USDat / sUSDat collateral Analyze → Propose

This folder contains one public demo package.

For review, start with [`RESULT.md`](RESULT.md). That is the human-readable result.

The `run/` subtree is the reproduction bundle behind the report. It keeps the filled analysis artifacts, source evidence, manifests, and final verification files needed to revalidate the run locally.

## Contents

- `RESULT.md` — human-readable review report.
- `input.json` — input used by the runner.
- `run/` — reproducibility bundle and supporting artifacts.
- `run/x-research/` — old-run social/points/PT expectation notes for USDat and sUSDat.
- `run/investment-analysis/` — old-run quantitative PT risk/return report and underwriting methodology.
- `run/pt-markets/` — old Pendle PT technical dossiers and raw Pendle snapshots.
- `run/agentic-flow/analyze-and-propose.md` — readable parent Analyze → Propose return.
- `run/agentic-flow/analyze-and-propose.json` — validator sidecar for the parent return.

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

The command regenerates validation side files inside `run/`.

## Important boundary

This is an Analyze → Propose demo only. Passing validation does not make either asset ready for Preview or Execute.
