# CLAUDE.md

This file is the operating contract for agents editing the Gearbox product knowledge vault.

## What this vault is

`front-knowledge-base` is an Obsidian-style product knowledge vault for Gearbox front-end and agent-facing reasoning. It is documentation, not code.

The vault now has two scopes:

- `user/` — runtime knowledge an agent needs to reason about user positions and funds.
- `dev/` — design lineage, implementation gaps, UI primitive drafts, and historical planning artifacts.

Canonical loop: `Discover → Analyze → Propose → Preview → Execute → Monitor`.

## Current layout

```text
front-knowledge-base/
  README.md
  CLAUDE.md

  user/
    foundations/
      Basic info and definitions.md
      Personas and audience.md
      Position risk and monitoring.md

    decision/
      Entry points.md
      Three-layer progressive disclosure.md

    flows/
      Pool deposit.md
      Pool monitoring.md
      Credit Account opening.md
      Credit Account management.md

    references/
      Pool deposit - reference.md
      Pool monitoring - reference.md
      Credit Account opening - reference.md
      Credit Account management - reference.md

  dev/
    implementation/
      Data requirements and to-dos.md
    ui-primitives/
      *.docx
    planning/foundation/
      historical planning artifacts
```

Legacy `JTBDs/`, `User flows/`, `user-flows/`, top-level benchmark pages, and standalone RWA leverage pages are not canonical. Use git history or `dev/planning/` only for archaeology.

## Current architectural rules

### User vs dev split

`user/` is for the agent's runtime understanding of positions and funds:

- definitions the agent must apply while reasoning;
- personas and loss vectors that justify flow questions;
- session / display axes;
- canonical position lifecycle flows;
- reference drills needed by those flows.

`dev/` is for implementation and design context:

- backend data gaps and stage artifact vocabulary;
- UI primitive drafts;
- old planning and merge reports;
- rationale that should not be loaded during routine position management.

If a dev-side concern matters at runtime, distill it into a user-side rule. Example: do not make the agent read a backend backlog while managing funds; instead add a runtime rule such as “missing issuer state blocks automation.”

### RWA / issuer-controlled assets

RWA is not a separate canonical flow or product universe.

Tokenized securities, issuer-controlled assets, redemption-window assets, and compliance-gated assets are conditional branches inside:

- `user/flows/Credit Account opening.md`
- `user/flows/Credit Account management.md`
- their reference drills
- `user/foundations/Position risk and monitoring.md`

Use this logic:

```text
If collateral / strategy includes RWA, tokenized security, issuer-controlled asset,
redemption-window asset, or compliance-gated asset:
  check issuer state
  check eligibility / KYC validity where applicable
  check freeze / transfer restrictions
  check redemption / claim readiness
  check eligible-liquidator depth
  treat automation as human-in-the-loop unless explicitly safe
```

If any material issuer, eligibility, freeze, redemption, transferability, or eligible-liquidator state is unknown, do not treat the position as ordinary liquid collateral.

Do not recreate `RWA leverage.md` or a separate RWA user flow unless the user action becomes fundamentally different from ordinary Credit Account opening / management.

### Threshold policy

Do not give the agent universal fixed defaults such as:

- “HF above X is safe”;
- “HF between X and Y is warning”;
- fixed green / yellow / red tables;
- hidden default slippage, leverage drift, liquidation, or APY bands.

`user/foundations/Position risk and monitoring.md` explains how to choose or request thresholds from:

- explicit user policy;
- a representative agent's mandate;
- protocol / market constraints that are facts rather than preferences;
- asset-property analysis;
- product policy for missing or blocking data.

Runtime flows may use labels like `ok`, `watch`, `review`, or `act now`, but each label must trace back to user policy, mandate, asset-specific analysis, or a blocking-data rule. If a required user policy is missing, the agent should ask, continue in read-only / analysis mode, or route state-changing actions to human review.

## File catalog

### `user/foundations/Basic info and definitions.md`

Shared Gearbox vocabulary: Credit Account, collateral, underlying token, IRM, yield sources, canonical loop, stage handoff rules, Preview / Execute invariants, and shared Pool / Credit Account mechanics.

Mutate when a downstream doc needs a new shared term. Do not put per-flow logic here.

### `user/foundations/Personas and audience.md`

Personas, sub-profiles, and loss vectors for Pool LPs and Credit Account operators. Flow questions derive from these loss vectors.

Mutate when a persona or loss vector changes. Do not put backend fields or computation logic here.

### `user/foundations/Position risk and monitoring.md`

Conceptual monitoring guidance. Explains why monitoring is needed, how position risk changes over time, how asset properties affect monitoring, which user policies are needed, and how missing data should be handled.

Mutate when the reasoning model changes, when a new asset-property branch matters, or when a new missing-data rule is needed. Do not add universal operating thresholds.

### `user/decision/Entry points.md`

Session-mode axis: Decision, Monitoring, Emergency; ownership-session branches; agent execution boundary; Preview / Execute approval modes.

Mutate when session modes, approval boundaries, bot policy, or emergency routing rules change.

### `user/decision/Three-layer progressive disclosure.md`

Screen / response organization: Glance, Analyze, Act. This is orthogonal to the six-stage loop.

Mutate when the Glance / Analyze / Act split changes for a persona or position type.

### `user/flows/Pool deposit.md`

Canonical LP entry flow. Stages 1–5 with handoff to Pool monitoring.

