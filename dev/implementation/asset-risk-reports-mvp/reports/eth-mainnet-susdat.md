# Saturn sUSDat — investment analyst risk note

Report date: 2026-06-04 UTC
Audience: investment analyst
Asset: Saturn sUSDat on Ethereum mainnet
Token address: `0xD166337499E176bbC38a1FBd113Ab144e5bd2Df7`
Symbol: `sUSDat`

This note is an analyst-readable rewrite of the technical dossier. It is source-linked context for risk review, not an asset-selection recommendation, suitability verdict, position-size recommendation, or execution instruction.

Detailed contract evidence was preserved separately in `technical-reports/eth-mainnet-susdat.md`.

## 1. Executive view

sUSDat is a yield-bearing share token issued in the Saturn ecosystem. A holder deposits USDat and receives sUSDat. The value of sUSDat is intended to rise through the exchange rate against USDat, rather than through the token balance increasing [D1][O1][O6].

The important investment point is that sUSDat should not be analyzed as a simple liquid stablecoin. The return and exit profile depend on several layers:

- USDat, the immediate asset used by the vault [O5][O6];
- STRC / digital-credit exposure that Saturn says supports sUSDat yield [D1][D2][D3];
- a withdrawal queue that can turn an exit into a non-atomic settlement process [D4][O2][O6];
- compliance controls, including blacklist / freeze / whitelist mechanics in sUSDat and USDat [O1][O5][O6];
- administrator and timelock state, including a pending migration from direct EOA control toward timelock-mediated control at the research snapshot [O4][O6][R1].

Primary risk implication: the token can have a visible price and a stated yield while still carrying redemption timing, reserve-verification, admin-control, and compliance-gating risk. Any live exit or collateral use should be refreshed with current queue state, holder eligibility, restriction state, and route quotes.

## 2. What the token represents

sUSDat represents a claim on a Saturn vault whose immediate accounting asset is USDat. Saturn describes USDat as a stablecoin backed by tokenized U.S. Treasuries, while sUSDat is the staked version that earns from digital-credit / STRC exposure [D1][D2][D5].

The token does not rebase. If value accrues, the holder owns the same number of sUSDat tokens, but each token should convert into more USDat through the vault exchange rate [D1][O1][O6].

The economic exposure is therefore not limited to a USDat balance. It includes STRC valuation, off-chain digital-credit performance, reserve verification, and the operational process used to convert or redeem those exposures [D2][D3][D5][D6].

## 3. Main risk implications

### Backing risk

Saturn’s own materials describe sUSDat as linked to STRC / digital-credit exposure, and the app snapshot showed most of sUSDat collateral value in STRC rather than idle USDat: USDat $8.036M / 8.3% and STRC $88.520M / 91.7% at extraction time [D6].

That means the analyst should not treat the vault as a simple cash-reserve product. The key question is whether STRC valuation, custody, and reserve reporting are independently verifiable. Saturn’s transparency page states that sUSDat STRC reserves require additional verification and that reserve-NAV work was in progress [D5].

Risk implication: the headline exchange rate can look orderly while the backing evidence is still incomplete. This prevents clean comparative ranking until STRC custody, valuation, reserve proof, and audit scope are reconciled.

### Redemption and liquidity risk

sUSDat exits do not use the simplest “redeem now and receive cash” path. Standard vault withdraw / redeem paths are disabled. A holder requests redemption, receives a withdrawal-request NFT, waits for queue processing, and later claims USDat [D4][O1][O2][O6].

This creates transition-stage assets: while the redemption request is pending, the holder no longer simply has freely liquid sUSDat, but has a claim that depends on queue state, processor action, and USDat availability [D4][O2].

Secondary liquidity was visible but uneven in the saved snapshot. Dexscreener showed the largest Ethereum Curve sUSDat venue at price $0.9260, liquidity $2.756M, and 24h volume $3.026M. Other venues were much smaller, and one Balancer venue had only $804 liquidity in the saved data [M1].

Risk implication: a quoted market price is not an executable exit assumption. For any specific size, the relevant check is a live route quote plus current queue and restriction state.

