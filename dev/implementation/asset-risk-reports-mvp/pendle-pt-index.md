# Pendle PT four-market index and unknowns summary

Scope date: 2026-06-04 UTC
Board: `asset-risk-dossiers-mvp`
Scope: exactly four Pendle Principal Token markets on Ethereum mainnet (`chain_id: 1`).

This index is factual source-linked context. It does not choose between markets, decide final use, or instruct live actions. Any live valuation, collateral integration, trade, liquidation, or post-maturity redemption path still requires a fresh protocol configuration review and live Preview.

Supersession note: this index is the four-market Pendle PT battery summary. It replaces any smaller Pendle-only scratch summary for these four supplied markets, while preserving the underlying asset dossiers as inherited inputs.

## Canonical market set

The represented PT markets are exactly:

- `Pendle PT apyUSD — 27 Aug 2026`: underlying `apyUSD`, maturity `2026-08-27`, user days label `83 days`.
- `Pendle PT apxUSD — 05 Nov 2026`: underlying `apxUSD`, maturity `2026-11-05`, user days label `153 days`.
- `Pendle PT USDat — 27 Aug 2026`: underlying `USDat`, maturity `2026-08-27`, user days label `83 days`.
- `Pendle PT sUSDat — 27 Aug 2026`: underlying `sUSDat`, maturity `2026-08-27`, user days label `83 days`.

No additional Pendle market is introduced by this index.

## Market 1: Pendle PT apyUSD — 27 Aug 2026

Scope identity:
- Chain: Ethereum mainnet (`chain_id: 1`).
- Underlying: `apyUSD` at `0x38eeb52f0771140d10c4e9a9a72349a329fe8a6a`.
- Maturity: `2026-08-27`.
- User days label: `83 days`.
- Pendle market / LP: `0x30bb9ee8dc6aab322dc3a0d36063cbf06a9e5952`.
- PT: `0xee5c7cda577484b70b65c21235ecbd302bb290e2`.
- SY: `0x04f8dca7bccd8997ac57ca6fef7c705e17d6bcb6`.
- YT: `0x67553fb2ab2a411029387e1c53c0a3e55f8d10c9`.
- Accounting asset for maturity economics: `apxUSD` at `0x98a878b1cd98131b271883b390f68d2c90674665`.

Artifact links:
- [Analyst PT report](reports/pendle-pt-eth-mainnet-apyusd-2026-08-27.md).
- [Technical PT report](technical-reports/pendle-pt-eth-mainnet-apyusd-2026-08-27.md).
- [PT verification](verification/pendle-pt-eth-mainnet-apyusd-2026-08-27.md).
- [Inherited underlying report](reports/eth-mainnet-apyusd.md).

Source quality:
- Market identity: high. Active-market and market-detail API snapshots agree on the supplied underlying/maturity and the PT/SY/YT contracts.
- Price/APY/liquidity snapshot: medium/high for the 2026-06-04 snapshot; refresh is required for any live valuation or Preview.
- Contract-role and upgrade-state depth: low/medium because the PT/SY/YT role surface was not fully audited in this pass.
- Gearbox PT support/feed state: low because no Gearbox-compatible PT oracle/feed was verified.

Fixed-yield and economic-risk summary:
- Snapshot PT price: $0.938959.
- Snapshot accounting asset price: $0.974237.
- Computed discount to accounting asset: 3.62%.
- Pendle implied APY field: 17.60%.
- Economic interpretation: the PT is a fixed-maturity claim whose economics converge only if Pendle redemption, the accounting asset, issuer/backing state, and market assumptions hold.

Inherited underlying-token risk:
- Apyx vault-share mechanics over apxUSD, AccessManager upgrade/control paths, deny-list/pause controls, fee/redemption settings, reserve/custody evidence gaps, and audit-scope uncertainty carry through to PT maturity and exit economics.

