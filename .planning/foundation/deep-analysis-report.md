# Gearbox Front Knowledge Base — Deep Analysis Report

> **Archive note.** This is a pre-merge planning artifact. References to deleted `JTBDs/`, `User flows/`, Tier 4 user-flow, Tier 5 UI-primitive, `Multi-position`, or placeholder RWA structures are historical source-state references. Current canonical navigation lives in `../../README.md`, `../../CLAUDE.md`, and `../../user-flows/`.

Date: 2026-04-29
Scope: `projects/front-knowledge-base/`

## Executive summary

The Gearbox front knowledge project is an Obsidian product-knowledge vault, not a codebase. Its purpose is to turn Gearbox protocol/product understanding into a shared decision model for humans, LLM agents, frontend screens, and backend planning.

The vault's strongest design is a unified decision spine: `Discover → Analyze → Propose → Preview → Execute → Monitor`, combined with session modes and Glance / Analyze / Act progressive disclosure. This gives Gearbox a coherent product language for pool LPs, Credit Account operators, RWA flows, monitoring, emergency response, and agentic execution.

The main weakness is source-of-truth discipline. The vault contains strong product thinking, but operationally meaningful facts are still too implicit, inconsistent, or draft-like: HF thresholds drift, schemas are referenced but not centrally defined, Preview is under-specified, RWA is scattered with an empty dedicated flow, and agent/bot execution boundaries remain unresolved.

## What the project is for

The project is a structured product knowledge base for:

1. Human Gearbox front-end users:
   - Pool LPs choosing and monitoring passive lending positions.
   - Credit Account operators opening and managing leveraged positions.
   - Treasury, fund, and RWA allocators needing risk and audit clarity.

2. LLM agents acting on the same facts:
   - Agents are treated as consumers of the same schema.
   - Agents should answer the same product questions a human screen answers, but serialized and verdict-first.

3. Product and backend planning:
   - The vault identifies fields the UI needs.
   - It exposes backend gaps such as historical series, preview simulation, PnL, curator profiles, governance feeds, and RWA/KYC data.

Core purpose:

> Build one product-decision schema for Gearbox positions so UI, agents, monitoring, and execution previews all reason from the same facts.

## Design model

### Tier 1 — Foundations

Root-level shared concepts:

- `Basic info and definitions.md`
  - Defines Credit Account, collateral, underlying token, IRM.
  - Defines the canonical loop: `Discover → Analyze → Propose → Preview → Execute → Monitor`.
  - Defines CA vocabulary: HF, LT, LT ramp, quota, safe pricing, forbidden tokens, TWV, liquidation premium, etc.
  - Defines Pool vocabulary: insurance fund, bad-debt canary, organic vs incentive APY.

- `Personas and audience.md`
  - Main personas: Pool LP and CA operator.
  - Each persona includes an Agent / LLM acting on behalf of the user.

- `Benchmarks and tresholds for metrics.md`
  - Green / yellow / red thresholds for pool and CA monitoring.
  - Intended to be the source for Glance verdicts.

- `Data requirements and to-dos.md`
  - Backend/product punch list.
  - Includes curator profiles, parameter-change feeds, historical series, preview types, RWA/KYC extension, PnL, scenario simulator, recommendation engine.

### Tier 2 — Decision axes

- `Entry points.md`
  - Decision session: full Discover → Execute.
  - Monitoring session: starts at Monitor, usually 10–30 seconds.
  - Emergency session: danger state, skips analysis, gets to remediation fast.

- `Three-layer progressive disclosure.md`
  - Glance: "Am I safe? Am I making money?"
  - Analyze: why the verdict is true.
  - Act: concrete action with before/after evidence.

This is one of the strongest design choices. The six-stage loop says where the user is in the lifecycle; Glance / Analyze / Act says how each surface or agent reply should be organized.

### Tier 3 — JTBDs

Persona × lifecycle documents:

- `JTBDs/Pool deposit — JTBD.md`
- `JTBDs/Pool position management - JTBD.md`
- `JTBDs/Credit Account (Opening) — JTBD.md`
- `JTBDs/Credit Account management - JTBD.md`
- `JTBDs/Multi-position & portfolio-level - JTBD.md`

These own the why/what:

- What question is the user trying to answer?
- What outcome counts as success?
- What emotional/social/functional dimensions matter?
- What edge cases exist?

The conceptual center is the ownership/session matrix in `Multi-position & portfolio-level - JTBD.md`:

| Session type | Path | Purpose |
| --- | --- | --- |
| Confirmation | Monitor → exit | Reassure user, no action |
| Analysis | Monitor → Analyze | Understand what changed |
| Action | Monitor → Propose → Preview → Execute | Maintenance / optimization |
| Emergency | Monitor danger → Propose → Preview → Execute | Remediate quickly |
| Exit | Monitor → Propose → Preview → Execute | Leave deliberately |
| Reallocation | Monitor → Discover → Analyze → Propose → Preview → Execute | Move capital elsewhere |

### Tier 4 — User flows

Operational walkthroughs:

