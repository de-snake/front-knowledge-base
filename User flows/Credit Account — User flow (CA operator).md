### Stage 1 · Discover (Strategy)

**User's goal:** "Give me strategies whose base collateral, leverage ceiling, and economics are in my target band."

**What the user does:**

1. Filters the unified feed by chain, target collateral token, access (`permissionless` / `kycRequired`), and agent-side whitelist.
   ==note: what if there are 0 strategies available based on token/chain? 
   do we interfere and suggest bridging / swapping?==
   
2. Reads each `StrategyOpportunity` for sizing bounds (==`minDebt`, `maxDebt`==), `borrowableLiquidity`, `maxLeverage`, `borrowApy`, and the headline economics (`maxLeverageYield`, ==`bestBaseYield`==).
   
   ==note: for the minDebt and maxDebt, don't we need to estimate a desired position size from the user first? Different CMs have different minDebt and maxDebt.==
   
   ==note: bestBaseYield - why is that interesting to the user?==
   
3. Checks operating flags: `isPaused`, `hasDelayedWithdrawal`.
4. Narrows to 1–3 strategies.

**Key questions (map to Stage 1 StrategyOpportunity extension):**

- Can I enter at my target size? (`minDebt`, `maxDebt`.) 
- How much room is left, and how much leverage is available? (`borrowableLiquidity`, `maxLeverage`, `borrowApy`.)
- What's the best visible leveraged economics? (`maxLeverageYield: LeveragedYieldBreakdown`, ==`bestBaseYield: YieldBreakdown`==.)
- Which collateral paths and quota constraints exist? (`collaterals: StrategyCollateral[]`.)
- Is the strategy currently usable, and does it involve non-atomic settlement? (`isPaused`, `hasDelayedWithdrawal`.)

### Stage 2 · Analyze — CA due diligence
#### Q1 · What will this position cost me, is the yield worth it?

Net yield = (collateral yield × leverage) − borrow cost − quota interest − fees − entry/exit friction.

Required evidence:

- Collateral token yield (base APY), current + 90d history — if this is below borrow cost, more leverage = more loss.
  
  ==note: should probaby combine w/ borrow rate on the same graph==
  
- Borrow rate, current + 30d history.
- IRM parameters — if +10 pp utilisation drives borrow rate materially higher, economics are fragile.
- Per-token quota rate — the annual holding cost in the quota system, on top of borrow rate. High quota rate = position bleeds when prices are flat.
- Quota increase fee — one-time entry cost.
- Liquidation fee and premium — how much the user loses beyond position value if liquidated.
  
  ==note: deleverage info seems much more appropriate than liquidation specifics since they rarely happen==
  
- Entry swap cost at position size — swapping underlying → collateral has real price impact; at moderate sizes ==it can be 2–3 weeks of yield.==
  
  ==note: is that true? example?==
  
- Breakeven period — `entry_cost / daily_net_yield`. If breakeven exceeds the user's horizon, the strategy is uneconomical regardless of headline APY.
  
  ==note: again, is this a reasonable concern to consider? does that happen?==
#### Q2 · How safe is my collateral? What could cause sudden liquidation?

Two separate concerns: **what is the asset** (inherent properties) and **how does Gearbox wrap it** (governance config).

_Asset properties per collateral token:_ 
- issuer, 
- asset type (native / wrapped / LST / LP / RWA / stablecoin / synthetic), 
- native lock-up / withdrawal queue, 
- underlying yield source, 
- ==90d volatility==.

==note: historical price chart? do we have this data for any given token / oracle?==

_Per-token Gearbox parameters:_ 
- liquidation threshold (LT determines max leverage: `1 / (1 − LT)`), 
- max leverage pre-computed, 
- LT ramp schedule (if active, HF will drop on schedule with zero price movement), 
- forbidden-tokens mask, 
- delayed-withdrawal support per token (via `WithdrawalCompressor.getWithdrawableAssets(creditManager)`), 
- ==adapter-accessible liquidity (the user can only route through CM-approved adapters, not the full market).== - ?

