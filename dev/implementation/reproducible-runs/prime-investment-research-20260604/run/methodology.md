# MVP asset-specific mining pipeline

## Purpose

This file defines the asset-specific research pipeline for MVP token dossiers.

The goal is to prepare enough objective, source-linked token context for the agent to reason about a selected asset without starting from only a token address.

Token selection is out of scope for this file. Each run starts from a supplied `chain_id`, `token_address`, `symbol`, and optional intended use.

The output is not an investment recommendation. It is a factual substrate for later agent reasoning against user mandate, position size, horizon, Gearbox state, and Preview results.

## Report inputs

```text
chain_id:
token_address:
symbol:
intended_use: pool_underlying | Credit Account collateral | reward_token | transition-stage asset | unknown
position_context: optional pool / Credit Manager / route / size / horizon
report_date:
analyst:
```

## Source priority

Use sources in this order:

1. Verified contract source, proxy implementation, and on-chain role state.
2. Official issuer / protocol docs, terms, risk disclosures, reserve pages, whitepapers, and status pages.
3. Official audit reports, formal verification reports, bug-bounty scope, and incident postmortems.
4. Governance docs, timelock records, Safe owners / thresholds, role registries, and admin-operation history.
5. Independent risk assessments from credible teams, used only as secondary interpretation.
6. Market data providers for liquidity, historical prices, volatility, and depth.
7. News or social sources only for incident discovery; confirm with primary sources before treating them as report facts.

Every material fact should carry a source URL, access date, source class, and confidence level.

## Asset-specific pipeline

### 1. Identity and token semantics

Record:

- canonical chain and token address;
- symbol, name, decimals, and token standard;
- verified implementation and proxy status;
- asset type: native wrapper, stablecoin, LST, LRT, LP token, synthetic, tokenized security, issuer-controlled asset, reward token, governance token, or other;
- token behavior: ordinary ERC-20, rebasing, non-rebasing share token, vault share, wrapper, claim token, receipt token, or other;
- whether the asset can become or represent a transition-stage asset.

Why it matters: the agent must not treat wrappers, vault shares, rebasing tokens, receipt tokens, and ordinary ERC-20 tokens as equivalent.

### 2. Issuer / protocol and business model

Record:

- issuer, protocol, DAO, or governing entity;
- one-paragraph mechanism description;
- official docs, terms, and risk-disclosure links;
- revenue or yield source if the token accrues value;
- whether the token depends on off-chain entities, custodians, validators, market makers, or exchanges;
- who can mint, redeem, pause, blacklist, freeze, rescue tokens, change parameters, or change backing composition;
- whether direct redemption is available to ordinary holders or only to eligible / whitelisted participants.

Why it matters: the agent needs to know who controls the asset, what the token represents, and which off-chain or governance assumptions are embedded in it.

### 3. Backing, NAV, and exposure map

Classify the NAV model:

```text
nav_model: none | 1:1 reserve | collateralized vault | delta-neutral synthetic | staking-share | LP basket | custodied-wrapper | issuer NAV | unknown
```

Record:

- reserve assets, underlying assets, collateral assets, or basket components;
- custody model and custodian names where applicable;
- reserve reports, proof-of-reserves, attestations, accounting reports, or NAV reports;
- update cadence for reserve / NAV data;
- primary redemption mechanism and access restrictions;
- known haircut, discount, slashing, funding-rate, basis, impermanent-loss, or collateral-quality exposure;
- whether NAV can diverge from secondary-market price;
- whether the asset's value depends on another token's oracle, exchange rate, or redemption queue.

Why it matters: the token can appear healthy by address and price while its actual exit value or backing quality is impaired.

### 4. Contract admin, multisigs, and sensitive actions

Inspect verified contracts and on-chain role holders.

Record:

- immutable contract or proxy / upgradeable pattern;
- owner, proxy admin, default admin, pauser, blacklister, minter, burner, upgrader, oracle reporter, fee setter, cooldown setter, registry setter, rescue role, and other sensitive roles;
- role holder addresses;
- holder type: EOA, Safe, timelock, DAO agent, contract, or unknown;
- Safe owner count and threshold where available;
- timelock duration where available;
- recent sensitive role changes or admin transactions;
- whether sensitive actions affect only future issuance / configuration or existing holders.

Classify each sensitive action:

```text
existing_holder_impact: none | indirect | direct_freeze | direct_transfer | direct_dilution | direct_redemption_block | unknown
execution_speed: immediate | timelocked | governance_vote | unknown
```