### Control and intervention risk

sUSDat and the related withdrawal queue are upgradeable. Role holders can pause, blacklist, upgrade, change key parameters, and process or seize withdrawal requests in specific circumstances [O1][O2][O5][O6].

At the snapshot, some powerful roles were still held by an EOA, with pending operations scheduled to revoke that EOA’s default-admin roles around 2026-06-08 UTC and move more control under a timelock. Those revocations were not yet executed in the snapshot [O4][O6][R1].

Risk implication: the governance-control profile was in transition. An analyst should not assume that the current admin speed is either fully immediate or fully timelocked without refreshing the exact role state.

### Legal and eligibility risk

The underlying USDat path includes freeze, forced-transfer, pause, and whitelist controls [O5][O6]. The legal and operational policy behind those controls was not fully mapped in the parent research.

Risk implication: holder-specific eligibility and restriction checks matter. A generic token balance does not prove that a specific holder can enter, redeem, transfer, or liquidate without review.

### Pricing and oracle risk

sUSDat accounting uses USDat balance plus vested STRC value, with STRC priced through an oracle. The STRC oracle had a 26-hour maximum staleness parameter in the snapshot, with price bounds around the STRC value [O3][O6].

Risk implication: vault accounting can miss practical exit frictions. Even if the oracle and vault exchange rate are current, the holder may still face queue delay, issuer controls, USDat restrictions, or DEX liquidity stress.

## 4. Backing and NAV quality

Current evidence supports the following plain-language model:

- Immediate vault asset: USDat [O5][O6].
- Yield source: Saturn says USDat deposits acquire STRC / digital-credit exposure [D1][D2].
- App snapshot: USDat TVL $138.566M, sUSDat TVL $96.557M, sUSDat APY 15.9%, USDat reserve ratio 100.01%, and sUSDat collateral split heavily weighted to STRC [D6].
- Independent reserve verification: incomplete in the extracted evidence. Saturn states that additional verification is needed for off-chain digital-credit holdings, and that Accountable / Chainlink reserve-NAV work is underway [D5].

Analyst conclusion: backing is explainable but not fully proven from the sources collected. Use the dossier for context, but require updated reserve / custody / valuation evidence before treating the asset as cleanly ranked or production-ready.

## 5. Liquidity and exit risk

There are two exit paths, each with different risks.

Primary redemption path:

1. The holder requests redemption.
2. sUSDat is placed into a withdrawal queue.
3. A withdrawal-request NFT represents the pending claim.
4. A processor handles the conversion and claim process.
5. The holder claims USDat after processing [D4][O2][O6].

Main risks: queue congestion, processor availability, USDat availability, minimum-out checks, and compliance state.

Secondary market path:

- Largest saved venue: Curve pair at price $0.9260, liquidity $2.756M, 24h volume $3.026M [M1].
- Additional venues existed but were materially smaller in the saved snapshot [M1].

Main risks: pool depth, price discount to accounting NAV, route fragmentation, and size-dependent slippage.

Action implication for an analyst: any real exit requires a fresh quote and should not rely on the saved market-data snapshot.

## 6. Controls, governance, and legal restrictions

The most relevant control facts are:

- sUSDat can be paused or blacklisted through compliance roles [O1][O6].
- USDat has freeze, forced-transfer, pause, and whitelist-manager roles that can affect entry and exit [O5][O6].
- sUSDat, the withdrawal queue, and USDat are upgradeable [O1][O2][O5][O6].
- A 5-day timelock existed, but at the snapshot some default-admin revocations were still pending and not executed [O4][O6].
- No Safe multisig was identified as a current sUSDat role holder in the parent on-chain artifact [R1].

Risk implication: admin and compliance controls can directly affect existing holders through pause, blacklist, queue processing, or underlying USDat restrictions. Before any live action, the analyst should refresh role holders, pending timelock operations, and current restriction state.

## 7. Pricing / oracle risk in plain language

The vault value is not simply a DEX price. It is calculated from the vault’s USDat balance plus STRC value, with STRC priced through an oracle [O1][O3][O6].

