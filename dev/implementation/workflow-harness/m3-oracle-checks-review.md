# M3 review — oracle-analysis harness checks

Scope: review `dev/implementation/workflow-harness/m3-oracle-checks-plan.md` for formal workflow-compliance coverage only. This review does not assess oracle economic quality, token investment quality, or whether any live oracle conclusion is correct.

## Checked inputs

- `CLAUDE.md`.
- `dev/implementation/workflow-harness/m3-oracle-checks-plan.md`.
- `dev/implementation/workflow-harness/plan-review.md`.
- `user/references/workflows/oracle-analysis/output-structure.md`.
- `user/references/workflows/oracle-analysis/stage-contracts.md`.
- `user/references/workflows/oracle-analysis/gearbox-price-feed-parsing.md`.
- Gearbox front-knowledge-base formal workflow critic and runtime-workflow placement references.

## Executive verdict

Not approved for implementation as written.

The plan is directionally strong: it keeps the edit boundary narrow, includes manifest-to-scope reconciliation, requires side-specific oracle verdict fields, forbids top-level-label-only conclusions, and wraps expected negative fixture exits. However, it still permits formal false passes for canonical final-verification drift, root status contradictions, missing top-level index/README contract sections, missing formula evidence, weak source-primitive audits, and incomplete Gearbox PFS context.

## P1 findings

### P1-1 — Canonical final-verification path is weakened

Evidence:

- The oracle workflow contract names `verification/final-oracle-analysis-verification.md` as the run-level final verification file in the canonical folder shape and manifest contract (`output-structure.md:48-49`, `output-structure.md:110-112`).
- The plan requires `final_verification` to resolve to `verification/final-oracle-analysis-verification.md` **or another declared run-level final verification file under the run root** (`m3-oracle-checks-plan.md:102-103`).

Risk:

A run could pass by declaring a different final verification path while omitting the canonical file that downstream agents and runbooks expect.

Blocking fix:

Require the canonical `verification/final-oracle-analysis-verification.md` path. If the implementer wants to allow additional verification files, treat them as supplementary and still require the canonical file and manifest value.

### P1-2 — Root status reconciliation is not defined

Evidence:

- The manifest and parent-agent return contract expose run status and per-scope status (`output-structure.md:95-111`, `output-structure.md:159-179`).
- The plan only checks that status strings are known (`m3-oracle-checks-plan.md:297-299`). It does not require manifest, index, final verification, and per-scope verification statuses to reconcile.
- The prior formal review made root status / blocker reconciliation an approval blocker for the harness family (`plan-review.md:45-59`, `plan-review.md:177-185`).

Risk:

The harness could pass a run whose manifest or index reports `pass` while a scope is `blocked` or `review_required`, or while the final verification reports unresolved blockers.

Blocking fix:

Add an oracle-specific reconciliation check that compares:

- manifest root status or declared validation status;
- every `scopes[].status`;
- `index.md` validation result;
- per-scope `verification/oracle-analysis-verification.md` statuses;
- run-level final verification status.

The rule should fail or require review when any root artifact upgrades unresolved `blocked` / `review_required` scope state to `pass`.

### P1-3 — Required `index.md` and `README.md` sections are not checked

Evidence:

- `index.md` must contain a scope table, feed formulas, side-specific verdict matrix, open blockers, artifact map, and validation result (`output-structure.md:115-130`).
- `README.md` must state what was analyzed, where the manifest is, where token or PT folders are, which files to read first, and final validation status (`output-structure.md:132-140`).
- The plan requires the files to exist and the manifest `final_index` to resolve, but it does not check these required sections (`m3-oracle-checks-plan.md:102`, `m3-oracle-checks-plan.md:146-153`).

Risk:

A run can pass with a valid folder tree but a top-level handoff that omits the validation result, blocker surface, or side-specific verdict matrix. That violates the formal workflow contract and makes downstream review brittle.

Blocking fix:

Add `oracle.index_contract_sections` and `oracle.readme_handoff_sections` checks, or explicitly mark top-level handoff content validation out of scope and move the check to a named dependent slice. Since M3 already validates oracle run shape, the safer fix is to include the checks here.

### P1-4 — Formula presence is only checked indirectly through final verification credibility

Evidence:

- The stage contract requires the feed graph to reach primitives and reconstruct the formula in human terms (`stage-contracts.md:140-145`).
- The node-classification stage requires a `Formula` section and explanation of every formula operation (`stage-contracts.md:162-173`).
- The plan checks recursive graph shape and top-level-label failures (`m3-oracle-checks-plan.md:177-185`, `m3-oracle-checks-plan.md:280-282`), but it does not define a direct check that `oracle/feed-graph.md` or `oracle/node-classification.md` contains a formula.
- The only formula reference appears inside the final-verification credibility list (`m3-oracle-checks-plan.md:161-173`).

Risk:

A run can pass if the final verification claims formula coverage while the actual graph/classification artifacts omit the formula. This is the same heading-overclaim failure class the harness is meant to prevent.

Blocking fix:

Add a direct `oracle.pricing_formula_present` or equivalent check against `oracle/feed-graph.md` and `oracle/node-classification.md`. Add a negative fixture where the graph has child feeds but omits formula evidence.

### P1-5 — Source-primitive audit check is too permissive

Evidence:

- The stage contract requires every leaf primitive to be covered, every timestamp or reporting cadence to be recorded, every issuer/reporting trust assumption to be explicit, and DEX/TWAP primitives to include liquidity/manipulation surface (`stage-contracts.md:194-199`).
- The plan accepts at least one marker among source address, source type, timestamp/cadence, trust note, or raw evidence pointer (`m3-oracle-checks-plan.md:202-212`).

Risk:

An audit row with only an address or only a source type could pass while omitting timestamp/cadence, trust/admin methodology, and liquidity/manipulation evidence. That is not enough for formal oracle workflow compliance.

Blocking fix:

Strengthen `oracle.source_primitive_audit_present` into a minimum field set:

- all leaf primitives named in graph or probes have an audit entry;
- each entry has source identity and source type;
- each entry has timestamp, reporting cadence, or explicit unavailable marker;
- each entry has trust/admin/methodology note or explicit unavailable marker;
- DEX/TWAP entries require liquidity/manipulation evidence or explicit unavailable marker;
- raw evidence absence requires a reason.

Add a negative fixture for weak source evidence, not only missing evidence.

### P1-6 — Gearbox PFS / Instance Owner context is not enforced

Evidence:

- The Gearbox parsing reference states that the Price Feed Store (PFS) is chain-specific, tokens must be added to PFS before use as collateral, only the chain-specific Instance Owner multisig can add or update PFS entries, and PFS status is availability context rather than a risk conclusion (`gearbox-price-feed-parsing.md:7-12`).
- The plan requires several Gearbox protocol-fit fields, but it does not require PFS availability or Instance Owner context (`m3-oracle-checks-plan.md:253-268`).

Risk:

A Gearbox oracle run could satisfy main/reserve feed and Liquidation Threshold fields while omitting whether the feed is actually available through PFS and who can update that availability. That is a formal availability/control gap, not an economic-quality judgment.

Blocking fix:

Extend `oracle.gearbox_fields_present` to require explicit rows or `unknown` markers for:

- PFS chain / token availability status;
- Instance Owner or feed-update authority;
- PFS add/update status when the feed is new or pending.

## P2 findings

### P2-1 — Side-specific verdict applicability is too discretionary

Evidence:

- The plan requires borrower, pool LP, liquidator, and curator/operator splits only when relevant to market design, and allows `not_in_scope` for liquidator or curator/operator when explained (`m3-oracle-checks-plan.md:242-251`).
- The workflow contract requires the side-specific verdict matrix in the index and requires final conclusions to name position side, token role, stress direction, and loss bearer (`output-structure.md:121-127`, `stage-contracts.md:47-58`).

Risk:

The phrase `when relevant to the market design` leaves too much implementer discretion. The harness could skip liquidator or curator/operator verdict checks without a deterministic trigger.

Recommended fix:

Define deterministic applicability from manifest fields and protocol context:

- require every side listed in `position_sides`;
- require borrower and pool LP rows when either side is in scope for a lending-market run;
- require liquidator and curator/operator rows for Gearbox unless `scope.json` explicitly marks them `not_in_scope` with a reason.

### P2-2 — The negative fixture matrix does not cover all newly required blocker classes

Evidence:

- The fixture matrix covers missing manifest field, missing final verification, missing per-scope file, missing source evidence, missing conclusion quad, missing cascade/trap, missing Gearbox fields, and top-level-label-only verdict (`m3-oracle-checks-plan.md:301-317`).
- It does not cover noncanonical final-verification path, root status contradiction, missing index/README sections, missing formula evidence, or weak source-primitive audit fields.

Risk:

Even if the implementation adds the missing checks, acceptance could still pass without proving the highest-risk false-pass cases.

Recommended fix:

Add required negative fixtures for:

- `oracle-bad-noncanonical-final-verification`;
- `oracle-bad-root-status-contradiction`;
- `oracle-bad-missing-index-section`;
- `oracle-bad-missing-formula`;
- `oracle-bad-weak-source-audit`.

## Positive coverage notes

The following parts of the plan are implementation-ready and should be preserved:

- Narrow edit boundary: `dev/tools/validate_workflow_run.py` plus optional oracle fixtures only (`m3-oracle-checks-plan.md:32-50`).
- Manifest-to-scope path reconciliation, including no absolute or parent-escaping `artifact_dir` paths (`m3-oracle-checks-plan.md:119-128`).
- Side-specific conclusion quad check (`m3-oracle-checks-plan.md:229-240`).
- Top-level-label-only verdict rejection (`m3-oracle-checks-plan.md:280-282`).
- Asserted negative-fixture wrapper that checks nonzero exit and expected check IDs (`m3-oracle-checks-plan.md:332-370`).

## Blocking fixes before implementation

1. Require canonical `verification/final-oracle-analysis-verification.md`; do not accept an arbitrary replacement final verification path.
2. Add root / scope / index / final-verification status reconciliation.
3. Add top-level `index.md` and `README.md` contract-section checks.
4. Add direct formula checks for feed graph and node classification artifacts.
5. Strengthen source-primitive audit checks from one-marker presence to required identity, type, timestamp/cadence, trust/methodology, and primitive-specific evidence.
6. Add Gearbox PFS / Instance Owner availability-control fields.
7. Add negative fixtures for the new failure classes above.

## Final review decision

approved: false

Reason: the M3 brief is close, but it still permits formal false passes in canonical final-verification pathing, status reconciliation, top-level handoff content, formula evidence, source-primitive audit credibility, and Gearbox PFS/control context. These are blocker-level harness gaps because the implementation would otherwise claim deterministic oracle workflow compliance while missing required workflow-contract fields.
