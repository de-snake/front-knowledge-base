# Pool deposit (LP × Entry)

**Persona:** [[Personas and audience#Pool LP (passive lender)]]
**Lifecycle scope:** Entry. Stages 1–5 of the canonical loop. Stage 6 (ongoing) is owned by [[Pool monitoring]].
**Session mode:** [[Entry points|Decision]] (full traversal Discover → Execute).

## Job statement

> **When I** have capital in a base asset and a target yield floor,
> **I want to** place it into a curated, transparent lending venue where I can trace my indirect exposure, exit when I need to, and be warned before conditions change,
> **so I can** earn a sustainable organic yield without taking liquidation risk or hidden compliance risk.

## Functional / emotional / social dimensions

| Dimension | Description |
| --- | --- |
| **Functional.** | Earn a predictable net yield on a base asset, with full control over exit and visible evidence for every risk claim. |
| **Emotional.** | Trust the counterparty chain. Feel that nothing is silently changing. Know that if conditions shift, the system warns them before they take a loss. |
| **Social.** | For institutional LPs: be able to defend the allocation to an investment committee with evidence — "here is the organic yield history, here is the curator record, here is the bad-debt canary." |

## Stage 1 · Discover (Pool)

**Sub-jobs satisfied here:**
- **Define the mandate** — the user has an asset class and a floor APY (composite — what they want to earn today). _(user-config — no backend surface)_
- **Locate candidates** — a 1–3 pool shortlist surfaces in under a minute.

**Exit gate:** "I have a 1–3 shortlist of pools that match my asset class and clear my floor APY."

**User's goal:** "Give me a short list of pools that might fit my mandate, ranked enough that I can pick 1–3 for deeper analysis."

### Inputs (what the user brings to this stage)

The user typically arrives with two real constraints:

| Input | Description |
| --- | --- |
| Asset class | What the user holds and wants to lend — USD-stable, ETH, BTC, EUR-stable, etc. The system maps class → set of underlying tokens. |
| Floor APY | Minimum acceptable annualized rate (composite — what the user wants to earn today). The breakdown organic vs incentives, and whether incentive-driven yield is sustainable, is verified at [[#Q1 · Where does the yield come from, and is it sustainable?|Stage 2 Q1]] — not at filter time. |

### Compute (agent-side)

Backend handles hard filtering by asset class — the 1st-importance input passed as a request parameter. Floor APY (composite) can go either way: as a hard backend filter, or kept as a soft post-response filter — the agent's call based on expected candidate density (loose backend filter → wider pool → more ranking room).

Example:
1. Rank candidates by composite headline yield (current value).
2. Narrow as needed using post-response data:
   - **Chain** — restrict to the chain(s) where the user actually holds the underlying (e.g., user has USDC on Arbitrum only).
   - **Specific token within the asset class** — if the user has a preference (e.g., USDC over USDT), filter accordingly.
   - **Secondary signals** — min TVL, max utilisation.

### Outputs (the hand-off to Stage 2)

A 1–3 `Opportunity.id[]` shortlist (each with `title` for human-readable labelling). All other per-candidate data — yield, asset, TVL, utilisation, curator, oracle methodology — is re-fetched in Stage 2 given these identifiers; pre-storing values here would only have them diverge from current state by the time Stage 2 reads them.

**Hand-off to Stage 2.** Identifiers only. Stage 2 owns its own retrieval.

## Stage 2 · Analyze — LP due diligence

**Sub-jobs satisfied here:**
- **Validate yield sustainability** — composite headline meets the floor; any material incentive dependency is verified for durability. _(Q1)_
- **Trace exposure** — the full pool → CMs → tokens chain is legible, including the insurance fund and oracle methodology. _(Q2)_
- **Verify exit feasibility** — available liquidity, utilisation trend, withdrawal fee, and IRM behaviour above U2 are all acceptable. _(Q3)_
- **Assess curator trust** — curator identity, operating breadth, and cumulative bad-debt record are visible and within the curator bad-debt tolerance threshold. _(Q4)_

**Exit gate:** every Q below answers Yes (or "acceptable to me"). The user has chosen a winner from the shortlist, or explicitly aborts the deposit.

**User's goal:** "Answer five questions with evidence before I commit capital."

### Inputs (what enters this stage)

| Input | Description |
| --- | --- |
| Candidate identifiers | 1–3 `Opportunity.id[]` from Stage 1's hand-off. |
| Floor APY | Carried from Stage 1; gates Q1's organic-yield evaluation. |

### Compute (agent-side)

Per candidate, run Q1 → Q5 below. Each Q has its own retrieval, reasoning, and exit gate. The agent's tolerances (for issuer-controlled collateral exposure, curator trust, monitoring cadence, etc.) are derived during analysis — they emerge from each pool's properties rather than being pre-set user inputs.

Across candidates, compare verdicts side-by-side and pick a winner — or explicitly abort. Surface a reasoning trail (which Qs cleared, which had caveats, why this winner).

**Scope tiers.** Sub-questions can be either default-scope (`T1` — runs for every flow) or extended-scope (`T2` — runs only for sophisticated users, or when a `T1` finding triggers drill-down). Each Q surfaces a tier column inside its computation table. Detailed drill references live in [[Pool deposit - reference]]. Tiering is a research-depth control; the underlying loss-vector ranking lives in [[Personas and audience#Pool LP (passive lender)|Personas]] and is not duplicated into this doc.

**Source boundary.** Pool contracts provide core state such as liquidity, utilisation, rates, accepted assets, and configuration changes. Product verdicts also rely on indexers and external diligence: incentive schedules, reward top-ups, curator history, bad-debt incidents, issuer reports, and user-specific comfort thresholds.

Q1–Q5 deep-dives below.

### Q1 · Where does the yield come from, and is it sustainable?

**Exit gate:** "Headline yield meets my floor; T2 verifies incentive durability when yield persistence is material to the hold thesis."

**Why this matters.** Yield decay is one of the LP loss vectors in [[Personas and audience#Pool LP (passive lender)|Personas]] — silent erosion of the rate the LP signed up for is the loss. Decomposing where the yield comes from is the only way to assess sustainability:
- Headline APY = organic + incentives.
- Organic alone rarely clears competitive floors today; most pools rely on incentives.
- The real risk is renewal uncertainty, not the existence of incentives. Some campaigns persist for years; some are one-shot grants that expire.
- The agent reads each layer's durability profile rather than treating incentives as binary.

**Data boundary.** The pool can expose current rate and liquidity primitives; incentive durability, renewal likelihood, top-up history, and composite APY quality require campaign/indexer data. If those feeds are missing, the product copy should say “yield quality unknown,” not imply the protocol proved durability.

**What the agent computes:**

| Sub-question | Tier | What the agent does | Data retrieved |
| --- | --- | --- | --- |
| Headline yield meets floor | T1 | Compare composite headline to the floor APY carried from Stage 1. Gate fails immediately if below. | `PoolOpportunity.yield.composite.{current, 90dSeries}`. |
| Yield decomposition (organic vs incentive) | T1 | Split headline into organic supply rate + incentive layers; size the LP's reliance on each. Organic alone rarely clears competitive floors today; most pools rely on incentives. | `PoolOpportunity.yield.organic.supplyRate` (current + 90d daily series); `PoolOpportunity.yield.incentive: IncentiveLayer[]` each layer: `source` (`merkl` / `protocolSpecific` / etc.), `currentApy`, `90dSeries`, `expiry` (or `null`), `referenceUrl`. |
| Incentive durability per layer | T2 | For each layer with non-null `expiry` or `referenceUrl`: read renewal pattern, top-up history, distribution mechanism, upcoming schedule. A *material* layer is one whose disappearance would drop headline below floor. | External: per `referenceUrl`, fetch campaign page (Merkl campaign page, protocol-specific incentive page) for distribution mechanism, history, upcoming schedule. |
| **Synthesis** | — | Decompose headline. Gate passes when headline clears floor; T2 incentive-durability check fires when persistence is material to the hold thesis. Otherwise fail. | — |

### Q2 · What's my maximum exposure, per token?

**Exit gate:** "I know which tokens carry the largest potential exposure inside the pool, and I accept the dominant tail risk."

**Why this matters.** Bad debt and oracle manipulation/staleness are both LP loss vectors ([[Personas and audience#Pool LP (passive lender)|Personas]]). The LP's exposure to both flows through the pool's collateral basket:
- The LP's risk is indirect: borrowers hold collateral → it crashes or gets liquidated badly → bad debt → the pool's [[Basic info and definitions#Pool vocabulary|insurance fund]] absorbs first → anything beyond is socialised to LPs.
- Each token in the pool's collateral basket has a bounded potential exposure, capped by pool-wide debt limits, the token's own quota, and which Credit Managers actually allow it as collateral.
- The token with the dominant max exposure is where tail risk concentrates; oracle weakness or token-specific properties on that token compound it.

**What the agent computes (per token in the basket):**

| Sub-question | Tier | What the agent does | Data retrieved |
| --- | --- | --- | --- |
| Current exposure per token | T1 | Capital actually at risk to this token's collapse right now: across all CMs accepting the token, the pool capital currently lent against positions where this token sits in the collateral basket. Distinct from the max ceiling — `quotaUsed` typically << `quotaLimit`, so live risk is often a fraction of the theoretical bound and is the more decision-relevant number. | `Pool.quotedTokens[].quotaUsed`; per CM accepting the token: current debt attributable to positions where this token contributes to the LT-weighted collateral mix. |
| Maximum potential exposure per token | T1 | `min(pool max debt; token quota limit; sum over CMs where it has nonzero LT (CM debt limit))` — the upper bound on how much pool capital could ride on this single token's collateral if utilisation grows to caps. | `Pool.totalDebtLimit`; `Pool.quotedTokens[].{quotaLimit, quotaRate, quotaUsed}`; `Pool.insuranceFundBalance`; per CM accepting the token: CM identity, debt limit, pause status, expiration, collateral LT/enabled/forbidden status, and LT-ramp schedule. |
| Live oracle sanity at entry | T1 | Feed not stale (`now - lastUpdate > stalenessWindow`); `mainOracle` and `reserveOracle` agreeing within tolerance. A broken feed at entry fails the gate. | Oracle last-update timestamp, staleness window, and main/reserve prices per quoted token. |
| Oracle type → risk shape | T2 | Map oracle category to LP failure mode: market = liquidity-cascade; NAV / fundamental = liquidity-trap; hardcoded = silent trap. [[Pool deposit - reference#Drill — Oracle types and LP risk shapes\|drill ↗]] | Oracle category and methodology per quoted token (`market`, `nav`, `hardcoded`, or `hybrid`; derived from methodology if not exposed directly). |
| Per-token 3-layer risk profile | T2 | T1 surface for this Q is a single per-token verdict; T2 surfaces per-pillar evidence behind it via the [Steakhouse Layers, Pillars and Criteria](https://www.steakhouse.financial/docs/risk-management/collateral/layers-pillars-and-criteria) framework. [[Pool deposit - reference#Drill — Per-token 3-layer risk profile (Steakhouse)\|drill ↗]] | Issuer-controlled collateral presence flag. External (no pre-computed token risk profile): curator-published ratings; Credora / [Steakhouse](https://www.steakhouse.financial/docs/markets/readme/morpho-v1) reports; issuer / reserve attestations. |
| **Synthesis** | — | Per-token verdict for each quoted token; the dominant-exposure token's worst-case failure mode (cascade vs trap) is the gate. Insurance fund net of **current** exposure sets the LP's loss surface today; **max** exposure sets the ceiling under fully-utilised conditions. | — |

==note: the per-token max-exposure aggregate (the `min(...)` above) is a derived field. Decide whether it computes MCP-side and returns per-token, or backend returns raw fields and the agent computes. Either is acceptable; product surface is the same==

==note: per-token *current* exposure — "pool capital currently lent against positions where this token contributes to collateral" — is not exposed as a single field today. Need either (a) per-CM aggregate `currentDebtAttributableTo[token]` returned by backend, or (b) sum-across-CAs derivation. `Pool.quotedTokens[].quotaUsed` is the closest existing proxy but is quota-consumption, not collateral-attributable debt — verify the two are equivalent or close enough.==

### Q3 · Can I withdraw when I need to?

**Exit gate:** "Current withdrawable liquidity and IRM defence are acceptable at default scope; T2 checks concentration, collateral-liquidity, and recent stress history when triggered."

**Why this matters.** Locked liquidity / blocked withdrawals is an LP loss vector ([[Personas and audience#Pool LP (passive lender)|Personas]]) — a pool that's solvent on paper but unable to honour withdrawals breaks the LP's "yield without losing access" contract. Several named LP-exit failure modes from real incidents map onto the dimensions below.

**Data boundary.** Current utilisation and available liquidity are protocol/state reads. Stress history, withdrawal pressure, incident context, and “can I get out on time?” confidence require historical market data and indexer context.

**What the agent computes — 5 industry-canonical dimensions, three lenses:**

| Dimension | Lens | Tier | What the agent does | Data retrieved |
| --- | --- | --- | --- | --- |
| Withdrawable now | Pool state today | T1 | `(1 − U) × TVL`. Foundation of every framework (Aave, Gauntlet, Chaos Labs, Steakhouse). | `Pool.{availableLiquidity, expectedLiquidity, totalBorrowed, utilisation}` (current). |
| IRM defence at the kink | Pool state today | T1 | Slope2 steepness above `U_optimal` (typically 80–90% in Aave-style two-slope IRM) plus any policy flags (e.g., "borrowing above U2 forbidden"). Sharp slope2 = pool punishes scarcity quickly, defending LP liquidity. | `Pool.IRM.{U1, U2, Rbase, Rslope1, Rslope2, Rslope3}` + policy flags if exposed; `Pool.withdrawalFee` (≤100 bps); withdraw mechanism (atomicity, queue / notice period, guardian / timelock gates, secondary-market listings for pool LP tokens). |
| Top-5 borrower share of total debt | Concentration | T2 | Concentration of exit-*blockers* — a single whale unable or unwilling to repay can hold the pool at high U indefinitely. | Top-N borrower addresses with debt share (subgraph or backend aggregate). |
| Collateral-induced liquidity risk | Cascade & history | T2 | Symptom: utilisation can spike to lockout when (a) un-liquidatable positions accumulate, pinning `Borrowed` high while collateral degrades, or (b) during a cascade, LP withdrawals drain `Cash` faster than liquidators close positions and repay debt — the cash side of the pool empties faster than the debt side. Both paths turn paper-solvency into stuck capital. [[Pool deposit - reference#Drill — Collateral-induced liquidity risk by oracle type\|drill ↗]] | DEX subgraphs / aggregators (Uniswap, Curve, 1inch) — for each dominant collateral, current `liquidationDepth` and slippage-at-trade-size. Cross-ref Q2 oracle category for cascade-vs-trap classification. |
| Recent 30d max withdrawal-to-TVL spike | Cascade & history | T2 | Revealed-preference stress test — what's actually happened to this pool, and how long did recovery take? Substitutes for synthetic stress simulation, which no authority publishes a numeric threshold for. | Withdraw / Deposit event logs over 30d; `Pool.tvl` daily series (90d for context); `Pool.utilisation` daily series (90d for context). |
| **Synthesis** | — | — | T1 gates on Pool state today (withdrawable + IRM defence). T2 fires when triggered: concentration of borrowers, cascade-vs-trap by oracle type on dominant collateral, and recent 30d withdrawal stress add structural / historical context. LP / agent sets the bar based on position size and hold horizon. | — |

### Q4 · Who manages this pool?

**Exit gate:** "Curator identity / governance clears default trust; T2 checks operating record, liquidity incidents, and design discipline where needed." _(Some users tolerate small or scoped bad debt; others demand zero. The gate is comfort, not zero.)_

**Why this matters.** Silent exposure changes by the curator is an LP loss vector ([[Personas and audience#Pool LP (passive lender)|Personas]]). The curator is the persistent counterparty to the deposit. They (1) chose the pool's parameters at design time (oracle types per token, LLTVs, quota sizes, accepted CMs, IRM curve) and (2) can change those parameters on an ongoing basis within protocol bounds. The LP's thesis can survive changing market conditions but not a curator who routinely takes on bad debt, picks wrong oracles, sizes quotas above realistic liquidity, or pivots strategy without warning.

**Data boundary.** The protocol shows current parameters and change authority. Trust, process maturity, bad-debt history, and incident interpretation come from external curator diligence and should be presented as such.

Q4 owns three concerns Q2 explicitly defers here:
- **Oracle methodology fit per dominant token** — Q2 covers what kind of risk each oracle TYPE creates; Q4 covers whether the type CHOICE for the token was correct.
- **3-layer rating rigor** — does the curator perform the Steakhouse Asset / Platform / Market assessment for each token they accept, or is the published grade superficial?
- **Liquidity-management discipline** — collateral-whitelist quality, quota-sizing vs realistic depth, notice-period compensation in LLTV / quotas, atomic-swap requirements, historical liquidity-incident track record (distinct from bad-debt incidents).

**What the agent computes:**

| Sub-section | Aggregation | Tier | What the agent does | Data retrieved |
| --- | --- | --- | --- | --- |
| Identity & governance (Steakhouse Issuer pillar) | best-of | T1 | Identity & legitimacy; decentralisation of authority; technical surface (what curator can change unilaterally vs gated). [[Pool deposit - reference#Drill — Curator identity & governance\|drill ↗]] | `Curator.identity` (`name`, `url`, `socials[]`, `doxxedTeam`, `regulatoryStatus`); `Curator.governanceMechanism` (`single-eoa` / `multisig-n-of-m` / `dao-governance`; signer addresses + concentration; guardian / timelock contracts). External: curator publications, social feeds, governance forum activity. |
| Operational track record (Steakhouse Operational pillar) | worst-of | T2 | Lindy; process maturity; economic transparency (`cumulativeBadDebtUsd`, `totalAumUsd`, `badDebtIncidents[]`). [[Pool deposit - reference#Drill — Curator operational track record\|drill ↗]] | `Curator.{firstOperationDate, cumulativeBadDebtUsd, totalAumUsd}`; `Curator.badDebtIncidents[]` each: `poolId`, `tokenAddress`, `dateRange`, `severityUsd`, `resolutionNotes`; `Curator.activityLog[]` — parameter changes, CMs added, governance interventions, with timestamps. External: incident post-mortems. |
| Liquidity-incident history | sibling to bad-debt | T2 | `Curator.liquidityIncidents[]` — paper-solvent-but-unusable events. Distinct from `badDebtIncidents[]`. [[Pool deposit - reference#Drill — Curator liquidity-incident history\|drill ↗]] | `Curator.liquidityIncidents[]` each: `poolId`, `dateRange`, `severityUsd`, `freezeDuration`, `resolutionNotes`. |
| Design discipline (deferred from Q2) | n/a | T2 | Oracle methodology fit per dominant token; 3-layer rating rigor; liquidity-management discipline. [[Pool deposit - reference#Drill — Curator design discipline\|drill ↗]] | `Pool.parameters` — to compare curator's oracle-type / LLTV / quota choices against Q2 per-token risk profiles. External: independent rating-agency coverage (Credora, Steakhouse — cross-ref Q2 external sources); token-specific docs (Lido for stETH, Securitize for RWAs, etc.) for oracle methodology fit. |
| **Synthesis** | — | — | T1 gates on Identity & governance (best-of pillar — any one of clean identity, decentralised authority, or hardened technical surface gives the LP a trustable counterparty). T2 fires when needed: operational record (worst-of: Lindy + process + transparency), liquidity-incident history (paper-solvent-but-unusable counts as curator failure even without a credit loss), and design discipline (oracle / quota / LLTV calibration; the Aave-CRV lesson — curator competence shows up in collateral-whitelist quality and quota-sizing, not just identity). Non-zero bad debt can still pass if scoped and the user is comfortable. | — |

==note: aggregate metrics like `cumulativeBadDebtUsd`, `totalAumUsd`, and `Curator.liquidityIncidents[]` are not exposed today — flag to Data requirements as "Curator profile endpoint" expansion. `Curator.liquidityIncidents[]` is a NEW addition, sibling to `badDebtIncidents[]`. `doxxedTeam` flag and `resolutionNotes` are editorial / subjective; need a curation source or external attestation.==

> Zero bad debt history - насколько легко получить эту информацию юзеру?

### Q5 · What could change after I deposit?

**Exit gate:** "I know what's queued in governance, the historical pace of material changes is acceptable, and any pending change either fits my thesis or I can wait for it to execute before depositing."

**Why this matters.** Same loss vector as Q4 — silent exposure changes by the curator ([[Personas and audience#Pool LP (passive lender)|Personas]]) — read here from the *change-feed* angle rather than the *curator-trust* angle. The pool's parameters can change between deposit and exit. Some changes are stable cadence and cosmetic (debt-limit increases as TVL grows, small `Rbase` tweaks). Others materially shift the LP's risk surface and would fail Q1–Q4 if those gates were re-run after the change. The agent reads both **history** (frequency and material-vs-cosmetic mix) and **queue** (what's pending), and decides whether to accept, wait, or skip.

**Changes the agent classifies** — material changes gate the deposit; cosmetic / stable changes are noted but don't gate.

| Change type | Classification | Re-evaluates / effect | Scope | Event source |
| --- | --- | --- | --- | --- |
| New CM added / expanded CM debt limit | material | [[#Q2 · What's my maximum exposure, per token?\|Q2]] — larger max exposure per the `min(...)` formula; new CM may add unfamiliar collateral. | T1 | `cmAdded` / `debtLimitChanged` |
| Quota rate raised on a token approaching `quotaLimit` | material | [[#Q3 · Can I withdraw when I need to?\|Q3]] — token can become more dominant; cascade lens. | T1 | `quotaRateChanged` |
| Forbidden-tokens flag flipped | material | Q2 collateral surface — previously-banned collateral now accepted. | T1 | `forbiddenTokenFlipped` |
| LT-ramp schedule update | material | Q2 effective LT — changes over the ramp window; may breach LP comfort by ramp end. | T1 | LT-ramp schedule update |
| IRM parameters adjusted (esp. `Rslope2` or `U_optimal`) | material | Q3 dim 2 — LP-exit defence at the kink changes. | T1 | `irmChanged` |
| CM paused with outstanding debt | material | Q3 liquidity-trap — any LP exit needing repayment from that CM is throttled. | T1 | `cmPaused` |
| Oracle changed for a dominant token | material | Q2 risk shape — new oracle type can flip cascade-vs-trap profile. | T2 | `oracleChanged` |
| Debt-limit raised proportional to TVL growth | info-only | not gated | info | `debtLimitChanged` + TVL growth context |
| Small `Rbase` adjustments without slope changes | info-only | not gated | info | `irmChanged` where changed parameter = `Rbase` |
| Curator metadata updates (URL, socials) | info-only | not gated | info | curator-profile update / non-pool event |
| **Synthesis** | — | Two lenses. **Pace** — frequency of material changes (≤1/quarter = quiet; multiple/month = busy). **Queue** — pending changes evaluated against thesis. Multiple queued changes is itself a signal of curator volatility (cross-ref [[#Q4 · Who manages this pool?\|Q4]] activity log). The agent forms a monitoring-cadence expectation from the data, not from a user-supplied cadence. | — | — |

> Все это непонятно и требует пояснений на примере

**Retrieval contracts.** Executed pool-change feed (filtered by pool, fields per the table's `Event source` column) drives the Pace lens; pending governance-change queue drives the Queue lens (description, affected parameters, expected execution time, timelock duration, proposer). New aggregate to add: pool change-frequency summary — counts by change type over 30d / 90d / 365d windows.

==note: executed-change and pending-governance feeds are already on the Data requirements punch list; this expands the per-field spec. The agent's "material vs cosmetic" classification is the agent's call, not a backend field — derive from change type + magnitude.==

### Outputs (the hand-off to Stage 3)

Per-candidate `ResearchMemo` — the analyst's compression of raw evidence into a structured assessment that Stage 3's Investment Committee uses for allocation. One memo per analyzed candidate; the IC sees the full set, not just a winner.

```
ResearchMemo {
  candidate_id, candidate_name,
  recommendation: "strong" | "acceptable" | "risky" | "reject",
  one_liner,
  profit: { headline_apy, apy_organic, apy_incentive, apy_trend, yield_sustainability },
  risk: { summary, exposure_concentration, oracle_health, exit_feasibility, curator_trust, pending_changes },
  constraints: { max_position_usd, min_position_usd, availability },
}
```

==note: overall risk score / cross-protocol comparable rating — Credora? или где еще его брать==

Each evidence field in the memo is a **computed summary backed by raw numbers, not a label** (per the [staged-agent-architecture memo standard](#)). E.g., `oracle_health` should read "Chainlink, 1h heartbeat, 0 stale episodes in 90d" — not just "healthy". The IC reads facts, applies independent judgment.

**Hand-off to Stage 3.** `ResearchMemo[]` — array of memos, one per analyzed candidate. Stage 3's IC selects allocation across them.

## Stage 3 · Propose (Pool) — Investment Committee

**Sub-job (part 1 of Commit capital):** allocate across the analyzed candidates — pick which to fund, how much, and why.

**Exit gate:** "I have an allocation decision — per candidate, either an amount I'll deploy with a rationale, or an explicit skip. Total deployed + reserve = my available capital."

**User's goal:** "Decide what to actually commit, taking the analyst's research and my portfolio context into account."

### Inputs (what enters this stage)

| Input | Description |
| --- | --- |
| Per-candidate research memos | `ResearchMemo[]` from Stage 2. |
| Available capital | Total amount the user wants to deploy this session (set here, not at Stage 1). |

### Compute (agent-side — IC analogy)

The agent acts as an Investment Committee: reads the memos, retrieves existing portfolio state, applies portfolio-level constraints, and decides allocation across the candidates.

| Decision class | Tier | What the agent does | Data retrieved |
| --- | --- | --- | --- |
| Per-candidate fund/skip classification | T1 | Classify each `ResearchMemo` → `deposit` or `skip` based on its risk verdict + capital availability. | `ResearchMemo[]` from Stage 2; user-stated available capital. |
| Allocation sizing per funded candidate | T1 | Size each funded position; attach a rationale one-liner (e.g., "highest organic yield, acceptable risk"). | Per-candidate `max_position_usd` / `min_position_usd` / `availability` from the memo; available capital. |
| Cross-candidate diversification | T2 | Apply concentration / correlation budgets across the funded set; may split a single thesis across several candidates. | Agent-derived concentration & correlation thresholds (functions of LP risk profile + portfolio state). |
| Existing-portfolio deduplication | T2 | Retrieve current LP positions across pools and strategies; reduce or skip candidates whose exposure overlaps with existing positions. | Agent-side position retrieval. |
| **Synthesis** | — | Output `AllocationDecision[]` per candidate. Palette maps: fund / split → `action: "deposit"` (on one or more candidates); skip → `action: "skip"`; hold-reserve → represented by `reserve_usd`, not a candidate action; no-op → all candidates skipped, `reserve_usd = available capital`. Invariant: `total_deployed_usd + reserve_usd = available capital`. See [[Pool deposit - reference#Drill — IC decision palette\|drill ↗]]. | — |

> Вот тут непонятно: если мы изначально подбирали пулы под доступные балансы на кошельке, то какие могут быть варианты?

(Route — wallet → pool underlying → pool — is trivial for Pool deposits and is handled at Stage 4 / Execution Desk; Stage 3 doesn't reason about it. **Forward note: in Credit Account flows, route is non-trivial (zaps, multi-hop, leverage assembly) and may move into Stage 3 there.**)

### Outputs (the hand-off to Stage 4)

```
AllocationDecision {
  decisions: Array<{ candidate_id, action, amount_usd, rationale }>,
  total_deployed_usd,  // sum of decisions[].amount_usd where action='deposit'
  reserve_usd,         // available capital − total_deployed_usd
  committee_notes,     // free-text rationale for the overall allocation
}
```

**Hand-off to Stage 4.** Stage 4 takes each `decision` with `action: "deposit"` and validates against current chain state — produces simulation + calldata per candidate.

## Stage 4 · Preview (Pool) — Execution Desk pre-trade

**Sub-job (part 2 of Commit capital):** validate the IC's proposal against current chain state — simulate the exact transaction, surface deviations from proposal-time assumptions, gate on them.

**Exit gate:** "Simulation matches my proposal: expected shares within tolerance, no deviation flags fire (APY / utilisation / TVL haven't materially shifted since Analyze), no Preview warnings, gas acceptable, and the resulting pool concentration is within my comfort." _(The concentration check lives here, not as a universal criterion — it's a Preview-time fact about this specific deposit size.)_

**User's goal:** "Will this exact transaction do what I expect _right now_, or have conditions changed since I analysed?"

### Inputs (what enters this stage)

| Input | Description |
| --- | --- |
| `AllocationDecision` | From Stage 3 — per-candidate `decisions[]`, `total_deployed_usd`, `reserve_usd`. |
| Current chain state | Re-fetched per `decision.candidate_id` to compare against memo-time assumptions. |

### Compute (agent-side — Execution Desk pre-trade)

For each `decision` with `action: "deposit"`:

> Реально ли нам все это нужно? Сейчас ничего этого нет, симуляция в кошельке и на совести юзера

- **Expected shares** at the deposit amount via `ERC-4626 previewDeposit`. A large deviation from the model means pool state changed since Analyze.
- **Share price / exchange rate** vs Analyze-time snapshot. A drop indicates a possible bad-debt event between memo and execution.
- **Projected pool TVL after deposit** + the resulting concentration percentage. If the projected concentration exceeds the user / mandate concentration policy, the user may reduce size or route to review.
- **Deviation flags** — APY, utilisation, TVL, and share-price changes since the action was proposed, evaluated against user / mandate tolerance or product guardrails rather than hidden defaults.
- **Gas estimate** (USD).
- **Warnings array** — free-text UX strings (e.g., "pool utilisation will exceed the configured utilisation ceiling after deposit").

### Outputs (the hand-off to Stage 5)

```
TransactionPreviewReport {
  candidate_id,
  expected_shares,
  share_price_at_preview,
  projected_tvl_post_deposit,
  resulting_concentration_pct,
  deviation_flags: { apy_change_pct, utilisation_change_pp, tvl_change_pct },
  gas_estimate_usd,
  warnings: string[],
  calldata,           // ready to sign
}
```

**Hand-off to Stage 5.** A `TransactionPreviewReport[]` (one per `decision` with `action: "deposit"`) — each carrying the validated calldata.

**On failure.** If Preview fails for a given candidate, the loop returns to **Propose** for that candidate, not Analyze. The underlying thesis can still be valid even if execution-time parameters need adjustment.

## Stage 5 · Execute (Pool) — Execution Desk trade

**Sub-job (part 3 of Commit capital):** sign and submit each previewed transaction, with an integrity guarantee that signed bytes match validated bytes.

**Exit gate:** "The bytes I signed match what Preview validated; the transaction confirms on-chain."

**User's goal:** "Sign and submit, with a guarantee that the bytes I signed are the bytes Preview validated."

### Inputs (what enters this stage)

| Input | Description |
| --- | --- |
| `TransactionPreviewReport[]` | From Stage 4 — each with validated calldata. |
| Signer context | HITL wallet OR scoped bot signer with on-chain permissions. |

### Compute (agent-side — Execution Desk trade)

Two modes:

| Mode | Description |
| --- | --- |
| **Human-in-the-loop** | Agent encodes the preview into a verifier flow; the human signs in their wallet. The verifier UI shows the same calldata that Preview produced — any divergence (e.g., wallet substituting calldata) breaks the integrity gate. |
| **Bot** | Scoped bot signer executes within on-chain permissions. Bot must verify calldata hash matches Preview output before submitting. |

No new data requirements; this stage consumes the approved transaction and the signer context.

### Outputs (the hand-off to Stage 6)

```
TransactionConfirmation {
  candidate_id,
  txHash,
  blockNumber,
  actualShares,
  actualSharePrice,
  gasPaidUsd,
}
```

**Hand-off to Stage 6.** A `TransactionConfirmation[]` per executed deposit. Stage 6 ([[Pool monitoring]]) picks up monitoring from these confirmations.

## Stage 6 · Monitor (handoff)

Ongoing monitoring is a separate, recurring job. See [[Pool monitoring]].
