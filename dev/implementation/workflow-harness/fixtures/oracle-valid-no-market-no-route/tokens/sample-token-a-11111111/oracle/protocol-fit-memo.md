# Protocol fit memo

Status: review_required.

Gearbox parsing reference applied: user/references/workflows/oracle-analysis/gearbox-price-feed-parsing.md.

This synthetic fixture proves the generalized no-result path, not token-specific policy. It models a valid adapter search where no Gearbox market / Credit Manager and no executable route / quote are found after the declared registry, API, contract, network, and evidence-path checks.

Child-source detail: Gearbox External wrapper points to the Chainlink SampleBaseToken/USD source primitive.
Primitive classification: Gearbox wrapper is hybrid, Chainlink source is market, scalar is hardcoded.
Formula evidence: `SampleBaseToken/USD = Chainlink_SampleBaseToken_USD × 1`.
Stress framing: liquidity-cascade and liquidity-trap branches are covered.

## Gearbox required fields
- Market or Credit Manager: state=investigated_no_result; no market / no credit manager found after Gearbox market registry checked, on-chain contract query attempted, Ethereum mainnet network context named, and evidence path `raw/no-market-no-route-search-log.json` recorded.
- Main feed path: state=found; Gearbox External aggregator -> Chainlink SampleBaseToken/USD.
- Reserve feed path: state=found; reserve feed branch checked in the fixture graph and resolved to the same Chainlink SampleBaseToken/USD primitive.
- Safe-pricing rule: state=found; conservative source-selection rule documented for the wrapper/source primitive pair.
- Exit Health Factor implication: state=found; price down can reduce exit Health Factor for collateral-side borrowers.
- Liquidation Threshold: state=found; synthetic LT parameter slot reviewed as protocol input.
- Liquidation Threshold ramp: state=found; synthetic LT ramp status reviewed with no active ramp in the fixture.
- Max leverage implied by Liquidation Threshold: state=found; max leverage relation documented from the LT input.
- Staleness, bounds, and timestamp controls: state=found; stale reports, bounds, and timestamps reviewed.
- Feed swap / reserve / timelock status: state=found; feed swap path, reserve feed, and timelock status reviewed.
- Delayed-withdrawal branch interaction: state=found; delayed-withdrawal branch reviewed; no live assertion made.
- Forbidden-token branch interaction: state=found; allowed-token / forbidden-token status reviewed in fixture registry context.
- Issuer-controlled branch interaction: state=found; issuer-controlled controls reviewed where applicable.
- PFS chain / token availability status: state=found; PFS token availability checked in fixture search space.
- Instance Owner or feed-update authority: state=found; Instance Owner / feed-update authority recorded in fixture graph.
- Route availability: state=investigated_no_result; no route / no supported route found after route registry checked, route API and contract query attempted, Ethereum mainnet network context named, and evidence path `raw/no-market-no-route-search-log.json` recorded.

## No-result proof bundle
- Registry checked: Gearbox synthetic market registry and route registry fixture surfaces were searched.
- API or contract query attempted: synthetic market API, route API, and on-chain contract query transcript are captured.
- Network context named: Ethereum mainnet fixture scope `eth-mainnet-sample-base-token-gearbox`.
- Evidence path present: `tokens/sample-token-a-11111111/raw/no-market-no-route-search-log.json` and `tokens/sample-token-a-11111111/raw/evidence-ledger.json`.

## Decision effect
The no-market/no-route result is an adequate negative investigation for deterministic adapter checks. It still keeps the workflow at review_required instead of ready_for_preview because absence of a market or route is not an execution recommendation.

## Side-specific verdict matrix
| position_side | token_role | stress_direction | loss_bearer | formal status |
| --- | --- | --- | --- | --- |
| credit_account_borrower | collateral | price down / stale report | borrower liquidation risk | review_required |
| pool LP / lender | collateral | persistent depeg | pool LP bad debt risk | review_required |
| liquidator | collateral | liquidity loss | liquidator execution risk | review_required |
| curator/operator | collateral | feed swap / timelock | curator intervention risk | review_required |
