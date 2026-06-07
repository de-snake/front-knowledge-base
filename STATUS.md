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

Five public packages are available:

1. A richer apyUSD investment-research dossier that follows the asset-specific mining methodology directly, without the Analyze → Propose formatting harness.
2. Matching rich research packages for apxUSD, PRIME, and deSPXA, using the old human-readable report style and support corpus.
3. A deterministic Analyze → Propose runner demo that can scaffold and validate a combined asset-diligence + oracle-analysis run for USDat / sUSDat, now enriched with old-run X/social, PT-market, and quantitative risk/return layers.

The rich investment-research packages include:

- apxUSD: `dev/implementation/reproducible-runs/apxusd-investment-research-20260604/RESULT.md`
- apyUSD: `dev/implementation/reproducible-runs/apyusd-investment-research-20260604/RESULT.md`
- PRIME: `dev/implementation/reproducible-runs/prime-investment-research-20260604/RESULT.md`
- deSPXA: `dev/implementation/reproducible-runs/despxa-investment-research-20260604/RESULT.md`
- reproduction protocol and scoped input inside each package root
- methodology, technical dossier, research notes, raw snapshots, and applicable X/social, PT-market, and quantitative support layers under each package's `run/` subtree

The USDat / sUSDat workflow-harness package includes:

- readable result: `dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/RESULT.md`
- input: `dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/input.json`
- filled artifacts: `dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/run/`
- reproduction instructions: `dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/README.md`

## apyUSD investment-research result

Question:

> What source-linked token context should an agent carry before treating apyUSD as a candidate Gearbox asset?

Short result:

apyUSD is a non-rebasing ERC-4626-style savings wrapper over apxUSD. Its investment risk is not just market price; it combines vault-share risk, issuer/backing risk, asynchronous redemption risk, secondary-liquidity risk, and upgrade / pause / deny-list control surfaces.

The report does not approve the asset. It concludes that apyUSD can be used as a factual substrate for later reasoning, but live use still requires fresh checks for backing reconciliation, audit scope, receipt/redemption mechanics, route liquidity, pending admin changes, and holder / Credit Account eligibility.

Full readable result:

[`dev/implementation/reproducible-runs/apyusd-investment-research-20260604/RESULT.md`](dev/implementation/reproducible-runs/apyusd-investment-research-20260604/RESULT.md)

Reproduction protocol:

[`dev/implementation/reproducible-runs/apyusd-investment-research-20260604/REPRODUCE.md`](dev/implementation/reproducible-runs/apyusd-investment-research-20260604/REPRODUCE.md)

Integrity check:

```text
Status: pass
```

## USDat / sUSDat workflow-harness result

Question:

> Should USDat or sUSDat be treated as acceptable Gearbox Credit Account collateral candidates on Ethereum mainnet when borrowing USDC at a 9% borrow-rate assumption?

Short result:

USDat is the stronger Analyze-stage candidate because the supplied Gearbox feed is market-derived from the USDat/USDC Curve pool and observed liquidity is deeper.

sUSDat remains more conditional because the supplied feed uses ERC-4626 accounting over USDat while immediate recovery depends on thinner liquidity, queue processing, and issuer / STRC realization.

Neither candidate is ready for Preview or Execute without additional live inputs.

Full readable result:

[`dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/RESULT.md`](dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/RESULT.md)

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

The public `main` tree is presentation-oriented. It excludes planning history, Kanban cards, fixture matrices, regression test fixtures, and internal audit notes.
