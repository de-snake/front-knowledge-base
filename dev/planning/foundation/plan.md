# Foundation completion plan

> **Archive note.** This is a pre-merge planning artifact. References to deleted `JTBDs/`, `User flows/`, Tier 4 user-flow, Tier 5 UI-primitive, `Multi-position`, or placeholder RWA structures are historical source-state references. Current canonical navigation lives in `../../README.md`, `../../CLAUDE.md`, and `../../user/flows/`.

Status: archived pre-merge draft. The current post-merge canonical structure is documented in `../../README.md` and `../../CLAUDE.md`.

Inputs:

- `dev/planning/foundation/glossary-inventory.md` — 49 concept terms (47 foundation-relevant) + 21 data-contract field references + 10 inconsistencies.
- `dev/planning/foundation/tier-2-gap-research.md` — 3-mode ↔ 6-row mapping (2 ambiguities), agent-reader synthesis (4 silent points), Glance/Analyze/Act per persona, file-move reference inventory (5 references, 4 break).

Locked-by-user decisions feeding this plan:

1. Personas content frozen (no polish). Prose intentionally raw; refinement happens in derived docs.
2. Basic info ↔ risk-configuration-dictionary relationship is **reference-only**. Glossary adds user-side / counterparty / risk-taxonomy / lifecycle / pool / RWA / agent concepts; protocol switches stay in the dict and are linked.
3. Decision-making loop docs **promote to vault root**, treated as Tier 1.
4. Tier 2 (now Tier 1) content gets **lock + targeted gap fixes**, not a full rewrite.

The plan has four workstreams. A and B can run in parallel after sign-off. C depends on B. D depends on A + B + C.

## 1 · Workstream A — Glossary expansion in Basic info and definitions.md

### 1.1 Inconsistency reconciliation (do this first)

Pick canonical form per term before drafting glossary entries. Recommendations:

| # | Inconsistency | Canonical form | Cross-reference |
| --- | --- | --- | --- |
| 1 | Quota umbrella vs Collateral-specific rate vs Collateral limit | Keep `quota` as user-facing umbrella. Define inside as `quota rate` (= dict's `Collateral-specific rate`) + `quota cap / per-token quota` (= dict's `Collateral limit` / `Quota Limit`). | risk-dict link |
| 2 | HF / Health Factor / health factor | `Health Factor` canonical; `HF` documented alias. Do **not** retroactively rewrite docs. | — |
| 3 | Credit Manager dual mental model | One entry holding both: "per-strategy borrowing module within a pool — pool-side a separate risk envelope, CA-side a strategy template." | risk-dict link |
| 4 | Session-mode taxonomy 3-row vs 6-row | Pin 3-row in Tier 1; treat 6-row matrix as ownership-lifecycle decomposition of Monitoring + Emergency modes (lives in Multi-position JTBD). | Multi-position JTBD link |
| 5 | Composite / Total / Net APY | Three explicit entries. LP headline = composite, CA headline = net. Total = alias for composite. | — |
| 6 | Forbidden token (mask vs parameter) | One entry: dict parameter + user-side consequence (safe-pricing kicks in on overlap). | risk-dict link |
| 7 | Concentration cap (user vs pool) | Two entries: `user concentration cap` (user-set diversification rule) and `pool concentration measure` (pool-side observation). | — |
| 8 | Quota composition (LP) vs per-token quota (CA) | Two entries, same word, different scope. Flag. | — |
| 9 | Borrow rate / borrow APY / borrow cost | `borrow rate` canonical user-facing; `borrowApy` = schema field; `borrow cost` = absolute (rate × principal). | — |
| 10 | Adapter (counterparty vs parameter) | One entry bridging dict parameter + user-side route-choice consequence. | risk-dict link |

### 1.2 Section structure for Basic info and definitions.md

Current file: 6 sections (CA, Collateral, Underlying, IRM, Sources of yield, Canonical loop). Target structure:

| § | Title | Entries (count) |
| --- | --- | --- |
| 1 | Core (existing) | CA, Collateral, Underlying, IRM, Sources of yield, Canonical loop, **Pool**, **Credit Manager**, **Utilisation** (expanded), **Borrowable liquidity**, **TVL** (10 entries — preserves the 6 existing, promotes 4 pool-side terms) |
| 2 | User-side derived metrics | HF, TWV, Net APY, Organic APY, Incentive APY, Composite APY, Leverage, Liquidation distance, Time-to-liquidation, Breakeven, Hurdle, Cost of doing nothing, User concentration cap, Share price, Insurance fund (15) |
| 3 | Counterparties / actors | Curator, Liquidator, Securitize / freeze authority, Protection bot, Issuer, Adapter, Investor (7). Pool LP / CA operator get one-line stubs linking to Personas. |
| 4 | Risk taxonomy | Bad debt, Socialised loss, Liquidation, Oracle (with methodology types: market / fundamental / hardcoded / composite), Oracle staleness, Safe pricing, Forbidden token, LT ramp, Quota system (rate + cap), Borrow rate, Liquidation premium / fee (stub), Withdrawal fee, Slippage / price impact (13) |
| 5 | Lifecycle / dynamics | CM expiration, Delayed withdrawal, Phantom token, Pause (3 states), Multicall, Parameter change log, Pending governance (7) |
| 6 | RWA-specific | Tokenised security, Frozen account, KYC, Redemption window, Transfer restriction type (5; NAV optional, currently low-signal) |
| 7 | Agent reader | Agent (full def, promoted from Personas table row), Plain-language translation, Emergency-path contract. **Glance/Analyze/Act stub** + **Session mode stub** link out to Tier 2 docs (now root). (3 + 2 stubs) |

