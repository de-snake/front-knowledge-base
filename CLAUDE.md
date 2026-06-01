# CLAUDE.md

This file is the operating contract for any agent (human or AI) editing the vault. It captures: what each file is, why it exists, what its conventions are, and what triggers an edit. Read this before touching any file you haven't edited recently.

## What this repo is

An **Obsidian vault** of Gearbox product-thinking docs (no code, no build, no tests). Content covers user research, the canonical decision-making loop, persona-scope flows for the front-end of the Gearbox protocol, and UI-primitive drafts. Both humans and LLM agents consume the same data schema; only ranking, surface, and tone diverge between them.

## Mechanical layout

```
front-knowledge-base/
├── *.md                          Tier 1 + Tier 2 + build-facing bridge files (top level — flat, by deliberate choice)
├── user-flows/                   Tier 3 files (post-merge — collapsed JTBDs + user flows)
│   ├── Pool deposit.md
│   ├── Pool deposit - reference.md   (sibling drill file)
│   ├── Pool monitoring.md
│   ├── Pool monitoring - reference.md
│   ├── Credit Account opening.md
│   ├── Credit Account opening - reference.md
│   ├── Credit Account monitoring.md
│   ├── Credit Account monitoring - reference.md
│   └── RWA leverage.md               (RWA overlay, not a separate product universe)
├── ui-primitives/                Tier 4 — .docx working drafts (not markdown by deliberate choice)
├── Assets/                       Obsidian attachment folder (set in .obsidian/app.json)
├── README.md                     Hand-maintained TOC
├── CLAUDE.md                     This file
├── .planning/foundation/         Foundation-level planning and merge artifacts
└── .obsidian/                    Obsidian vault config — don't edit unless explicitly asked
```

The legacy `JTBDs/` and `User flows/` folders have been removed after the post-merge flow docs became canonical. If old source material is needed for archaeology, use git history or `.planning/` artifacts; do not recreate legacy folders.

`README.md` uses URL-encoded standard-markdown links (Obsidian renders them correctly outside the vault); body docs use wikilinks (`[[Note#Anchor]]`). The README's canonical sections point to top-level docs and `user-flows/`; deleted legacy folders are not listed as navigation.

## Tier model (4-tier, post-merge)

The vault is a four-tier dependency graph. Edges only go downward (Tier N depends on Tier N-1). Earlier docs may still reference a 5-tier model — that's pre-merge state.

| Tier | Role | Folder |
|---|---|---|
| 1 | **Foundations** | top-level `.md` |
| 2 | **Decision-making loop scaffolding + build-facing contracts** | top-level `.md` |
| 3 | **Persona-scope flows** (post-merge: absorbs old Tier-3 JTBDs + Tier-4 user flows) | `user-flows/` |
| 4 | **UI primitives** (was Tier 5 pre-merge) | `ui-primitives/` |

Cross-cutting concerns (RWA / Securitize, agent-as-LLM-reader) are not separate tiers — they appear as labelled extensions inside Tier 1 and Tier 3 wherever they apply. `user-flows/RWA leverage.md` is the RWA-specific overlay on the Credit Account flows, not a separate product universe. The schema is unified; only the surfacing differs.

## File-by-file catalog

