# Workflow semantic critic rubric v1

Schema version: `workflow-semantic-critic-rubric-v1`

Purpose: evaluate semantic stage quality that deterministic validators cannot judge. Deterministic checks prove file shape, links, status tables, and required markers. This rubric judges whether the artifact is actually decision-useful.

## Independence and fixture scope

The critic must be independent from the producer. Judge only the bounded packet, stage contract, output artifacts, evidence ledger, validator summary, and parent context provided in the request bundle. Do not accept producer self-certification as evidence.

All examples use synthetic fixtures. They illustrate critic behavior only; they are not Gearbox policy, token-specific precedent, market recommendation, or execution approval.

## Status policy

Return `blocked` for any P0:

- The artifact makes or enables a Preview / Execute recommendation when the contract only allows Analyze -> Propose.
- A required decision, calculation, investigation, or proposal is absent and the absence prevents safe downstream use.
- The artifact invents addresses, APRs, prices, oracle verdicts, backing, liquidity, protocol parameters, or regulatory facts not supported by the evidence bundle.
- The critic adapter cannot produce structured JSON.

Return `review_required` for any P1:

- Headings are present but the body has no decision, calculation, investigation result, or actionable proposal.
- Evidence exists but does not support the quoted conclusion.
- `not found`, `unknown`, or `not applicable` appears without required search path, source failure, applicability rule, and decision effect.
- Quantitative sections provide formulas or labels without computed values, assumptions, sensitivity, or break-even logic when requested.
- Oracle/protocol-fit sections describe generic risks but omit side-specific implication.
- Parent context requires synthesis across child workflows and the artifact only restates child status.

Return `pass` only when no P0/P1 issue remains. `pass` means no material stage-quality defect found in the bounded bundle; it is not investment or execution approval.

## Rubric selection matrix

Apply every matching rubric:

| Rubric | Typical artifact |
| --- | --- |
| Investigation adequacy | source mining, protocol adapters, no-result claims, final verification |
| Evidence sufficiency | material claims, evidence ledgers, source-evidence files, parent synthesis |
| Asset diligence utility | technical reports, analyst reports, token / PT / issuer-controlled asset memos |
| Oracle/protocol-fit | feed graph, node classification, source audit, stress tradeoff, protocol-fit memo |
| Quantitative underwriting | methodology, investment analysis, scenario or risk/return memo |
| Parent proposal | Analyze -> Propose parent return, next-action state, final proposal gate |

## Rubric 1 — Investigation adequacy critic

Question: did the worker actually investigate mandatory facts and prove no-result claims?

Pass criteria:

- Every mandatory fact is resolved as `confirmed`, `investigated_no_result`, `source_unavailable`, `source_inconclusive`, `contradicted`, `input_missing`, or `not_applicable` with decision effect.
- `investigated_no_result` includes search space, exact methods/queries, sources checked, raw search log, and sufficiency rationale.
- `not_applicable` cites the applicability rule and input evidence; it is not a substitute for search.
- `not_investigated` appears only as an explicit failure state that blocks or requires review.

Examples (fixtures only):

| Status | Example |
| --- | --- |
| `pass` | Fixture token report records admin, issuer, transfer, liquidity, and oracle facts with ledger entries; absent market search has exact negative-search methods, raw log, sufficient search-space rationale, and `blocks_decision`. |
| `review_required` | Fixture worker says “no FixtureProtocol market found” after checking one web page, omitting adapter/API/RPC search path. |
| `blocked` | Fixture parent treats `not_investigated` issuer controls as “no controls found” and allows downstream proposal use. |

## Rubric 2 — Evidence sufficiency critic

Question: can a reviewer replay or audit every material claim?

Pass criteria:

- Every material address, parameter, APR/APY, price, liquidity, legal/issuer, governance, incident, and oracle claim cites a `fact_id`, raw evidence path, source quote, command/query, or validator artifact.
- The cited evidence supports the specific claim and decision effect; source lists without claim mapping are insufficient.
- Negative and unavailable results point to exact failed source, status/error/search log, and freshness basis.
- Parent artifacts cite child artifact paths or fact IDs rather than relying on prose summaries.

Examples (fixtures only):

| Status | Example |
| --- | --- |
| `pass` | Fixture analyst report maps each decision sentence to ledger `fact_id`s, source quotes, and freshness labels before using the claim in the recommendation boundary. |
| `review_required` | Fixture memo lists three sources but does not identify which one supports “redemption is weekly.” |
| `blocked` | Fixture analysis invents a collateral factor, oracle address, or APR absent from the request bundle. |

## Rubric 3 — Asset diligence utility critic

Question: does the memo translate evidence into decision implications rather than only list risks?

Pass criteria:

- States asset role, affected side, controls/permissions, transferability, redemption/settlement path, liquidity/exit feasibility, oracle dependency, governance/admin surface, and unresolved blockers when applicable.
- Converts findings into decision implications: analysis-only, request inputs, human review, block proposal, or acceptance criteria.
- For issuer-controlled, tokenized-security, redemption-window, or compliance-gated assets, unknown issuer, eligibility, freeze, transfer, redemption, or eligible-liquidator state prevents ordinary-liquid-collateral treatment.
- Risk severity follows evidence and stage context; it does not use universal green/yellow/red thresholds without policy basis.

Examples (fixtures only):

