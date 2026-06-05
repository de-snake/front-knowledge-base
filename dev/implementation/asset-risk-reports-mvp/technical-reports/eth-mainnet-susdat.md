# Saturn sUSDat — MVP asset risk dossier

Report date: 2026-06-04 UTC
Analyst: Hermes kanban synthesis worker
Display: Saturn sUSDat
Chain: Ethereum mainnet (`chain_id: 1`)
Token address: `0xD166337499E176bbC38a1FBd113Ab144e5bd2Df7`
Symbol: `sUSDat`
Intended use: unknown

This dossier is an objective, source-linked asset context artifact. It does not advise asset selection, position sizing, position fit, or execution.

Citation format: inline source IDs resolve in Section 13 to URL or local evidence path, source class, access date, and confidence. Material rows also state the source class/access/confidence inline where the source is especially important.

## 1. Agent-context summary

Saturn sUSDat is an Ethereum mainnet ERC-20 / ERC-20Permit / ERC-4626-style non-rebasing share token at `0xD166337499E176bbC38a1FBd113Ab144e5bd2Df7`; its `asset()` is USDat at `0x23238F20B894f29041f48d88Ee91131c395aAA71`, and standard ERC-4626 `withdraw` / `redeem` are disabled in favor of `requestRedeem` plus a withdrawal-queue NFT flow [O1/O2/O6, onchain, 2026-06-04, high]. Saturn docs describe sUSDat as a yield-bearing vault token whose USDat deposits are used to acquire STRC / digital-credit exposure, with value accruing through a rising sUSDat-to-USDat exchange rate [D1/D2/D4, issuer_docs, 2026-06-04, medium]. The practical risk surface is not limited to market price: backing/NAV depends on USDat, STRC, a STRC oracle, offchain reserve/NAV verification, queue processing, compliance controls, and admin/timelock state [O1/O2/O3/O5/O6/D4/D5, mixed onchain+issuer_docs, 2026-06-04, medium-high]. Material unknowns that affect downstream behavior are marked `review_required` or `block_automation` below instead of being treated as absence of risk.

## 2. One-paragraph mechanism

sUSDat is a Saturn vault/share token: users deposit USDat and receive sUSDat shares; Saturn docs state the deposited USDat is used to acquire STRC / digital-credit exposure, and STRC dividends or rewards increase the vault value so that the sUSDat-to-USDat exchange rate rises over time [D1/D2/D4, issuer_docs, 2026-06-04, medium; O6, onchain/RPC snapshot, 2026-06-04, high]. Onchain accounting for the exact token tracks `totalAssets()` as USDat balance plus vested STRC value priced through the STRC oracle; exits do not use normal ERC-4626 `withdraw` / `redeem` and instead use `requestRedeem`, escrowed sUSDat, a withdrawal-request NFT, processor execution, and a final USDat claim [O1/O2/O3/O6, onchain, 2026-06-04, high; D4, issuer_docs, 2026-06-04, medium].

## 3. Identity and token semantics

| Field | Value | Source |
|---|---|---|
| Canonical chain | Ethereum mainnet | User-supplied scope corroborated by Ethereum RPC and Etherscan token pages [O1/O6, onchain, 2026-06-04, high] |
| chain_id | `1` | User-supplied scope and Ethereum mainnet RPC context [O6, onchain, 2026-06-04, high] |
| Token address | `0xD166337499E176bbC38a1FBd113Ab144e5bd2Df7` | Etherscan token/source page plus direct RPC calls [O1/O6, onchain, 2026-06-04, high] |
| Explorer label / tracker | `Saturn: sUSDat Token`; token tracker `Staked USDat (sUSDat)` | Etherscan address/token page [O1, onchain, 2026-06-04, high] |
| `name()` | `Staked USDat` | Direct RPC calls recorded in the onchain snapshot [O6, onchain, 2026-06-04, high] |
| `symbol()` | `sUSDat` | Direct RPC calls recorded in the onchain snapshot [O6, onchain, 2026-06-04, high] |
| `decimals()` | `18` | Direct RPC and verified source summary [O1/O6, onchain, 2026-06-04, high] |
| Standards / interfaces | ERC-20, ERC-20Permit, ERC-4626-style vault share token | Verified source imports/inheritance and behavior summary [O1/O6, onchain, 2026-06-04, high] |
| Underlying asset from `asset()` | USDat, `0x23238F20B894f29041f48d88Ee91131c395aAA71`, 6 decimals | Direct `asset()` / USDat RPC calls and USDat source page [O5/O6, onchain, 2026-06-04, high] |
| Token behavior | Non-rebasing share token / vault share; value accrues through exchange-rate changes rather than balance rebasing | Saturn overview plus verified `totalAssets()` / share accounting summary [D1, issuer_docs, 2026-06-04, medium; O6, onchain, 2026-06-04, high] |
| Asset type | Issuer-controlled ERC-4626-style share token with USDat and STRC / digital-credit exposure; not an ordinary ERC-20 cash token | Saturn docs and exact-token onchain accounting [D1/D2/D3/D4, issuer_docs, 2026-06-04, medium; O6, onchain, 2026-06-04, high] |
| Transition-stage behavior | A holder can enter a redemption transition state: sUSDat shares are escrowed into the withdrawal queue and a withdrawal-request NFT represents the claim until processing/claim completion | Saturn unstaking docs and queue contract/source summary [D4, issuer_docs, 2026-06-04, medium; O2/O6, onchain, 2026-06-04, high] |
| Current paused status | `paused=false` for sUSDat in the snapshot | Direct RPC in onchain snapshot [O6, onchain, 2026-06-04, high] |
| Current deposit fee | `0` bps; `feeRecipient=0x3dc0aa75A6Fd01C3dcf9f6FdAF08308B6489f5B5` | Direct RPC in onchain snapshot [O6, onchain, 2026-06-04, high] |
| Current tolerance / max rewards / vesting | `toleranceBps=2000`; `maxRewardsBps=250`; `vestingPeriod=259200` seconds / 3 days | Direct RPC in onchain snapshot [O6, onchain, 2026-06-04, high] |

