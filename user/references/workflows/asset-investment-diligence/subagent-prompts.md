# Subagent prompts

These are paste-ready prompts for delegated workers. Replace bracketed fields before use.

## Shared stage-worker return contract

Every stage worker must return a machine-checkable compressed handoff. Include explicit fields for `status`, `run_artifact_root`, `artifact_paths`, `verification_path`, `blockers`, `blocked_scopes`, `review_required_scopes`, `dominant_blockers`, `live_input_blockers`, `not_in_scope`, `null_fields`, and `commands_run` when applicable.

Use explicit `null` for unknown values and `not_in_scope` for fields that do not apply. Do not omit required fields because they are inconvenient, and do not handwave final verification with phrases like "looks good" or "not verified" without a concrete verification artifact, command, or blocker.

Research workers write reusable evidence artifacts. Formatter workers create report shapes from those artifacts. A formatter must not create new source facts unless it also writes them back into the correct research artifact.

## S0 prompt — Scope decomposition and reuse plan

Goal:

Decompose `[user_question]` into asset baseline, platform baseline, product delta, and requested form before research starts.

Context:

- Run artifact root: `[run_artifact_root]`.
- Existing research-library root, if any: `[research_library_root]`.
- Read `research-composition-methodology.md`, `output-structure.md`, and `stage-contracts.md`.
- Known identifiers:
  - asset symbol/address: `[asset_scope]`
  - platform: `[platform_scope]`
  - product/vault/market/PT/maturity: `[product_scope]`
  - requested form: `[requested_form]`

Instructions:

1. Decide whether each layer is needed: asset, platform, product delta, form.
2. Check whether an existing asset/platform baseline can be reused, must be refreshed, or must be created.
3. Identify volatile fields that must be refreshed before underwriting.
4. Write:
   - `scope-decomposition.json`
   - `scope-decomposition.md`
   - update `run-manifest.json` layer plan if it exists.
5. Return compressed handoff only:
   - decomposition artifact paths;
   - asset action: reuse/refresh/create;
   - platform action: reuse/refresh/create;
   - product action: create_or_refresh;
   - missing identifiers;
   - blockers.

## S1 prompt — Asset baseline research

Goal:

Create or refresh the reusable asset baseline for `[symbol]` on `[chain]` at `[token_address]`.

Context:

- Run artifact root: `[run_artifact_root]`.
- Asset artifact directory: `[asset_artifact_dir]`, for example `research-library/assets/ethereum-usdc-a0b86991`.
- Read `research-composition-methodology.md` and `asset-issuer-pillar-methodology.md`.
- Asset scope:
  - chain_id: `[chain_id]`
  - chain: `[chain]`
  - symbol: `[symbol]`
  - token_address: `[token_address]`
  - intended_use: `[intended_use]`

Instructions:

1. Collect asset-only evidence: issuer/control plane, on-chain admin/proxy/roles, backing/NAV/reserves, mint/burn/redeem, transfer restrictions, freeze/blacklist/pause, oracle/accounting implications intrinsic to the asset, audits/incidents.
2. Write:
   - `[asset_artifact_dir]/scope.json`
   - `[asset_artifact_dir]/asset-baseline.md`
   - `[asset_artifact_dir]/asset-baseline.json`
   - `[asset_artifact_dir]/pillars/issuer.md`
   - `[asset_artifact_dir]/sources.md`
   - `[asset_artifact_dir]/refresh.md`
   - `[asset_artifact_dir]/verification.md`
3. Include source URLs, dates, confidence, no-result proofs, gates, and refresh rules.
4. Do not include platform-specific product conclusions, curator claims, vault parameters, PT maturity facts, or investment recommendations.
5. Return only a compressed handoff:
   - artifact paths;
   - five strongest numeric facts;
   - top asset-layer risks;
   - blockers;
   - volatile fields;
   - validation status.

Do not return raw contract source or raw API dumps to the parent.

## S1P prompt — Platform baseline research

Goal:

Create or refresh the reusable platform baseline for `[platform_slug]`.

Context:

- Run artifact root: `[run_artifact_root]`.
- Platform artifact directory: `[platform_artifact_dir]`, for example `research-library/platforms/morpho-vaults`.
- Read `research-composition-methodology.md` and `stage-contracts.md`.
- Platform scope:
  - platform family: `[platform_family]`
  - mechanism: `[platform_mechanism]`
  - chain(s): `[chains]`

Instructions:

