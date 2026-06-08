# Stage contracts — asset investment diligence workflow

This file defines the agent handoff interface for every stage. A future agent should treat these contracts as mandatory.

## Shared envelope

Every stage artifact should support this summary envelope in the parent-agent response.

All stage output paths in this file are relative to the chosen run artifact root, for example `dev/implementation/<run-slug>/`. The reusable workflow itself lives at `user/references/workflows/asset-investment-diligence/`.

Every run must follow `output-structure.md`: one returned `<run_artifact_root>/` folder, reusable research under `research-library/assets/`, `research-library/platforms/`, and `research-library/products/`, form-layer deliverables under `forms/`, and run-level `run-manifest.json`, `index.md`, and `verification/final-investment-analysis-verification.md`.

```json
{
  "stage_id": "S1_general_asset_mining",
  "scope_id": "eth-mainnet-apxusd",
  "status": "pass | review_required | blocked",
  "artifact_paths": ["tokens/ethereum-sample-vault-token-22222222/analyst-report.md"],
  "key_numbers": [
    {"name": "liquidity", "value": "USD 38,260,000", "source": "..."}
  ],
  "top_risks": [
    {"risk": "primary redemption eligibility", "evidence": "...", "decision_effect": "review_required"}
  ],
  "blocking_unknowns": ["..."],
  "validation": {
    "result": "pass | fail",
    "checks": ["..."]
  }
}
```

The parent should read this envelope before reading the full artifact.

## Research / form separation

Stages must not collapse evidence collection and report formatting.

- Research stages write source-backed asset, platform, and product-delta artifacts.
- Form stages consume those artifacts and generate the requested report shape.
- If a form writer discovers a new source fact, it must be written back into the relevant research artifact before final verification.

Use `research-composition-methodology.md` as the controlling method when this file is ambiguous.

## Research layers

Every opportunity is decomposed before research starts:

```json
{
  "asset_layer": "research-library/assets/<asset-slug>",
  "platform_layer": "research-library/platforms/<platform-slug>",
  "product_delta_layer": "research-library/products/<platform-slug>/<asset-slug>/<product-slug>",
  "form_layer": "forms/<form-slug>"
}
```

- The asset layer answers what the asset is by itself.
- The platform layer answers what the platform does and where to inspect product-specific risk.
- The product delta layer answers what changes for this exact asset-on-platform instance.
- The form layer answers how the user wants the result presented.

Do not re-research asset/platform baselines when a fresh existing artifact can be reused.

## S0 — Scope decomposition and reuse plan

Role: split the user request into asset baseline, platform baseline, product delta, and requested form before delegating research.

Input contract:

- User question or opportunity scope.
- Known asset addresses, platform names, market/vault/PT identifiers, if provided.
- Existing research-library index, if available.

Output contract:

- `scope-decomposition.json`.
- `scope-decomposition.md`.
- Updated `run-manifest.json` layer plan.

Required fields:

- asset slug and whether to `reuse`, `refresh`, or `create`.
- platform slug and whether to `reuse`, `refresh`, or `create`.
- product slug and whether to `create_or_refresh`.
- requested form.
- known volatile fields that must be refreshed before underwriting.

Compression rule:

- Parent should receive only the layer plan, missing identifiers, and blockers.

## S1 — General asset mining

Role: create or refresh the reusable asset baseline for one asset. This is asset-only research; platform/product-specific facts are out of scope.

Input contract:

- `chain_id`.
- `chain_name`.
- `token_address`.
- `symbol`.
- `intended_use`.
- Optional: position context, holder address, size.

Allowed raw data:

- Verified contract source and proxy state.
- RPC reads and explorer state.
- Issuer docs, terms, risk pages, dashboards, audits.
- Market/liquidity data providers.
- Governance, timelock, and Safe state.

Output contract:

- `<asset_artifact_dir>/scope.json`.
- `<asset_artifact_dir>/asset-baseline.md`.
- `<asset_artifact_dir>/asset-baseline.json`.
- `<asset_artifact_dir>/pillars/issuer.md`.
- `<asset_artifact_dir>/sources.md`.
- `<asset_artifact_dir>/refresh.md`.
- `<asset_artifact_dir>/verification.md`.

Required facts:

- Token identity, decimals, implementation/proxy status.
- Issuer/protocol entity.
- Backing/NAV model.
- Transfer restrictions.
- Mint/redeem access.
- Freeze/blacklist/pause/forced-transfer/admin controls.
- Liquidity venues and current depth.
- Oracle/accounting method.
- Audits/incidents.
- Missing fields and decision effect.

Layer rule:

- Do not decide whether the asset is safe inside a specific platform product.
- Do not include curator, vault, PT maturity, or market-specific claims except as examples explicitly marked out of scope.

Compression rule:

- Do not return raw contract dumps to the parent.
- Return only artifact path, five strongest numbers, top risks, and blockers.

## S1P — Platform baseline mining

Role: create or refresh the reusable platform baseline for one protocol/platform mechanism.

