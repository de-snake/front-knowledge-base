# apyx apyUSD — investment analyst risk note

Report date: 2026-06-04 UTC
Audience: investment analyst
Asset: apyx apyUSD on Ethereum mainnet
Token address: `0x38EEb52F0771140d10c4E9A9a72349A329Fe8a6A`
Symbol: `apyUSD`

This note is an analyst-readable rewrite of the technical dossier. It is source-linked context for risk review. It is not an asset-selection recommendation. It is not an investment recommendation, suitability verdict, position-size recommendation, or execution instruction.

Detailed contract evidence was preserved separately in `run/tokens/eth-mainnet-apyusd/technical-report.md`.

## 1. Executive view

apyUSD is a yield-bearing vault share issued by Apyx. Holders deposit apxUSD and receive apyUSD. The balance does not rebase; instead, the exchange rate between apyUSD and apxUSD is intended to rise as yield is added to the vault [S4][S5].

The main investment issue is that apyUSD combines three types of risk:

- a vault-share risk: apyUSD is only as good as the apxUSD vault accounting and exit mechanics [S1][S4];
- an issuer / reserve risk: apxUSD depends on off-chain preferred-share exposure, custody, dashboards, and attestations [S6][S9][S10];
- a market-exit risk: the saved market quotes showed discounts versus the vault accounting rate, including a second-leg apxUSD-to-USDC discount [S1][S14][S15].

Primary risk implication: the vault exchange rate is not the same as executable USD exit value. Before a live decision, an analyst must check reserve evidence, receipt mechanics, deny-list / pause state, governance queue, and current market route depth.

## 2. What the token represents

apyUSD represents a share of an Apyx vault whose immediate asset is apxUSD [S1][S5]. Apyx materials describe apxUSD as backed by a preferred-share collateral stack, with reserve transparency and attestations referenced through Accountable and Wolf & Company materials [S6][S9][S10].

A holder who exits apyUSD does not simply receive final cash in one step. The current source path burns apyUSD, applies a vault-side fee, escrows net apxUSD, and mints an Unlock Receipt NFT that can later claim apxUSD [S4][S8]. That receipt period creates a transition-stage asset: the holder has a claim in process, not final settlement.

For investment analysis, apyUSD should be viewed as a savings-token wrapper over apxUSD, not as an ordinary USD stablecoin.

## 3. Main risk implications

### Backing risk

The immediate vault asset is apxUSD, but the final economic risk depends on how apxUSD is backed. Apyx docs describe the backing as low-volatility, variable-rate preferred shares issued by Digital Asset Treasuries, and state that redemption scenarios liquidate preferred shares to USDC [S6].

The research found links to reserve / collateral visibility and monthly attestation materials, but did not parse and reconcile the full reserve PDFs to current on-chain supply [S9][S10].

Risk implication: the existence of dashboards and attestation links is useful evidence, but not enough to conclude that current reserve composition, custody, valuation, and supply reconciliation are independently verified for this dossier. This blocks clean ranking and requires human review for collateral valuation.

### Redemption risk

The exit path is not a simple instant stablecoin withdrawal. Current source behavior indicates that apyUSD exits create an Unlock Receipt NFT before the holder can claim apxUSD [S4][S8]. The receipt fee curve had a maximum fee of 3.4%, a minimum duration of 3 days, and a maximum duration of 20 days in the snapshot; the vault-side unlocking fee was 0.1% [S1][S8].

Risk implication: even when vault accounting is correct, the holder may face time, fee, receipt-state, and claimability risk. A live exit requires fresh receipt, fee, pause, deny-list, and apxUSD transfer checks.

### Market-exit risk

The main saved apyUSD market route was apyUSD to apxUSD, then apxUSD to USDC. The parent snapshot showed the apyUSD/apxUSD Curve route below the vault accounting rate, and the apxUSD/USDC second leg below $1 [S1][S14][S15].

Examples from the snapshot:

- the main Curve apyUSD/apxUSD venue reported $13.23M liquidity and $25.09M 24h volume [S14][S15];
- direct quotes showed 1 apyUSD to 1.321608 apxUSD, while vault accounting was near 1.374366 apxUSD per apyUSD [S1];
- the apxUSD/USDC second leg quoted 1 apxUSD to 0.903873 USDC in the same parent snapshot [S1].

Risk implication: market exit value can materially diverge from vault accounting. Any execution or liquidation analysis must use fresh route quotes for the exact size.

