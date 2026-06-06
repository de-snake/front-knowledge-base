# Source primitive audit

Status: pass.

## Chainlink SampleBaseToken/USD primitive
- Source identity: Chainlink SampleBaseToken/USD at address 0x5555555555555555555555555555555555555555.
- Source type: Chainlink market oracle primitive.
- Timestamp / reporting cadence: latest report timestamp recorded in raw feed probe; heartbeat unavailable marker recorded if not returned.
- Trust / methodology: Chainlink signer set and reporting methodology; unavailable fields are marked unknown, not assumed.
- Raw evidence pointer: raw/source-evidence/missing-sample-token-a-feed.md.

## Hardcoded scalar primitive
- Source identity: hardcoded scalar 1.0 in the feed graph.
- Source type: hardcoded primitive.
- Timestamp / reporting cadence: not applicable; static configuration.
- Trust / methodology: invariant is unit scaling only; it breaks if token decimals or scalar semantics change.
- Raw evidence pointer: raw/source-evidence/hardcoded-scalar.md.
