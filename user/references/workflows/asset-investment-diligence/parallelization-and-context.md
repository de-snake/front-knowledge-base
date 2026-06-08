# Parallelization and context-control plan

This workflow is designed so the parent agent coordinates the run while subagents do bounded work. The goal is to avoid shared context bloat, preserve reasoning quality, and prevent reusable research from being mixed into one-off report forms.

## Parent-agent responsibilities

The parent agent owns:

- user scope and constraints;
- scope decomposition into asset, platform, product delta, and formatter layers;
- workflow stage graph;
- subagent task spawning;
- artifact path registry;
- final cross-candidate reasoning;
- validation and user-facing summary.

The parent agent should not own:

- raw explorer dumps;
- raw X results;
- full contract source;
- full research logs;
- per-asset/platform/product evidence expansion unless auditing a disputed field.

## Subagent responsibilities

A subagent owns one bounded stage unit:

- one scope decomposition for S0;
- one asset baseline for S1;
- one platform baseline for S1P;
- one product/combination delta for S2;
- one form/report generation for S2F;
- one PT market product delta for S3;
- one asset/platform/product social lane for S4.

Subagents write artifacts to disk. They return a compressed handoff, not full notes.

Research subagents write reusable facts. Formatter subagents write presentation artifacts from those facts. Do not ask a formatter to secretly become the only source of a new material fact.

## Parallelizable stages

### S0 — Scope decomposition

Parallel unit: usually the whole request.

Run once before research unless the user submits many unrelated opportunities. S0 is cheap and should happen before spawning asset/platform/product workers.

### S1 — Asset baseline research

Parallel unit: one asset.

Safe to parallelize because:

- asset evidence collection is independent;
- each asset writes to a separate `research-library/assets/<asset-slug>/` directory;
- platform/product conclusions are not allowed in S1.

Suggested concurrency:

- 2–3 subagents for normal runs;
- 4 subagents only if API/rate-limit pressure is low.

Parent handoff into each subagent:

- token address, chain, symbol, intended use;
- `research-composition-methodology.md` and relevant pillar methodology path;
- output directory;
- required file list.

Parent return expected:

- artifact paths;
- five strongest numeric facts;
- top asset-layer risks;
- blocking unknowns;
- volatile fields;
- validation status.

### S1P — Platform baseline research

Parallel unit: one platform mechanism.

Safe to parallelize because:

- platform mechanics are independent across protocols;
- each platform writes to `research-library/platforms/<platform-slug>/`;
- product-instance conclusions are not allowed in S1P.

Dependency:

- S0 must identify the platform slug and mechanism.

Suggested concurrency:

- 2–3 subagents.

### S2 — Product / combination delta research

Parallel unit: one product instance.

Safe to parallelize because:

- each product has its own vault/market/PT/pool/route identity;
- each product writes to `research-library/products/<platform-slug>/<asset-slug>/<product-slug>/`;
- each product delta inherits asset and platform artifacts by path instead of copying them.

Dependencies:

- Asset baseline exists or is explicitly marked stale/review-required.
- Platform baseline exists or is explicitly marked stale/review-required.

Suggested concurrency:

- 2–3 subagents.

### S2F — Form/report generation

Parallel unit: one requested form.

Safe to parallelize because:

- each form writes to `forms/<form-slug>/`;
- form output is presentation, not canonical research storage;
- each form declares its inputs in `composition-manifest.json`.

Dependency:

- Relevant asset/platform/product artifacts exist.

Important:

- If the form writer discovers a new material source fact, it must be written back into the correct research artifact before final verification.

### S3 — PT market/economics product delta

Parallel unit: one PT market.

Safe to parallelize because:

- each PT market has independent Pendle market identity;
- each PT product delta writes to a separate product directory;
- shared Pendle platform baseline is inherited by path without parent context expansion.

Dependencies:

- Underlying asset baseline exists.
- Pendle platform baseline exists.

Suggested concurrency:

- 2–3 subagents.

### S4 — X/social mining

Parallel unit: one asset/platform/product social scope.

Safe to parallelize because:

- each X search lane is independent;
- raw social results are the largest context-bloat risk, so they should stay inside subagents;
- parent only needs return models, risk narratives, points mechanics, and artifact path.

Dependencies:

- Relevant research artifacts exist.

Suggested concurrency:

- up to 3 subagents, matching the current Hermes delegated batch limit.

Important:

- S4 subagents must not call X write actions.
- S4 subagents must mark degraded citations instead of forcing unsupported certainty.

## Serial stages

### S5 — X/social synthesis

Must run serial after S4.

Reason:

- it reasons across all social artifacts;
- it identifies contradictions, common narratives, and source-quality boundaries;
- parallel synthesis would duplicate cross-scope reasoning and create conflicting summaries.

Context-control rule:

- read each S4 artifact's executive read, return models, risk narratives, and source index;
- do not paste all X source details into the synthesis artifact.

### S6 — Quantitative underwriting

Must run serial after asset/platform/product/social inputs exist.

Reason:

- expected-loss priors and points scenarios must be consistent across candidates;
- inherited asset risk, inherited platform risk, and product-specific risk must be separated;
- risk-adjusted returns are comparative;
- decision statuses depend on common hurdle rates and position-size assumptions.

Context-control rule:

- use S1/S1P/S2/S3/S5 summary fields and direct numeric fields;
- only read full upstream artifacts when a number, risk prior, or source claim needs audit.

### S7 — Final verification

Must run serial after all writes.

Reason:

- verification observes the final artifact set;
- workspace and cross-link checks require stable files;
- it verifies no formatter report is the only location of a material source fact.

## Delegation map

Use delegated workers for:

- S1 asset baseline research.
- S1P platform baseline research.
- S2 product-delta research.
- S2F form/report generation.
- S3 PT product-delta research.
- S4 X/social mining.

Avoid delegated workers for:

- S0 if the decomposition is small enough for the parent.
- S5 synthesis if the parent already has the scope registry.
- S6 quantitative underwriting, unless the subagent is given all final stage summaries and returns a draft that parent verifies.
- S7 final verification.

## Context budget rules

For subagent prompts:

- Include scope and output contract.
- Include only immediate predecessor artifact paths.
- Include validation requirements.
- Do not include full prior-stage content unless the subagent cannot read local files.

For parent synthesis:

- Read indexes first.
- Read executive sections before technical appendices.
- Read source maps only when validating claims.
- Keep raw data out of parent context.

## Handoff compression standards

A valid handoff contains:

- artifact path;
- status;
- key numbers;
- top risks by layer;
- blockers;
- validation result.

A poor handoff contains:

- raw search results;
- raw ABI/source dumps;
- long copied sections from reports;
- unsupported labels like `healthy`, `risky`, or `good yield` without numbers.

## Failure and recovery

If a subagent crashes:

1. Inspect the task scope and output paths.
2. Check whether partial artifacts were written.
3. Recover manually or respawn the same bounded task.
4. Run the stage validator before marking complete.
5. Add a recovery note to the verification artifact.

If a stage blocks on missing data:

- mark the missing input and decision effect;
- do not silently replace it with a qualitative label;
- continue downstream only if the methodology allows a conservative expected-loss haircut.

If downstream reasoning disagrees with upstream evidence:

- parent expands the specific source artifact;
- parent audits the number or source claim;
- parent patches the upstream artifact if it is wrong;
- parent reruns affected validation.
