# Output structure — oracle analysis workflow

Every oracle-analysis run returns one artifact folder. The parent agent should return this folder path plus a short summary, not raw evidence dumps.

## Canonical run folder

```text
<run_artifact_root>/
  README.md
  run-manifest.json
  index.md

  tokens/
    <token-scope-slug>/
      scope.json
      oracle/
        scope.md
        feed-graph.md
        node-classification.md
        source-primitive-audit.md
        stress-tradeoff-analysis.md
        protocol-fit-memo.md
      raw/
        feed-probes.json
        source-evidence/
      verification/
        oracle-analysis-verification.md

  pt-markets/
    <pt-scope-slug>/
      scope.json
      oracle/
        scope.md
        feed-graph.md
        node-classification.md
        source-primitive-audit.md
        stress-tradeoff-analysis.md
        protocol-fit-memo.md
      raw/
        feed-probes.json
        source-evidence/
      verification/
        oracle-analysis-verification.md

  comparisons/
    <comparison-slug>.md

  verification/
    final-oracle-analysis-verification.md
```

## Scope slug rules

Use deterministic lowercase slugs.

Token scope slug:

```text
<chain>-<symbol>-<address-prefix>
```

Example:

```text
ethereum-sample-vault-token-22222222
```

PT market scope slug:

```text
<chain>-pt-<underlying-symbol>-<maturity>-<market-prefix>
```

Example:

```text
ethereum-pt-susde-2025-09-25-abc12345
```

If the same token is analyzed for multiple sides, keep one token folder and include multiple side verdicts in `oracle/protocol-fit-memo.md`. Do not create separate borrower and LP folders unless the feed path or protocol market differs.

## Required top-level files

### `run-manifest.json`

Machine-readable registry used by the parent agent and future sessions.

Required fields:

```json
{
  "workflow_id": "oracle-analysis-v1",
  "run_id": "oracle-analysis-YYYY-MM-DD",
  "run_artifact_root": "dev/implementation/<run-slug>",
  "scopes": [
    {
      "scope_id": "eth-mainnet-sample-vault-token-gearbox",
      "scope_slug": "ethereum-sample-vault-token-22222222",
      "scope_type": "token",
      "chain": "Ethereum mainnet",
      "asset_symbol": "SampleVaultToken",
      "asset_address": "0x2222222222222222222222222222222222222222",
      "protocol": "Gearbox",
      "position_sides": ["credit_account_borrower", "pool_lp"],
      "token_roles": ["collateral"],
      "artifact_dir": "tokens/ethereum-sample-vault-token-22222222",
      "status": "pass | review_required | blocked"
    }
  ],
  "final_index": "index.md",
  "final_verification": "verification/final-oracle-analysis-verification.md"
}
```

### `index.md`

Human-readable run summary.

Required sections:

- Scope table by token / PT market.
- Feed formulas.
- Side-specific verdict matrix:
  - borrower / Credit Account operator;
  - pool LP / lender;
  - liquidator;
  - curator/operator.
- Open blockers.
- Artifact map.
- Validation result.

### `README.md`

Short handoff page for the run folder:

- what was analyzed;
- where the manifest is;
- where each token or PT folder is;
- which files to read first;
- final validation status.

## Required per-scope files

Each token or PT market folder must contain the same canonical files. This keeps multi-token runs easy to inspect and lets future agents jump directly to the relevant token.

Required per-scope files:

- `scope.json` — exact input scope for this token or PT market.
- `oracle/scope.md` — readable scope and acceptance policy.
- `oracle/feed-graph.md` — recursive feed graph and formula.
- `oracle/node-classification.md` — market / fundamental / NAV / hardcoded / hybrid classification for every node.
- `oracle/source-primitive-audit.md` — leaf-source audits.
- `oracle/stress-tradeoff-analysis.md` — side-aware stress behavior.
- `oracle/protocol-fit-memo.md` — side-specific verdicts.
- `raw/feed-probes.json` — raw feed probe registry.
- `raw/source-evidence/` — bulky source snapshots.
- `verification/oracle-analysis-verification.md` — per-scope validation.

## Parent-agent return contract

A completed workflow run returns:

```json
{
  "status": "pass | review_required | blocked",
  "run_artifact_root": "dev/implementation/<run-slug>",
  "manifest": "dev/implementation/<run-slug>/run-manifest.json",
  "index": "dev/implementation/<run-slug>/index.md",
  "scope_dirs": [
    "dev/implementation/<run-slug>/tokens/ethereum-sample-vault-token-22222222"
  ],
  "final_verification": "dev/implementation/<run-slug>/verification/final-oracle-analysis-verification.md",
  "summary": {
    "scopes_analyzed": 1,
    "blocked_scopes": 0,
    "review_required_scopes": 1,
    "dominant_blockers": ["size-specific exit liquidity unknown"]
  }
}
```

The user-facing answer should include the folder path and final verdict summary. It should not paste raw RPC output unless requested.

## Workflow harness outputs

The workflow harness writes deterministic compliance artifacts under the run verification directory:

- `workflow-harness-report.json` — machine-readable report with status, exit code, checks, and findings.
- `workflow-harness-verification.md` — Markdown verification summary for human review.

Parent-agent return handoffs must include these paths when the harness is run, especially when `review_required` leaves unresolved finding ids.
