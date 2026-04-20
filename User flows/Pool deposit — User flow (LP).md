### Stage 1 · Discover (Pool)

**User's goal at this stage:** "Give me a short list of pools that might fit my mandate, ranked enough that I can pick 1–3 for deeper analysis."

**Key questions at this stage (map to data-flow Stage 1 base + PoolOpportunity extension):**

- What is this opportunity and how do I refer to it later? (`Opportunity.id / type / title`)
- Which chain and base asset? (`Opportunity.chainId`, `Opportunity.underlyingToken`)
- Whose pool is this? (`Opportunity.curatorId`)
- ==Do I need KYC before I can use it? (`Opportunity.access.permissionless / kycRequired / kycUrl`) ?== 
- Is there anything I should notice upfront? (`Opportunity.risk.summary / warnings`)
- Which pool exactly, and what does it pay? (`PoolOpportunity.poolAddress`, `PoolOpportunity.yield: YieldBreakdown`)
- How large is it and how much liquidity is immediately available? (`supplied`, `borrowed`, `utilization`, `tvl`, `tvlUsd`, `availableLiquidity`)
- What first-pass collateral exposure am I inheriting? (`PoolOpportunity.collaterals[]`)

**Output of this stage.** A 1–3 pool shortlist carried into Analyze. 
For an agent, this is a serialised `AnalyzedCandidate[]` stub; 
for a human, it's "I'll look more carefully at these three."

### Stage 2 · Analyze — LP due diligence

**User's goal at this stage:** "Answer five questions with evidence before I commit capital."

#### Q1 · Where does the yield come from, and is it sustainable?

The user decomposes total APY into organic (supply rate from borrowers + quota revenue) and incentive (Merkl, protocol-specific campaigns). Incentive yield can disappear; organic yield is the floor.

Required evidence:

- Supply rate (organic) — current value AND 90d daily series, so the user sees whether organic alone meets their floor.
- Incentive yield, with Merkl campaigns tagged separately from protocol-specific campaigns (the former are stable and historical; the latter are approximations).
- Composite total APY, current + 90d daily, to check historical stability.

#### Q2 · What could blow up this pool? (Exposure chain)

The LP's real risk is indirect: borrowers hold risky collateral → it depegs or crashes → positions liquidate with bad debt → the pool's insurance fund absorbs it → anything beyond that is socialised to LPs.

The user traces the chain at two levels:

_Pool level_ — total debt limit, quoted token list and quota rates/limits/used, insurance fund balance, oracle methodology per token.

_Per Credit Manager (each CM is a separate risk envelope, a pool can have many)_ — CM identity, liquidation threshold per token, borrowed amount per CM, debt limit per CM, pause status. Concentration question: does one CM dominate the pool's total debt?

**RWA extension.** If any CM accepts tokenised securities, three additional loss vectors enter the picture:

- Frozen account bad debt (Securitize can freeze individual CAs; frozen accounts cannot be liquidated; debt grows silently and eventually socialises).
- Liquidator scarcity (only whitelisted addresses can liquidate RWA positions; small whitelist = slow liquidation = more bad debt).
- Off-chain asset risk (underlying issuer/fund-manager/redemption mechanism is outside on-chain control).

Required evidence for RWA includes: `hasRwaCollateral` flag per CM, frozen accounts count and total debt, whitelisted liquidator count, transfer-restriction type, underlying asset type, issuer, redemption mechanism and delay, NAV update frequency.

#### Q3 · Can I withdraw when I need to?

Withdrawal is a function of utilisation, the IRM curve, and any policy flags (e.g., "borrowing above U2 forbidden" — a safety net that reserves high-utilisation liquidity for LP exit).

Required evidence:

- Available liquidity, expected liquidity, total borrowed, utilisation rate (current).
- Utilisation and TVL 90d daily series (is it normal today, or trending toward 100 %?).
  >если представить, что есть график с исторической утилизацией - реально ли я как юзер могу что-то по нему понять и принять решение?
  >
  >в целом интересно наверно, но не супер критично
  
- IRM parameters (U1, U2, Rbase, Rslope1-3) — does the curve force borrowers to repay at high utilisation, freeing liquidity?
- Withdrawal fee (capped at 100 bps; factored into net return).

#### Q4 · Who manages this pool?

