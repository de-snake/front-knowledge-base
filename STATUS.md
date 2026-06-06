# Current status — front-knowledge-base

## What is clear now

The current vault has a clean runtime structure for Gearbox front / agent reasoning:

- `user/foundations/` defines shared terms, personas, and monitoring principles.
- `user/decision/` defines entry modes and display / response hierarchy.
- `user/flows/` defines canonical Pool and Credit Account flows.
- `user/references/mechanics/` holds stable cross-flow mechanics.
- `user/references/workflows/` holds executable diligence / oracle worker contracts.

The canonical loop is:

```text
Discover → Analyze → Propose → Preview → Execute → Monitor
```

Issuer-controlled assets, tokenized securities, redemption-window assets, and compliance-gated assets are treated as conditional branches inside Credit Account opening / management, not as a separate standalone product flow.

## What works now

A deterministic Analyze → Propose runner can scaffold and validate a combined asset-diligence + oracle-analysis run.

The public demo package includes:

- input: `dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/input.json`
- filled run artifacts: `dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/run/`
- result summary: `dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/RESULT.md`
- local reproduction instructions: `dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/README.md`

## Demo result

Question:

> Should USDat or sUSDat be treated as acceptable Gearbox Credit Account collateral candidates on Ethereum mainnet when borrowing USDC at a 9% borrow-rate assumption?

Validation result:

```text
Status: pass
Exit code: 0
asset: pass
oracle: pass
combined: pass
```

Workflow decision:

```text
Discover: complete by user premise
Analyze: complete
Propose: request_more_inputs
Preview: blocked
Execute: blocked
Monitor: not_started
```

Interpretation:

- USDat is the stronger Analyze-stage candidate because the supplied Gearbox feed is market-derived from the USDat/USDC Curve pool and observed liquidity is deeper.
- sUSDat remains more conditional because the supplied feed uses ERC-4626 accounting over USDat while immediate recovery depends on thinner liquidity, queue processing, and issuer / STRC realization.
- Neither candidate is ready for Preview or Execute without additional live inputs.

## Missing before decision-grade proposal

The demo intentionally blocks Preview / Execute until these inputs exist:

- evaluated Gearbox market / Credit Manager / pool for USDat;
- evaluated Gearbox market / Credit Manager / pool for sUSDat;
- position size or scenario size range;
- target leverage or scenario leverage;
- intended hold horizon;
- user risk policy: HF floor, max drawdown, automation policy;
- wallet / Credit Account / liquidator eligibility for holding, transfer, redemption, freeze, and blacklist state;
- size-specific route or liquidation quote for the proposed unwind path.

## What this repository no longer includes

The public `main` tree is now presentation-oriented. It excludes planning history, Kanban cards, fixture matrices, regression test fixtures, and internal audit notes.
