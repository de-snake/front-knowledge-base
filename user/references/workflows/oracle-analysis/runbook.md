# Runbook — oracle analysis workflow

This runbook tells an agent how to execute `workflow.json` without loading all raw evidence into the parent context.

## 0. Start here

Workflow directory:

`user/references/workflows/oracle-analysis`

Run artifact root:

`[run_artifact_root]`

Read in this order:

1. `README.md`.
2. `workflow.json`.
3. `stage-contracts.md`.
4. `parallelization-and-context.md`.
5. `subagent-prompts.md`.
6. `output-structure.md`.
7. `gearbox-price-feed-parsing.md` when protocol is Gearbox.

Do not start by reading every raw RPC or explorer artifact. Raw snapshots belong under `<scope_artifact_dir>/raw/`.

Every run returns one folder at `run_artifact_root`. Every analyzed token or PT market gets its own subfolder as defined in `output-structure.md`.

## 1. Define the run scope

Create a scope object before spawning workers:

```json
{
  "run_id": "oracle-analysis-YYYY-MM-DD",
  "run_artifact_root": "dev/implementation/<run-slug>",
  "scope_id": "eth-mainnet-sample-vault-token-gearbox",
  "chain_id": 1,
  "chain": "Ethereum mainnet",
  "protocol": "Gearbox",
  "asset": {
    "symbol": "SampleVaultToken",
    "address": "0x2222222222222222222222222222222222222222"
  },
  "market_context": {
    "credit_manager": null,
    "lt": 0.86,
    "position_size_usd": null,
    "target_leverage": null
  },
  "position_side": "credit_account_borrower",
  "token_role": "collateral",
  "known_feeds": [
    {"role": "main", "address": "0x4444444444444444444444444444444444444444"}
  ],
  "accepted_oracle_methodologies": null,
  "question": "Is this oracle setup acceptable for Credit Account opening analysis?"
}
```

If a field is unknown, keep it and set it to `null`.

Do not proceed to a final verdict without `position_side` and `token_role`. If the run is only a neutral feed inventory, set both to `null` and stop before protocol-fit conclusions.

Before S1, assign each scope a deterministic `scope_slug` and `scope_artifact_dir`:

- token: `tokens/<chain>-<symbol>-<address-prefix>`;
- PT market: `pt-markets/<chain>-pt-<underlying-symbol>-<maturity>-<market-prefix>`.

Create or update `run-manifest.json` and `index.md` at the run root before spawning subagents.

## 2. Execute stages

### 2.1 Scope

Write `oracle/scope.md` with the scope object and the acceptance policy.

Actual path:

```text
<scope_artifact_dir>/oracle/scope.md
```

Also write:

```text
<scope_artifact_dir>/scope.json
```

Record whether the analysis is for a pool LP, Credit Account borrower, liquidator, or curator/operator. This controls the final conclusion: hardcoded, NAV, market, bounded, and composite feeds do not have the same implications for each side.

### 2.2 Feed graph

Run S1 for each independent asset/feed tree.

If the protocol is Gearbox, read `gearbox-price-feed-parsing.md` before probing. The official Gearbox curator guide defines feed-specific setup patterns for:

- External AggregatorV3-compatible feeds;
- ERC4626 exchange-rate feeds;
- Pyth pull feeds;
- Redstone pull feeds;
- bounded / upper-bound feeds;
- composite feeds;
- constant feeds;
- Curve LP and Curve TWAP feeds;
- Pendle PT and Pendle LP feeds;
- Kodiak Island feeds;
- Balancer V3 LP feeds.

Do not classify a Gearbox feed only by the PFS wrapper label. `External`, `Composite`, `Bounded`, or `ERC4626` tells you the Gearbox wrapper shape, not the complete economic oracle type.

For Gearbox PFS feeds, probe the common getter set from `stage-contracts.md`. Example command shape:

```bash
RPC=https://ethereum-rpc.publicnode.com
FEED=0x...
cast call $FEED 'contractType()(bytes32)' --rpc-url $RPC
cast call $FEED 'description()(string)' --rpc-url $RPC
cast call $FEED 'latestRoundData()(uint80,int256,uint256,uint256,uint80)' --rpc-url $RPC
cast call $FEED 'priceFeed()(address)' --rpc-url $RPC
```

Continue recursively for every child feed.

Parent action after S1:

