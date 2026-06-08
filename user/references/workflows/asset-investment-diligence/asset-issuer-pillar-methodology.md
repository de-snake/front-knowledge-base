# Asset issuer pillar research methodology

This page is the detailed research method for the first Steakhouse-style Asset Rating pillar: **Issuer**.

It turns “issuer risk” from a broad checklist into a concrete research procedure. Use it when researching any token, vault token, PT underlying, tokenized security, redemption-window asset, or issuer-controlled collateral candidate.

Reference model: Steakhouse Financial’s collateral risk framework defines the Asset layer as three pillars — Issuer, Credit Risk, and Operational Risk. The Issuer pillar asks who has ultimate control over token issuance and redemption, and evaluates that issuer through Social, Decentralization, and Technical criteria. Steakhouse sets the Issuer pillar rating as the **best** of those three criteria, because one strong control channel can justify issuer confidence. In Gearbox research, still preserve the weaker criteria as explicit red flags; do not let the best-of rule hide a freeze, redemption, governance, or upgrade risk that affects a Credit Account user.

## Output of this page

A good issuer-pillar research artifact answers four questions:

1. **Who can change the asset holder’s outcome?** Identify the entity, DAO, multisig, contract admin, platform, or legal wrapper with ultimate influence over issuance, redemption, transferability, reserve access, upgrades, and emergency controls.
2. **Which control path protects holders best?** Decide whether holder protection primarily comes from Social/legal accountability, Decentralized governance, or Technical on-chain constraints.
3. **Which control path can still break the trade?** Preserve weak criteria as blockers or sizing constraints even when the pillar’s best criterion is strong.
4. **What should the next analyst trust, verify, or refuse to assume?** Return source-backed facts, unresolved gates, and the issuer-control map, not a narrative-only score.

The artifact should be named:

```text
tokens/<token-slug>/issuer-pillar-research.md
tokens/<token-slug>/raw/issuer-pillar-research.json
```

If the token is issued through a separate platform wrapper, produce both:

```text
tokens/<token-slug>/issuer-pillar-research.md
platforms/<platform-slug>/issuer-pillar-research.md
```

Example: a Securitize-issued RWA has an asset issuer and a platform issuer. Do not collapse them into one “issuer” unless the same party controls both economics and transfer/redemption plumbing.

## Research stance

Issuer research is not “find the company and summarize it.” It is a control-surface investigation.

The analyst must reconstruct all decisions the issuer or issuer-adjacent control plane can make that affect the holder:

- **Economic value:** reserve transfer, reserve composition, revenue distribution, fees, waterfall changes, NAV calculation, yield routing, redemption price, maturity treatment.
- **Business activity:** change of underlying strategy, collateral pool, service provider, fund mandate, custodian, bank account, SPV, or off-chain operator.
- **Technical implementation:** token upgrades, proxy admin changes, mint/burn permissions, pause/freeze/blacklist, redemption queue changes, oracle/accounting hooks, migration/runoff of previous versions.
- **Governance:** DAO process, multisig signer changes, quorum, vetoes, guardians, emergency councils, recentralization paths, governance-token holder/depositor conflict.
- **Partnerships:** exclusivity, funding lines, market maker dependency, custody arrangements, issuer-platform agreements, redemption agent, transfer agent, administrator, auditor, and oracle/data providers.

For each decision, capture:

- decision owner;
- execution mechanism;
- notice period or timelock;
- whether users can exit before it applies;
- holder impact if used badly;
- source evidence;
- whether the same control matters for Gearbox liquidation, unwind, or collateral eligibility.

## Required source hierarchy

Use primary sources first. Secondary summaries can guide the search, but they cannot carry the final claim unless no primary source is available and the limitation is explicit.

### Strong sources

- Issuer legal documents: terms, prospectus, offering memorandum, fund documents, trust/SPV documents, redemption policy, tokenholder agreement, risk disclosures.
- Regulator or registry records: license lookup, filing database, registration status, enforcement history, authorized activities, jurisdiction-specific public records.
- Official issuer docs: reserve reports, attestations, audit reports, proof-of-reserve pages, redemption docs, incident reports, governance docs.
- On-chain sources: verified contract code, proxy/admin slots, role assignments, multisig addresses, timelocks, DAO votes, event logs for mint/burn/pause/freeze/blacklist/upgrades.
- Governance sources: forum proposals, Snapshot/Tally/Agora/board votes, quorum rules, delegate distribution, emergency/guardian rules.
- Third-party assurance: top-tier audit reports, attestation firms, Credora/Steakhouse/rating reports, custodian or administrator confirmations.

