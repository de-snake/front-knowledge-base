# Asset-risk reports MVP — six-asset battery index

Board slug: `asset-risk-dossiers-mvp`
Date: 2026-06-04 UTC
Audience: investment analyst

This index supersedes the earlier four-asset index after the two expansion assets, Saturn USDat and apyx apxUSD, completed asset-level research, synthesis, and verification.

This folder covers exactly the six supplied assets listed below. It is factual risk-review context, not a ranking, recommendation, suitability verdict, position-sizing guide, token-selection note, or execution instruction.

The analyst-readable reports in `reports/` are the user-facing risk notes. The technical dossiers in `technical-reports/` preserve auditability, raw role/address evidence, source IDs, and method-level checks. The verification files in `verification/` record asset-level QA decisions.

Readability verification: [verification/analyst-readability-verification.md](verification/analyst-readability-verification.md)
Final battery verifier: [verification/final-six-asset-battery-verification.md](verification/final-six-asset-battery-verification.md)

## Supplied six-asset list

- Saturn sUSDat
  - Chain: Ethereum mainnet
  - `chain_id`: `1`
  - Address: `0xd166337499e176bbc38a1fbd113ab144e5bd2df7`
  - Symbol: `sUSDat`
  - Issuer hint: Saturn
  - Analyst report: [reports/eth-mainnet-susdat.md](reports/eth-mainnet-susdat.md)
  - Technical report: [technical-reports/eth-mainnet-susdat.md](technical-reports/eth-mainnet-susdat.md)
  - Verification: [verification/eth-mainnet-susdat.md](verification/eth-mainnet-susdat.md)

- apyx apyUSD
  - Chain: Ethereum mainnet
  - `chain_id`: `1`
  - Address: `0x38eeb52f0771140d10c4e9a9a72349a329fe8a6a`
  - Symbol: `apyUSD`
  - Issuer hint: apyx
  - Analyst report: [reports/eth-mainnet-apyusd.md](reports/eth-mainnet-apyusd.md)
  - Technical report: [technical-reports/eth-mainnet-apyusd.md](technical-reports/eth-mainnet-apyusd.md)
  - Verification: [verification/eth-mainnet-apyusd.md](verification/eth-mainnet-apyusd.md)

- Hastra PRIME
  - Chain: Ethereum mainnet
  - `chain_id`: `1`
  - Address: `0x19ebb35279A16207Ec4ba82799CC64715065F7F6`
  - Symbol: `PRIME`
  - Issuer hint: Hastra
  - Analyst report: [reports/eth-mainnet-prime.md](reports/eth-mainnet-prime.md)
  - Technical report: [technical-reports/eth-mainnet-prime.md](technical-reports/eth-mainnet-prime.md)
  - Verification: [verification/eth-mainnet-prime.md](verification/eth-mainnet-prime.md)

- Centrifuge deSPXA
  - Chain: Base
  - `chain_id`: `8453`
  - Address: `0x9c5C365e764829876243d0b289733B9D2b729685`
  - Symbol: `deSPXA`
  - Issuer hint: Centrifuge
  - Analyst report: [reports/base-despxa.md](reports/base-despxa.md)
  - Technical report: [technical-reports/base-despxa.md](technical-reports/base-despxa.md)
  - Verification: [verification/base-despxa.md](verification/base-despxa.md)

- Saturn USDat
  - Chain: Ethereum mainnet
  - `chain_id`: `1`
  - Address: `0x23238F20B894f29041f48d88Ee91131c395aAA71`
  - Symbol: `USDat`
  - Issuer hint: Saturn
  - Analyst report: [reports/eth-mainnet-usdat.md](reports/eth-mainnet-usdat.md)
  - Technical report: [technical-reports/eth-mainnet-usdat.md](technical-reports/eth-mainnet-usdat.md)
  - Verification: [verification/eth-mainnet-usdat.md](verification/eth-mainnet-usdat.md)

- apyx apxUSD
  - Chain: Ethereum mainnet
  - `chain_id`: `1`
  - Address: `0x98A878b1Cd98131B271883B390f68D2c90674665`
  - Symbol: `apxUSD`
  - Issuer hint: apyx
  - Analyst report: [reports/eth-mainnet-apxusd.md](reports/eth-mainnet-apxusd.md)
  - Technical report: [technical-reports/eth-mainnet-apxusd.md](technical-reports/eth-mainnet-apxusd.md)
  - Verification: [verification/eth-mainnet-apxusd.md](verification/eth-mainnet-apxusd.md)

