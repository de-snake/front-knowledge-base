# Agent handoff — Analyze → Propose

Paste this single line to the agent instead of pasting workflow details:

```text
Open dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/run/.workflow/agent-handoff.md; USDat: token 0x23238f20b894f29041f48d88ee91131c395aaa71, feed 0x54DF8bAa0F35B767fFd2124c1D4F13788251E312, USDat LTV/LT context: 0.90; sUSDat: token 0xd166337499e176bbc38a1fbd113ab144e5bd2df7, feed 0xe5d7ce380349f0380d8A216A75BCd1070C0ed5b1, sUSDat LTV/LT context: 0.86; Borrow asset: USDC, Borrow rate assumption: 9%; Analyze→Propose only; no Preview/Execute.
```

Agent launcher: `codex`.

## Contract

- Work in repository root `/Users/ilya/Documents/Codex/front-knowledge-base`.
- Write only under `dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/run`.
- Discover is already complete; perform Analyze → Propose only.
- Preview and Execute are blocked. Do not perform state-changing on-chain actions.
- Use generated files for context: `.workflow/input.normalized.json`, child `scope.json` files, packets, and required references.
- Do not invent missing live values. Record unresolved gates and validator findings explicitly.

## Loop

1. Read `.workflow/next-action.md`.
2. Read `.workflow/registry.json`.
3. Execute packets in registry order, filling only each packet's declared `required_outputs`.
4. Keep raw evidence inside the child run roots; do not expand it into parent context.
5. After filling artifacts, run validation:

```bash
python3 dev/tools/run_workflow.py analyze-propose --input dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/input.json --run-root dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/run --mode validate --resume --format markdown
```

Validation exit semantics:

- `0`: pass — summarize final recommendation and exact report paths.
- `1`: review_required — summarize unresolved finding IDs and why they remain review gates.
- `2`: blocked — fix P0 findings, rerun validation, or report the exact blocker if not fixable.

## Required final response

- Run root: `dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/run`.
- Final validator exit code and status.
- Recommendation for the requested assets, with Preview/Execute still blocked unless separately authorized.
- Unresolved gates from `.workflow/input.normalized.json` and `.workflow/validation/summary.md`.
- Exact child report paths and parent `agentic-flow/analyze-and-propose.md` path.
