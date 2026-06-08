# Runbook — asset investment diligence workflow

This runbook tells an agent how to execute `workflow.json` without loading all evidence into the parent context.

The workflow is compositional: research is stored as reusable asset, platform, and product-delta artifacts; requested reports are form-layer outputs generated from those artifacts.

## 0. Start here

Workflow directory:

`user/references/workflows/asset-investment-diligence`

Run artifact root:

`[run_artifact_root]`

Example run artifact root:

`dev/implementation/asset-risk-reports-mvp`

Read in this order:

1. `README.md`.
2. `research-composition-methodology.md`.
3. `workflow.json`.
4. `stage-contracts.md`.
5. `parallelization-and-context.md`.
6. `subagent-prompts.md`.
7. `output-structure.md`.

Do not start by reading every report under the run artifact root. Those directories are stage outputs, not parent-agent context.

Every run returns one folder at `run_artifact_root`. Canonical reusable research lives under `research-library/assets/`, `research-library/platforms/`, and `research-library/products/`. Generated reports live under `forms/` or `investment-analysis/`.

## 1. Define the run scope

Create a scope object before spawning workers:

```json
{
  "run_id": "asset-risk-diligence-YYYY-MM-DD",
  "run_artifact_root": "dev/implementation/<run-slug>",
  "position_size_usd": 1000000,
  "base_net_apr_hurdle": 0.10,
  "opportunistic_net_apr_hurdle": 0.20,
  "assets": [
    {
      "asset_slug": "ethereum-usdc-a0b86991",
      "chain_id": 1,
      "chain": "Ethereum mainnet",
      "symbol": "USDC",
      "token_address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
      "intended_use": "spot / collateral / PT underlying / points exposure"
    }
  ],
  "platforms": [
    {
      "platform_slug": "morpho-vaults",
      "platform_family": "Morpho",
      "mechanism": "curator-managed vaults"
    }
  ],
  "products": [
    {
      "product_slug": "morpho-vault-usdc-abcdef12",
      "asset_slug": "ethereum-usdc-a0b86991",
      "platform_slug": "morpho-vaults",
      "product_type": "vault",
      "primary_address": "0x..."
    }
  ],
  "forms": [
    {
      "form_slug": "gearbox-collateral-memo-usdc-morpho-2026-06-08",
      "requested_form": "Gearbox collateral analyst memo",
      "product_slugs": ["morpho-vault-usdc-abcdef12"]
    }
  ],
  "social_scopes": []
}
```

If a field is unknown, keep the field and set it to `null`. Do not delete unknown fields. Downstream stages must know what is missing.

## 2. Stage execution order

### 2.0 Scope decomposition and reuse plan

Run S0 first.

Parent action:

- identify asset baseline(s), platform baseline(s), product delta(s), and requested form(s);
- decide whether existing asset/platform baselines can be reused, refreshed, or must be created;
- write `scope-decomposition.json`, `scope-decomposition.md`, and initial `run-manifest.json`.

Do not spawn general research until this layer plan exists.

### 2.1 Asset baseline research

Run S1 for each asset that must be created or refreshed.

Parallelization:

- Spawn one subagent per asset.
- Batch at most three subagents at once.
- Use the S1 prompt from `subagent-prompts.md`.

Parent receives:

- artifact paths;
- five strongest numeric facts;
- top asset-layer risks;
- blocking unknowns;
- volatile fields;
- validation status.

Parent action after S1:

- Record paths in a run registry.
- Do not read full raw research unless validation fails or a later stage needs audit.

### 2.2 Platform baseline research

Run S1P for each platform that must be created or refreshed.

Parallelization:

- Spawn one subagent per platform mechanism.
- Batch at most three subagents at once.
- Use the S1P prompt from `subagent-prompts.md`.

Parent receives:

- artifact paths;
- top platform risks;
- product inspection points;
- blockers;
- validation status.

Parent action after S1P:

- Record paths in a run registry.
- Check that `product-inspection-guide.md` names where product-specific parameters live.

### 2.3 Product / combination delta research

Run S2 for each exact product instance.

Parallelization:

- Spawn one subagent per product instance.
- Batch at most three subagents at once.
- Use the S2 prompt from `subagent-prompts.md`.

Required inputs:

- asset baseline path;
- platform baseline path;
- exact product identifier: vault, market, PT, SY, pool, route, maturity, or primary address.

Parent action after S2:

- Record live parameters and stale-data markers.
- Verify inherited asset/platform risks are separated from product-specific risks.

### 2.4 PT market and economics product delta

Run S3 for each Pendle PT market if PTs are in scope.

Parallelization:

- Spawn one subagent per PT market.
- Batch at most three subagents at once.
- Use the S3 prompt from `subagent-prompts.md`.

Parent action after S3:

- Record PT price, accounting asset price, maturity, liquidity, gross ROI/APR, and break-even drawdown.
- Do not treat PT APY as final return; expected loss and points are applied in S6.

### 2.5 Form/report generation

Run S2F after relevant research artifacts exist.

Parallelization:

- Spawn one subagent per requested form if multiple forms are needed.
- Use the S2F prompt from `subagent-prompts.md`.

Parent action after S2F:

- Read `composition-manifest.json` first.
- Verify `facts_created_in_form_layer` is empty or explicitly blocked.
- Verify the form cites asset/platform/product research inputs.

### 2.6 X/social mining

Run S4 if points, social yield, depeg narratives, or market sentiment are in scope.

Parallelization:

- Spawn one subagent per social scope.
- Batch at most three subagents at once.
- Use the S4 prompt from `subagent-prompts.md`.

