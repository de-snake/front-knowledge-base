# Stress tradeoff analysis

Status: pass.

- Temporary market dislocation / short-term volatility: borrower liquidation risk can rise before market normalization.
- Persistent depeg, insolvency, issuer failure, or redemption impairment: pool LP bad debt risk can dominate.
- Thin-liquidity manipulation and TWAP lag: liquidator execution risk and stale price use are review triggers.
- Stale report, stale external feed, or delayed update: curator/operator should review feed update status.
- Liquidation feasibility: liquidator receives execution risk when collateral sale path is impaired.
- Liquidity-cascade risk: forced liquidation can amplify price pressure.
- Liquidity-trap risk: NAV-like pricing can hide weak exit liquidity.
- Who bears first loss / loss bearer: named per side in protocol-fit-memo.md.
