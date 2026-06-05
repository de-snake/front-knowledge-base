# Pendle PT sUSDat — 27 Aug 2026 — investment analyst risk/economics note

Report date: 2026-06-04 UTC
Protocol: Pendle
User-supplied days to maturity label: `83 days`
Chain and token identity: Ethereum mainnet (`chain_id: 1`), PT market `0x91bc86899c8391b6caaf26535b9cd82efe49a189`, PT token `0xc689f76f90fe1762fac55983ff25ae71033a84f7`, underlying `sUSDat` at `0xd166337499e176bbc38a1fbd113ab144e5bd2df7`.

This note is factual risk/economics analysis. Final use depends on a separate user mandate, protocol configuration review, and live Preview.

## 1. Executive view

The exact Pendle market for the supplied scope was identified from Pendle's active-market and market-detail APIs: `Pendle PT sUSDat — 27 Aug 2026` uses market `0x91bc86899c8391b6caaf26535b9cd82efe49a189`, PT `0xc689f76f90fe1762fac55983ff25ae71033a84f7`, SY `0x8917f8c7feb840b5837edc7e128123baa2f289f9`, YT `0x7956bb9504b8a1f515f2890e309cee398198d3bd`, and expiry `2026-08-27T00:00:00.000Z`.

The PT is a fixed-maturity claim whose price reflects a discount to its accounting asset. The reported point-in-time PT price was $0.935847, the accounting asset price was $0.999639, and the computed discount to that accounting asset was 6.38%. Pendle's implied APY field was 13.44%. These are market snapshots, not guarantees.

The main incremental risk is timing and exit path. Before maturity, exit depends on Pendle AMM liquidity. At maturity, value depends on Pendle redemption mechanics and the accounting asset. The PT also inherits the issuer, backing, restriction, and redemption risks already identified for `sUSDat`.

## 2. What this PT represents

Pendle separates a yield-bearing position into principal exposure and yield exposure. The PT is the principal side. Pendle documentation describes PT as redeemable at maturity against the accounting asset named for the market.

For this market, Pendle identifies the accounting asset as `USDat` at `0x23238f20b894f29041f48d88ee91131c395aaa71`. The PT label is `PT sUSDat (USDat)`. This accounting-asset detail matters because the economic maturity value may reference the accounting asset rather than one unit of the named yield-bearing wrapper.

## 3. How underlying-token risk carries into the PT

The PT inherits sUSDat exposure to an ERC-4626-style Saturn share token over USDat, disabled standard withdraw/redeem paths, requestRedeem plus withdrawal-queue NFT mechanics, STRC/digital-credit NAV exposure, blacklist checks, upgradeability, pending admin transitions, and oracle dependence on STRC valuation. The underlying sUSDat report marks STRC custody/NAV proof, audit-scope mapping, queue state, holder restrictions, and live exit depth as review-required or blocking for automated use.

The Pendle wrapper changes the timing and market mechanics, but it does not remove the underlying issuer-control, backing, restriction, or redemption issues. If the underlying token or accounting asset is frozen, restricted, depegged, paused, or difficult to redeem, the PT can be affected even when the PT itself still has an observable market price.

## 4. PT-specific yield and maturity economics

The fixed-yield signal comes from a PT trading below the expected maturity redemption reference. The 2026-06-04 API snapshot showed:

- PT price: $0.935847.
- Accounting asset price: $0.999639.
- Computed discount to accounting asset: 6.38%.
- Pendle implied APY: 13.44%.
- Pendle APY field: 1.05%.
- Active API yield range: 8.00%–25.00%.

Those values require fresh review before live use. The economic result depends on market price, time to maturity, redemption mechanics, and the condition of `USDat` / `sUSDat`.

## 5. Liquidity and exit risk

The current API liquidity snapshot was $5,125,750. This is a market-data field, not a guaranteed executable exit size.

Before maturity, the holder exits through Pendle market liquidity unless another route is available. That means the realized price can differ from the maturity value, especially during liquidity stress, stale pricing, restriction events, or issuer/NAV uncertainty.

For any live action, size-specific route quotes and slippage checks are required. Without them, automation remains blocked.

## 6. Pricing/oracle/valuation risk

The report found Pendle API prices and implied-yield fields, but it did not verify a Gearbox-compatible PT oracle or a production valuation feed for this PT.

A valuation design would need to handle:

- PT market price before maturity;
- convergence toward accounting-asset redemption at maturity;
- the accounting asset `USDat`;
- inherited `sUSDat` issuer and redemption restrictions;
- stale price updates;
- market depeg and liquidity stress.

Until that feed design is explicitly verified, the PT should be treated as requiring human review for valuation and blocking for automated live use.