Material caveat: Saturn docs describe a 30-day reward vesting process, while the exact-token onchain snapshot observed a 3-day `vestingPeriod`; current contract reasoning should use the onchain value and treat the docs/onchain mismatch as `missing_behavior: review_required` for any workflow that depends on vesting-period assumptions [D1/D4, issuer_docs, 2026-06-04, medium; O6, onchain, 2026-06-04, high].

## 4. Issuer / protocol and business model

| Topic | Facts | Source |
|---|---|---|
| Issuer / protocol | Saturn is the protocol/issuer context named by the official site/docs for USDat and sUSDat | Saturn docs/site references in parent artifacts [D1/D2/D3/D4/D5, issuer_docs, 2026-06-04, medium] |
| Product framing | Saturn describes USDat as a non-yielding stablecoin backed 100% by tokenized U.S. treasuries, and sUSDat as the staked version that earns through digital-credit / STRC exposure | Saturn site/docs/app summaries [D1/D2/D5/D6, issuer_docs, 2026-06-04, medium] |
| Yield / revenue source | Docs state sUSDat yield comes from STRC / digital-credit dividends and that STRC exposure was 100% at launch; app snapshot showed sUSDat APY `15.9%` at extraction | Saturn overview/digital-credit strategy and app insight snapshot [D1/D2/D6, issuer_docs, 2026-06-04, medium] |
| Offchain dependencies | Saturn states sUSDat reserves include offchain digital-credit holdings that require additional verification, and says Accountable / Chainlink reserve-NAV work is underway | Transparency/audits page [D5, issuer_docs, 2026-06-04, medium] |
| Onchain dependencies | sUSDat depends on USDat, STRC balances/value, the STRC oracle, withdrawal queue, processor role, compliance role, and admin roles | Verified source/RPC/event snapshot [O1/O2/O3/O5/O6, onchain, 2026-06-04, high] |
| Mint/deposit path | Deposits/mints accept USDat and mint sUSDat shares; permit variants are supported | Verified source/RPC summary [O1/O6, onchain, 2026-06-04, high] |
| Redemption path | Ordinary holders can request redemption, but the exit path is queue/processor/oracle/compliance dependent; normal ERC-4626 `withdraw` / `redeem` revert | Verified source/RPC summary and Saturn unstaking docs [O1/O2/O6, onchain, 2026-06-04, high; D4, issuer_docs, 2026-06-04, medium] |
| Who can pause / blacklist / freeze / rescue / upgrade | sUSDat compliance role can blacklist and pause; default admin can upgrade, unpause, rescue tokens, change fees/vesting/tolerance/reward parameters, and redistribute blacklisted balances; USDat roles can freeze, force transfer, pause, and manage whitelist state | Role and source inventory [O1/O2/O5/O6, onchain, 2026-06-04, high] |
| Direct redemption eligibility | Contract path allows redemption requests but actual claim completion depends on queue processing, oracle validation, user minimum amount, blacklist/freeze state, and USDat availability; full legal/KYC eligibility terms were not independently mapped | Queue/source/docs summary [O2/O5/O6, onchain, 2026-06-04, high; D4, issuer_docs, 2026-06-04, medium]. Missing legal/KYC policy: `review_required`. |

## 5. Backing, NAV, and exposure map

`nav_model: collateralized vault / issuer NAV / offchain-credit exposure`