Why it matters: the agent must distinguish market risk from administrative intervention risk.

### 5. Audits, formal verification, and incidents

Record:

- audit firms, report dates, and report URLs;
- audited scope versus currently deployed contracts;
- unresolved critical / high issues if any;
- bug-bounty program and scope;
- formal verification claims and verified invariants if any;
- incident history: exploit, depeg, blacklist / freeze event, pause, oracle failure, slashing event, bridge incident, redemption delay, or governance emergency;
- whether each incident affected the exact token, a related token, or only the broader protocol.

Why it matters: “audited” is not a verdict. Scope, recency, unresolved findings, and incident response are the useful facts.

### 6. Transferability, redemption, and liquidity

Record:

- transfer restrictions and eligibility / KYC requirements;
- freeze, blacklist, forced-transfer, or registry mechanics;
- primary redemption path;
- cooldown, withdrawal queue, settlement window, or claim process;
- whether redemption creates a claim token / NFT / receipt;
- claim readiness semantics where applicable;
- secondary-market liquidity venues;
- current depth and size-dependent exit caveats;
- historical depeg, premium, discount, or liquidity stress;
- eligible-liquidator depth for compliance-gated or issuer-controlled assets.

Why it matters: the same nominal token value can imply very different exit risk depending on holder eligibility, queue state, and market depth.

### 7. Oracle and pricing methodology

Record:

- primary price source: market oracle, Chainlink-style feed, exchange rate, NAV, hardcoded value, fundamental value, composite oracle, or unknown;
- update cadence and staleness window;
- dependencies in a composite oracle;
- whether the oracle follows market price, NAV, exchange rate, or a fixed / fundamental value;
- whether the oracle can miss market depeg, issuer freeze, redemption delay, liquidity break, or NAV impairment;
- observed divergence between oracle value and external market value where available;
- Gearbox-specific main / reserve oracle notes if the asset is already supported.

Why it matters: Health Factor and apparent asset value can be misleading when oracle methodology does not reflect the practical exit path.

### 8. Governance / change-feed watchlist

Record current and pending changes affecting:

- asset support status;
- issuer or protocol governance proposals;
- reserve / backing composition;
- admin roles;
- oracle configuration;
- withdrawal, cooldown, or redemption terms;
- mint / redemption eligibility;
- fees;
- bridge, custody, validator, or exchange providers;
- Gearbox-specific parameters if the token is already used by a pool or Credit Manager.

Why it matters: the agent should compare the current state to the last accepted state and catch material drift.

### 9. Data quality and missing-data behavior

For every material field, record:

```text
source_class: onchain | issuer_docs | legal_terms | audit | governance | market_data | risk_assessment | news | unknown
freshness: current | stale | dated | unknown
confidence: high | medium | low
missing_behavior: continue | cannot_rank_cleanly | review_required | block_automation
```

Default handling:

- Missing field used only for explanation: mark unknown and continue.
- Missing field used for ranking: do not rank the asset as cleanly acceptable.
- Missing admin-role owner for a mutable asset: review-required.
- Missing issuer / eligibility / freeze / redemption state for issuer-controlled or compliance-gated assets: review-required or blocking.
- Missing oracle methodology for Credit Account collateral: review-required.
- Missing liquidity / exit path for a state-changing action: block automation until Preview or a route quote resolves it.
- Missing execution-package integrity binding: block Execute.

Why it matters: unknowns must change agent behavior instead of disappearing from the reasoning trace.

## Minimal report output

Each asset report should contain:

- agent-context summary;
- one-paragraph mechanism;
- filled sections for the nine pipeline steps above;
- highest-impact unknowns with missing-data behavior;
- source list with URLs, source class, accessed date, and confidence.

## Acceptance criteria

A report is usable for MVP reasoning only if:

1. The token was supplied by user or backend scope.
2. Identity facts are pinned to chain and address.
3. At least two primary sources are cited when available.
4. Admin roles and sensitive actions are checked or explicitly marked unknown.
5. NAV / backing / reserve exposure is classified, including `none` where not applicable.
6. Transfer, freeze, redemption, and liquidity paths are checked or explicitly marked unknown.
7. Oracle methodology is checked or explicitly marked unknown.
8. Missing material fields state whether they allow continued explanation, prevent clean ranking, require human review, or block automation.
9. The report avoids recommendation language and leaves final suitability to the agent plus user mandate.
