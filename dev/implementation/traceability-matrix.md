# Traceability matrix

This matrix ties the canonical user-facing flow questions to backend data fields, read/write artifacts, and verification checks. It is intentionally requirement-first: fields exist only because a product / agent decision needs them.

## Requirement ID convention

```text
DR-<persona>-<lifecycle>-<question/stage>
```

- `LP`: Pool LP.
- `CA`: Credit Account operator.
- `DISC`: Discover.
- `AN`: Analyze / due diligence.
- `MON`: Monitor.
- `PROP`: Propose.
- `PRE`: Preview.
- `EXEC`: Execute.

## LP entry flow

| Requirement ID | Source | User / agent question | Decision story | Data / artifact coverage | Verification |
| --- | --- | --- | --- | --- | --- |
| `DR-LP-DISC-001` | [[Pool deposit#Stage 1 · Discover (Pool)]] | Which 1–3 pools match my asset class and current floor APY? | Backend filters by asset class / chain and optionally current composite APY; agent returns identifiers only so Stage 2 re-fetches current facts. | `PoolOpportunitySearchResult`, `OpportunityCandidate`, `PoolOpportunity.{pool_id, chain, underlying_token, currentCompositeApy}` | Search result contains IDs and current timestamps; Stage 2 re-fetch changes candidate values rather than trusting stale Stage 1 copies. |
| `DR-LP-AN-Q1` | [[Pool deposit#Q1 · Where does the yield come from, and is it sustainable?]] | Where does the yield come from, and is it sustainable? | Compare composite APY to floor; split organic vs incentive; if incentive dependency is material, inspect expiry / renewal / top-up evidence. | `PoolOpportunity.yield.*`, `IncentiveLayer[]`, APY series, campaign references | If organic / incentive split missing, verdict is `unknown_review_required`; if current composite missing, gate cannot pass. |
| `DR-LP-AN-Q2` | [[Pool deposit#Q2 · What's my maximum exposure, per token?]] | Which token can create the largest loss surface? | Compute current and max per-token exposure, compare insurance fund, inspect oracle type and token risk profile. | `quoted_token_exposures[]`, `credit_managers[]`, `insurance_fund_balance`, `OracleTelemetry`, per-token risk refs | Current exposure or oracle sanity missing prevents clean accept; max-exposure formula reruns when CM / quota / LT changes. |
| `DR-LP-AN-Q3` | [[Pool deposit#Q3 · Can I withdraw when I need to?]] | Can I withdraw when I need to? | Compare withdrawable now and IRM defense; trigger deeper concentration / stress-history checks when risk is elevated. | `Pool.{availableLiquidity, expectedLiquidity, totalBorrowed, utilisation, withdrawalFee}`, `IRM`, borrower concentration, withdrawal stress history | Current withdrawable liquidity missing blocks deposit preview; stress history missing marks T2 confidence gap. |
| `DR-LP-AN-Q4` | [[Pool deposit#Q4 · Who manages this pool?]] | Who manages this pool? | Establish curator identity / governance; optionally check operational record, liquidity incidents, and design discipline. | `CuratorProfile`, `badDebtIncidents[]`, `liquidityIncidents[]`, external refs | Unknown curator identity is review-required or blocking depending on mandate. |
| `DR-LP-AN-Q5` | [[Pool deposit#Q5 · What could change after I deposit?]] | What could change after I deposit? | Classify pending and recent changes; queue and pace determine whether thesis is stable enough to enter. | `EventFeedItem[]`, `GovernanceChange[]`, change-frequency summary | Pending material change inside user horizon produces review/action; feed missing prevents clean accept. |
| `DR-LP-PROP-001` | [[Pool deposit#Stage 3 · Propose (Pool) — Investment Committee]] | What should I actually fund or skip? | Convert research memos into deposit / skip / reserve decisions and size each funded pool against capital and concentration policy. | `ResearchMemo[]`, `ActionDecision`, portfolio context, policy inputs | Allocation sums to available capital; no hidden concentration default used. |
| `DR-LP-PRE-001` | [[Pool deposit#Stage 4 · Preview (Pool) — Execution Desk pre-trade]] | Will this exact transaction do what I expect right now? | Simulate deposit package and compare expected shares, APY/utilisation/TVL/share-price drift, gas, and concentration. | `TransactionPreview`, `before_after`, `warnings[]`, `raw_txs[]`, `execution_package_hash` | Preview fails if current state materially drifted, warnings are blocking, or package cannot be hashed. |
| `DR-LP-EXEC-001` | [[Pool deposit#Stage 5 · Execute (Pool) — Execution Desk trade]] | Are the signed bytes the bytes Preview validated? | Execute only the approved package; refresh monitor baseline after confirmation. | `ExecutionReceipt`, `submitted_package_hash`, `monitor_baseline_update` | Hash mismatch, expired preview, or missing signer approval rejects execute. |

## LP monitoring flow

| Requirement ID | Source | User / agent question | Decision story | Data / artifact coverage | Verification |
| --- | --- | --- | --- | --- | --- |
| `DR-LP-MON-Q1` | [[Pool monitoring#Q1 · Am I earning what I expected?]] | Am I earning what I expected? | Compare current composite APY and 30d trend against floor; inspect material incentive expiry. | `LpPosition`, `PoolOpportunity.yield.*`, APY series, `IncentiveLayer[]` | Missing APY current blocks returns verdict; incentive expiry missing is review-required. |
| `DR-LP-MON-Q2` | [[Pool monitoring#Q2 · Can I still exit at size?]] | Can I still exit at size? | Compare withdrawable liquidity to LP position size and monitor utilisation trend; classify cascade/trap symptoms when triggered. | `LpPosition.currentValueUsd`, `withdrawable_now`, utilisation series, oracle category | If withdrawable now cannot be computed, action sizing cannot proceed. |
| `DR-LP-MON-Q3` | [[Pool monitoring#Q3 · Is the pool still composed the way my thesis expects?]] | Is pool composition still aligned with thesis? | Compare top-3 exposure, new CMs, and quota changes against previous-check snapshot and thesis. | `agentLog.previousCheck`, `quoted_token_exposures[]`, `EventFeedItem[]` | First call establishes baseline; subsequent calls compute deltas. |
| `DR-LP-MON-Q4` | [[Pool monitoring#Q4 · Has anyone changed the rules?]] | Has anyone changed pool rules? | Read pending and executed changes since last check; classify material vs cosmetic. | `GovernanceChange[]`, `EventFeedItem[]`, change-frequency summary | Feed missing is review-required; material change routes to focused Analyze. |
| `DR-LP-MON-Q5` | [[Pool monitoring#Q5 · Is the bad-debt canary intact?]] | Is the bad-debt canary intact? | Detect share-price drop or insurance-fund movement; cross-reference incidents. | share-price series, insurance fund series, curator incidents | Unexplained share-price drop creates alert even if incident log is empty. |
| `DR-LP-MON-Q6` | [[Pool monitoring#Q6 · Are the oracles I depend on fresh?]] | Are dependent oracles fresh? | Drill-only check: freshness, divergence, methodology changes, accepted methodology. | `OracleTelemetry`, oracle change events, user accepted methodologies | Current oracle freshness missing blocks execution for oracle-sensitive actions. |
| `DR-LP-MON-Q7` | [[Pool monitoring#Q7 · Is the issuer-controlled collateral branch drifting?]] | Are issuer-controlled exposures changing? | Compare frozen account count / debt and liquidator-set changes against policy and insurance fund. | `RwaAssetProfile`, `RwaComplianceProfile`, issuer events | Missing issuer state prevents treating exposure as ordinary liquid collateral. |
| `DR-LP-MON-PROP-001` | [[Pool monitoring#Stage 3 · Propose (Pool) — Action Committee]] | What should I do about this LP position? | Map verdict to top-up, partial exit, full exit, or hold; size action. | `FocusedAnalyzeReport`, `ActionDecision` | No action class without a source question and rationale. |
| `DR-LP-MON-PRE-001` | [[Pool monitoring#Stage 4 · Preview (Pool) — Execution Desk pre-trade]] | Will top-up / exit do what I expect now? | Simulate action-specific package and deviation flags. | `TransactionPreview`, before/after shares / underlying / fees | Preview fails if withdraw queue / utilisation / fee drift invalidates action. |
| `DR-LP-MON-EXEC-001` | [[Pool monitoring#Stage 5 · Execute (Pool) — Execution Desk trade]] | Did the validated action execute? | Submit approved package and update monitor baseline. | `ExecutionReceipt`, new `LpPosition` baseline | Receipt hash matches preview package and confirms new baseline. |

## Credit Account entry flow

| Requirement ID | Source | User / agent question | Decision story | Data / artifact coverage | Verification |
| --- | --- | --- | --- | --- | --- |
| `DR-CA-DISC-001` | [[Credit Account opening#Stage 1 · Discover (CA)]] | Which 1–3 strategies match my asset class and floor APY? | Filter by chain / access / underlying or collateral family; rank by leveraged headline economics and carry only IDs into Stage 2. | `StrategyOpportunitySearchResult`, `OpportunityCandidate` | Candidate IDs re-fetch current facts in Stage 2; target leverage is not guessed in Stage 1. |
| `DR-CA-AN-Q1` | [[Credit Account opening#Q1 · Will the economics survive?]] | Will economics survive after leverage, borrow, quota, entry and exit friction? | Compute net APY, breakeven horizon, utilisation headroom, and IRM sensitivity. | `StrategyOpportunity.economics`, `Pool.IRM`, quota rates, route-cost estimates | Missing current borrow / quota rates blocks open / increase leverage; missing history marks sensitivity gap. |
| `DR-CA-AN-Q2` | [[Credit Account opening#Q2 · How safe is my collateral? What could force liquidation?]] | Is collateral safe enough at target leverage? | Compute HF / LT feasibility, LT-ramp horizon, forbidden overlap, oracle fit, safe-pricing exit HF, and issuer branch. | `SafetyEnvelope`, `OracleTelemetry`, `RwaAssetProfile`, `RwaComplianceProfile`, policy inputs | Missing issuer / eligibility state for controlled collateral is blocking; missing HF floor requires review before Preview / Execute. |
| `DR-CA-AN-Q3` | [[Credit Account opening#Q3 · Can I exit at size when I need to?]] | Can I exit at size and by deadline? | Check adapter-route liquidity, iterative unwind under `minDebt`, borrowable liquidity headroom, withdrawal queues. | `adapter_routes[]`, route quotes, `minDebt`, `borrowableLiquidity`, withdrawal-status feed | Current route quote missing blocks Preview; withdrawal claim state missing blocks exit claims. |
| `DR-CA-AN-Q4` | [[Credit Account opening#Q4 · Who manages this CM, and is the envelope stable?]] | Who manages this CM and can it operate safely? | Check curator / CM envelope, pause, capacity, debt limit, expiration, compliance-gated routing, track record. | `CuratorProfile`, `CreditManagerEnvelope`, compliance flags | KYC-gated CM marks bot path unavailable unless explicit compliant route exists. |
| `DR-CA-AN-Q5` | [[Credit Account opening#Q5 · What could change between now and exit?]] | What can change before exit? | Classify LT, oracle, forbidden-token, delayed-withdrawal, IRM, CM pause, liquidation-term changes. | `EventFeedItem[]`, `GovernanceChange[]`, scheduled LT ramps | Material pending change inside horizon requires review / action. |
| `DR-CA-PROP-001` | [[Credit Account opening#Stage 3 · Propose (CA) — Investment Committee + Route Selection]] | What strategy, leverage, route, and reserve should I use? | Convert memos into `open_ca` / skip decisions; select target leverage, size, route, and diversification. | `ResearchMemo[]`, `ActionDecision`, route set, policy inputs | Leverage below max and post-open HF above floor; route budget explicit. |
| `DR-CA-PRE-001` | [[Credit Account opening#Stage 4 · Preview (CA) — Execution Desk pre-trade]] | Will this exact multicall open the expected position? | Simulate multicall; gate on HF, leverage, swap impact, deviation flags, gas. | `TransactionPreview`, before/after HF/leverage/equity/debt, `raw_txs[]` | Preview cannot be ready to execute if user safety floor or tolerance missing. |
| `DR-CA-EXEC-001` | [[Credit Account opening#Stage 5 · Execute (CA) — Execution Desk trade]] | Do signed bytes match validated bytes and post-open state? | Execute approved multicall and verify post-state. | `ExecutionReceipt`, `submitted_package_hash`, `CreditAccountPosition` baseline | Hash mismatch, KYC-bot mismatch, or post-state mismatch raises failure. |

## Credit Account monitoring flow

| Requirement ID | Source | User / agent question | Decision story | Data / artifact coverage | Verification |
| --- | --- | --- | --- | --- | --- |
| `DR-CA-MON-Q1` | [[Credit Account management#Q1 · Am I safe?]] | Am I safe? | Compare HF, liquidation distance, LT ramps, forbidden overlap, leverage delta, and HF attribution. | `CreditAccountPosition.health_and_debt`, `SafetyEnvelope`, `OracleTelemetry`, previous snapshot | Emergency condition routes direct to Propose; own frozen status overrides HF acceptability. |
| `DR-CA-MON-Q2` | [[Credit Account management#Q2 · Am I making money?]] | Am I making money? | Compare net APY, PnL trend, borrow-vs-yield spread, claimable rewards, decomposition. | PnL endpoint, account-value series, reward attribution, borrow / quota / yield series | Missing PnL marks returns Glance incomplete; claimable reward source must identify owner-wallet vs CA attribution. |
| `DR-CA-MON-Q3` | [[Credit Account management#Q3 · Has anyone changed the rules?]] | Has CM rules changed? | Surface pending and recent changes; classify material with CA opening Q5 logic. | `EventFeedItem[]`, `GovernanceChange[]`, previous parameter set | Material LT / oracle / pause / forbidden change routes focused Analyze. |
| `DR-CA-MON-Q4` | [[Credit Account management#Q4 · Are operational mechanics intact?]] | Are operational mechanics intact? | Check expiration, facade pause, emergency-liquidator status, delayed withdrawals, phantom tokens, partial-exit feasibility, active bots. | `CreditManagerEnvelope`, withdrawal queue, bot registry, `minDebt` feasibility | Unknown bot with broad permission escalates manual review; matured claim creates claim prompt. |
| `DR-CA-MON-Q5` | [[Credit Account management#Q5 · Are oracles fresh? *(drill, not default)*]] | Are held-token oracles fresh? | Drill-only freshness, divergence, methodology change, and accepted-methodology fit. | `OracleTelemetry`, oracle events, user accepted methodologies | If fired and stale, execution is blocked until refreshed or manually reviewed. |
| `DR-CA-MON-Q6` | [[Credit Account management#Q6 · Is the issuer-controlled collateral branch drifting? *(conditional)*]] | Is issuer-controlled collateral drifting? | Own frozen status, eligibility / KYC, registry, redemption window, liquidator depth. | `RwaComplianceProfile`, issuer events, redemption calendar | Own frozen = blocked path regardless of HF; missing eligibility state blocks controlled-asset exit automation. |
| `DR-CA-MON-PROP-001` | [[Credit Account management#Stage 3 · Propose (CA) — Action Committee]] | What should I do, and in emergency can I do it fast? | Map verdict to action class; size amount / target; select route; emergency collapses to one stabilizing action. | `FocusedAnalyzeReport`, `ActionDecision`, policy inputs | Emergency proposal has amount, target HF, route if needed, and no broad Analyze dependency. |
| `DR-CA-MON-PRE-001` | [[Credit Account management#Stage 4 · Preview (CA) — Execution Desk pre-trade]] | Will the exact action improve or produce target state? | Simulate action; gate on HF after action, leverage / unwind target, swap impact, deviation flags, gas. | `TransactionPreview`, before/after, `is_emergency`, warnings | Emergency Preview fails if action does not improve safety or violates bot/user policy. |
| `DR-CA-MON-EXEC-001` | [[Credit Account management#Stage 5 · Execute (CA) — Execution Desk trade]] | Did the validated action execute? | Execute approved multicall; bots blocked for KYC-gated CMs and first-time emergency users. | `ExecutionReceipt`, `submitted_package_hash`, signer context | KYC-gated bot path rejected; receipt updates monitor baseline. |

## Backward trace by artifact

| Artifact / model | Requirement coverage |
| --- | --- |
| `PoolOpportunity` | `DR-LP-DISC-001`, `DR-LP-AN-Q1`–`Q5`, `DR-LP-MON-Q1`–`Q7`. |
| `StrategyOpportunity` | `DR-CA-DISC-001`, `DR-CA-AN-Q1`–`Q5`. |
| `LpPosition` | `DR-LP-MON-Q1`–`Q7`, LP proposal / preview / execute requirements. |
| `CreditAccountPosition` | `DR-CA-MON-Q1`–`Q6`, CA proposal / preview / execute requirements. |
| `CuratorProfile` | `DR-LP-AN-Q4`, `DR-LP-MON-Q5`, `DR-CA-AN-Q4`, `DR-CA-MON-Q3`. |
| `EventFeedItem` / `GovernanceChange` | LP / CA Analyze Q5 and Monitor change-rule questions. |
| `OracleTelemetry` | LP Analyze Q2, LP Monitor Q6, CA Analyze Q2, CA Monitor Q1/Q5. |
| `RwaAssetProfile` / `RwaComplianceProfile` | LP Monitor Q7, CA Analyze Q2/Q4, CA Monitor Q6, Preview / Execute blocking checks. |
| `TransactionPreview` | All `*-PRE-*` requirements. |
| `ExecutionReceipt` | All `*-EXEC-*` requirements. |