The curator can change pool and CM parameters. The user needs a trust frame: curator identity, name, URL, socials, cumulative bad-debt history across all curator-managed pools, operating breadth (pools and strategies managed). Zero bad debt history is a clean record; non-zero prompts the user to investigate which pool, when, how much.

> Zero bad debt history - насколько легко получить эту информацию юзеру? 

#### Q5 · What could change after I deposit?

> Все это непонятно и требует пояснений на примере

- Parameter change log (recent collateral additions, debt-limit increases, IRM changes). No changes in months = stable. Frequent changes = monitor more actively.
- Pending governance changes in Safe-TX queue or timelock, with description, expected execution time, and affected parameters. The user asks: does this change my risk profile? Should I wait?

#### Output
A ranked, evidence-backed shortlist with per-candidate: 
- profitability summary, 
- adjusted return estimate, 
- overall risk score, - Credora? или где еще его брать
- risk breakdown (collateral / curator / smart-contract / market / exit / — for RWA — compliance),  
- reasoning notes.

### Stage 3 · Propose (Pool)

**User's goal:** "Commit to an exact action — amount, target pool, expected outcome — or decide explicitly not to act."

The user answers four questions:

1. Is any current position already acceptable? (If rebalancing from another pool: would the switch cost exceed the expected gain?)
2. What size? (Constrained by: available liquidity, target concentration in the pool, and the user's overall allocation.)
3. Which route / token path? (Usually trivial for Pool deposits: wallet → pool underlying → pool.)
   >Вот тут непонятно: если мы изначально подбирали пулы под доступные балансы на кошельке, то какие могут быть варианты?
   
4. Should I do nothing right now? (A legitimate, explicit output of this stage.)

**Output.** A proposal package with: candidate reference, action type (`deposit` / `redeposit` / `no-op`), amount, rationale, and the exact unsigned transaction bytes.

### Stage 4 · Preview (Pool)

**User's goal:** "Will this exact transaction do what I expect _right now_, or have conditions changed since I analysed?"

Preview simulates the proposed transaction against current chain state. The user checks:

> Реально ли нам все это нужно? Сейчас ничего этого нет, симуляция в кошельке и на совести юзера

- Expected shares at the deposit amount (via `ERC-4626 previewDeposit`). A large deviation from the model means pool state changed since Analyze.
- Share price / exchange rate. A drop since Analyze can indicate a bad-debt event in between.
- Projected pool TVL after deposit and the resulting concentration percentage. If the user becomes >10 % of the pool, they may want to reduce.
- Deviation from proposal — explicit flags for: APY changed >10 %, utilisation changed >5 pp, TVL changed >20 % since the action was proposed.
- Gas estimate (USD).
- Warnings array — free-text UX strings (e.g., "pool utilisation will exceed 95 % after deposit").
- Calldata (ready to sign).

**Gate.** If Preview fails, the loop returns to **Propose**, not Analyze. The underlying thesis can still be valid even if parameters need adjustment.

### Stage 5 · Execute (Pool)

**User's goal:** "Sign and submit, with a guarantee that the bytes I signed are the bytes Preview validated."

Two modes:

- **Human-in-the-loop** — the agent encodes the preview into a verifier flow; the human signs in their wallet.
- **Bot** — a scoped bot signer executes within on-chain permissions.

No new data requirements; this stage consumes the approved transaction and the signer context.

### Stage 6 · Monitor (Pool)

**User's goal:** "Is yield holding, can I still get out, and has the pool changed since I entered?"

- **Yield & value tracking.** APY with breakdown (organic / incentive), share price current + 90d history (share price is the canonical bad-debt canary — it drops when the pool socialises a loss).
- **Pool health & exit readiness.** Current utilisation and TVL, ==insurance-fund balance change (only relevant if the buffer was part of the original thesis)==?.
- **Risk composition changes.** Explicit curator actions (collateral added, debt-limit changes, ==IRM edits==), _and_ organic ==quota-composition shift== (borrowers migrating from token A to token B without any parameter change — the LP's exposure mix changes silently), new CMs added to the pool, pending governance changes.
- **RWA monitoring** (if applicable). Frozen accounts delta, frozen debt delta, ==whitelist changes for liquidators.==

A meaningful deviation (structural or composition) pushes the loop back to Analyze for a fresh due-diligence pass.