| Field | Current facts | Source |
|---|---|---|
| Reserve / underlying assets | Exact token `asset()` is USDat; `totalAssets()` is tracked as USDat balance plus vested STRC value priced through the STRC oracle | Onchain snapshot/source summary [O1/O3/O5/O6, onchain, 2026-06-04, high] |
| STRC exposure | Saturn docs describe USDat deposits being used to acquire STRC, described as Strategy preferred-equity / digital-credit exposure with dividend mechanics | Digital-credit strategy and sUSDat overview [D1/D2, issuer_docs, 2026-06-04, medium] |
| Dynamic reserve model | Docs describe allocation between Treasuries and digital credit based on Strategy LTV; lower LTV can permit higher digital-credit exposure and higher LTV shifts toward Treasuries | Dynamic reserve docs [D3, issuer_docs, 2026-06-04, medium] |
| Current issuer-app snapshot | Saturn app insights showed USDat TVL `$138,566,486`, sUSDat TVL `$96,556,553`, sUSDat APY `15.9%`, USDat reserve ratio `100.01%`, and sUSDat collateral split of USDat `$8,036,628 / 8.3%` and STRC `$88,519,925 / 91.7%` | Saturn app insights snapshot via parent artifact [D6, issuer_docs/app data, 2026-06-04, medium] |
| Custody / reserve verification | Saturn transparency page states USDat capital is onchain but sUSDat STRC reserves require additional verification; Accountable / Chainlink reserve-NAV work was described as in progress | Transparency/audits page [D5, issuer_docs, 2026-06-04, medium] |
| NAV report cadence | App data was observed as point-in-time issuer app data; independent reserve/NAV attestation cadence for sUSDat STRC exposure was not confirmed | App insight and transparency docs [D5/D6, issuer_docs, 2026-06-04, medium]. `missing_behavior`: `review_required`. |
| Primary redemption mechanism | Request → queue NFT receipt → processor lock/process/convert STRC into USDat → claim USDat; user-supplied minimum can revert processing if USDat owed is too low | Saturn unstaking docs and queue source summary [D4, issuer_docs, 2026-06-04, medium; O2/O6, onchain, 2026-06-04, high] |
| NAV vs secondary price | NAV/share accounting, STRC oracle value, queue exit value, and DEX market price are distinct and can diverge | Onchain accounting, unstaking docs, Dexscreener snapshot [O3/O6, onchain, 2026-06-04, high; D4, issuer_docs, 2026-06-04, medium; M1, market_data, 2026-06-04, medium] |
| Principal exposure categories | STRC/offchain-credit valuation, dividend/payment timing, issuer/operator processing, oracle valuation, queue timing, compliance freeze/blacklist/whitelist controls, and DEX liquidity/slippage | Synthesized from onchain/admin, issuer/backing, and transfer/oracle artifacts [R1/R2/R3, local research artifacts, 2026-06-04, medium-high] |

Missing-data behavior for backing/NAV: independent STRC custody, valuation, reserve proof, and legal/custodial terms were not fully verified in the parent artifacts. For explanation-only uses this can be marked unknown and continued; for ranking, collateral admission, or automated execution it is `review_required`, and for a concrete exit it is `block_automation` until Preview/live quote and queue state are known [METH, methodology, 2026-06-04, high; D5, issuer_docs, 2026-06-04, medium].

## 6. Contract admin, multisigs, and sensitive actions

### 6.1 Proxy / implementation / upgradeability

| Contract | Address | Pattern / current admin state | Upgrade or admin authority | Source |
|---|---|---|---|---|
| sUSDat | `0xD166337499E176bbC38a1FBd113Ab144e5bd2Df7` | ERC-1967 proxy + UUPS implementation; implementation `0x2005E0CA201A37694125fF267aE57872bEa0a0Ce`; EIP-1967 admin slot zero | `_authorizeUpgrade` gated by `DEFAULT_ADMIN_ROLE` | Etherscan/source + storage RPC [O1/O6, onchain, 2026-06-04, high] |
| Withdrawal queue | `0x4Bc9FEC04F0F95e9b42a3EF18F3C96fB57923D2e` | ERC-1967 proxy + UUPS implementation; implementation `0x256fA0ba1b6dFB50EE883955c5a99D3C1b017Fd5`; admin slot zero | `_authorizeUpgrade` gated by `DEFAULT_ADMIN_ROLE` | Etherscan/source + storage RPC [O2/O6, onchain, 2026-06-04, high] |
| STRC oracle | `0x5f7EcD0D045C393DA6CB6C933C671AC305a871BF` | Non-proxy `StrcPriceOracle` AccessControl contract in the parent snapshot | Default admin can update wrapped oracle, staleness, and price bounds | Etherscan/source + RPC [O3/O6, onchain, 2026-06-04, high] |
| USDat underlying | `0x23238F20B894f29041f48d88Ee91131c395aAA71` | TransparentUpgradeableProxy; implementation `0x17cAC25c6D6BBcB592837FEA083A5c8Eb4D1E52E`; proxy admin `0xcf1072DA5f0D127AEf99136489BAd08bFa3D1A7D` | ProxyAdmin owner `0x610182581C93687Ca03F4a8E7f124f8cEC616820` can upgrade implementation | Etherscan/source + storage RPC [O5/O6, onchain, 2026-06-04, high] |

### 6.2 Current sensitive role holders

