# Oracle valid no-market/no-route fixture

## What was analyzed
This synthetic fixture analyzes SampleBaseToken as Gearbox collateral on Ethereum mainnet and models an adapter-valid negative investigation.

## Manifest
The manifest is `run-manifest.json`.

## Scope folders
- `tokens/sample-token-a-11111111`

## Files to read first
Read `index.md`, `tokens/sample-token-a-11111111/oracle/protocol-fit-memo.md`, `tokens/sample-token-a-11111111/raw/evidence-ledger.json`, and `verification/final-oracle-analysis-verification.md` first.

## Final validation status
Status: review_required because the valid no-market/no-route result is not Preview readiness. The fixture should not emit `oracle.protocol_adapter_no_result_proof_bundle`, `oracle.protocol_adapter_no_result_evidence_ledger`, or `oracle.protocol_adapter_not_investigated_not_no_result` findings.
