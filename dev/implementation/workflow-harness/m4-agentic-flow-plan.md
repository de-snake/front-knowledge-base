# M4 implementation brief — combined post-Discover Analyze → Propose harness

Purpose: implement only the combined-run guardrail for a token run where Discover has already happened and the parent agent runs Analyze → Propose before any Preview or Execute action. This is a formal workflow-compliance slice. It does not assess token economics, oracle quality, allocation suitability, or whether a candidate should be used.

This planning task changes only this file. The future implementation task must stay inside the exact edit list below unless a reviewer explicitly expands scope.

## Inputs reviewed

- `CLAUDE.md` — canonical loop, user/dev split, Preview / Execute boundary, and validation expectations.
- `dev/implementation/workflow-harness/plan.md` — original harness shape and combined-run check sketch.
- `dev/implementation/workflow-harness/plan-review.md` — review blockers for root status, parent-return, gate fixtures, and acceptance commands.
- `dev/implementation/workflow-harness/hardened-plan.md` — P3 hardened execution brief.
- `user/references/workflows/asset-investment-diligence/output-structure.md`.
- `user/references/workflows/oracle-analysis/output-structure.md`.
- `user/references/workflows/asset-investment-diligence/subagent-prompts.md`.
- `user/references/workflows/oracle-analysis/subagent-prompts.md`.
- Known good parent handoff: `dev/implementation/sample-base-token-sample-vault-token-agentic-analyze-propose-2026-06-05/agentic-flow/analyze-and-propose.md`.

## Exact implementation files to edit

Required:

1. `dev/tools/validate_workflow_run.py`
   - Add or complete `--workflow combined-analyze-propose` validation.
   - Do not add live RPC, explorer, web, X, Dune, or LLM calls.
   - Do not modify canonical workflow final-verification files.

2. `user/references/workflows/asset-investment-diligence/subagent-prompts.md`
   - Strengthen the final verification / handoff prompt so the asset run returns machine-checkable blocker fields to the parent combined flow.
   - Required returned fields: `status`, `run_artifact_root`, `final_verification`, `blocked_scopes`, `review_required_scopes`, `dominant_blockers`, and `live_input_blockers`.
   - Require any missing support, eligibility, route/depth, wallet, user-policy, or live-input gate to be returned as a blocker, not buried in prose.

3. `user/references/workflows/oracle-analysis/subagent-prompts.md`
   - Strengthen the optional verifier prompt so the oracle run returns machine-checkable blocker fields to the parent combined flow.
   - Required returned fields: `status`, `run_artifact_root`, `final_verification`, `blocked_scopes`, `review_required_scopes`, `dominant_blockers`, and `live_input_blockers`.
   - Require missing feed, source-primitive, route/depth, protocol-support, LT/LLTV, safe-pricing, user-policy, or live-input gates to be returned as blockers.

Not warranted in M4:

- Do not add a new `user/references/workflows/<combined-workflow>/` package in this slice. A reusable combined workflow package would require navigation updates to `README.md` and `CLAUDE.md`, which are outside this task's allowed edit set. The M4 docs change is limited to the two existing prompt files above.
- Do not edit historical run artifacts. Use fixtures or temporary copies for tests.

## Required parent artifact contract

For `--workflow combined-analyze-propose`, the run root is a parent folder with this minimum shape:

```text
<run-root>/
  README.md or index.md
  asset-investment-diligence/
  oracle-analysis/
  agentic-flow/
    analyze-and-propose.md
```

`agentic-flow/analyze-and-propose.md` is the parent-stage handoff. It must contain enough structured text for deterministic parsing. M4 should accept the existing known-good bullet format and may also accept a fenced JSON block for future runs.

Minimum accepted markdown shape:

```markdown
## Stage status

- Discover: complete by user premise | complete by agent | blocked
- Analyze: complete | review_required | blocked
- Propose: `request_more_inputs` | `blocked` | `ready_for_preview`
- Preview: blocked | ready | complete
- Execute: blocked | ready | complete
- Monitor: not started | active | blocked
```

The parser must normalize common punctuation and backticks, but it must not infer missing stages from prose. If any of the six canonical stages is absent, emit a P1 finding.

Preferred future structured block, if implementation wants a stricter path without breaking the existing fixture:

```json
{
  "schema_version": "agentic-analyze-propose-v1",
  "stage_status": {
    "Discover": "complete_by_user_premise",
    "Analyze": "complete",
    "Propose": "request_more_inputs",
    "Preview": "blocked",
    "Execute": "blocked",
    "Monitor": "not_started"
  },
  "analyze_artifacts": {
    "asset_final_verification": "asset-investment-diligence/verification/final-investment-analysis-verification.md",
    "oracle_final_verification": "oracle-analysis/verification/final-oracle-analysis-verification.md"
  },
  "unresolved_gates": [
    {
      "gate": "feed_support",
      "status": "missing_input",
      "requested_input": "Identify active Gearbox PFS/feed support for the candidate collateral."
    }
  ],
  "preview_gate": {"status": "blocked", "reason": "unresolved feed/support and wallet eligibility gates"},
  "execute_gate": {"status": "blocked", "reason": "Preview is blocked and no signed execution package exists"}
}
```

