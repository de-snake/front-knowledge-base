# Parallelization and context rules — oracle analysis workflow

Oracle analysis is graph-shaped. Parallelism is useful for independent feed trees and leaf-source audits, but dangerous when it fragments the formula or final stress conclusion.

## Parent-agent responsibilities

The parent owns:

- the run scope;
- the run folder, manifest, index, and per-scope artifact directories;
- the position side and token role;
- the protocol context;
- the complete dependency graph;
- the final stress tradeoff analysis;
- the protocol-fit verdict;
- final verification.

The parent should not ingest raw RPC dumps, explorer pages, Chainlink history, DEX snapshots, or full verified source unless a stage summary exposes a blocker or disputed fact.

## Parallelizable work

### S1 feed tree discovery

Parallelize only when there are multiple independent assets or markets.

Good units:

- one Gearbox allowed token feed tree;
- one Morpho market oracle;
- one Pendle PT feed tree;
- one reserve feed tree.

Bad units:

- one subagent per child node inside the same formula before the graph is known;
- separate agents classifying the same graph without a shared formula.

### S3 source primitive audits

Parallelize after S2 classification has produced the complete leaf list.

Good units:

- Chainlink/Pyth feed audit;
- Curve/DEX TWAP audit;
- Pendle factory oracle audit;
- ERC4626/NAV audit;
- issuer/fundamental source audit;
- hardcoded-invariant audit.

Each worker returns only:

- artifact path;
- primitive identifier;
- current value/timestamp;
- quality/freshness verdict;
- manipulation or trust assumptions;
- blockers.

## Serial work

Keep these serial in the parent unless the scope is very large:

- S0 scope and policy.
- S2 node classification and formula reconstruction.
- S4 stress tradeoff analysis.
- S5 protocol-fit memo.
- S6 verification.

These stages require seeing how all nodes interact. Delegating them independently often causes double-counted risk or missed weak links.

## Context-bloat guardrails

- Use `<scope_artifact_dir>/raw/` for raw RPC/explorer/API snapshots.
- Use short stage summaries for parent handoffs.
- Prefer line-item source maps over pasted raw data.
- Store feed probes as JSON; summarize in Markdown.
- Keep the final memo readable: formula, source primitives, stress behavior, protocol impact, blockers.
- Keep side-specific conclusions in the parent context. Subagents may report side effects, but the parent is responsible for final borrower / LP / liquidator / curator verdicts.
- Keep token and PT outputs isolated in the `output-structure.md` folders. Do not merge multiple analyzed tokens into one `oracle/` folder.

## Handoff summary template

```json
{
  "stage_id": "S3_source_primitive_audit",
  "scope_id": "eth-mainnet-sample-vault-token-gearbox",
  "status": "review_required",
  "run_artifact_root": "dev/implementation/oracle-analysis-YYYY-MM-DD",
  "scope_artifact_dir": "tokens/ethereum-sample-vault-token-22222222",
  "position_side": "credit_account_borrower",
  "token_role": "collateral",
  "artifact_paths": ["tokens/ethereum-sample-vault-token-22222222/oracle/source-primitive-audit.md"],
  "covered_primitives": ["Curve SampleBaseToken/SampleDebtToken", "Chainlink SampleDebtToken/USD", "ERC4626 SampleVaultToken"],
  "key_numbers": [
    {"name": "sample-base-token_curve_twap", "value": "0.99963034 USD", "source": "RPC latestRoundData"}
  ],
  "top_risks": [
    "ERC4626 accounting value can diverge from queue-based exit value",
    "Curve TWAP depends on executable SampleBaseToken/SampleDebtToken liquidity"
  ],
  "blocking_unknowns": ["current queue depth", "size-specific exit route"],
  "validation": {"result": "pass", "checks": ["all leaf primitives covered"]}
}
```
