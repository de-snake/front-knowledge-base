# Workflow entrypoint runner

This page documents the smallest supported command for the Analyze → Propose workflow harness. The runner is a scaffold and validation bridge only. It does not launch agents, perform live research, infer asset suitability, infer oracle correctness, or unlock Preview / Execute.

## Minimal command

For a fresh human-requested run, create a temporary repo-local input file under
`dev/implementation/workflow-harness/tmp/inputs/` from the user's supplied
parameters. Do not save one-off asset inputs under `dev/inputs/` or promote them
to permanent fixtures unless explicitly requested.

```bash
python3 dev/tools/run_workflow.py analyze-propose \
  --input dev/implementation/workflow-harness/tmp/inputs/<scope>.json \
  --mode scaffold \
  --agent generic \
  --format markdown
```

The command creates one deterministic parent run root under `dev/implementation/` unless `--run-root` is supplied. It also creates:

- `asset-investment-diligence/` child root
- `oracle-analysis/` child root
- `.workflow/plan.json`
- `.workflow/registry.json`
- `.workflow/execution-graph.json`
- `.workflow/packets/<workflow>/*.json`
- `.workflow/packets/<workflow>/*.md`
- `.workflow/next-action.json`
- `.workflow/next-action.md`

## Metadata-only parallelization guidance

The execution graph is a scheduling hint, not executable orchestration. `.workflow/execution-graph.json`, `.workflow/next-action.json.ready_packets`, `.workflow/next-action.json.blocked_packets`, and `.workflow/next-action.json.parallel_waves` describe which generated packets appear independent enough for a human or external graph-aware operator to consider next.

The runner itself must not launch workers, create Kanban cards, call `delegate_task`, start subprocesses, invoke an LLM, retry packets, or advance proposal gates from this metadata. `delegate_to_subagent: true` means only that the packet is a manual delegation candidate; it is not an instruction to spawn a subagent.

Legacy serial behavior remains supported. Consumers that do not understand graph metadata should keep reading `.workflow/next-action.json.first_packet`, then execute packets in `.workflow/registry.json` order. `first_packet` remains present with its existing shape and remains anchored to the serial registry order rather than being replaced by the first graph-ready packet.

If `.workflow/execution-graph.json` is missing, ignored, invalid, stale, or too strict, fall back to the serial path: use `first_packet`, read `.workflow/registry.json`, execute registry order, then run validation. Graph readiness never means formal validation passed, semantic review passed, the parent proposal is decision-grade, or Preview / Execute is allowed.

## Agent-specific packet launchers

Only the launcher text changes across supported agents. The `task_payload` is identical for `generic`, `codex`, `claude-code`, and `hermes`.

### Codex

```bash
python3 dev/tools/run_workflow.py analyze-propose \
  --input dev/implementation/workflow-harness/tmp/inputs/<scope>.json \
  --agent codex \
  --format markdown
```

Then give Codex the compact generated prompt from `.workflow/next-action.md`, which may include token addresses, feed addresses, and risk parameters:

```text
Open <run-root>/.workflow/agent-handoff.md. SampleBaseToken: token <address>, feed <feed>, SampleBaseToken LTV/LT context: 0.50; SampleVaultToken: token <address>, feed <feed>, SampleVaultToken LTV/LT context: 0.45; Borrow asset: SampleDebtToken, Borrow rate assumption: 5%; Analyze→Propose only; no Preview/Execute.
```

The problem to avoid is not inline parameters; it is pasting the full workflow/runbook/packet body into Codex. The handoff file points Codex to `.workflow/next-action.md`, `.workflow/registry.json`, packets, generated input files, and the validation command.

### Claude Code

```bash
python3 dev/tools/run_workflow.py analyze-propose \
  --input dev/implementation/workflow-harness/tmp/inputs/<scope>.json \
  --agent claude-code \
  --format markdown
```

Then give Claude Code the packet path from `.workflow/next-action.md`.

### Hermes

```bash
python3 dev/tools/run_workflow.py analyze-propose \
  --input dev/implementation/workflow-harness/tmp/inputs/<scope>.json \
  --agent hermes \
  --format markdown
```

Then give Hermes the packet path from `.workflow/next-action.md`.

## Validate an existing scaffold

After child artifacts are filled, validate the child roots and import validator findings into the parent next-action file:

```bash
python3 dev/tools/run_workflow.py analyze-propose \
  --input dev/implementation/workflow-harness/tmp/inputs/<scope>.json \
  --run-root <run-root-under-dev/implementation> \
  --mode validate \
  --resume \
  --format markdown
```

Validation writes:

- `.workflow/validation/summary.json`
- `.workflow/validation/summary.md`
- `.workflow/next-action.json`
- `.workflow/next-action.md`
- child validator reports under each child `verification/` directory

Exit semantics:

- `0`: deterministic checks pass and the next-action state is decision-grade for the requested mode.
- `1`: review is required. The runner completed, but validator or proposal-gate findings prevent treating the run as complete.
- `2`: blocked or input error. Required artifacts, inputs, or safety gates are absent or contradictory.

## Quality-gated validation model

The runner has two validation layers. Keep them separate in handoffs and final reports.

### Deterministic validation

`--mode validate` runs the declared child validators from `.workflow/registry.json` and then validates the parent `agentic-flow/analyze-and-propose.md`. These checks are mechanical: file existence, required headings, status blocks, JSON shape, local links, evidence-ledger fields, fact-state markers, proposal-gate fields, and status propagation from child reports to the parent next action.

Deterministic validation can reject:

- missing child or parent artifacts;
- missing final-verification files;
- broken run-local links;
- `not_investigated` facts presented as if they were searched;
- `investigated_no_result` claims without the required negative-search proof bundle;
- parent proposals that overrule blocked or review-required child reports;
- `ready_for_preview` or execution-like status when Preview / Execute are outside the Analyze -> Propose contract.

It does not judge whether the prose is useful, whether cited evidence is sufficient for a human decision, or whether a proposal is economically correct.

### Semantic critic gates

Use the semantic critic when deterministic validation passes but the artifact may still be low quality. The critic is independent from the producer and receives only a bounded request bundle: packet, stage contract, output artifacts, evidence ledgers, validator summary, rubric, and optional parent context.

For full-run validation, enable critic orchestration during `--mode validate`:

```bash
python3 dev/tools/run_workflow.py analyze-propose \
  --input dev/implementation/workflow-harness/tmp/inputs/<scope>.json \
  --run-root <run-root-under-dev/implementation> \
  --mode validate \
  --resume \
  --semantic-review \
  --semantic-critic-command "<independent-critic-command>" \
  --format markdown
```

For a single stage or fixture replay, run the critic directly:

```bash
python3 dev/tools/semantic_critic_runner.py \
  --packet <run-root>/.workflow/packets/<workflow>/<stage>.json \
  --output <stage-output.md> \
  --validator-summary <run-root>/.workflow/validation/summary.json \
  --rubric dev/implementation/workflow-harness/semantic-critic-rubric-v1.md \
  --critic-command "<independent-critic-command>" \
  --request-out <run-root>/.workflow/semantic/<stage>-request.json \
  --report-out <run-root>/.workflow/semantic/<stage>-report.json
```

Semantic statuses are `pass`, `review_required`, or `blocked`. A form-compliant artifact must still fail semantic review when it only fills headings, omits decision-grade evidence mapping, uses generic risk prose, skips required calculations, or says “monitor / investigate / validate” without owner, trigger, artifact, and next action. If no critic is run, record `semantic_review_status: semantic_review_unavailable`; do not relabel that as a pass.

## Investigation-result taxonomy

Packets and validator reports use reusable fact states rather than asset-specific prose. Use the exact state names in artifacts and evidence ledgers:

| State | Meaning | Gate effect |
| --- | --- | --- |
| `found` | The fact was found and supported by cited evidence. | Can support downstream analysis if evidence maps to the claim. |
| `not_applicable` | The fact does not apply under a named applicability rule and cited input evidence. | Acceptable only with rule and decision effect. |
| `input_missing` | The human or upstream context did not provide a required input. | Blocks exact decisions or routes to `request_more_inputs`. |
| `not_investigated` | The worker has not searched the required source space. | Non-decision-grade; do not treat as no result. |
| `investigated_no_result` | The worker searched the required source space and found no result. | Acceptable only with negative-search proof: registry/source checked, API or contract query attempted when relevant, network/context named, and run-local raw evidence path. |
| `source_unavailable` | A required source could not be reached or returned an error. | Requires source/error evidence and decision effect. |
| `source_inconclusive` | Sources were checked but did not resolve the fact. | Requires cited evidence and decision effect. |
| `contradicted` | Sources conflict or contradict the input. | Requires contradiction evidence and normally blocks proposal readiness. |

