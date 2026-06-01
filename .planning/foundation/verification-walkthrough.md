# Verification walkthrough — auditing the vault from foundations down

> **Archive note.** This is a pre-merge planning artifact. References to deleted `JTBDs/`, `User flows/`, Tier 4 user-flow, Tier 5 UI-primitive, `Multi-position`, or placeholder RWA structures are historical source-state references. Current canonical navigation lives in `../../README.md`, `../../CLAUDE.md`, and `../../user-flows/`.

## When to use this

You're a new reader (PM, LLM, or returning author) and you want to convince yourself that the vault is internally consistent — that every downstream claim is backed by an upstream definition you agree with, and that no Tier 1 element is being silently mis-used downstream.

The conceptual model: **upstream is canonical, downstream consumes**. So you read upstream first, then read each downstream doc *with the upstream concept in mind*, asking "does this faithfully derive what the upstream defines?"

This file is a meta-guide. It does not replace `CLAUDE.md` (the operating contract) or the `.planning/codebase/` reference docs (which describe the vault's structure as it is). It's the audit path you walk when you want to *verify* the vault rather than *describe* it.

## The dependency diagram (current state, post-2026-04-29 edits)

```
TIER 1 — Foundations (top-level .md)
├── Basic info and definitions.md
│   ├── Credit Account / Collateral / Underlying / IRM / Sources of yield
│   ├── Canonical loop (Discover → Analyze → Propose → Preview → Execute → Monitor)
│   ├── Credit Account vocabulary  (HF, LT, LT ramp, quota, safe pricing,
│   │     phantom token, delayed withdrawal, CM, CM expiration, minDebt/maxDebt,
│   │     oracle, TWV, forbidden tokens, liquidation premium, multicall, IRM bands)
│   └── Pool vocabulary  (insurance fund, bad-debt canary, organic vs incentive APY,
│         concentration cap, whitelisted-liquidator count)
├── Personas and audience.md  (Pool LP, CA operator, loss-vector tables, agent sub-profile)
├── Benchmarks and tresholds for metrics.md  (green/yellow/red bands per persona)
└── Data requirements and to-dos.md  (EXHAUST — aggregates ==note:== gaps from downstream)
        │
        ▼
TIER 2 — Decision-making loop (scaffolding, root-level)
├── Entry points.md  (3 session modes + 6-row matrix mapping — the canonical
│     refinement of "Decision / Monitoring / Emergency" into Confirmation /
│     Analysis / Action / Emergency / Exit / Reallocation)
└── Three-layer progressive disclosure.md  (Glance / Analyze / Act)
        │
        ▼
TIER 3 — JTBDs (persona × scope)
├── Pool deposit — JTBD                  (LP × Entry)        →─┐
├── Pool position management - JTBD      (LP × Ownership)    →─┤
├── Credit Account (Opening) — JTBD      (CA × Entry)        →─┤── satisfied by Tier 4
├── Credit Account management - JTBD     (CA × Ownership)    →─┤
└── Multi-position & portfolio - JTBD    (cross-persona)     →─┘
                                                              ──┐
                                                                ▼
TIER 4 — User flows (Stage 1 → Stage 6 traversal)
├── Pool deposit - User flow (LP)         (satisfies Pool deposit JTBD 1–5
│                                          + Pool position mgmt JTBD Stage 6)
├── Credit Account - User flow (CA operator)  (satisfies CA Opening JTBD 1–5
│                                          + CA mgmt JTBD Stage 6)
└── rwa-leverage.md  (empty stub)
        │
        ▼
TIER 5 — UI primitives (.docx in ui-primitives/)
├── Opportunity            (both personas, Stage 1)
├── LenderDetails          (LP, Stages 1–4)
├── StrategyDetails        (CA operator, Stages 1–4)
├── Positions              (both personas, Stage 6 cross-position roll-up,
│                           mirrors Multi-position JTBD)
├── LenderPosition         (LP, Stage 6 single-position)
└── StrategyPosition       (CA operator, Stage 6 single-position)
```

### Edge inventory

**Explicit (wikilinked)**:
- Multi-position matrix → `Entry points#Mapping…`; → all four sibling ownership JTBDs by section
- CA Opening sub-jobs 8, 9 → CA management (handoffs)
- CA management → Data requirements (strategy description, virtual liquidations)
- CA management sub-job 5 → Benchmarks (borrow-rate spread)
- Pool position management → Basic info Pool vocabulary, Canonical loop, Data requirements (entry baseline, oracle feed)
- Pool deposit → Basic info Pool vocabulary, Data requirements (curator threshold, RWA threshold, concentration cap)

**Implicit (used but not yet wikilinked — deferred Item 6 in the 2026-04-29 plan)**:
- JTBD main-job statements don't wikilink `[[Personas and audience#Pool LP]]` / `[[…#CA operator]]`
- Tier 4 user flows don't wikilink the JTBDs they satisfy
- Tier 5 (`.docx`) — primitives reference flow stages by prose, no automated link checking

## Verification path

### Step 1 — Read the four Tier 1 foundations in order

| # | File | What you're calibrating |
|---|---|---|
| 1 | `Basic info and definitions.md` | Literal vocabulary. Notice the **two vocab tables** (CA + Pool). These are the definitions any downstream doc must conform to. |
| 2 | `Personas and audience.md` | Two personas + loss-vector tables. The risk inventory every downstream JTBD must address. Agent sub-profile lives here. |
| 3 | `Benchmarks and tresholds for metrics.md` | Numeric thresholds. Every "alert when X" or "good when Y" claim downstream must cite a row here, not invent a new band. |
| 4 | `Data requirements and to-dos.md` | What's missing. Read **last** — it's exhaust, not input. Tells you which downstream gaps are known and which are silent. |

### Step 2 — Read the two Tier 2 scaffolding docs

| # | File | What you're calibrating |
|---|---|---|
| 5 | `Entry points.md` | Three session modes + six-row matrix mapping. After this, the matrix in Multi-position reads as a refinement, not a duplicate. |
| 6 | `Three-layer progressive disclosure.md` | Glance / Analyze / Act — the layering perpendicular to the loop. Every screen and every agent reply should respect it. |

### Step 3 — For each Tier 1 element, walk it downstream (the "state transition" check)

This is the load-bearing step. Pick a concept, trace it through the dependency edges, and verify each downstream use is consistent with the upstream definition.

#### Trace A — `HF`

| Hop | File | What to verify |
|---|---|---|
| Tier 1 | `Basic info and definitions#Credit Account vocabulary` | HF = TWV / debt; drift drivers listed |
| Tier 1 | `Personas and audience` (CA operator loss vectors) | HF appears as a Priority-1 loss vector |
| Tier 1 | `Benchmarks and tresholds for metrics` | Green > 1.3, yellow 1.1–1.3, red < 1.1 |
| Tier 3 | `CA Opening JTBD` criterion 2 | **Currently struck through with no replacement** ← gap (deferred item 4 in 2026-04-29 plan) |
| Tier 3 | `CA management JTBD` Q1 + Emergency-path contract | Cites HF < 1.1 as danger zone — agrees with Benchmarks ✓ |
| Tier 3 | `CA management JTBD` translation table | "HF 1.036 / Low — your position liquidates if HF drops below 1.0" — agrees ✓ |
| Tier 4 | `CA user flow` Stage 4 Preview | Hard floor cited as **`HF > 1.07`** ← **contradicts** Benchmarks (red < 1.1) and CA mgmt (danger < 1.1). **Three docs, two numbers — known unresolved.** |
| Tier 5 | `StrategyPosition.docx` | Verify HF surface treats label/numeric pair per CA management Q1 contract |

**Verdict for HF**: definition in Tier 1 ✓; downstream propagation mostly consistent except the **1.07 vs 1.1 floor contradiction** in the user flow. Editorial decision needed: is 1.07 a Preview-time hard reject and 1.1 a Monitor alert band, or is one wrong?

#### Trace B — `Insurance fund`

| Hop | File | What to verify |
|---|---|---|
| Tier 1 | `Basic info and definitions#Pool vocabulary` | Pool-level loss-absorption pot, first hit on bad debt |
| Tier 1 | `Personas and audience` (LP loss vectors) | "bad debt absorption" listed |
| Tier 1 | `Benchmarks` | "Material decline or approaching zero" threshold row |
| Tier 1 | `Data requirements` | "Insurance-fund balance delta feed" row ✓ |
| Tier 3 | `Pool deposit JTBD` sub-job 4 | Wikilinks `[[Basic info and definitions#Pool vocabulary]]` ✓ |
| Tier 3 | `Pool position management JTBD` Q5 | Wikilinks `[[Basic info and definitions#Pool vocabulary]]` ✓ |
| Tier 4 | `Pool user flow` Stage 2 + Stage 6 | Verify the field name used matches the Data-requirements feed name |
| Tier 5 | `LenderPosition.docx` | Verify it surfaces insurance fund delta on the Stage 6 view |

**Verdict for insurance fund**: clean propagation. Definition exists, threshold exists, data feed is on the punch list, both consuming JTBDs link back to vocab.

#### Trace C — `Canonical loop`

| Hop | File | What to verify |
|---|---|---|
| Tier 1 | `Basic info and definitions#Canonical loop` | Six stages defined verbatim |
| Tier 2 | `Entry points` | All three session modes are described as different traversals of the loop |
| Tier 3 | All JTBDs | Sub-jobs *should* map to stages. **Pool deposit JTBD's 8 sub-jobs use a parallel taxonomy** (Define mandate / Locate / Validate / Trace / Verify / Assess / Commit / Maintain) that does not name the canonical stages. ← **gap**, not patched |
| Tier 4 | Both user flows | Use the canonical headings literally — `## Stage 2 · Analyze (CA)` etc. ✓ |
| Tier 5 | `.docx` | Loop-coverage column in the CLAUDE.md Tier 5 table maps each primitive to the stages it covers ✓ |

**Verdict for canonical loop**: Tier 1 → Tier 4 clean. Tier 3 has the Pool-deposit anomaly.

#### Trace D — `Six session-type matrix`

| Hop | File | What to verify |
|---|---|---|
| Tier 1 | `Basic info` | Canonical loop (steps the matrix re-traverses) |
| Tier 2 | `Entry points` § Mapping to ownership-lifecycle session types | The 6-row matrix is mapped to the 3-mode taxonomy ✓ |
| Tier 3 | `Multi-position JTBD` § Session-type matrix | Wikilinks back to `[[Entry points#Mapping…]]` ✓; rows wikilink to specific sibling JTBD sections ✓ |
| Tier 3 | All four ownership-flavoured JTBDs | The "Maintain conviction / Detect change / Optimise / Act under pressure / Exit / Reallocate" labels exist as sections or sub-jobs ✓ |

**Verdict**: coherent post-2026-04-29. Before that, this trace was completely broken (§2.X anchors pointed nowhere).

#### Trace E — Personas → JTBD coverage matrix

For each persona in `Personas and audience.md`, list every loss vector named for that persona, then find the JTBD sub-job or question that surfaces it.

**Pool LP loss vectors (current coverage)**:

| Loss vector | Where surfaced | OK? |
|---|---|---|
| Bad-debt absorption | Pool position mgmt Q5 | ✓ |
| IRM compression / yield decay | Pool position mgmt Q1 | ✓ |
| Underlying depeg | CA management edge cases (also relevant to LPs); not explicit in Pool position mgmt | partial |
| Withdrawal queue / utilisation spike | Pool position mgmt Q2 + edge case "Utilisation spike lockout" | ✓ |
| Silent curator/composition shift | Pool position mgmt Q3, Q4 | ✓ |
| Oracle staleness | Pool position mgmt Q6 + sub-job 7 | ✓ |
| RWA freeze cascade | Pool position mgmt Q7 + edge case | ✓ |

**CA operator loss vectors (current coverage)**:

| Loss vector | Where surfaced | OK? |
|---|---|---|
| Liquidation | CA mgmt Q1 | ✓ |
| HF drift | CA mgmt Q1, sub-job 4 attribution | ✓ |
| LT ramp cliff | CA mgmt sub-job 6 + edge case | ✓ |
| Safe-pricing kick-in | CA mgmt edge case + Tier 1 vocab | ✓ |
| Quota rate bleed | CA mgmt sub-job 5 (borrow-rate spread) + edge case | ✓ |
| Delayed-withdrawal clog | CA mgmt edge case + sub-job 9 | ✓ |
| CM expiration | CA mgmt edge case | ✓ |
| RWA freeze / KYC revocation | CA mgmt sub-jobs 17–18 + edge cases | ✓ |
| Oracle staleness at wrong moment | CA mgmt sub-job 7 + edge case | ✓ |

Personas → JTBD coverage is structurally complete on both sides, with one partial item (LP underlying depeg).

### Step 4 — Run the highlight grep (the doc test suite)

```bash
grep -rn "==note:\|==resolved_note:" \
  /Users/ilya/ai-assistant/projects/front-knowledge-base/ \
  --include="*.md"
```

What you should see:

- **JTBDs**: 4 highlights remaining, all genuine open questions:
  - Multi-position §3 scope question (`==is it necessary?==`)
  - CA Opening borrowable-liquidity UX question (`==note: could be an alert if low or 0, otherwise redundant==`)
  - CA management `==PNL==` minor wording flag
  - Pool position mgmt "list of new CMs" design question
- **Tier 1**: a few notes in `Data requirements`; inline highlights in `Personas` if any (Personas was modified pre-session — worth a separate skim).
- **Tier 2 `Entry points.md`**: 4 unresolved agent-related notes (persistent state, agent autonomous Decision sessions, agent emergency protocol, agent-whitelist vs scoped-bot disambiguation). Genuine cross-cutting open questions that would benefit from being promoted to Data requirements eventually.

If a highlight surprises you (you can't tell whether it's intentional vs forgotten), flag it: either resolve, promote to Data requirements, or convert to `==resolved_note: …==` with the inline answer.

### Step 5 — Spot the cross-doc contradictions

Run the obvious greps:

```bash
# HF threshold consistency
grep -rn "HF" /Users/ilya/ai-assistant/projects/front-knowledge-base/ --include="*.md" \
  | grep -E "1\.0[0-9]|1\.[1-9]"

# Field-name consistency
grep -rn "PoolOpportunity\.\|StrategyOpportunity\.\|EventFeedItem\|GovernanceChange\|CuratorProfile" \
  /Users/ilya/ai-assistant/projects/front-knowledge-base/ --include="*.md"
```

Flag where the same numeric threshold appears with different values, or where the same field name appears in inconsistent forms.

## Known residual smell (deferred — not silent)

Two things did not get patched in the 2026-04-29 session that the new-PM trace will trip over:

1. **F/E/S sections still missing** in `Pool position mgmt`, `CA management`, and `Multi-position` JTBDs. The skeleton-conformance issue means a new reader sees three of five JTBDs missing the same two table sections (Functional / Emotional / Social dimensions, and Decision criteria) that the other two have. Item 5 in the 2026-04-29 plan, deferred.
2. **The wikilink graph is partial** — Tier 1 is wikilinked from where it gets used in 2026-04-29's edits, but the JTBD main-job statements still don't say "Persona: `[[Personas and audience#Pool LP]]`", and the Tier 4 user flows don't wikilink the JTBDs they satisfy. Item 6 in the 2026-04-29 plan, deferred.

Both are deferred-on-purpose, not forgotten.

Other known gaps surfaced by the audit but deferred:
- CA Opening leverage/HF criterion struck through with no replacement (item 4)
- CA management Tim appendix unintegrated (lines 64–101 of `Credit Account management - JTBD.md`) (item 3)
- Cross-position aggregation rules absent in Multi-position (item 7)

## Cross-references

- `CLAUDE.md` — operating contract, semantic-scheme rules, ripple rules.
- `.planning/codebase/ARCHITECTURE.md` — full conceptual model.
- `.planning/codebase/STRUCTURE.md` — full directory tree with per-file annotations.
- `.planning/codebase/CONCERNS.md` — content-concern register.
- `.planning/foundation/glossary-inventory.md` — what was in the glossary before the 2026-04-29 expansion.
- `.planning/foundation/plan.md` — the foundation-building implementation plan.
- `.planning/foundation/tier-2-gap-research.md` — Tier 2 research that informed the Decision-making loop folder relocation.
