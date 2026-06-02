# Data requirements and to-dos

This is the backend-facing implementation hub for the Gearbox front knowledge base. Product-facing flow docs own user-visible data, decisions, and failure modes. The files in this folder compile those canonical runtime docs into backend/data specs after the flow shape is settled.

User preference / thesis persistence is outside Gearbox-side protocol scope. Rows that mention user policy inputs describe runtime inputs supplied by the user or the user's representative agent, not data Gearbox must store by default.

## Formal spec map

| File | Role |
| --- | --- |
| [[data-read-spec]] | Snapshots, histories, event logs, read models, provenance, freshness, and unknown-state behavior. |
| [[data-write-spec]] | Propose / Preview / Execute command contracts, transaction-package integrity, bot policy, errors, and receipts. |
| [[data-dictionary]] | Logical fields, types, source classes, temporal shapes, validation rules, unknown-state behavior, and requirement coverage. |
| [[data-architecture]] | Source-of-truth map, bounded contexts, storage / projection shape, ingestion cadence, APIs, data quality controls, and failure modes. |
| [[traceability-matrix]] | Product source → requirement → data/artifact coverage → verification, with backward trace by artifact. |
| [[implementation-slices]] | Ordered backend/data build slices by decision impact and safety. |

## Implementation principles

| Principle | Meaning |
| --- | --- |
| Source separation | Separate protocol facts, indexer facts, issuer / compliance facts, product judgment, and user / agent policy. |
| Unknown is explicit | Missing external data should surface as `unknown`, `review_required`, or `blocking` where material, never as green status. |
| Read / write split | Informational read models are separate from Preview / Execute command contracts and receipts. |
| No hidden thresholds | User floors, concentration caps, oracle-methodology acceptance, HF floors, and automation scope are explicit policy inputs. |
| RWA as extension | Tokenized securities / issuer-controlled collateral are conditional branches inside ordinary LP / Credit Account flows, not standalone flows. |

## Canonical stage artifacts

