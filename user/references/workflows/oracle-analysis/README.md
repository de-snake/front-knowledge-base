# Oracle analysis agent workflow

This workflow turns an oracle setup into a decision-grade analysis that an agent can use during Pool deposit, Credit Account opening, Credit Account management, and market-comparison work.

The goal is not to label an oracle as "good" or "bad." The goal is to understand exactly what price the protocol uses, how that price is built, what stress it recognizes, what stress it hides, and who bears loss when the oracle's chosen price diverges from executable value.

Conclusion invariant: oracle analysis is position-side-specific. The same feed can be borrower-friendly and LP-unfriendly, or LP-protective and borrower-unfriendly. Every final verdict must name the side, token role, stress direction, and loss bearer.

## What this workflow does

It transforms a token, market, or strategy scope into an oracle memo with:

1. A recursive feed dependency graph.
2. A reconstructed pricing formula.
3. A node-by-node oracle type classification.
4. A source-primitive audit for market, fundamental, NAV, hardcoded, and hybrid feeds.
5. A side-aware stress-mode analysis that maps short-term volatility, long-term depeg, manipulation, staleness, liquidity, and liquidation feasibility.
6. A protocol-fit verdict for Gearbox, Morpho, or another lending market, split by position side.

## Source framing

Use the Steakhouse Financial field guide as the conceptual anchor: oracle design is a tradeoff between responsiveness and stability. Market feeds recognize stress quickly but can amplify liquidation cascades when liquidity is thin. NAV, fundamental, and hardcoded feeds filter short-term noise but can hide real divergence and create liquidity traps or shadow bad debt. Hybrid designs, including MetaOracle-style primary/backup systems, try to combine stability with delayed responsiveness when deviations persist.

Reference: [No Country for Old Prices: A Field Guide to DeFi Oracles](https://kitchen.steakhouse.financial/p/no-country-for-old-prices-a-field).

## Oracle taxonomy used by this workflow

- **Market** — observed trade execution price or derivative: Chainlink market feed, Pyth, DEX TWAP, VWAP, auction price, Pendle market TWAP. Strength: responsive to executable market value. Weakness: manipulation, temporary dislocations, liquidation-cascade risk if liquidity is thin.
- **Fundamental** — primary-market or issuer/admin exchange rate, collateralization ratio, proof-of-reserves ratio, or underlying asset reference used because redemption is expected to hold. Strength: matches the contractual or primary-market claim. Weakness: adds trust in issuer/admin/reporting and can miss secondary-market stress.
- **NAV** — intrinsic value from underlying holdings or accounting, including ERC4626 `convertToAssets`, staking-derivative exchange rates, fund NAV reports, and tokenized-fund attestations. Strength: resists short-term volatility and manipulation. Weakness: liquidity-trap risk when assets cannot be sold or redeemed near NAV.
- **Hardcoded** — fixed rate such as `1 USDT = 1 SampleDebtToken`. Strength: no market-manipulation surface in the feed itself. Weakness: no mechanism to surface depeg or issuer failure; losses shift to lenders or pool users if parity breaks.
- **Hybrid / composite** — formulas, bounded feeds, main/reserve pairs, MetaOracle-style primary/backup systems, Pendle factory oracle plus SY/USD, Curve TWAP plus Chainlink quote, or any multi-node path. Strength and weakness depend on each node and the switching/bounding logic. The weakest node or most delayed switch usually controls stress behavior.

## Files

- `workflow.json` — machine-readable stage graph, dependencies, parallelization, and output contracts.
- `stage-contracts.md` — exact input/output contract for every stage.
- `parallelization-and-context.md` — what can run in parallel and how the parent agent avoids context bloat.
- `subagent-prompts.md` — paste-ready prompts for delegated workers.
- `runbook.md` — execution order, artifact-root convention, validation, and example on-chain probes.
- `output-structure.md` — canonical run folder layout with per-token and per-PT subfolders.
- `gearbox-price-feed-parsing.md` — Gearbox-specific PFS and price-feed parsing rules grounded in the curator configuration guide.
- `examples/sample-vault-feed-map.md` — example mapping for the SampleVaultToken Gearbox feed chain.

## Core execution rule

Do not stop at a top-level feed type or human label.

Do not produce a universal verdict. Conclusions must be side-aware:

- borrower / Credit Account operator;
- pool LP / lender;
- liquidator;
- curator / operator.

For example, a hardcoded collateral price can be better for borrowers during a temporary market depeg because it delays liquidation, while worse for LPs if the executable collateral value has fallen and liquidation cannot clear. A market oracle can be better for LPs because it recognizes stress early, while worse for borrowers when a temporary thin-liquidity dislocation liquidates otherwise recoverable collateral.

The parent agent must parse the oracle as a dependency DAG:

```text
asset price used by protocol
  = top-level protocol feed
    = child feed(s)
      = primitive source(s)
```

Examples:

```text
SampleVaultToken/USD
= ERC4626/accounting feed
  × SampleBaseToken/USD

SampleBaseToken/USD
= Curve SampleBaseToken/SampleDebtToken TWAP
  × bounded SampleDebtToken/USD

SampleDebtToken/USD
= bounded Chainlink SampleDebtToken/USD
```

```text
PT/USD
= bounded(
    composite(
      Pendle factory PT→SY oracle
      × SY/USD feed
    )
  )
```

## Expected final outputs

A complete oracle-analysis run should end with:

- one returned `<run_artifact_root>/` folder;
- `run-manifest.json` and `index.md` at the run root;
- one subfolder per analyzed token under `tokens/<token-scope-slug>/`;
- one subfolder per analyzed PT market under `pt-markets/<pt-scope-slug>/`;
- within each token / PT folder:
  - `oracle/feed-graph.md` — recursive feed graph, addresses, source primitives, and pricing formula;
  - `oracle/node-classification.md` — oracle type and risk role for every node;
  - `oracle/source-primitive-audit.md` — Chainlink/Pyth/Curve/Pendle/ERC4626/NAV/fundamental/hardcoded evidence;
  - `oracle/stress-tradeoff-analysis.md` — short-term volatility, long-term depeg, manipulation, staleness, cascade/trap mapping;
  - `oracle/protocol-fit-memo.md` — Gearbox/Morpho/market-specific verdicts split by side, parameter implications, and open blockers;
  - `verification/oracle-analysis-verification.md` — per-scope checks proving the graph, math, classification, and links are complete;
- `verification/final-oracle-analysis-verification.md` at the run root.

The user-facing answer should return the run folder path and the final index path, not raw evidence.