Incremental Pendle/PT market risk:
- Pre-maturity exit depends on Pendle AMM liquidity and route depth, not only final maturity mechanics.
- Maturity behavior depends on PT redemption, SY/accounting-asset routing, and any holder restrictions on the output asset.
- The PT holder does not receive variable yield or points separated into YT.
- If the underlying or accounting asset is frozen, deny-listed, paused, depegged, stale-priced, or difficult to redeem, the PT can be affected even with visible Pendle market metadata.

Liquidity and exit caveats:
- Size-specific route depth and slippage were not computed; `missing_behavior: block_automation` for any trade, liquidation, or live route Preview.
- API prices and liquidity are point-in-time 2026-06-04 values; `missing_behavior: refresh before live use`.

Highest-impact unknowns:
- Live PT/SY route quote and size-dependent slippage: `missing_behavior: block_automation`.
- Gearbox-compatible PT oracle/feed design: `missing_behavior: review_required`.
- Pendle market/PT/SY/YT role, upgrade, pause, and emergency-control state: `missing_behavior: review_required`.
- Underlying issuer/backing/restriction/redemption state: `missing_behavior: review_required` or `block_automation` according to the inherited dossier.
- Accounting-asset redemption semantics: `missing_behavior: review_required` when feed design, post-maturity path, or holder eligibility depends on the accounting asset.

## Market 2: Pendle PT apxUSD — 05 Nov 2026

Scope identity:
- Chain: Ethereum mainnet (`chain_id: 1`).
- Underlying: `apxUSD` at `0x98a878b1cd98131b271883b390f68d2c90674665`.
- Maturity: `2026-11-05`.
- User days label: `153 days`.
- Pendle market / LP: `0xaf0349fb9b1ba07d34381870c59b560b31412660`.
- PT: `0xaf687b5ecb525ccea96115088999b4ed80c388b6`.
- SY: `0x4f116ee5bcd227d1a1c4f57918d694a4abe7b3fc`.
- YT: `0x7fbc01c63b0ac372ec75907f3a1d8adc8cf28e1f`.
- Accounting asset for maturity economics: `apxUSD` at `0x98a878b1cd98131b271883b390f68d2c90674665`.

Artifact links:
- [Analyst PT report](reports/pendle-pt-eth-mainnet-apxusd-2026-11-05.md).
- [Technical PT report](technical-reports/pendle-pt-eth-mainnet-apxusd-2026-11-05.md).
- [PT verification](verification/pendle-pt-eth-mainnet-apxusd-2026-11-05.md).
- [Inherited underlying report](reports/eth-mainnet-apxusd.md).

Source quality:
- Market identity: high. Active-market and market-detail API snapshots agree on the supplied underlying/maturity and the PT/SY/YT contracts.
- Price/APY/liquidity snapshot: medium/high for the 2026-06-04 snapshot; refresh is required for any live valuation or Preview.
- Contract-role and upgrade-state depth: low/medium because the PT/SY/YT role surface was not fully audited in this pass.
- Gearbox PT support/feed state: low because no Gearbox-compatible PT oracle/feed was verified.

Fixed-yield and economic-risk summary:
- Snapshot PT price: $0.897297.
- Snapshot accounting asset price: $0.974237.
- Computed discount to accounting asset: 7.90%.
- Pendle implied APY field: 21.68%.
- Economic interpretation: the PT is a fixed-maturity claim whose economics converge only if Pendle redemption, the accounting asset, issuer/backing state, and market assumptions hold.

Inherited underlying-token risk:
- Apyx synthetic-dollar exposure, off-chain preferred-share collateral, UUPS upgradeability, AccessManager roles, pause/deny-list controls, eligible-participant primary mint/redeem limits, reserve/NAV gaps, and audit-scope uncertainty carry through to the PT.

Incremental Pendle/PT market risk:
- Pre-maturity exit depends on Pendle AMM liquidity and route depth, not only final maturity mechanics.
- Maturity behavior depends on PT redemption, SY/accounting-asset routing, and any holder restrictions on the output asset.
- The PT holder does not receive variable yield or points separated into YT.
- If the underlying or accounting asset is frozen, deny-listed, paused, depegged, stale-priced, or difficult to redeem, the PT can be affected even with visible Pendle market metadata.

