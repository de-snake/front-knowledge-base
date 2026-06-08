# Research composition methodology

This page defines the storage and workflow model for reusable asset diligence.

It exists because an analyst should not re-research USDC every time the question is “USDC on Morpho”, “USDC in a Pendle PT”, or “USDC inside a vault”. The reusable asset facts, reusable platform facts, and lightweight product-specific facts must be separated first, then composed into whatever report form is needed.

## Core rule

Separate **research matter** from **form matter**.

- **Research matter** is source-backed evidence, entity boundaries, facts, uncertainties, gates, and refresh rules.
- **Form matter** is the presentation applied on top: analyst memo, investment decision page, comparison table, UI-readable summary, public report, or Snapshot-style field.

A researcher does not write the final “nice report” first. A researcher writes reusable evidence artifacts. A formatter/report writer consumes those artifacts and creates the requested form without changing the underlying facts.

## Three reusable research layers

Every opportunity should be decomposed into these layers before research starts.

```text
asset baseline + platform baseline + product delta = composed opportunity view
```

### Layer 1 — Asset baseline

The asset baseline answers: **what is this asset by itself?**

Examples:

- USDC as issued by Circle.
- sUSDe as issued by Ethena.
- PT-sUSDe only as a fixed-maturity token primitive if the PT itself is the asset being reused.
- A tokenized security as issued by its issuer / transfer agent.

Asset baseline research covers durable facts about the asset:

- issuer / control plane;
- legal or DAO accountability;
- mint, burn, freeze, blacklist, pause, upgrade, and transfer controls;
- redemption / claim model;
- backing / reserve / NAV model;
- chain deployments and canonical contracts;
- oracle/accounting implications intrinsic to the asset;
- incidents and invariant failures;
- asset-level gates that follow the asset everywhere.

It must not include platform-specific claims such as “safe on Morpho” or “good PT APY”. Those belong to product deltas or form-layer underwriting.

### Layer 2 — Platform baseline

The platform baseline answers: **what does this platform do, and where are its generic risks?**

Examples:

- Morpho Blue as a lending-market primitive.
- Morpho Vaults / MetaMorpho as a curator-managed allocation primitive.
- Pendle as a PT/YT/SY fixed-yield market primitive.
- A Securitize transfer-agent platform.

Platform baseline research covers reusable platform facts:

- protocol architecture and actor model;
- factories, market/vault registries, routers, adapters, and canonical contracts;
- governance/admin/guardian/emergency powers;
- generic liquidation, redemption, settlement, or maturity mechanics;
- oracle model and where product-specific oracle choices appear;
- curator / allocator / manager model, if any;
- permissioning, transfer, whitelist, and address-eligibility mechanics;
- generic failure modes and historical incidents;
- exact locations an analyst must inspect for a product on this platform.

It must not embed a conclusion about a specific USDC vault, market, PT maturity, curator, collateral list, or liquidity snapshot unless that product is the platform’s only live instance and the limitation is explicit.

### Layer 3 — Product / combination delta

The product delta answers: **what changes when this asset is used on this platform in this exact product instance?**

Examples:

- USDC supplied to a specific Morpho vault.
- USDC in a specific Morpho Blue market against WETH collateral.
- PT-USDC maturity on Pendle, including the SY and market address.
- A Securitize-issued asset inside a Gearbox Credit Account path.

Product delta research is intentionally lightweight compared with the baselines. It reuses the asset and platform artifacts, then adds only instance-specific facts:

- exact product identifier: vault, market, PT, SY, pool, route, curator, manager, maturity;
- inherited asset baseline path and platform baseline path;
- current product parameters: caps, fees, LLTV, collateral list, oracle, queue, maturity, settlement, liquidity;
- curator / allocator / manager or other product-level controller;
- product-specific address eligibility, transferability, liquidation path, or redemption path;
- product-specific live risks and stale-data markers;
- deltas from baseline assumptions.

The product delta should be the main thing re-run when the question changes from “USDC generally” to “USDC on Morpho vault X”.

## Form layer

The form layer answers: **what shape should the research take for this user or decision?**

