# M4 review — combined post-Discover Analyze → Propose flow harness and stage prompts

Scope: formal review of `dev/implementation/workflow-harness/m4-agentic-flow-plan.md` only. This review checks missing formal checks, unsafe scope boundaries, fixture and acceptance adequacy, and false-pass risk. It does not assess token economic quality, oracle correctness, allocation suitability, or whether any candidate asset should be used.

## Checked inputs

- `CLAUDE.md` — canonical loop, user/dev split, Preview / Execute boundary, linking conventions, and validation expectations.
- `dev/implementation/workflow-harness/m4-agentic-flow-plan.md`.
- `dev/implementation/workflow-harness/plan-review.md`.
- `dev/implementation/workflow-harness/hardened-plan.md`.
- `dev/implementation/workflow-harness/m1-validator-core-plan.md`.
- `dev/implementation/workflow-harness/m2-asset-checks-plan.md`.
- `dev/implementation/workflow-harness/m5-fixtures-docs-plan.md`.
- `user/references/workflows/asset-investment-diligence/output-structure.md`.
- `user/references/workflows/oracle-analysis/output-structure.md`.
- Gearbox front-knowledge-base formal workflow critic and runtime workflow placement references.

## Executive verdict

Not approved for implementation as written.

The slice has the right product boundary: it stays in formal workflow compliance, keeps Preview and Execute blocked after unresolved Analyze gates, avoids live data calls, and avoids creating a new reusable combined workflow package. However, the plan still allows false passes in the exact area this slice is meant to protect: parent/child status reconciliation, child-validator import, parent-return fields, override handling, and fixture-backed acceptance.

## P1 findings

### P1-1 — Child status reconciliation is under-severed and not fully machine-checkable

Evidence:

- The M4 plan makes parent status reconciliation a P2 hardening check: `flow.status_reconciles_children` says the parent Propose status is not more permissive than child root status (`m4-agentic-flow-plan.md:131-135`).
- The same plan requires child prompts to return `status`, `run_artifact_root`, `final_verification`, `blocked_scopes`, `review_required_scopes`, `dominant_blockers`, and `live_input_blockers` (`m4-agentic-flow-plan.md:28-36`).
- The asset and oracle output contracts already define parent-agent return status and blocker summaries (`asset-investment-diligence/output-structure.md:151-176`; `oracle-analysis/output-structure.md:159-182`).

Risk:

A combined run can appear to pass while a child run is `review_required` or `blocked`, as long as the parent handoff text looks safe enough. That is not a P2 polish issue; it is a P1 false-pass risk because the parent may mark Propose or Preview more permissive than the analyzed child artifacts allow.

Blocking fix:

- Promote `flow.status_reconciles_children` to P1.
- Define the exact child status sources the combined validator trusts: child validator JSON reports, child final verification files, and/or child parent-return JSON/handoff fields.
- Require the combined report to import child P0/P1 status and unresolved blocker fields into the parent status calculation.
- Fail or return `review_required` if either child validator still emits deferred checks such as `validator.workflow_checks_deferred`.
- Add an acceptance assertion where one child is `review_required` or `blocked` and the parent attempts `ready_for_preview`; expected result must include `flow.status_reconciles_children` and a nonzero exit.

### P1-2 — `flow.child_*_validation_runs` does not define how child validation is run or imported

Evidence:

- The plan requires `flow.child_asset_validation_runs` and `flow.child_oracle_validation_runs`, described as child roots being validated or their P0/P1 findings imported (`m4-agentic-flow-plan.md:115-116`).
- It does not define whether M4 calls the child validator internally, requires existing child harness report files, accepts `--child-report` inputs, or parses child final verification sections.
- The acceptance commands cover a good combined run, missing handoff, unresolved-gate mutation, prompt-doc terms, and diff hygiene (`m4-agentic-flow-plan.md:176-296`), but they do not prove child P0/P1 import.

Risk:

An implementation can satisfy the combined-root shape with child directories present while never validating those child artifacts. The combined report would then be a stage-handoff parser, not a true post-Discover Analyze → Propose harness.

