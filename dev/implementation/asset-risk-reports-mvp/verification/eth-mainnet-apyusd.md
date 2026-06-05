# apyx apyUSD — dossier QA verification

Report date: 2026-06-04 UTC
Verifier: Hermes operator recovery after QA worker crashed
Dossier: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/reports/eth-mainnet-apyusd.md`

## Verdict

PASS for MVP asset-risk reasoning.

This is a source-linked factual dossier. It does not rank the asset, approve it, provide a suitability verdict, or make an investment recommendation.

## Checks performed

- Token identity is pinned to Ethereum mainnet `chain_id: 1` and token address `0x38EEb52F0771140d10c4E9A9a72349A329Fe8a6A`.
- Report contains an agent-context summary and one-paragraph mechanism.
- Report contains filled pipeline sections for identity, issuer/business model, backing/NAV, admin/sensitive actions, audits/incidents, transfer/liquidity, oracle/pricing, governance watchlist, data quality, highest-impact unknowns, and sources.
- At least two primary source classes are represented: onchain / verified source evidence and issuer documentation.
- Admin and sensitive actions are explicitly checked, including AccessManager, Safe-compatible role holder, UUPS upgrade path, pause, deny-list, receipt, fees, vesting, and role-0 caveats.
- NAV/backing is classified with `nav_model: collateralized vault / issuer NAV / dividend-backed underlying` and explains the `apxUSD` dependency.
- Transferability, freeze/deny-list, redemption receipt, DEX liquidity, and size-dependent exit caveats are documented.
- Oracle/pricing methodology is documented as ERC-4626 internal accounting and explicitly separates vault accounting from market exit value.
- Missing material fields use `missing_behavior` labels, including `review_required`, `cannot_rank_cleanly`, and `block_automation` where relevant.
- Source list contains IDs used in the dossier and source class / access / confidence columns.
- Header language explicitly says no ranking, acceptance, suitability verdict, portfolio action, or investment recommendation is provided.

## Minor caveats retained intentionally

- Reserve/custody/attestation PDFs were identified but not fully reconciled; dossier correctly marks this as `review_required` / `cannot_rank_cleanly`.
- Safe pending transactions and modules/guard were not fully decoded; dossier correctly marks production actions as `block_automation` until refreshed.
- Market stress history was not built beyond sampled quotes; dossier keeps this as `review_required`.

## Verification result

The dossier satisfies the methodology acceptance criteria for MVP use as a factual substrate. Any production action still requires a fresh Preview covering route quotes, pause/deny-list/receipt state, pending governance/admin transactions, and backing-state refresh.