### Weak sources

- Marketing pages without legal commitments.
- Blog posts that describe the product but not controls.
- Dune dashboards or DefiLlama pages with no source lineage.
- X threads unless used as leads or for public incident chronology.
- Aggregator token pages that do not identify issuer/admin/redemption authority.

### No-result proof

If a required source is missing, write the negative investigation as a fact:

```text
Searched: issuer docs, docs site, GitHub, Etherscan verified contracts, Snapshot/Tally, regulator registry, terms page, audit page.
No source found for: redemption priority during freeze.
Impact: cannot assume primary redemption is available for liquidation/unwind.
Gate: issuer_redemption_priority_missing.
```

No-source is a result. Silent omission is not.

## Step 1 — Define the issuer boundary

Start by drawing the issuer stack before scoring anything.

### Required questions

- What exactly is the asset being researched: ERC-20, vault share, PT, receipt token, fund token, stablecoin, tokenized security, wrapper, LP token, rebasing token, or points-bearing instrument?
- Who can mint it?
- Who can burn it?
- Who controls redemption into the backing asset or cash/settlement asset?
- Who controls the backing assets, bank/custody accounts, strategy assets, or off-chain claims?
- Who controls transfer restrictions, whitelist/blacklist/freeze, or compliance gates?
- Who controls upgrades and parameter changes?
- If the issuer and platform are different, where does responsibility transfer between them?
- If the token is a PT, which risks come from the underlying issuer and which come from the PT market/protocol?

### Required output: issuer-control map

```yaml
issuer_control_map:
  asset: "<token name / chain / address>"
  token_type: "erc20 | vault_share | pt | tokenized_security | stablecoin | wrapper | other"
  economic_issuer:
    name: "<entity / DAO / protocol>"
    evidence_ids: ["E-001"]
  platform_or_transfer_agent:
    name: "<entity or none>"
    evidence_ids: ["E-002"]
  onchain_admin:
    address: "0x..."
    type: "multisig | dao | timelock | eoa | immutable | unknown"
    evidence_ids: ["E-003"]
  redemption_controller:
    name_or_address: "<entity/address>"
    evidence_ids: ["E-004"]
  control_split:
    summary: "<one paragraph on who controls economics vs token plumbing>"
    unresolved_gates: []
```

### Hard failure cases

Mark issuer research `review_required` or `blocked` if any of these remain unknown:

- ultimate redemption controller;
- mint authority;
- freeze/blacklist/transfer-restriction authority for permissioned or issuer-controlled assets;
- proxy/admin authority for upgradeable core token contracts;
- legal entity or DAO with claimed economic responsibility.

## Step 2 — Decision inventory

Before criterion scoring, list issuer decisions that can affect the asset.

Use this format:

```yaml
issuer_decisions:
  - decision_id: "D-001"
    category: "economic_value | business_activity | technical_implementation | governance | partnership"
    decision: "Change reserve composition from T-bills to repo exposure"
    controller: "<entity/address/governance body>"
    mechanism: "board decision | DAO vote | multisig tx | contract call | legal terms update"
    notice_or_delay: "<timelock / notice / none / unknown>"
    holder_exit_before_effective: "yes | no | conditional | unknown"
    gearbox_relevance: "affects redemption value and liquidation exit"
    evidence_ids: ["E-010", "E-011"]
    unresolved_gate_ids: []
```

Minimum categories to cover:

- reserves or backing assets;
- redemption policy and settlement timing;
- transferability / whitelist / freeze / blacklist;
- upgrades and admin role changes;
- governance process changes;
- fees and yield distribution;
- custodian / bank / administrator changes;
- market-maker or liquidity-provider dependency;
- incident response powers.

If the issuer claims “fully decentralized” or “immutable,” prove the absence of these decisions with contract and governance evidence.

## Step 3 — Social criterion

Social asks whether society can reduce issuer risk through identity, regulation, and experience.

Do not score “Social” by brand familiarity. Score it by enforceability, accountability, and demonstrated operating capacity.

### Evidence to collect

#### Identity and accountability