Liquidity and exit caveats:
- Size-specific route depth and slippage were not computed; `missing_behavior: block_automation` for any trade, liquidation, or live route Preview.
- API prices and liquidity are point-in-time 2026-06-04 values; `missing_behavior: refresh before live use`.

Highest-impact unknowns:
- Live PT/SY route quote and size-dependent slippage: `missing_behavior: block_automation`.
- Gearbox-compatible PT oracle/feed design: `missing_behavior: review_required`.
- Pendle market/PT/SY/YT role, upgrade, pause, and emergency-control state: `missing_behavior: review_required`.
- Underlying issuer/backing/restriction/redemption state: `missing_behavior: review_required` or `block_automation` according to the inherited dossier.
- Accounting-asset redemption semantics: `missing_behavior: review_required` when feed design, post-maturity path, or holder eligibility depends on the accounting asset.

## Market 3: Pendle PT USDat — 27 Aug 2026

Scope identity:
- Chain: Ethereum mainnet (`chain_id: 1`).
- Underlying: `USDat` at `0x23238f20b894f29041f48d88ee91131c395aaa71`.
- Maturity: `2026-08-27`.
- User days label: `83 days`.
- Pendle market / LP: `0x9afe7a057a09cf5da748d952078c9c99938b4329`.
- PT: `0x1d69402390657308c91179aa184bf992908c1e08`.
- SY: `0x7a7de491e1be5287874904e2b7c8488249a4d0a9`.
- YT: `0x076a3ea71e83ca09319b161e40f5fb3bb943d3c6`.
- Accounting asset for maturity economics: `USDat` at `0x23238f20b894f29041f48d88ee91131c395aaa71`.

Artifact links:
- [Analyst PT report](reports/pendle-pt-eth-mainnet-usdat-2026-08-27.md).
- [Technical PT report](technical-reports/pendle-pt-eth-mainnet-usdat-2026-08-27.md).
- [PT verification](verification/pendle-pt-eth-mainnet-usdat-2026-08-27.md).
- [Inherited underlying report](reports/eth-mainnet-usdat.md).

Source quality:
- Market identity: high. Active-market and market-detail API snapshots agree on the supplied underlying/maturity and the PT/SY/YT contracts.
- Price/APY/liquidity snapshot: medium/high for the 2026-06-04 snapshot; refresh is required for any live valuation or Preview.
- Contract-role and upgrade-state depth: low/medium because the PT/SY/YT role surface was not fully audited in this pass.
- Gearbox PT support/feed state: low because no Gearbox-compatible PT oracle/feed was verified.

Fixed-yield and economic-risk summary:
- Snapshot PT price: $0.980282.
- Snapshot accounting asset price: $0.999639.
- Computed discount to accounting asset: 1.94%.
- Pendle implied APY field: 8.96%.
- Economic interpretation: the PT is a fixed-maturity claim whose economics converge only if Pendle redemption, the accounting asset, issuer/backing state, and market assumptions hold.

Inherited underlying-token risk:
- Saturn permissioned stablecoin exposure, launch backing by M0 $M per issuer docs, whitelist-enabled transfer/holding state, pause/freeze/forced-transfer paths, role-management, asset-claim, upgrade surfaces, reserve proof, route depth, and pending admin transitions carry through to PT settlement and post-maturity output.

Incremental Pendle/PT market risk:
- Pre-maturity exit depends on Pendle AMM liquidity and route depth, not only final maturity mechanics.
- Maturity behavior depends on PT redemption, SY/accounting-asset routing, and any holder restrictions on the output asset.
- The PT holder does not receive variable yield or points separated into YT.
- If the underlying or accounting asset is frozen, deny-listed, paused, depegged, stale-priced, or difficult to redeem, the PT can be affected even with visible Pendle market metadata.

Liquidity and exit caveats:
- Size-specific route depth and slippage were not computed; `missing_behavior: block_automation` for any trade, liquidation, or live route Preview.
- API prices and liquidity are point-in-time 2026-06-04 values; `missing_behavior: refresh before live use`.

