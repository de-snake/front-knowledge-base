# Hastra PRIME — issuer/backing/security research

Report date: 2026-06-04 UTC
Analyst: Hermes operator recovery after worker provider-preflight overflow
Task scope: methodology sections 2, 3, and 5 only — issuer/protocol/business model; backing/NAV/exposure; audits/formal verification/incidents.
Input asset: Ethereum mainnet (`chain_id: 1`), `0x19ebb35279A16207Ec4ba82799CC64715065F7F6`, symbol `PRIME`, intended use unknown.
Output type: objective source-linked facts, not token selection, ranking, suitability verdict, or investment recommendation.

Related evidence:

- `research/hastra-prime/onchain-admin.md`
- `research/hastra-prime/raw/onchain-admin-snapshot-2026-06-04.json`
- `research/hastra-prime/raw/feed-verifier-snapshot-2026-06-04.json`

## Source index

| ID | URL / local evidence | source_class | freshness | accessed | confidence | Notes |
|---|---|---:|---:|---:|---:|---|
| S1 | `research/hastra-prime/onchain-admin.md` and raw snapshots | onchain | current | 2026-06-04 | high | Exact PRIME proxy/implementation, roles, FeedVerifier/NAV oracle, pause/freeze/admin event state. |
| S2 | `https://hastra.io/terms` | legal_terms | dated | 2026-06-04 | medium | Terms identify Signum Ltd / Provenance Cayman Foundation and describe wYLDS/PRIME mechanism, restrictions, no guarantees. |
| S3 | `https://hastra.io/proof-of-reserves` | issuer_docs | current | 2026-06-04 | medium | Hastra proof-of-reserves page with live displayed wYLDS/PRIME/vaulted-wYLDS metrics and audit labels. |
| S4 | `https://hastra.io/` | issuer_docs | current | 2026-06-04 | medium | Official product site/category context. |
| S5 | `https://github.com/provenance-io/hastra-eth-vault` | issuer_docs / source | current | 2026-06-04 | medium | Public repository and docs; repo text found in search says “Not yet deployed - Pending audit and security review,” which may be stale relative to deployed Sourcify-verified contracts. |
| S6 | `https://github.com/provenance-io/hastra-eth-vault/blob/main/docs/ROLES.md` | issuer_docs | current | 2026-06-04 | medium | Intended role meanings; current holders verified onchain in S1. |
| S7 | `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/methodology.md` | unknown | current | 2026-06-04 | high | Report labels and missing-data behavior. |

## Agent-context summary

Hastra PRIME is an Ethereum mainnet ERC-4626 vault-share token over Hastra wYLDS. Hastra terms describe PRIME as a liquid staking token representing participation in Figure Democratized Prime HELOC lending pools; PRIME accrues wYLDS based on the performance of Figure's Democratized Prime operations. The exact PRIME contract uses a Chainlink Data Streams / FeedVerifier-style NAV path rather than ordinary total-assets/total-supply conversion. The issuer/backing story is materially offchain and legal-entity dependent: wYLDS is described as backed by YLDS, YLDS is associated with Figure, and PRIME returns depend on HELOC operations. No final deployed-system public audit report was located in this bounded pass, so security posture remains `review_required`.

## 2. Issuer / protocol and business model

### Issuer / governing entity

Hastra terms state that the Site and Protocol are provided by Signum Ltd., a company organized under the laws of the British Virgin Islands, and state Signum Ltd. is a wholly owned subsidiary of Provenance Cayman Foundation. Source: S2 medium.

### Mechanism

- Users lock USDC and receive Solana-based wYLDS representing a claim against fully collateralized assets held by Hastra; users may stake wYLDS for PRIME. Source: S2 medium.
- wYLDS is described in the terms as backed 1:1 by YLDS, a yield-bearing stablecoin issued by Figure and registered with the SEC. Hastra says it holds YLDS as collateral for wYLDS but does not issue YLDS and makes no representations/warranties about YLDS or associated parties. Source: S2 medium.
- PRIME is described as a liquid staking token representing participation in Figure Democratized Prime HELOC lending pools. PRIME tokens accrue wYLDS based on the performance of Figure's Democratized Prime HELOC lending operations; wYLDS is derived from interest spreads on real-world home equity lines of credit. Source: S2 medium.
- Exact onchain contract semantics: PRIME is an ERC-4626 vault-share token over wYLDS asset `0x6aD038cA6C04e885630851278ca0a856Ad9a66Cc`, but conversions use verified NAV from `FeedVerifier` rather than only internal balances. Source: S1 high.

### Access and offchain dependencies

- Terms restrict eligibility: users must not be located in the United States or listed sanctioned/restricted jurisdictions; Hastra may require additional information/documentation and may block access or interests as required by law. Source: S2 medium.
- PRIME depends on Hastra, wYLDS/YLDS, Figure / Democratized Prime HELOC operations, NAV reporting, FeedVerifier/Chainlink Data Streams verification, and Ethereum contract admin roles. Sources: S1/S2 medium-high.
- Direct ordinary-holder redemption/claim semantics are contract-available through ERC-4626 deposit/mint/redeem/withdraw paths when not paused/frozen and when NAV is valid; legal/site eligibility and operational offchain constraints still apply. Source: S1 high, S2 medium.