- Legal entity name, jurisdiction, registration number, and operating entities.
- Parent/subsidiary/SPV structure if different entities issue, manage reserves, operate frontends, or serve as transfer agent.
- Doxxed founders/executives/directors and their roles.
- Multisig signer identities if the issuer is a multisig rather than a company.
- Contact and dispute paths: support, legal notices, registered agent, governing law.

#### Regulatory status

- Licenses, exemptions, registrations, notices, or agreements that authorize the issuer’s activity.
- Regulator name and registry URL, not only issuer claims.
- Supervision frequency if stated: audits, examinations, reporting cadence, reserve segregation requirements.
- Restrictions on eligible holders, transfer, geography, sanctions, leverage, redemption, or marketing.
- Enforcement or disciplinary history.

#### Financial and operational requirements

- Reserve segregation, bankruptcy remoteness, custody requirements, capital requirements.
- Attestation or audit cadence and reporting standard.
- Service providers: custodian, trustee, administrator, auditor, transfer agent, market maker.
- Insurance, indemnities, guarantee structures, or explicit absence of them.

#### Experience and legitimacy

- Years operating this asset or similar assets.
- AUM/TVL history and maximum historical outstanding supply.
- Prior incidents: depegs, delayed redemptions, freezes, exploits, legal disputes, reserve gaps, delayed attestations.
- Quality of incident response: disclosure speed, reimbursement, post-mortems, recurrence prevention.
- Public reputation from credible counterparties; ignore pure affiliate marketing.

### Social research procedure

1. Start with the issuer’s legal/terms docs and identify all named entities.
2. Verify each material entity in an independent registry or regulator source.
3. Match legal entities to on-chain/admin/platform roles.
4. Read redemption and risk disclosure sections before reading marketing materials.
5. Search for enforcement, sanctions, lawsuits, insolvency, depeg, freeze, and withdrawal-delay history.
6. Build a timeline of attestations/audits and check for missing periods.
7. Confirm whether regulations protect token holders specifically or only regulate the issuer generally.
8. Record which user has recourse: token holder, whitelisted investor, platform user, DAO participant, or no direct claimant.

### Social red flags

- Issuer identity unclear or only a brand name.
- Legal issuer differs from marketed issuer and responsibility is not explained.
- No public redemption terms.
- Terms allow unilateral reserve, fee, redemption, or eligibility changes without notice.
- Claims of regulation without registry proof.
- Regulation exists but does not cover the token activity.
- Attestations exist but reserve composition, liabilities, or methodology are incomplete.
- Prior incident with weak disclosure or no remediation.
- Multisig signer identities unknown and no DAO/timelock protection.

### Social rating notes

Use letter grades only as an internal rubric unless a published rating exists. Prefer a reasoned finding over false precision.

- **AA/A shape:** named and verified entity or accountable signer set; relevant regulation/supervision; clear redemption/legal terms; strong reserve segregation or enforceable holder claim; clean incident record; high-quality recurring attestations/audits.
- **BB/B shape:** identifiable issuer and plausible operating history, but weaker supervision, incomplete reserve/legal details, limited public attestations, or terms with broad discretion.
- **CC/C shape:** unknown issuer, unverifiable licenses, unclear redemption/legal claim, history of unresolved incidents, or terms that can remove holder value/exit without meaningful constraint.

## Step 4 — Decentralization criterion

Decentralization asks whether a broad governance process protects holders from issuer discretion.

This criterion is not automatically strong because a token has a DAO. The governance participants must be able to control the relevant issuer decisions, and their incentives must not obviously conflict with asset holders.

### Evidence to collect

#### Governance structure

- Governance body: DAO, foundation, company board, multisig, council, guardian, tokenholder vote.
- Governance documents: constitution, bylaws, forum rules, proposal lifecycle, emergency process.
- Voting system: Snapshot, Tally, on-chain governor, custom voting, multisig-only.
- Proposal lifecycle: discussion period, voting period, quorum, approval threshold, execution delay, timelock.
- Scope: which parameters/actions governance can actually control.

#### Power distribution

- Governance token holder distribution, top holders, delegates, insiders, treasury, market makers, exchanges.
- Delegation concentration and active voter concentration, not only token supply concentration.
- Multisig signer set, threshold, signer affiliations, signer rotation process.
- Emergency council or guardian powers and constraints.
- Veto, dual governance, depositor guardian, rage-quit, or withdrawal delay protections.

#### Governance behavior