Highest-impact unknowns:
- Live PT/SY route quote and size-dependent slippage: `missing_behavior: block_automation`.
- Gearbox-compatible PT oracle/feed design: `missing_behavior: review_required`.
- Pendle market/PT/SY/YT role, upgrade, pause, and emergency-control state: `missing_behavior: review_required`.
- Underlying issuer/backing/restriction/redemption state: `missing_behavior: review_required` or `block_automation` according to the inherited dossier.
- Accounting-asset redemption semantics: `missing_behavior: review_required` when feed design, post-maturity path, or holder eligibility depends on the accounting asset.

## Market 4: Pendle PT sUSDat — 27 Aug 2026

Scope identity:
- Chain: Ethereum mainnet (`chain_id: 1`).
- Underlying: `sUSDat` at `0xd166337499e176bbc38a1fbd113ab144e5bd2df7`.
- Maturity: `2026-08-27`.
- User days label: `83 days`.
- Pendle market / LP: `0x91bc86899c8391b6caaf26535b9cd82efe49a189`.
- PT: `0xc689f76f90fe1762fac55983ff25ae71033a84f7`.
- SY: `0x8917f8c7feb840b5837edc7e128123baa2f289f9`.
- YT: `0x7956bb9504b8a1f515f2890e309cee398198d3bd`.
- Accounting asset for maturity economics: `USDat` at `0x23238f20b894f29041f48d88ee91131c395aaa71`.

Artifact links:
- [Analyst PT report](reports/pendle-pt-eth-mainnet-susdat-2026-08-27.md).
- [Technical PT report](technical-reports/pendle-pt-eth-mainnet-susdat-2026-08-27.md).
- [PT verification](verification/pendle-pt-eth-mainnet-susdat-2026-08-27.md).
- [Inherited underlying report](reports/eth-mainnet-susdat.md).

Source quality:
- Market identity: high. Active-market and market-detail API snapshots agree on the supplied underlying/maturity and the PT/SY/YT contracts.
- Price/APY/liquidity snapshot: medium/high for the 2026-06-04 snapshot; refresh is required for any live valuation or Preview.
- Contract-role and upgrade-state depth: low/medium because the PT/SY/YT role surface was not fully audited in this pass.
- Gearbox PT support/feed state: low because no Gearbox-compatible PT oracle/feed was verified.

Fixed-yield and economic-risk summary:
- Snapshot PT price: $0.935847.
- Snapshot accounting asset price: $0.999639.
- Computed discount to accounting asset: 6.38%.
- Pendle implied APY field: 13.44%.
- Economic interpretation: the PT is a fixed-maturity claim whose economics converge only if Pendle redemption, the accounting asset, issuer/backing state, and market assumptions hold.

Inherited underlying-token risk:
- sUSDat ERC-4626-style share-token exposure over USDat, disabled standard withdraw/redeem paths, requestRedeem plus withdrawal-queue NFT mechanics, STRC/digital-credit NAV dependence, blacklist checks, upgradeability, pending admin transitions, and oracle dependence on STRC valuation carry through to PT economics.

Incremental Pendle/PT market risk:
- Pre-maturity exit depends on Pendle AMM liquidity and route depth, not only final maturity mechanics.
- Maturity behavior depends on PT redemption, SY/accounting-asset routing, and any holder restrictions on the output asset.
- The PT holder does not receive variable yield or points separated into YT.
- If the underlying or accounting asset is frozen, deny-listed, paused, depegged, stale-priced, or difficult to redeem, the PT can be affected even with visible Pendle market metadata.

Liquidity and exit caveats:
- Size-specific route depth and slippage were not computed; `missing_behavior: block_automation` for any trade, liquidation, or live route Preview.
- API prices and liquidity are point-in-time 2026-06-04 values; `missing_behavior: refresh before live use`.

