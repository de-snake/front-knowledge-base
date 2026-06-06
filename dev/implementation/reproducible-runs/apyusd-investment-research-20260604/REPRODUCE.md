# Reproduce — apyUSD investment research dossier

This file is the run handoff, not a replacement prompt.

Use the canonical research workflow, then apply the run-specific input and methodology below.

## Canonical workflow

Primary workflow docs:

- [`user/references/workflows/asset-investment-diligence/runbook.md`](../../../../user/references/workflows/asset-investment-diligence/runbook.md)
- [`user/references/workflows/asset-investment-diligence/stage-contracts.md`](../../../../user/references/workflows/asset-investment-diligence/stage-contracts.md)
- [`user/references/workflows/asset-investment-diligence/output-structure.md`](../../../../user/references/workflows/asset-investment-diligence/output-structure.md)

Those docs define the research sequence, evidence-first staging, source maps, missing-data behavior, and final analyst report expectations. Do not duplicate that process here.

## Run-specific inputs

Use [`input.json`](input.json):

- chain: Ethereum mainnet / `chain_id: 1`
- token: `0x38EEb52F0771140d10c4E9A9a72349A329Fe8a6A`
- symbol: `apyUSD`
- issuer/protocol hint: `Apyx`
- report date: `2026-06-04 UTC`

Run-specific methodology snapshot:

- [`run/methodology.md`](run/methodology.md)

## Artifact contract

A reproduced package should regenerate these artifacts:

1. `run/tokens/eth-mainnet-apyusd/research/onchain-admin.md`
2. `run/tokens/eth-mainnet-apyusd/research/issuer-backing-security.md`
3. `run/tokens/eth-mainnet-apyusd/research/transfer-liquidity-oracle-governance.md`
4. `run/tokens/eth-mainnet-apyusd/technical-report.md`
5. `RESULT.md`
6. `run/tokens/eth-mainnet-apyusd/verification.md`

## Verification

From the repository root:

```bash
python3 dev/tools/validate_research_package.py \
  dev/implementation/reproducible-runs/apyusd-investment-research-20260604
```

Expected result:

```text
Status: pass
```

Manual acceptance bar: source IDs resolve, material claims are supported by the technical dossier or research notes, unresolved backing/audit/redemption/liquidity/control details remain visible, and `RESULT.md` stays a risk note rather than an investment recommendation.
