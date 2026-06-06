# Result — USDat / sUSDat collateral Analyze → Propose

Generated: 2026-06-06 UTC

Audience: human reviewer. This is the report to share. The `run/` folder is the reproduction bundle behind it, not the primary review document.

## Question

Should USDat or sUSDat be treated as acceptable Gearbox Credit Account collateral candidates on Ethereum mainnet when borrowing USDC at a 9% borrow-rate assumption?

## Short answer

USDat is the stronger Analyze-stage candidate. Its supplied Gearbox feed is market-derived from the USDat/USDC Curve pool and observed public liquidity is materially deeper.

sUSDat remains more conditional. Its Gearbox feed uses ERC-4626 accounting over USDat, while immediate recovery can depend on thinner secondary liquidity, queue processing, and issuer / STRC realization.

Neither candidate is ready for Preview or Execute from this run. The correct next state is `request_more_inputs`, not approval.

## What the run established

The run completed the Analyze stage for two Ethereum-mainnet collateral candidates and combined asset diligence with Gearbox oracle/feed analysis.

Formal validation passes for the asset workflow, the oracle workflow, and the combined parent workflow. That means the reproduced artifacts are structurally complete and internally linkable; it does not mean either token is decision-grade collateral for a live position.

The important product result is the gate behavior: the workflow can produce a candidate comparison, but it stops before Preview because live market, position, wallet, and user-policy inputs are missing.

## USDat review

USDat is Saturn's non-yielding dollar token.

The supplied token scope is Ethereum mainnet address `0x23238f20b894f29041f48d88ee91131c395aaa71`. The run treated USDC as the borrow asset and used a 9% borrow-rate assumption.

The strongest point for USDat is the oracle path. The supplied Gearbox feed does not appear to be a hardcoded 1.00 peg. It reads a Curve USDat/USDC market primitive and a bounded USDC/USD child quote. The effective feed answer recorded by the run was `0.99965317` USD at `2026-06-06 08:00:47 UTC`.

The observed public exit venue was the Curve USDat/USDC pool, with about `$15.7M` displayed liquidity and direct balances of roughly `7.82M USDC` and `7.88M USDat` at the run snapshot.

The main blockers are not just price. USDat is issuer-controlled collateral: Saturn documentation describes onboarding requirements, and the token exposes freeze / pause surfaces. A Gearbox Credit Account, liquidator, or recipient route must be proven eligible before any automation or execution decision.

USDat remains `review_required` until the exact Credit Manager / market, allowed-token status, position size, wallet eligibility, route capacity, and user risk policy are supplied.

## sUSDat review

sUSDat is Saturn's ERC-4626 yield-bearing vault token over USDat.

The supplied token scope is Ethereum mainnet address `0xd166337499e176bbc38a1fbd113ab144e5bd2df7`. The run treated USDC as the borrow asset and used a 9% borrow-rate assumption.

The supplied Gearbox feed values sUSDat through ERC-4626 exchange-rate accounting multiplied by the USDat feed. That is a meaningful recursive feed graph, but it creates a different liquidation question: can the accounting value be realized fast enough at the actual position size?

The effective sUSDat feed answer recorded by the run was `0.95272729` USD at `2026-06-06 08:00:47 UTC`. The ERC-4626 exchange-rate probe returned about `0.953119 USDat` per `1 sUSDat`.

The observed sUSDat/USDC Curve venue was much smaller than the USDat venue, with about `$1.8M` displayed liquidity and roughly `296,560 USDC` against `1.62M sUSDat` at the run snapshot.

The main blockers are queue and realization risk. sUSDat adds digital-credit / STRC exposure, queue-based redemption, blacklist / pause surfaces, and a possible gap between accounting value and immediate market exit value.

sUSDat remains `review_required` and should require a higher bar than USDat before any proposal can be considered.

## Oracle and liquidation implication

For USDat, the oracle path is more LP-protective than a fixed peg because it can reflect Curve market pressure. The remaining risk is whether the market is liquid enough and whether issuer controls allow the collateral to move or redeem when needed.

For sUSDat, the feed is structurally complete but more dangerous to treat as simple collateral. The feed follows ERC-4626 accounting, while liquidation may need to happen through a thinner secondary market or delayed redemption path. That accounting-versus-exit gap is the central Gearbox risk.

## Proposal gate

The run's proposal is not “approve USDat” or “approve sUSDat.”

The proposal is:

- keep USDat as the cleaner Analyze-stage candidate;
- keep sUSDat as a higher-risk, review-required candidate;
- block Preview and Execute;
- request missing live inputs before any decision-grade proposal.

## Missing before decision-grade proposal

The run intentionally stops until these inputs are supplied:

- evaluated Gearbox market / Credit Manager / pool for USDat;
- evaluated Gearbox market / Credit Manager / pool for sUSDat;
- position size or scenario size range;
- target leverage or scenario leverage;
- intended hold horizon;
- user risk policy: HF floor, max drawdown, automation policy;
- wallet / Credit Account / liquidator eligibility for holding, transfer, redemption, freeze, and blacklist state;
- size-specific route or liquidation quote for the proposed unwind path.

## Readable supporting reports

For detailed review, read these files in order:

- [USDat analyst report](run/asset-investment-diligence/tokens/eth-mainnet-usdat/analyst-report.md)
- [USDat technical report](run/asset-investment-diligence/tokens/eth-mainnet-usdat/technical-report.md)
- [USDat feed graph](run/oracle-analysis/tokens/eth-mainnet-usdat-gearbox-oracle/oracle/feed-graph.md)
- [USDat protocol-fit memo](run/oracle-analysis/tokens/eth-mainnet-usdat-gearbox-oracle/oracle/protocol-fit-memo.md)
- [sUSDat analyst report](run/asset-investment-diligence/tokens/eth-mainnet-susdat/analyst-report.md)
- [sUSDat technical report](run/asset-investment-diligence/tokens/eth-mainnet-susdat/technical-report.md)
- [sUSDat feed graph](run/oracle-analysis/tokens/eth-mainnet-susdat-gearbox-oracle/oracle/feed-graph.md)
- [sUSDat protocol-fit memo](run/oracle-analysis/tokens/eth-mainnet-susdat-gearbox-oracle/oracle/protocol-fit-memo.md)
- [combined Analyze → Propose return](run/agentic-flow/analyze-and-propose.md)

## Reproduction

From the repository root:

```bash
python3 dev/tools/run_workflow.py analyze-propose \
  --input dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/input.json \
  --run-root dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/run \
  --mode validate \
  --resume \
  --format markdown
```

Expected result:

```text
Status: pass
Exit code: 0
asset: pass
oracle: pass
combined: pass
```

The command regenerates validation side files inside `run/`. Those generated files are intentionally not the primary review surface.