### Control and governance risk

apyUSD is upgradeable and controlled through an AccessManager setup. Operational powers include pause, deny-list replacement, receipt rotation, fee changes, vesting changes, implementation upgrades, and access-role changes [S1][S4][S16].

The parent snapshot identified a Safe-compatible operational holder with a 3-of-6 threshold for roles 21–25, but also found a high-authority role-0 EOA. The Safe Transaction Service returned 103 unexecuted transactions that were not fully decoded [S1][S16].

Risk implication: sensitive changes can be pending or pre-staged. A production action should be blocked until the Safe queue, AccessManager history, and current authority mapping are refreshed.

### Legal and eligibility risk

Apyx documentation says apyUSD vault access is permissionless and does not require KYB/KYC, while the Terms restrict use by certain territories and persons. apxUSD primary mint / redemption docs also refer to eligible whitelisted participants [S5][S6][S13].

Risk implication: a generic token transfer may be possible, but user-specific legal eligibility and primary-settlement access cannot be assumed. Live user flows require jurisdiction and process checks.

## 4. Backing and NAV quality

Plain-language model:

- apyUSD is a vault share over apxUSD [S1][S5].
- The vault exchange rate is based on total assets divided by supply, denominated in apxUSD [S1][S4].
- apxUSD backing depends on the preferred-share / collateral stack described by Apyx [S6].
- Reserve dashboards and attestation links exist, but the source pass did not fully parse and reconcile the reserve reports to live supply [S9][S10].

Analyst conclusion: vault mechanics are clear, but backing assurance is incomplete. Use the report for understanding the asset, not for clean reserve acceptance without additional attestation review.

## 5. Liquidity and exit risk

There are three practical exit considerations.

First, primary exit produces an Unlock Receipt NFT before final apxUSD claim [S4][S8]. This means the holder may have a pending claim rather than immediate liquid value.

Second, apxUSD itself must be liquid or redeemable into the desired final asset. The parent snapshot showed apxUSD-to-USDC trading below $1 in the sampled route [S1].

Third, DEX liquidity can be price-sensitive. Even the large apyUSD/apxUSD Curve pool showed a discount to vault accounting at the sampled time [S1][S14][S15].

Action implication: for any position-specific exit, require a fresh route quote across both legs, a receipt-state check, and current pause / deny-list status. The saved snapshot is evidence of risk, not an executable quote.

## 6. Controls, governance, and legal restrictions

The controls most relevant to existing holders are:

- pause of apyUSD flows [S1][S4];
- deny-list checks affecting transfers, deposits, redemptions, and claims [S1][S4];
- Unlock Receipt rotation and receipt pause / claim behavior [S4][S8];
- fees and vesting changes [S1][S4];
- implementation upgrade authority [S1][S4];
- AccessManager reconfiguration by high-authority roles [S1][S16].

Risk implication: the asset has a meaningful administrative surface. Current governance state should be refreshed before any investment or collateral process that depends on predictable transferability, redemption, or pricing.

## 7. Pricing / oracle risk in plain language

apyUSD does not rely on a dedicated external USD price feed in the reviewed source. Its conversion value is based on internal vault accounting in apxUSD [S4].

That creates a blind spot: the accounting rate can be higher than what the market will pay, especially if apxUSD trades below $1 or if the receipt/claim path is impaired [S1][S14][S15].

Risk implication: do not use the vault exchange rate alone as liquidation value, portfolio value, or exit value. A live analysis should compare vault accounting, apxUSD market price, final USDC route, and receipt/eligibility state.

## 8. What must be checked before live use

Before using this dossier for a live position, collateral decision, liquidation path, or execution package, refresh:

- current apyUSD implementation and authority address;
- current pause state for apyUSD, Unlock Receipt, and apxUSD;
- deny-list contract, denied-address state, and holder/recipient status;
- receipt address, fee curve, claimability, and receipt admin roles;
- current vault-side unlocking fee and vesting state;
- AccessManager role-0 holder and role mappings;
- Safe owners, threshold, modules, guard, and pending transactions;
- reserve / custody / attestation PDFs and reconciliation to live supply;
- apxUSD primary mint/redeem SLA and eligible-participant process;
- live apyUSD/apxUSD and apxUSD/USDC route quotes;
- any updated audits, incidents, pauses, denials, depegs, or redemption delays;
- Gearbox-specific oracle/support state if this is being evaluated for Credit Account collateral.

