# Data architecture

This document turns the read/write requirements into an implementation architecture. It stays technology-neutral where possible and names the storage / ingestion shape that each product decision needs.

## Architecture principles

1. **Product questions define the read model.** Do not expose backend subsystem seams directly to the agent when a product decision needs a composed view.
2. **Protocol state is not enough.** Verdicts require protocol state, indexer aggregates, issuer/compliance feeds, product policy, and user / agent policy to remain separate.
3. **Normalize authoritative write data.** Denormalize into read projections only for named access patterns.
4. **Treat time as first-class.** Monitoring and Preview require snapshots, histories, scheduled changes, and event logs; current-only state is insufficient.
5. **Read and write are separate.** Queries answer “what should I think?” Commands answer “what exact bytes may be signed?”
6. **Unknown is a state, not a default.** Missing issuer, oracle, Preview-integrity, or safety-policy data must block or route to review rather than becoming green.

## Logical bounded contexts

| Context | Business meaning | Source of truth | Read projections |
| --- | --- | --- | --- |
| Pool market state | Current pool liquidity, utilisation, rates, accepted Credit Managers, share price. | Protocol contracts + indexer. | `PoolOpportunity`, `LpPosition`, LP Preview before/after. |
| Credit Manager / Credit Account state | Credit Manager envelope and per-account debt, balances, HF, leverage, operational state. | Protocol contracts + indexer. | `StrategyOpportunity`, `CreditAccountPosition`, CA Preview before/after. |
| Risk telemetry | Oracle freshness, price history, exposure, borrow / quota / APY series, bad-debt canaries. | Indexer + derived computations + selected external feeds. | Monitoring snapshots, research memos, risk drill views. |
| Governance / change feed | Pending and executed parameter changes by pool, Credit Manager, token, oracle, issuer program. | Safe / timelock / protocol event sources + indexer. | `EventFeedItem`, `GovernanceChange`, change-frequency summaries. |
| Curator / operator profile | Curator identity, governance mechanism, track record, incidents, external references. | Curated profile + protocol authority reads + indexer aggregates. | `CuratorProfile`. |
| Issuer / compliance state | Eligibility, freeze, transfer / redemption restrictions, eligible liquidator depth. | Issuer/compliance endpoints + platform integrations + indexer where possible. | `RwaAssetProfile`, `RwaComplianceProfile`. |
| User / agent policy | User floors, concentration caps, accepted oracle methodologies, bot policies, continuity log. | User / agent-side policy store. | Read-model inputs; never silently treated as Gearbox protocol state. |
| Execution | Preview, approval, transaction packages, receipts. | Command service + simulation + wallet / bot signer + chain receipts. | `TransactionPreview`, `ExecutionReceipt`. |

## Source-of-truth map

| Fact family | Primary source of truth | Secondary / derived sources | Notes |
| --- | --- | --- | --- |
| Pool liquidity, borrowed, utilisation, share price | Protocol + indexer | Computed read model | Current values are execution-sensitive; histories come from indexer. |
| IRM parameters | Protocol | Change-feed event log | Needed by LP exit defense and CA borrow-rate sensitivity. |
| Credit Manager pause, facade pause, debt limit, expiration, min/max debt | Protocol | Event-feed projection | Blocks opens, leverage increases, and exits. |
| Token LT, LT ramps, forbidden status | Protocol | Scheduled-change projection | Needed for HF feasibility and monitoring drift. |
| Oracle price, reserve price, freshness window, methodology | Protocol / oracle payloads | Oracle-methodology registry + event feed | Methodology interpretation remains product / user policy. |
| APY / rewards / incentives | Indexer + campaign source | Merkl / protocol reward APIs, human reference URLs | Distinguish confirmed organic yield from incentive assumptions. |
| Curator identity, governance, incidents | Curated profile + protocol authority reads | DefiLlama / GitHub / X / governance forums / postmortems | Mark authorship and confidence. |
| RWA issuer / eligibility / freeze / redemption | Issuer or compliance integration | Platform indexer if available | Missing own eligibility/freeze state is blocking for controlled-asset actions. |
| User thresholds and bot scopes | User / agent policy store | Current session input | No hidden defaults. |
| Preview package and receipt | Command service + chain | Simulation result and wallet/bot signer logs | Package hash must bind Preview to Execute. |

