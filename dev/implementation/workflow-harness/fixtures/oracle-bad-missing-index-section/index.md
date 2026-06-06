# Oracle analysis fixture index

## Scope table
| scope_id | token / PT market | artifact_dir | status |
| --- | --- | --- | --- |
| eth-mainnet-sample-base-token-gearbox | SampleBaseToken token | tokens/sample-token-a-11111111 | pass |

## Feed formulas
Formula: `SampleBaseToken/USD = Chainlink_SampleBaseToken_USD × hardcoded_scalar_1`.

## Side-specific verdict matrix
| position_side | token_role | stress_direction | loss_bearer | status |
| --- | --- | --- | --- | --- |
| credit_account_borrower | collateral | price down / stale report | borrower liquidation risk | pass |
| pool LP / lender | collateral | persistent depeg | pool LP bad debt risk | pass |
| liquidator | collateral | liquidity loss | liquidator execution risk | pass |
| curator/operator | collateral | feed swap / timelock | curator intervention risk | pass |

## Open blockers
None.

## Artifact map
- `tokens/sample-token-a-11111111/oracle/feed-graph.md`
- `tokens/sample-token-a-11111111/oracle/node-classification.md`
- `tokens/sample-token-a-11111111/oracle/source-primitive-audit.md`
- `tokens/sample-token-a-11111111/oracle/stress-tradeoff-analysis.md`
- `tokens/sample-token-a-11111111/oracle/protocol-fit-memo.md`

## Notes
The run is intentionally missing the contract validation section.