- `User flows/Pool deposit - User flow (LP).md`
- `User flows/Credit Account - User flow (CA operator).md`
- `User flows/rwa-leverage.md` — currently empty stub.

These own the how:

- Stage-by-stage questions.
- Field references like `PoolOpportunity.yield`, `StrategyOpportunity.minDebt`, `TransactionPreview`.
- Preview/execution gates.
- Monitoring deltas.
- RWA/KYC extensions.

Important invariant:

- Failed Preview loops back to Propose, not Analyze.
- Monitor deviation loops back to Analyze.

This is a good product model: it prevents over-researching when only parameters changed, but forces renewed diligence when the thesis changed.

### Tier 5 — UI primitives

Stored as `.docx` files in `ui-primitives/`:

- `Opportunity.docx`
- `LenderDetails.docx`
- `StrategyDetails.docx`
- `Positions.docx`
- `LenderPosition.docx`
- `StrategyPosition.docx`

These are screen/component specs mapping to loop stages:

- Opportunity = Discover.
- Lender/Strategy Details = Discover → Analyze → Propose → Preview.
- Positions = Monitor roll-up.
- Lender/Strategy Position = Monitor + Act.

## Strong parts

### 1. Real product spine

The canonical loop maps to both a user's cognitive journey and a transaction pipeline.

Each stage produces a structured artifact:

| Stage | Artifact |
| --- | --- |
| Discover | `Opportunity[]` |
| Analyze | `AnalyzedCandidate[]` |
| Propose | `ProposedAction` |
| Preview | `TransactionPreview` |
| Execute | receipt / position update |
| Monitor | snapshot + deltas |

This is stronger than generic dashboard documentation.

### 2. Monitoring-first framing

The vault correctly treats first-time decisions as rare and monitoring as frequent. Most DeFi UIs over-optimize for opening a position and under-serve "I already have money here, what changed?"

The session taxonomy makes monitoring actionable instead of generic.

### 3. Glance / Analyze / Act bridges UI and agents

For humans:

- Glance = visual verdicts, chips, charts.
- Analyze = drilldown.
- Act = buttons and previews.

For agents:

- Glance = structured verdict.
- Analyze = evidence.
- Act = proposed action.

Same data, different render.

### 4. Gearbox-specific risk understanding

The vault correctly tracks Gearbox-specific mechanics:

- HF = `TWV / debt`.
- LT ramp can reduce HF without price movement.
- Quota caps affect TWV.
- Safe pricing is not automatic oracle fallback.
- Forbidden tokens affect exit HF.
- CM expiration can make accounts liquidatable regardless of HF.
- Pool LPs do not have liquidation risk, but inherit bad debt / liquidity / curator risk.
- RWA introduces freeze, KYC, redemption, and liquidator-whitelist risks.

### 5. Agent-ready intent

The vault already thinks in:

- machine-readable fields,
- shared schema,
- verdict tokens,
- action proposals,
- preview gates,
- structured artifacts.

This is a strong base for an agentic Gearbox product.

## Weak parts

### 1. Authority without enough source-of-truth discipline

Operationally meaningful thresholds are present but inconsistent or unresolved.

Main example: HF thresholds drift across docs:

- HF > 1.3 = green.
- 1.1–1.3 = yellow.
- < 1.1 = red.
- Preview hard floor uses `HF > 1.07`.
- Examples mention HF 1.4.
- Recommendation engine mentions HF > 1.5 for "increase leverage".

Why it matters: an agent or UI could make materially different recommendations depending on which doc it reads.

Corrective action: make `Benchmarks and tresholds for metrics.md` the canonical threshold source and classify threshold types:

| Threshold type | Example |
| --- | --- |
| Solvency fact | HF ≤ 1 liquidatable |
| UI warning band | red < 1.1 |
| Preview reject floor | reject if projected HF < X |
| User-configurable floor | user-specific |
| Recommendation band | increase leverage only if HF > Y |

### 2. Schema is implied, not defined

The vault references many fields but has no central registry:

- `Opportunity.id`
- `Opportunity.chainId`
- `Opportunity.curatorId`
- `PoolOpportunity.yield`
- `PoolOpportunity.collaterals[]`
- `StrategyOpportunity.minDebt`
- `StrategyOpportunity.maxDebt`
- `StrategyOpportunity.maxLeverageYield`
- `TransactionPreview`
- `PreviewRoute`
- `RawTx`
- `GovernanceChange[]`
- `RwaAssetProfile`
- `RwaComplianceProfile`

Why it matters: future frontend/backend/agent implementation will diverge.

Corrective action: add `Data contracts.md` or `Schema.md` with type, field, meaning, source, freshness, used-by, and availability status.

### 3. RWA is important but not fully integrated

RWA appears everywhere, but `User flows/rwa-leverage.md` is empty.

Current RWA handling is scattered as extension blocks:

- RWA LP risk in personas.
- RWA fields in data requirements.
- RWA compliance in CA flow.
- RWA emergency variants in multi-position JTBD.

Why it matters: RWA changes action semantics: freezes, KYC expiry, redemption windows, whitelisted liquidators, blocked bot permissions.

