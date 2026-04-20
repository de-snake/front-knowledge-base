- **Curator profile endpoint.** A standalone `CuratorProfile` is called out across Stage 1, Stage 2a Q4, and Stage 2b Q3. Today it is missing. Shipping this unblocks "Who manages this pool?" and "Who manages this strategy?" on both flows.

==note: and/or external linkl + summary from DefiLlama or similar==

- **Parameter-change log + pending governance feed.** Both flows (Analyze Q5-LP, Analyze Q4-CA, Monitor 6a, Monitor 6b) rely on the same `EventFeedItem` / `GovernanceChange[]` machinery. One stream, many readers.
- **Historical series (7 series).** Supply rate 90d, incentive 90d, composite APY 90d, utilisation 90d, TVL 90d, borrow rate 30d, volatility 90d, oracle prices 90d, share price 90d, price-impact 90d. Backend needs to store and serve these daily.
- **Preview type family.** `TransactionPreview`, `PreviewRoute`, and `RawTx` are missing. Today Preview is the weakest stage in terms of served fields — which is the highest-leverage one to harden because it's the execution gate.
- **RWA / KYC extension (`RwaAssetProfile`, `RwaComplianceProfile`).** 32 additional fields across the stages. Needed end-to-end before the Securitize-integrated CMs are safe to promote in the UI.
- **PnL / returns endpoint.** Flagged as the single largest information gap by the UX audit. Requires: account value history (per-tx or daily), cost-basis anchor at entry, yield-source decomposition (farming / rewards / price appreciation / borrowing cost / protection-bot fees), merkle-reward attribution (rewards accrue to the owner wallet, not the CA — need explicit linkage for PnL totals).
- **Before/after transaction preview component.** Backed by the `TransactionPreview` family above, but the component itself — two-column current → projected for HF, leverage, equity, position size, net APY — is a first-class product surface that every action flow (Add Collateral, Reduce Leverage, Increase Leverage, Enter Farm, Partial Withdrawal, Close) consumes.
  
  ==note: maybe it's on the wallet side though?==
- **Scenario simulator + virtual liquidation counter.** Both are backend-dependent risk-analysis primitives that surface the same underlying facts already needed for Monitor stage, but in a "what if" frame. The virtual-liquidation counter (how many times the position would have been liquidated in the past 90 days based on historical price action) is a high-trust primitive that competitors don't offer.
- **Contextual recommendation engine.** Quick-Actions logic (HF < 1.1 → Add Collateral / Reduce Leverage; HF > 1.5 → suggest Increase Leverage; unclaimed rewards > 0 → Claim; better strategy available → suggest switch) needs a defined rule matrix agreed between product, protocol, and the agent reasoning layer. Today it lives only in the design spec as described behaviour.
  
  ==note: don't forget that there are current recommendations for better strategies if present + for specific reward / withdrawal events==