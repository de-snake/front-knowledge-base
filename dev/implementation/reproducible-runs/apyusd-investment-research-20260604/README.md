# Reproducible run — apyUSD investment research dossier

This package restores the earlier apyUSD report style: a methodology-guided investment research dossier, not the current Analyze → Propose formatting harness.

Start with [`RESULT.md`](RESULT.md). It is the full analyst-readable report.

## Why this package exists

The USDat / sUSDat harness demo is useful for proving that the workflow runner and validators can scaffold and re-check a structured run. It is not the best first-click example of a rich investment-risk note.

This apyUSD package shows the richer path: evidence first, then a readable analyst synthesis that follows the asset-specific mining methodology directly.

## Contents

- `RESULT.md` — primary human-readable apyUSD risk note.
- `input.json` — scoped run input and artifact map.
- `REPRODUCE.md` — compact reproduction handoff that points to the canonical workflow docs.
- `run/methodology.md` — asset-specific mining methodology used by the run.
- `run/tokens/eth-mainnet-apyusd/technical-report.md` — source-linked technical dossier.
- `run/tokens/eth-mainnet-apyusd/research/` — stage research notes and raw onchain snapshots.
- `run/tokens/eth-mainnet-apyusd/verification.md` — verification checklist for the dossier.

## Revalidate package integrity

From the repository root:

```bash
python3 dev/tools/validate_research_package.py \
  dev/implementation/reproducible-runs/apyusd-investment-research-20260604
```

Expected result:

```text
Status: pass
```

## Reproduce the report style

Follow [`REPRODUCE.md`](REPRODUCE.md). The important boundary is that this is not a deterministic renderer. It is a research workflow: gather evidence, write technical dossier, rewrite into an analyst-readable risk note, then verify source coverage and missing-data behavior.