| Contract / role | Current holder(s) | Holder type | Sensitive powers | Source |
|---|---|---|---|---|
| sUSDat `DEFAULT_ADMIN_ROLE` | `0x610182581C93687Ca03F4a8E7f124f8cEC616820`; `0xfD5782E3BFF366601da3973aE30C583dE4F08A67` | EOA; timelock contract | Grants/revokes roles; UUPS upgrades; unpause; rescue; parameter changes; redistribute blacklisted balances | Event/RPC/source reconstruction [O1/O4/O6, onchain, 2026-06-04, high] |
| sUSDat `PROCESSOR_ROLE` | `0x09D6E34cE24D54890fF0BC6a090b5f880F8C729f` | EOA | Converts USDat/STRC and transfers rewards | Event/source reconstruction [O1/O6, onchain, 2026-06-04, high] |
| sUSDat `COMPLIANCE_ROLE` | `0x10D59F776db12b4B271b2609CB8b7Ddd0A82703B` | EOA | Blacklist/unblacklist and pause | Event/source reconstruction [O1/O6, onchain, 2026-06-04, high] |
| Queue `DEFAULT_ADMIN_ROLE` | `0x610182581C93687Ca03F4a8E7f124f8cEC616820`; `0xfD5782E3BFF366601da3973aE30C583dE4F08A67` | EOA; timelock contract | UUPS upgrades, role admin, unpause | Event/source reconstruction [O2/O4/O6, onchain, 2026-06-04, high] |
| Queue `PROCESSOR_ROLE` | `0x09D6E34cE24D54890fF0BC6a090b5f880F8C729f` | EOA | Lock/unlock/process withdrawal requests and supply USDat | Event/source reconstruction [O2/O6, onchain, 2026-06-04, high] |
| Queue `COMPLIANCE_ROLE` | `0x10D59F776db12b4B271b2609CB8b7Ddd0A82703B` | EOA | Seize requests, seize blacklisted funds, pause | Event/source reconstruction [O2/O6, onchain, 2026-06-04, high] |
| Queue `STAKED_USDAT_ROLE` | sUSDat contract `0xD166337499E176bbC38a1FBd113Ab144e5bd2Df7` | Contract | Add requests and claim-for-user helpers | Event/source reconstruction [O1/O2/O6, onchain, 2026-06-04, high] |
| Timelock | `0xfD5782E3BFF366601da3973aE30C583dE4F08A67` | Timelock contract | Minimum delay 432,000 seconds / 5 days; open executor; EOA proposer/canceller `0x610182...` | Direct `hasRole` / `getMinDelay` calls and verified source [O4/O6, onchain, 2026-06-04, high] |
| USDat freeze / forced-transfer / pauser / whitelist manager | `0x10D59F776db12b4B271b2609CB8b7Ddd0A82703B` for freeze/forced transfer/pauser/whitelist manager roles in the snapshot | EOA | Freeze/unfreeze, forced transfer from frozen accounts, pause, whitelist management | USDat role/source/RPC summary [O5/O6, onchain, 2026-06-04, high] |
| Safe multisig | No Safe multisig was identified among current sUSDat role holders in the parent onchain artifact | n/a / unknown offchain | No enforceable Safe threshold was found onchain for current roles | Code checks + role-holder inventory [O6/R1, onchain/local artifact, 2026-06-04, medium] |

### 6.3 Pending admin transition

As of the 2026-06-04 RPC snapshot, pending timelock operations were scheduled to revoke `DEFAULT_ADMIN_ROLE` from EOA `0x610182...` on sUSDat, USDat, the STRC oracle, and the withdrawal queue, with ready timestamps around 2026-06-08 UTC; the operations were in `Waiting` state and not yet executed in the snapshot [O4/O6/R1, onchain/local artifact, 2026-06-04, high]. `missing_behavior`: recheck the four operations after the ready timestamps before classifying default-admin execution speed as timelocked rather than immediate (`review_required`).

### 6.4 Sensitive action classification

