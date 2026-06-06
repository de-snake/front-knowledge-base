# Subagent prompts

These are paste-ready prompts for delegated workers. Replace bracketed fields before use.

## Shared stage-worker return contract

Every stage worker must return a machine-checkable compressed handoff. Include explicit fields for `status`, `run_artifact_root`, `artifact_paths`, `verification_path`, `final_verification`, `workflow_harness_report`, `blockers`, `blocked_scopes`, `review_required_scopes`, `dominant_blockers`, `live_input_blockers`, `preview_execute_relevance`, `not_in_scope`, `null_fields`, and `commands_run` when applicable.

Use explicit `null` for unknown values and `not_in_scope` for fields that do not apply. Do not omit required fields because they are inconvenient, and do not handwave final verification with phrases like "looks good" or "not verified" without a concrete verification artifact, command, or blocker.

## S1 prompt — General asset mining

Goal:

Collect token-level evidence for `[symbol]` on `[chain]` at `[token_address]` and write the S1 artifacts required by `user/references/workflows/asset-investment-diligence/stage-contracts.md`.

Context:

- Run artifact root: `[run_artifact_root]`.
- Token artifact directory: `[token_artifact_dir]`, for example `tokens/ethereum-sample-vault-token-22222222`.
- Read `methodology.md` before writing.
- Token scope:
  - chain_id: `[chain_id]`
  - chain: `[chain]`
  - symbol: `[symbol]`
  - token_address: `[token_address]`
  - intended_use: `[intended_use]`
- Output directory prefix: `[token_artifact_dir]/research/`.

Instructions:

1. Collect evidence for on-chain admin/proxy/roles, issuer/backing/security, transfer/liquidity/oracle/governance.
2. Write:
   - `[token_artifact_dir]/scope.json`
   - `[token_artifact_dir]/research/onchain-admin.md`
   - `[token_artifact_dir]/research/issuer-backing-security.md`
   - `[token_artifact_dir]/research/transfer-liquidity-oracle-governance.md`
   - `[token_artifact_dir]/technical-report.md`
3. Include source URLs, dates, confidence, and missing-data behavior.
4. Do not write an investment recommendation.
5. Return only a compressed handoff:
   - artifact paths;
   - five strongest numeric facts;
   - top risks;
   - blockers;
   - validation status.

Do not return raw contract source or raw API dumps to the parent.

## S2 prompt — Asset-risk analyst report

Goal:

Convert S1 evidence for `[symbol]` into an analyst-readable token risk report.

Context:

- Run artifact root: `[run_artifact_root]`.
- Token artifact directory: `[token_artifact_dir]`.
- Read `requirements-brief.md`.
- Read these S1 artifacts:
  - `[technical_report_path]`
  - `[research_onchain_admin_path]`
  - `[research_issuer_backing_security_path]`
  - `[research_transfer_liquidity_oracle_governance_path]`
- Output report: `[token_artifact_dir]/analyst-report.md`.
- Output verification: `[token_artifact_dir]/verification.md`.

Instructions:

1. Write a decision-useful token-level analyst report with plain-language sections:
   - Executive view.
   - What the token represents.
   - Main risk implications.
   - Backing and NAV quality.
   - Liquidity and exit risk.
   - Controls, governance, and legal restrictions.
   - Pricing/oracle risk in plain language.
   - What must be checked before live use.
   - Evidence quality.
   - Source map.
   - Technical appendix pointer.
2. Preserve source IDs and confidence notes.
3. Do not compare against other tokens.
4. Do not include code fences.
5. Do not give a recommendation or suitability verdict.
6. Return compressed handoff only:
   - report path;
   - executive view;
   - key risk implications;
   - missing-behavior blockers;
   - numeric facts;
   - verification result.

## S3 prompt — PT market/economics analysis

Goal:

Identify and analyze the exact Pendle PT market for `[symbol]` maturity `[maturity_date]` on `[chain]`.

Context:

- Run artifact root: `[run_artifact_root]`.
- PT artifact directory: `[pt_artifact_dir]`, for example `pt-markets/ethereum-pt-sample-vault-token-2026-08-27-abc12345`.
- Underlying token report: `[underlying_report_path]`.
- Underlying technical report: `[underlying_technical_report_path]`.
- PT scope:
  - underlying symbol: `[symbol]`
  - underlying token address: `[token_address]`
  - chain_id: `[chain_id]`
  - target maturity: `[maturity_date]`
  - user days label: `[days_label]`

Instructions:

1. Identify the exact Pendle market, PT, SY, YT, maturity, accounting asset, and output asset.
2. Fetch or read current market snapshot evidence from approved/local sources.
3. Calculate:
   - gross ROI to accounting asset;
   - simple APR;
   - compound APY;
   - break-even accounting-asset drawdown;
   - liquidity snapshot.
4. Write:
   - `[pt_artifact_dir]/scope.json`
   - `[pt_artifact_dir]/analyst-report.md`
   - `[pt_artifact_dir]/technical-report.md`
   - `[pt_artifact_dir]/verification.md`
5. Separate inherited token risk from PT-specific risk.
6. Return compressed handoff only:
   - artifact paths;
   - market/PT/SY/YT addresses;
   - maturity;
   - PT price;
   - accounting asset price;
   - implied APY;
   - liquidity;
   - break-even drawdown;
   - blockers.

## S4 prompt — X/social mining

Goal:

Collect X/social evidence for `[scope_name]` covering points, yield, PT return, depeg/stress, redemption, queue, liquidity, and risk narratives.

Context:

- Run artifact root: `[run_artifact_root]`.
- Underlying report: `[underlying_report_path]`.
- PT report, if applicable: `[pt_report_path]`.
- Output: `x-research/x-research-[scope-slug].md`.
- Use Hermes `x_search` first.
- X access is read-only. Do not post, like, follow, DM, or perform account actions.

Required query angles:

- Exact ticker and market label.
- Issuer/project variants.
- Points/airdrop/program names.
- STAC/STRC/yield terms.
- PT implied APY / fixed yield / maturity.
- Risk terms: depeg, redemption, freeze, blacklist, queue, liquidity, criticism, stress.
- Date-bounded recent search.
- Discovered key handles.

Instructions:

1. Write sections:
   - Scope.
   - Executive read.
   - Query log.
   - Distinct return models.
   - Distinct risk narratives.
   - Source index.
   - Signal vs noise.
   - Open threads.
2. Each material claim must have handle, date/search-window date, and status URL/ID.
3. If a material claim lacks full citation, mark it `citation_degraded` at the claim line.
4. Separate social speculation from local/source-artifact facts.
5. Return compressed handoff only:
   - artifact path;
   - return models;
   - risk narratives;
   - points mechanics;
   - source count;
   - degraded-citation count;
   - validation status.

## S5 prompt — X/social synthesis

Goal:

Synthesize all X/social artifacts into one cross-scope social expectations overlay.

Context:

- Run artifact root: `[run_artifact_root]`.
- Input artifacts:
  - `[x_artifact_1]`
  - `[x_artifact_2]`
  - `[x_artifact_3]`
  - `[x_artifact_4]`
- Output: `x-research/index.md`.
- Verification: `verification/final-x-research-points-yield-verification.md`.

Instructions:

1. Synthesize return models, not raw X posts.
2. Separate:
   - social estimates;
   - local/source-artifact facts;
   - degraded citations.
3. Cover:
   - points uncertainty;
   - STAC/STRC/yield uncertainty;
   - issuer/redemption/freeze/control risk;
   - PT liquidity/maturity/accounting risk;
   - crowded farming/leverage/unwind risk.
4. Identify contradictions and likely disagreement sources.
5. Validate that all scoped artifacts are represented and no extra token/maturity is introduced.
6. Return compressed handoff:
   - synthesis path;
   - main return narratives;
   - main risk narratives;
   - contradictions;
   - verification result.

## S6 prompt — Quantitative underwriting

Goal:

Build a decision-grade investment analyst report from token reports, PT reports, and social synthesis.

Context:

- Run artifact root: `[run_artifact_root]`.
- Token directories: `[token_artifact_dirs]`.
- PT market directories: `[pt_artifact_dirs]`.
- Methodology output: `investment-analysis/quantitative-underwriting-methodology.md`.
- Report output: `investment-analysis/investment-analyst-report-points-pt-risk-return.md`.
- Index output: `investment-analysis/index.md`.
- Input token reports:
  - `[token_report_paths]`
- Input PT reports, if applicable:
  - `[pt_report_paths]`
- Input social synthesis, if applicable:
  - `[x_synthesis_path]`
- Position size: `[position_size]`.
- Base hurdle: `[base_hurdle]`.
- Opportunistic hurdle: `[opportunistic_hurdle]`.

Instructions:

1. Define or reuse methodology for:
   - PT ROI/APR;
   - points EV/ROI/APR;
   - expected loss;
   - price-stability certainty;
   - risk-adjusted return;
   - break-even points ROI.
2. Compute gross and risk-adjusted numbers for every scoped strategy.
3. Make expected-loss priors explicit. Do not hide uncertainty in adjectives.
4. Produce decision statuses with assumption triggers.
5. Include required live inputs before capital allocation.
6. Return compressed handoff:
   - report paths;
   - top conclusions;
   - risk-adjusted returns;
   - points break-evens;
   - live-input blockers;
   - validation result.

## S7 prompt — Final verification

Goal:

Verify the completed workflow artifact set.

Context:

- Run artifact root: `[run_artifact_root]`.
- Workflow manifest: `user/references/workflows/asset-investment-diligence/workflow.json`.
- Stage contracts: `user/references/workflows/asset-investment-diligence/stage-contracts.md`.

Instructions:

1. Verify all declared outputs exist for the run scope.
2. Verify `output-structure.md` layout: token outputs under `tokens/<token-slug>/`, PT outputs under `pt-markets/<pt-scope-slug>/`, and run-level `run-manifest.json`, `index.md`, and final verification.
3. Check cross-links resolve.
4. Check required quantitative fields exist.
5. Check citation-degraded social claims are marked.
6. Run workspace validation from monorepo root:
   - `python3 scripts/workspace_sync.py --check`
   - `python3 scripts/workspace_policy_check.py --all`
7. Write `verification/final-investment-analysis-verification.md`.
8. Return final compressed handoff with these exact fields:
   - `status`: `pass`, `review_required`, or `fail`;
   - `run_artifact_root`;
   - `artifact_paths`;
   - `verification_path`;
   - `final_verification`;
   - `workflow_harness_report`;
   - `commands_run` with command, cwd, exit code, and output marker;
   - `blockers` using `[]` when none remain;
   - `blocked_scopes` using `[]` when no scope is blocked;
   - `review_required_scopes` using `[]` when no scope requires review;
   - `dominant_blockers` using `[]` when none remain;
   - `live_input_blockers` using `[]` when none remain;
   - `preview_execute_relevance` explaining whether any result is safe to carry toward Preview / Execute;
   - `not_in_scope` for excluded scopes such as absent PT markets;
   - `null_fields` for required fields whose value is genuinely unknown.

Do not handwave final verification. If a command was not run or a verification artifact is missing, return `review_required` or `fail` with a concrete blocker rather than a verbal assurance.
