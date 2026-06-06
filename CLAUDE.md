# CLAUDE.md

This file is the operating contract for agents editing the Gearbox product knowledge vault.

## What this vault is

`front-knowledge-base` is an Obsidian-style product knowledge vault for Gearbox front-end and agent-facing reasoning. It is documentation, not code.

The vault now has two scopes:

- `user/` — runtime knowledge an agent needs to reason about user positions and funds.
- `dev/` — design lineage, implementation gaps, UI primitive drafts, and historical planning artifacts.

Canonical loop: `Discover → Analyze → Propose → Preview → Execute → Monitor`.

## Human-request routing for executable harnesses

Agents must translate human-readable requests into the correct repository workflow.
Do not require the user to name file paths, runner commands, packet names, or
stage contracts when the intent is clear.

When the user asks for fresh Gearbox collateral research, asset diligence,
oracle/feed analysis, Credit Account opening analysis, or an `Analyze → Propose`
assessment:

1. Treat the request as a workflow-harness task, not as an ad hoc memo.
2. Read `dev/implementation/workflow-entrypoint/run-workflow-usage.md`.
3. Convert the user's provided asset/feed/risk parameters into a temporary
   repo-local input under `dev/implementation/workflow-harness/tmp/inputs/`.
4. Run `dev/tools/run_workflow.py analyze-propose` in scaffold mode.
5. Open the generated `.workflow/agent-handoff.md` and follow the generated
   packets for deliverables, validation, final response shape, and next-action
   suggestions.
6. Keep Preview and Execute out of scope unless the user explicitly requests
   them and the generated gates allow them.
7. Do not persist asset-specific scratch inputs or generated run artifacts as
   canonical fixtures or docs unless the user explicitly asks.

The harness is the routing and validation interface. A normal user prompt such
as “run fresh Gearbox Analyze → Propose research for these two collateral
assets” is sufficient; the agent is responsible for discovering and operating
the harness from the repository instructions.

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
      mechanics/
        oracle-and-liquidity-risk.md
        token-and-curator-risk.md
        allocation-and-action-palettes.md
        credit-account-risk-controls.md
        agent-continuity-log.md
      workflows/
        oracle-analysis/
          executable oracle graph / methodology workflow
        asset-investment-diligence/
          executable token / PT diligence workflow

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
- stable mechanics and executable diligence workflows needed by those flows.

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
- `user/references/mechanics/credit-account-risk-controls.md`
- `user/references/workflows/asset-investment-diligence/` when candidate diligence is needed
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

### `user/references/mechanics/`

Stable product mechanics that are neither router pages nor executable workflows. Use this subtree for reusable explanations, risk mechanics, action vocabularies, and agent-state concepts that multiple flows can link to without carrying long appendix sections inline.

Current mechanics files:

- `oracle-and-liquidity-risk.md` — oracle categories, liquidity-cascade versus liquidity-trap mechanics, and LP / Credit Account oracle drill triggers.
- `token-and-curator-risk.md` — per-token risk rubrics and curator trust / operating-discipline mechanics.
- `allocation-and-action-palettes.md` — allocation, LP action, Credit Account action, route-selection, and Emergency-mode palettes.
- `credit-account-risk-controls.md` — IRM sensitivity, HF floor reasoning, issuer-controlled collateral, adapter routing, CM envelope, KYC-gated execution, multicall Preview, and HF attribution.
- `agent-continuity-log.md` — previous-check state for LP and Credit Account monitoring.

Do not put multi-stage data mining, subagent orchestration, source compilation, or underwriting runbooks in mechanics files. If a mechanics section becomes an executable procedure, promote it into `user/references/workflows/<workflow-name>/` and link to it from the relevant flow.

### `user/references/workflows/`

End-agent executable reference workflows. Use this subtree for procedures an agent can run directly during opportunity evaluation, monitoring review, or strategy diligence.

Workflow packages may include stage graphs, worker contracts, subagent prompts, context controls, examples, and validation runbooks. One-off evidence, reports, and verification outputs still live under a run artifact root such as `dev/implementation/<run-slug>/`.

### `user/references/workflows/oracle-analysis/`

End-agent executable reference workflow for oracle setup analysis. It parses a feed as a recursive dependency graph, classifies each node as market / fundamental / NAV / hardcoded / hybrid, audits source primitives such as Chainlink, Curve, Pendle, ERC4626, issuer reports, and fixed scalars, then produces a protocol-fit memo for Gearbox, Morpho, or another lending market.

Oracle conclusions must be side-specific. The same feed can be borrower-friendly and LP-unfriendly, or LP-protective and borrower-unfriendly. The workflow must name the position side, token role, stress direction, and loss bearer before writing a verdict.

For Gearbox scopes, use `user/references/workflows/oracle-analysis/gearbox-price-feed-parsing.md`, which grounds PFS and feed-type parsing in the official curator price-feed configuration guide.

Run this workflow whenever oracle methodology fit cannot be answered by a single feed label, especially for Gearbox composite / bounded / ERC4626 / Curve TWAP / Pendle factory / main-reserve setups or when comparing Gearbox oracle risk against a simpler market.

### `user/references/workflows/asset-investment-diligence/`

End-agent executable reference workflow for token / Pendle PT diligence. It belongs under `user/` because the agent can run it directly during opportunity evaluation, not only while implementing the product.

### `dev/implementation/`

Human-readable implementation handoff compiled from canonical runtime docs. This is the backend / MCP data-architecture layer derived from product flows, not the runtime agent reasoning layer.

Use `Data requirements and to-dos.md` as the single backend / MCP architecture map. It should stay readable by a product owner and useful to backend builders: product flow → repeated user / agent question → deterministic facts → entities / methods → missing data → build order.

Do not add UI-card taxonomies or agent verdict schemas here. Backend / MCP methods should expose deterministic facts, histories, event feeds, source/freshness envelopes, previews, and receipts. Agent-specific verdicts, threshold interpretation, recommendations, and final user copy stay in the agent / product layer.

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