| Sensitive action | Existing-holder impact | Execution speed in snapshot | Source / missing behavior |
|---|---|---|---|
| Upgrade sUSDat implementation | `unknown` because implementation can change token semantics | `immediate` while EOA default admin remains; potentially `timelocked` if revocations execute | sUSDat source/roles [O1/O4/O6, onchain, 2026-06-04, high]. Recheck pending revocations: `review_required`. |
| Upgrade withdrawal queue implementation | `unknown` because queue controls redemption requests/claims | `immediate` while EOA default admin remains; potentially `timelocked` if revocations execute | Queue source/roles [O2/O4/O6, onchain, 2026-06-04, high]. Recheck pending revocations: `review_required`. |
| Upgrade USDat implementation | `unknown` because underlying asset controls can affect entry/exit | `immediate` via ProxyAdmin owner EOA in the snapshot | USDat proxy/source/RPC [O5/O6, onchain, 2026-06-04, high]. ProxyAdmin ownership migration not verified: `review_required`. |
| Blacklist sUSDat address | `direct_freeze` | `immediate` via compliance EOA | sUSDat source/role logs [O1/O6, onchain, 2026-06-04, high] |
| Pause sUSDat | `direct_redemption_block` and transfer/deposit block | `immediate` via compliance EOA | sUSDat source/role logs [O1/O6, onchain, 2026-06-04, high] |
| Redistribute locked sUSDat amount | `direct_transfer` from blacklisted holder balance into remaining holder value | `immediate` while EOA default admin remains | sUSDat source/role logs [O1/O6, onchain, 2026-06-04, high] |
| Change deposit fee / fee recipient / vesting / tolerance / max rewards | `indirect` | `immediate` while EOA default admin remains | sUSDat source/RPC [O1/O6, onchain, 2026-06-04, high] |
| Processor conversions / reward transfers | `indirect` through backing mix and reward timing | `immediate` via processor EOA | sUSDat source/role logs [O1/O6, onchain, 2026-06-04, high] |
| Lock/unlock/process withdrawal requests | `direct_redemption_block` while locked/unprocessed | `immediate` via queue processor EOA | Queue source/role logs [O2/O6, onchain, 2026-06-04, high] |
| Queue seizure of blacklisted requests/funds | `direct_transfer` for affected blacklisted/frozen accounts | `immediate` via queue compliance EOA | Queue source/role logs [O2/O6, onchain, 2026-06-04, high] |
| Update STRC oracle address/staleness/bounds | `indirect`; can affect NAV/share accounting and queue processing | `immediate` while EOA default admin remains; potentially `timelocked` if revocations execute | STRC oracle source/RPC [O3/O4/O6, onchain, 2026-06-04, high] |
| USDat freeze / forced transfer / whitelist / pause | `direct_freeze`, `direct_transfer`, or `direct_redemption_block` depending path | `immediate` via USDat role holders in the snapshot | USDat source/RPC/role logs [O5/O6, onchain, 2026-06-04, high]. Full legal policy not mapped: `review_required`. |

## 7. Audits, formal verification, and incidents

| Item | Facts found | Source / confidence |
|---|---|---|
| Audit reports listed by Saturn | Saturn transparency/audits page lists Three Sigma Audit #1, Certora Audit #2, Certora Audit #3, and Certora Formal Verification downloadable reports | Official transparency page [D5, issuer_docs, 2026-06-04, medium] |
| Audit scope match | Parent issuer/security artifact did not download/read every PDF body end-to-end and did not match report scope to the current sUSDat implementation `0x2005E0...a0Ce`, current queue implementation, current USDat implementation, or STRC oracle | Parent artifact plus onchain implementation inventory [R2, local research, 2026-06-04, medium; O1/O2/O3/O5/O6, onchain, 2026-06-04, high]. `missing_behavior`: `review_required`. |
| Formal verification | Certora formal verification is listed by Saturn, but verified invariants and exact deployed-scope match were not extracted in parent artifacts | Official transparency page [D5, issuer_docs, 2026-06-04, medium]. `missing_behavior`: `review_required`. |
| Bug bounty | A bug-bounty program/scope was not located in the parent artifacts | Parent source index and security section [R2, local research, 2026-06-04, medium]. `missing_behavior`: `review_required` for security acceptance, `continue` for descriptive context. |
| Incidents | No confirmed exploit, depeg, reserve shortfall, oracle-failure postmortem, or emergency governance postmortem for the exact sUSDat token was found in the bounded parent sources | Parent incident pass [R2, local research, 2026-06-04, medium]. `missing_behavior`: absence of found incident is not proof of no incident; `review_required` for production acceptance. |
| Material onchain events | Parent onchain artifact observed multiple sUSDat/queue implementation upgrades, two sUSDat blacklist events, no scanned sUSDat pause/unpause events, and pending timelock operations for admin-role migration | Onchain/admin artifact and raw snapshot [R1/O6, onchain/local research, 2026-06-04, high] |

## 8. Transferability, redemption, and liquidity