- Record top-level answer, timestamp, node count, and leaf primitives.
- Do not classify the setup yet unless the full graph is complete.

### 2.3 Node classification

Run S2 serially in the parent.

Classify each node:

- market;
- fundamental;
- NAV;
- hardcoded;
- hybrid/composite.

Write `oracle/node-classification.md`.

Actual path:

```text
<scope_artifact_dir>/oracle/node-classification.md
```

Parent action after S2:

- Verify every node has one type.
- Verify the formula explains how the protocol price is produced.

### 2.4 Source primitive audits

Run S3 in parallel by primitive after S2 is complete.

Examples:

- Chainlink SampleDebtToken/USD worker.
- Curve SampleBaseToken/SampleDebtToken TWAP worker.
- Pendle PT→SY factory oracle worker.
- ERC4626 vault accounting worker.
- Issuer NAV/fundamental reporting worker.

Parent action after S3:

- Read only the primitive summaries first.
- Expand raw evidence only for blockers, stale timestamps, surprising values, or unverified assumptions.

### 2.5 Stress tradeoff analysis

Run S4 serially.

Use the Steakhouse framing:

- Market feeds are responsive but can create liquidation-cascade risk when liquidity is thin.
- NAV, fundamental, and hardcoded feeds filter short-term noise but can create liquidity-trap or shadow-bad-debt risk when executable value diverges.
- Hybrid feeds must be analyzed by switching/bounding logic and by weakest node.

Write `oracle/stress-tradeoff-analysis.md`.

Actual path:

```text
<scope_artifact_dir>/oracle/stress-tradeoff-analysis.md
```

Required side split:

- borrower / Credit Account operator;
- pool LP / lender;
- liquidator;
- curator/operator.

Example conclusion pattern:

```text
For a Credit Account borrower using the token as collateral, a hardcoded price is protective during temporary market dislocation because it avoids immediate liquidation.

For a pool LP, the same hardcoded price is risky during persistent depeg because liquidation may not recognize the lower executable collateral value, creating bad debt or locked liquidity.
```

### 2.6 Protocol fit

Run S5 serially.

For Gearbox, include:

- LT and max leverage implication;
- main and reserve feeds;
- safe-pricing exit HF;
- staleness and bounds;
- delayed-withdrawal or issuer-controlled branch interaction;
- comparison to a simpler Morpho market setup when requested.

For Morpho, include:

- LLTV;
- oracle formula;
- liquidation feasibility;
- whether MetaOracle/deviation timelock or equivalent switching exists;
- liquidity and redemption assumptions.

Write `oracle/protocol-fit-memo.md`.

Actual path:

```text
<scope_artifact_dir>/oracle/protocol-fit-memo.md
```

The memo must contain separate side verdicts. Do not merge borrower and LP outcomes into one score.

### 2.7 Verification

Run S6 after all artifacts exist.

Required output:

Per-scope output:

```text
<scope_artifact_dir>/verification/oracle-analysis-verification.md
```

Run-level output:

```text
verification/final-oracle-analysis-verification.md
```

Minimum checks:

- required files exist;
- every token / PT market has its own subfolder;
- every graph leaf has a primitive audit;
- no unclassified nodes;
- formula present;
- staleness/bounds/timestamps present or explicitly unavailable;
- protocol-fit memo ties oracle risk to LT/LLTV and liquidation/safe-pricing;
- no conclusion stops at top-level feed type.
- side-specific conclusions exist for each relevant side;
- Gearbox-specific parsing reference was applied when protocol is Gearbox.

## 3. Final answer shape

When reporting to the user, include:

- feed formula;
- node types;
- dominant weak link;
- cascade-vs-trap behavior;
- protocol-fit verdict;
- side-specific borrower / LP / liquidator / curator verdicts;
- human-review blockers;
- artifact paths;
- run folder path;
- final index path;
- validation result.

Do not paste raw RPC dumps into the final answer unless the user asks.

## 4. Workflow harness command

Run this harness command from the vault root after S6 writes the final verification:

```bash
python3 dev/tools/validate_workflow_run.py \
  --workflow oracle-analysis \
  --run-root <run_artifact_root> \
  --format json,markdown \
  --report-dir <run_artifact_root>/verification \
  --write-verification
```

Completion rule: fix all P0 findings before returning the run as complete. If the report status is `review_required`, include the harness command, exit code, report path, and unresolved finding ids in the final parent-agent handoff instead of hiding them.
