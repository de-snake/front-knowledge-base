# Analyze -> Propose parent return

## Stage status

- Discover: complete by user premise
- Analyze: complete
- Propose: request_more_inputs
- Preview: blocked
- Execute: blocked
- Monitor: not_started

## Status block

Formal validation has run for the child workflows and the parent validator will re-run this file. Semantic review was not run. Workflow decision readiness remains review_required because the run has unresolved live inputs and the proposal gate is request_more_inputs, not a decision-grade pass.

## Analyze artifacts

- asset child report: [asset-investment-diligence/verification/workflow-harness-report.json](../asset-investment-diligence/verification/workflow-harness-report.json)
- asset final verification: [asset-investment-diligence/verification/final-investment-analysis-verification.md](../asset-investment-diligence/verification/final-investment-analysis-verification.md)
- oracle child report: [oracle-analysis/verification/workflow-harness-report.json](../oracle-analysis/verification/workflow-harness-report.json)
- oracle final verification: [oracle-analysis/verification/final-oracle-analysis-verification.md](../oracle-analysis/verification/final-oracle-analysis-verification.md)
- parent return: [agentic-flow/analyze-and-propose.md](analyze-and-propose.md)

## Recommendation

USDat is the stronger Analyze-stage collateral candidate because its supplied Gearbox feed is market-derived from the USDat/USDC Curve pool and observed liquidity is materially deeper. sUSDat remains more conditional because the feed uses ERC-4626 accounting over USDat while immediate recovery can depend on thinner secondary liquidity, queue processing, and issuer/STRC realization.

Neither collateral candidate is ready for Preview or Execute.

## Requested next checks

- requested_input: `eth-mainnet-usdat-gearbox-oracle.market_or_credit_manager` - provide the evaluated Gearbox market/Credit Manager/pool.
- requested_input: `eth-mainnet-susdat-gearbox-oracle.market_or_credit_manager` - provide the evaluated Gearbox market/Credit Manager/pool.
- requested_input: `run.position_size` - provide position size or scenario size range.
- requested_input: `run.target_leverage` - provide target leverage or scenario leverage.
- requested_input: `run.hold_horizon` - provide intended hold horizon.
- requested_input: `run.user_risk_policy` - provide user HF floor, max drawdown, and automation policy.
- requested_input: wallet/Credit Account/liquidator eligibility - prove USDat/sUSDat/USDat-underlying holding, transfer, redemption, freeze, and blacklist state for the relevant addresses.
- requested_input: route/liquidation quote - provide size-specific route evidence for the proposed collateral unwind path.