Practical implication: unresolved reserve, governance, and eligibility questions require human review. Unresolved route, pause, deny-list, receipt, and pending-governance state should block automated execution.

Methodology labels: backing, audit-scope, Safe/module, market-stress, and eligibility unknowns remain `review_required`; unresolved route, pause, deny-list, receipt, and pending-governance state is `block_automation` for execution.

## 9. Evidence quality

High-confidence evidence:

- exact token identity, underlying asset, proxy status, implementation, authority, receipt, vesting, and role snapshots from on-chain reads [S1][S2][S3][S4];
- verified source behavior for pause, deny-list, receipt, fee, and vault accounting [S4];
- point-in-time Curve / DEX route evidence [S1][S14][S15].

Medium-confidence evidence:

- Apyx documentation on apyUSD / apxUSD mechanism and addresses [S5][S6][S7][S8];
- Apyx transparency and attestation pages [S9][S10];
- listed audit reports and Certora summary [S11][S12].

Lower-confidence or incomplete evidence:

- full reserve / custody reconciliation;
- exact deployed-scope audit mapping;
- all pending Safe transaction payloads;
- long market-stress history;
- user-specific jurisdiction / eligibility state;
- Gearbox-specific oracle configuration.

## 10. Source map

Each source ID below now includes the actual URL or local evidence path. Local paths are relative to this report folder unless shown as full project paths.