Highest-impact unknowns:
- Live PT/SY route quote and size-dependent slippage: `missing_behavior: block_automation`.
- Gearbox-compatible PT oracle/feed design: `missing_behavior: review_required`.
- Pendle market/PT/SY/YT role, upgrade, pause, and emergency-control state: `missing_behavior: review_required`.
- Underlying issuer/backing/restriction/redemption state: `missing_behavior: review_required` or `block_automation` according to the inherited dossier.
- Accounting-asset redemption semantics: `missing_behavior: review_required` when feed design, post-maturity path, or holder eligibility depends on the accounting asset.

## Cross-market notes

Inherited underlying-token risk:
- The Apyx pair (`apyUSD`, `apxUSD`) carries issuer/collateral/admin/eligibility/oracle uncertainty from the underlying dossiers. The PT wrapper changes timing and exit mechanics but does not remove those risks.
- The Saturn pair (`USDat`, `sUSDat`) carries permissioned-token, blacklist/whitelist, freeze/forced-transfer, admin transition, reserve/NAV, and queue/redemption uncertainty from the underlying dossiers. The PT wrapper adds a Pendle market layer rather than replacing those controls.

Incremental Pendle/PT market risk:
- All four markets add PT/SY/YT contract dependency, maturity-redemption mechanics, pre-maturity AMM exit dependence, pricing snapshot staleness, and an unverified Gearbox-compatible PT oracle/feed requirement.
- All four markets require live route/depth refresh before any state-changing use because size-specific slippage was not computed.
- All four markets preserve `missing_behavior: review_required` for Pendle contract role/upgrade/emergency-control review.

Source-quality notes:
- Exact market/PT/SY/YT identities are high-confidence because active-market, market-detail, and verification artifacts agree.
- The yield, price, discount, APY, and liquidity fields are snapshot-quality only and should be refreshed before live valuation.
- Local underlying reports are verified as source-linked research inputs, but issuer/backing/admin state may change and must be refreshed for live use.
- Etherscan links in the technical reports are address pointers, not a full role or implementation audit.

Cross-market highest-impact unknowns:
- Gearbox-compatible PT oracle/feed design is not verified for any of the four markets: `missing_behavior: review_required`.
- Live size-specific route quotes and slippage are missing for every market: `missing_behavior: block_automation`.
- Pendle PT/SY/YT admin, upgrade, pause, and emergency controls are not fully audited: `missing_behavior: review_required`.
- Underlying issuer/backing/restriction state must be refreshed before live use: `missing_behavior: review_required` or `block_automation` according to the underlying dossier.
- Post-maturity output and accounting-asset handling require human review when the named underlying differs from the accounting asset, especially `apyUSD` using `apxUSD` and `sUSDat` using `USDat` as the accounting asset.

## Source index

- Methodology: [methodology.md](methodology.md).
- Requirements brief: [requirements-brief.md](requirements-brief.md).
- apyUSD PT: [analyst](reports/pendle-pt-eth-mainnet-apyusd-2026-08-27.md), [technical](technical-reports/pendle-pt-eth-mainnet-apyusd-2026-08-27.md), [verification](verification/pendle-pt-eth-mainnet-apyusd-2026-08-27.md), [underlying report](reports/eth-mainnet-apyusd.md).
- apxUSD PT: [analyst](reports/pendle-pt-eth-mainnet-apxusd-2026-11-05.md), [technical](technical-reports/pendle-pt-eth-mainnet-apxusd-2026-11-05.md), [verification](verification/pendle-pt-eth-mainnet-apxusd-2026-11-05.md), [underlying report](reports/eth-mainnet-apxusd.md).
- USDat PT: [analyst](reports/pendle-pt-eth-mainnet-usdat-2026-08-27.md), [technical](technical-reports/pendle-pt-eth-mainnet-usdat-2026-08-27.md), [verification](verification/pendle-pt-eth-mainnet-usdat-2026-08-27.md), [underlying report](reports/eth-mainnet-usdat.md).
- sUSDat PT: [analyst](reports/pendle-pt-eth-mainnet-susdat-2026-08-27.md), [technical](technical-reports/pendle-pt-eth-mainnet-susdat-2026-08-27.md), [verification](verification/pendle-pt-eth-mainnet-susdat-2026-08-27.md), [underlying report](reports/eth-mainnet-susdat.md).