Total: ~60 entries spread across 7 sections, all in one file.

### 1.3 Per-entry format

```
### Term name

One-to-three-sentence definition. Formula if applicable.

For terms also in risk-configuration-dictionary.md:
> See also: [risk-configuration-dictionary.md](path)#`<param>`.

For terms with thresholds:
> See also: [Position risk and monitoring](Position risk and monitoring%20and%20tresholds%20for%20metrics.md) — green/yellow/red rows.
```

### 1.4 Out of scope

The 21 data-contract field references (`Type.field` form) are tracked in the inventory but **not** added to Basic info. They belong in a future data-schema doc, which is a separate artifact and outside the foundation. The glossary entries that have schema-field counterparts may include a one-line "Schema field: `borrowApy` (see schema doc — TBD)" where useful.

## 2 · Workstream B — Tier 2 file move (mechanical)

Per `tier-2-gap-research.md` §4.6:

1. `git mv "Decision-making loop/Entry points.md" "Entry points.md"`.
2. `git mv "Decision-making loop/Three-layer progressive disclosure.md" "Three-layer progressive disclosure.md"`.
3. Edit `README.md:18-19` — rewrite paths and link texts (drop `Decision-making loop/` prefix).
4. Edit `CLAUDE.md:41-48` — rewrite Tier 2 / Tier 1 framing, fix two file paths.
5. Delete the now-empty `Decision-making loop/` folder.

Reference inventory: 4 of 5 references break (README:18, README:19, CLAUDE.md:47, CLAUDE.md:48). One survives (CLAUDE.md:84 prose mention). Outbound wikilink in `Entry points.md:3` to `Basic info and definitions#Canonical loop` resolves by note title and survives. Zero inbound wikilinks.

## 3 · Workstream C — Tier 2 content gap fixes (after move)

### 3.1 Entry points.md targeted edits

**E1. Reallocation framing.** Add a sentence to the Decision-session row (or below the table) explicitly noting that any session walking the full Discover → Execute path takes the Decision shape, including a Reallocation triggered from Monitoring. This adopts §1.3(b) recommendation — broaden by example, do not redefine the entry trigger.

**E2. Action / Exit handling.** Add a paragraph below the table noting that Monitoring sessions can produce a Propose-tail traversal (Monitor → Propose → Preview → Execute) when the deviation chooses to act without re-running Analyze. This is the back-edge sentence in line 12 made explicit. Adopts §1.3(a) recommendation.

**E3. 3-mode ↔ 6-row bridge.** Add a paragraph linking out to `JTBDs/Multi-position & portfolio-level - JTBD.md` and framing the 6-row matrix as the ownership-lifecycle decomposition of Monitoring + Emergency. Include the mapping table from `tier-2-gap-research.md` §1.2 inline.

**E4. Agent reader paragraph.** Add a section after the table (or as a follow-on to the existing line 15 design implication) covering the synthesis from `tier-2-gap-research.md` §2.2:

- Schema parity: agents and humans consume the same data; surfacing differs.
- Default mode: Monitoring.
- Hand-off line: Execute, configurable by action class (high-value or first-time → human; routine → scoped bot).
- Open questions (mark with `==note:==`): persistent state across sessions, autonomous Decision sessions, Emergency-specific protocol, agent-side whitelist vs scoped-bot-signer distinction.

**E5. (Optional) "10–30 seconds" claim.** Either add a `==note:==` flagging it as a UX assertion vs measured data, or leave alone. Recommendation: leave alone; it's a product-belief claim, not a measurement.

### 3.2 Three-layer progressive disclosure.md targeted edits

**T1. Per-persona Glance content tables.** Two tables (LP and CA) listing what content surfaces in each layer, drawn from `tier-2-gap-research.md` §3.1 and §3.2. The LP Glance is the 5 ownership questions (with the 2 named "Glance at …" sub-jobs as the strongest); the CA Glance is Q1 (HF, < 3 s) and Q2 (Net APY, < 5 s).

**T2. Position risk and monitoring ↔ Glance/Analyze relationship.** Note that the Position risk and monitoring file is the source of Glance verdict inputs, but most rows are Analyze-tier evidence. The "Overview or advanced" column at `Position risk and monitoring…:26` already encodes the Glance / Analyze split for CA — formalise the convention here so it propagates.

**T3. Agent vs human surfacing.** Add the divergence note: same hierarchy (verdict first, then analysis, then action), different format (raw values + verdict for agents; plain-language translation for humans). Cite `JTBDs/Credit Account management - JTBD.md:17` for the plain-language principle.

