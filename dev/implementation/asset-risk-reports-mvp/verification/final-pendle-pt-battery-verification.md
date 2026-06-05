# Final verification — Pendle PT four-market analysis battery

Verification date: 2026-06-04 UTC
Verifier: Hermes operator recovery after verifier protocol violation
Task: `t_653751cb`

## Final decision

PASS. The four-market Pendle PT battery satisfies the final QA contract.

The battery is approved as source-linked factual analysis for downstream synthesis. It does not decide final use, collateral acceptance, token choice, or live actions.

## Files reviewed

- `pendle-pt-index.md`
- `reports/pendle-pt-eth-mainnet-apyusd-2026-08-27.md`
- `technical-reports/pendle-pt-eth-mainnet-apyusd-2026-08-27.md`
- `verification/pendle-pt-eth-mainnet-apyusd-2026-08-27.md`
- `reports/eth-mainnet-apyusd.md`
- `reports/pendle-pt-eth-mainnet-apxusd-2026-11-05.md`
- `technical-reports/pendle-pt-eth-mainnet-apxusd-2026-11-05.md`
- `verification/pendle-pt-eth-mainnet-apxusd-2026-11-05.md`
- `reports/eth-mainnet-apxusd.md`
- `reports/pendle-pt-eth-mainnet-usdat-2026-08-27.md`
- `technical-reports/pendle-pt-eth-mainnet-usdat-2026-08-27.md`
- `verification/pendle-pt-eth-mainnet-usdat-2026-08-27.md`
- `reports/eth-mainnet-usdat.md`
- `reports/pendle-pt-eth-mainnet-susdat-2026-08-27.md`
- `technical-reports/pendle-pt-eth-mainnet-susdat-2026-08-27.md`
- `verification/pendle-pt-eth-mainnet-susdat-2026-08-27.md`
- `reports/eth-mainnet-susdat.md`

## Scope check

- Pendle PT apyUSD — 27 Aug 2026: `apyUSD`, maturity `2026-08-27`, user days label `83 days`, market `0x30bb9ee8dc6aab322dc3a0d36063cbf06a9e5952`, PT `0xee5c7cda577484b70b65c21235ecbd302bb290e2`, SY `0x04f8dca7bccd8997ac57ca6fef7c705e17d6bcb6`, YT `0x67553fb2ab2a411029387e1c53c0a3e55f8d10c9`.
- Pendle PT apxUSD — 05 Nov 2026: `apxUSD`, maturity `2026-11-05`, user days label `153 days`, market `0xaf0349fb9b1ba07d34381870c59b560b31412660`, PT `0xaf687b5ecb525ccea96115088999b4ed80c388b6`, SY `0x4f116ee5bcd227d1a1c4f57918d694a4abe7b3fc`, YT `0x7fbc01c63b0ac372ec75907f3a1d8adc8cf28e1f`.
- Pendle PT USDat — 27 Aug 2026: `USDat`, maturity `2026-08-27`, user days label `83 days`, market `0x9afe7a057a09cf5da748d952078c9c99938b4329`, PT `0x1d69402390657308c91179aa184bf992908c1e08`, SY `0x7a7de491e1be5287874904e2b7c8488249a4d0a9`, YT `0x076a3ea71e83ca09319b161e40f5fb3bb943d3c6`.
- Pendle PT sUSDat — 27 Aug 2026: `sUSDat`, maturity `2026-08-27`, user days label `83 days`, market `0x91bc86899c8391b6caaf26535b9cd82efe49a189`, PT `0xc689f76f90fe1762fac55983ff25ae71033a84f7`, SY `0x8917f8c7feb840b5837edc7e128123baa2f289f9`, YT `0x7956bb9504b8a1f515f2890e309cee398198d3bd`.

Exactly these four PT markets are represented. No additional market scope is introduced by `pendle-pt-index.md`.

## Checklist

- required files exist: PASS
- glob counts exact four: PASS
- index exists: PASS
- index exactly four market sections: PASS
- all four user supplied markets represented: PASS
- every asset level verification passed: PASS
- exact market ids sourced or blocked: PASS
- inherited underlying vs pt specific risk split: PASS
- analyst reports readable: PASS
- analyst source links present: PASS
- index links exist: PASS
- missing behavior retained: PASS
- no affirmative action selection language: PASS
- terminology scan clean: PASS
- no extra market scope: PASS

## Per-market asset-level status

- `pendle-pt-eth-mainnet-apyusd-2026-08-27`: scope=PASS; asset verification=PASS; inherited/PT split=PASS; missing_behavior=PASS.
- `pendle-pt-eth-mainnet-apxusd-2026-11-05`: scope=PASS; asset verification=PASS; inherited/PT split=PASS; missing_behavior=PASS.
- `pendle-pt-eth-mainnet-usdat-2026-08-27`: scope=PASS; asset verification=PASS; inherited/PT split=PASS; missing_behavior=PASS.
- `pendle-pt-eth-mainnet-susdat-2026-08-27`: scope=PASS; asset verification=PASS; inherited/PT split=PASS; missing_behavior=PASS.

## Terminology scan

PASS. Canonical Gearbox terms appear only contextually where relevant, and malformed lowercase/hyphenated variants scanned by this verifier were absent.

## Retained caveats

- Live size-specific PT/SY route quotes and slippage remain missing for all four markets; `missing_behavior: block_automation`.
- Gearbox-compatible PT oracle/feed design remains unverified; `missing_behavior: review_required`.
- Pendle market/PT/SY/YT role, upgrade, pause, and emergency-control state remains a production-review item; `missing_behavior: review_required`.
- Underlying issuer/backing/restriction/redemption state must be refreshed before live use; inherited dossiers classify the exact block/review behavior per asset.
- Accounting-asset handling requires review where the named underlying and maturity accounting asset differ.

## Deterministic check result

`FINAL_PENDLE_PT_BATTERY_CHECK_PASS`

## Final verifier decision

Complete the final Pendle PT battery verifier card. The downstream X/social-expectations lane can proceed independently while preserving the caveats above.