| Field | Current facts | Source |
|---|---|---|
| ERC-20 transferability | sUSDat has ERC-20 transfer functions but transfer/transferFrom/deposit/request paths check blacklist state | sUSDat source/RPC summary [O1/O6, onchain, 2026-06-04, high] |
| Current restriction state | sUSDat `paused=false`; two `Blacklisted` events were observed in the scanned range; no sUSDat pause/unpause events were found in that scan | Onchain/admin artifact [R1/O6, onchain/local research, 2026-06-04, high] |
| Underlying restrictions | USDat whitelist was enabled in the snapshot and USDat has freeze, forced-transfer, pause, and whitelist-manager controls that can affect sUSDat entry/exit flows | USDat source/RPC summary [O5/O6, onchain, 2026-06-04, high] |
| Primary redemption path | Request redemption with shares and minimum USDat amount; queue receives sUSDat and mints a request NFT; processor locks/processes batch and obtains USDat; holder claims USDat and NFT is burned | Saturn unstaking docs and queue source summary [D4, issuer_docs, 2026-06-04, medium; O2/O6, onchain, 2026-06-04, high] |
| Claim readiness semantics | The withdrawal-request NFT represents a pending/processed claim state until claim; queue state and processor actions determine readiness | Saturn docs and queue source summary [D4, issuer_docs, 2026-06-04, medium; O2/O6, onchain, 2026-06-04, high] |
| Queue state | Parent snapshot recorded `pendingCount=65` and `paused=false` for the withdrawal queue | Onchain/admin artifact [R1/O6, onchain/local research, 2026-06-04, high] |
| Secondary-market venues in saved snapshot | Dexscreener snapshot showed Ethereum Curve pair `0x6206cA315c2fCDd2A857b47EFB285AA12c529a7a` at `priceUsd=0.9260`, liquidity `$2,755,680.11`, 24h volume `$3,025,785.78`; Uniswap pair `0x37083a...0a11` at `priceUsd=0.9434`, liquidity `$286,998.44`, 24h volume `$45,476.34`; another Curve pair `0xcAF1969E9ba98C05113b75d8633A17196e2D02a5` at `priceUsd=1.0010`, liquidity `$179,672.26`, 24h volume `$260,970.15`; Balancer composite pool id beginning `0xC32474B0...` at `priceUsd=0.7962`, liquidity `$803.83`, 24h volume `$210.61` | Saved Dexscreener JSON snapshot [M1, market_data, 2026-06-04, medium] |
| Liquidity caveat | Saved API liquidity is point-in-time market data and not an executable quote; size-dependent exit requires a live route quote / Preview | Dexscreener snapshot plus methodology execution rule [M1, market_data, 2026-06-04, medium; METH, methodology, 2026-06-04, high]. `missing_behavior`: `block_automation` for execution without live quote/Preview. |
| Eligible-liquidator depth | Not established in parent artifacts | Parent transfer/liquidity artifact [R3, local research, 2026-06-04, medium]. `missing_behavior`: `review_required` for compliance-gated collateral analysis; `block_automation` for liquidation/execution assumptions without route/eligibility proof. |

## 9. Oracle and pricing methodology

| Field | Current facts | Source |
|---|---|---|
| Primary price/NAV source | sUSDat share accounting uses `totalAssets()` = internally tracked USDat balance + vested STRC value; STRC value comes from `STRC_ORACLE.getPrice()` | sUSDat and STRC oracle source/RPC summary [O1/O3/O6, onchain, 2026-06-04, high] |
| STRC oracle | `0x5f7EcD0D045C393DA6CB6C933C671AC305a871BF` | sUSDat `getStrcOracle()` and Etherscan/source/RPC [O1/O3/O6, onchain, 2026-06-04, high] |
| Wrapped oracle dependency | STRC oracle wraps Chainlink-compatible oracle `0xf4d2076277FFf631eFC4385AB36b1f7734218d23` | STRC oracle RPC/source summary [O3/O6, onchain, 2026-06-04, high] |
| Staleness / bounds / observed price | `maxPriceStaleness=93600` seconds / 26 hours; price bounds min `20e8`, max `150e8`; snapshot `getPrice()` returned `94.72e8` with 8 decimals | STRC oracle RPC/source summary [O3/O6, onchain, 2026-06-04, high] |
| Redemption validation | Saturn docs state processing validates STRC sale execution price against the onchain oracle and the user's minimum USDat amount; if owed USDat is below the user's minimum the transaction reverts | Saturn unstaking docs and queue/source summary [D4, issuer_docs, 2026-06-04, medium; O2/O3/O6, onchain, 2026-06-04, high] |
| Oracle blind spots | STRC oracle/NAV accounting can miss immediate DEX discount/premium, queue congestion, processor availability, compliance freeze/blacklist, USDat whitelist/freeze, offchain STRC settlement delay, and secondary-market liquidity stress | Transfer/oracle parent artifact synthesized from onchain/source/docs/market data [R3, local research, 2026-06-04, medium-high] |
| Gearbox-specific oracle notes | Parent artifacts did not identify an active Gearbox main/reserve oracle configuration for this exact token | Parent artifacts [R1/R2/R3, local research, 2026-06-04, medium]. `missing_behavior`: `review_required` if used as Credit Account collateral. |

## 10. Governance / change-feed watchlist

Track these fields before reusing this dossier for live reasoning:

