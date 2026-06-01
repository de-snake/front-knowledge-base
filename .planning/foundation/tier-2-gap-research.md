# Tier 2 promotion — gap research

> **Archive note.** This is a pre-merge planning artifact. References to deleted `JTBDs/`, `User flows/`, Tier 4 user-flow, Tier 5 UI-primitive, `Multi-position`, or placeholder RWA structures are historical source-state references. Current canonical navigation lives in `../../README.md`, `../../CLAUDE.md`, and `../../user-flows/`.

Read-only research artefact. Inputs for two follow-up changes:

1. Targeted content edits to the two Tier 2 docs.
2. File move from `Decision-making loop/` to vault root (treating them as Tier 1).

All citations are `path:line`. No vault edits performed in this artefact.

The two source docs are short:

- `Decision-making loop/Entry points.md` (16 lines) — three session modes
  Decision / Monitoring / Emergency, each a different traversal of the
  canonical six-stage loop.
- `Decision-making loop/Three-layer progressive disclosure.md` (11 lines) —
  three layers Glance / Analyze / Act, orthogonal to the loop, describing
  how any single screen or agent reply is organised.

---

## GAP 1 · 3-mode ↔ 6-row mapping

### 1.1 Source verbatim

The 3-mode definition (`Decision-making loop/Entry points.md:9-13`):

| Mode | Definition (verbatim, condensed) |
| --- | --- |
| **Decision session** | "first deposit or new capital… full traversal from Discover through Execute… the _rarest_ session type by frequency." (line 11) |
| **Monitoring session** | "return visit… enters the loop at Stage 6 (Monitor)… 10–30 seconds, 'glance at safety and returns, leave.' A meaningful deviation loops the user back to Analyze (and possibly all the way to Discover if they want to switch venues)." (line 12) |
| **Emergency session** | "pressure event… enters Stage 6 in danger state, then goes directly to Propose → Preview → Execute without re-running Analyze… UI and agent must collapse the path from 'awareness of danger' to 'signed remediation' to under two clicks." (line 13) |

The 6-row matrix from `JTBDs/Multi-position & portfolio-level - JTBD.md:45-56`
(verbatim header + rows):

> The ownership lifecycle surfaces four distinct session types. Each is a different traversal of the canonical loop entered at Stage 6, with its own JTBD, required data, and success criterion. (line 47)

| Session type | Entry trigger | Loop path | Primary JTBD served | Session length | Success = |
| --- | --- | --- | --- | --- | --- |
| **Confirmation** | Scheduled check-in | Monitor → exit | Maintain conviction (§2.1) | 10–30 s | Left reassured, no action |
| **Analysis** | Change detected or suspicion | Monitor → Analyze → exit _or_ Propose | Detect change early (§2.2) | 2–10 min | Understood why, decided whether to act |
| **Action** | Deliberate optimisation or claim | Monitor → Propose → Preview → Execute | Optimise (§2.3) _or_ maintenance action | 2–15 min | Action signed, before/after matched expected |
| **Emergency** | HF breach, oracle incident, governance alert | Monitor (danger) → Propose → Preview → Execute | Act under pressure (§2.4) | 30 s – 3 min | Remediation signed in ≤ 2 clicks |
| **Exit** | Thesis broken, capital need | Monitor → Propose → Preview → Execute (exit variant) | Exit deliberately (§2.5) | 5–20 min | Exit executed at expected cost and timeline |
| **Reallocation** | Better venue or strategy found | Monitor → Discover → Analyze → Propose → Preview → Execute | Optimise (§2.3) across venues | 15–30 min | Moved capital with net positive expected value |

Two notes from the verbatim text that shape the mapping:

- The matrix header at line 47 says "four distinct session types" but the
  table has six rows. The lead-in undercount is itself a content
  inconsistency to flag (Exit and Reallocation may have been added after the
  intro line was written). It is not load-bearing for the mapping.
- Every row's "Loop path" begins at Stage 6 (Monitor), so by definition no
  row in the matrix is a pure Decision session. The matrix is the
  ownership-lifecycle decomposition; Decision-mode (first-deposit) is by
  construction outside it.

### 1.2 Proposed mapping

The mapping criterion: which of the three loop-traversal shapes in
`Entry points.md` does each row's "Loop path" structurally resemble?

