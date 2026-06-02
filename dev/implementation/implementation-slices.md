# Implementation slices

This build plan turns the data specs into shippable backend/data slices. Order is by decision impact, not by table count.

## Prioritization rule

1. Preview / Execute integrity and blockers.
2. User-fund safety and issuer/compliance unknowns.
3. Monitoring drift and emergency routing.
4. Entry due-diligence ranking quality.
5. Explanation depth and institutional reporting.

## Slice 0 — Preview integrity gate

| Item | Detail |
| --- | --- |
| User/product decision unblocked | “Can this exact package be signed / submitted safely?” |
| Requirements covered | All `*-PRE-*` and `*-EXEC-*` requirements in [[traceability-matrix]]. |
| Entities / events touched | `ActionDecision`, `TransactionPreview`, `PreviewRoute`, `RawTx`, `ExecutionReceipt`. |
| Sources / ingestion needed | Current protocol snapshots, simulation RPC, route quote source, signer context, issuer / oracle rechecks. |
| API endpoints | `POST /actions/preview`, `POST /actions/execute`, `GET /previews/{preview_id}`. |
| Verification | Hash mismatch rejected; expired Preview rejected; stale oracle / issuer state blocks; receipt updates monitor baseline. |
| Open questions | Exact hash canonicalization for multicall / raw tx arrays; whether package hashes live in backend, verifier UI, or both. |

## Slice 1 — Source provenance and unknown-state envelope

| Item | Detail |
| --- | --- |
| User/product decision unblocked | Prevents missing data from being shown as acceptable. |
| Requirements covered | All decision-driving read requirements. |
| Entities / events touched | Shared field envelope in [[data-dictionary]], `blocking_gaps[]`, `warnings[]`. |
| Sources / ingestion needed | Source refs and `as_of` timestamps for protocol, indexer, issuer, curated, and policy inputs. |
| API endpoints | Applies to every read endpoint; no standalone endpoint required. |
| Verification | Each verdict-driving field has `source_class`, `as_of`, unknown state, and `used_by`; missing safety-critical fields create blockers. |
| Open questions | Exact freshness SLA values by field family; product-policy ownership. |

## Slice 2 — Unified event / governance change feed

| Item | Detail |
| --- | --- |
| User/product decision unblocked | “What changed?” for LP and Credit Account Analyze / Monitor. |
| Requirements covered | `DR-LP-AN-Q5`, `DR-LP-MON-Q3`, `DR-LP-MON-Q4`, `DR-CA-AN-Q5`, `DR-CA-MON-Q3`. |
| Entities / events touched | `EventFeedItem`, `GovernanceChange`, change-frequency summaries. |
| Sources / ingestion needed | Protocol events, Safe / timelock queue, oracle changes, CM pause/facade events, LT/IRM/quota/forbidden-token updates. |
| API endpoints | `GET /events?scope=...`, `GET /events/summary?window=30d,90d,365d`. |
| Verification | Pool and CM monitors can answer pending + recent changes since `agentLog.previousCheck.asOf`; material/cosmetic classification is traceable. |
| Open questions | Which change types have reliable event signatures vs require indexer derivation. |

## Slice 3 — Oracle telemetry and methodology feed

| Item | Detail |
| --- | --- |
| User/product decision unblocked | Oracle freshness, safe-pricing, methodology-fit gates. |
| Requirements covered | `DR-LP-AN-Q2`, `DR-LP-MON-Q6`, `DR-CA-AN-Q2`, `DR-CA-MON-Q1`, `DR-CA-MON-Q5`, Preview freshness checks. |
| Entities / events touched | `OracleTelemetry`, oracle methodology registry, oracle-change `EventFeedItem`. |
| Sources / ingestion needed | Oracle contract payloads, price update events, main/reserve oracle config, methodology classification. |
| API endpoints | `GET /oracle-telemetry?token=...&scope=...`. |
| Verification | Stale oracle blocks execution where freshness is required; methodology changes since last check are surfaced. |
| Open questions | Whether real market price vs oracle price is in scope for collateral details; docs currently flag this as uncertain. |