**T4. (Optional) Concrete render examples.** A short illustration of what an LP Glance and CA Glance literally render as for both surfaces. Recommendation: include only if it doesn't overstep into UI design speculation. If unsure, skip.

### 3.3 Side issue (separate edit, not blocking)

`JTBDs/Multi-position & portfolio-level - JTBD.md:47` says "four distinct session types" but the table has six rows. One-line fix: "six distinct session types". Not on the foundation critical path; flag as a follow-up.

## 4 · Workstream D — Cascade updates

### 4.1 README.md

- **Section structure.** Two viable shapes:
  - **Option D-A.** Keep "Decision-Making Loop" as a separate section (renamed to "Decision Axes"), holding the two promoted files. Mirrors the conceptual class distinction (vocabulary vs axes).
  - **Option D-B.** Fold the two files into "Foundations" as additional rows. Single foundation block; reads as one unit.
- **My recommendation: D-A** — the two docs are *axes*, not vocabulary; keeping them visually distinct mirrors the conceptual model.
- Add no new entries from Workstream A — the glossary expansion stays inside Basic info, no new top-level docs.

### 4.2 CLAUDE.md

- Rewrite §"Tier 2 — Decision-making loop (scaffolding)" (lines 41-48). Two viable shapes:
  - **Option D-C.** Collapse Tier 2 → Tier 1. The four-tier graph becomes three-tier (Foundations → JTBDs → User flows). Add a sub-categorisation inside Tier 1 ("vocabulary / axes / personas") if useful.
  - **Option D-D.** Keep two-tier framing but rename Tier 2 to "Tier 1 (axes)" — preserves numbering, fixes the misnomer.
- **My recommendation: D-C.** Cleaner. The two-tier story was always cosmetic.
- Update CLAUDE.md §"Authoring conventions" or add a note in §"Semantic scheme": Basic info now contains the foundation glossary; risk-config-dict is the protocol-switch reference and is linked from Basic info entries.
- §"Cross-cutting concerns" — add a one-line note that Entry points has an explicit agent-reader paragraph; the schema-parity invariant is stated there as the authoritative version.

## 5 · Sequencing

1. Sign off plan + open decisions (see §6).
2. **Parallel:** start Workstream A (glossary draft) and Workstream B (file move).
3. After B completes: Workstream C (content gap fixes).
4. After A, B, C: Workstream D (cascade updates).
5. Validation:
   - Run `grep -rn "==note:\|==resolved_note:" front-knowledge-base/ --include="*.md"` to confirm no new unintentional `==note:==` leaks.
   - From monorepo root: `python3 scripts/workspace_sync.py --check` and `python3 scripts/workspace_policy_check.py --all`.
   - Manual scan: README link integrity, CLAUDE.md tier diagram coherence.

## 6 · Open decisions (sign-off needed before execution)

Numbered for quick stamping. Recommendations marked.

**DG · Glossary**

- DG.1 — Accept all 10 inconsistency canonicalisation recommendations in §1.1? *(recommend: yes)*
- DG.2 — Section structure of 7 sections in §1.2? *(recommend: yes)*
- DG.3 — Glossary inside Basic info and definitions.md, or split into a separate `Glossary.md`? *(recommend: keep inside Basic info — preserves the existing entry-point file as the foundation entry)*

**DM · Mode model**

- DM.1 — Keep 3-mode taxonomy with Action / Exit / Reallocation as Monitoring-with-tail? *(recommend: yes; §3.1.E2)*
- DM.2 — Reallocation framing: broaden by example, no redefinition? *(recommend: yes; §3.1.E1)*

**DT · Tier 2 → Tier 1 architecture**

- DT.1 — README structure: D-A (separate "Decision Axes" section) or D-B (fold into Foundations)? *(recommend: D-A)*
- DT.2 — CLAUDE.md framing: D-C (three-tier graph) or D-D (rename Tier 2 in place)? *(recommend: D-C)*
- DT.3 — Delete `Decision-making loop/` folder after move? *(recommend: yes, no inbound wikilinks point inside it)*

**DA · Agent reader**

- DA.1 — Add explicit agent-reader paragraph in Entry points (§3.1.E4)? *(recommend: yes)*
- DA.2 — Mark the 4 silent points (persistent state, autonomous Decisions, Emergency protocol, agent-whitelist vs bot-signer) with `==note:==` as open questions? *(recommend: yes — they're real gaps, the marker is the project's grep-test)*

**DB · Position risk and monitoring ↔ Three-layer**

- DB.1 — Formalise the "Overview or advanced" column convention in the Three-layer doc (§3.2.T2)? *(recommend: yes — pulls the implicit split into Tier 1 where it belongs)*

**DR · Render examples in Three-layer**

- DR.1 — Include concrete LP / CA Glance render examples (§3.2.T4)? *(recommend: skip — risks UI design speculation)*

## 7 · Risks and rollback

- The file move is a `git mv`; reversible via `git mv` back. README and CLAUDE.md edits are in the same change and reversible.
- Glossary expansion is additive to Basic info and definitions.md. Worst case: re-export to a separate file later if it grows unwieldy.
- No external systems touched. No git push. No data deletions.
