# Credit account
CA operator opens an isolated on-chain Credit Account, borrows the pool's underlying, swaps into a target collateral, and runs a leveraged strategy inside a whitelisted adapter set.

### Collateral
Collateral is the yield-generating token inside of the credit account. 
### Underlying token
Underlying token is the asset that user has on his EOA (wallet) that he uses to deposit into the strategy. 
During the credit account opening, underlying token is swapped to the **collateral** of the strategy. 
Underlying token should be used in any PnL / Revenue estimations (e.g. how much USDC I made in the mEdge strategy?) and is the target token for the withdrawal from the credit account. 

### IRM
Interest rate model
utilization = borrowed amount / supply
![[telegram-cloud-photo-size-2-5409340258404472434-y.jpg]]

# Sources of yield

1. **Pools (passive lending)** — the LP deposits a base asset (USDC, WETH, etc.) into a curated pool and earns yield from borrowers plus incentives. No leverage, no liquidation.
2. **Credit Accounts (leveraged positions)** — the CA operator opens an isolated on-chain Credit Account, borrows the pool's underlying, swaps into a target collateral, and runs a leveraged strategy inside a whitelisted adapter set.

# Canonical loop 
`Discover → Analyze → Propose → Preview → Execute → Monitor`

The same six stages apply to both Pool and Credit Account flows. This is the organising spine of the rest of the document.

1. **Discover** — the user scans the unified opportunity surface and narrows to 1–3 candidates.
2. **Analyze** — the user does due diligence on each finalist and forms an evidence-backed ranking.
3. **Propose** — the user commits to a specific action: amount, collateral, leverage, route. Or explicitly decides to do nothing.
4. **Preview** — the exact transaction package is simulated against current chain state; pass/fail gate.
5. **Execute** — the previewed bytes are signed (human-in-the-loop or bot) and submitted.
6. **Monitor** — periodic checks that thesis still holds; meaningful deviation loops back to Analyze, failed preview loops back to Propose.