## Slice 4 — RWA / issuer-compliance state extension

| Item | Detail |
| --- | --- |
| User/product decision unblocked | Controlled-asset positions are not treated as ordinary liquid collateral. |
| Requirements covered | `DR-LP-MON-Q7`, `DR-CA-AN-Q2`, `DR-CA-AN-Q4`, `DR-CA-MON-Q6`, controlled-asset Preview / Execute checks. |
| Entities / events touched | `RwaAssetProfile`, `RwaComplianceProfile`, issuer events, eligible-liquidator depth. |
| Sources / ingestion needed | Issuer / Securitize / platform endpoints, investor registry, freeze data, redemption calendar, liquidator allowlist/depth. |
| API endpoints | `GET /issuer-state?token=...`, `GET /issuer-state/account/{account}`, `GET /issuer-state/liquidators`. |
| Verification | Own frozen status blocks action; unknown eligibility blocks controlled-asset automation; redemption/claim path is visible before exit. |
| Open questions | Exact issuer integrations and freshness guarantees; whether eligible-liquidator depth is indexable or manually curated. |

## Slice 5 — Curator profile endpoint

| Item | Detail |
| --- | --- |
| User/product decision unblocked | “Who manages this pool / CM?” and curator track record. |
| Requirements covered | `DR-LP-AN-Q4`, `DR-LP-MON-Q5`, `DR-CA-AN-Q4`, curator portions of Monitor change questions. |
| Entities / events touched | `CuratorProfile`, `badDebtIncidents[]`, `liquidityIncidents[]`, external refs, curator activity log. |
| Sources / ingestion needed | Protocol authority reads, pool/CM history, incident logs, curated external links, DefiLlama / governance/forum sources where accepted. |
| API endpoints | `GET /curators/{curator_id}`. |
| Verification | Curator identity and governance mechanism render with source refs; unknown incidents are not shown as zero incidents. |
| Open questions | Editorial ownership for doxxed-team flags, resolution notes, and external summaries. |

## Slice 6 — LP pool research read model

| Item | Detail |
| --- | --- |
| User/product decision unblocked | LP can answer the five entry due-diligence questions with evidence. |
| Requirements covered | `DR-LP-DISC-001`, `DR-LP-AN-Q1`–`Q5`. |
| Entities / events touched | `PoolOpportunity`, `TokenExposure`, `HistoricalSeries`, `CuratorProfile`, `EventFeedItem`. |
| Sources / ingestion needed | Pool state, APY / incentive data, exposure formula, IRM, oracle telemetry, curator profile, change feed. |
| API endpoints | `GET /opportunities/pools`, `GET /pools/{pool_id}/research`. |
| Verification | Research memo can produce yield, exposure, exit, curator, and change verdicts; missing fields map to explicit gaps. |
| Open questions | Current exposure per token: derive from per-CA debt or treat `quotaUsed` as proxy only after verification. |

## Slice 7 — Credit Account strategy research read model

| Item | Detail |
| --- | --- |
| User/product decision unblocked | CA operator can choose strategy, leverage, and route with safety evidence. |
| Requirements covered | `DR-CA-DISC-001`, `DR-CA-AN-Q1`–`Q5`, `DR-CA-PROP-001`. |
| Entities / events touched | `StrategyOpportunity`, `SafetyEnvelope`, `CreditManagerEnvelope`, `OracleTelemetry`, `RwaComplianceProfile`, route quotes. |
| Sources / ingestion needed | CM state, pool IRM, collateral yield, borrow / quota series, route quotes, LT ramps, safe-pricing, issuer branch. |
| API endpoints | `GET /opportunities/strategies`, `GET /strategies/{strategy_id}/research`. |
| Verification | Target leverage clears net APY and HF floor; missing policy routes to review instead of Preview readiness. |
| Open questions | Route-quality comparison against 1inch / CoW and sample-size policy. |

## Slice 8 — LP monitoring snapshot and action sizing