## Storage / projection shape

| Store / projection | Role | Candidate physical shape | Required by |
| --- | --- | --- | --- |
| Protocol snapshot cache | Current pool / CM / CA state, refreshed frequently. | Relational tables or document cache keyed by chain + address; TTL by fact family. | All read models and Preview. |
| Event log | Parameter changes, governance queue, oracle changes, issuer/compliance events, execution receipts. | Append-only relational/event table with typed payload JSON and indexed scope. | Monitor drift, audit, Preview / Execute trace. |
| Time-series store | APY, utilisation, TVL, borrow / quota rates, oracle prices, share price, account value. | Time-series table or analytics store; daily retention minimum from [[data-read-spec]]. | Analyze histories and monitoring trends. |
| Read projections | `PoolOpportunity`, `StrategyOpportunity`, `LpMonitoringSnapshot`, `CreditAccountMonitoringSnapshot`. | Materialized views / cached API responses, rebuilt from snapshots + histories + policies. | Agent and UI query surfaces. |
| Curated profile store | Curator profile, external refs, incident notes, strategy descriptions. | Relational/document store with author/source metadata. | Curator trust and strategy description. |
| Issuer/compliance cache | Eligibility, freeze, redemption, liquidator depth. | Isolated cache with strict freshness + source refs. | RWA conditional branches and execution blockers. |
| User / agent policy store | Runtime policies and continuity logs. | User-owned session/profile store, not Gearbox protocol data. | Thresholds, deltas, bot authorization. |
| Execution ledger | Preview, approval, submitted package, receipt, post-state baseline. | Append-only command table with hashes and tx refs. | Preview / Execute integrity. |

## Ingestion and update cadence

| Feed | Cadence | Backfill | Freshness class | Failure behavior |
| --- | --- | --- | --- | --- |
| Protocol current state | Near-real-time / per request for Preview | Not applicable | execution-sensitive | If unavailable, block Preview / Execute. |
| APY / utilisation / TVL / rate series | Daily minimum; current on request | 90d where required | decision-sensitive | If current missing, block decision; if history missing, mark T2 gap. |
| Oracle telemetry | Current on request; history daily | 90d oracle history where useful | execution-sensitive for Preview | Stale/missing freshness blocks oracle-sensitive execution. |
| Governance / parameter events | Event-driven; poll fallback | 30d / 90d / 365d change summary | monitoring-sensitive | Missing feed prevents clean “nothing changed” verdict. |
| Curator incidents | Manual / periodic curated updates + indexer signals | Full incident history when possible | review-sensitive | Unknown record is not zero incidents; show unknown. |
| Issuer / compliance state | Current on request for affected positions; periodic monitor refresh | Event history where available | execution-sensitive for controlled assets | Unknown own state blocks controlled-asset automation. |
| Preview simulation | Per action request | Not applicable | execution-sensitive | Failed simulation returns structured blocker / retry route. |
| Execution receipt | Per submitted tx | Chain history | audit-sensitive | Do not infer success without confirmation or explicit pending state. |

## API contract shape

Prefer task-oriented read endpoints over raw table exposure.

