# Reproducible run — PRIME investment research dossier

This package restores the older rich Markdown report style for Hastra PRIME: a methodology-guided investment research dossier, not the Analyze → Propose formatting harness.

Start with [`RESULT.md`](RESULT.md). It is the full analyst-readable report.

## Contents

- `RESULT.md` — primary human-readable PRIME risk note.
- `input.json` — scoped run input and artifact map.
- `REPRODUCE.md` — compact reproduction handoff that points to the canonical workflow docs.
- `run/methodology.md` — asset-specific mining methodology used by the old run.
- `run/technical-reports/eth-mainnet-prime.md` — source-linked technical dossier.
- `run/research/eth-mainnet-prime/` — stage research notes and raw snapshots.
- Supporting layer: explicit missing-layer boundaries for X/social and quantitative/PT underwriting.

## Revalidate package integrity

From the repository root:

```bash
python3 dev/tools/validate_research_package.py \
  dev/implementation/reproducible-runs/prime-investment-research-20260604
```

Expected result:

```text
Status: pass
```

## Boundary

This is a research dossier and risk note. It is not an investment recommendation, suitability verdict, position-size recommendation, or execution instruction.
