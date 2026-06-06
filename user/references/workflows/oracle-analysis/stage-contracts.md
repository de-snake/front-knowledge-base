# Stage contracts — oracle analysis workflow

This file defines the handoff interface for each oracle-analysis stage. A future agent should treat these contracts as mandatory.

## Shared envelope

Every stage artifact should support this parent-agent summary envelope:

```json
{
  "stage_id": "S1_feed_inventory_and_graph",
  "scope_id": "eth-mainnet-sample-vault-token-gearbox",
  "status": "pass | review_required | blocked",
  "artifact_paths": ["tokens/ethereum-sample-vault-token-22222222/oracle/feed-graph.md"],
  "position_side": "pool_lp | credit_account_borrower | liquidator | curator_operator",
  "token_role": "collateral | borrowed_token | quoted_token | vault_share | lp_token | pt | transition_stage_asset",
  "key_numbers": [
    {"name": "latest_answer", "value": "0.94182990 USD", "source": "RPC latestRoundData"}
  ],
  "node_summaries": [
    {"node": "0x...", "type": "market | fundamental | nav | hardcoded | hybrid", "role": "Curve SampleBaseToken/SampleDebtToken TWAP"}
  ],
  "top_risks": [
    {"risk": "NAV-exit divergence", "evidence": "ERC4626 layer over queue-based asset", "decision_effect": "review_required"}
  ],
  "blocking_unknowns": ["..."],
  "validation": {"result": "pass | fail", "checks": ["..."]}
}
```

The parent should read this envelope before loading full artifacts.

## Output folder rule

Every run must follow `output-structure.md`.

The workflow returns one `<run_artifact_root>/` folder with:

- `run-manifest.json` and `index.md` at the run root;
- `tokens/<token-scope-slug>/` for each analyzed token;
- `pt-markets/<pt-scope-slug>/` for each analyzed PT market;
- per-scope `oracle/`, `raw/`, and `verification/` subfolders;
- `verification/final-oracle-analysis-verification.md` at the run root.

Do not write all token outputs into a single flat `oracle/` folder. Single-token runs still use the same per-token folder structure.

## Side-aware conclusion rule

Oracle conclusions are not universal. The same feed can improve outcomes for one side while worsening them for another.

Every final conclusion must state:

- position side: pool LP, Credit Account borrower, liquidator, or curator/operator;
- token role: collateral, borrowed token, pool quoted token, vault share, LP token, PT, or transition-stage asset;
- stress direction: price down, price up, depeg, stale update, manipulation, liquidity loss, or redemption impairment;
- loss bearer: borrower liquidation, LP bad debt, LP locked liquidity, liquidator execution risk, or curator intervention requirement.

Do not write a single verdict such as `safe`, `unsafe`, `good`, or `bad` without this side split.

## S0 — Scope and acceptance policy

Role: define what oracle setup is being analyzed and what the user or mandate considers acceptable.

Input contract:

- `scope_id`.
- `chain_id` and chain name.
- Asset/token/market identifiers.
- Protocol context: Gearbox pool / Credit Manager / strategy, Morpho market ID, or other lending market.
- Position side: pool LP, Credit Account borrower, liquidator, curator/operator, or `null` if the run is only a neutral feed inventory.
- Token role: collateral, borrowed token, quoted token, vault share, LP token, PT, transition-stage asset, or `null` if not yet known.
- Top-level feed address if known.
- Position size, leverage, LT/LLTV, and hold horizon if the analysis is attached to a position.
- Accepted oracle methodologies if user or mandate provides them. Unknown values remain `null`.

Output contract:

- `run-manifest.json`.
- `index.md`.
- `<scope_artifact_dir>/scope.json`.
- `<scope_artifact_dir>/oracle/scope.md`.

Validation:

- Chain, asset, and protocol are named.
- Position side and token role are named or explicitly set to `null`.
- Scope slug and `scope_artifact_dir` are assigned according to `output-structure.md`.
- Unknown fields are explicit, not omitted.
- If no feed address is known, the discovery method is named.

## S1 — Feed inventory and dependency graph

Role: recursively discover the oracle dependency graph.

Output contract:

- `<scope_artifact_dir>/oracle/feed-graph.md`.
- `<scope_artifact_dir>/raw/feed-probes.json`.

Required facts per node:

- Address or source identifier.
- Protocol/component owner.
- `contractType`, `description`, `version`, `decimals`, and `stalenessPeriod` where exposed.
- `latestRoundData` or equivalent current value where exposed.
- Bounds, deviation thresholds, challenge windows, and `skipCheck` / safe-pricing flags where exposed.
- Child feeds or primitive sources.
- Human formula role.

Common Gearbox PFS probes:

```text
contractType()(bytes32)
version()(uint256)
decimals()(uint8)
description()(string)
stalenessPeriod()(uint32)
latestRoundData()(uint80,int256,uint256,uint256,uint80)
priceFeed()(address)
underlyingPriceFeed()(address)
basePriceFeed()(address)
targetPriceFeed()(address)
token()(address)
pool()(address)
market()(address)
sy()(address)
pt()(address)
lowerBound()(int256)
upperBound()(int256)
skipCheck()(bool)
```

Gearbox-specific parsing rule:

- Apply `gearbox-price-feed-parsing.md` when the protocol scope is Gearbox.
- Do not classify by PFS wrapper label alone. For example, `External` can mean Chainlink market, Redstone push, EO, Midas NAV, or another AggregatorV3-compatible source; classify by underlying methodology.
- For Gearbox bounded feeds, record whether the bounded token is a borrowed token or collateral token. The official curator guide frames upper bounds differently by side: bounding borrowed tokens can protect borrowers from liquidations, while bounding collateral tokens can protect LPs from price manipulation.
- For Gearbox ERC4626, Composite, Curve LP, Curve TWAP, Pendle PT TWAP, Kodiak Island, Pendle LP, and Balancer LP feeds, recurse through every child feed listed by the configuration guide before writing a verdict.

Validation:

- The graph reaches primitives rather than stopping at top-level label.
- Each non-leaf node has children or an explicit no-child explanation.
- The formula is reconstructed in human terms.

## S2 — Node classification and math reconstruction

Role: classify every node and reconstruct the actual price equation.

Output contract:

- `<scope_artifact_dir>/oracle/node-classification.md`.

Classification rules:

- `market`: observed trade price or derivative: Chainlink market pair, Pyth, Curve TWAP, Uniswap TWAP, Pendle TWAP, auction, VWAP.
- `fundamental`: primary-market ratio, issuer/admin exchange rate, proof-of-reserves collateralization ratio, underlying reference used because redemption is expected to hold.
- `nav`: accounting value or reported holdings value, including ERC4626 `convertToAssets`, staking derivative exchange rate, fund NAV, tokenized-fund NAV attestation.
- `hardcoded`: fixed scalar or peg assumption that does not observe current market or NAV.
- `hybrid`: composite, bounded, main/reserve, MetaOracle, or switching logic that combines multiple nodes.

Required sections:

- Formula.
- Node table with type, role, input, output, decimals, and risk role.
- Bound/switch/safe-pricing logic.
- Unclassified or ambiguous nodes.

Validation:

- Every graph node has a type.
- Every formula operation is explained.
- Decimals and scale factors are checked.
- Classification uncertainty is marked `review_required`, not hidden.

## S3 — Source primitive audit

Role: audit every leaf source and trust assumption.

Output contract:

- `<scope_artifact_dir>/oracle/source-primitive-audit.md`.
- `<scope_artifact_dir>/raw/source-evidence/` when raw snapshots are saved.

Required audits by primitive type:

- **Chainlink/Pyth market feed**: answer, decimals, updated time, staleness, data-source quality, and whether the pair is the right economic reference.
- **Curve/DEX TWAP**: pool address, tokens, balances or liquidity, amplification/fee where relevant, TWAP window or observation logic, recent imbalance, and size-specific route relevance.
- **Pendle factory oracle**: market, PT/SY/YT, maturity, TWAP duration, base oracle type, cardinality readiness, oldest-observation satisfaction, and maturity behavior.
- **ERC4626/NAV**: vault asset, `convertToAssets`/exchange rate, total assets, withdrawal path, queue/claim timing, and whether accounting value is executable at size.
- **Fundamental/issuer source**: issuer, reporting cadence, proof scope, auditor/admin signer, legal redemption promise, delays, and eligibility constraints.
- **Hardcoded scalar**: invariant being assumed, why it is assumed, what breaks the invariant, and who bears loss if it breaks.

Validation:

- Every leaf primitive is covered.
- Every timestamp or reporting cadence is recorded.
- Every issuer/reporting trust assumption is explicit.
- DEX/TWAP primitives include liquidity/manipulation surface, not just address.

## S4 — Stress and tradeoff analysis