Use as the structural example for new flow docs: stage framing, Q tables, synthesis rows, and reference-drill links.

### `user/flows/Pool monitoring.md`

Canonical LP ownership flow. Starts at Stage 6 and conditionally back-edges to focused Analyze, Propose, Preview, and Execute.

Mutate when LP monitoring questions, drift signals, action classes, or back-edge mappings change.

### `user/flows/Credit Account opening.md`

Canonical Credit Account entry flow. Includes economics, collateral safety, exit feasibility, curator / Credit Manager envelope, pending changes, route selection, multicall Preview, and Execute.

Issuer-controlled collateral belongs here as a conditional collateral branch, not as a separate flow.

### `user/flows/Credit Account management.md`

Canonical Credit Account ownership / monitoring flow. Starts at Stage 6, detects safety / return / governance / operational / oracle / issuer drift, and routes to focused Analyze or action.

Issuer-controlled collateral belongs here as Q6 conditional logic. Emergency routing is a product / agent safety route based on user policy or action-blocking state, not a universal HF number.

### `user/references/* - reference.md`

Sibling drill files. Use flat `## Drill — <topic>` headings. Main flow tables should carry verdict-level summaries and link to drills when details exceed table-cell scannability.

Keep drill names flow-agnostic where possible.

### `dev/implementation/`

Human-readable implementation handoff compiled from canonical runtime docs. This is an exhaust from flow docs, not an input to runtime agent reasoning.

Use `Data requirements and to-dos.md` as the single implementation map. It should stay readable by a product owner: scenario → user asks/clicks → agent checks → user gets back → build order.

Do not add taxonomies of card names, field dictionaries, schemas, or database architecture unless the user explicitly asks for them.

Rows and fields should separate protocol facts, indexer facts, issuer / compliance facts, product judgment, and user / agent policy when that detail is needed.

### `dev/ui-primitives/*.docx`

Word-based UI component drafts. They follow the canonical user flows; they do not define product logic independently.

### `dev/planning/foundation/`

Historical planning archive. These files may mention old folder names, fixed benchmark tables, or standalone tokenized-security leverage. Treat them as historical source state, not current canonical guidance.

## Flow doc conventions

### Stage shape

For stages whose shape is data-pipeline oriented:

- `Inputs` — what enters this stage;
- `Compute` — what the agent does;
- `Outputs` — what hands off to the next stage.

For Analyze / Monitor questions, use:

1. `Exit gate`
2. `Why this matters`
3. computation table
4. `**Synthesis**` row

### Computation tables

Baseline table:

```markdown
| Sub-question | Tier | What the agent does | Data retrieved |
| --- | --- | --- | --- |
```

Use additional columns only when the local pattern already requires them, for example `Lens`, `Aggregation`, or change-classification fields.

### T1 / T2

- `T1` = default scope inside a firing question.
- `T2` = extended drill scope, triggered by sophistication, review-required findings, or structural risks.

Tier is a research-depth control. Priority lives in `Personas and audience.md`.

### Synthesis row

Each computation table ends with a `**Synthesis**` row. The synthesis names what default scope covers, what extended scope adds, and where drift back-edges.

### Drill externalization

If explanatory content would exceed roughly five lines in a flow table cell, move it to the sibling reference file under `## Drill — <topic>` and link with:

```text
[[<flow> - reference#Drill — <topic>|drill ↗]]
```

### Agent / human execution boundary

The agent may read, analyze, monitor, explain, and prepare proposals without changing user state.

Any state-changing action follows:

```text
Propose → Preview → Execute
```

Execute requires a human signature or a pre-authorized scoped bot policy. Missing execution-package integrity, missing issuer / eligibility data for controlled collateral, or missing user policy for a safety-critical action blocks automation.

## Linking conventions

- Body docs use Obsidian wikilinks: `[[Note#Anchor|label]]`.
- `README.md` uses URL-encoded standard Markdown links.
- Do not recreate old paths to satisfy broken links. Update links to the canonical file under `user/` or `dev/`.
- Prefer wiki note names without folder prefixes unless disambiguation is required.

## Marker preservation

Preserve these markers verbatim during restructuring:

- `==note: ...==`
- `==resolved_note: ...==`
- `==phrase==`
- Russian voice-note fragments

Move markers with the section they annotate. Do not delete them unless the user explicitly asks or the resolution is incorporated and the note is intentionally removed.

## Gearbox terminology and style

Follow `projects/gearbox/CLAUDE.md` for Gearbox terminology. Key reminders:

- Use `Credit Account`, not `credit account`, `credit-account`, or `creditAccount` in prose.
- Use `Credit Manager`, capitalized as two words.
- Prefer `partner protocol` over `external protocol` or `third-party protocol`.
- Use formal, precise wording.
- For tokenized securities / Securitize flows, use positive issuer / eligibility wording and avoid whitelist-bypass framing.

## Validation

After moved files, renamed files, or navigation changes, run from this vault:

```bash
git diff --check
git status --short
```

Also search for stale current-doc references outside explicitly historical archive or validation instructions:

```text
user-flows
RWA leverage
RWA collateral branch
Benchmarks and tresholds
Credit Account monitoring
fixed green / yellow / red threshold tables
```

From the monorepo root (`~/ai-assistant`), run:

```bash
python3 scripts/workspace_sync.py --check
python3 scripts/workspace_policy_check.py --all
```

If generated workspace files drift, run `python3 scripts/workspace_sync.py`, then rerun both checks.