Blocking fix:

- Add a concrete child-validation import contract. For example: run asset/oracle validator functions in-process against `asset-investment-diligence/` and `oracle-analysis/`, or require `verification/workflow-harness-report.json` under each child root and validate its command evidence and status.
- Namespace imported child findings so the combined report can cite exact child workflow, path, severity, and check ID.
- Specify status calculation: child P0 → combined `fail`; child P1 → combined `review_required`; child P2 may remain pass unless strict warnings are enabled.
- Add one acceptance case where a child report contains P1/P0 findings and the parent handoff is otherwise well formed; expected combined status must not be `pass`.

### P1-3 — The required good fixture is not available, and M4 forbids creating it

Evidence:

- The plan cites a known-good parent handoff at `dev/implementation/sample-base-token-sample-vault-token-agentic-analyze-propose-2026-06-05/agentic-flow/analyze-and-propose.md` (`m4-agentic-flow-plan.md:17`), but this checkout has no `analyze-and-propose.md` or `good-agentic-sample-assets` fixture under `front-knowledge-base`.
- M4 acceptance requires `dev/tools/workflow_harness/fixtures/good/good-agentic-sample-assets` (`m4-agentic-flow-plan.md:185-194`, `m4-agentic-flow-plan.md:206-214`, `m4-agentic-flow-plan.md:234-247`).
- The M4 edit boundary allows only `dev/tools/validate_workflow_run.py` plus two prompt files (`m4-agentic-flow-plan.md:19-37`) and explicitly says not to edit historical run artifacts (`m4-agentic-flow-plan.md:38-42`).
- The separate M5 plan is the slice that creates `dev/implementation/workflow-harness/fixtures/good/good-agentic-sample-assets` and the bad fixture battery (`m5-fixtures-docs-plan.md:37-50`).

Risk:

The implementation worker either cannot run M4 acceptance as written, fabricates a fixture outside the allowed edit set, or silently relies on a later M5 task. That makes M4 non-executable as an independent implementation brief.

Blocking fix:

Choose one explicit dependency model:

1. Make M4 depend on the fixture slice and state that the implementation must block until the fixture battery exists; or
2. Expand M4's allowed edit set to create the minimal combined fixture and tests it needs; or
3. Rewrite M4 acceptance to build temporary synthetic combined roots inside subprocess wrappers from the existing child sample roots, and state that no persistent fixtures are added in M4.

Do not leave acceptance commands pointing at a fixture path that this slice cannot create and that is absent in the current checkout.

### P1-4 — Human override bypass is undefined

Evidence:

- `flow.preview_execute_blocked_when_unresolved` allows Preview and Execute to be non-blocked if a “local explicit human-override artifact is present and linked from the handoff” (`m4-agentic-flow-plan.md:126`).
- The plan does not define the override file name, schema, required fields, permitted gate scope, signature/approval evidence, or whether an override can ever make Execute ready without a signed execution package.

Risk:

A vague link or empty file can become a bypass for unresolved support, eligibility, feed, route/depth, wallet, Credit Manager envelope, user-policy, or live-input gates. That undermines the Preview / Execute boundary in `CLAUDE.md`.

Blocking fix:

- Either remove the override exception from M4 and always require Preview/Execute blocked while unresolved gates remain, or define a strict local override schema.
- If an override is allowed, require it to live under the run root, name the exact gates it overrides, include the human decision source, timestamp, scope, and reason, and state that Execute still requires a signed execution package or pre-authorized scoped bot policy.
- Add a negative acceptance case for a missing/empty/malformed override artifact and, if override support remains in scope, a minimal positive case that proves only the named gate is overridden.

### P1-5 — Acceptance assertions are fragile and inconsistent with the report schema

Evidence:

- The missing-handoff and unresolved-gate wrappers read `finding['check_id']` (`m4-agentic-flow-plan.md:218-220`, `m4-agentic-flow-plan.md:251-254`).
- The M1 report schema uses `id` for findings/check entries, while later M5 acceptance defensively reads `finding.get('id') or finding.get('check_id')` (`m1-validator-core-plan.md:152-174`; `m5-fixtures-docs-plan.md:233-239`).
- The unresolved-gate mutation uses plain string replacements without asserting that each replacement actually changed the handoff (`m4-agentic-flow-plan.md:238-243`).
- The acceptance suite has no assertion that the good fixture exists before copy/mutation, no assertion that the validator actually emitted a machine-readable combined report schema, and no assertion that `--format json,markdown` writes/prints both formats predictably.

Risk:

The tests can fail because of schema mismatch rather than validator behavior, or worse, pass against an unmutated fixture because the replacement strings did not match the fixture text.

Blocking fix:

- Align acceptance with the canonical report schema before implementation. Prefer `finding.get('id') or finding.get('check_id')` until all milestone plans use one field name.
- In every mutation wrapper, assert that the source text contains the expected strings and that the mutated text differs from the source.
- Add a report-shape assertion for `workflow`, `run_root`, `status`, `exit_code`, `summary`, `findings`, and check/result arrays if present.
- Specify the behavior of `--format json,markdown`: stdout JSON only with markdown written to a path, or two files via `--write-verification`; avoid ambiguous mixed stdout.

### P1-6 — Gate keyword coverage can miss common blocking wording

Evidence:

- The unresolved gate detector only names status markers such as `unknown`, `missing`, `unresolved`, `not supplied`, `review_required`, `blocked`, `must check`, and `requires` (`m4-agentic-flow-plan.md:137-150`).
- The same section says false positives are acceptable because safe output is `request_more_inputs` or blocked Preview/Execute (`m4-agentic-flow-plan.md:150`).

Risk:

Common formal blocker wording can still false-pass: `unsupported`, `not enabled`, `unavailable`, `not verified`, `to be confirmed`, `TBD`, `no route`, `no quote`, `no active market`, `no Credit Manager`, `not eligible`, `cannot determine`, and `insufficient data`.

Blocking fix:

Expand the conservative marker list and add at least one negative acceptance mutation using blocker wording that does not contain the current keywords, for example `Gearbox support unsupported` or `wallet eligibility not verified`.

## P2 findings

### P2-1 — Markdown bullet versus JSON stage status precedence is unspecified

Evidence:

- The plan accepts the existing markdown bullet format and may also accept a fenced JSON block (`m4-agentic-flow-plan.md:56-102`).
- It does not specify precedence or failure behavior when both are present but disagree.

Recommended fix:

Define parser precedence. A safe rule is: if JSON is present, validate it strictly; if markdown is also present and conflicts with JSON, emit P1. If no JSON exists, accept the normalized markdown bullets.

### P2-2 — Parent index mapping is too broad to prove final-verification traceability

Evidence:

- `flow.parent_index_maps_children` only says the parent `index.md` or `README.md` links to asset, oracle, and agentic-flow outputs (`m4-agentic-flow-plan.md:114`).

Recommended fix:

Require links to the child final verification files or child harness reports, not only child folders. This keeps the combined parent index from satisfying the check with shallow directory links.

## Approval blockers

Implementation should not start until these fixes are made in the M4 plan:

1. Promote child/parent status reconciliation to P1 and make child status/blocker sources machine-checkable.
2. Define the exact child validation import contract and add acceptance for imported child P0/P1 findings.
3. Resolve the missing fixture dependency by depending on M5, expanding M4 fixture scope, or using temporary fixtures in acceptance wrappers.
4. Define or remove the human-override bypass for Preview/Execute blockers.
5. Align acceptance wrappers with the report schema and assert fixture mutation success.
6. Expand gate keyword coverage and add a negative fixture/assertion for currently missed blocking wording.

## Final review decision

approved: false

Reason: the plan is directionally sound but still permits formal false passes in child-validation import, parent/child status reconciliation, override handling, and unresolved-gate detection, and its acceptance commands depend on absent fixtures outside the M4 edit boundary.