This can create a gap between three values:

- accounting value, based on the vault and oracle;
- primary redemption value, based on queue processing and USDat availability;
- market exit value, based on DEX liquidity and trade size.

Risk implication: a healthy accounting value can coexist with a discounted market exit or a blocked redemption path. For Credit Account or liquidation analysis, use live market and restriction checks rather than the accounting rate alone.

## 8. What must be checked before live use

Before using this dossier for a live position, collateral decision, liquidation path, or execution package, refresh:

- current sUSDat and queue pause state;
- current blacklist / freeze / whitelist state for the holder and recipient;
- USDat restriction state and legal / eligibility policy;
- queue pending count, claim readiness, and processor status;
- STRC oracle address, price, staleness, and bounds;
- current reserve / custody / NAV evidence for STRC exposure;
- current admin-role holders and whether pending timelock operations executed;
- live route quote for the specific size;
- audit / formal-verification scope against the exact deployed contracts;
- any new incident, pause, reserve-shortfall, oracle-failure, or redemption-delay disclosures.

Practical implication: unresolved backing and control questions require human review; unresolved route, queue, eligibility, or restriction state should block automated execution.

## 9. Evidence quality

High-confidence evidence:

- exact token identity, underlying USDat address, proxy/source state, and role snapshots from Etherscan/RPC [O1][O2][O3][O4][O5][O6];
- withdrawal queue mechanics from verified source and Saturn docs [D4][O2];
- point-in-time market data from Dexscreener [M1].

Medium-confidence evidence:

- Saturn documentation on STRC / digital-credit mechanism and app metrics [D1][D2][D3][D6];
- transparency and audit page listings [D5].

Lower-confidence or incomplete evidence:

- independent STRC custody / valuation / reserve proof;
- exact deployed-scope audit mapping;
- comprehensive incident history;
- holder-specific eligibility and restriction state;
- live executable liquidity for a concrete position.

## 10. Source map

Each source ID below now includes the actual URL or local evidence path. Local paths are relative to this report folder unless shown as full project paths.

