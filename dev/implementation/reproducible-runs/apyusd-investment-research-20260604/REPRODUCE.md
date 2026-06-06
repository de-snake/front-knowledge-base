# Reproduce — apyUSD investment research dossier

This run predates the current Analyze → Propose formatting harness. Reproducing it means following the investment-research methodology directly and regenerating the same artifact classes, not running a fixed markdown renderer.

## Input

Use [`input.json`](input.json):

- chain: Ethereum mainnet / `chain_id: 1`
- token: `0x38EEb52F0771140d10c4E9A9a72349A329Fe8a6A`
- symbol: `apyUSD`
- issuer/protocol hint: `Apyx`
- report date: `2026-06-04 UTC`
- methodology: [`run/methodology.md`](run/methodology.md)

## Output contract

Regenerate these artifacts:

1. `run/tokens/eth-mainnet-apyusd/research/onchain-admin.md`
2. `run/tokens/eth-mainnet-apyusd/research/issuer-backing-security.md`
3. `run/tokens/eth-mainnet-apyusd/research/transfer-liquidity-oracle-governance.md`
4. `run/tokens/eth-mainnet-apyusd/technical-report.md`
5. `RESULT.md`
6. `run/tokens/eth-mainnet-apyusd/verification.md`

## Research sequence

### 1. Read the methodology

Read [`run/methodology.md`](run/methodology.md) before drafting anything.

Use its nine sections as the required evidence map:

1. identity and token semantics;
2. issuer / protocol and business model;
3. backing, NAV, and exposure map;
4. contract admin, multisigs, and sensitive actions;
5. audits, formal verification, and incidents;
6. transferability, redemption, and liquidity;
7. oracle and pricing methodology;
8. governance / change-feed watchlist;
9. data quality and missing-data behavior.

### 2. Gather evidence before synthesis

Produce separate research notes instead of writing the final report directly:

- `onchain-admin.md`: verified source, proxy/implementation, token metadata, ERC-4626 asset, AccessManager, sensitive functions, role holders, pause/deny-list/upgrade surfaces, raw onchain snapshots.
- `issuer-backing-security.md`: issuer docs, apyUSD/apxUSD mechanism, reserve/backing/transparency claims, attestations, audits, incidents, unresolved scope caveats.
- `transfer-liquidity-oracle-governance.md`: redemption mechanics, transfer restrictions, market depth, quote caveats, oracle/accounting methodology, governance/change watchlist.

Every material fact should carry source ID, source class, access date, freshness, and confidence.

### 3. Write the technical dossier

Use the research notes to generate `run/tokens/eth-mainnet-apyusd/technical-report.md`.

Rules:

- include the token address and chain in the header;
- fill all nine methodology sections;
- classify backing/NAV and token behavior explicitly;
- preserve `missing_behavior` labels for unresolved fields;
- avoid approval, suitability, ranking, position sizing, or execution language;
- include a source map that resolves every source ID used in the text.

### 4. Rewrite as the analyst-readable report

Generate [`RESULT.md`](RESULT.md) from the technical dossier.

Rules:

- optimize for a human investment/risk reviewer;
- keep the executive view short, then expand into backing, redemption, liquidity, control, legal, and oracle risk;
- do not add new facts absent from the technical dossier/research notes;
- keep caveats visible instead of hiding them behind polished prose;
- preserve source IDs for material claims;
- end with a technical appendix pointer and live-use checklist.

### 5. Verify

Run the package-integrity check:

```bash
python3 dev/tools/validate_research_package.py \
  dev/implementation/reproducible-runs/apyusd-investment-research-20260604
```

Expected result:

```text
Status: pass
```

Then manually verify the decision bar:

- source IDs in `RESULT.md` resolve in its source map;
- source IDs in `technical-report.md` resolve in its source map;
- no material claim appears in `RESULT.md` without support from the technical dossier or research notes;
- missing backing, audit-scope, redemption, liquidity, Safe/module, and market-stress details remain visible;
- the final report remains a risk note, not an investment recommendation.

## Why this differs from the harness demo

The harness demo proves structured workflow scaffolding and validation. This apyUSD report proves the quality target for the research output itself.

For future runs, the right direction is to keep this evidence-rich analyst report as the content target, then add only enough lightweight validation to prove artifact presence, source resolution, and missing-data behavior.
