# Reproducible run — apxUSD investment research dossier

This package restores the older rich Markdown report style for apyx apxUSD: a methodology-guided investment research dossier, not the Analyze → Propose formatting harness.

Start with [`RESULT.md`](RESULT.md). It is the full analyst-readable report.

## Contents

- `RESULT.md` — primary human-readable apxUSD risk note.
- `input.json` — scoped run input and artifact map.
- `REPRODUCE.md` — compact reproduction handoff that points to the canonical workflow docs.
- `run/methodology.md` — asset-specific mining methodology used by the old run.
- `run/technical-reports/eth-mainnet-apxusd.md` — source-linked technical dossier.
- `run/research/eth-mainnet-apxusd/` — stage research notes and raw snapshots.
- Supporting layer: old-run X/social research, PT-market reports, quantitative risk/return underwriting.

## Revalidate package integrity

From the repository root:

```bash
python3 dev/tools/validate_research_package.py \
  dev/implementation/reproducible-runs/apxusd-investment-research-20260604
```

Expected result:

```text
Status: pass
```

## Boundary

This is a research dossier and risk note. It is not an investment recommendation, suitability verdict, position-size recommendation, or execution instruction.