Corrective action: write the RWA flow or delete the stub. If written, treat it as a CA operator variant rather than a separate product universe.

### 4. Preview is critical but under-specified

The docs correctly identify Preview as the execution gate, but the contract is thin:

- `TransactionPreview` is missing.
- `PreviewRoute` is missing.
- `RawTx` is missing.
- Before/after preview component ownership is unresolved.
- Pool preview questions whether wallet or product owns this.

Why it matters: Preview is the trust boundary — the signed bytes must be the bytes validated by Preview.

Corrective action: define Preview as its own contract:

```text
TransactionPreview
- actionType
- currentState
- projectedState
- deltas
- warnings
- hardFailures
- route
- calldata
- simulationBlock
- freshness
- userApprovalsNeeded
- signerPolicy
```

### 5. Agent vs bot boundary is fuzzy

Open questions remain:

- Does the agent keep persistent user state?
- Can the agent initiate Decision sessions autonomously?
- What is the emergency protocol for agents?
- How is "agent-side whitelist" different from scoped bot signer?

Why it matters: agentic financial products need hard execution boundaries.

Corrective action: add `Agent execution boundaries.md`:

| Layer | Can do | Cannot do |
| --- | --- | --- |
| LLM agent | analyze, propose, explain, prepare preview | sign, bypass Preview, mutate state silently |
| Preview engine | simulate, compare before/after | reason about user preference |
| Bot signer | execute approved scoped actions | choose thesis |
| Human | approve policy / high-value / first-time actions | n/a |

### 6. Product truth is mixed with working notes

The vault contains many `==note:==` and `==resolved_note:==` markers. Some are fine as author working memory, but they weaken authoritative tables.

Examples:

- "depends, could be adjusted based on Credora scores"
- "maybe it's on the wallet side"
- "is that true? example?"
- "seems unnecessary"
- Russian commentary inside flow docs
- casual language like "be a good guy", "token bullshit", "legitness"

Corrective action: triage notes into:

| Type | Destination |
| --- | --- |
| Resolved fact | Convert to normal prose or `==resolved_note:==` |
| Real backend gap | Promote to `Data requirements and to-dos.md` |
| Product decision needed | Add to `Open decisions.md` |
| Author scratch | Move to planning artifact |
| Not needed | Delete |

### 7. Multi-position lacks operational flow

`Multi-position & portfolio-level - JTBD.md` is conceptually strong, but there is no matching user flow.

Why it matters: portfolio view is where high-value use cases live:

- total exposure,
- worst HF,
- correlated oracle/underlying risk,
- same-curator contagion,
- reallocation,
- emergency triage order.

Corrective action: add `User flows/Multi-position - User flow.md` focused on roll-up, compare, triage, reallocation, export/report.

### 8. Data requirements are not buildable slices

`Data requirements and to-dos.md` mixes endpoints, backend series, UI components, policy decisions, risk primitives, simulator ideas, and product rules.

Corrective action: split by vertical product slice:

| Slice | Needed for |
| --- | --- |
| LP Glance | yield, utilization, liquidity, share price |
| CA Glance | HF, net APY, liquidation distance, LT ramp |
| Preview | simulation, before/after, warnings, calldata |
| RWA safety | frozen status, KYC, redemption, whitelist |
| Portfolio | positions, exposures, worst HF, concentration |

### 9. Link/naming validation is manual

Observed fragilities:

- `tresholds` typo in filename.
- Empty `rwa-leverage.md` breaks naming convention.
- Obsidian wikilinks and URL-encoded markdown links are mixed.
- Some planning docs are stale relative to current structure.

Corrective action: add deterministic vault checks:

- README links point to real files.
- Wikilink note targets exist.
- Empty markdown docs are intentional.
- No unclosed `==note:` markers.
- No stale `Stage 2a/2b` references.
- Schema fields are registered.

### 10. No provenance / review cadence

Docs with financial implications lack metadata:

- owner,
- last reviewed,
- source of truth,
- protocol version,
- review cadence.

Corrective action: add frontmatter at least to Tier 1 docs:

```yaml
owner: product
lastReviewed: 2026-04-29
sourceOfTruth: internal-product-design
reviewCadence: monthly or on protocol parameter change
status: draft/internal
```

## Top 5 recommended fixes

1. Create `Data contracts.md` for all `Opportunity`, `Position`, `TransactionPreview`, RWA, governance, and PnL fields.
2. Resolve the HF / threshold model into one canonical benchmark source with threshold types.
3. Define `TransactionPreview` fully as the trust boundary for all actions.
4. Write the missing Multi-position user flow because portfolio, emergency, and reallocation are core differentiators.
5. Triage all `==note:==` markers into resolved facts, backlog, open decisions, or scratch.

## Overall verdict

The vault is an excellent product-architecture base. It is stronger than normal product docs because it has a real decision loop, a monitoring-first model, a UI-agent bridge, and deep Gearbox risk understanding.

It is not yet an implementation-grade source of truth. To become one, it needs tighter schema ownership, canonical thresholds, a formal Preview contract, resolved agent/bot boundaries, and deterministic validation.