Input contract:

- `platform_slug`.
- Platform family and mechanism, for example `morpho-vaults`, `morpho-blue`, or `pendle-pt-markets`.
- Optional: known product identifiers to guide which inspection guide is needed.

Allowed raw data:

- Official platform docs.
- Verified contracts, factories, registries, routers, adapters.
- Governance, admin, guardian, and emergency control sources.
- Incident reports, audits, risk docs, and public post-mortems.
- Product metadata APIs used only to understand inspection mechanics, not to conclude on one product.

Output contract:

- `<platform_artifact_dir>/scope.json`.
- `<platform_artifact_dir>/platform-baseline.md`.
- `<platform_artifact_dir>/platform-baseline.json`.
- `<platform_artifact_dir>/mechanics.md`.
- `<platform_artifact_dir>/risk-map.md`.
- `<platform_artifact_dir>/product-inspection-guide.md`.
- `<platform_artifact_dir>/sources.md`.
- `<platform_artifact_dir>/refresh.md`.
- `<platform_artifact_dir>/verification.md`.

Required facts:

- Protocol architecture and product types.
- Actor/controller model: governance, admins, guardians, curators, managers, allocators.
- Factories, registries, routers, adapters, and canonical contracts.
- Generic liquidation, redemption, maturity, settlement, and oracle mechanics.
- Where product-specific parameters live.
- Generic incidents and failure modes.
- Product inspection checklist.

Layer rule:

- Do not conclude on a specific vault, market, collateral list, PT maturity, or liquidity snapshot.

Compression rule:

- Parent receives artifact path, top platform risks, product inspection points, blockers, and validation status.

## S2 — Product / combination delta research

Role: research the exact asset-on-platform product instance by composing an asset baseline with a platform baseline and adding only the lightweight product-specific delta.

Input contract:

- Product scope.
- Asset baseline path.
- Platform baseline path.
- Exact vault, market, PT, SY, pool, route, maturity, or product identifier.

Output contract:

- `<product_artifact_dir>/scope.json`.
- `<product_artifact_dir>/product-delta.md`.
- `<product_artifact_dir>/product-delta.json`.
- `<product_artifact_dir>/live-parameters.json`.
- `<product_artifact_dir>/sources.md`.
- `<product_artifact_dir>/refresh.md`.
- `<product_artifact_dir>/verification.md`.

Required facts:

- Exact product identifiers and addresses.
- Inherited asset and platform artifact paths.
- Product-specific controller, curator, allocator, manager, or admin.
- Product-specific oracle, caps, fees, LLTV, collateral list, queues, maturity, settlement, liquidity, and transfer/eligibility path.
- Which inherited risks become active in this product.
- Which facts are volatile and must be refreshed before underwriting.

Compression rule:

- Parent receives artifact path, inherited artifacts, live parameters, active inherited risks, product-specific blockers, and validation status.

## S2F — Asset-risk analyst form

Role: convert reusable asset, platform, and product-delta research into the requested analyst-readable form.

Input contract:

- Requested form.
- Asset baseline path.
- Platform baseline path, if applicable.
- Product-delta path, if applicable.
- Requirements brief.

Output contract:

- `<form_artifact_dir>/composition-manifest.json`.
- `<form_artifact_dir>/analyst-report.md`.
- `<form_artifact_dir>/verification.md`.

Required report sections:

- Executive view.
- What the token represents.
- Main risk implications.
- Backing and NAV quality.
- Liquidity and exit risk.
- Controls, governance, and legal restrictions.
- Pricing/oracle risk in plain language.
- What must be checked before live use.
- Evidence quality.
- Source map.
- Technical appendix pointer.
- Research input paths by layer.

Compression rule:

- The report is a form-layer artifact.
- It should not create new source facts; if it does, they must be written back into the correct research layer.
- It should not compare products except where required by the requested form.
- Cross-token ranking belongs to S6.

## S3 — PT market/economics product delta

Role: analyze one Pendle PT market as a product-delta artifact that inherits the underlying asset baseline and the Pendle platform baseline.

Input contract:

- `chain_id`.
- Underlying token symbol/address.
- Target maturity date.
- User-supplied days-to-maturity label, if provided.
- Underlying asset baseline path.
- Pendle platform baseline path.

Output contract:

- `<product_artifact_dir>/scope.json`.
- `<product_artifact_dir>/product-delta.md`.
- `<product_artifact_dir>/product-delta.json`.
- `<product_artifact_dir>/live-parameters.json`.
- `<product_artifact_dir>/verification.md`.
- Optional form-layer `pt-markets/index.md` after all PTs finish.

Required facts:

- Exact market address.
- PT token address.
- SY token address.
- YT token address.
- Maturity timestamp.
- Accounting asset and output asset.
- PT price.
- Accounting asset price.
- Computed discount to accounting asset.
- Implied APY.
- Liquidity snapshot.
- PT-specific maturity, liquidity, valuation, and oracle risks.
- Inherited underlying-token risks separated from PT-specific risks.
- Inherited Pendle platform risks separated from PT-market-specific risks.