Parent action after S4:

- Record return models, points mechanics, risk narratives, source count, and degraded-citation count.
- Do not ingest raw X result lists.

### 2.7 X/social synthesis

Run S5 once after all S4 artifacts exist.

Serial execution:

- Parent can run this directly, or delegate once if the artifact list is complete.
- Use the S5 prompt from `subagent-prompts.md`.

Parent action after S5:

- Read `x-research/index.md` under the run artifact root as the social handoff to underwriting.
- Note contradictions and citation degradation.

### 2.8 Quantitative underwriting

Run S6 once after asset, platform, product, form, and social inputs are available.

Serial execution:

- Parent should run this directly when possible.
- Use the S6 prompt if delegating a draft.

Required inputs:

- all relevant asset baselines;
- all relevant platform baselines;
- all relevant product-delta artifacts;
- form-layer analyst reports, if already generated;
- X synthesis, if social evidence is in scope;
- position size;
- base and opportunistic hurdle rates.

Required outputs under the run artifact root:

- `investment-analysis/quantitative-underwriting-methodology.md`;
- `investment-analysis/investment-analyst-report-points-pt-risk-return.md`;
- `investment-analysis/index.md`.

Parent action after S6:

- Verify formulas and numbers.
- Verify inherited asset risk, inherited platform risk, and product-specific risk are separate in expected-loss assumptions.
- Read the decision summary, assumptions, risk-adjusted stack, sensitivity map, and live-input blockers.

### 2.9 Final verification

Run S7 after all output files exist.

Serial execution:

- Parent should run verification directly.

Required checks:

- `workflow.json` parses.
- `output-structure.md` exists and research-library/form folders match it.
- Every stage has id, title, role, dependencies, parallelization, inputs, outputs, and validation fields.
- Links from `README.md` resolve.
- Form-layer artifacts are not the only location of material source facts.
- Investment-analysis reports contain quantitative fields when S6 is in scope.
- Terminology checks pass for workflow docs.
- Workspace validation passes where applicable:
  - `python3 scripts/workspace_sync.py --check`
  - `python3 scripts/workspace_policy_check.py --all`

Write under the run artifact root:

- `verification/final-investment-analysis-verification.md`.

## 3. Parent run registry

During execution, keep a small registry in memory or a temporary JSON file:

```json
{
  "S0_scope_decomposition": {
    "status": "pass",
    "artifacts": ["scope-decomposition.json", "scope-decomposition.md"]
  },
  "S1_asset_baseline_research": {
    "ethereum-usdc-a0b86991": {
      "status": "pass",
      "artifact_dir": "research-library/assets/ethereum-usdc-a0b86991",
      "artifacts": ["research-library/assets/ethereum-usdc-a0b86991/asset-baseline.md"]
    }
  },
  "S1P_platform_baseline_research": {},
  "S2_product_delta_research": {},
  "S2F_form_generation": {},
  "S3_pt_market_economics_product_delta": {},
  "S4_x_social_mining": {},
  "S5_x_social_synthesis": {},
  "S6_quantitative_underwriting": {},
  "S7_final_verification": {}
}
```

The registry lets the parent evaluate completeness without reading every artifact.

## 4. Validation commands

From repository root `/Users/ilya/ai-assistant`:

```bash
python3 - <<'PY'
import json
from pathlib import Path
workflow = Path('projects/front-knowledge-base/user/references/workflows/asset-investment-diligence')
manifest = json.loads((workflow / 'workflow.json').read_text())
required_stage_keys = {'id', 'title', 'role', 'depends_on', 'parallelization', 'inputs', 'outputs', 'validation'}
for stage in manifest['stages']:
    missing = required_stage_keys - set(stage)
    assert not missing, (stage.get('id'), missing)
print('WORKFLOW_MANIFEST_SCHEMA_CHECK_PASS')
PY

python3 scripts/workspace_sync.py --check
python3 scripts/workspace_policy_check.py --all
```

From vault root `/Users/ilya/ai-assistant/projects/front-knowledge-base`:

```bash
python3 - <<'PY'
from pathlib import Path
workflow = Path('user/references/workflows/asset-investment-diligence')
files = [
    workflow / 'README.md',
    workflow / 'research-composition-methodology.md',
    workflow / 'workflow.json',
    workflow / 'stage-contracts.md',
    workflow / 'parallelization-and-context.md',
    workflow / 'subagent-prompts.md',
    workflow / 'runbook.md',
    workflow / 'output-structure.md',
    workflow / 'examples/asset-risk-reports-mvp-current-run-map.md',
]
missing = [str(p) for p in files if not p.exists()]
assert not missing, missing
print('AGENTIC_OPS_WORKFLOW_FILE_CHECK_PASS')
PY
```

## 5. Completion standard

A run is complete only when:

- all required stage outputs exist under the run artifact root;
- research-library asset/platform/product artifacts are separated;
- form artifacts include composition manifests;
- serial synthesis and underwriting outputs exist when in scope;
- validation commands pass or unrelated failures are isolated;
- the final user summary includes exact files created, commands run, and unresolved live-input blockers.

If a stage was skipped, the final summary must state why it was skipped.

## 6. Workflow harness command

Run this harness command from the vault root after S7 writes the final verification:

```bash
python3 dev/implementation/workflow-harness/scripts/validate_research_package.py \
  --run-root [run_artifact_root] \
  --workflow user/references/workflows/asset-investment-diligence/workflow.json \
  --output-dir [run_artifact_root]/verification
```

If the harness is not present in the current checkout, record that as `not_available` in final verification rather than fabricating a pass.