_Oracle risk:_ 
- methodology per token (no oracle type is "good" or "bad" in isolation — market oracle on a liquid token is fine, on a thin market it's manipulation risk; hardcoded oracle is safe from manipulation but can prevent liquidation if real price diverges), 
- ==historical main and reserve oracle prices (90d daily)==, 
  
  ==note: should we provide that? or just a link to the oracle contract?==
  
- oracle staleness period.

_Structural risk disclosure:_ 
- factual description of structural risk ("in case of bad debt exceeding insurance, losses are socialised across all LPs", "this collateral has a 7-day withdrawal queue").

_Cross-reference._ Borrow rate history from Q1 is also a liquidation-risk signal: extreme rate spikes can liquidate via rapid interest accrual, not just reduce profit.

_Exit feasibility:_ 
- price impact via router at position size (current + 90d), 
- borrowable liquidity remaining (can the user adjust leverage later?), 
- `minDebt` / `maxDebt` boundaries (can the user iteratively unwind?).

**Extension**: Credora risk scores + BDP (Bad Debt Probability) if available for the token. 

**RWA extension.** Compliance risks per RWA token in the CM:

- Transfer restriction type (DS Token Protocol, ERC-3643, or custom) — a compliance layer that can block transactions.
- Freeze capability — if the CM uses `SecuritizeKYCFactory`, Securitize's admin can call `setFrozenStatus()` on the user's Credit Account. When frozen: no deposits, no withdrawals, no borrowing, no repaying, no liquidation.
- Freeze authority — the specific address / entity that holds the freeze power.
- Investor reassignment risk — `setInvestor()` can reassign the CA to a different investor (intended for estate settlement / lost keys, but structurally it exists).
- Whitelisted liquidator count (from the CA perspective — few liquidators = the user may sit in a liquidatable state longer).
- Redemption windows and secondary market liquidity — when can the user actually convert RWA back to cash.

#### Q3 · Who manages this strategy, and what are the hard constraints?

- Curator / controller address + name — trust frame.
  ==note: add more info about the curator, e.g. from DefiLlama==
- CM expiration date — for expirable strategies, is remaining time long enough for profitability after entry costs?
- `maxDebtPerBlockMultiplier` — zero means no new borrows allowed; the user skips.
  
#### Example info from DefiLlama
https://defillama.com/protocol/kpk

[Website](https://kpk.io/)[GitHub](https://github.com/karpatkey)[Twitter](https://x.com/kpk_io)

Treasury breakdown 
https://defillama.com/protocol/treasury/kpk

[TVL: Sum of curated vault deposits (Morpho, Aleph, Euler, Gearbox), Gearbox v3.1 credit account collateral, and kpk Fund AUM via onchain NAV Calculators.View code on GitHub](https://github.com/DefiLlama/DefiLlama-Adapters/blob/main/projects/kpk/index.js)

https://defillama.com/protocol/tvl/kpk

----

**KYC-gated CM operational extension:**

- Operation routing — KYC-gated CMs route everything through `SecuritizeKYCFactory → SecuritizeWallet → CreditFacade`. The user can't call `CreditFacade` directly.
- Bot permissions blocked — `SecuritizeWallet` explicitly blocks bot permissions; position management must go through the factory.

#### Q4 · What has changed recently, and what might change next?

Parameter change log (CM-level): LT reductions (the user's HF could drop again), token forbids (exit routes shrink), IRM changes (borrow rate spike). Pending governance changes queued in Safe TX or timelock — with description, execution time, and affected parameters.

==note: do we really need to provide this info?==

**Output of Analyze.** A ranked, evidence-backed analyzed shortlist, same contract as the LP side: candidate ref, adjusted return estimate, overall risk score, risk breakdown across collateral / curator / smart-contract / market / exit / — for RWA — compliance.

### Stage 3 · Propose (CA)

**User's goal:** "Commit to an exact action — sizing, target collateral, target leverage, route, or explicitly do nothing."

The user answers:

1. Is the current position (if any) already acceptable? Rebalance cost vs expected gain?
2. What size, at what target leverage? (Constrained by `minDebt` / `maxDebt`, `borrowableLiquidity`, internal concentration cap.)
    ==note: add info about credit manager potential / suggested==
3. Which route? (Entry swap: underlying → collateral, via which adapter set.)
4. ~~Any better alternative from the shortlist? Do I even act right now?~~

**Output.** A proposal package with candidate ref, action type (`openCA`, `adjustLeverage`, `rebalance`, `no-op`), sizing, target leverage, collateral choice, and the exact unsigned multicall bytes.

### Stage 4 · Preview (CA)

**User's goal:** "Will this exact multicall produce the position I expect, right now, against current chain state?"

Via SDK router simulation, the user checks:

- Simulated health factor after open — if lower than expected, reduce leverage or abort. Hard floor: HF > 1.07 (user's own threshold; default flag).
- Position value USD — sanity check against proposal sizing.
- Actual leverage — may differ from target due to swap impact. 5 → 5.2 × acceptable; 5 → 6.1 × concerning.
  ==note: what's the real delta typically?==
- Swap impact in bps — compare to entry cost estimate from Analyze. Significantly worse = abort.
- Token balances after open — full composition post-open.
- Deviation from proposal — flagged if `borrowable liquidity dropped >40 % since analysis`, `HF below 1.07 threshold`, etc.
- Gas estimate (USD).
- Warnings array.
- Multicall data (ready to submit).

**Gate.** Fail → loop back to Propose (not Analyze); the thesis can still hold.

### Stage 5 · Execute (CA)

Same invariant as the LP side: the previewed multicall is the executed multicall. Human-in-the-loop for high-value or first-time actions, bot execution within scoped permissions for automated management. For KYC-gated CMs the call goes through `SecuritizeKYCFactory → SecuritizeWallet → CreditFacade` rather than direct to `CreditFacade`.

### Stage 6 · Monitor (CA)

**User's goal:** "Is my position safe, what's moving HF, am I making money?"

- **Position state.** 
	- Health factor (the metric), 
	- total value USD, 
	- TWV USD (numerator of HF — if TWV dropped but total value didn't, cause is LT change or quota cap, not price), total debt USD,
	  
	  ==note: seems unnecessary==
	  
	- debt breakdown (principal + interest + quota interest + fees), 
	- per-token balances and values, 
	- per-token quota, 
	- current leverage, 
	- HF history, 
	- total-value history.
	  
- **Delayed withdrawals.** 
	- Pending withdrawals per token (expected amount, `claimableAt` timestamp) — the user schedules a claim when the clock matures.
	- Claimable withdrawals (amount, claim calldata). 
	- Phantom-token positions (staked Convex, Infrared vault, Midas redemption) — non-transferable position wrappers that auto-withdraw via adapter on exit.
	  
- **Oracle and collateral health.** 
	- Oracle freshness per token (last update vs staleness period — if a token's oracle is about to be stale, the next update could trigger immediate liquidation),
	- paired main/reserve oracle prices (safe pricing uses `min(main, reserve)` on multicalls, including close — a large divergence means exit HF will be lower than the snapshot suggests), 
	- forbidden-tokens overlap with the user's holdings, 
	- LT-ramp status per token, 
	- enabled-tokens count vs max.
	  
	  ==note: ?==
	  
- **Expiration & operational.** 
	- Expiration date (after expiration, the position is liquidatable regardless of HF with reduced premium), 
	- facade paused status.
	
	==note: I would only display this info if facade is paused / expiration date exists and is sooner than 1m.==
	
- **External changes.** 
	- Parameter changes since last check (the user correlates LT reductions with HF movements), 
	- pending governance changes. ==note: if present==
- **Emergency state bundle.** Facade paused + forbidden tokens affecting the position + loss-policy status + emergency-liquidator active — checked as a unit to detect abnormal CM mode.
  
- **Automation.** 
	- Active bots with permissions (expected: partial-liquidation bot; ==unexpected: unknown bot with `EXTERNAL_CALLS_PERMISSION`)==.
	  
- **RWA own-account compliance.** 
	- Own frozen status (the critical check — if frozen, no action is possible), 
	- investor registry status, 
	- KYC validity. ==note: seems unnecessary in form of a value - would make sense as an alert / notification==
	  
- **RWA upcoming redemptions.** 
	- Next redemption window, 
	- redemption notice deadline — the user plans exits around these.

A meaningful deviation (HF trending down structurally, LT ramp active, forbidden-token overlap, pending governance change) loops back to Analyze.

## Shared decision artifacts (what the loop produces at each stage)

Each stage produces a structured artifact that flows into the next. These are the contracts the frontend, the SDK, and the MCP layer all share.

| Stage    | Artifact (shared by Pool & CA paths)                                                      | Gates into next stage                                    |
| -------- | ----------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| Discover | `Opportunity[]` shortlisted to 1–3                                                        | Agent filter + rank produces `AnalyzedCandidate[]` stubs |
| Analyze  | Ranked `AnalyzedCandidate[]` with profitability, risk, and reasoning                      | Pass if ≥ 1 candidate meets the user's decision criteria |
| Propose  | `ProposedAction` with sizing, target leverage/amount, route, rationale, unsigned tx bytes | Forward to Preview                                       |
| Preview  | `TransactionPreview` — simulated outcome + warnings + calldata                            | `go` / `no-go`; `no-go` loops back to Propose            |
| Execute  | Submitted transaction + receipt                                                           | Updates `UserPoolPosition` or `UserStrategyPosition`     |
| Monitor  | Periodic snapshot + deltas vs last check + pending governance                             | Material deviation loops back to Analyze                 |