- Last 10–20 material proposals.
- Turnout vs quorum.
- Evidence of contested votes or rubber-stamping.
- Parameter changes affecting issuance, redemption, fees, upgrades, collateral, or user rights.
- Emergency actions and whether post-hoc governance ratified them.
- Forum quality: active debate, risk analysis, transparent conflicts, implementation reviews.

#### Holder alignment

- Are governance voters the same economic group as token holders/depositors?
- Can governance extract value from token holders through fees, dilution, redemption queue, or parameter changes?
- Are there explicit depositor protections when voters and holders differ?
- Can holders exit before adverse governance changes become effective?

### Decentralization research procedure

1. Map the formal governance process from docs.
2. Verify the live governance system and contracts.
3. Identify which issuer decisions from Step 2 governance can control.
4. Measure holder/delegate/signer concentration using current on-chain data or governance dashboards.
5. Review recent proposals for issuer-relevant actions.
6. Check timelocks and emergency bypasses on-chain.
7. Decide whether governance is a protection mechanism, a disclosure mechanism, or mostly theater.

### Decentralization red flags

- DAO exists but core issuer/admin decisions remain with a company or EOA.
- Governance token is concentrated enough for one party or cartel to pass votes.
- Low participation makes quorum easy for insiders.
- Emergency council can bypass governance without narrow scope or post-action review.
- Multisig signers are mostly employees/affiliates and no timelock exists.
- Depositors/token holders cannot vote, veto, or exit before adverse changes.
- Recent governance changed user economics with little notice.
- Forum lacks implementation detail, risk review, or dissent.

### Decentralization rating notes

- **AA/A shape:** relevant decisions governed by broad, active, transparent governance; low unilateral control; timelocks; emergency powers narrow; depositor/holder protections exist; voters aligned with asset holders.
- **BB/B shape:** governance exists and controls some material decisions, but concentration, low participation, broad councils, or weak holder alignment limit protection.
- **CC/C shape:** governance is absent, irrelevant, captured, or bypassable for material issuer decisions.

## Step 5 — Technical criterion

Technical asks whether smart contracts embed holder protections directly on-chain.

For issuer research, “technical” is narrower than a full exploit audit. Focus on whether code limits issuer discretion and makes holder-affecting actions predictable, atomic, delayed, or impossible.

### Evidence to collect

#### Contract identity

- Canonical token address and all proxy/implementation addresses.
- Deployment chain(s) and bridge/wrapper contracts if cross-chain.
- Verified source code status.
- Contract standard and deviations: ERC-20, ERC-4626, ERC-7540, rebasing, permissioned token, PT, wrapper.
- Upgrade pattern: immutable, transparent proxy, UUPS, beacon, diamond, custom admin, clone, unknown.

#### Roles and permissions

- Owner/admin/proxy admin.
- Minter/burner roles and caps.
- Pauser/freezer/blacklister/whitelister roles.
- Transfer-restriction manager.
- Redemption queue/admin roles.
- Fee setter, oracle/accounting updater, rate setter, supply cap setter.
- Role admin role: who can grant/revoke each role.

#### Upgrade and parameter controls

- Timelock duration and whether all upgrades/parameter changes route through it.
- Multisig threshold and signer set for admin actions.
- DAO executor linkage.
- Emergency bypasses and their scope.
- Historical upgrades and parameter changes from event logs.
- Whether users can observe pending changes before execution.

#### Routine discretionary operations

- Does normal redemption require a team call?
- Does NAV/accounting update require a team call?
- Does mint/burn settlement require a human/admin transaction?
- Can the issuer halt transfers or redemptions during stress?
- Are there keeper/automation dependencies, and who can replace them?

#### Holder-protection mechanics

- Atomic deposit/redeem/withdraw paths.
- Preview functions and whether they can be stale or manipulated.
- Caps, rate limits, cooldowns, queues, withdrawal windows.
- On-chain proof of reserves/accounting, if any.
- Invariant checks around totalSupply, totalAssets, share price, NAV, redemption price.
- Recovery/migration path if a contract version is deprecated.

### Technical research procedure

1. Resolve canonical contracts from official docs and block explorers; reject unverified addresses unless corroborated.
2. Pull ABI/source and enumerate write functions with holder impact.
3. Extract role/admin ownership from chain state, not only docs.
4. Check proxy/admin slots and implementation history.
5. Trace whether admin powers route through multisig, timelock, DAO, or EOA.
6. Search event logs for upgrades, pauses, freezes, blacklists, mint/burn spikes, role changes, cap changes, accounting updates.
7. Compare docs’ stated protections against actual contract permissions.
8. Classify each holder-affecting action as impossible, delayed, multisig/DAO-controlled, EOA-controlled, or unknown.

