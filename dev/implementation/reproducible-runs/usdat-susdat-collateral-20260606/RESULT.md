# Result — USDat / sUSDat collateral Analyze → Propose

Generated: 2026-06-06

## Question

Should USDat or sUSDat be treated as acceptable Gearbox Credit Account collateral candidates on Ethereum mainnet when borrowing USDC at a 9% borrow-rate assumption?

## Validation result

```text
Status: pass
Exit code: 0
asset: pass
oracle: pass
combined: pass
```

The validator reports had no P0/P1/P2 findings in the parent validation summary.

## Workflow decision

```text
Discover: complete by user premise
Analyze: complete
Propose: request_more_inputs
Preview: blocked
Execute: blocked
Monitor: not_started
```

## Recommendation returned by the run

USDat is the stronger Analyze-stage collateral candidate because its supplied Gearbox feed is market-derived from the USDat/USDC Curve pool and observed liquidity is materially deeper.

sUSDat remains more conditional because the supplied feed uses ERC-4626 accounting over USDat while immediate recovery can depend on thinner secondary liquidity, queue processing, and issuer / STRC realization.

Neither collateral candidate is ready for Preview or Execute.

## Required follow-up inputs before decision-grade proposal

- Evaluated Gearbox market / Credit Manager / pool for USDat.
- Evaluated Gearbox market / Credit Manager / pool for sUSDat.
- Position size or scenario size range.
- Target leverage or scenario leverage.
- Intended hold horizon.
- User risk policy: HF floor, max drawdown, automation policy.
- Wallet / Credit Account / liquidator eligibility for holding, transfer, redemption, freeze, and blacklist state.
- Size-specific route or liquidation quote for the proposed unwind path.

## Reproduction command

```bash
python3 dev/tools/run_workflow.py analyze-propose \
  --input dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/input.json \
  --run-root dev/implementation/reproducible-runs/usdat-susdat-collateral-20260606/run \
  --mode validate \
  --resume \
  --format markdown
```
