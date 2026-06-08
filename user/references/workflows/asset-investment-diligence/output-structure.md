# Output structure — asset investment diligence workflow

Every asset-investment-diligence run returns one artifact folder. The parent agent should return this folder path plus a short summary, not a set of loose report paths.

The storage model separates reusable researcher output from formatter/report deliverables:

- `research-library/assets/` — asset baselines that can be reused across platforms and reports.
- `research-library/platforms/` — platform baselines that can be reused across assets and reports.
- `research-library/products/` — lightweight product / combination deltas for one asset on one platform instance.
- `forms/` — formatter outputs composed from the research library.
- `investment-analysis/` — underwriting and decision outputs, when a capital decision is in scope.

## Canonical run folder

```text
<run_artifact_root>/
  README.md
  run-manifest.json
  index.md

  research-library/
    assets/
      <asset-slug>/
        scope.json
        asset-baseline.md
        asset-baseline.json
        pillars/
          issuer.md
          credit-risk.md
          operational-risk.md
        sources.md
        refresh.md
        verification.md

    platforms/
      <platform-slug>/
        scope.json
        platform-baseline.md
        platform-baseline.json
        mechanics.md
        risk-map.md
        product-inspection-guide.md
        sources.md
        refresh.md
        verification.md

    products/
      <platform-slug>/
        <asset-slug>/
          <product-slug>/
            scope.json
            product-delta.md
            product-delta.json
            live-parameters.json
            sources.md
            refresh.md
            verification.md

  forms/
    <form-slug>/
      composition-manifest.json
      analyst-report.md
      verification.md

  x-research/
    <scope-slug>.md
    index.md

  investment-analysis/
    quantitative-underwriting-methodology.md
    investment-analyst-report-points-pt-risk-return.md
    index.md

  verification/
    workflow-harness-report.json
    workflow-harness-verification.md
    final-investment-analysis-verification.md
```

Legacy `tokens/<token-slug>/` and `pt-markets/<pt-scope-slug>/` folders may be generated for compatibility, but they are formatter/report projections. The canonical reusable storage is `research-library/assets/`, `research-library/platforms/`, and `research-library/products/`.

## Slug rules

Asset slug:

```text
<chain>-<symbol>-<address-prefix>
```

Example:

```text
ethereum-usdc-a0b86991
```

Platform slug:

```text
<platform-family>-<mechanism>
```

Examples:

```text
morpho-blue
morpho-vaults
pendle-pt-markets
securitize-transfer-agent
```

Product slug:

```text
<product-type>-<asset-symbol>-<identifier-prefix-or-maturity>
```

Examples:

```text
morpho-vault-usdc-abcdef12
morpho-market-usdc-weth-86lltv-12345678
pendle-pt-usdc-2026-08-27-abc12345
```

Form slug:

```text
<requested-form>-<scope>-<date>
```

Examples:

```text
gearbox-collateral-memo-usdc-morpho-2026-06-08
pt-investment-memo-usdc-pendle-2026-06-08
```

Social scope slug:

```text
<asset-slug>
<product-slug>
portfolio
```

## Required top-level files

### `run-manifest.json`

Required fields:

```json
{
  "workflow_id": "asset-investment-diligence-v1.1",
  "run_id": "asset-diligence-YYYY-MM-DD",
  "run_artifact_root": "dev/implementation/<run-slug>",
  "research_layers": {
    "assets": [
      {
        "asset_slug": "ethereum-usdc-a0b86991",
        "artifact_dir": "research-library/assets/ethereum-usdc-a0b86991",
        "action": "reuse | refresh | create",
        "status": "pass | review_required | blocked | stale"
      }
    ],
    "platforms": [
      {
        "platform_slug": "morpho-vaults",
        "artifact_dir": "research-library/platforms/morpho-vaults",
        "action": "reuse | refresh | create",
        "status": "pass | review_required | blocked | stale"
      }
    ],
    "products": [
      {
        "product_slug": "morpho-vault-usdc-abcdef12",
        "artifact_dir": "research-library/products/morpho-vaults/ethereum-usdc-a0b86991/morpho-vault-usdc-abcdef12",
        "asset_slug": "ethereum-usdc-a0b86991",
        "platform_slug": "morpho-vaults",
        "status": "pass | review_required | blocked | stale"
      }
    ]
  },
  "forms": [
    {
      "form_slug": "gearbox-collateral-memo-usdc-morpho-2026-06-08",
      "artifact_dir": "forms/gearbox-collateral-memo-usdc-morpho-2026-06-08",
      "composition_manifest": "forms/gearbox-collateral-memo-usdc-morpho-2026-06-08/composition-manifest.json"
    }
  ],
  "x_research_scopes": [],
  "final_index": "index.md",
  "final_verification": "verification/final-investment-analysis-verification.md"
}
```

### `index.md`

Human-readable run summary:

- asset baselines used, refreshed, or created;
- platform baselines used, refreshed, or created;
- product deltas researched;
- forms generated;
- inherited risks by layer;
- missing data and blockers;
- artifact map;
- final verification status.

### `README.md`

Short handoff page:

- what was analyzed;
- where the manifest is;
- which asset/platform/product artifacts are reusable;
- which form artifacts were generated;
- which files to read first;
- final validation status.