Do not require the JSON block for the first M4 implementation if the existing good fixture only has markdown bullets. The acceptance gate is the semantic contract, not the serialization format.

## Combined-run validator behavior

Add these checks to `dev/tools/validate_workflow_run.py` under the combined workflow mode.

### P0 structural checks

- `flow.parent_root_exists`: supplied parent root exists.
- `flow.child_asset_root_exists`: `asset-investment-diligence/` exists under the parent root.
- `flow.child_oracle_root_exists`: `oracle-analysis/` exists under the parent root.
- `flow.propose_handoff_exists`: `agentic-flow/analyze-and-propose.md` exists.
- `flow.parent_index_maps_children`: parent `index.md` or `README.md` links to asset, oracle, and agentic-flow outputs.
- `flow.child_asset_validation_runs`: the child asset root is validated or its P0/P1 findings are imported into the combined report.
- `flow.child_oracle_validation_runs`: the child oracle root is validated or its P0/P1 findings are imported into the combined report.
- `links.local_paths_resolve`: parent and child run-local links resolve from their actual nesting level.

### P1 stage-gate checks

- `flow.stage_status_table_present`: `agentic-flow/analyze-and-propose.md` names all six stages: Discover, Analyze, Propose, Preview, Execute, Monitor.
- `flow.discover_state_declared`: Discover says whether it was supplied by premise, completed by the agent, or blocked.
- `flow.analyze_artifacts_declared`: the handoff names the asset and oracle final-verification artifacts used for Analyze.
- `flow.propose_status_declared`: Propose is one of `ready_for_preview`, `request_more_inputs`, or `blocked`.
- `flow.unresolved_gates_request_more_inputs`: if child findings or the handoff contain unresolved support, eligibility, feed, route/depth, wallet, Credit Manager envelope, user-policy, or live-input gates, Propose must be `request_more_inputs` or `blocked`.
- `flow.preview_execute_blocked_when_unresolved`: Preview and Execute must be blocked while any of those gates remain unresolved, unless a local explicit human-override artifact is present and linked from the handoff.
- `flow.no_unsupported_execution_recommendation`: the parent handoff must not recommend opening a Credit Account, allocating funds, signing transactions, or moving to Execute from Analyze-only evidence.
- `flow.monitor_not_started_before_execute`: Monitor must be `not started` or `blocked` unless Execute is complete.
- `flow.requested_next_checks_named`: when Propose is `request_more_inputs`, the handoff lists concrete next checks. Vague text such as "needs review" without named checks is a P1 finding.

### P2 hardening checks

- `flow.command_evidence_present`: combined verification output includes the validator command, exit code, and generated report path when `--write-verification` is used.
- `flow.raw_dump_absent`: parent index and handoff cite child artifact paths instead of pasting raw evidence dumps.
- `flow.status_reconciles_children`: parent Propose status is not more permissive than child root status. If either child is `blocked` or `review_required`, the parent cannot be `ready_for_preview` without an explicit override artifact.

## Blocker and gate detection rules

M4 does not need natural-language understanding. Use deterministic markers and conservative keyword checks.

Treat these as unresolved gate families when they appear with `unknown`, `missing`, `unresolved`, `not supplied`, `review_required`, `blocked`, `must check`, `requires`, or equivalent status markers:

- `support` / `Gearbox support` / `PFS` / `Credit Manager envelope`.
- `eligibility` / `KYC` / `wallet` / `issuer` / `transfer` / `redeem`.
- `feed` / `oracle` / `safe pricing` / `LT` / `LLTV`.
- `route` / `route depth` / `liquidity` / `exit` / `quote`.
- `user policy` / `mandate` / `position size` / `target leverage`.
- `live input` / `current state` / `fresh data`.

A conservative false positive is acceptable for this harness because the safe output is `request_more_inputs` or blocked Preview/Execute. Do not allow a false pass that marks Preview or Execute ready while blockers remain.

## Prompt-doc implementation notes

In the asset prompt file, update only the final verification / compressed handoff area. Add a short parent-handoff note requiring:

```text
Return final compressed handoff:
- status: pass | review_required | blocked
- run_artifact_root
- final_verification
- blocked_scopes
- review_required_scopes
- dominant_blockers
- live_input_blockers
- preview_execute_relevance: gates that must be resolved before a parent agent may mark Preview or Execute ready
```

In the oracle prompt file, update only the optional verifier prompt. Add the same fields, with oracle-specific blocker examples: feed support, recursive feed uncertainty, source primitive gaps, side-specific loss-bearer omissions, Gearbox protocol-fit rows, safe-pricing/LT status, and live market/feed state.

Do not change stage order, output folder names, or child workflow meaning.

## Acceptance commands for the M4 implementation task

Run from `/Users/ilya/Documents/Codex/front-knowledge-base` after implementing M4.

