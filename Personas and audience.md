# Personas and audience

## Pool LP (passive lender)

A depositor who wants yield on a base asset without operational overhead, volatility in principal, or liquidation exposure.

**Typical profiles**

| Profile | Description |
| --- | --- |
| **DeFi-native yield farmer** | cares about net APY vs comparable venues (Aave, Morpho, Euler), sustainability of incentives, and exit liquidity. |
| **Treasury / fund operator** | cares about counterparty surface, governance transparency, curator track record, and concentration. |
| **Institutional / RWA-oriented allocator** | cares about all of the above plus compliance-layer risks (freeze authority, liquidator whitelist, redemption mechanics). |
| **Agent (LLM) acting for any of the above** | needs the same facts, serialised. |

The LP has **no health factor, no liquidation, no leverage**.

**Loss vectors**

| Vector | Mitigation strategy & comments | Priority |
| --- | --- | --- |
| Bad debt | Review collateral (isnt token bullshit); Track socials for exploits; Track accounts with unrealized bad debt (market price tracked somewhere is very different from gearbox oracle [usually fundamental]); Check insurance buffer size | 1 |
| Locked liquidity (blocked withdrawals) | Review collateral oracle setup (market/fundamental). Fundamental = problems with tokens lead to bankrun while borrowers arent liquidated (remember USR, rsETH, xUSD cases). Track socials for exploits; Track accounts with unrealized bad debt (market price tracked somewhere is very different from gearbox oracle [usually fundamental]) | 1 |
| yield decay | Review yield history; Yield decomposition | 1 |
| silent exposure changes by the curator | Review curator legitness, track upcoming changes: {Max asset exposure, new CM, oracle, LT ramp, liquidation premium, IRM, quota rate, Pool pause} | 1 |
| and — for RWA-backed pools — frozen accounts and liquidator scarcity | read RWA T&C, verify liquidation liquidity available | 2 |
| oracle manipulation/staleness | review oracle price source. how resilient it is? how frequently it goes stale? | 2 |

## CA operator (leveraged user)

A user who opens and manages an isolated Credit Account to run a leveraged strategy.

**Typical profiles**

| Profile | Description |
| --- | --- |
| **Leveraged-yield farmer** | stETH / USDe / LP-token loop; cares about `collateral yield × leverage − borrow cost − quota − fees` and HF stability. |
| **Structured-product / fund desk** | treats CAs as building blocks for a larger portfolio; cares about liquidity and exit paths under stress. |
| **RWA-collateral user (new, post-Securitize integration)** | wants leverage on tokenised securities; additionally cares about freeze authority, redemption windows, KYC validity. |
| **Agent (LLM) acting for any of the above** | runs the same decision loop autonomously or with human approval at Execute. |

The CA operator owns an isolated position.

**Loss vectors**

| Vector | Mitigation strategy & comments | Priority |
| --- | --- | --- |
| yield decay | Review yield history; Yield decomposition; Utilization spike (lp withdrew), utilization grows (was low in the beginning) | 1 |
| liquidation | review oracle setup (fundamental - safer) | 1 |
| collateral exposure | review collateral; one may not be liquidated immediately, but have its assets gone worthless or frozen (remember RLP) | 1 |
| expiration | track expiration time | 1 |
| silent exposure changes by the curator | Review curator legitness, track upcoming changes {LT, quota rate, IRM, oracle (note that main oracle can be changed for reserve without timelock and cause liquidations), CM pause, token forbidden} | 1 |
| Limited enter/exit liquidity | Enter slippage/price impact is displayed in advance. Upon exit, liquidity can change or price can drop. Some assets have only delayed redemptions | 1 |
| oracle manipulation/staleness/configuration/safe price | review oracle price source. how resilient it is? how frequently it goes stale? if collaterla is priced with composite, is underlying priced accordingly (e.g. underlying wstETH/USD; collateral: cp0xLRT/wstETH * wstETH/stETH * stETH/USD) | 2 |
|RWA issuer intervention| Read T&C, be a good guy | 1 |