| Artifact | Where formalized | Notes |
| --- | --- | --- |
| `OpportunityCandidate` | [[data-read-spec#Stage handoff artifacts]] | Identifier-only shortlist; Stage 2 re-fetches current facts. |
| `ResearchMemo` | [[data-read-spec#Stage handoff artifacts]], [[traceability-matrix]] | Evidence-backed Analyze output for one candidate. |
| `ProposedAction` | [[data-read-spec#Stage handoff artifacts]], [[data-write-spec#Command model]] | Umbrella Propose → Preview handoff. Entry flows use concrete `AllocationDecision`; ownership / monitoring flows use concrete `ActionDecision`. |
| `TransactionPreview` | [[data-write-spec#TransactionPreview]], [[data-dictionary#Write-side artifacts]] | Highest-priority hardening target: exact package, simulation, warnings, expiry, and integrity hash. |
| `ExecutionReceipt` | [[data-write-spec#Execution receipt]], [[data-dictionary#Write-side artifacts]] | Confirms submitted package hash, tx status, state delta, and monitoring-baseline update. |
| `MonitoringSnapshot` | [[data-read-spec#Stage handoff artifacts]], [[traceability-matrix]] | Current position state + drift verdicts + alerts. |
| `MonitorAlert` | [[data-read-spec#Stage handoff artifacts]] | Specific actionable drift / blocker emitted by monitoring. |

## Gap register

| Gap | Primary spec / slice | Product decisions unblocked | Notes |
| --- | --- | --- | --- |
| Source provenance and unknown-state labels | [[data-read-spec#Source and unknown-state contract]], [[data-dictionary#Shared field envelope]], [[implementation-slices#Slice 1 — Source provenance and unknown-state envelope]] | Any verdict, ranking, Preview, or automation decision. | Missing external data should surface as `unknown` or `blocking` where material. |
| Preview type family and integrity gate | [[data-write-spec#TransactionPreview]], [[implementation-slices#Slice 0 — Preview integrity gate]] | All Preview / Execute stages, including emergency and RWA / compliance-gated actions. | Needs `preview_id`, expiry, pass/fail, warning severity / source / blocking status, approval mode, exact execution package, and package hash binding. |
| Parameter-change log + pending governance feed | [[data-read-spec#EventFeedItem / GovernanceChange]], [[data-architecture#Ingestion and update cadence]], [[implementation-slices#Slice 2 — Unified event / governance change feed]] | LP Analyze Q5, CA Analyze Q5, LP Monitor Q3/Q4, CA Monitor Q3. | One stream, many readers. Include parameter changed, effective time, timelock / Safe status, materiality, scope, and 30d / 90d / 365d summaries. |
| Oracle telemetry + methodology feed | [[data-read-spec#OracleTelemetry]], [[data-dictionary#OracleTelemetry]], [[implementation-slices#Slice 3 — Oracle telemetry and methodology feed]] | LP exposure / oracle drills, CA safe-pricing, Preview freshness checks. | Raw feed supplies category/methodology, last update, staleness window, main-vs-reserve divergence, methodology-change history, and source confidence. Accepted methodology remains user / product policy. |
| RWA / KYC extension | [[data-read-spec#RwaAssetProfile and RwaComplianceProfile]], [[data-dictionary#RwaAssetProfile / RwaComplianceProfile]], [[implementation-slices#Slice 4 — RWA / issuer-compliance state extension]] | Tokenized-security exposure, compliance-gated CA opens / exits, issuer-controlled monitoring. | Needs issuer state, KYC validity, own freeze status, investor registry status, redemption calendar, issuer/regulatory event notes, and eligible-liquidator depth. |
| Curator profile endpoint | [[data-read-spec#CuratorProfile]], [[data-dictionary#CuratorProfile]], [[implementation-slices#Slice 5 — Curator profile endpoint]] | “Who manages this pool?” and “Who manages this CM?” on LP and CA flows. | Include identity, governance mechanism, first operation date, AUM, cumulative bad debt, bad-debt incidents, liquidity incidents, and source refs. ==note: and/or external link + summary from DefiLlama or similar== |
| LP pool research read model | [[data-read-spec#PoolOpportunity]], [[traceability-matrix#LP entry flow]], [[implementation-slices#Slice 6 — LP pool research read model]] | LP Discover and LP five-question due diligence. | Requires APY / incentive data, exposure formula, IRM, oracle telemetry, curator profile, and change feed. |
| Credit Account strategy research read model | [[data-read-spec#StrategyOpportunity]], [[traceability-matrix#Credit Account entry flow]], [[implementation-slices#Slice 7 — Credit Account strategy research read model]] | CA Discover, CA due diligence, target leverage, route selection. | Requires economics, safety envelope, exit feasibility, CM envelope, change feed, route quotes, and issuer branch. |
| LP monitoring snapshot and action sizing | [[data-read-spec#LpPosition]], [[traceability-matrix#LP monitoring flow]], [[implementation-slices#Slice 8 — LP monitoring snapshot and action sizing]] | LP Confirmation, Analysis, Action, Exit branches. | First call establishes baseline; later calls compare deltas and route focused Analyze / action proposals. |
| Credit Account monitoring snapshot and emergency routing | [[data-read-spec#CreditAccountPosition]], [[traceability-matrix#Credit Account monitoring flow]], [[implementation-slices#Slice 9 — Credit Account monitoring snapshot and emergency routing]] | CA safety / returns / rule / operational / issuer monitoring and emergency path. | Emergency may skip broad Analyze, but cannot skip Preview. Own frozen status overrides HF. |
| PnL / returns endpoint | [[data-read-spec#Core read models]], [[data-dictionary#CreditAccountPosition]], [[implementation-slices#Slice 10 — PnL / returns endpoint]] | CA returns Glance and institutional monthly reporting. | Requires account value history, cost-basis anchor at entry, yield-source decomposition, and Merkl owner-wallet attribution. |
| Historical series service | [[data-read-spec#HistoricalSeries]], [[data-architecture#Storage / projection shape]], [[implementation-slices#Slice 11 — Historical series service]] | Trends, stress history, oracle history, virtual liquidation counter, scenario simulator. | Minimum current list: supply rate 90d, incentive 90d, composite APY 90d, utilisation 90d, TVL 90d, borrow rate 30d, volatility 90d, oracle prices 90d, share price 90d, price-impact 90d. |
| Withdrawal queue / claim-readiness feed | [[data-dictionary#SafetyEnvelope]], [[data-dictionary#CreditAccountPosition]], [[implementation-slices#Slice 4 — RWA / issuer-compliance state extension]] | CA exit feasibility, delayed-withdrawal monitoring, matured claim prompts. | Backend hint: periphery/SDK surface includes `getWithdrawableAssets(creditManager)` for supported assets and `getCurrentWithdrawals(creditAccount)` for current pending/claimable queue state. Keep these method names out of product-facing flow copy. |
| LT-ramp schedule fields | [[data-dictionary#SafetyEnvelope]], [[traceability-matrix#Credit Account entry flow]], [[traceability-matrix#Credit Account monitoring flow]] | CA HF feasibility and monitoring safety drift. | Backend hint: map implementation fields such as `ltInitial`, `ltFinal`, `timestampRampStart`, and `rampDuration`; product docs should say “LT-ramp schedule.” |
| KYC-gated execution routing metadata | [[data-write-spec#Execution boundary]], [[data-write-spec#Bot-policy contract]], [[implementation-slices#Slice 4 — RWA / issuer-compliance state extension]] | Compliance-gated CA execution and bot eligibility. | Backend hint: contract-level routing may involve `SecuritizeKYCFactory`, `SecuritizeWallet`, and `CreditFacade`; product docs should surface this as “compliance-gated execution” and HITL-only management. |
| Contextual recommendation engine | [[traceability-matrix]], [[implementation-slices#Slice 8 — LP monitoring snapshot and action sizing]], [[implementation-slices#Slice 9 — Credit Account monitoring snapshot and emergency routing]] | Quick actions and monitoring-to-action routing. | Parameterize by user policy and asset-specific blockers rather than fixed universal thresholds. Include better-strategy recommendations, reward claims, and withdrawal events when present. |
| Before/after transaction preview component | [[data-write-spec#Before / after contract]] | Every action flow that reaches Preview. | Product surface backed by `TransactionPreview`: two-column current → projected state for HF, leverage, equity, position size, net APY, withdrawal / claim result, warnings, and gas. ==note: maybe it's on the wallet side though?== |
| Market risk history | [[data-read-spec#HistoricalSeries]], [[data-dictionary#CuratorProfile]], [[implementation-slices#Slice 12 — Explanation and institutional reporting layer]] | Curator track record, exit confidence, bad-debt canary explanations. | Includes cumulative bad debt, bad-debt incidents, liquidity incidents, AUM, utilisation history, withdrawal pressure, and historical pool/debt composition. |

## Product/data boundary reminders

- Flow docs should name user-visible facts and decisions; this folder names implementation artifacts, field families, and verification requirements.
- Backend feeds should return facts, provenance, and timestamps; product / agent policy decides whether those facts are acceptable for this user.
- Issuer-controlled collateral data is required only as a conditional extension on ordinary Pool / Credit Account lifecycles.
- Preview / Execute must prove transaction-package integrity. Missing integrity binding means do not execute.