### Minimum technical control table

```yaml
technical_controls:
  - control_id: "T-001"
    control: "upgrade implementation"
    current_authority: "0x... Safe 3/5"
    delay: "48h timelock | none | unknown"
    user_notice: "on-chain queued tx | docs notice | none | unknown"
    can_user_exit_before_effective: "yes | no | conditional | unknown"
    gearbox_relevance: "implementation can add transfer restrictions before liquidation"
    evidence_ids: ["E-100", "E-101"]
    finding: "acceptable | concern | blocker"
```

Required controls to cover:

- upgrade implementation;
- grant/revoke admin roles;
- mint;
- burn;
- pause transfers;
- freeze/blacklist address;
- change redemption terms or queue parameters;
- update accounting/NAV/share price source;
- change fees;
- migrate or sunset contract version.

### Technical red flags

- Unverified token or implementation source.
- Upgradeable proxy with EOA admin.
- Admin can mint, freeze, blacklist, or change redemption without timelock or narrow constraints.
- Role admin can grant itself broader powers.
- Emergency powers have no objective trigger, duration, or post-action reporting.
- Normal operations require discretionary team calls in stress conditions.
- Docs claim immutability but proxy/admin slots show upgradeability.
- Contract can block Gearbox liquidation/unwind path for the Credit Account or liquidator.

### Technical rating notes

- **AA/A shape:** immutable or strongly timelocked code; narrow roles; holder-affecting operations impossible or delayed; routine operations atomic or automation-backed; verified source; historical admin actions match docs.
- **BB/B shape:** upgrade/admin powers exist but are multisig/DAO-controlled, visible, and historically disciplined; some discretionary operations remain but are documented.
- **CC/C shape:** EOA/broad admin powers, unverified contracts, unrestricted freeze/blacklist/mint/redemption changes, or unknown control path.

## Step 6 — Pillar synthesis

The Steakhouse-style Issuer pillar uses the **best** of Social, Decentralization, and Technical criteria. Use that as the rubric, but do not let it erase risk mechanics.

### Synthesis rules

1. Assign each criterion a finding: `strong`, `acceptable`, `weak`, `blocker`, or `unknown`.
2. Identify the strongest criterion and explain why it can carry issuer confidence.
3. Identify each weak criterion and state whether it is:
   - irrelevant to this asset’s holder outcome;
   - relevant but mitigated by another criterion;
   - relevant and must become a blocker/sizing constraint.
4. Convert unresolved critical facts into gates.
5. Translate issuer findings into Gearbox-specific implications.

### Gearbox-specific implications to always state

- Can a Credit Account hold the asset without whitelist/transfer restrictions breaking operations?
- Can Gearbox or a liquidator transfer/sell/redeem the asset during stress?
- Can issuer actions change collateral value faster than governance/oracle/liquidation can react?
- Does the issuer have discretionary freeze/blacklist power over borrower, Credit Account, pool, liquidator, or router addresses?
- Does redemption depend on KYC, user identity, minimum size, cutoff time, queue, notice period, or off-chain approval?
- Does the issuer’s legal/regulatory framework protect the actual Gearbox holder path or only direct whitelisted holders?
- What should be assumed in quantitative underwriting: immediate redemption, delayed redemption, secondary-only exit, haircut, or no reliable exit?

### Required synthesis format

```yaml
issuer_pillar_result:
  pillar: "asset_issuer"
  steakhouse_reference: "Asset Rating Layer 1 / Issuer Pillar 1"
  issuer_definition: "organization/control plane with ultimate control over issuance and redemption"
  criteria:
    social:
      finding: "strong | acceptable | weak | blocker | unknown"
      evidence_ids: []
      summary: ""
    decentralization:
      finding: "strong | acceptable | weak | blocker | unknown"
      evidence_ids: []
      summary: ""
    technical:
      finding: "strong | acceptable | weak | blocker | unknown"
      evidence_ids: []
      summary: ""
  best_criterion: "social | decentralization | technical | none"
  pillar_finding: "strong | acceptable | weak | blocker | unknown"
  weak_criterion_implications:
    - criterion: "technical"
      implication: "freeze role creates liquidation-transfer blocker unless addresses are confirmed eligible"
      gate_id: "issuer_freeze_transfer_path_unverified"
  gearbox_implications:
    hold_eligibility: "pass | review_required | blocked"
    liquidation_unwind: "pass | review_required | blocked"
    redemption_assumption: "immediate | delayed | secondary_only | unavailable | unknown"
    oracle_accounting_dependency: "low | medium | high | unknown"
  unresolved_gates: []
```

