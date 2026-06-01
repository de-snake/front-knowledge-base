# Three-layer progressive disclosure (Glance / Analyze / Act)

Inside every monitoring or management session, the user wants a three-layer structure:

| # | Layer | Description |
| --- | --- | --- |
| 1 | **Glance** | two-second answer to "Am I safe? Am I making money?" on a single screen, no navigation. |
| 2 | **Analyze** | drill into _why_ the glance answers look the way they do: risk charts, PnL breakdown, history, governance feed. |
| 3 | **Act** | execute a specific change with before/after evidence. |

This is orthogonal to the six-stage loop: the loop describes the decision lifecycle, the three-layer structure describes how any single screen should be organised.

## Glance content per persona

The Glance verdict is anchored on the named Stage 6 monitoring questions in each persona's canonical ownership flow.

### Pool LP

| Layer | Content | Source |
| --- | --- | --- |
| Glance | Yield: organic / incentive / floor + 30d trend. Exit feasibility: available liquidity vs position size, utilisation 30d trend. Three further "no change / changed" verdicts: composition, governance, bad-debt canary. | [[Pool monitoring]] Stage 6 questions Q1–Q5. |
| Analyze | Yield decomposition + 90d series; full exposure chain pool → CMs → tokens → insurance; exit feasibility with IRM curve; curator trust frame; parameter change log + pending governance. | [[Pool deposit]] Stage 2 questions Q1–Q5. |
| Act | Top-up, partial exit, full exit. | [[Pool monitoring]] Stage 3 Action Committee. |

### CA operator

| Layer | Content | Source |
| --- | --- | --- |
| Glance | Q1 "Am I safe?" — Health Factor + plain-language label, liquidation distance, time-to-liquidation, LT-ramp status, forbidden-tokens overlap (visible in < 3 s). Q2 "Am I making money?" — Net APY, total return in underlying + %, 30d account-value sparkline (visible in < 5 s). | [[Credit Account monitoring]] Stage 6 questions Q1–Q2. |
| Analyze | Composition, debt breakdown, leverage, strategy description; contextual recommendations; chronological action log; full economics dossier; collateral safety dossier; curator + CM constraints; parameter change log + pending governance. | [[Credit Account monitoring]] Stage 6 questions Q3–Q5; [[Credit Account opening]] Stage 2 dossiers. |
| Act | Add collateral, Reduce leverage, Increase leverage, Change strategy, Partial exit, Full exit, Handle emergency, RWA compliance check. | [[Credit Account monitoring]] Stage 3 Action Committee. |

## Benchmarks file as Glance verdict source

[[Benchmarks and tresholds for metrics]] is the source of Glance verdict inputs, but most rows are Analyze-tier evidence rather than Glance content directly.

The CA section's "Overview or advanced" column already encodes this split: rows tagged **overall** (e.g. Health Factor itself) are Glance candidates; rows tagged **advanced** (e.g. HF 30d trend) are Analyze candidates. Rows with empty Overview-or-advanced cells default to Analyze unless they collapse cleanly into a verdict line. The convention should be applied to the Pool side as well.

Consequence for surfacing: a literal Glance UI does not surface every Benchmarks row as a chip. The likely render is the persona's named Glance questions (5 for Pool LP, 2 for CA operator) reduced to a green / yellow / red verdict each, with the contributing Benchmarks rows accessible one tap deeper inside Analyze.

## Agent vs human surfacing

Agents follow the same Glance / Analyze / Act hierarchy as humans — verdict first, then analysis, then action recommendation — but the format differs:

- **Agent**: raw values + a verdict token (e.g. `green` / `yellow` / `red`) + a structured action proposal. No plain-language wrapper required.
- **Human**: the same fields rendered with a plain-language translation alongside the raw value (per [[Credit Account monitoring]]'s plain-language metric pairs — every raw metric is paired with a translation for the human-facing glance). Visual cues (colour, sparkline, chip) carry the verdict.

Both surfaces draw from the same schema; the divergence is in render, not in data.
