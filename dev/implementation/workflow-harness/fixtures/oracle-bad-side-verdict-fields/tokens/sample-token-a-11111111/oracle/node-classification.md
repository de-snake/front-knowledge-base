# Node classification

Status: pass.

Formula: `SampleBaseToken/USD = Chainlink_SampleBaseToken_USD × 1`.

| node | type | role | input | output |
| --- | --- | --- | --- | --- |
| Gearbox External aggregator | hybrid | top-level wrapper | Chainlink primitive answer | SampleBaseToken/USD price |
| Chainlink SampleBaseToken/USD | market | source primitive | Chainlink report | USD price |
| hardcoded scalar 1 | hardcoded | unit scalar | invariant decimals | multiplier |

No node is unclassified.
