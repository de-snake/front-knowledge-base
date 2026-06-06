# Oracle analysis fixture index

## Scope table
| scope_id | token / PT market | artifact_dir | status |
| --- | --- | --- | --- |
| eth-mainnet-sample-base-token-gearbox | SampleBaseToken token | tokens/sample-token-a-11111111 | review_required |

## Feed formulas
Formula: `SampleBaseToken/USD = Chainlink_SampleBaseToken_USD × hardcoded_scalar_1`.

## Side-specific verdict matrix
| position_side | token_role | stress_direction | loss_bearer | status |
| --- | --- | --- | --- | --- |
| credit_account_borrower | collateral | price down / stale report | borrower liquidation risk | review_required |
| pool LP / lender | collateral | persistent depeg | pool LP bad debt risk | review_required |
| liquidator | collateral | liquidity loss | liquidator execution risk | review_required |
| curator/operator | collateral | feed swap / timelock | curator intervention risk | review_required |

## Open blockers
- Market or Credit Manager: investigated_no_result after adapter-valid search; not Preview readiness.
- Route availability: investigated_no_result after adapter-valid search; not Execute readiness.

## Artifact map
- `tokens/sample-token-a-11111111/oracle/feed-graph.md`
- `tokens/sample-token-a-11111111/oracle/node-classification.md`
- `tokens/sample-token-a-11111111/oracle/source-primitive-audit.md`
- `tokens/sample-token-a-11111111/oracle/stress-tradeoff-analysis.md`
- `tokens/sample-token-a-11111111/oracle/protocol-fit-memo.md`
- `tokens/sample-token-a-11111111/raw/evidence-ledger.json`

## Validation result
Status: review_required.