| Item | Detail |
| --- | --- |
| User/product decision unblocked | LP sees in under a minute whether yield, exit, exposure, rules, bad-debt canary, or issuer branch drifted. |
| Requirements covered | `DR-LP-MON-Q1`–`Q7`, `DR-LP-MON-PROP-001`. |
| Entities / events touched | `LpPosition`, `LpMonitoringSnapshot`, `FocusedAnalyzeReport`, `ActionDecision`. |
| Sources / ingestion needed | LP position state, pool state, APY series, event feed, share-price series, issuer extension, agent continuity log. |
| API endpoints | `GET /positions/lp/{position_id}/monitoring`, `POST /actions/propose` or internal proposal builder. |
| Verification | First call establishes baseline; subsequent calls produce deltas and focused Analyze back-edge; action sizing uses supplied concentration / exit policy. |
| Open questions | Policy for LP “quiet” cadence and notification threshold. |

## Slice 9 — Credit Account monitoring snapshot and emergency routing

| Item | Detail |
| --- | --- |
| User/product decision unblocked | CA operator sees safety/returns/rule/operational/issuer drift and can route directly to emergency action. |
| Requirements covered | `DR-CA-MON-Q1`–`Q6`, `DR-CA-MON-PROP-001`. |
| Entities / events touched | `CreditAccountPosition`, `CreditAccountMonitoringSnapshot`, `FocusedAnalyzeReport`, `ActionDecision`. |
| Sources / ingestion needed | CA state, HF history, debt / balance breakdown, PnL, reward attribution, event feed, withdrawal queues, oracle telemetry, issuer state. |
| API endpoints | `GET /positions/credit-account/{account}/monitoring`, `POST /actions/propose`. |
| Verification | Emergency condition skips broad Analyze but not Preview; frozen status overrides HF; missing floor blocks automated leverage changes. |
| Open questions | Exact emergency policy UX for first-time users vs scoped bot users. |

## Slice 10 — PnL / returns endpoint

| Item | Detail |
| --- | --- |
| User/product decision unblocked | CA returns Glance and monthly reporting. |
| Requirements covered | `DR-CA-MON-Q2`, portions of institutional reporting requirements in personas. |
| Entities / events touched | Account-value series, reward attribution, yield-source decomposition. |
| Sources / ingestion needed | Per-tx or daily account value, cost-basis anchor at entry, borrow / quota / reward series, Merkl owner-wallet linkage. |
| API endpoints | `GET /positions/credit-account/{account}/returns`. |
| Verification | PnL total decomposes into farming / rewards / price appreciation / borrow / quota / fees; owner-wallet rewards are explicitly linked. |
| Open questions | Cost-basis method and whether account-value series is daily or per transaction. |

## Slice 11 — Historical series service

| Item | Detail |
| --- | --- |
| User/product decision unblocked | Trends, stress history, virtual liquidation counter, scenario simulator. |
| Requirements covered | History dependencies across LP / CA Analyze and Monitor. |
| Entities / events touched | `HistoricalSeries` families from [[data-read-spec]]. |
| Sources / ingestion needed | APY, utilisation, TVL, borrow, quota, oracle, share price, account value, price impact. |
| API endpoints | `GET /series?entity=...&metric=...&window=...`. |
| Verification | 90d daily minimum available for named metrics; current-vs-history missing semantics enforced. |
| Open questions | Whether scenario simulator / virtual-liquidation counter belongs in this slice or separate analytics product. |

## Slice 12 — Explanation and institutional reporting layer

| Item | Detail |
| --- | --- |
| User/product decision unblocked | Defensible monthly check-ins and drill views. |
| Requirements covered | T2 drill requirements and social persona needs. |
| Entities / events touched | Research memos, monitoring snapshots, source refs, curator / incident / oracle drill data. |
| Sources / ingestion needed | All prior slices. |
| API endpoints | Export / report endpoints, or frontend-only composition over existing read models. |
| Verification | Every explanation points to raw values and source refs; labels are not orphaned. |
| Open questions | Report format and whether to generate artifacts server-side or client-side. |