Role: determine how the oracle behaves when the world diverges from the model.

Output contract:

- `<scope_artifact_dir>/oracle/stress-tradeoff-analysis.md`.

Required scenarios:

- Short-term volatility or temporary market dislocation.
- Long-term depeg, insolvency, issuer failure, or persistent redemption impairment.
- Thin-liquidity manipulation or TWAP lag.
- Stale report, stale external feed, or delayed oracle update.
- Liquidation path: recognition, profitability, execution before further price decline.
- Safe-pricing or reserve-oracle fallback behavior where applicable.

Required analysis:

- Which node sees the stress first.
- Which node hides the stress longest.
- Whether borrowers or lenders/pool users bear the first loss.
- Liquidity-cascade risk: market oracle triggers liquidations into thin liquidity.
- Liquidity-trap risk: NAV/fundamental/hardcoded oracle keeps value high while executable exit value falls.
- Shadow-bad-debt risk: position looks solvent by oracle but cannot be liquidated profitably.

Required side split:

- **Borrower / Credit Account operator:** Does this oracle increase liquidation probability, suppress collateral value, allow more borrowing, or hide debt/collateral stress?
- **Pool LP / lender:** Does this oracle help liquidations recognize stress early, or does it create bad debt / locked-liquidity risk by keeping value above executable exit value?
- **Liquidator:** Does this oracle create profitable and executable liquidation windows, or does it leave liquidators with stale, non-transferable, queue-bound, or illiquid collateral?
- **curator/operator:** Does this oracle require active update, bound refresh, PFS change, pull-feed data update, or human intervention under stress?

Validation:

- Both cascade and trap possibilities are addressed.
- Persistent depeg is separated from temporary dislocation.
- Stress conclusion is tied to nodes, not generic token fear.
- Borrower and LP outcomes are separately stated even when they point in opposite directions.

## S5 — Protocol fit and parameter context

Role: decide whether the oracle setup fits the actual market parameters.

Output contract:

- `<scope_artifact_dir>/oracle/protocol-fit-memo.md`.

Required side verdicts:

- Borrower / Credit Account operator verdict.
- Pool LP / lender verdict.
- Liquidator verdict, when liquidation is part of the market design.
- curator/operator verdict, when a feed can require PFS, bound, pull-feed, or reserve-feed intervention.

Each verdict must include the token role and stress direction. Example: `Hardcoded collateral price is borrower-protective during a temporary market dip but LP-risky during persistent depeg because liquidation will not recognize executable exit value.`

Gearbox-required fields:

- Main and reserve feed paths.
- Safe-pricing rule and exit HF implication.
- LT and LT ramp.
- Max leverage implied by LT.
- Staleness and bounds.
- Whether a feed can be swapped or reserved without timelock.
- Whether delayed withdrawals, forbidden tokens, or issuer-controlled branches interact with the oracle.

Morpho-required fields:

- Collateral asset, loan asset, LLTV.
- Oracle formula and source contract.
- Whether the oracle is market, NAV, fundamental, hardcoded, or hybrid.
- Liquidation feasibility and secondary-market depth.
- Whether MetaOracle/deviation timelock or equivalent primary/backup logic exists.

Required comparison when requested:

- Explain whether the setup is simpler or more complex than a reference market.
- Compare number of oracle nodes, source primitives, switching/bounding logic, and stress modes.
- Do not equate lower node count with lower risk automatically; explain the dominant risk.

Validation:

- Protocol parameters are tied to oracle risk.
- The memo does not rely on a universal HF/LLTV default.
- Human-review gates are explicit.
- The memo does not collapse borrower and LP outcomes into one score.

## S6 — Final verification

Role: verify the artifact set.

Output contract:

- `<scope_artifact_dir>/verification/oracle-analysis-verification.md`.
- `verification/final-oracle-analysis-verification.md` at the run root.
- Updated `index.md` at the run root.

Checks:

- Required files exist.
- Per-token / per-PT subfolders follow `output-structure.md`.
- Every graph leaf has a source-primitive audit.
- Every node is classified.
- Pricing formula is present.
- Bounds, staleness, and timestamps are present or explicitly unavailable.
- Protocol-fit memo names LT/LLTV and safe-pricing/liquidation implications.
- No conclusion stops at top-level `contractType` or UI label.
- Position-side conclusions are present.
- Gearbox-specific feed parsing reference was applied when protocol scope is Gearbox.
- Terminology check passes.