### 1. Syntax and scoped tests

```bash
python3 -m py_compile dev/tools/validate_workflow_run.py
python3 -m pytest dev/tools/workflow_harness/tests -k 'combined or agentic or flow'
```

If no test package exists yet, replace the pytest command with the three subprocess assertions below and record that the M4 slice did not add persistent fixture files.

### 2. Good combined run passes

```bash
python3 dev/tools/validate_workflow_run.py \
  --workflow combined-analyze-propose \
  --run-root dev/tools/workflow_harness/fixtures/good/good-agentic-sample-assets \
  --format json,markdown
```

Expected: exit code `0`; report contains no P0/P1 findings; `flow.propose_handoff_exists`, `flow.stage_status_table_present`, and `flow.preview_execute_blocked_when_unresolved` pass.

### 3. Missing handoff fails with P0

```bash
python3 - <<'PY'
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

src = Path('dev/tools/workflow_harness/fixtures/good/good-agentic-sample-assets')
with tempfile.TemporaryDirectory() as td:
    run = Path(td) / 'missing-propose-handoff'
    shutil.copytree(src, run)
    shutil.rmtree(run / 'agentic-flow')
    proc = subprocess.run([
        'python3', 'dev/tools/validate_workflow_run.py',
        '--workflow', 'combined-analyze-propose',
        '--run-root', str(run),
        '--format', 'json',
    ], text=True, capture_output=True)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    report = json.loads(proc.stdout)
    check_ids = {f['check_id'] for f in report['findings']}
    assert 'flow.propose_handoff_exists' in check_ids, check_ids
PY
```

### 4. Unresolved gates require `request_more_inputs` and blocked Preview/Execute

```bash
python3 - <<'PY'
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

src = Path('dev/tools/workflow_harness/fixtures/good/good-agentic-sample-assets')
with tempfile.TemporaryDirectory() as td:
    run = Path(td) / 'ready-for-preview-with-unresolved-gates'
    shutil.copytree(src, run)
    handoff = run / 'agentic-flow' / 'analyze-and-propose.md'
    text = handoff.read_text()
    text = text.replace('Propose: `request_more_inputs`, not `ready_for_preview`.', 'Propose: `ready_for_preview`.')
    text = text.replace('Preview: blocked.', 'Preview: ready.')
    text = text.replace('Execute: blocked.', 'Execute: ready.')
    handoff.write_text(text)
    proc = subprocess.run([
        'python3', 'dev/tools/validate_workflow_run.py',
        '--workflow', 'combined-analyze-propose',
        '--run-root', str(run),
        '--format', 'json',
    ], text=True, capture_output=True)
    assert proc.returncode in (1, 2), proc.stdout + proc.stderr
    report = json.loads(proc.stdout)
    check_ids = {f['check_id'] for f in report['findings']}
    assert 'flow.unresolved_gates_request_more_inputs' in check_ids, check_ids
    assert 'flow.preview_execute_blocked_when_unresolved' in check_ids, check_ids
PY
```

### 5. Prompt docs contain parent blocker handoff fields

```bash
python3 - <<'PY'
from pathlib import Path
required = {
    'status',
    'run_artifact_root',
    'final_verification',
    'blocked_scopes',
    'review_required_scopes',
    'dominant_blockers',
    'live_input_blockers',
    'preview_execute_relevance',
}
files = [
    Path('user/references/workflows/asset-investment-diligence/subagent-prompts.md'),
    Path('user/references/workflows/oracle-analysis/subagent-prompts.md'),
]
for path in files:
    text = path.read_text()
    missing = sorted(term for term in required if term not in text)
    assert not missing, f'{path}: missing {missing}'
PY
```

### 6. Diff hygiene

```bash
git diff --check -- \
  dev/tools/validate_workflow_run.py \
  user/references/workflows/asset-investment-diligence/subagent-prompts.md \
  user/references/workflows/oracle-analysis/subagent-prompts.md

git status --short -- \
  dev/tools/validate_workflow_run.py \
  user/references/workflows/asset-investment-diligence/subagent-prompts.md \
  user/references/workflows/oracle-analysis/subagent-prompts.md
```

Expected changed files are exactly the three files listed above. If the implementation task inherits pre-existing unrelated workspace changes, report them separately and do not modify them.

## Definition of done for M4 implementation

- `combined-analyze-propose` mode validates parent root shape, child roots, and `agentic-flow/analyze-and-propose.md`.
- The handoff must name Discover, Analyze, Propose, Preview, Execute, and Monitor statuses.
- Unresolved support, eligibility, feed, route/depth, wallet, Credit Manager envelope, user-policy, or live-input blockers force Propose to `request_more_inputs` or `blocked`.
- Preview and Execute stay blocked while blockers remain.
- Asset and oracle prompt docs return blocker fields the parent can reconcile.
- Acceptance commands above run with the expected exit codes.
- No new combined workflow package, navigation update, economics grading, oracle-quality grading, live data fetch, or historical artifact rewrite is included in this slice.