Examples:

- internal analyst memo;
- Gearbox collateral review;
- product UI summary;
- investment comparison;
- public report;
- Snapshot/GIP field;
- Telegram short answer.

The form layer may rank, summarize, simplify, or translate the research, but it must cite the research artifacts it used. It must not create new source claims without writing them back into the relevant research layer.

## Canonical storage model

Reusable artifacts should be stored by entity, not by the latest report request.

```text
research-library/
  assets/
    <asset-slug>/
      asset-baseline.md
      asset-baseline.json
      pillars/
        issuer.md
        credit-risk.md
        operational-risk.md
      sources.md
      refresh.md

  platforms/
    <platform-slug>/
      platform-baseline.md
      platform-baseline.json
      mechanics.md
      risk-map.md
      product-inspection-guide.md
      sources.md
      refresh.md

  products/
    <platform-slug>/
      <asset-slug>/
        <product-slug>/
          product-delta.md
          product-delta.json
          live-parameters.json
          sources.md
          refresh.md

  forms/
    <run-or-request-slug>/
      composition-manifest.json
      analyst-report.md
      investment-analysis.md
      verification.md
```

A run folder may keep local copies or pointers to these artifacts, but the conceptual storage key is still `asset`, `platform`, and `product`, not “report”.

## Required metadata envelope

Every reusable research artifact should include this envelope.

```yaml
research_artifact:
  artifact_id: "asset:ethereum-usdc | platform:morpho-blue | product:morpho-blue-usdc-weth-lltv86"
  layer: "asset | platform | product_delta | form"
  subject:
    name: "USDC"
    chain: "Ethereum mainnet"
    address: "0x..."
  version: "YYYY-MM-DD"
  status: "pass | review_required | blocked | stale"
  inherited_from: []
  source_ledger: "sources.md"
  refresh_policy:
    durable_until_changed:
      - "legal issuer identity"
      - "contract architecture"
    volatile_fields:
      - "liquidity"
      - "caps"
      - "oracle price"
      - "curator allocation"
    refresh_before_use:
      - "live parameters"
      - "admin roles"
      - "liquidity depth"
  unresolved_gates: []
```

## Workflow order

### Step 0 — Decompose the question

Before launching research, identify the layers.

```yaml
scope_decomposition:
  user_question: "Assess USDC on Morpho vault X"
  asset_layer:
    asset_slug: "ethereum-usdc"
    needed: true
    existing_artifact: "research-library/assets/ethereum-usdc/asset-baseline.md"
    action: "reuse | refresh | create"
  platform_layer:
    platform_slug: "morpho-vaults"
    needed: true
    existing_artifact: "research-library/platforms/morpho-vaults/platform-baseline.md"
    action: "reuse | refresh | create"
  product_delta_layer:
    product_slug: "morpho-vaults-usdc-<vault-address-prefix>"
    needed: true
    existing_artifact: null
    action: "create_or_refresh"
  form_layer:
    requested_form: "Gearbox collateral analyst memo"
    action: "compose_after_research"
```

If this decomposition is missing, the workflow is likely to duplicate research or mix platform facts into asset facts.

### Step 1 — Reuse or refresh asset baseline

Research the asset only once per material change.

Refresh the asset baseline when:

- canonical contract changes;
- issuer / admin / transfer-agent structure changes;
- redemption terms change;
- freeze/blacklist/permissioning rules change;
- backing/reserve/NAV method changes;
- major incident occurs;
- prior baseline has unresolved gates that matter to the current product.

Do not refresh the whole asset baseline just because a platform-specific parameter changed.

### Step 2 — Reuse or refresh platform baseline

Research the platform once per platform mechanism, not once per asset.

Refresh the platform baseline when:

- contracts/factories/routers change;
- governance/admin/guardian structure changes;
- protocol risk model changes;
- curator model changes;
- liquidation/redemption/maturity mechanics change;
- major incident occurs;
- product inspection guide becomes wrong.

Do not place the live risk state of one vault, market, or PT maturity in the generic platform baseline.

### Step 3 — Research product delta

Run fresh product-delta research for the exact product instance.

