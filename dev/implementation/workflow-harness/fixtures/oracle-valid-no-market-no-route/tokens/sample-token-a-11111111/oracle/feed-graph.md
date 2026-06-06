# Feed graph

Status: pass.

Top-level feed: Gearbox External aggregator for SampleBaseToken/USD.
Child feed / source primitive: Chainlink SampleBaseToken/USD report at 0x5555555555555555555555555555555555555555.
Hardcoded child: scalar 1.0; invariant is that the scalar is unit-only and breaks if decimals are changed.

Formula: `SampleBaseToken/USD = Chainlink_SampleBaseToken_USD × hardcoded_scalar_1`.
The graph reaches the source primitive instead of stopping at the External label.