- **S1** — [ethereum-rpc.publicnode.com](https://ethereum-rpc.publicnode.com) plus local raw snapshots [run/tokens/eth-mainnet-apyusd/research/raw/onchain-admin-snapshot-2026-06-04.json](run/tokens/eth-mainnet-apyusd/research/raw/onchain-admin-snapshot-2026-06-04.json) and [run/tokens/eth-mainnet-apyusd/research/raw/onchain-market-snapshot-2026-06-04.json](run/tokens/eth-mainnet-apyusd/research/raw/onchain-market-snapshot-2026-06-04.json). Source class: onchain. Accessed: 2026-06-04. Confidence: high. Token metadata, proxy slots, implementation, AccessManager, roles/delays, Safe-like reads, pause/deny-list/receipt/vesting/fee values, ERC-4626 totals, Curve quotes.
- **S2** — Etherscan token / contract page, [etherscan.io/address/0x38EEb52F0771140d10c4E9A9a72349A329Fe8a6A](https://etherscan.io/address/0x38EEb52F0771140d10c4E9A9a72349A329Fe8a6A). Source class: onchain. Accessed: 2026-06-04. Confidence: high. Verified proxy/source, token page, implementation corroboration.
- **S3** — Dedaub contract explorer, [app.dedaub.com/ethereum/address/0x38eeb52f0771140d10c4e9a9a72349a329fe8a6a](https://app.dedaub.com/ethereum/address/0x38eeb52f0771140d10c4e9a9a72349a329fe8a6a). Source class: onchain. Accessed: 2026-06-04. Confidence: medium. Secondary proxy / ERC-20 metadata corroboration.
- **S4** — Apyx EVM contracts repository, [github.com/apyx-labs/evm-contracts](https://github.com/apyx-labs/evm-contracts). Source class: issuer_docs / onchain. Accessed: 2026-06-04. Confidence: medium. `ApyUSD.sol`, deny-list extension, receipt interfaces, fee curve, APY view source behavior.
- **S5** — Apyx docs, `apyUSD` overview, [docs.apyx.fi/product-overview/apyusd-overview](https://docs.apyx.fi/product-overview/apyusd-overview). Source class: issuer_docs. Accessed: 2026-06-04. Confidence: medium. Savings-token mechanism, ERC-4626 vault, non-rebasing exchange-rate accrual, permissionless access, flexible redemption.
- **S6** — Apyx docs, `apxUSD` overview, [docs.apyx.fi/product-overview/apxusd-overview](https://docs.apyx.fi/product-overview/apxusd-overview). Source class: issuer_docs. Accessed: 2026-06-04. Confidence: medium. Underlying `apxUSD`, preferred-share backing description, mint/redeem eligibility context.
- **S7** — Apyx docs, Smart Contract Addresses, [docs.apyx.fi/resources/smart-contract-addresses](https://docs.apyx.fi/resources/smart-contract-addresses). Source class: issuer_docs. Accessed: 2026-06-04. Confidence: high for listed addresses, medium for dynamic state. Official listed token / view addresses.
- **S8** — Apyx docs, Unlocking `apyUSD` for `apxUSD`, [docs.apyx.fi/technical-overview/unlocking](https://docs.apyx.fi/technical-overview/unlocking). Source class: issuer_docs. Accessed: 2026-06-04. Confidence: medium. Unlock Receipt / cooldown / fee path; caveat that page mixes current receipt wording with legacy unlock-token wording.
- **S9** — Apyx docs, Transparency, [docs.apyx.fi/collateral-and-custody/transparency](https://docs.apyx.fi/collateral-and-custody/transparency). Source class: issuer_docs. Accessed: 2026-06-04. Confidence: medium. Accountable, Apyx dashboard, Dune dashboard, custodian attestation process.
- **S10** — Apyx docs, Third Party Attestation, [docs.apyx.fi/collateral-and-custody/third-party-attestation](https://docs.apyx.fi/collateral-and-custody/third-party-attestation). Source class: issuer_docs. Accessed: 2026-06-04. Confidence: medium for listed PDFs, low for reserve conclusions. Wolf & Company March / April 2026 attestation links.
- **S11** — Apyx docs, Audits, [docs.apyx.fi/resources/audits](https://docs.apyx.fi/resources/audits). Source class: audit. Accessed: 2026-06-04. Confidence: medium for listed reports, low for unresolved finding status. Listed Quantstamp, Certora, and Zellic reports.
- **S12** — Certora public report summary, [www.certora.com/reports/apyx-apxusd](https://www.certora.com/reports/apyx-apxusd). Source class: audit. Accessed: 2026-06-04. Confidence: medium. Certora March 2026 summary, issue count, high-severity fixed/confirmed statement.
- **S13** — Apyx Terms of Service, [docs.apyx.fi/resources/terms-of-service](https://docs.apyx.fi/resources/terms-of-service). Source class: legal_terms. Accessed: 2026-06-04. Confidence: high for published terms, medium for practical enforcement. Restricted-territory / restricted-person framing and APYX Protocol legal entity references.
- **S14** — DEXScreener API and pair page, [api.dexscreener.com/latest/dex/tokens/0x38EEb52F0771140d10c4E9A9a72349A329Fe8a6A](https://api.dexscreener.com/latest/dex/tokens/0x38EEb52F0771140d10c4E9A9a72349A329Fe8a6A), [dexscreener.com/ethereum/0xe41be7b340f7c2eda4da1e99b42ee1b228b526b7](https://dexscreener.com/ethereum/0xe41be7b340f7c2eda4da1e99b42ee1b228b526b7). Source class: market_data. Accessed: 2026-06-04. Confidence: high for current reported pair data, medium for API-derived market statistics. Secondary venues, liquidity, volume, pair price.
- **S15** — CoinGecko `apyUSD`, [www.coingecko.com/en/coins/apyusd](https://www.coingecko.com/en/coins/apyusd) and public API `/api/v3/coins/apyusd`. Source class: market_data. Accessed: 2026-06-04. Confidence: medium. Market price, market cap, volume, broader venue context.
- **S16** — Safe Transaction Service and direct on-chain Safe-like reads for `0xf9862EfC1704aC05e687f66E5cD8c130E5663CE2`, [safe-transaction-mainnet.safe.global/api/v1/safes/0xf9862EfC1704aC05e687f66E5cD8c130E5663cE2…](https://safe-transaction-mainnet.safe.global/api/v1/safes/0xf9862EfC1704aC05e687f66E5cD8c130E5663cE2/multisig-transactions/?executed=false&limit=5). Source class: governance. Accessed: 2026-06-04. Confidence: high for threshold / owners / pending-count reads, medium for pending impact. Safe-like role holder, 3-of-6 threshold, pending unexecuted transaction caveat.
- **S17** — Project methodology, [run/methodology.md](run/methodology.md). Source class: unknown. Accessed: 2026-06-04. Confidence: high. Source-priority rules, asset-section requirements, `missing_behavior` labels.

## 11. Technical appendix pointer

For raw addresses, role identifiers, implementation slots, method names, and table-level evidence, see:

- `run/tokens/eth-mainnet-apyusd/technical-report.md`
- `run/tokens/eth-mainnet-apyusd/research/`