## Step 7 — Analyst report structure

The human-readable page should be short enough to review but detailed enough to audit.

Use this outline:

```text
# Issuer pillar research — <asset>

## Decision
- Pillar finding:
- Best supporting criterion:
- Gearbox consequence:
- Open blockers:

## Issuer-control map
- Economic issuer:
- Token/platform issuer:
- On-chain admin:
- Redemption controller:
- Transfer/freeze controller:
- Control split:

## Decision inventory
- Economic value decisions:
- Business activity decisions:
- Technical implementation decisions:
- Governance decisions:
- Partnership/service-provider decisions:

## Social criterion
- Finding:
- Evidence:
- Red flags:
- Missing facts:

## Decentralization criterion
- Finding:
- Evidence:
- Red flags:
- Missing facts:

## Technical criterion
- Finding:
- Evidence:
- Red flags:
- Missing facts:

## Gearbox path impact
- Holding path:
- Transfer/liquidation path:
- Redemption/unwind path:
- Quantitative-underwriting assumption:

## Source ledger
- E-001 ...
```

## Step 8 — Integration with the asset workflow

Issuer-pillar research should feed multiple stages, not sit as appendix text.

### S1 general asset mining

S1 must collect raw issuer facts:

- issuer-control map;
- source ledger;
- legal/regulatory documents;
- contract/admin evidence;
- governance evidence;
- decision inventory;
- unresolved gates.

S1 should not produce a final pillar rating unless enough sources exist. It should produce `unknown` or `review_required` explicitly when sources are missing.

### S2 asset-risk analyst report

S2 converts S1 evidence into:

- Social/Decentralization/Technical criterion findings;
- best-criterion rationale;
- weak-criterion implications;
- holder and Gearbox path impact;
- issuer-driven red flags for Credit Risk, Operational Risk, and Market layer follow-up.

### S6 quantitative underwriting

S6 must consume issuer outputs before ROI/VaR/expected-shortfall assumptions.

Issuer gates can change quantitative assumptions:

- no confirmed redemption right → no immediate-redemption base case;
- freeze/blacklist risk → add liquidation-transfer blocker or stress haircut;
- delayed redemption window → model time-to-cash, borrow-cost drag, and liquidity haircut;
- discretionary NAV/accounting updates → add accounting/oracle stale-value stress;
- unclear legal claim → no recovery-rate assumption above zero without evidence.

## Quick checklist

Before marking issuer-pillar research complete, verify:

- [ ] Economic issuer identified.
- [ ] Platform/transfer agent identified or explicitly not applicable.
- [ ] Mint/burn authority identified.
- [ ] Redemption controller and redemption terms identified.
- [ ] Freeze/blacklist/transfer-restriction authority identified.
- [ ] Proxy/admin/upgrade authority identified.
- [ ] Social evidence includes entity, jurisdiction, regulatory/registry status, and accountability path.
- [ ] Decentralization evidence includes governance scope, participation/concentration, quorum/threshold, and timelock/emergency rules.
- [ ] Technical evidence includes verified contracts, roles, admin path, and holder-affecting write functions.
- [ ] Decision inventory covers economic, business, technical, governance, and partnership changes.
- [ ] Weak criteria are preserved as implications, not hidden by the best-of rule.
- [ ] Gearbox hold, liquidation, and redemption paths have explicit pass/review/block status.
- [ ] Every material claim has `evidence_ids` or `unresolved_gate_ids`.

## Common failure mode

Bad issuer research says:

> “Issuer is reputable and regulated; risk low.”

Good issuer research says:

> “Social is strong because entity, supervision, reserve segregation, and reporting are sourced. Technical is weak because the proxy admin can freeze transfers through a 3/5 Safe with no timelock. The Steakhouse-style Issuer pillar may be carried by Social, but Gearbox liquidation remains `review_required` until Credit Account, router, and liquidator addresses are confirmed eligible and freeze/blacklist treatment is known.”