| Status | Example |
| --- | --- |
| `pass` | Fixture asset report allows Analyze-only review, names issuer/transfer unknowns as blockers, explains affected loss bearer, and lists evidence-backed acceptance criteria before proposal. |
| `review_required` | Fixture report lists “transfer risk, oracle risk, governance risk” but never says which fact changes suitability, monitoring, or next checks. |
| `blocked` | Fixture controlled-asset memo recommends ordinary-liquid-collateral treatment while eligibility and freeze state are unknown. |

## Rubric 4 — Oracle/protocol-fit critic

Question: are side-specific outcomes, token role, stress direction, loss bearer, and protocol grounding explicit?

Pass criteria:

- Names position side, token role, stress direction, and loss bearer before any verdict.
- Connects feed graph, node classification, source primitive evidence, update/staleness assumptions, bounds/scalars, and math reconstruction to the protocol decision.
- Distinguishes borrower, LP/lender, liquidator, curator/admin, and protocol-reserve effects where relevant.
- Accepts protocol-adapter or market/route absence only after adapter-defined no-result proof.
- Bounds verdict to the analyzed protocol and market context; no generic oracle safety label.

Examples (fixtures only):

| Status | Example |
| --- | --- |
| `pass` | Fixture oracle memo shows downside NAV lag for FixtureAsset collateral is lender-unfriendly under borrower default stress, names borrower/lender loss channels, and blocks protocol-fit until source primitive and market parameters are confirmed. |
| `review_required` | Fixture memo says “conservative oracle” without stating whether the stress protects lenders or harms borrowers for the tested token role. |
| `blocked` | Fixture memo allows protocol onboarding while feed source primitives, adapter route existence, or market parameters are not investigated. |

## Rubric 5 — Quantitative underwriting critic

Question: are required calculations/scenarios attempted, or are missing inputs handled with labelled scenario bands?

Pass criteria:

- Required calculations include numbers, units, formulas, assumptions, source references, and sensitivity or break-even logic.
- When the stage contract marks `scenario_allowed=true` because only user sizing/leverage/horizon/risk-policy inputs are missing, the artifact must produce labelled Analyze-only conservative/base/upside scenario bands; merely writing `skipped_due_to_missing_input`, blank fields, or a blocker without calculations is `blocked`.
- Missing non-scenario prerequisites such as token identity, oracle source, live price, liquidity source, or borrow-rate source must block exact underwriting instead of inventing scenario inputs.
- Missing user sizing, horizon, price, liquidity, or borrow-rate inputs either block exact underwriting or produce labelled non-executable scenario bands.
- Carry, borrow cost, fees, liquidity/exit, liquidation or margin stress, oracle stress, redemption/settlement timing, and downside cases are covered when material.
- Quantitative output does not imply Preview/Execute readiness unless the gate allows it and all inputs are available.

Examples (fixtures only):

| Status | Example |
| --- | --- |
| `pass` | Fixture memo computes base, downside, and severe bands from cited rates/liquidity; exact sizing is blocked because user horizon is missing, and the next check asks for horizon and risk budget. |
| `review_required` | Fixture page gives net APY and break-even formulas but leaves values blank or omits units/date/source. |
| `blocked` | Fixture analysis recommends exact position size or execution using made-up user capital, leverage, or liquidity inputs. |

## Rubric 6 — Parent proposal critic

Question: does the final proposal name blockers, acceptance criteria, next checks, and why Preview/Execute are blocked or allowed?

Pass criteria:

- Separates deterministic validation status, semantic review status, workflow decision readiness, and Preview/Execute gate status.
- Synthesizes child outputs into a decision; names blockers, acceptance criteria, next checks, owner/stage, and required evidence.
- Blocks Preview/Execute unless the contract allows them, child findings permit them, and execution-package integrity is available.
- For `request_more_inputs`, states exact inputs needed and what decision those inputs unlock.

Examples (fixtures only):

| Status | Example |
| --- | --- |
| `pass` | Fixture parent says validation passed but semantic review requires more evidence; blocks Preview/Execute, lists unresolved market/issuer facts, names acceptance criteria, and routes next run to the investigation stage. |
| `review_required` | Fixture parent says “asset and oracle checks complete; monitor and validate next” without acceptance criteria, owner, trigger, or next artifact. |
| `blocked` | Fixture parent allows Preview or Execute despite child `blocked` findings, missing semantic review, missing execution package, or unknown issuer/eligibility state. |

## Low-utility form compliance traps

Flag these even if deterministic checks passed:

- “All required headings are present” but bodies are placeholders, generic prose, or restatements of the prompt.
- Sources are named without quoting or mapping the relevant fact to the decision.
- A proposal says “monitor,” “investigate,” or “validate” without owner, trigger, artifact, or next action.
- A verification file claims pass while nearby artifacts still contain blockers or missing live inputs.
- A table has labels but no numbers, assumptions, or units.

## Required JSON output

The critic command must print one JSON object:

```json
{
  "status": "pass | review_required | blocked",
  "findings": [
    {
      "id": "semantic.short_stable_id",
      "status": "review_required | blocked",
      "severity": "P0 | P1 | P2",
      "violated_requirement": "Specific stage/rubric requirement violated",
      "evidence": {
        "path": "relative/path.md",
        "quote": "Short exact quote or artifact observation"
      },
      "required_remediation": "Concrete change needed before rerun"
    }
  ]
}
```

Use an empty findings array only for `pass`. Non-pass outputs must include at least one actionable finding.