## Cross-asset analyst takeaway

The shared pattern across the six-asset battery is that none of these assets should be treated as an ordinary unrestricted liquid ERC-20 without additional checks.

Recurring risk layers:

- issuer, protocol, fund, reserve, or backing evidence outside the token contract;
- NAV, reserve, attestation, dashboard, or feed data that requires freshness and reconciliation checks;
- redemption paths that may depend on queues, receipts, Authorized Participants, whitelists, primary-redemption eligibility, or issuer interfaces;
- freeze, blacklist, whitelist, deny-list, member-state, pause, upgrade, or forced-transfer controls;
- Safe, timelock, AccessManager, Root, ProxyAdmin, or EOA-controlled administration that can change holder-relevant behavior;
- oracle/accounting values that may diverge from executable market exit value;
- DEX liquidity that is point-in-time, venue-dependent, and size-dependent.

The reports are suitable as factual inputs for analyst review. They are not sufficient for automated live use unless holder eligibility, restriction state, queue/receipt/redemption state, route quotes, admin drift, oracle freshness, and current backing evidence are refreshed.

## Per-asset highest-impact unknowns and analyst implications

### Saturn sUSDat

Mechanism in brief: sUSDat is a Saturn yield-bearing share token over USDat, with yield and NAV exposure linked to STRC / digital-credit collateral and a withdrawal queue rather than simple immediate withdrawal.

Highest-impact unknowns:

- STRC custody, valuation, reserve proof, and NAV-feed details were not independently verified beyond Saturn materials. `missing_behavior`: `review_required`.
- Audit and formal-verification reports were not mapped end-to-end to the current sUSDat, queue, USDat, and STRC-oracle deployments. `missing_behavior`: `review_required`.
- Admin control was in transition in the snapshot: EOA default-admin revocations were pending, not proven executed. `missing_behavior`: `review_required`.
- USDat underlying eligibility, whitelist, freeze, and legal policy were not fully mapped. `missing_behavior`: `review_required`; live assumptions about unrestricted entry/exit are `block_automation`.
- Queue readiness and executable exit slippage were not measured for a real position. `missing_behavior`: `block_automation` until live queue state, holder eligibility, and route quote are checked.
- Docs/on-chain vesting-period mismatch remains unresolved. `missing_behavior`: `review_required`.

Analyst-facing implication: treat vault exchange-rate growth as only one layer. Backing proof, queue claimability, USDat restrictions, admin state, and route depth are all required before concluding what a holder can realize.

### apyx apyUSD

Mechanism in brief: apyUSD is an Apyx savings-vault share over apxUSD. Exits create an Unlock Receipt NFT before final apxUSD claim, and apxUSD itself depends on off-chain preferred-share backing and primary redemption eligibility.

Highest-impact unknowns:

- Full reserve, custody, attestation contents, and current collateral composition were not parsed and reconciled to on-chain supply. `missing_behavior`: `cannot_rank_cleanly` and `review_required`.
- Audit and formal-verification PDFs were not mapped to the live implementation, AccessManager, receipt, vesting, and apxUSD contracts. `missing_behavior`: `review_required`.
- AccessManager admin-operation history and role-0 operating identity were not fully verified. `missing_behavior`: `review_required`.
- Safe-compatible holder modules, guard, fallback handler, and all pending Safe transactions were not decoded. `missing_behavior`: `review_required`; production action packages remain `block_automation` without refresh.
- Deny-list administration and current denied-address state were not fully expanded. `missing_behavior`: `review_required`.
- Unlock Receipt implementation details and full role mapping were not fully expanded. `missing_behavior`: `review_required`; real exits are `block_automation` without fresh receipt checks.
- apxUSD primary mint/redeem SLA, whitelist process, and eligible-participant access remain user-specific. `missing_behavior`: `review_required`; live redemption is `block_automation` without eligibility proof.

Analyst-facing implication: vault accounting is not executable USD value. A live exit depends on receipt terms, deny-list and pause state, apxUSD route/primary redemption, reserve evidence, and Safe/AccessManager state.

### Hastra PRIME

