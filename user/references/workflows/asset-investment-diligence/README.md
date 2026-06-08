# Asset investment diligence agent workflow

This folder turns the current asset-risk diligence process into an executable agent workflow.

The purpose is to let a future agent run the process without loading every raw artifact into the parent context. Each stage has a bounded input contract, a bounded output contract, and explicit parallelization rules.

The workflow now treats research as composable evidence, not as one-off reports. Researchers produce reusable asset, platform, and product-delta artifacts. Formatters then apply the requested report form on top of those artifacts.

## What this workflow does

It transforms a token / platform / product opportunity scope into reusable research artifacts and, only after that, into a decision-grade investment analyst report.

The pipeline separates reusable researcher output from formatter output:

1. Scope decomposition into asset baseline, platform baseline, product delta, and requested form.
2. Reuse or refresh asset baseline research.
3. Reuse or refresh platform baseline research.
4. Research the lightweight product / combination delta.
5. Apply the requested form: analyst report, investment memo, UI summary, or public page.
6. Quantitative underwriting and final verification, when a capital decision is requested.

## Files

- `workflow.json` — machine-readable stage graph, dependencies, parallelization, subagent policy, and output paths.
- `stage-contracts.md` — exact input/output contract for every stage.
- `research-composition-methodology.md` — canonical separation between researcher output and form/report output, plus asset/platform/product-delta storage rules.
- `asset-issuer-pillar-methodology.md` — granular Steakhouse-style Asset Layer / Issuer pillar research method: Social, Decentralization, Technical, control map, gates, and Gearbox path impact.
- `parallelization-and-context.md` — what the parent agent can parallelize, what must stay serial, and how to avoid context bloat.
- `subagent-prompts.md` — paste-ready prompts for delegated workers.
- `runbook.md` — execution order and validation sequence.
- `output-structure.md` — canonical run folder layout with reusable research-library and formatter-output subfolders.
- `examples/asset-risk-reports-mvp-current-run-map.md` — maps the current asset-risk reports MVP artifacts to the workflow stages.

## Core execution rule

The parent agent should not ingest all raw evidence.

Use this pattern:

- Parent owns the scope, stage graph, and final decision.
- Research subagents own bounded asset, platform, or product-delta research tasks.
- Formatter subagents consume research artifacts; they do not create unsourced facts while formatting.
- Subagents write artifacts to disk and return only:
  - artifact path;
  - verdict;
  - key numbers;
  - blockers;
  - validation result.
- Parent reads indexes and final memos first, then selectively expands source artifacts only when a number or conclusion needs audit.

## When to run each stage

Always start with S0 decomposition from `research-composition-methodology.md`: identify the asset baseline, platform baseline, product delta, and requested form. Reuse existing asset/platform baselines whenever they are still fresh enough for the decision.

- Pure asset question: run S0, S1 if the asset baseline is missing/stale, optional S2F form, then S7.
- Pure platform question: run S0, S1P if the platform baseline is missing/stale, optional S2F form, then S7.
- Asset-on-platform product question: run S0, S1/S1P as needed, S2 product delta, optional S2F form, then S7.
- PT opportunity: run S0, S1 underlying asset, S1P Pendle platform, S3 PT product delta, optional S2F form, S6 if underwriting is requested, then S7.
- Points/social opportunity: add S4 and S5 before S6.
- Evidence pack only: stop after the requested research layers and validation; do not generate a form unless requested.

## Expected final outputs

A complete investment-decision run should end with:

- one returned `<run_artifact_root>/` folder;
- `run-manifest.json` and `index.md` at the run root;
- reusable research under `research-library/assets/`, `research-library/platforms/`, and `research-library/products/`;
- formatter deliverables under `forms/` and underwriting deliverables under `investment-analysis/`;
- composition manifests for every generated form;
- product-delta artifacts for each exact asset-on-platform or PT instance;
- social evidence reports under `x-research/`, if points/social are in scope;
- social synthesis under `x-research/index.md`, if points/social are in scope;
- quantitative methodology and investment analyst report under `investment-analysis/`;
- final verification under `verification/final-investment-analysis-verification.md`.

The user-facing answer should return the run folder path, final index path, reusable asset/platform/product folders, generated form folders, and final verification path.

## Included example status

The included example map records a completed six-stage run for:

- apyUSD / PT-apyUSD 27 Aug 2026;
- apxUSD / PT-apxUSD 05 Nov 2026;
- SampleBaseToken / PT-SampleBaseToken 27 Aug 2026;
- SampleVaultToken / PT-SampleVaultToken 27 Aug 2026.

See `examples/asset-risk-reports-mvp-current-run-map.md` for artifact mapping.