```json
{
  "analyze_artifacts": {
    "asset_child_report": "asset-investment-diligence/verification/workflow-harness-report.json",
    "asset_final_verification": "asset-investment-diligence/verification/final-investment-analysis-verification.md",
    "oracle_child_report": "oracle-analysis/verification/workflow-harness-report.json",
    "oracle_final_verification": "oracle-analysis/verification/final-oracle-analysis-verification.md",
    "parent_return": "agentic-flow/analyze-and-propose.md"
  },
  "execute_gate": {
    "status": "blocked"
  },
  "preview_gate": {
    "status": "blocked"
  },
  "proposal_gate": {
    "blockers": [
      {
        "acceptance_criteria": "The evaluated Gearbox market/Credit Manager/pool is named before Preview.",
        "method": "Provide the Credit Manager or market context and rerun allowed-token, LT, route, and oracle binding checks.",
        "owner": "workflow_operator",
        "requested_input": "eth-mainnet-usdat-gearbox-oracle.market_or_credit_manager",
        "source": "oracle.eth-mainnet-usdat-gearbox-oracle.market_or_credit_manager",
        "status": "request_more_inputs"
      },
      {
        "acceptance_criteria": "The evaluated Gearbox market/Credit Manager/pool is named before Preview.",
        "method": "Provide the Credit Manager or market context and rerun allowed-token, LT, route, and oracle binding checks.",
        "owner": "workflow_operator",
        "requested_input": "eth-mainnet-susdat-gearbox-oracle.market_or_credit_manager",
        "source": "oracle.eth-mainnet-susdat-gearbox-oracle.market_or_credit_manager",
        "status": "request_more_inputs"
      },
      {
        "acceptance_criteria": "Position size, target leverage, and hold horizon are supplied before any risk/return or route conclusion.",
        "method": "Provide scenario size, leverage, and horizon; rerun quantitative underwriting and route checks.",
        "owner": "workflow_operator",
        "requested_input": "run.position_size, run.target_leverage, run.hold_horizon",
        "source": "run.live_inputs",
        "status": "request_more_inputs"
      },
      {
        "acceptance_criteria": "User HF floor/risk policy and issuer eligibility are supplied before Preview.",
        "method": "Provide user policy and wallet/Credit Account/liquidator eligibility/freeze/blacklist/redemption evidence.",
        "owner": "workflow_operator",
        "requested_input": "run.user_risk_policy and issuer eligibility state",
        "source": "run.policy_and_issuer_state",
        "status": "request_more_inputs"
      },
      {
        "acceptance_criteria": "Size-specific liquidation/unwind route evidence exists before Preview.",
        "method": "Quote the expected route at proposed size and compare executable value to oracle value.",
        "owner": "workflow_operator",
        "requested_input": "route/liquidation quote",
        "source": "gearbox.route_availability",
        "status": "request_more_inputs"
      }
    ],
    "explanation": "Analyze found plausible feed paths but unresolved live inputs prevent a decision-grade proposal.",
    "status": "request_more_inputs",
    "type": "request_more_inputs"
  },
  "schema_version": "agentic-analyze-propose-v1",
  "stage_status": {
    "Analyze": "complete",
    "Discover": "complete by user premise",
    "Execute": "blocked",
    "Monitor": "not_started",
    "Preview": "blocked",
    "Propose": "request_more_inputs"
  },
  "status_block": {
    "explanation": "Formal validation checks artifact structure; semantic review was not run, and workflow readiness remains review_required because live market, route, size, eligibility, and policy inputs are missing.",
    "formal_validation_status": "pass",
    "proposal_gate": {
      "blockers": [
        {
          "acceptance_criteria": "The evaluated Gearbox market/Credit Manager/pool is named before Preview.",
          "method": "Provide the Credit Manager or market context and rerun allowed-token, LT, route, and oracle binding checks.",
          "owner": "workflow_operator",
          "requested_input": "eth-mainnet-usdat-gearbox-oracle.market_or_credit_manager",
          "source": "oracle.eth-mainnet-usdat-gearbox-oracle.market_or_credit_manager",
          "status": "request_more_inputs"
        },
        {
          "acceptance_criteria": "The evaluated Gearbox market/Credit Manager/pool is named before Preview.",
          "method": "Provide the Credit Manager or market context and rerun allowed-token, LT, route, and oracle binding checks.",
          "owner": "workflow_operator",
          "requested_input": "eth-mainnet-susdat-gearbox-oracle.market_or_credit_manager",
          "source": "oracle.eth-mainnet-susdat-gearbox-oracle.market_or_credit_manager",
          "status": "request_more_inputs"
        },
        {
          "acceptance_criteria": "Position size, target leverage, and hold horizon are supplied before any risk/return or route conclusion.",
          "method": "Provide scenario size, leverage, and horizon; rerun quantitative underwriting and route checks.",
          "owner": "workflow_operator",
          "requested_input": "run.position_size, run.target_leverage, run.hold_horizon",
          "source": "run.live_inputs",
          "status": "request_more_inputs"
        },
        {
          "acceptance_criteria": "User HF floor/risk policy and issuer eligibility are supplied before Preview.",
          "method": "Provide user policy and wallet/Credit Account/liquidator eligibility/freeze/blacklist/redemption evidence.",
          "owner": "workflow_operator",
          "requested_input": "run.user_risk_policy and issuer eligibility state",
          "source": "run.policy_and_issuer_state",
          "status": "request_more_inputs"
        },
        {
          "acceptance_criteria": "Size-specific liquidation/unwind route evidence exists before Preview.",
          "method": "Quote the expected route at proposed size and compare executable value to oracle value.",
          "owner": "workflow_operator",
          "requested_input": "route/liquidation quote",
          "source": "gearbox.route_availability",
          "status": "request_more_inputs"
        }
      ],
      "explanation": "Analyze found plausible feed paths but unresolved live inputs prevent a decision-grade proposal.",
      "status": "request_more_inputs",
      "type": "request_more_inputs"
    },
    "semantic_review_status": "semantic_review_unavailable",
    "workflow_decision_status": "review_required"
  },
  "unresolved_gates": [
    {
      "gate": "Gearbox market/Credit Manager",
      "requested_input": "eth-mainnet-usdat-gearbox-oracle.market_or_credit_manager"
    },
    {
      "gate": "Gearbox market/Credit Manager",
      "requested_input": "eth-mainnet-susdat-gearbox-oracle.market_or_credit_manager"
    },
    {
      "gate": "position sizing",
      "requested_input": "run.position_size"
    },
    {
      "gate": "target leverage",
      "requested_input": "run.target_leverage"
    },
    {
      "gate": "hold horizon",
      "requested_input": "run.hold_horizon"
    },
    {
      "gate": "user risk policy",
      "requested_input": "run.user_risk_policy"
    },
    {
      "gate": "issuer and route state",
      "requested_input": "wallet eligibility and route/liquidation quote"
    }
  ]
}
```