Mechanism in brief: PRIME is a Hastra vault-share token whose direct redemption asset is wYLDS, with economics linked by Hastra terms to YLDS backing and Figure Democratized Prime HELOC lending operations.

Highest-impact unknowns:

- Exact off-chain NAV / redemption-rate construction for the active feed ID was not found. `missing_behavior`: `review_required`; execution depending on feed construction/freshness is `block_automation`.
- Current reserve, custody, and attestation report bodies for wYLDS / YLDS backing were not located. `missing_behavior`: `cannot_rank_cleanly` and `review_required`.
- Public audit scope for the deployed PRIME and FeedVerifier system was not located. `missing_behavior`: `review_required`.
- User-specific eligibility, KYC, redemption process, and SLA were not fully specified. `missing_behavior`: `review_required`; real exits are `block_automation` without live eligibility and settlement confirmation.
- Exact operational identity and off-chain control process for Safe owners and EOA role holders were not established. `missing_behavior`: `review_required`.
- Large-size route behavior can cliff near visible pool inventory. `missing_behavior`: `block_automation` until a live route quote is checked.

Analyst-facing implication: separate three values before drawing conclusions: issuer/NAV value, on-chain conversion value, and executable market exit value.

### Centrifuge deSPXA

Mechanism in brief: deSPXA is a Base token distributed through Centrifuge and described as the DeFi-distribution / freely transferable form of SPXA exposure linked to Janus Henderson Anemoy S&P 500 Index Fund exposure.

Highest-impact unknowns:

- Active Root ward contracts were not mapped to named governance, owners, Safe thresholds, or operating policy. `missing_behavior`: `review_required`.
- Holder-specific member / Authorized Participant / KYC eligibility and frozen/member state were not established. `missing_behavior`: `review_required`; primary redemption or automated request execution is `block_automation`.
- Primary legal/fund terms, custody/service providers, holdings/replication method, cash buffers, audited financial statements, and NAV reports were not fully retrieved. `missing_behavior`: `review_required` and `cannot_rank_cleanly`.
- Audit/formal-verification coverage for the exact Base deployment was not matched to public reports. `missing_behavior`: `review_required`.
- Chronicle feed address, update cadence, staleness policy, reporter authority, and failure handling were not fully expanded. `missing_behavior`: `review_required`; oracle-dependent execution is `block_automation`.
- Live executable exit depth and size-dependent slippage were not measured. `missing_behavior`: `block_automation` until a live route quote and recipient/account status are checked.

Analyst-facing implication: deSPXA should be reviewed as controlled tokenized-fund exposure. Secondary transferability does not prove primary NAV redemption access or clean fund-level backing evidence.

### Saturn USDat

Mechanism in brief: USDat is Saturn's permissioned stablecoin on Ethereum mainnet, described by Saturn as backed at launch by M0 `$M`, with issuer onboarding, whitelist, freeze, forced-transfer, pause, and upgrade controls.

Highest-impact unknowns:

- Independent M0 `$M` reserve, custody, legal, and redemption details were not expanded beyond Saturn's own overview. `missing_behavior`: `review_required`.
- Saturn onboarding / legal eligibility, per-holder whitelist state, freeze state, and redemption access were not tested. `missing_behavior`: `review_required`; state-changing live use without eligibility and restriction refresh is `block_automation`.
- Audit and formal-verification report scopes were not mapped to the current implementation, ProxyAdmin owner, timelock state, inherited components, and role holders. `missing_behavior`: `review_required`.
- Admin execution speed was in transition: pending timelock migration evidence was not proof of execution, and the ProxyAdmin-owner EOA path remained immediate in the snapshot. `missing_behavior`: `review_required`.
- Token-native oracle methodology was not found. Issuer peg, reserve evidence, and DEX market price can diverge from practical exit value. `missing_behavior`: `review_required`; live exits without a route quote are `block_automation`.
- No comprehensive incident assurance was completed. `missing_behavior`: `continue` for descriptive use and `review_required` for production acceptance.

Analyst-facing implication: a near-$1 market price does not prove unrestricted transfer, redemption, or collateral value. Eligibility, controls, backing proof, admin state, and executable liquidity all need refresh.

### apyx apxUSD

Mechanism in brief: apxUSD is Apyx's base synthetic-dollar token, described as backed by preferred-share collateral and redeemable for USDC by eligible whitelisted participants, while general users use external liquidity pools.