| 6-row session type | Maps to 3-mode | Structural reason | Confidence |
| --- | --- | --- | --- |
| **Confirmation** | **Monitoring** | Path `Monitor → exit`. Length 10–30 s. Both literally use the phrase "10–30 s" — `Entry points.md:12` and `Multi-position…:51`. | High — quotes match. |
| **Analysis** | **Monitoring**, may escalate to **Decision** | Path `Monitor → Analyze → exit _or_ Propose`. This is exactly the "meaningful deviation loops the user back to Analyze" branch from `Entry points.md:12`. If it then walks `Analyze → Propose → Preview → Execute`, the second half of the session is decision-shaped. | High — but the "→ Propose" tail is a Monitoring-triggered Decision tail, so the row is genuinely two-mode in sequence. |
| **Action** | **Monitoring** (with Propose / Preview / Execute tail) | Path `Monitor → Propose → Preview → Execute` skips Analyze (the thesis already holds). The 3-mode model has no name for this — it is faster than a Decision session (no Analyze) but not driven by danger. | Medium — see §1.3 ambiguity (a). |
| **Emergency** | **Emergency** | Path `Monitor (danger) → Propose → Preview → Execute`. Length 30 s – 3 min. ≤ 2 clicks success criterion. Both rows quote the same emergency-path contract — `Entry points.md:13` and `Multi-position…:54`. | High — quotes match. |
| **Exit** | **Monitoring** (with full Propose → Execute tail) | Path `Monitor → Propose → Preview → Execute (exit variant)`. Same shape as Action; differs only in the action chosen (close / unwind). | Medium — see §1.3 ambiguity (a). |
| **Reallocation** | **Decision** triggered from **Monitoring** | Path `Monitor → Discover → Analyze → Propose → Preview → Execute` is the full canonical loop. The trigger is monitoring (a return visit), but the traversal is identical to a Decision session. The 3-mode model doesn't currently name this hybrid. | Low — see §1.3 ambiguity (b). |

### 1.3 Genuine ambiguities to flag

(a) **The "Action / Exit" gap.** The 3-mode model has no clean home for
`Monitor → Propose → Preview → Execute` traversals that are neither
emergencies nor purely informational. They share the path shape with
Emergency but lack the speed constraint and danger trigger. Two options for
the targeted edit:

- Treat them as Monitoring-with-tail (Monitoring is the entry; the tail is
  just "the deviation chose to act"). Coherent with `Entry points.md:12`'s
  back-edge sentence.
- Add a fourth mode — "Maintenance" or "Action" — to make the 6-row matrix
  collapse cleanly to four. Bigger change; touches every doc that quotes
  "three modes."

Recommendation: keep the 3-mode model and explicitly say in the edit that
Action / Exit are Monitoring sessions whose deviation produced a Propose
tail. Cite the back-edge sentence as the structural justification.

(b) **Reallocation = Decision-triggered-by-Monitoring.** The full canonical
loop is walked, so structurally it is a Decision session. But the trigger
is a return visit, not new capital. `Entry points.md:11` defines Decision
sessions as "first deposit or new capital" — Reallocation is neither.
Either:

- Broaden the Decision-session definition to "any session that walks the
  full Discover → Execute path, regardless of whether capital is new."
- Or treat Reallocation as a Monitoring session that escalates all the way
  to Discover (which `Entry points.md:12` already explicitly admits:
  "possibly all the way to Discover if they want to switch venues").

The second framing is consistent with the existing text and requires no
definitional change. Recommended.

(c) **"Four distinct session types" intro vs six rows.** The lead-in at
`Multi-position…:47` undercounts. Mention this as a separate content gap;
do not let it block the mapping.

---

## GAP 2 · Agent (LLM) reader treatment

### 2.1 Inventory of agent / LLM / bot mentions

Every place the vault explicitly addresses an automated reader:

| File:line | Framing (verbatim) |
| --- | --- |
| `Personas and audience.md:14` | LP profile row: **"Agent (LLM) acting for any of the above** — needs the same facts, serialised." |
| `Personas and audience.md:40` | CA-operator profile row: **"Agent (LLM) acting for any of the above** — runs the same decision loop autonomously or with human approval at Execute." |
| `CLAUDE.md:9` | "used by both humans and LLM agents acting on the same data schema." |
| `CLAUDE.md:48` | Three-layer doc described as "how a single screen or agent reply is organised." |
| `CLAUDE.md:77` | "RWA / Securitize and the 'agent (LLM) reader' are **not separate docs**. They appear as labelled extensions inside Tier 3 and Tier 4 wherever they apply. The schema is unified; only the surfacing differs." |
| `Decision-making loop/Entry points.md:7` | "The UI and agent prompts must recognise the mode." |
| `Decision-making loop/Entry points.md:13` | "The UI and agent must collapse the path from 'awareness of danger' to 'signed remediation' to under two clicks." |
| `Decision-making loop/Entry points.md:15` | "the _same_ data fields the agent needs for due diligence are also the fields needed for monitoring and for emergency response — served with a different ranking, surface, and tone. Building one schema for all three modes is the product-engineering lever." |
| `Decision-making loop/Three-layer progressive disclosure.md:11` | "Agents should answer questions with the same hierarchy — give the glance verdict first, then the analysis, then the action recommendation." |
| `JTBDs/Pool position management - JTBD.md:21` | "An agent representing an LP should answer these five (six with RWA) questions first on every monitoring call, in the order above. If all answers are 'no change,' the session can end in under a minute with a single summary line. If any answer is 'yes, changed,' the agent loops back to Analyze for a fresh due-diligence pass — that is the explicit back-edge in the canonical loop." |
| `JTBDs/Credit Account management - JTBD.md:9` | Column header for ownership questions: "Notes for agent / UI." |
| `JTBDs/Credit Account management - JTBD.md:17` | "**Plain-language principle for agents.** Every raw metric should be served with a translation. Raw value for machines and advanced users; translation for the glance." |
| `JTBDs/Credit Account management - JTBD.md:27` | "the agent must surface a top-line danger line and a single concrete proposed action (Add Collateral or Reduce Leverage, with amount and before/after)." |
| `JTBDs/Credit Account (Opening) — JTBD.md:60` | "UI and agents should surface this — daily borrowing cost in plain language, unclaimed reward amount, days-to-expiration for expirable CMs — as a recurring gentle push." |
| `User flows/Pool deposit - User flow (LP).md:21` | "For an agent, this is a serialised `AnalyzedCandidate[]` stub; for a human, it's 'I'll look more carefully at these three.'" |
| `User flows/Pool deposit - User flow (LP).md:138` | Execute mode: "Human-in-the-loop — the agent encodes the preview into a verifier flow; the human signs in their wallet." |
| `User flows/Pool deposit - User flow (LP).md:139` | Execute mode: "Bot — a scoped bot signer executes within on-chain permissions." |
| `User flows/Credit Account - User flow (CA operator).md:9` | Discover step: "Filters the unified feed by chain, target collateral token, access (`permissionless` / `kycRequired`), and **agent-side whitelist**." |
| `User flows/Credit Account - User flow (CA operator).md:217` | "Same invariant as the LP side: the previewed multicall is the executed multicall. Human-in-the-loop for high-value or first-time actions, bot execution within scoped permissions for automated management." |
| `User flows/Credit Account - User flow (CA operator).md:283` | Discover artifact handoff: "Agent filter + rank produces `AnalyzedCandidate[]` stubs." |
| `Data requirements and to-dos.md:13` | Contextual recommendation engine "needs a defined rule matrix agreed between product, protocol, and the agent reasoning layer." |

Distinction note: the vault uses two related but distinct words.

- **Agent** / **LLM agent** = an LLM-based reader/decision-maker. References
  above use this meaning unless specified.
