# Example — SampleVaultToken Gearbox feed map

This example records the shape discovered for an Ethereum SampleVaultToken Gearbox price feed during an operator discussion. Re-run the live workflow before using the values for execution.

## Scope

- Asset: SampleVaultToken.
- Chain: Ethereum mainnet.
- Protocol context: Gearbox Credit Account collateral analysis.
- Example position side: Credit Account borrower using SampleVaultToken as collateral.
- Counter-side to analyze separately: pool LP exposure to the same collateral path.
- Top-level feed: `0x4444444444444444444444444444444444444444`.
- Known LT in referenced market: `0.86`.

## Feed graph

```text
SampleVaultToken/USD
= Gearbox PRICE_FEED::ERC4626
  top-level feed: 0x4444444444444444444444444444444444444444
  child priceFeed(): 0x3333333333333333333333333333333333333333

SampleBaseToken/USD
= Gearbox PRICE_FEED::CURVE_TWAP
  feed: 0x3333333333333333333333333333333333333333
  token: SampleBaseToken 0x1111111111111111111111111111111111111111
  pool: 0x5555555555555555555555555555555555555555
  child priceFeed(): 0x5555555555555555555555555555555555555555

SampleDebtToken/USD
= Gearbox PRICE_FEED::BOUNDED over Chainlink SampleDebtToken/USD
  bounded feed: 0x5555555555555555555555555555555555555555
  child priceFeed(): 0x5555555555555555555555555555555555555555
```

## Node classification

- Top-level SampleVaultToken feed: **hybrid / NAV-accounting** node. It wraps an ERC4626-style accounting/exchange-rate path and inherits all child price risk.
- SampleBaseToken Curve TWAP feed: **market** node. It observes the SampleBaseToken/SampleDebtToken market through Curve TWAP mechanics.
- SampleDebtToken bounded feed: **hybrid / bounded market** node. It wraps Chainlink SampleDebtToken/USD with bounds.
- Chainlink SampleDebtToken/USD: **market/reference** primitive.

## Stress implication

This is not a simple stablecoin oracle.

It combines:

- accounting or ERC4626 value for SampleVaultToken;
- Curve market value for SampleBaseToken/SampleDebtToken;
- bounded Chainlink value for SampleDebtToken/USD.

The setup can be reasonable, but the agent must analyze both sides:

- For the Credit Account borrower: whether the accounting layer, Curve TWAP, and bounded SampleDebtToken leg increase liquidation risk, suppress collateral value, or allow borrowing against value that may not be executable.
- For the pool LP: whether the same path recognizes stress early enough to avoid bad debt, or whether the accounting layer can keep collateral value above executable exit value.
- For liquidators: whether liquidation would deliver liquid transferable collateral or a queue-/issuer-constrained claim.
- For curator/operator: whether bounds, PFS entries, or source feeds require active intervention.

## Execution note

Do not reuse this example as live evidence. It demonstrates the graph shape and expected analysis depth. A live run must refresh feed answers, timestamps, bounds, Curve liquidity, issuer/queue state, and the exact Credit Manager configuration.