Highest-impact unknowns:

- Current collateral dashboard values, attestation PDFs, custodian details, preferred-share issuer concentration, and reserve composition were not reconciled to on-chain supply. `missing_behavior`: `cannot_rank_cleanly` and `review_required`.
- Primary mint/redeem legal eligibility, whitelist process, permitted jurisdictions, and live redemption SLA were not verified beyond official docs. `missing_behavior`: `review_required`; real redemption is `block_automation`.
- Audit/formal-verification PDFs were not mapped to the live apxUSD implementation, AccessManager roles, MinterV0, deny-list, and pending Safe state. `missing_behavior`: `review_required`.
- Full AccessManager admin history and pending Safe payloads were not exhaustively decoded. `missing_behavior`: `review_required`; production action packages are `block_automation`.
- Safe modules, guards, fallback handlers, human/entity identities, and operating policies were not verified. `missing_behavior`: `review_required`.
- Deny-list administration and current denied-address state were not fully expanded. `missing_behavior`: `review_required`; user-specific actions are `block_automation`.
- No token-native oracle / staleness methodology was found, and saved market data showed venue-level price divergence. `missing_behavior`: `review_required`; live exits require a route quote.

Analyst-facing implication: apxUSD can look stablecoin-like in interfaces, but practical exit value depends on preferred-share backing evidence, primary-redemption eligibility, deny-list/pause state, AccessManager/Safe state, and current market route depth.

## Cross-asset source quality notes

High-confidence source classes across the battery:

- direct on-chain RPC reads and explorer/source snapshots for token identity, roles, implementation/proxy state, pause/restriction state, and selected liquidity or route samples;
- verified source or local source extracts for token, vault, queue, receipt, AccessManager, Root, FeedVerifier, and related mechanics where available;
- local verification artifacts that independently checked scope, section coverage, source maps, missing_behavior labels, and no-recommendation constraints.

Medium-confidence source classes across the battery:

- issuer/protocol documentation describing mechanism, backing model, redemption access, legal or eligibility framing, dashboards, and audits;
- DEXScreener / CoinGecko / venue snapshots used as point-in-time liquidity and price context;
- Safe Transaction Service or governance-feed snapshots where payloads were not fully decoded.

Lower-confidence or incomplete source classes across the battery:

- reserve, custody, attestation, fund, and legal documents that were identified but not fully retrieved or reconciled;
- audit/formal-verification reports whose existence was found but not mapped to exact deployed contracts and current admin state;
- comprehensive incident-history searches, because bounded no-incident findings are not proof of no incident;
- holder-specific eligibility, KYC, whitelist/member/deny-list/freeze status, and redemption SLA;
- live executable route quotes for concrete sizes.

Analyst implication: use the reports to decide what must be checked, not as a substitute for current-state proof. The strongest facts are identity/control snapshots and source-linked mechanics. The weakest facts are live holder eligibility, live route execution, reserve reconciliation, and off-chain legal/custody terms.

## Cross-asset checks before live use

For any of the six assets, refresh these before using the report in a live position, collateral admission, liquidation path, or execution package:

- current backing / reserve / custody / attestation / fund evidence;
- current audit or formal-verification scope mapped to the deployed contracts;
- current issuer, legal, jurisdiction, eligibility, KYC, whitelist, member, Authorized Participant, or primary-redemption requirements;
- current freeze, blacklist, whitelist, deny-list, member, pause, forced-transfer, queue, receipt, or claim state for the relevant holder and recipient;
- current admin holders, Safe thresholds, modules, guards, fallback handlers, AccessManager/Root/ProxyAdmin/timelock state, pending transactions, and recent sensitive changes;
- current oracle / NAV feed value, update time, staleness rules, bounds, failure behavior, and off-chain construction method;
- current route quote and size-specific slippage for the exact transaction path;
- any new incident, depeg, pause, freeze, reserve discrepancy, oracle failure, redemption delay, governance emergency, or legal disclosure;
- Gearbox-specific oracle and support configuration if an asset is evaluated for Credit Account collateral.

## Scope guard

This index introduces no additional scoped assets. Underlying tokens, queues, receipts, vaults, oracles, funds, backing instruments, managers, and admin contracts are mentioned only to explain the six supplied assets and their analyst-facing risk implications.