## 7. Scenario behavior and live-use checks

If the underlying or accounting asset depegs, the PT discount and implied APY can stop representing clean fixed-yield economics.

If transfer restrictions, freeze controls, holder eligibility, or redemption access become binding, Pendle settlement or output conversion can be impaired.

If Pendle AMM liquidity falls, pre-maturity exit may require a wider discount or waiting until maturity.

If the market reaches maturity, the relevant question changes from AMM exit to redemption path, output asset, and holder eligibility.

Before any live use, refresh:

- market/PT/SY/YT addresses and maturity;
- current PT price, implied APY, liquidity, and route quote;
- accounting-asset price and output asset;
- holder eligibility and restriction state for `sUSDat` / `USDat`;
- oracle/feed availability and freshness;
- underlying issuer/admin/backing state from the local underlying dossier.

## 8. Evidence quality

Evidence quality is strongest for market identity, PT/SY/YT addresses, maturity, current API price fields, and local inherited-risk files.

Evidence quality is weaker for live size-specific exit depth, Pendle contract role and upgrade state, and any Gearbox-specific oracle or support status. Those fields require fresh review before production use.

## 9. Source map

- P1 — Pendle market API detail: [https://api-v2.pendle.finance/core/v1/1/markets/0x91bc86899c8391b6caaf26535b9cd82efe49a189](https://api-v2.pendle.finance/core/v1/1/markets/0x91bc86899c8391b6caaf26535b9cd82efe49a189); local copy `research/pendle-pt-eth-mainnet-susdat-2026-08-27/raw/pendle-market-api-2026-06-04.json`. source_class: market_data / protocol_api. accessed: 2026-06-04. confidence: high for current API fields.
- P2 — Pendle active markets API: [https://api-v2.pendle.finance/core/v1/1/markets/active](https://api-v2.pendle.finance/core/v1/1/markets/active); local exact-match copy `research/pendle-pt-eth-mainnet-susdat-2026-08-27/raw/pendle-active-market-details-2026-06-04.json`. source_class: market_data / protocol_api. accessed: 2026-06-04. confidence: high for active listing.
- P3 — Local same-underlying candidate scan: `research/pendle-pt-eth-mainnet-susdat-2026-08-27/raw/pendle-active-candidates-susdat-2026-06-04.json`. source_class: local derived evidence. accessed: 2026-06-04. confidence: high for disambiguation within the active API response.
- P4 — Pendle PT documentation: [https://docs.pendle.finance/pendle-v2/ProtocolMechanics/YieldTokenization/PT](https://docs.pendle.finance/pendle-v2/ProtocolMechanics/YieldTokenization/PT). source_class: protocol_docs. accessed: 2026-06-04. confidence: high for PT mechanism.
- P5 — Pendle AMM documentation: [https://docs.pendle.finance/pendle-v2/ProtocolMechanics/LiquidityEngines/AMM](https://docs.pendle.finance/pendle-v2/ProtocolMechanics/LiquidityEngines/AMM). source_class: protocol_docs. accessed: 2026-06-04. confidence: high for AMM mechanism.
- P6 — Pendle FAQ: [https://docs.pendle.finance/pendle-v2/FAQ](https://docs.pendle.finance/pendle-v2/FAQ). source_class: protocol_docs. accessed: 2026-06-04. confidence: medium/high for maturity framing.
- U1 — Underlying analyst report: `reports/eth-mainnet-susdat.md`. source_class: local analyst report. accessed: 2026-06-04. confidence: high for inherited-risk summary.
- U2 — Underlying technical report: `technical-reports/eth-mainnet-susdat.md`. source_class: local technical dossier. accessed: 2026-06-04. confidence: high for inherited technical evidence.
- U3 — Underlying verification artifact: `verification/eth-mainnet-susdat.md`. source_class: local verification artifact. accessed: 2026-06-04. confidence: high for upstream QA status.
- E1 — Market/PT/SY/YT address pointers: [market](https://etherscan.io/address/0x91bc86899c8391b6caaf26535b9cd82efe49a189), [PT](https://etherscan.io/address/0xc689f76f90fe1762fac55983ff25ae71033a84f7), [SY](https://etherscan.io/address/0x8917f8c7feb840b5837edc7e128123baa2f289f9), [YT](https://etherscan.io/address/0x7956bb9504b8a1f515f2890e309cee398198d3bd). source_class: explorer / onchain pointer. accessed: 2026-06-04. confidence: medium because this report did not fully audit contract roles.

## 10. Technical appendix pointer

Technical dossier: `technical-reports/pendle-pt-eth-mainnet-susdat-2026-08-27.md`.
