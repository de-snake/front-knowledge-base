# Reproduce — deSPXA research note

This is only the run-specific handoff. It intentionally does not restate the research workflow.

## Use the canonical workflow

Follow the asset investment diligence workflow:

- [`runbook.md`](../../../../user/references/workflows/asset-investment-diligence/runbook.md)
- [`stage-contracts.md`](../../../../user/references/workflows/asset-investment-diligence/stage-contracts.md)
- [`output-structure.md`](../../../../user/references/workflows/asset-investment-diligence/output-structure.md)

Those docs define the evidence staging, source maps, missing-data behavior, and analyst report shape.

## Apply this run input

Use [`input.json`](input.json):

- chain: Base / `chain_id: 8453`
- token: `0x9c5C365e764829876243d0b289733B9D2b729685`
- symbol: `deSPXA`
- issuer/protocol hint: `Centrifuge / Janus Henderson Anemoy`
- report date: `2026-06-04 UTC`

Use [`run/methodology.md`](run/methodology.md) as the run-specific methodology snapshot.

The included [`RESULT.md`](RESULT.md) and [`run/`](run/) directory are the reference output for this run.