| Watch item | Why it matters | Source / missing behavior |
|---|---|---|
| Pending revocation of EOA `DEFAULT_ADMIN_ROLE` on sUSDat, USDat, STRC oracle, and queue | Execution speed may change from immediate EOA control to timelock-mediated control after ready timestamps around 2026-06-08 UTC | Timelock/RPC snapshot [O4/O6/R1, onchain/local research, 2026-06-04, high]. `review_required` after ready timestamps. |
| sUSDat and queue implementation upgrades | UUPS upgrades can change existing-holder semantics, queue behavior, and oracle/accounting logic | Upgrade events and current implementation inventory [O1/O2/O6/R1, onchain/local research, 2026-06-04, high] |
| sUSDat blacklist / unblacklist / pause / unpause events | These can directly restrict transfers, deposits, and redemption requests | sUSDat source/event scan [O1/O6/R1, onchain/local research, 2026-06-04, high] |
| USDat freeze / forced-transfer / whitelist / pause state | Underlying USDat controls can affect sUSDat entries, exits, and claims | USDat source/RPC summary [O5/O6/R1, onchain/local research, 2026-06-04, high] |
| STRC oracle address, max staleness, and price bounds | Affects `totalAssets()` and queue processing validation | STRC oracle source/RPC summary [O3/O6, onchain, 2026-06-04, high] |
| Withdrawal queue state | Pending count, locked batches, processed requests, claims, seizures, pause state, and processor availability affect redemption timing | Queue source/RPC/docs [O2/O6, onchain, 2026-06-04, high; D4, issuer_docs, 2026-06-04, medium] |
| Deposit fee, fee recipient, vesting period, tolerance, max rewards bps | These parameters affect deposits, reward accrual timing, and validation behavior | sUSDat parameter RPC/source summary [O1/O6, onchain, 2026-06-04, high] |
| Saturn reserve/NAV proof rollout | Accountable/Chainlink reserve/NAV evidence would materially affect backing verification status | Transparency/audits page [D5, issuer_docs, 2026-06-04, medium]. `missing_behavior`: `review_required`. |
| App reserve ratio / collateral split / TVL / APY | Issuer app data can drift and should not be treated as independent attestation | Saturn app insights snapshot [D6, issuer_docs/app data, 2026-06-04, medium]. `missing_behavior`: refresh before reuse. |
| Audit report scope and unresolved issues | Current deployed implementations may differ from report scope | Transparency/audits page and parent caveat [D5, issuer_docs, 2026-06-04, medium; R2, local research, 2026-06-04, medium]. `missing_behavior`: `review_required`. |

## 11. Data quality and missing-data behavior

| Material field | Current data quality | missing_behavior |
|---|---|---|
| Token identity and exact address | High-confidence direct RPC + Etherscan verified source/source summary [O1/O6, onchain, 2026-06-04, high] | `continue` |
| Proxy / implementation / core role state | High-confidence storage/RPC/event reconstruction in parent snapshot [O1/O2/O3/O4/O5/O6/R1, onchain/local research, 2026-06-04, high] | `continue` for descriptive use; `review_required` after 2026-06-08 pending timelock ready timestamps |
| EOA human/entity identity and operating controls | Not verified from primary Saturn governance/ops documents [R1, local research, 2026-06-04, medium] | `review_required` |
| Safe owners / thresholds | No Safe multisig role holder identified onchain; offchain control arrangements unknown [R1, local research, 2026-06-04, medium] | `continue` for onchain role description; `review_required` if operational custody is required |
| USDat underlying legal/freeze/whitelist policy | Onchain roles/states identified, policy/process not fully mapped [O5/O6/R1, onchain/local research, 2026-06-04, high/medium] | `review_required` |
| STRC custody / valuation / reserve proof | Saturn says additional verification is required; parent artifacts did not independently verify custody/valuation [D5/R2, issuer_docs/local research, 2026-06-04, medium] | `review_required` |
| Accountable / Chainlink reserve-NAV details | Mentioned by Saturn as work in progress; feed details not independently read/matched [D5/R2, issuer_docs/local research, 2026-06-04, medium] | `review_required` |
| Audit / formal verification scope | Reports listed by Saturn, exact deployed-scope and unresolved issues not matched [D5/R2, issuer_docs/local research, 2026-06-04, medium] | `review_required` |
| Incident history | No confirmed exploit/depeg/reserve-shortfall/oracle-failure postmortem found in bounded sources; absence is not proof none occurred [R2, local research, 2026-06-04, medium] | `continue` for explanation; `review_required` for production acceptance |
| Queue claim readiness | Queue contract/path identified; exhaustive request-level readiness not enumerated [O2/O6/R3, onchain/local research, 2026-06-04, high/medium] | `review_required` |
| Live executable liquidity / slippage | Dexscreener point-in-time snapshot saved; no live route quote for any position size [M1/R3, market_data/local research, 2026-06-04, medium] | `block_automation` until live quote / Preview |
| Gearbox-specific oracle / supported-market state | Not identified in parent artifacts [R1/R2/R3, local research, 2026-06-04, medium] | `review_required` if the asset is used as Credit Account collateral |
| Ranking / position-fit decision | Out of scope for this dossier by methodology | `cannot_rank_cleanly` without mandate, position context, live state, and missing-field resolution [METH, methodology, 2026-06-04, high] |

## 12. Highest-impact unknowns

