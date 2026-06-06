# Evidence ledger fixture — positive and no-result

This fixture demonstrates the generalized `evidence-ledger-v1` contract with synthetic data only.

Files:

- `evidence-ledger.json` — one positive RPC fact, one positive HTTP/API fact, and one negative/no-result investigation fact.
- `raw/rpc-decimals-output.txt` — raw EVM call output for the positive RPC fact.
- `raw/api-market-response.json` — raw API response for the positive HTTP/API fact.
- `raw/no-result-search-log.json` — raw query log for the no-result fact.

The fixture intentionally uses placeholder sample scopes and `example.invalid` sources so it is reusable for asset, oracle, and protocol-adapter validators without encoding any real asset.
