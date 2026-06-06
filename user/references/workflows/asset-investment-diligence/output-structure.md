# Output structure — asset investment diligence workflow

Every asset-investment-diligence run returns one artifact folder. The parent agent should return this folder path plus a short summary, not a set of loose report paths.

## Canonical run folder

```text
<run_artifact_root>/
  README.md
  run-manifest.json
  index.md

  tokens/
    <token-slug>/
      scope.json
      research/
        onchain-admin.md
        issuer-backing-security.md
        transfer-liquidity-oracle-governance.md
      technical-report.md
      analyst-report.md
      verification.md

  pt-markets/
    <pt-scope-slug>/
      scope.json
      technical-report.md
      analyst-report.md
      verification.md
    index.md

  x-research/
    <scope-slug>.md
    index.md

  investment-analysis/
    quantitative-underwriting-methodology.md
    investment-analyst-report-points-pt-risk-return.md
    index.md

  verification/
    final-investment-analysis-verification.md
```

## Slug rules

Token slug:

```text
<chain>-<symbol>-<address-prefix>
```

Example:

```text
ethereum-sample-vault-token-22222222
```

PT market slug:

```text
<chain>-pt-<underlying-symbol>-<maturity>-<market-prefix>
```

Example:

```text
ethereum-pt-sample-vault-token-2026-08-27-abc12345
```

Social scope slug:

```text
<token-slug>
<pt-scope-slug>
portfolio
```

## Required top-level files

### `run-manifest.json`

Required fields:

```json
{
  "workflow_id": "asset-investment-diligence-v1",
  "run_id": "asset-diligence-YYYY-MM-DD",
  "run_artifact_root": "dev/implementation/<run-slug>",
  "tokens": [
    {
      "token_slug": "ethereum-sample-vault-token-22222222",
      "chain": "Ethereum mainnet",
      "symbol": "SampleVaultToken",
      "address": "0x2222222222222222222222222222222222222222",
      "artifact_dir": "tokens/ethereum-sample-vault-token-22222222",
      "status": "pass | review_required | blocked"
    }
  ],
  "pt_markets": [],
  "x_research_scopes": [],
  "final_index": "index.md",
  "final_verification": "verification/final-investment-analysis-verification.md"
}
```

### `index.md`

Human-readable run summary:

- tokens analyzed;
- PT markets analyzed;
- headline risk / return findings;
- missing data and blockers;
- artifact map;
- final verification status.

### `README.md`

Short handoff page:

- what was analyzed;
- where the manifest is;
- where each token / PT folder is;
- which files to read first;
- final validation status.

## Required per-token files

Each token folder must contain:

- `scope.json`;
- `research/onchain-admin.md`;
- `research/issuer-backing-security.md`;
- `research/transfer-liquidity-oracle-governance.md`;
- `technical-report.md`;
- `analyst-report.md`;
- `verification.md`.

## Required per-PT files

Each PT folder must contain:

- `scope.json`;
- `technical-report.md`;
- `analyst-report.md`;
- `verification.md`.

The run-level `pt-markets/index.md` summarizes all PT scopes.

## Parent-agent return contract

A completed workflow run returns:

```json
{
  "status": "pass | review_required | blocked",
  "run_artifact_root": "dev/implementation/<run-slug>",
  "manifest": "dev/implementation/<run-slug>/run-manifest.json",
  "index": "dev/implementation/<run-slug>/index.md",
  "token_dirs": [
    "dev/implementation/<run-slug>/tokens/ethereum-sample-vault-token-22222222"
  ],
  "pt_market_dirs": [],
  "final_verification": "dev/implementation/<run-slug>/verification/final-investment-analysis-verification.md",
  "summary": {
    "tokens_analyzed": 1,
    "pt_markets_analyzed": 0,
    "blocked_scopes": 0,
    "review_required_scopes": 1,
    "dominant_blockers": ["issuer redemption queue depth unknown"]
  }
}
```

The user-facing answer should include the run folder path, final index path, token folders, and final verification path. It should not paste raw source notes unless requested.

## Workflow harness outputs

The workflow harness writes deterministic compliance artifacts under the run verification directory:

- `workflow-harness-report.json` — machine-readable report with status, exit code, checks, and findings.
- `workflow-harness-verification.md` — Markdown verification summary for human review.

Parent-agent return handoffs must include these paths when the harness is run, especially when `review_required` leaves unresolved finding ids.