- **METH** — [methodology.md](../methodology.md). Source class: unknown. Accessed: 2026-06-04. Confidence: high. Project-specific pipeline, section requirements, labels, and missing-data behavior.
- **R1** — [research/eth-mainnet-susdat/onchain-admin.md](../research/eth-mainnet-susdat/onchain-admin.md). Source class: onchain. Accessed: 2026-06-04. Confidence: high. Parent onchain/admin research; summarizes exact-token RPC/source/role/event evidence.
- **R2** — [research/eth-mainnet-susdat/issuer-backing-security.md](../research/eth-mainnet-susdat/issuer-backing-security.md). Source class: mixed issuer_docs/onchain/audit. Accessed: 2026-06-04. Confidence: medium-high. Parent issuer/backing/security synthesis.
- **R3** — [research/eth-mainnet-susdat/transfer-liquidity-oracle-governance.md](../research/eth-mainnet-susdat/transfer-liquidity-oracle-governance.md). Source class: mixed onchain/issuer_docs/market_data. Accessed: 2026-06-04. Confidence: medium-high. Parent transfer/liquidity/oracle/governance synthesis.
- **O1** — [etherscan.io/address/0xD166337499E176bbC38a1FBd113Ab144e5bd2Df7](https://etherscan.io/address/0xD166337499E176bbC38a1FBd113Ab144e5bd2Df7). Source class: onchain. Accessed: 2026-06-04. Confidence: high. sUSDat address, proxy/source page, token tracker, verified source reference.
- **O2** — [etherscan.io/address/0x4Bc9FEC04F0F95e9b42a3EF18F3C96fB57923D2e](https://etherscan.io/address/0x4Bc9FEC04F0F95e9b42a3EF18F3C96fB57923D2e). Source class: onchain. Accessed: 2026-06-04. Confidence: high. WithdrawalQueueERC721 proxy/source page.
- **O3** — [etherscan.io/address/0x5f7EcD0D045C393DA6CB6C933C671AC305a871BF](https://etherscan.io/address/0x5f7EcD0D045C393DA6CB6C933C671AC305a871BF). Source class: onchain. Accessed: 2026-06-04. Confidence: high. STRC oracle exact-match source and parameters.
- **O4** — [etherscan.io/address/0xfD5782E3BFF366601da3973aE30C583dE4F08A67](https://etherscan.io/address/0xfD5782E3BFF366601da3973aE30C583dE4F08A67). Source class: onchain. Accessed: 2026-06-04. Confidence: high. Saturn timelock source, role state, and delay evidence.
- **O5** — [etherscan.io/address/0x23238F20B894f29041f48d88Ee91131c395aAA71](https://etherscan.io/address/0x23238F20B894f29041f48d88Ee91131c395aAA71). Source class: onchain. Accessed: 2026-06-04. Confidence: high. USDat underlying source/proxy/role evidence relevant to sUSDat exits.
- **O6** — [ethereum-rpc.publicnode.com](https://ethereum-rpc.publicnode.com) and [research/eth-mainnet-susdat/raw/onchain-admin-snapshot-2026-06-04.json](../research/eth-mainnet-susdat/raw/onchain-admin-snapshot-2026-06-04.json). Source class: onchain. Accessed: 2026-06-04. Confidence: high. Direct RPC calls, EIP-1967 storage slots, event logs, role state, timelock operation state.
- **D1** — [saturncredit.gitbook.io/saturn-docs/solution/susdat-overview](https://saturncredit.gitbook.io/saturn-docs/solution/susdat-overview). Source class: issuer_docs. Accessed: 2026-06-04. Confidence: medium. sUSDat overview, ERC-4626 framing, underlying USDat, yield/reward vesting prose.
- **D2** — [saturncredit.gitbook.io/saturn-docs/solution/susdat-overview/digital-credit-strategy](https://saturncredit.gitbook.io/saturn-docs/solution/susdat-overview/digital-credit-strategy). Source class: issuer_docs. Accessed: 2026-06-04. Confidence: medium. STRC / digital-credit strategy and dividend framing.
- **D3** — [saturncredit.gitbook.io/saturn-docs/solution/susdat-overview/susdat-dynamic-reserve](https://saturncredit.gitbook.io/saturn-docs/solution/susdat-overview/susdat-dynamic-reserve). Source class: issuer_docs. Accessed: 2026-06-04. Confidence: medium. Dynamic reserve allocation between Treasuries and digital credit.
- **D4** — [saturncredit.gitbook.io/saturn-docs/solution/susdat-overview/staking-and-unstaking-process](https://saturncredit.gitbook.io/saturn-docs/solution/susdat-overview/staking-and-unstaking-process). Source class: issuer_docs. Accessed: 2026-06-04. Confidence: medium. Deposit/unstaking flow, withdrawal queue NFT, processor sale, oracle validation, secondary-market path.
- **D5** — [saturncredit.gitbook.io/saturn-docs/operations-and-governance/transparency-and-audits](https://saturncredit.gitbook.io/saturn-docs/operations-and-governance/transparency-and-audits). Source class: issuer_docs. Accessed: 2026-06-04. Confidence: medium. Transparency/audit page, USDat capital notes, sUSDat reserve verification caveat, audit/FV report links.
- **D6** — [app.saturn.credit/insights](https://app.saturn.credit/insights). Source class: issuer_docs. Accessed: 2026-06-04. Confidence: medium. App insight snapshot for TVL, APY, reserve ratio, and sUSDat collateral split; issuer app data, not independent attestation.
- **M1** — [research/eth-mainnet-susdat/raw/dexscreener-saturn_susdat-2026-06-04.json](../research/eth-mainnet-susdat/raw/dexscreener-saturn_susdat-2026-06-04.json). Source class: market_data. Accessed: 2026-06-04. Confidence: medium. Saved Dexscreener API snapshot for venues, price, liquidity, and 24h volume.

## 11. Technical appendix pointer

For raw addresses, role identifiers, implementation slots, method names, and table-level evidence, see:

- `technical-reports/eth-mainnet-susdat.md`
- `research/eth-mainnet-susdat/`
