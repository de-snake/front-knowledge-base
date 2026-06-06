# Reproduce — apyUSD research note

This is only the run-specific handoff. It intentionally does not restate the research workflow.

## Use the canonical workflow

Follow the asset investment diligence workflow:

- [`runbook.md`](../../../../user/references/workflows/asset-investment-diligence/runbook.md)
- [`stage-contracts.md`](../../../../user/references/workflows/asset-investment-diligence/stage-contracts.md)
- [`output-structure.md`](../../../../user/references/workflows/asset-investment-diligence/output-structure.md)

Those docs define the evidence staging, source maps, missing-data behavior, and analyst report shape.

## Apply this run input

Use [`input.json`](input.json):

- chain: Ethereum mainnet / `chain_id: 1`
- token: `0x38EEb52F0771140d10c4E9A9a72349A329Fe8a6A`
- symbol: `apyUSD`
- issuer/protocol hint: `Apyx`
- report date: `2026-06-04 UTC`

Use [`run/methodology.md`](run/methodology.md) as the run-specific methodology snapshot.

The included [`RESULT.md`](RESULT.md) and [`run/`](run/) directory are the reference output for this run.