## 3. Backing, NAV, and exposure map

`nav_model: staking-share / issuer NAV / RWA-linked HELOC exposure`

### Current exact-token values

At snapshot block `25243587`, the onchain/admin artifact recorded:

- `totalSupply() = 129096016382551` raw = `129,096,016.382551 PRIME`.
- `totalAssets() = 134374638283899` raw = `134,374,638.283899 wYLDS`.
- `getVerifiedNav() = 1040904685772521320` = `1.040904685772521320 wYLDS / PRIME`.
- `paused=false`.
- `navOracle = 0xdF4ab20fA7752Be52E41e42F1FD667f37964d6a3` and `navFeedId = 0x0007c8ed155d952e003b1e15ce7666fea785cfbe216577d578fce3920e997271`.

Source: S1 high.

### Reserve / backing evidence

- Hastra proof-of-reserves page displayed wYLDS backing at `101.08%`, wYLDS supply `400,776,067.41`, PRIME supply `379,393,659.83`, vaulted wYLDS supply `394,912,638.27`, and PRIME price `$1.0409` at the time extracted. Source: S3 medium. Treat as issuer web data, not independent audit by itself.
- The same page displayed Provenance YLDS balance / pending sale / pending redemption fields and Figure Markets Democratized Prime YLDS balance / current rate / earnings fields. Source: S3 medium.
- The onchain FeedVerifier snapshot shows recent NAV price and timestamp: `priceByFeed(current)=1040906939176726297`, `timestampByFeed=1780571081`, default staleness `3600` seconds, `paused=false`. Source: S1 high.

### Exposure caveats

- PRIME value depends on a chain of exposures: PRIME → wYLDS → YLDS / Hastra collateral arrangements → Figure Democratized Prime HELOC lending operations. Source: S2 medium; exact onchain PRIME/wYLDS link S1 high.
- NAV and market price are distinct: PRIME uses a NAV feed for contract conversions while any secondary-market price can diverge due to liquidity, freeze/pause/NAV availability, and legal eligibility. Source: S1 high.
- This card did not verify offchain audit workpapers, custody statements, YLDS issuer reports, Figure loan-pool performance data, or the legal enforceability of claims. `missing_behavior: review_required`.

## 5. Audits, formal verification, and incidents

### Security/audit reports located

- The Hastra proof-of-reserves page displays labels `Audit - Nov 25, 2025` and `Audit - Apr 12, 2026`, but the extraction did not expose the underlying audit report URLs or scopes. Source: S3 medium.
- Web search found the official GitHub repository `provenance-io/hastra-eth-vault`; its search snippet said “Not yet deployed - Pending audit and security review.” That language conflicts with the fact that PRIME and FeedVerifier are deployed and Sourcify full-match verified in the onchain/admin artifact, so it may be stale repo text. Source: S5 medium, S1 high.
- No final public smart-contract audit report URL for the deployed Ethereum PRIME / FeedVerifier implementation was located in this bounded pass. `missing_behavior: review_required`.

### Incidents / material events found in bounded pass

- Onchain/admin artifact observed two PRIME pause windows: 2026-05-04 21:51:11Z to 23:55:11Z, and 2026-06-02 14:53:47Z to 15:29:47Z. Current state was `paused=false`. Source: S1 high.
- No `AccountFrozen` or `AccountThawed` events were observed from the first code block through the snapshot in the onchain/admin artifact. Source: S1 high.
- FeedVerifier had no pause/unpause events observed and was `paused=false` at the snapshot; feed ID was changed to the current feed on 2026-04-23. Source: S1 high.
- No confirmed exploit, reserve shortfall, depeg, oracle failure, or redemption-delay postmortem for exact PRIME was found in the bounded sources used here. This is not proof none occurred. `missing_behavior: review_required`.

## Highest-impact unknowns

| Unknown / caveat | Why it matters | missing_behavior | Confidence |
|---|---|---|---|
| Public audit report scope for deployed PRIME / FeedVerifier was not located. | Security/audit status cannot be treated as clean. | `review_required` | high |
| Proof-of-reserves page showed audit labels but not report bodies/scopes in extracted content. | Reserve proof cannot be independently validated from labels alone. | `review_required` | high |
| wYLDS/YLDS/Figure HELOC loan-pool backing was not independently reconciled. | PRIME's economic exposure depends on offchain systems. | `review_required` | high |
| Legal eligibility and freeze/blocking policy were not mapped to exact onchain freeze usage policy. | Terms allow access/interest blocking under conditions; onchain freeze role exists. | `review_required` | high |
| No incident found in bounded sources. | Absence of evidence is not a clean incident history. | `continue` / `review_required` for acceptance | medium |

## Minimal handoff

Use PRIME as a mutable, issuer-controlled ERC-4626-style wYLDS staking share whose NAV is externally reported through FeedVerifier. Primary facts are enough for dossier synthesis, but audit status, reserve attestation scope, legal eligibility, and underlying wYLDS/YLDS/Figure exposure all remain review-required.