Each entry uses the same template: **Scope** (what's in it), **Purpose** (why it exists distinct from siblings), **Conventions** (structural rules specific to this file), **Mutates when** (edit triggers + out-of-scope), **Depends on / depended on by**.

### Tier 1 — Foundations

#### `Basic info and definitions.md`

**Scope.** Shared vocabulary: Credit Account, Collateral, Underlying token, IRM, yield sources, the canonical six-stage loop (`Discover → Analyze → Propose → Preview → Execute → Monitor`), and Pool / CA / RWA vocabulary tables (HF, LT, LT ramp, Quota, Safe pricing, Phantom token, etc.).

**Purpose.** Single source of truth for terminology. Every Tier 2/3/4 doc that uses a defined term should wikilink here rather than re-define.

**Conventions.**
- Each defined term gets a `## Term` heading and a definition paragraph. Sub-vocabularies use 3-col tables (`Term | Definition | Used in`).
- The canonical-loop stage names (`Discover`, `Analyze`, `Propose`, `Preview`, `Execute`, `Monitor`) are referenced verbatim throughout the vault — they are not aliased or re-cased.
- Yield sources use a 3-col table (`# | Source | Description`).

**Mutates when.**
- A new term is needed by a Tier 3 doc and doesn't exist yet (wikilink-first design — define here, then reference downstream).
- An existing term's mechanics shift (e.g., new oracle category, new Quota mechanic).
- Out of scope: per-flow stage logic, persona traits, threshold values — those belong in Tier 2/3 docs.

**Depends on / depended on by.**
- Upstream: external Gearbox protocol docs (informally; not wikilinked).
- Downstream: every other Tier 1 doc; all Tier 2 / 3 docs; some Tier 4 primitives.

#### `Personas and audience.md`

**Scope.** Two personas (Pool LP, CA operator) with sub-profile rows, plus per-persona loss-vector tables ranked by priority (P1 / P2). Mentions the agent (LLM) reader as a profile sub-type for both personas.

**Purpose.** Single source of truth for *who the user is* and *what they care about*. Every Tier 3 flow doc derives its Q-set, exit gates, and tier assignments from the loss vectors here. No Tier 3 doc should invent a concern not traceable to a vector here.

**Conventions.**
- Per persona: name + headline sentence + sub-profile sub-table (`Profile | Description`) + Loss-vectors table (`Vector | Mitigation strategy & comments | Priority`).
- Priority ∈ {`1`, `2`}. P1 = baseline concern for every user (incl. noobs); P2 = professional-tier concern.
- Russian voice notes preserved as blockquotes.

**Mutates when.**
- A new persona type emerges (rare).
- A new loss vector is identified (e.g., RWA introduced compliance-overlay losses; new strategy archetypes may add new vectors).
- Priority ranking shifts after incident analysis.
- Out of scope: data fields, UX details, agent-side computation logic — these belong in Tier 3.

**Depends on / depended on by.**
- Upstream: `Basic info and definitions.md` (terminology — HF, liquidation, oracle, IRM, etc.).
- Downstream: every Tier 3 flow doc cites loss vectors from here in each Q's `Why this matters` opener.

#### `Benchmarks and tresholds for metrics.md`

**Scope.** Green / yellow / red threshold tables for ongoing-ownership criteria — one table per persona (Pool, CA). Each row = one criterion + threshold bands + (CA only) Overview-or-advanced tag.

**Purpose.** Threshold reference for Stage 6 (Monitor) sections of flow docs and for the Glance / Analyze split in `Three-layer progressive disclosure.md`. Decouples threshold values from the flow narrative so threshold tweaks don't ripple across multiple files.

**Conventions.**
- Filename typo (`tresholds` → should be `thresholds`) is **preserved on purpose** — renaming would break every wikilink that targets it.
- Tables use 4-col shape (`Criterion | Green | Yellow | Red`) for Pool; 5-col for CA (adds `Overview or advanced`).
- `==note:==` and `==resolved_note:==` markers preserved verbatim.

**Mutates when.**
- A monitoring criterion shifts (e.g., HF threshold changes from 1.1 to 1.07 — this kind of resolution should land here, not inside a flow doc).
- A new criterion is added (e.g., new RWA dimension).
- Out of scope: defining what the criteria mean — that's terminology (Tier 1) and per-Q logic (Tier 3).

**Depends on / depended on by.**
- Upstream: `Basic info and definitions.md` (definitions of HF, LT, etc.).
- Downstream: Stage-6 sections of flow docs cite these bands; `Three-layer progressive disclosure.md` derives Glance verdict candidates from the `Overview` rows.

#### `Data requirements and to-dos.md`

**Scope.** Backend / SDK punch-list — endpoints, feeds, components, and primitives that flow docs need but don't yet exist. One row per gap: area + description + notes.

**Purpose.** Exhaust, not input — aggregates concrete gaps from downstream product-flow docs into a backend punch list. Read by humans deciding what to build next. User / agent preference persistence is not Gearbox-side scope; if those values appear here, they are runtime inputs supplied by the user or representative agent.

**Conventions.**
- 3-col table (`Area | Description | Notes`).
- Gaps land here when a Tier 3 doc surfaces a missing field with `==note: ...==`. The note can be promoted to this table once the gap is concrete enough to act on.

**Mutates when.**
- A flow doc surfaces a new backend gap.
- An existing gap is shipped (move to a "shipped" section or remove).
- A gap's scope is refined (e.g., field shape clarified, dependencies added).
- Out of scope: implementation detail beyond what the flow doc needs to know.

**Depends on / depended on by.**
- Upstream: `==note:==` markers across all Tier 3 docs.
- Downstream: build / backend-design teams read this to plan work; informally feeds back into Tier 3 once gaps ship.

### Tier 2 — Scaffolding

#### `Entry points.md`

**Scope.** Names the **session-mode axis** — three different entry shapes (Decision / Monitoring / Emergency) over the same canonical loop. Notes that Monitoring branches into ownership sub-shapes without creating a placeholder cross-position flow.

**Purpose.** Tier 1 says the loop has six stages; this doc says there are three different ways to enter and walk them. Sets up the agent-as-LLM-reader's default-monitoring traversal contract.

**Conventions.**
- Opens with a wikilink to `[[Basic info and definitions#Canonical loop]]` (Tier 2 → Tier 1 derivation pattern).
- Modes presented as a 2-col table (`Mode | Description`).
- The Monitoring → ownership-session-type refinement (Confirmation / Analysis / Action / Exit / Reallocation) lives here in name only; a cross-position flow should be added only when it is complete enough to be canonical.

**Mutates when.**
- A new session mode is identified (rare — the three are stable).
- The Monitoring branch refinement changes shape.
- The agent-handoff line (currently Execute) shifts.
- Out of scope: per-flow stage logic, threshold values.

**Depends on / depended on by.**
- Upstream: `Basic info and definitions.md` (canonical loop), `Personas and audience.md` (agent profile sub-type).
- Downstream: every Tier 3 flow doc references session modes; `Three-layer progressive disclosure.md` is the orthogonal axis to this one.

#### `Three-layer progressive disclosure.md`

**Scope.** Per-screen / per-agent-reply organisation: `Glance / Analyze / Act`. Three layers describing how a single screen or agent response should be structured, orthogonal to the six-stage loop.

**Purpose.** Loop = decision lifecycle (across time). Three-layer = single-screen organisation (within a moment). Both axes apply to every flow doc.

**Conventions.**
- Glance content per persona uses 3-col tables (`Layer | Content | Source`) where the source column wikilinks back to the Tier 3 sub-jobs that ground each Glance verdict.
- The Pool-side and CA-side splits mirror the persona split in Tier 1.

**Mutates when.**
- A new Glance verdict is identified for a persona.
- The Benchmarks-as-Glance-source convention shifts.
- The agent-vs-human surfacing distinction changes.
- Out of scope: per-flow stage logic.

**Depends on / depended on by.**
- Upstream: `Personas and audience.md`, `Basic info and definitions.md` (canonical loop), `Benchmarks and tresholds for metrics.md` (Overview rows = Glance candidates).
- Downstream: Tier 3 monitoring flows use this for Stage-6 surface design; Tier 4 UI primitives implement the layering.

### Build-facing contract bridge

#### `Data contracts.md`

**Scope.** Product-level contract registry for stage handoffs, source ownership, and protocol-vs-product-vs-external-data boundaries.

**Purpose.** Bridges user-flow logic to backend / SDK implementation without pushing contract names into product-facing flow copy.

**Mutates when.** A flow introduces a new stage handoff, data source, required field, or source-boundary rule. Backend-only lookup hints still belong in `Data requirements and to-dos.md`.

#### `Preview contract.md`

**Scope.** Stage 4 Preview contract: before/after state, warning severity, pass/fail rules, integrity binding, emergency preview, and RWA compliance extension.

**Purpose.** Makes Preview the hard execution gate between Propose and Execute.

**Mutates when.** A new action class, warning class, approval mode, or preview failure route is added.

#### `Agent execution boundaries.md`

**Scope.** Permission boundary for read-only analysis, proposals, previews, human-in-the-loop execution, delegated bot execution, emergency mode, and RWA/compliance-gated actions.

**Purpose.** Defines what the agent can do alone, what needs explicit approval, and what must be blocked.

**Mutates when.** Bot policy, emergency behavior, RWA execution constraints, or action-class approval modes change.

### Tier 3 — Persona-scope flows

The post-merge tier. One file per (persona × lifecycle scope), plus a sibling reference file for drill content.

| Flow | Persona | Scope | Status |
|---|---|---|---|
| `Pool deposit.md` + `Pool deposit - reference.md` | LP | Entry | **Canonical example — done** |
| `Pool monitoring.md` + `Pool monitoring - reference.md` | LP | Monitoring | **Convention pass complete — matches Pool deposit shape** |
| `Credit Account opening.md` + `Credit Account opening - reference.md` | CA operator | Entry | **Drafted — convention-aligned with Pool deposit** |
| `Credit Account monitoring.md` + `Credit Account monitoring - reference.md` | CA operator | Monitoring | **Drafted — convention-aligned with Pool monitoring; CA-specific Emergency-mode branch** |
| `RWA leverage.md` | CA operator / RWA LP overlay | RWA extension | **Overlay for tokenized-security / issuer-controlled collateral paths; not a separate product universe** |

#### `user-flows/Pool deposit.md`

**Scope.** End-to-end flow doc for a Pool LP entering a deposit position. Stages 1 → 5 (Discover → Execute) plus hand-off to `Pool monitoring.md` at Stage 6.

**Purpose.** Canonical example of the post-merge flow-doc pattern. Other Tier 3 flow docs replicate its structure. When in doubt about how a section should be shaped, check this file.

**Conventions.**
- Stage layout: Stage 1 (Discover, I/C/O), Stage 2 (Analyze, Q1–Q5), Stage 3 (Propose, IC analogy), Stage 4 (Preview, Execution Desk pre-trade), Stage 5 (Execute).
- Each Q in Stage 2: `Exit gate` → `Why this matters` (opens with Personas loss vector + wikilink) → computation table → synthesis row.
- Computation table baseline shape: `Sub-question | Tier | What the agent does | Data retrieved`. Q-specific extensions add columns (`Lens` for Q3, `Aggregation` for Q4) or restructure (Q5 change-watch shape: `Change type | Classification | Re-evaluates / effect | Scope | Event source`).
- T1 = default scope; T2 = extended scope. Tier ≠ priority (priorities live in Personas).
- Synthesis row: prose in the descriptive "what" column; `—` in others.
- Drill content (>5 lines) lives in `Pool deposit - reference.md`; main-file row links via `[[Pool deposit - reference#Drill — X|drill ↗]]`.
- `==note:==` and Russian voice notes preserved verbatim, never deleted in restructuring passes.

**Mutates when.**
- Personas adds a new LP loss vector → new Q or new row in an existing Q.
- Personas changes a priority → row tier reassignment + exit-gate rephrase.
- Backend / SDK schema gap discovered → `==note:==` flag inline; aggregates upward to `Data requirements and to-dos.md`.
- A drill exceeds main-file scannability (>5 lines in a table cell) → externalize to reference file.
- Out of scope: recreating deleted legacy `JTBDs/` or `User flows/` files; editing UI primitives (those follow flow docs, not lead).

**Depends on / depended on by.**
- Upstream: `Personas and audience.md` (loss vectors), `Basic info and definitions.md` (terminology), `Benchmarks and tresholds for metrics.md` (thresholds for the Stage 6 hand-off), `Entry points.md` + `Three-layer progressive disclosure.md` (session-mode framing).
- Downstream: `Pool monitoring.md` (Stage 6 hand-off via back-edge), `Pool deposit - reference.md` (sibling drill file), Tier 4 UI primitives `LenderDetails.docx` (Discover → Preview) and `LenderPosition.docx` (Monitor + Act).

#### `user-flows/Pool deposit - reference.md`

**Scope.** Drill content too long for main-file table cells: oracle taxonomy, Steakhouse 3-layer framework, curator-pillar drills, IC decision palette.

**Purpose.** Keeps `Pool deposit.md` table-scannable; provides flow-agnostic anchor names so future flow docs (CA opening, monitoring) can link to the same drills without duplication.

**Conventions.**
- Heading style: flat `## Drill — <topic>` (no `T1` / `T2` prefix — tier lives on the calling row in the main file's table).
- Topic names are **flow-agnostic** (e.g., `Drill — Curator identity & governance`, not `Drill — Q4 Curator`). Future flow docs reuse the same anchors.
- Each drill is a self-contained explanatory unit; the main file's table cell carries only the verdict-level summary plus the wikilink.

**Mutates when.**
- A new drill is added (a main-file table row gains drill content >5 lines).
- A drill is refined (e.g., new historical anchor, new mechanism explanation).
- Topic-naming changes (requires updating all wikilinks in main file — sweep before renaming).
- Out of scope: anything that belongs in the main file's table (verdict-level content).

**Depends on / depended on by.**
- Upstream: `Pool deposit.md` (drives content additions).
- Downstream: future flow docs (CA opening, monitoring) may link to the same anchors — confirm anchor stability before refactoring drill names.

#### `user-flows/Pool monitoring.md`

**Scope.** LP Monitoring flow. Full canonical-loop traversal in monitoring-mode order: **Stage 6** (Monitor entry, Q1–Q5 default + Q6 drill + Q7 RWA conditional, with I/C/O framing) → **Stage 2** (Analyze focused re-run, drift → Pool-deposit-Q mapping) → **Stage 3** (Action Committee — top-up / partial exit / full exit for the existing position) → **Stage 4** (Preview, deposit + withdrawal previews) → **Stage 5** (Execute, HITL or bot). Plus: Job statement, F/E/S dimensions, Edge cases.

**Purpose.** The recurring ownership job an LP performs on every return visit. Different shape from Pool deposit (this is a Monitoring-mode entry point per Tier 2; Pool deposit is a Decision-mode entry point), but applies the same Stage I/C/O convention and Q-deep-dive convention — Pool deposit Stage 2 and Pool monitoring Stage 6 share the table shape, tier system, and synthesis-row pattern; Pool monitoring Stages 2 / 3 / 4 / 5 share the I/C/O Stage shape with Pool deposit's same-numbered stages, scoped to single-position drift response.

**Conventions.**
- Stage layout follows the canonical loop: Stage 6 (entry) → Stage 2 (focused re-run, when triggered) → Stage 3 (Action Committee) → Stage 4 (Preview) → Stage 5 (Execute). Each stage uses the same Sub-jobs / Exit gate / User's goal / Inputs / Compute / Outputs framing as Pool deposit's stages.
- Stage 2 in monitoring is **focused re-run** (not full Analyze) — re-runs only the affected Pool-deposit-Q(s) per the drift → Q mapping table; outputs `FocusedAnalyzeReport` with `position_thesis_verdict`. The Pool-deposit-Q deep-dive logic is not duplicated here — Stage 2 references it via wikilink.
- Stage 3 in monitoring is the **Action Committee** for one existing position — distinct from Pool deposit Stage 3's **Investment Committee** which allocates across multiple candidates. No reserve concept; outputs a single-action `ActionDecision`. LPs do not have an Emergency action class. Cross-pool reallocation is outside this single-position flow.
- Stage 4 in monitoring covers **both deposit (top-up) and withdrawal (exit) previews** — withdrawal-specific fields (price impact at exit size, in-flight rewards forfeited, time-to-fill estimate, withdrawal fee) are added to the `TransactionPreviewReport` shape. Top-up case delegates directly to Pool deposit Stage 4 via wikilink.
- Stage 5 in monitoring is identical to Pool deposit Stage 5 in shape (HITL or bot, integrity gate). Hand-off back to Stage 6 with the agent updating `agentLog.previousCheck` to reflect post-action state.
- Each Q in Stage 6: `Exit gate` → `Why this matters` (opens with Personas loss vector + wikilink) → computation table → synthesis row. Same convention as Pool deposit Stage 2.
- Computation table baseline shape: `Sub-question | Tier | What the agent does | Data retrieved`. Q5 (bad-debt canary) and Q7 (RWA) use the same baseline shape — no Q-specific extensions needed for monitoring.
- T1 / T2 tiering: T1 runs every monitoring call; T2 fires when the LP is sophisticated, a T1 verdict flipped, or a known structural risk warrants persistent T2 coverage.
- Synthesis row: prose in the descriptive "what" column; `—` in others. Each synthesis names the back-edge target (which Pool deposit Q gets re-run on drift).
- Verdict-only Stage 6 output: each Q resolves to a green / yellow / red verdict against [[Benchmarks and tresholds for metrics#Pool-related|Benchmarks]]; deep analysis lives in Pool deposit Stage 2 via the back-edge.
- **Inputs are carry-overs + user-config only** (matches Pool deposit Stages 1/2 convention): `Position id` (handoff handle) + `User thesis / criteria` (forward-looking gates). Compute-time data sources — pool current state (backend, re-fetched per call) and agent continuity log (user / agent-side state) — are described in the Compute prose, not in the Inputs table.
- **Sunk-cost-blind monitoring.** Stage 6 verdicts are anchored to forward-looking thesis criteria (the user's `floorApy`, accepted oracle methodologies, accepted curator profile, hold horizon) and to the agent's own continuity log (`agentLog.previousCheck.{...}`) for delta detection. There is no `EntryBaseline` backend snapshot — entry-time pool conditions are not the gate; "what would the LP accept entering today?" is. Each Q phrases its sub-Qs accordingly: "vs floor / vs current criteria" (forward-looking) and "since last check" (agent-log delta) — never "vs entry."
- **Q-level firing is gated by Personas priority.** P1-mapped Qs (Q1–Q5: yield, exit, composition, governance, bad-debt) run on every monitoring call with at least one T1 sub-Q each. P2-mapped Qs are conditional: **Q6** (oracle, P2) is all-T2 — fires as a drill when Q5 canary flagged, Q3 detected new top-3 collateral, the LP is sophisticated, or the pool has known structural oracle risk on dominant collateral. Oracle is also explicitly excluded from the Pool LP Glance set in [[Three-layer progressive disclosure]], reinforcing the drill positioning. **Q7** (RWA, P2) is conditioned at Q-level by "RWA pools only"; once Q7 fires, T1/T2 split inside operates normally. The MonitoringSnapshot output type marks `q6_oracle` and `q7_rwa` as optional accordingly.
- Methodology / acceptability splits: where a sub-Q conflates *change detection* with *acceptability gate* (e.g., Q6 oracle methodology change), split into two rows — one for delta-detection (against agent log), one for the forward-looking gate (against user thesis).
- Reference sibling file (`Pool monitoring - reference.md`) holds three drills: **LP action-class palette** (Stage 3 synthesis content — mirrors Pool deposit's IC palette drill), **Q6 oracle drill triggers** (the four firing conditions for Q6 + when Q6 is skipped), **Agent continuity log mechanics** (`previousCheck` schema, per-Q delta usage, first-call rule, user / agent-side persistence boundary).
- Q-numbering is monitoring-specific (Q1 yield → Q2 exit → Q3 composition → Q4 governance → Q5 bad-debt → Q6 oracle → Q7 RWA) and does NOT correspond 1:1 to Pool deposit Q-numbering. The back-edge mapping table makes the cross-reference explicit.
- `==note:==` and Russian voice notes preserved verbatim, never deleted in restructuring passes.

**Mutates when.**
- A new monitoring question is identified (e.g., a new RWA dimension).
- A drift signal needs a new Q-mapping after a Pool deposit Q is added or restructured (back-edge table updates).
- Personas adds a new LP loss vector → new Q or new row in an existing Q.
- A Stage-6 sub-Q grows drill content > 5 lines → externalize to a new `Pool monitoring - reference.md`.
- Out of scope: editing pre-deposit Q1–Q5 logic in Pool deposit — that's Pool deposit's job; introducing fresh due-diligence logic that doesn't exist upstream — Stage 6's job is verdict-on-delta, not greenfield analysis.

**Depends on / depended on by.**
- Upstream: `Pool deposit.md` (back-edge target — must stay in sync; back-edge table maps each monitoring Q to one or two Pool deposit Qs), `Personas and audience.md` (LP loss vectors), `Benchmarks and tresholds for metrics.md` (Pool ownership thresholds — the green / yellow / red bands), `Entry points.md` + `Three-layer progressive disclosure.md` (session-mode + Glance-layer framing).
- Downstream: Tier 4 `LenderPosition.docx` (Monitor + Act primitive).

#### `user-flows/Credit Account opening.md` + `user-flows/Credit Account opening - reference.md`

**Scope.** End-to-end flow doc for a CA operator opening a leveraged Credit Account. Stages 1 → 5 (Discover → Execute) plus hand-off to `Credit Account monitoring.md` at Stage 6. Reference holds CA-specific drills (IRM curve sensitivity, structural risk taxonomy, RWA compliance layers, adapter routing constraints, CM operational envelope, KYC-gated execution path, IC decision palette + route selection, multicall preview mechanics). Reuses Pool deposit's reference for flow-agnostic curator + oracle drills.

**Purpose.** CA-side counterpart to Pool deposit. Same I/C/O Stage shape and Q-deep-dive convention, with CA-specific extensions: (a) **Stage 1 is shared with Pool deposit** — same 2-input shape (asset class + floor APY), agent searches across both `PoolOpportunity` and `StrategyOpportunity`, this doc continues for strategy candidates only; (b) target leverage / HF floor / hold horizon are **agent-derived at Stage 2** per candidate (not user-supplied at Stage 1) per Personas' "minimalist user input" preference and "agent-driven technical parameters" trait; (c) Stage 2 Q-set covers HF feasibility, LT-ramp horizon, oracle methodology + safe-pricing exit HF, RWA compliance layer, and CM expiration horizon — multiple P1 vectors converge on Q2; (d) Stage 3 IC adds **Route Selection** (adapter set, slippage tolerance, max-price-impact budget) because the underlying → collateral entry swap is non-trivial; (e) Stage 4 Preview simulates a multicall (open + borrow + entry swap), not a simple deposit; (f) Stage 5 routes through `SecuritizeKYCFactory → SecuritizeWallet → CreditFacade` for KYC-gated CMs and blocks bot signers there.

**Job statement framing.** Reframed away from "user has a thesis on a specific yield-bearing collateral" — the actual job is "earn yield on preferred asset type; comfortable with whatever strategy passes analysis." The user may arrive with a specific collateral in mind, but is equally well-served by "show me strategies on USD-stables that clear 8 % net APY at acceptable risk." Stage 2's analysis gates the open; Stage 1 surfaces candidates regardless.

**Conventions.**
- Same I/C/O / Q-shape / synthesis-row conventions as Pool deposit. Action-class enum is snake_case (`open_ca, adjust_leverage, rebalance, skip, no_op`) for parity with Pool monitoring's snake_case action vocabulary.
- Q1 (economics) carries a T1 utilisation-headroom + borrow-rate-trend sub-Q in addition to the T2 IRM curve sensitivity drill — covers the P1 yield-decay loss vector at default scope. Drill goes deeper for sophisticated users.
- Q2 (collateral safety) uses Lens shape (Asset / Gearbox config / Oracle / Structural / Platform-RWA). The Steakhouse 3-layer drill in Pool deposit reference is reused as Lens-Steakhouse T2.
- Q4 (curator / CM) splits "CM operational envelope" (paused + maxDebtPerBlockMultiplier + facade pause) from "CM expiration horizon" (expirable CMs only) as separate T1 sub-rows because expiration is a P1 loss vector with a horizon-comparison gate, not just an envelope state.
- Curator Identity / Operational track record / Liquidity-incident history / Design discipline drills wikilink to `Pool deposit - reference` directly — flow-agnostic, no duplication.
- KYC-gated execution path constraint surfaces at Stage 3 (route selection), not just Stage 5 — prevents bot-delegation-impossible Stage 5 surprises.
- Markers preserved verbatim: legacy CA opening user-flow `==note:==` / `==resolved_note:==` / `==phrase==` markers are absorbed into the corresponding Q-table cells.

**Mutates when.**
- Personas adds a new CA loss vector → new Q or new row in an existing Q.
- A new oracle methodology / asset class / adapter routing constraint is identified.
- A new pre-open backend gap surfaces → `==note: ...==` flagged inline; aggregated upward to `Data requirements and to-dos.md`.
- A drill exceeds main-file scannability (>5 lines in a table cell) → externalize to reference file.
- KYC-gated CM mechanics shift (e.g., new `SecuritizeWallet` capabilities) → update Q4 KYC-gated row + Stage 5 routing note.
- Out of scope: recreating deleted legacy `JTBDs/` or `User flows/` source files.

**Depends on / depended on by.**
- Upstream: `Personas and audience.md` (CA loss vectors), `Basic info and definitions.md` (CA vocabulary — HF, LT, LT ramp, Quota, Safe pricing, Phantom token, CM, Forbidden tokens, Liquidation premium, Multicall, IRM bands, TWV), `Benchmarks and tresholds for metrics.md` (CA-related thresholds), `Entry points.md` + `Three-layer progressive disclosure.md` (session-mode + Glance framing), `Pool deposit.md` (Stage 3 / Stage 5 patterns reused).
- Downstream: `Credit Account monitoring.md` (Stage 6 hand-off via TransactionConfirmation; Stage 2 back-edge target; Q1–Q5 deep-dive references); Tier 4 `StrategyDetails.docx` (Discover → Preview).

#### `user-flows/Credit Account monitoring.md` + `user-flows/Credit Account monitoring - reference.md`

**Scope.** CA-side monitoring flow. Full canonical-loop traversal in monitoring-mode order: Stage 6 (Monitor entry, Q1–Q5 default + Q6 oracle drill + Q7 RWA conditional) → Stage 2 (Analyze focused re-run) → Stage 3 (Action Committee, 11+ action classes incl. Emergency variants and bot management) → Stage 4 (Preview, per-action-class multicall simulation) → Stage 5 (Execute). Plus: Job statement, F·E·S, **Cost of doing nothing** section (CA-specific — bleeds on autopilot), Edge cases. Reference holds CA action-class palette, Emergency mode contract, HF movement attribution, Q6 oracle drill triggers, Agent continuity log mechanics for CA.

**Purpose.** CA-side counterpart to Pool monitoring. Same architectural conventions (sunk-cost-blind, agent continuity log, T1/T2 sub-Q tiering, P1/P2 Q-level firing, focused re-run at Stage 2, Action Committee at Stage 3) with CA-specific extensions: (a) **Five session-mode branches** — Confirmation, Analysis, Action, Exit, **Emergency** (vs Pool monitoring's four); (b) **Emergency override** — when Stage 6 Q1 verdict crosses HF < 1.1, hand-off skips Stage 2 and goes directly to Stage 3 with the ≤ 2-clicks contract; (c) **Cost of doing nothing** as a top-of-doc section because CA bleeds (borrow + quota + unclaimed-rewards + HF drift + expirable CMs) — Pool LP doesn't bleed; (d) **11+ action classes** (add_collateral, reduce_leverage, increase_leverage, partial_exit, full_exit, change_strategy, rebalance, claim_rewards, enable_bot / disable_bot / adjust_bot_threshold, plus emergency variants) vs Pool monitoring's 3 (top_up, partial_exit, full_exit); (e) **Plain-language pairs** for Q1 + Q2 metrics (HF, liquidation-distance, time-to-liquidation, net APY, total return, spread); (f) **Q1 and Q2 are the named Glance set** per [[Three-layer progressive disclosure]] (vs Pool LP's 5-verdict Glance set).

**Conventions.**
- Same Stage-layout / Q-shape / I/C/O / synthesis-row / sunk-cost-blind / user / agent-side agent-continuity-log conventions as Pool monitoring. Q-level firing gated by Personas priority.
- Q1 carries **plain-language translation pairs** for every raw metric (HF, Liquidation Price, Time to liquidation, Virtual liquidations) per [[Personas and audience#CA operator (leveraged user)|Personas]]'s "agent must explain HF movement within one cycle" requirement. Same principle applies to Q2 (Net APY, total return, spread).
- Q1's exit gate explicitly invokes Q7 frozen-status override — when the CA is frozen, the safety verdict cannot be green regardless of HF.
- Q3 schema in the agent continuity log includes `oracleSet` so that Q6's drill trigger ("new token added with unfamiliar oracle") has a comparison baseline.
- Q5 includes a `Partial-exit feasibility under minDebt` T1 sub-Q so that the Stage 3 sizing logic for `partial_exit` doesn't surprise the user with "your partial exit is gated to full exit by minDebt."
- Q6 oracle drill has a **proactive trigger** — "Per-token oracle approaching staleness window" per Benchmarks yellow band — so freshness-degradation is caught before liquidation, not just after.
- Stage 3 Action Committee operates on **11+ action classes** (vs Pool monitoring's 3) and supports composite / fallback flows (add-funds-with-leverage, step-by-step unwind, system-constraint fallback) documented in the action-class palette drill.
- Stage 4 Preview emergency-mode HF gate: post-action HF must improve over pre-action HF, with a partial-liquidation-bot exception (bot path raises HF in a small step that may not clear δ).
- Cross-position dedup at Stage 3 can surface the option to fund Emergency from another idle Credit Account's collateral, but the multi-CA reallocation case remains outside this single-position flow.
- Markers preserved verbatim from absorbed source notes attached to CA monitoring.

**Mutates when.**
- A new monitoring Q is identified (e.g., a new RWA dimension, a new operational mechanic).
- A drift signal needs a new mapping after a CA opening Q is added or restructured.
- A new action class is added to the palette (e.g., a new bot type) → update palette drill + Stage 3 compute table + Stage 4 per-action-class compute.
- Emergency-mode contract changes (≤ 2-clicks threshold, sizing logic, bot availability for first-time users).
- Personas changes a CA loss-vector priority → Q-level firing rule re-checked.
- A Stage-6 sub-Q grows drill content > 5 lines → externalize to reference.
- Out of scope: editing pre-open Q1–Q5 logic in CA opening — that's CA opening's job.

**Depends on / depended on by.**
- Upstream: `Credit Account opening.md` (back-edge target — must stay in sync; back-edge table maps each monitoring Q to one or two CA-opening Qs), `Personas and audience.md` (CA loss vectors), `Benchmarks and tresholds for metrics.md` (CA ownership thresholds — HF, HF trend, net APY hurdle, spread, LT ramp, forbidden-token overlap, oracle freshness, divergence, price impact, CM expiration, pause, parameter-change log, pending governance, RWA frozen, KYC validity, pending delayed withdrawals), `Entry points.md` + `Three-layer progressive disclosure.md` (session-mode incl. Emergency + Glance Q1 / Q2), `Pool monitoring.md` (architectural patterns reused — sunk-cost-blind, agent log, focused re-run, Action Committee).
- Downstream: Tier 4 `StrategyPosition.docx` (Monitor + Act primitive).

### Tier 4 — UI primitives

#### `ui-primitives/*.docx` (class-level entry — covered as a class, not per-file)

**Scope.** Per-screen / per-component design drafts — Word documents (`.docx`) by deliberate choice, the only non-markdown content folder in the vault. Two parallel families per persona (Lender* and Strategy*), plus shared primitives (`Opportunity.docx`, `Positions.docx`).

| File | Persona | Loop coverage |
|---|---|---|
| `Opportunity.docx` | Both | Discover (root list) |
| `LenderDetails.docx` | Pool LP | Discover → Analyze → Propose → Preview |
| `StrategyDetails.docx` | CA operator | Discover → Analyze → Propose → Preview |
| `Positions.docx` | Both | Monitor (dashboard) |
| `LenderPosition.docx` | Pool LP | Monitor + Act |
| `StrategyPosition.docx` | CA operator | Monitor + Act |

**Purpose.** Translates Stage-by-stage flow logic (Tier 3) into concrete UI surfaces backed by SDK shapes (`sdk.opportunities.*`, `sdk.positions.*`, `sdk.tx.preview()`). Introduces SDK contract conventions (method names, tab structures, position-extension hierarchy).

**Conventions.**
- Authored in Word on purpose — tables, screenshots, and embedded formatting that don't survive a flat-file conversion. Don't convert to markdown unless explicitly asked.
- Field names referenced inside a primitive must already exist in the matching Tier 3 flow doc. If a primitive needs a field that isn't named upstream, flag it with `==note: ...==` for promotion to `Data requirements and to-dos.md`.
- Position-extension hierarchy: `StrategyPosition extends Position`, `LenderPosition extends Position`.

**Mutates when.**
- Tier 3 stage logic changes → corresponding primitive must follow.
- A new SDK contract is introduced (rare; goes into the relevant Details / Position primitive).
- A new screen is needed → new `.docx` in the appropriate family + table-of-contents update.
- Out of scope: introducing a UI affordance with no corresponding Tier 3 criterion (that's a Tier 3 gap, not a Tier 4 invention); converting `.docx` to markdown.

**Depends on / depended on by.**
- Upstream: matching Tier 3 flow doc.
- Downstream: external implementation (front-end build).

### Index

#### `README.md`

**Scope.** Hand-maintained TOC. Lists every top-level document grouped by tier, with a one-line description per file.

**Purpose.** Human-curated surface view of the dependency graph. Entry point for newcomers to the vault.

**Conventions.**
- Uses **URL-encoded standard-markdown links** (`Basic%20info%20and%20definitions.md`), not Obsidian wikilinks. This is the only file in the vault using that link form — body docs use wikilinks.
- Description per file: one sentence, framing what the file does, not what's literally in it.
- Canonical sections point to top-level docs and `user-flows/`. Deleted legacy folders are not listed as navigation.

**Mutates when.**
- A top-level note is added, renamed, or removed.
- A top-level or canonical flow file is added, renamed, or removed.
- Out of scope: depth detail beyond one-liner per file.

**Depends on / depended on by.**
- Upstream: every top-level doc.
- Downstream: external readers (humans browsing the vault on GitHub or Obsidian's file panel).

## Convention catalog — flow-doc structural primitives

Rules that apply to every Tier 3 flow doc. Pool deposit is the canonical example.

### Scope-tier system (T1 / T2)

- `T1` = **default scope** — runs for every flow execution.
- `T2` = **extended scope** — runs only when (a) the user is sophisticated, or (b) a `T1` finding triggers drill-down.
- Tiering is a **research-depth control**, not a priority restatement. Priorities live in `Personas and audience.md` and are not duplicated into flow docs. The flow doc maps each P1 vector to at least one T1 row; rows that are mechanism breakdowns or structural / historical context are typically T2.
- Tiering applies at both the Q level (skip the Q entirely) and the sub-Q level (keep the Q but research it shallowly). Tier tags live in the table's Tier column; no `[T1]` / `[T2]` inline prose tags.

### Computation-table shapes

Baseline:

```
| Sub-question | Tier | What the agent does | Data retrieved |
```

Q-specific extensions:

- **Q3-style multi-lens grouping** adds a `Lens` column: `Dimension | Lens | Tier | What | Data retrieved`.
- **Q4-style aggregation pillars** add an `Aggregation` column: `Sub-section | Aggregation | Tier | What | Data retrieved`.
- **Q5-style change-watch** restructures entirely: `Change type | Classification | Re-evaluates / effect | Scope | Event source`. `Classification` ∈ {`material`, `info-only`}; `Scope` ∈ {`T1`, `T2`, `info`}.

### Synthesis-row placement

Each Q's table ends with a synthesis row:

- Column 1 (sub-question / dimension / etc.) = `**Synthesis**`
- The descriptive "what" column = the synthesis prose
- All other columns = `—`

Synthesis prose names what T1 covers vs what T2 adds when triggered. Replaces the legacy `**How the agent reasons.**` paragraph that earlier drafts placed after the table.

### Drill externalization

Any explanatory content that would exceed ~5 lines in a table cell goes to the sibling reference file under a flat `## Drill — <topic>` heading. The main-file table cell carries only the verdict-level summary plus a wikilink: `[[<flow> - reference#Drill — <topic>|drill ↗]]`.

Topic names are **flow-agnostic** (re-usable across flows). Heading prefix is just `Drill —`, never `T1 drill —` or `T2 drill —`.

### IC analogy at Stage 3

Stage 3 (Propose) uses Investment Committee framing. Decision-class table replaces prose. Palette mapping (`fund / split → "deposit"`, `skip → "skip"`, `hold-reserve → reserve_usd`, `no-op → all-skipped, reserve = capital`) lives in the synthesis row + a `Drill — IC decision palette` reference. Schema invariant: `total_deployed_usd + reserve_usd = available capital` (skipped candidates do not consume capital).

### I/C/O stage shape

For stages whose shape is data-pipeline (filter / transform / retrieve / surface):

- **Inputs** — what enters this stage (table)
- **Compute** — what the agent does (prose or table)
- **Outputs** — what hands off to the next stage (token / minimal contract, not a full data dump)

Currently used at Stages 1 (Discover) and 2 (Analyze top-frame). Stage 2 deep-dive uses Q-shape; Stages 3–5 use linear sections.

### Cross-stage progressive disclosure

Each stage operates on data **required AND sufficient** for its own job. Hand-off to the next stage is a minimal-contract token (e.g., Stage 1 → Stage 2 hands off only `Opportunity.id[]`, not full opportunity records). Subsequent stages re-fetch their own rich data given the hand-off. Demonstrated in Pool deposit Stage 1 → Stage 2.

### Stage 1 is unified across pool and CA flows

Stage 1 (Discover) operates on a **single unified opportunity surface** — `PoolOpportunity` and `StrategyOpportunity` together — with the same hard filters (asset class, chain, access) and the same soft-filter / ranking surface (composite or maxLeverage yield, operational health, sizing fit). Coarse reasoning may diverge slightly (strategies have a leverage axis; pools don't), but candidate filtering is mostly identical. **Stage 2 is where the path forks** — pool candidates flow into Pool deposit's LP due-diligence Q-set; strategy candidates flow into CA opening's CA due-diligence Q-set. Each entry-flow doc (Pool deposit, CA opening) describes its own Stage 1 inputs / compute / outputs; the unification is canonical and is named in [[Basic info and definitions#Canonical loop|Canonical loop]] — flow docs reference the convention rather than restating it. Implication for both flows: Stage 1 user inputs are **just two** (asset class + floor APY); strategy-specific user-config (target leverage, HF floor, hold horizon, position size) is agent-derived at Stage 2 per [[Personas and audience#CA operator (leveraged user)|Personas]] preference for minimalist user input.

### Marker preservation

`==note: ...==`, `==resolved_note: ...==`, `==phrase==` (no prefix), and Russian voice notes (blockquotes) are **always preserved verbatim**. Move with the section they're attached to; don't delete in restructuring passes; don't auto-clean grammar.

## Derivation rules

Concrete edges between tiers — what each downstream file is required to derive from upstream.

| Upstream input | Where it lands downstream | Rule |
|---|---|---|
| Tier 1 terminology | Wikilinks in Tier 2/3/4 | If a doc uses a term defined in Tier 1, wikilink the first usage. Don't redefine. |
| Personas loss vector | Each Q's `Why this matters` opener | Q's existence is justified by a Personas loss vector. Opener names the vector with wikilink to Personas. |
| Personas priority ranking | T1 vs T2 row assignments | At minimum: every P1 vector has one T1 row that addresses it. Mechanism / drill / structural rows can be T2. |
| Canonical 6-stage loop | Flow doc layout | Stages named verbatim (`Discover` / `Analyze` / `Propose` / `Preview` / `Execute` / `Monitor`). Stage headings use the middle-dot separator: `## Stage 1 · Discover (Pool)`. |
| Benchmarks thresholds | Stage 6 sections of flow docs | Cite the benchmark; don't re-state the value (changes ripple from Tier 1). |
| Entry points session modes | Tier 3 framing prose | Each flow doc opens by naming which session mode it covers (Decision / Monitoring / Emergency). |
| Three-layer disclosure | Tier 4 primitives | Every primitive declares its Glance / Analyze / Act split. |
| Tier 3 field names | Tier 4 primitives | Primitives reuse field names already cited upstream. New names → flag with `==note:==` for promotion to `Data requirements and to-dos.md`. |

## Authoring recipe — new flow doc

Procedure for authoring a new Tier 3 flow doc (e.g., Credit Account opening). Use `Pool deposit.md` + `Pool deposit - reference.md` as templates.

1. **Open `Personas and audience.md`** for the relevant persona (LP or CA operator). Enumerate the loss vectors at P1 and P2.
2. **Check canonical sources first**: `Personas and audience.md`, `Basic info and definitions.md`, `Benchmarks and tresholds for metrics.md`, and the nearest `user-flows/` sibling. If deleted legacy source material is genuinely needed, read it from git history or `.planning/` artifacts; do not recreate the legacy folders.
3. **Create the file pair**: `<flow>.md` + `<flow> - reference.md` under `user-flows/`. Copy the section structure from Pool deposit's pair.
4. **Write the job statement** using Personas voice (`When I … I want to … so I can …`).
5. **Layout Stages 1 → 6** with middle-dot headings.
6. **For each Q in Stage 2**:
   1. Pick the Personas loss vector it addresses.
   2. Write the `Exit gate` line using "default scope; T2 checks X when triggered" framing if there's any T2 content.
   3. Write `Why this matters`, opening with the loss-vector name + wikilink to Personas.
   4. Build the computation table — pick the appropriate shape (baseline, Lens, Aggregation, or change-watch).
   5. Assign T1 to coverage rows, T2 to mechanism / drill / structural-historical rows.
   6. Add the synthesis row at the bottom.
7. **Move drill content** (>5 lines) to the reference file under `## Drill — <topic>` headings. Topic-named for flow-agnostic reuse. Replace inline prose with wikilink.
8. **Stage 3** uses IC-analogy table; palette mapping in synthesis row; reference the IC-decision-palette drill.
9. **Stages 4–5** use Execution-Desk framing (preview → execute) per Pool deposit's pattern.
10. **Preserve all `==note:==` / `==resolved_note:==` / Russian voice notes** from any source files being absorbed. Move them with the section they're attached to.
11. **Sanity sweep**:
    - `T1 drill —` / `T2 drill —` prefix → 0
    - `Drill below.` → 0
    - `**How the agent reasons.**` → 0
    - `priority-1` / `priority-2` → 0 (priorities live in Personas only)
    - All wikilinks resolve.
12. **Update `README.md`** with the new file (URL-encoded standard-markdown link).
13. **Run workspace structural checks** (Validation section below).

## Connection mechanisms (cross-file edges)

In decreasing strictness:

1. **Wikilinks** (`[[Note#Anchor]]`) — strongest. Used in body when one doc literally derives from another.
   - Tier 2 / 3 docs open with the Tier-1 source they derive from.
   - Q's `Why this matters` opens with `[[Personas and audience#…|Personas]]`.
   - Drill rows use `[[<flow> - reference#Drill — X|drill ↗]]`.
2. **Field references** (`PoolOpportunity.yield`, `StrategyOpportunity.minDebt`) — implicit data-contract edges. No central glossary; types propagate by copy-reference. Don't invent new field names — reuse one already cited upstream or flag with `==note:==`.
3. **`README.md`** — the human-curated surface view of the graph; URL-encoded standard-markdown links.

## Authoring conventions (project-wide)

- **Highlights as test markers.** `==note: ...==` (open question), `==resolved_note: ...==` (historical question + resolution), `==phrase==` (uncertain phrasing). Preserve verbatim.
- **Stage heading dot separator.** `## Stage 1 · Discover (Pool)` — middle dot, not hyphen, not colon. Sub-questions inside Analyze use the same dot: `### Q1 · Where does the yield come from?`.
- **Filenames** contain spaces, em-dashes (`—`), parentheses, ampersands on purpose. Don't rename to kebab-case. The typo in `Benchmarks and tresholds for metrics.md` is preserved on purpose. JTBD and user-flow filenames mix em-dash (` — `) and hyphen (` - `) as title separator — both forms coexist; don't normalise.
- **Russian voice notes** as blockquotes are author memory. Leave in place unless asked to translate.
- **Tables are the dominant format** for criteria, sub-jobs, fields, thresholds, and Q computations. Match surrounding table style; don't introduce prose where the surrounding pattern is tabular.

## Validation

There is no markdown linter or doc-CI. Three things stand in for "running the test suite":

1. **The `==highlight==` grep** — the doc-equivalent of a test-suite run. Open questions are the failing tests; resolved notes are the passing regression fixtures.

   ```bash
   grep -rn "==note:\|==resolved_note:" \
     /Users/ilya/ai-assistant/projects/front-knowledge-base/ \
     --include="*.md"
   ```

2. **Workspace structural checks.** After renames, moved files, or new top-level docs, run from the parent monorepo root (`~/ai-assistant`):

   ```bash
   python3 scripts/workspace_sync.py --check
   python3 scripts/workspace_policy_check.py --all
   ```

   If they drift, run `python3 scripts/workspace_sync.py` then re-check.

3. **Per-flow sanity sweeps.** After restructuring a Tier 3 flow doc, grep for stale convention markers (see Authoring recipe Step 11).