1. Collect platform-only evidence: architecture, factories/registries/routers/adapters, governance/admin/guardian powers, curator/manager/allocator model, generic liquidation/redemption/maturity/oracle mechanics, incident history, and where product-specific parameters live.
2. Write:
   - `[platform_artifact_dir]/scope.json`
   - `[platform_artifact_dir]/platform-baseline.md`
   - `[platform_artifact_dir]/platform-baseline.json`
   - `[platform_artifact_dir]/mechanics.md`
   - `[platform_artifact_dir]/risk-map.md`
   - `[platform_artifact_dir]/product-inspection-guide.md`
   - `[platform_artifact_dir]/sources.md`
   - `[platform_artifact_dir]/refresh.md`
   - `[platform_artifact_dir]/verification.md`
3. Do not conclude on a specific vault, market, maturity, collateral list, live cap, or liquidity snapshot.
4. Return only a compressed handoff:
   - artifact paths;
   - top platform risks;
   - product inspection points;
   - blockers;
   - validation status.

## S2 prompt — Product / combination delta research

Goal:

Research the exact product instance `[product_scope]` by composing `[asset_baseline_path]` and `[platform_baseline_path]`, then adding only the product-specific delta.

Context:

- Run artifact root: `[run_artifact_root]`.
- Product artifact directory: `[product_artifact_dir]`, for example `research-library/products/morpho-vaults/ethereum-usdc-a0b86991/morpho-vault-usdc-abcdef12`.
- Asset baseline: `[asset_baseline_path]`.
- Platform baseline: `[platform_baseline_path]`.
- Product identifiers:
  - product type: `[product_type]`
  - primary address: `[primary_address]`
  - market/vault/PT/SY/pool/route/maturity: `[product_identifiers]`

Instructions:

1. Read the asset and platform baselines first.
2. Collect only product-specific facts: exact addresses, controller/curator/allocator/manager, oracle, caps, fees, LLTV, collateral list, queues, maturity, settlement path, liquidity, address eligibility, and live parameters.
3. Explain which inherited asset risks and platform risks become active in this product.
4. Write:
   - `[product_artifact_dir]/scope.json`
   - `[product_artifact_dir]/product-delta.md`
   - `[product_artifact_dir]/product-delta.json`
   - `[product_artifact_dir]/live-parameters.json`
   - `[product_artifact_dir]/sources.md`
   - `[product_artifact_dir]/refresh.md`
   - `[product_artifact_dir]/verification.md`
5. Return compressed handoff only:
   - artifact paths;
   - inherited artifact paths;
   - live parameters;
   - active inherited risks;
   - product-specific blockers;
   - stale/volatile fields;
   - validation status.

## S2F prompt — Form/report generation

Goal:

Create `[requested_form]` from existing research artifacts without inventing new source facts.

Context:

- Run artifact root: `[run_artifact_root]`.
- Form artifact directory: `[form_artifact_dir]`, for example `forms/gearbox-collateral-memo-usdc-morpho-2026-06-08`.
- Asset baseline inputs: `[asset_baseline_paths]`.
- Platform baseline inputs: `[platform_baseline_paths]`.
- Product-delta inputs: `[product_delta_paths]`.
- Requirements brief: `[requirements_brief_path]`.

Instructions:

1. Write `[form_artifact_dir]/composition-manifest.json` before the report.
2. Write the requested report, usually `[form_artifact_dir]/analyst-report.md`.
3. Preserve asset/platform/product separation in the report.
4. Cite source research artifacts by path.
5. If you discover a new source fact while writing, record it in `facts_that_must_be_written_back` and do not mark final verification pass until it is moved to the right research artifact.
6. Write `[form_artifact_dir]/verification.md`.
7. Return compressed handoff only:
   - form path;
   - composition manifest path;
   - inherited research inputs;
   - facts_that_must_be_written_back;
   - blockers;
   - verification result.

## S3 prompt — PT market/economics product delta

Goal:

Identify and analyze the exact Pendle PT market for `[symbol]` maturity `[maturity_date]` on `[chain]` as a product-delta artifact.

Context:

- Run artifact root: `[run_artifact_root]`.
- Product artifact directory: `[product_artifact_dir]`, for example `research-library/products/pendle-pt-markets/ethereum-usdc-a0b86991/pendle-pt-usdc-2026-08-27-abc12345`.
- Underlying asset baseline: `[asset_baseline_path]`.
- Pendle platform baseline: `[platform_baseline_path]`.
- PT scope:
  - underlying symbol: `[symbol]`
  - underlying token address: `[token_address]`
  - chain_id: `[chain_id]`
  - target maturity: `[maturity_date]`
  - user days label: `[days_label]`

Instructions:

1. Identify the exact Pendle market, PT, SY, YT, maturity, accounting asset, and output asset.
2. Fetch/read current market snapshot evidence from approved/local sources.
3. Calculate gross ROI, simple APR, compound APY, break-even accounting-asset drawdown, and liquidity.
4. Write the product-delta files required by S2.
5. Separate inherited asset risk, inherited Pendle platform risk, and PT-market-specific risk.
6. Return compressed handoff only:
   - artifact paths;
   - market/PT/SY/YT addresses;
   - maturity;
   - PT price;
   - accounting asset price;
   - implied APY;
   - liquidity;
   - break-even drawdown;
   - blockers.

## S4 prompt — X/social mining

Goal:

Collect X/social evidence for `[scope_name]` covering points, yield, PT return, depeg/stress, redemption, queue, liquidity, and risk narratives.

Context:

- Run artifact root: `[run_artifact_root]`.
- Research artifact paths:
  - `[asset_baseline_paths]`
  - `[platform_baseline_paths]`
  - `[product_delta_paths]`
- Output: `x-research/x-research-[scope-slug].md`.
- Use Hermes `x_search` first.
- X access is read-only. Do not post, like, follow, DM, or perform account actions.

Instructions:

1. Search exact ticker, product label, issuer/project variants, points/program names, yield terms, PT APY/maturity terms, and risk/stress terms.
2. Write sections: Scope, Executive read, Query log, Distinct return models, Distinct risk narratives, Source index, Signal vs noise, Open threads.
3. Each material claim must have handle, date/search-window date, and status URL/ID; otherwise mark `citation_degraded`.
4. Separate social speculation from research-artifact facts.
5. Return compressed handoff only: artifact path, return models, risk narratives, points mechanics, source count, degraded-citation count, validation status.

## S5 prompt — X/social synthesis

Goal:

Synthesize all X/social artifacts into one cross-scope social expectations overlay.

Context:

- Run artifact root: `[run_artifact_root]`.
- Input artifacts: `[x_artifact_paths]`.
- Output: `x-research/index.md`.
- Verification: `verification/final-x-research-points-yield-verification.md`.

Instructions:

1. Synthesize return models, not raw X posts.
2. Separate social estimates, local/research-artifact facts, and degraded citations.
3. Cover points uncertainty, yield uncertainty, issuer/redemption/freeze/control risk by layer, PT liquidity/maturity/accounting risk, and crowded farming/leverage/unwind risk.
4. Identify contradictions and likely disagreement sources.
5. Validate that all scoped artifacts are represented and no extra asset/product/maturity is introduced.
6. Return compressed handoff: synthesis path, main return narratives, main risk narratives, contradictions, verification result.

## S6 prompt — Quantitative underwriting

Goal:

Build a decision-grade investment analysis from asset baselines, platform baselines, product deltas, form reports, and social synthesis.

Context:

- Run artifact root: `[run_artifact_root]`.
- Asset baseline paths: `[asset_baseline_paths]`.
- Platform baseline paths: `[platform_baseline_paths]`.
- Product-delta paths: `[product_delta_paths]`.
- Form report paths, if any: `[form_report_paths]`.
- Social synthesis, if applicable: `[x_synthesis_path]`.
- Methodology output: `investment-analysis/quantitative-underwriting-methodology.md`.
- Report output: `investment-analysis/investment-analyst-report-points-pt-risk-return.md`.
- Index output: `investment-analysis/index.md`.
- Position size: `[position_size]`.
- Base hurdle: `[base_hurdle]`.
- Opportunistic hurdle: `[opportunistic_hurdle]`.

Instructions:

1. Define or reuse methodology for PT ROI/APR, points EV/ROI/APR, expected loss, price-stability certainty, and risk-adjusted return.
2. Separate inherited asset risk, inherited platform risk, and product-specific risk in expected-loss assumptions.
3. Use live product parameters only if they are fresh according to product `refresh.md`.
4. Write the methodology, report, and index outputs.
5. Return compressed handoff: output paths, risk-adjusted returns, expected-loss priors, points break-even, price-stability scores, decision statuses, live input blockers.

## S7 prompt — Final verification

Goal:

Verify the complete workflow run before the parent reports completion.

Context:

- Run artifact root: `[run_artifact_root]`.
- Manifest: `run-manifest.json`.
- Output structure spec: `user/references/workflows/asset-investment-diligence/output-structure.md`.
- Stage contracts: `user/references/workflows/asset-investment-diligence/stage-contracts.md`.

Instructions:

1. Verify required files exist for each asset, platform, product, form, social, underwriting, and verification scope.
2. Verify cross-links resolve.
3. Verify no research-layer artifact makes unsupported allocation conclusions.
4. Verify no form-layer artifact is the only location of a material source fact.
5. Verify volatile product fields are marked and refreshed before underwriting.
6. Write `verification/final-investment-analysis-verification.md`.
7. Return compressed handoff: final verification path, pass/fail status, unresolved blockers, commands/checks run.