| Endpoint family | Returns | Primary consumers |
| --- | --- | --- |
| `GET /opportunities/pools` | `PoolOpportunitySearchResult[]` | LP Discover. |
| `GET /opportunities/strategies` | `StrategyOpportunitySearchResult[]` | Credit Account Discover. |
| `GET /pools/{pool_id}/research` | `PoolResearchMemo` inputs or composed memo data. | LP Analyze. |
| `GET /strategies/{strategy_id}/research` | `CreditAccountResearchMemo` inputs or composed memo data. | CA Analyze. |
| `GET /positions/lp/{position_id}/monitoring` | `LpMonitoringSnapshot`. | LP Monitor. |
| `GET /positions/credit-account/{account}/monitoring` | `CreditAccountMonitoringSnapshot`. | CA Monitor / Emergency. |
| `GET /curators/{curator_id}` | `CuratorProfile`. | LP / CA curator checks. |
| `GET /events` | scoped `EventFeedItem[]` / `GovernanceChange[]`. | Analyze Q5 and Monitor change questions. |
| `GET /oracle-telemetry` | token-scoped oracle freshness / methodology / history. | Oracle drills and Preview freshness. |
| `GET /issuer-state` | token / account / issuer-scoped RWA state. | RWA branches and controlled-asset execution. |
| `POST /actions/preview` | `TransactionPreview`. | Stage 4. |
| `POST /actions/execute` | `ExecutionReceipt`. | Stage 5. |

Versioning should be additive by default. Adding optional fields is safe; removing / renaming fields or changing types requires an explicit version and migration window.

## Data quality controls

| Dimension | Control |
| --- | --- |
| Accuracy | Source refs for protocol reads, event feeds, issuer state, and curated external facts; contract tests for Preview package hashes. |
| Completeness | Per-read-model coverage checks against [[traceability-matrix]]; blocking-gap arrays for missing safety-critical facts. |
| Consistency | Shared IDs for pools, Credit Managers, tokens, strategies, positions; event-feed scope normalization. |
| Timeliness | `as_of` + freshness SLA on decision-driving fields; execution-time rechecks before submitting. |
| Validity | Typed enums for source class, unknown state, action class, event type, and Preview status. |
| Uniqueness | Stable IDs for events, previews, receipts, incidents, reward claims; dedupe by source ref where available. |

## Failure modes and fallback behavior

| Failure mode | Affected decision | Required behavior |
| --- | --- | --- |
| Protocol snapshot unavailable | Preview / Execute; current safety checks | Block action; do not rely on cached data past freshness SLA. |
| Indexer history unavailable | T2 histories / trend checks | Continue T1 only when current values suffice; mark T2 gap. |
| Change feed unavailable | “Nothing changed” monitor verdicts | Mark review-required; do not assert quiet state. |
| Curator profile missing | Curator trust | Show unknown; block only when mandate requires curator approval. |
| Issuer/compliance endpoint unavailable | Controlled-asset actions | Block automation and route to human / issuer resolution. |
| User policy missing | Threshold-based verdicts | Show raw facts; ask / review before recommendation or Preview readiness. |
| Preview hash unavailable | Execute | Block Execute. |
| Receipt unavailable after submission | Monitor baseline | Mark pending/unknown; do not claim confirmed success. |

## Minimal ERD-level relationships

```text
CuratorProfile 1 ── * PoolOpportunity
PoolOpportunity 1 ── * CreditManagerEnvelope
PoolOpportunity 1 ── * TokenExposure
CreditManagerEnvelope 1 ── * StrategyOpportunity
CreditManagerEnvelope 1 ── * CreditAccountPosition
CreditAccountPosition 1 ── * HeldTokenBalance
Token / CreditManager / Pool / IssuerProgram 1 ── * EventFeedItem
Token 1 ── * OracleTelemetry snapshots/history
IssuerProgram 1 ── * RwaAssetProfile / RwaComplianceProfile
Position / Candidate 1 ── * ActionDecision
ActionDecision 1 ── * TransactionPreview
TransactionPreview 1 ── 0..1 ExecutionReceipt
UserPolicy 1 ── * ActionDecision / MonitoringSnapshot inputs
```

This ERD is conceptual. Physical schema should be derived after deciding which projections are materialized and which are computed on request.