The critical distinction is `not_investigated` versus `investigated_no_result`. A missing Gearbox market, oracle route, liquidity venue, issuer fact, or source primitive is valid only after replayable negative-search evidence. If the worker did not search, keep the state as `not_investigated` and propagate the blocker.

## Parent proposal-gate statuses

The parent return must carry a status block with these fields: `formal_validation_status`, `semantic_review_status`, `workflow_decision_status`, and `proposal_gate`.

Use proposal gates as follows:

- `request_more_inputs`: validation or analysis identified exact missing inputs. Name each input and the decision it unlocks.
- `review_required`: deterministic checks ran, but unresolved P1 findings, weak semantic evidence, or non-blocking contradictions require human or reviewer action.
- `blocked`: P0 findings, missing required artifacts, unavailable critical sources, uninvestigated required facts, or child blocked status prevent the Analyze -> Propose handoff.
- `semantic_review_unavailable`: no independent critic report was run. This is not a pass and should stay non-decision-grade unless the operator explicitly scopes out semantic review.
- `ready_for_preview`: use only if the workflow contract explicitly allows Preview and every child report, semantic critic, execution package, and parent gate permits it. The current Analyze -> Propose harness normally blocks Preview / Execute.
- `pass` / `ready`: only for a fully validated Analyze -> Propose handoff with no material deterministic or semantic defects. This does not approve token economics or execution.

Never collapse these fields into a single “done” line. A run can have deterministic validation `pass` while semantic review is `review_required`, and the final proposal gate must reflect the stricter status.

## Operator input and fixtures

For real user-requested asset runs, use a temporary input path under
`dev/implementation/workflow-harness/tmp/inputs/` and a temporary run root under
`dev/implementation/workflow-harness/tmp/`. These scratch files are not
canonical docs or fixtures.

Entry-point test fixtures live under `dev/implementation/workflow-harness/fixtures/entrypoint-inputs/`:

- `sample-assets-minimal.json` — SampleBaseToken/SampleVaultToken Gearbox scaffold input.
- `missing-live-fields.json` — valid input with omitted live fields; packets must preserve them as blocking unknowns.
- `malformed-missing-assets.json` — stable `WE_ASSETS` input-error fixture.
- `path-escape-artifact-root.json` — stable `WE_PATH_ESCAPE` input-error fixture.

## Regression and smoke checks

Run the existing workflow-harness fixture matrix, generalized quality-gate regression suite, semantic-critic runner tests, and entrypoint tests:

```bash
python3 dev/tools/run_fixture_checks.py
python3 -m pytest dev/tools/workflow_harness/tests -q
```

To replay the synthetic low-quality form-fill trap directly:

```bash
python3 dev/tools/semantic_critic_runner.py \
  --packet dev/implementation/workflow-harness/fixtures/regression-evals/semantic-low-quality-form-fill/packet.json \
  --output dev/implementation/workflow-harness/fixtures/regression-evals/semantic-low-quality-form-fill/stage-output.md \
  --validator-summary dev/implementation/workflow-harness/fixtures/regression-evals/semantic-low-quality-form-fill/validator-summary.json \
  --critic-command "python3 dev/tools/workflow_harness/tests/semantic_fixture_critic_stub.py dev/implementation/workflow-harness/fixtures/regression-evals/semantic-low-quality-form-fill/critic-response.json"
```

The fixture checks prove routing and gate behavior, including low-quality semantic rejection and `investigated_no_result` / `not_investigated` separation. They do not judge token quality, oracle quality, allocation suitability, or execution merit.

## Production enablement and rollback

Do not enable graph-aware production operation until every gate in `dev/implementation/workflow-harness/SAFE_PARALLELIZATION_KANBAN.md` passes: fixture checks and the workflow-harness pytest suite are green, the dry-run report is accepted, validator status and finding counts do not regress against the legacy graph-absent baseline, no automatic subagent or worker orchestration exists, and old `first_packet` / registry-order consumers remain supported.

Rollback is intentionally data-only. Ignore or delete `.workflow/execution-graph.json` and ignore `ready_packets`, `blocked_packets`, and `parallel_waves` in `.workflow/next-action.json`; then operate from `first_packet` and `.workflow/registry.json` in serial registry order. Validators must continue to accept graph-absent legacy runs, so deleting graph metadata must not require code or fixture migration.