## Required per-asset files

Each asset folder must contain:

- `scope.json`;
- `asset-baseline.md`;
- `asset-baseline.json`;
- `pillars/issuer.md`;
- `sources.md`;
- `refresh.md`;
- `verification.md`.

`pillars/credit-risk.md` and `pillars/operational-risk.md` are required when those Steakhouse-style Asset layer pillars are in scope.

Asset artifacts must not include platform-specific product claims. Example: USDC baseline may discuss Circle freeze powers and redemption model, but not whether a specific Morpho USDC vault is acceptable.

## Required per-platform files

Each platform folder must contain:

- `scope.json`;
- `platform-baseline.md`;
- `platform-baseline.json`;
- `mechanics.md`;
- `risk-map.md`;
- `product-inspection-guide.md`;
- `sources.md`;
- `refresh.md`;
- `verification.md`.

Platform artifacts must not include product-instance conclusions unless the platform has only one instance and that limitation is explicit. Example: Morpho baseline may define curator and oracle inspection points, but not declare a specific USDC vault safe.

## Required per-product files

Each product folder must contain:

- `scope.json`;
- `product-delta.md`;
- `product-delta.json`;
- `live-parameters.json`;
- `sources.md`;
- `refresh.md`;
- `verification.md`.

Product delta artifacts must cite inherited asset and platform artifacts. They should contain only instance-specific facts plus the explanation of which inherited risks become active in this product.

Minimum `scope.json`:

```json
{
  "product_slug": "morpho-vault-usdc-abcdef12",
  "asset_slug": "ethereum-usdc-a0b86991",
  "platform_slug": "morpho-vaults",
  "product_type": "vault | market | pt_market | wrapper | pool | route | other",
  "chain": "Ethereum mainnet",
  "primary_address": "0x...",
  "inherited_artifacts": {
    "asset_baseline": "research-library/assets/ethereum-usdc-a0b86991/asset-baseline.md",
    "platform_baseline": "research-library/platforms/morpho-vaults/platform-baseline.md"
  }
}
```

## Required form files

Each form folder must contain:

- `composition-manifest.json`;
- the requested form, usually `analyst-report.md`, `investment-memo.md`, `ui-summary.md`, or `public-report.md`;
- `verification.md`.

Minimum `composition-manifest.json`:

```json
{
  "form_slug": "gearbox-collateral-memo-usdc-morpho-2026-06-08",
  "requested_form": "Gearbox collateral analyst memo",
  "asset_inputs": ["research-library/assets/ethereum-usdc-a0b86991/asset-baseline.md"],
  "platform_inputs": ["research-library/platforms/morpho-vaults/platform-baseline.md"],
  "product_delta_inputs": ["research-library/products/morpho-vaults/ethereum-usdc-a0b86991/morpho-vault-usdc-abcdef12/product-delta.md"],
  "formatter_inputs": ["requirements brief"],
  "facts_created_in_form_layer": [],
  "facts_that_must_be_written_back": []
}
```

If `facts_created_in_form_layer` is non-empty, the form is not final until those facts are moved into the correct research artifact.

## Parent-agent return contract

A completed workflow run returns:

```json
{
  "status": "pass | review_required | blocked",
  "run_artifact_root": "dev/implementation/<run-slug>",
  "manifest": "dev/implementation/<run-slug>/run-manifest.json",
  "index": "dev/implementation/<run-slug>/index.md",
  "asset_dirs": [
    "dev/implementation/<run-slug>/research-library/assets/ethereum-usdc-a0b86991"
  ],
  "platform_dirs": [
    "dev/implementation/<run-slug>/research-library/platforms/morpho-vaults"
  ],
  "product_dirs": [
    "dev/implementation/<run-slug>/research-library/products/morpho-vaults/ethereum-usdc-a0b86991/morpho-vault-usdc-abcdef12"
  ],
  "form_dirs": [
    "dev/implementation/<run-slug>/forms/gearbox-collateral-memo-usdc-morpho-2026-06-08"
  ],
  "final_verification": "dev/implementation/<run-slug>/verification/final-investment-analysis-verification.md",
  "summary": {
    "assets_reused": 1,
    "platforms_reused": 1,
    "product_deltas_created": 1,
    "forms_generated": 1,
    "blocked_scopes": 0,
    "review_required_scopes": 1,
    "dominant_blockers": ["product-specific curator allocation stale"]
  }
}
```

The user-facing answer should include the run folder path, final index path, reusable asset/platform/product directories, generated form directories, and final verification path. It should not paste raw source notes unless requested.

## Workflow harness outputs

The workflow harness writes deterministic compliance artifacts under the run verification directory:

- `workflow-harness-report.json` — machine-readable report with status, exit code, checks, and findings.
- `workflow-harness-verification.md` — Markdown verification summary for human review.

Parent-agent return handoffs must include these paths when the harness is run, especially when `review_required` leaves unresolved finding ids.

## Compatibility rule

If older tooling still expects `tokens/<token-slug>/analyst-report.md` or `pt-markets/<pt-scope-slug>/analyst-report.md`, generate those files as formatter views and include their source composition manifest. Do not treat legacy report folders as the canonical research store.