1. Independent STRC custody, valuation, reserve proof, and Accountable/Chainlink NAV-feed details were not verified beyond Saturn's own statements; `missing_behavior: review_required` because sUSDat NAV depends heavily on STRC/offchain digital-credit exposure [D5/R2, issuer_docs/local research, 2026-06-04, medium].
2. Audit and formal-verification report scopes were not matched to the current deployed sUSDat, queue, USDat, and STRC-oracle implementations; `missing_behavior: review_required` before treating report existence as deployed-scope coverage [D5/R2/O1/O2/O3/O5/O6, mixed, 2026-06-04, medium-high].
3. Admin execution speed was in transition: EOA default-admin revocations were pending, not executed, in the snapshot; `missing_behavior: review_required` after 2026-06-08 UTC ready timestamps [O4/O6/R1, onchain/local research, 2026-06-04, high].
4. USDat underlying legal/eligibility/freeze/whitelist policy was not fully mapped even though onchain controls exist; `missing_behavior: review_required` for issuer-controlled-asset reasoning and `block_automation` for actions that assume unrestricted entry/exit [O5/O6/R1, onchain/local research, 2026-06-04, high/medium].
5. Live queue readiness and executable exit slippage for a specific position were not measured; `missing_behavior: block_automation` until live queue state, holder eligibility, and route quote / Preview are available [O2/O6/D4/M1/R3, mixed, 2026-06-04, medium-high].
6. Docs/onchain vesting-period mismatch remains unresolved: docs describe 30-day vesting, while the exact-token snapshot shows 3 days; `missing_behavior: review_required` for accrual/front-running assumptions [D1/D4/O6/R2, mixed, 2026-06-04, medium-high].
7. No public incident was found in the bounded parent sources, but this is not comprehensive incident assurance; `missing_behavior: continue` for explanation-only use and `review_required` for acceptance workflows [R2, local research, 2026-06-04, medium].

## 13. Sources

| ID | URL / local evidence | source_class | Accessed | Confidence | Notes |
|---|---|---|---|---|---|
| METH | `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/methodology.md` | unknown | 2026-06-04 | high | Project-specific pipeline, section requirements, labels, and missing-data behavior. |
| R1 | `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/eth-mainnet-susdat/onchain-admin.md` | onchain | 2026-06-04 | high | Parent onchain/admin research; summarizes exact-token RPC/source/role/event evidence. |
| R2 | `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/eth-mainnet-susdat/issuer-backing-security.md` | mixed issuer_docs/onchain/audit | 2026-06-04 | medium-high | Parent issuer/backing/security synthesis. |
| R3 | `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/eth-mainnet-susdat/transfer-liquidity-oracle-governance.md` | mixed onchain/issuer_docs/market_data | 2026-06-04 | medium-high | Parent transfer/liquidity/oracle/governance synthesis. |
| O1 | `https://etherscan.io/address/0xD166337499E176bbC38a1FBd113Ab144e5bd2Df7` | onchain | 2026-06-04 | high | sUSDat address, proxy/source page, token tracker, verified source reference. |
| O2 | `https://etherscan.io/address/0x4Bc9FEC04F0F95e9b42a3EF18F3C96fB57923D2e` | onchain | 2026-06-04 | high | WithdrawalQueueERC721 proxy/source page. |
| O3 | `https://etherscan.io/address/0x5f7EcD0D045C393DA6CB6C933C671AC305a871BF` | onchain | 2026-06-04 | high | STRC oracle exact-match source and parameters. |
| O4 | `https://etherscan.io/address/0xfD5782E3BFF366601da3973aE30C583dE4F08A67` | onchain | 2026-06-04 | high | Saturn timelock source, role state, and delay evidence. |
| O5 | `https://etherscan.io/address/0x23238F20B894f29041f48d88Ee91131c395aAA71` | onchain | 2026-06-04 | high | USDat underlying source/proxy/role evidence relevant to sUSDat exits. |
| O6 | `https://ethereum-rpc.publicnode.com` and `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/eth-mainnet-susdat/raw/onchain-admin-snapshot-2026-06-04.json` | onchain | 2026-06-04 | high | Direct RPC calls, EIP-1967 storage slots, event logs, role state, timelock operation state. |
| D1 | `https://saturncredit.gitbook.io/saturn-docs/solution/susdat-overview` | issuer_docs | 2026-06-04 | medium | sUSDat overview, ERC-4626 framing, underlying USDat, yield/reward vesting prose. |
| D2 | `https://saturncredit.gitbook.io/saturn-docs/solution/susdat-overview/digital-credit-strategy` | issuer_docs | 2026-06-04 | medium | STRC / digital-credit strategy and dividend framing. |
| D3 | `https://saturncredit.gitbook.io/saturn-docs/solution/susdat-overview/susdat-dynamic-reserve` | issuer_docs | 2026-06-04 | medium | Dynamic reserve allocation between Treasuries and digital credit. |
| D4 | `https://saturncredit.gitbook.io/saturn-docs/solution/susdat-overview/staking-and-unstaking-process` | issuer_docs | 2026-06-04 | medium | Deposit/unstaking flow, withdrawal queue NFT, processor sale, oracle validation, secondary-market path. |
| D5 | `https://saturncredit.gitbook.io/saturn-docs/operations-and-governance/transparency-and-audits` | issuer_docs | 2026-06-04 | medium | Transparency/audit page, USDat capital notes, sUSDat reserve verification caveat, audit/FV report links. |
| D6 | `https://app.saturn.credit/insights` | issuer_docs | 2026-06-04 | medium | App insight snapshot for TVL, APY, reserve ratio, and sUSDat collateral split; issuer app data, not independent attestation. |
| M1 | `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/eth-mainnet-susdat/raw/dexscreener-saturn_susdat-2026-06-04.json` | market_data | 2026-06-04 | medium | Saved Dexscreener API snapshot for venues, price, liquidity, and 24h volume. |