The product delta must answer:

- which asset baseline is inherited;
- which platform baseline is inherited;
- exact product contracts and identifiers;
- product-specific controller / curator / allocator / manager;
- product-specific oracle, collateral, limits, caps, queues, fees, maturity, liquidity;
- what inherited asset/platform risks become relevant in this product;
- what product-specific gates block Gearbox holding, liquidation, unwind, or underwriting.

### Step 4 — Compose the requested form

Only after the three research layers exist, create the requested form.

The form must include a composition manifest:

```yaml
composition_manifest:
  requested_form: "Gearbox collateral analyst memo"
  asset_inputs:
    - "research-library/assets/ethereum-usdc/asset-baseline.md"
  platform_inputs:
    - "research-library/platforms/morpho-vaults/platform-baseline.md"
  product_delta_inputs:
    - "research-library/products/morpho-vaults/ethereum-usdc/<product-slug>/product-delta.md"
  formatter_inputs:
    - "requirements brief"
  facts_created_in_form_layer: []
  facts_that_must_be_written_back: []
```

If the report writer discovers a new source fact while formatting, it must be written into the correct research layer first, then the form regenerated or patched from that source.

## Researcher / formatter separation

### Researcher responsibilities

The researcher writes:

- source ledger;
- fact tables;
- control maps;
- decision inventories;
- no-result proofs;
- gates and stale-data markers;
- explicit inheritance links;
- machine-readable JSON where possible.

The researcher does not:

- optimize prose for a public audience;
- hide weak facts to make a report read cleaner;
- combine asset and platform risks into one unsupported conclusion;
- make allocation recommendations unless the stage explicitly asks for underwriting.

### Formatter responsibilities

The formatter writes:

- narrative report;
- user-facing summary;
- decision page;
- comparison view;
- executive memo;
- product/UI text.

The formatter must:

- cite asset, platform, and product-delta inputs;
- preserve gates and uncertainty;
- separate inherited risks from product-specific risks;
- mark any missing research input as a blocker or assumption.

## Example — USDC on Morpho

The correct decomposition is:

```text
Asset baseline: USDC / Circle / canonical contracts / mint-burn-freeze-redemption / reserve attestations
Platform baseline: Morpho Blue or Morpho Vaults / market-vault mechanics / curators / oracle/liquidation model
Product delta: exact USDC vault or market / curator / collateral list / oracle / LLTV / caps / liquidity / current allocation
Form: Gearbox-specific collateral memo, investment view, or UI summary
```

Bad workflow:

```text
Research “USDC on Morpho” as one giant report and repeat USDC + Morpho basics every time.
```

Good workflow:

```text
Reuse USDC baseline.
Reuse or refresh Morpho baseline.
Research only the exact USDC-on-Morpho product delta.
Compose the requested report from those inputs.
```

## Example — USDC PT on Pendle

The decomposition may be:

```text
Asset baseline: USDC
Platform baseline: Pendle PT/YT/SY mechanics
Product delta: exact PT market, maturity, SY, accounting asset, liquidity, implied APY, maturity settlement path
Form: PT investment memo or Gearbox collateral eligibility review
```

The PT product delta and any later PT report must not bury USDC issuer/freezing/redemption facts inside Pendle facts. It inherits USDC asset risk, inherits Pendle platform mechanics, then adds PT-market facts.

## Validation checklist

Before a workflow run is accepted:

- [ ] Scope decomposition identifies asset, platform, product delta, and form layer.
- [ ] Existing asset baseline was reused or explicitly refreshed.
- [ ] Existing platform baseline was reused or explicitly refreshed.
- [ ] Product delta contains only instance-specific facts plus explicit inherited risks.
- [ ] Formatter/report artifacts cite all research inputs.
- [ ] No form-layer report is the only place where a material source fact exists.
- [ ] Stale volatile fields are marked and refreshed before underwriting.
- [ ] Asset gates, platform gates, and product gates are not collapsed into one generic “risk” bucket.
- [ ] Gearbox hold/liquidation/redemption implications state whether they come from the asset, platform, or product delta.