Required calculations:

- `Gross ROI = accounting_asset_price / PT_price - 1`.
- `Simple APR = Gross ROI × 365 / days_to_maturity`.
- `Compound APY = (1 + Gross ROI)^(365 / days_to_maturity) - 1`.
- `Break-even accounting-asset drawdown = 1 - PT_price / accounting_asset_price`.

Compression rule:

- Parent should receive only the key market IDs, price fields, calculated return fields, liquidity, and blockers.
- Full PT reasoning stays in the artifact.

## S4 — X/social mining

Role: collect social evidence for one asset, platform, or product-delta scope without polluting the reusable research layers with unsourced narrative.

Input contract:

- Asset/platform/product scope.
- Asset baseline path, if applicable.
- Platform baseline path, if applicable.
- Product-delta path, if applicable.
- Time window.
- Query angles.

Required query angles:

- Exact ticker and PT label.
- Issuer/project variants.
- Points/airdrop/program names.
- Yield and STAC/STRC variants.
- PT implied APY / fixed yield / maturity.
- Risk/depeg/redemption/freeze/liquidity/queue/stress.
- Recent date-bounded search.
- Key discovered handles.

Output contract:

- `x-research/x-research-<scope>.md`.

Required sections:

- Scope.
- Executive read.
- Query log.
- Distinct return models.
- Distinct risk narratives.
- Source index.
- Signal vs noise.
- Open threads.

Citation rule:

- Each material social claim must have handle, date or search-window date, and URL/status ID.
- If not available, mark `citation_degraded` at the claim level.

Safety rule:

- X tools are read-only in this workflow.
- No X posts, likes, follows, DMs, or account actions.

Compression rule:

- Parent should not receive raw X result lists.
- Parent receives only return models, risk narratives, points mechanics, source count, degraded-citation count, and artifact path.

## S5 — X/social synthesis

Role: synthesize all S4 reports into cross-scope social expectations.

Input contract:

- All S4 artifact paths.
- Scope list.

Output contract:

- `x-research/index.md`.
- `verification/final-x-research-points-yield-verification.md`.

Required synthesis fields:

- Cross-issuer summary.
- Return-estimate models.
- Points / airdrop uncertainty.
- STAC/STRC/yield uncertainty.
- Issuer/redemption/freeze/control risk by research layer.
- PT liquidity/maturity/accounting risk.
- Crowded farming/leverage/unwind risk.
- Signal vs noise.
- Citation degradation.
- Contradictions and controversies.
- Open follow-up threads.

Compression rule:

- This is the social handoff to underwriting.
- It should not include raw post dumps.

## S6 — Quantitative underwriting

Role: convert evidence into decision variables.

Input contract:

- All relevant asset baselines.
- All relevant platform baselines.
- All relevant product-delta artifacts.
- Form-layer analyst reports, if already generated.
- S5 social synthesis, if points/social are in scope.
- Position size.
- Horizon.
- Net annualized hurdle.
- Optional: mandate constraints and risk appetite.

Output contract:

- `investment-analysis/quantitative-underwriting-methodology.md`.
- `investment-analysis/investment-analyst-report-points-pt-risk-return.md`.
- `investment-analysis/index.md`.

Required calculations:

- Gross ROI.
- Simple annualized return.
- Compound annualized return, when relevant.
- Points EV.
- Points ROI.
- Points annualized return.
- Expected loss.
- Exit cost.
- Risk-adjusted ROI.
- Risk-adjusted annualized return.
- Break-even points ROI.
- Break-even terminal drawdown.
- Price-stability certainty score.

Required outputs:

- Decision summary.
- Base assumptions.
- Gross return stack.
- Risk-adjusted return stack.
- Points valuation.
- Price-stability certainty by token.
- Token-by-token investment view.
- Sensitivity map.
- Required live inputs before capital allocation.
- Source map.
- Stale-data markers.

Decision statuses:

- Underwrite.
- Underwrite only with points upside.
- Reject on risk-adjusted basis.
- Cannot underwrite.

Compression rule:

- S6 is the first stage allowed to compare candidates or make capital-decision tradeoffs.
- It should cite research-layer paths rather than paste full upstream content.
- It must separate inherited asset risk, inherited platform risk, and product-specific risk in expected-loss assumptions.

## S7 — Final verification

Role: verify full run before completion.

Input contract:

- All declared output paths.
- Workflow manifest.
- Workspace validation commands.

Output contract:

- `verification/final-investment-analysis-verification.md`.

Required checks:

- Required files exist.
- Research-library asset, platform, product, and form folders follow `output-structure.md`.
- Cross-links resolve.
- Required sections present.
- Quantitative fields present.
- No research-layer artifact gives unsupported allocation conclusions.
- No form-layer artifact is the only location of a material source fact.
- Workspace validation passes or unrelated failures are isolated.

Parent completion rule:

- The parent should report only after S7 passes or explicitly names unresolved blockers.