- **Bot** = a scoped on-chain signer with limited permissions; mentioned at
  Execute (`Pool deposit…:139`), in CA management (`Credit Account
  management…:15`'s "bot triggers"), and inside `User flows/Credit Account
  …:264`'s "Active bots with permissions." These are not LLM agents — they
  are deterministic on-chain helpers. Conflating them in a Tier-1 edit
  would weaken the model.

### 2.2 Synthesis

What the vault says, taken together:

**Schema parity, surface divergence.** `CLAUDE.md:77` and
`Entry points.md:15` both state the same invariant: humans and agents
consume identical data; only ranking, surface, and tone change.
`Personas and audience.md:14` repeats it ("needs the same facts,
serialised") on the LP side.

**Default agent session mode.** Two anchor sentences:

- LP side, `Pool position management - JTBD.md:21`: an agent's default
  session is the monitoring-call loop — answer the five (six with RWA)
  ownership questions, end in "no change" or escalate to Analyze.
- CA side, `Personas and audience.md:40`: agent "runs the same decision
  loop autonomously or with human approval at Execute."

Putting these together: the agent's _default_ traversal is the Monitoring
session. It has the schema to walk Decision and Emergency too, and may
walk them autonomously, but the high-frequency case is monitoring-call
shape.

**Where the agent hands off to a human.** The vault is explicit on one
hand-off point and silent on others:

- `Personas and audience.md:40` — "with human approval at Execute" — names
  Execute as the canonical hand-off boundary.
- `User flows/Pool deposit - User flow (LP).md:138` — "the agent encodes
  the preview into a verifier flow; the human signs in their wallet" —
  matches: Execute is the hand-off; the agent prepares everything up to
  signature.
- `User flows/Credit Account - User flow (CA operator).md:217` — "Human-in-
  the-loop for high-value or first-time actions, bot execution within
  scoped permissions for automated management" — qualifies: human approval
  is required for high-value or first-time actions; routine actions can
  execute via on-chain bot. So the hand-off line at Execute is configurable
  by action class, not absolute.
- The vault is silent on whether an agent ever hands off at **Propose**
  (e.g. asks the human "do you want me to propose?"). The current text
  treats the agent as autonomous through Discover / Analyze / Propose /
  Preview, then hands the previewed bytes to the human at Execute.

**Glance output structurally for an agent vs human.** The vault is partly
explicit:

- `Three-layer progressive disclosure.md:11` — the agent should "give the
  glance verdict first, then the analysis, then the action recommendation."
  Same hierarchy, different format.
- `Credit Account management - JTBD.md:17` — "Raw value for machines and
  advanced users; translation for the glance." Implicitly: the agent
  consumes raw values; the human-facing glance gets the plain-language
  translation. The two glances diverge in surfacing but draw from the same
  fields.
- The vault does NOT state explicitly that an agent's glance is a single
  token / verdict line vs the human's visual UI. The closest is
  `Credit Account management - JTBD.md:27` — "the agent must surface a
  top-line danger line and a single concrete proposed action" — which
  is the Emergency-mode glance, not the general case.

**What's silent and should not be invented.**

- Whether agents and humans share the same persistent state (e.g. user
  floor APY, HF threshold) across sessions, or whether each agent call
  re-derives them.
- Whether agents enter their own Decision sessions (first-deposit-shaped)
  or only act on user-initiated Decision sessions.
- Whether agents have an Emergency-session-specific protocol beyond the
  ≤ 2-clicks contract that applies to humans.
- Whether the "agent-side whitelist" at `User flows/Credit Account…:9`
  is the same as the "scoped bot signer" at `Pool deposit…:139`. The
  former gates which strategies an agent will surface; the latter is an
  on-chain signer permission. Two layers, same word adjacent — clarify
  in any edit.

---

## GAP 3 · Glance / Analyze / Act content per persona

The 11-line `Three-layer progressive disclosure.md` defines layers but
gives no content. Below is the candidate inventory drawn from existing
docs, by persona × ongoing-session.

### 3.1 Pool LP (ongoing monitoring session)

**Glance candidates.**

- "Am I earning what I expected?" — current APY with organic / incentive
  breakdown + 30d trend vs entry baseline (`Pool position management -
  JTBD.md:13`; sub-job at line 27 `Glance at yield`).
- "Can I still exit at size?" — current available liquidity vs the user's
  position; utilisation 30d trend (`Pool position management - JTBD.md:14`;
  sub-job line 28 `Glance at exit feasibility`).
- "Is composition / governance / canary intact?" — three further ownership
  questions (`Pool position management - JTBD.md:15-17`).

The two sub-jobs explicitly named "Glance at …" are the strongest Glance
candidates. The other three ownership questions are answerable
glance-style ("no change" / "changed") per the back-edge logic at
`Pool position management - JTBD.md:21`.

**Analyze candidates.** The five Stage-2 questions in
`User flows/Pool deposit - User flow (LP).md:24-95`:

- Q1 yield decomposition (organic vs incentive) and 90d series — `:28-36`.
- Q2 exposure chain — pool → CMs → tokens → insurance — `:38-58`.
- Q3 exit feasibility (utilisation trend, IRM, withdrawal fee) — `:60-72`.
- Q4 curator trust frame — `:74-78`.
- Q5 governance and parameter change log — `:80-86`.

These are also the questions that the monitoring session escalates back
to when the Glance flips yellow / red.

**Act candidates.** The three "Decide" sub-jobs from
`Pool position management - JTBD.md:34-36`:

- Decide top-up (sub-job 8).
- Decide partial exit (sub-job 9).
- Decide full exit (sub-job 10).

Each runs through Propose → Preview → Execute with a before/after preview.

### 3.2 CA operator (ongoing management session)

**Glance candidates.** The "Five ownership questions" in
`Credit Account management - JTBD.md:7-15`, with explicit timing budgets:

- Q1 "Am I safe?" — HF + plain-language label, liquidation distance,
  time-to-liquidation, LT-ramp status, forbidden-tokens overlap — must be
  answerable in **< 3 s** (line 11).
- Q2 "Am I making money?" — Net APY, total return in underlying + %, 30d
  account-value sparkline — must be answerable in **< 5 s** (line 12).

The two sub-jobs at `Credit Account management - JTBD.md:33-34` use the
exact word "Glance":

- Sub-job 1 "Glance at safety" — visible in **< 3 s**.
- Sub-job 2 "Glance at returns" — visible in **< 5 s**.

These two are the strongest Glance candidates by the doc's own naming.

**Analyze candidates.** The remaining ownership questions at
`Credit Account management - JTBD.md:13-15`:

- Q3 "What's inside my account?" — composition, debt breakdown, leverage,
  strategy description.
- Q4 "What can I do?" — contextual recommendations.
- Q5 "What happened?" — chronological action log.

Plus the deeper Stage-2 dossier from `User flows/Credit Account - User flow
(CA operator).md`:

- Q1 economics dossier — `:40-66`.
- Q2 collateral safety dossier (asset properties, Gearbox params, oracles)
  — `:69-134`.
- Q3 curator + CM constraints — `:136-162`.
- Q4 parameter change log + pending governance — `:164-172`.

And the granular Monitor stage at `User flows/Credit Account…:222-275`
covers all the deltas a yellow / red Glance would push the user to.

**Act candidates.** Sub-jobs 10–17 in `Credit Account management -
JTBD.md:42-49`:

- Add collateral, Reduce leverage, Increase leverage, Change strategy,
  Partial exit, Full exit, Handle emergency, RWA compliance check.

Each runs through `Stage 3 · Propose (CA)` → `Stage 4 · Preview (CA)` →
`Stage 5 · Execute (CA)` with a before/after preview component (called
out at `Data requirements and to-dos.md:11`).

### 3.3 Hypothesis check — are the Benchmarks rows the canonical Glance?

The hypothesis: the green / yellow / red rows in
`Benchmarks and tresholds for metrics.md` are the canonical Glance content.

**Pool side.** `Benchmarks…:5-20` lists ten ongoing-ownership criteria.
Mapping to the five Glance / ownership questions in
`Pool position management - JTBD.md:11-17`:

| Benchmarks row | Maps to Glance / Analyze question |
| --- | --- |
| Organic APY vs user floor (line 11) | Q1 yield |
| Composite APY 30d trend (line 12) | Q1 yield |
| Utilisation (line 13) | Q2 exit |
| Utilisation 30d trend (line 14) | Q2 exit |
| Share price (line 15) | Q5 bad-debt canary |
| Insurance fund (line 16) | Q5 bad-debt canary (and Q2 exposure tail) |
| Pending governance (line 17) | Q4 governance |
| Quota composition vs entry (line 18) | Q3 composition |
| RWA frozen accounts (line 19) | RWA Q6 compliance drift |
| Curator change log (line 20) | Q4 governance |

Every JTBD ownership question has at least one Benchmarks row. So
**confirmed for Pool LP**: the Benchmarks rows are the Glance verdict
inputs — each row reduces to a green / yellow / red token; ten tokens
together answer the five ownership questions in one screen.

Caveat: the Benchmarks rows are denser than the JTBD's "five glance
questions." A literal Glance UI that surfaced ten chips would be too
heavy for a 30-second session. The likely render: collapse the ten
Benchmarks rows under the five JTBD questions — Glance shows five
verdicts; tapping each opens the contributing Benchmarks rows in Analyze.

**CA side.** `Benchmarks…:22-44` lists fifteen criteria. The doc itself
has an "Overview or advanced" column to pre-classify them
(`Benchmarks…:26`):

- HF (line 28) — column says **overall** → Glance.
- HF 30d trend (line 29) — column says **advanced** → Analyze.
- Most other rows have empty Overview-or-advanced cells.

Mapping to the CA management ownership questions
(`Credit Account management - JTBD.md:11-15`):

| Benchmarks row | Maps to Glance Q1/Q2 / Analyze |
| --- | --- |
| HF (line 28) | Glance Q1 (overall) |
| HF 30d trend (line 29) | Analyze (advanced) |
| Net APY vs hurdle (line 30) | Glance Q2 |
| Borrow rate vs collateral APY (line 31) | Analyze Q2 / Q3 |
| LT ramp status (line 32) | Glance Q1 (sub) / Analyze |
| Forbidden-token overlap (line 33) | Glance Q1 (sub) / Analyze |
| Oracle freshness (line 34) | Analyze |
| Main-vs-reserve oracle divergence (line 35) | Analyze |
| Price-impact at position size (line 36) | Analyze |
| CM expiration (line 37) | Analyze (gentle nudge per `Credit Account (Opening) — JTBD.md:60`) |
| CM pause status (line 38) | Glance Q1 (sub) — emergency banner |
| Parameter change log 30d (line 39) | Analyze |
| Pending governance (line 40) | Analyze |
| RWA own-frozen status (line 41) | Glance Q1 (sub) — RWA emergency |
| RWA KYC validity (line 42) | Analyze (RWA) |
| Pending delayed withdrawals (line 43) | Analyze |

So **partial confirmation, partial refute** for CA:

- The Benchmarks doc's own "Overview or advanced" classification at
  `Benchmarks…:26` already separates Glance-tier rows (HF, marked
  "overall") from Analyze-tier rows (HF 30d trend, marked "advanced").
- Most rows are empty in that column. The hypothesis "Benchmarks rows ARE
  the Glance content" only holds for those rows explicitly tagged
  "overall." The rest belong in Analyze.
- A clean refute: **HF 30d trend is explicitly NOT a Glance row**
  (`Benchmarks…:29` column = "advanced"), so the Benchmarks file is
  already encoding a Glance / Analyze split via that column. The targeted
  edit should formalise this column rather than restate the hypothesis.

Recommendation for the Tier-2 edit: Glance content per persona is
**the two named "Glance at …" sub-jobs** (Pool LP) / **Q1 + Q2 ownership
questions** (CA operator). Benchmarks rows feed those Glance verdicts
but don't ARE them — most rows are Analyze-tier evidence.

---

## GAP 4 · Reference / wikilink inventory for the file move

Goal: enumerate every reference to either Tier 2 file across the vault.
Determine which break when moving from `Decision-making loop/<file>.md`
to `<file>.md` at vault root.

### 4.1 Inventory

Total references found: **5**. (Plus a meta-reference to the folder name
in `CLAUDE.md:41` heading "Tier 2 — Decision-making loop (scaffolding)".)

| # | File:line | Reference text (verbatim) | Type | Breaks on move? |
| --- | --- | --- | --- | --- |
| 1 | `README.md:18` | `[Decision-making loop/Entry points](Decision-making%20loop/Entry%20points.md)` | Standard markdown link, URL-encoded | **Yes** — path `Decision-making%20loop/Entry%20points.md` no longer exists; must be rewritten to `Entry%20points.md`. Also retitle the link text to drop the `Decision-making loop/` prefix for consistency. |
| 2 | `README.md:19` | `[Decision-making loop/Three-layer progressive disclosure](Decision-making%20loop/Three-layer%20progressive%20disclosure.md)` | Standard markdown link, URL-encoded | **Yes** — same as above. Path becomes `Three-layer%20progressive%20disclosure.md`. |
| 3 | `CLAUDE.md:47` | `` `Decision-making loop/Entry points.md` `` | Inline-code prose mention (filename string) | **Yes (factually)** — the path string in the doc's Tier-2 table will be wrong. Code-formatted, so won't render-break, but the doc literally lists the wrong location. Update to `` `Entry points.md` ``. The whole "Tier 2 — Decision-making loop (scaffolding)" section header at `CLAUDE.md:41` is also factually wrong post-move and needs broader rework. |
| 4 | `CLAUDE.md:48` | `` `Decision-making loop/Three-layer progressive disclosure.md` `` | Inline-code prose mention | **Yes (factually)** — same as above. Update to `` `Three-layer progressive disclosure.md` ``. |
| 5 | `CLAUDE.md:84` | `` `Entry points.md` opens with `[[Basic info and definitions#Canonical loop]]` `` | Bare-filename prose mention | **No** — the prose says only `Entry points.md`, no folder. Survives the move. (This is in the "Connection mechanisms" example list.) |

### 4.2 Wikilinks specifically

There are **zero** wikilinks targeting either file anywhere in the vault.
Verification: full vault grep for `[[` produced 8 hits
(`Basic info and definitions.md:25`, `JTBDs/Credit Account (Opening) —
JTBD.md:14/18/19/20`, `JTBDs/Credit Account management - JTBD.md:14`,
`User flows/Credit Account - User flow (CA operator).md:48/171`,
`Decision-making loop/Entry points.md:3` — itself, an outbound link to
`Basic info and definitions`). None target Entry points or Three-layer.

This is consistent with `CLAUDE.md:84`'s framing — the Tier 2 docs are
currently the _origin_ of one wikilink (out to Tier 1) and the
_destination_ of zero wikilinks. They are referenced only via README.md
and CLAUDE.md.

### 4.3 Outbound wikilink in `Entry points.md` — does it survive the move?

`Decision-making loop/Entry points.md:3` contains:

```
[[Basic info and definitions#Canonical loop]]
```

Wikilinks resolve by note title in Obsidian, not file path. `Basic info
and definitions.md` is at vault root before and after. **Does not break.**

### 4.4 Asset / image references — none

`Entry points.md` and `Three-layer progressive disclosure.md` contain no
image embeds, no relative-path refs to `Assets/`. Move is safe in that
regard.

### 4.5 Folder cleanup

After the move, `Decision-making loop/` is empty. Decide whether to:

- Delete the empty folder.
- Keep it as a guard against future stale wikilinks (negligible benefit;
  no wikilinks point inside it).

CLAUDE.md narrative also references `Decision-making loop` as a Tier
container in:

- `CLAUDE.md:41` — heading "Tier 2 — Decision-making loop (scaffolding)".
- `CLAUDE.md:46` — table column "Axis" + the two file rows.

These are structural-narrative references, not link references. The
broader Tier-2 section needs rewriting as part of the promotion to
Tier 1, not just path-fixing. Treat as a separate edit beyond the
mechanical path rewrites in §4.1.

### 4.6 Move checklist (mechanical, for the follow-up file-move task)

In order:

1. `git mv "Decision-making loop/Entry points.md" "Entry points.md"`.
2. `git mv "Decision-making loop/Three-layer progressive disclosure.md"
   "Three-layer progressive disclosure.md"`.
3. Edit `README.md:18-19` — rewrite both paths and link texts (drop the
   `Decision-making loop/` prefix). Move both rows from the
   "Decision-Making Loop" section into the "Foundations" section if the
   intent is to promote them visually as Tier 1; or leave the section
   header in README and just fix paths if the section is preserved.
4. Edit `CLAUDE.md:41-48` — rewrite the Tier 2 / Tier 1 framing and the
   two file paths. Confirm whether the four-tier graph is becoming a
   three-tier graph or if Tier 2 still exists with different contents.
5. (Optional) `rmdir "Decision-making loop"` after confirming empty.
6. Run the validation greps from `CLAUDE.md:178-180` and `:187-189`.
