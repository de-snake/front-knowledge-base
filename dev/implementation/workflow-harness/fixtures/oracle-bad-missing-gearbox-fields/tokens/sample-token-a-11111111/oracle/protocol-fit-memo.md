# Protocol fit memo

Status: pass.

Gearbox parsing reference applied: user/references/workflows/oracle-analysis/gearbox-price-feed-parsing.md.
Child-source detail: Gearbox External wrapper points to the Chainlink SampleBaseToken/USD source primitive.
Primitive classification: Gearbox wrapper is hybrid, Chainlink source is market, scalar is hardcoded.
Formula evidence: `SampleBaseToken/USD = Chainlink_SampleBaseToken_USD × 1`.
Stress framing: liquidity-cascade and liquidity-trap branches are covered.

## Gearbox required fields
- Main feed path: Gearbox External aggregator -> Chainlink SampleBaseToken/USD.
- Reserve feed path: unknown marker recorded.
- Safe-pricing rule: unknown marker recorded.
- Exit Health Factor implication: price down can reduce exit Health Factor.
- Liquidation Threshold: unknown marker recorded.
- Max leverage implied by Liquidation Threshold: unknown marker recorded.
- Staleness and bounds: checked.
- PFS chain / token availability status: unknown marker recorded.
- Instance Owner or feed-update authority: unknown marker recorded.
- PFS add/update status: unknown marker recorded.

## Side-specific verdict matrix
| position_side | token_role | stress_direction | loss_bearer | formal status |
| --- | --- | --- | --- | --- |
| credit_account_borrower | collateral | price down / stale report | borrower liquidation risk | pass |
| pool LP / lender | collateral | persistent depeg | pool LP bad debt risk | pass |
| liquidator | collateral | liquidity loss | liquidator execution risk | pass |
| curator/operator | collateral | feed swap / timelock | curator intervention risk | pass |
