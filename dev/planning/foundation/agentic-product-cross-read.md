# Cross-read: Gearbox Agentic Product vs Front Knowledge Base

> **Archive note.** This is a pre-merge planning artifact. References to deleted `JTBDs/`, `User flows/`, Tier 4 user-flow, Tier 5 UI-primitive, `Multi-position`, or placeholder RWA structures are historical source-state references. Current canonical navigation lives in `../../README.md`, `../../CLAUDE.md`, and `../../user/flows/`.

Date: 2026-04-29

## Source scope

Primary project reviewed: `projects/gearbox-agentic-product/`

Primary comparison target: `projects/front-knowledge-base/dev/planning/foundation/deep-analysis-report.md`

Key files read from the agentic product project:

- `README.md`
- `STATUS.md`
- `synthesis/staged-agent-architecture.md`
- `synthesis/backend-datatype-stage-mapping.md`
- `synthesis/loss-vectors-summary.md`
- `synthesis/call-analysis-and-action-items.md`
- `outputs/agentic-data-flow/00.introduction.md`
- `outputs/agentic-data-flow/03. Stage 2b: Analyze — CA Due Diligence.md`
- `outputs/agentic-data-flow/04. Stage 3: Propose — Action selection and transaction construction.md`
- `outputs/agentic-data-flow/05. Stage 4: Preview — Universal transaction validation.md`
- `outputs/agentic-data-flow/06. Stage 5: Execute — Approval and submission.md`
- `outputs/agentic-data-flow/07. Stage 6a: Monitor — LP.md`
- `outputs/agentic-data-flow/08. Stage 6b: Monitor — CA.md`
- `outputs/agentic-data-flow/11. Appendix C: Computed Data.md`
- `outputs/agentic-data-flow/12. Appendix D: RWA and KYC-specific Loss Vector Summary.md`
- `outputs/agentic-data-flow/13. Summary.md`

## Executive finding

The agentic product project answers several of the unclear points from the front knowledge base analysis. It is more implementation-facing than the front vault. The front vault describes the user/product model; the agentic project describes the staged agent runtime, MCP/SDK surface, and backend data gaps.

The strongest answer from the agentic project is that the correct shared architecture is:

```text
Discover → Analyze → Propose → Preview → Execute → Monitor
```

with these rules:

- Preview failure loops back to Propose.
- Monitoring events loop back to Analyze.
- Agent path: agent → MCP server → Gearbox SDK.
- Frontend path: frontend → Gearbox SDK.
- Both paths consume the same canonical domain types.
- Preview is the universal security gate: the same bytes previewed must be the same bytes executed.

The main unresolved issue remains the same: many of the needed types are named and justified, but not implemented or centrally registered in a frontend-facing source of truth.

## Question-by-question resolution

### 1. What is the canonical product/runtime design?

**Status: answered.**

The agentic project confirms that the front knowledge base is aligned with the intended agentic architecture. The six-stage loop is not only a product narrative; it is the intended SDK/MCP/frontend runtime model.

The agentic project adds a stronger implementation rule:

> one SDK type powers the API response, the same type is exposed as an MCP tool result, and the same type is renderable as a UI component.

This answers the earlier uncertainty around whether the front vault is only product framing or a real implementation model. It is meant to become the shared product/runtime schema.

### 2. Is `TransactionPreview` defined anywhere?

**Status: partially answered.**

The agentic project gives stronger Preview rules than the front vault, but still marks the concrete backend type as missing.

Canonical preview rule:

- `sdk.previewTransaction(rawTx)` is the universal method.
- Preview simulates exact unsigned bytes.
- The exact previewed transaction package is what Execute signs/submits.
- Failed preview returns to Propose, not Analyze.

Preview output shape in `synthesis/staged-agent-architecture.md`:

```ts
interface TransactionPreview {
  success: boolean
  warnings: string[]
  healthFactor?: number
  gasEstimate?: string
  actions: Array<{
    title: string
    description: string
    protocol?: string
  }>
  balanceChanges: Array<{
    token: TokenRef
    delta: string
    direction: "in" | "out"
  }>
  routes?: Array<{
    tokenIn: TokenRef
    tokenOut: TokenRef
    amountIn: string
    expectedOut: string
    priceImpactBps?: number
    dex?: string
  }>
  exitInfo?: {
    hasDelayedWithdrawal: boolean
    zeroSlippageAvailable: boolean
  }
}
```

Stage-specific preview fields are also listed:

- LP preview: expected shares, share price, projected pool TVL, concentration percentage, deviation from proposal, gas estimate, warnings, calldata.
- CA preview: simulated Health Factor after open, position value USD, actual leverage, swap impact, token balances after open, deviation from proposal, gas estimate, warnings, multicall data.

**Remaining gap:** `TransactionPreview`, `PreviewAction`, `BalanceChange`, `PreviewRoute`, `ExitInfo`, `RawTx`, and `ExecutionReadyAction` are still marked missing in `types_.ts`.

**Implication for front vault:** The stage-handoff and Preview details should be folded into the canonical loop, execution boundary, and backend requirements rather than invented from scratch.

### 3. Is the agent/bot boundary clarified?

**Status: partially answered.**

The agentic project makes the execution split clearer:

| Mode | Signer | Best for |
|---|---|---|
| Human-in-the-Loop | human wallet / Safe signer | high-value positions, institutional controls, initial trust building |
| Bot Execution | bot signer with bounded permissions | automated rebalancing, liquidation protection, routine management |

Boundaries established:

- SDK builds transactions but never signs them.
- Execution mode changes who signs, not what gets built or previewed.
- Both execution modes use the same Propose and Preview stages.
- Bot execution remains permission-bounded.
- Example bot permissions: `ADD_COLLATERAL`, `INCREASE_DEBT`, `DECREASE_DEBT`, `WITHDRAW_COLLATERAL`, `UPDATE_QUOTA`, `EXTERNAL_CALLS`.
- Protocol still enforces solvency and permission boundaries.

**Remaining gap:** the frontend/product policy layer is still not complete. The agentic project does not fully answer:

- Which actions are allowed for autonomous bots by product policy?
- Which actions require Safe/human approval regardless of permissions?
- How user-defined thresholds are persisted and enforced.
- How emergency policy differs from routine management.
- How KYC-gated/RWA positions constrain bot execution.

Important RWA-specific answer: the CA due-diligence doc says SecuritizeWallet blocks bot permissions and KYC-gated CMs route operations through SecuritizeKYCFactory → SecuritizeWallet → CreditFacade. That means RWA/KYC products cannot be treated as ordinary bot-managed positions.

**Implication for front vault:** The execution-boundary rules should start from the agentic project's execution modes and add product-policy rows in the session / entry-point layer.

### 4. Are schemas/data contracts clarified?

**Status: strongly clarified, not fully solved.**

The agentic project contains the closest thing to the missing schema registry: `synthesis/backend-datatype-stage-mapping.md`.

It maps each data group to:

- human-readable data name,
- agent story,
- technical type/field reference,
- coverage in `types_.ts`.

High-level coverage summary:

| Stage | Strong coverage already present | Largest missing pieces |
|---|---|---|
| Discover | `Opportunity`, `PoolOpportunity`, `StrategyOpportunity`, `TokenRef`, `YieldBreakdown`, `LeveragedYieldBreakdown`, collateral types | discover-query input type |
| Analyze | opportunity, yield, collateral, token primitives | `CuratorProfile`, history series, governance/event feed, oracle metadata, RWA profiles |
| Propose | no canonical backend types yet | `RawTx`, proposed-action envelope, route result |
| Preview | no canonical backend types yet | `TransactionPreview`, decoded actions, balance changes, route detail, exit info |
| Execute | no canonical backend types yet | execution mode, reviewer payload, bot permission state |
| Monitor | `UserPoolPosition`, `UserStrategyPosition`, `UserCollateral`, `PnlBreakdown` | alerts, Health Factor attribution, delayed-withdrawal state, oracle freshness, emergency state |

Highest-priority missing types listed by the agentic project:

- `CuratorProfile`
- discover-query input type
- `HistoricalMetricPoint` / `MetricSeries<T>`
- `GovernanceChange`
- `EventFeedItem`
- `RawTx`
- `ProposedAction`
- `TransactionPreview`
- `PreviewAction`
- `BalanceChange`
- `PreviewRoute`
- `ExecutionReadyAction`
- `MonitorAlert`

Next layer:

- `RwaAssetProfile`
- `RwaComplianceProfile`
- oracle / pricing metadata types
- insurance snapshot type
- `HealthFactorAttribution`
- `DelayedWithdrawalState`
- `ClaimableWithdrawal`
- `BotPermissionState`

**Implication for front vault:** The stage-handoff vocabulary should import this stage mapping and turn it into frontend-readable requirements with status, source, freshness, owner, and used-by surfaces.

### 5. Are RWA/KYC specifics clearer?

**Status: much clearer.**

The agentic project gives a concrete RWA/KYC loss-vector model.

RWA/KYC-specific risks:

- frozen account bad debt,
- liquidator scarcity,
- off-chain asset default,
- redemption lockout,
- compliance-layer immobilization,
- investor reassignment,
- operational restrictions,
- KYC expiry.

Fields needed:

- `RwaComplianceProfile.transferRestrictionType`
- `RwaComplianceProfile.freezeCapability`
- `RwaComplianceProfile.freezeAuthority`
- `RwaComplianceProfile.investorReassignmentRisk`
- `RwaComplianceProfile.whitelistedLiquidatorCount`
- `RwaAssetProfile.redemptionWindows`
- `RwaAssetProfile.redemptionNoticeDeadline`
- `RwaAssetProfile.redemptionMechanism`
- secondary-market-liquidity field
- KYC operation routing field
- account-level freeze status
- investor-registry state
- KYC-validity field

RWA/KYC operation routing answer:

- KYC-gated CMs route operations through SecuritizeKYCFactory → SecuritizeWallet → CreditFacade.
- The agent cannot call CreditFacade directly.
- SecuritizeWallet blocks bot permissions.

**Implication for front vault:** The empty `User flows/rwa-leverage.md` can be written as a Credit Account variant with extra compliance and redemption constraints. It does not need to become a separate product universe.

### 6. Are monitoring and emergency fields clearer?

**Status: clearer.**

The agentic project decomposes CA monitoring into the exact raw facts needed to explain Health Factor movement:

- Health Factor,
- total value USD,
- TWV USD,
- total debt USD,
- debt breakdown,
- per-token balances and per-token value,
- per-token quota,
- leverage,
- Health Factor history,
- total-value history.

It also names the missing Health Factor explanation primitive:

- `HealthFactorAttribution`

Factors to attribute:

- collateral price movement,
- LT ramping,
- interest accrual,
- quota interest,
- forbidden token safe pricing,
- oracle staleness.

Emergency state bundle:

- facade paused status,
- forbidden tokens affecting the position,
- loss policy status,
- emergency liquidator active.

LP monitoring fields:

- APY breakdown history,
- share price/exchange rate,
- utilization,
- TVL,
- insurance fund balance change,
- parameter changes,
- quota composition shift,
- new CMs added,
- pending governance changes,
- frozen account/debt deltas for RWA pools.

**Implication for front vault:** The multi-position/portfolio flow should use these as its triage inputs: worst Health Factor, Health Factor attribution, emergency state, delayed withdrawals, RWA freeze/KYC state, and correlated exposure shifts.

### 7. Are thresholds resolved?

**Status: not resolved.**

The agentic project confirms that Health Factor is central, but it does not define one canonical threshold model.

It gives examples:

- below 1 = liquidation,
- agent threshold example: 1.3,
- preview warning example: HF 1.08 below 1.1 threshold.

It also states the agent compares Health Factor to its own threshold. That implies thresholds are partly user- or agent-policy-specific, not only protocol facts.

**Implication for front vault:** The previous threshold recommendation remains valid. The front vault should define threshold classes:

| Threshold class | Owner | Example |
|---|---|---|
| Protocol fact | protocol | HF ≤ 1 means liquidatable |
| Product default warning | frontend/product | red below 1.1; yellow below 1.3 |
| Preview hard reject | product / policy | reject below configured floor |
| User-configurable policy | user / agent config | maintain HF above 1.3 |
| Strategy recommendation band | agent policy | only increase leverage above a higher comfort threshold |

The agentic project does not provide final numeric values beyond examples.

### 8. Are data requirements sliced better?

**Status: yes, enough to restructure.**

The agentic project organizes data by stage and by agent question. This is more buildable than the front vault's mixed `Data requirements and to-dos.md`.

The practical slice model should become:

1. Discover handoff — opportunity scan types.
2. Analyze handoff — due diligence facts, history, curator, governance, oracle, RWA profiles.
3. Propose handoff — `ProposedAction`, `RawTx`, route result.
4. Preview handoff — `TransactionPreview`, deltas, warnings, route, calldata, execution-ready handoff.
5. Execute handoff — execution mode, verifier/reviewer payload, bot permission state.
6. Monitor handoff — position state, attribution, alerts, emergency state, delayed withdrawals.
7. RWA/KYC extensions — compliance profile, asset profile, account state, redemption schedule.

This directly answers the earlier weakness: `Data requirements and to-dos.md` should be organized by vertical stage handoffs, not by loose backlog themes.

## Net change to the previous front analysis

### Previous unclear point → current answer

| Previous unclear point | Answer from agentic product | Remaining unresolved part |
|---|---|---|
| Is the six-stage loop only product framing? | No. It is the canonical SDK/MCP/frontend runtime loop. | Need one canonical front source that imports this. |
| Is Preview defined? | Partially. Universal `sdk.previewTransaction(rawTx)`, same bytes previewed/executed, concrete preview fields listed. | Backend types still missing. |
| What is `TransactionPreview`? | A preview verdict with warnings, Health Factor, gas, decoded actions, balance changes, route details, exit info. | Needs final type registry and frontend rendering contract. |
| What is the agent/bot boundary? | SDK builds, never signs. Humans or bounded bots sign. Same Propose/Preview path for both. | Product policy and user-configurable limits still missing. |
| Are RWA risks concrete? | Yes. Freeze, liquidator whitelist, off-chain asset, redemption, reassignment, KYC expiry, blocked bot permissions. | Dedicated RWA user flow still missing in front vault. |
| How should monitoring explain Health Factor changes? | Use raw components and define `HealthFactorAttribution`. | Type missing; frontend explanation format missing. |
| Are thresholds canonical? | No. Only examples exist. | Need canonical threshold taxonomy and owner. |
| Are stage handoffs listed? | Yes, via backend datatype stage mapping. | Need frontend-readable stage-handoff vocabulary in the canonical docs. |

## Recommended next edits to `projects/front-knowledge-base/`

1. Fold stage-handoff vocabulary from `projects/gearbox-agentic-product/synthesis/backend-datatype-stage-mapping.md` into the canonical loop and backend requirements.

2. Define the Preview gate using the agentic project's `TransactionPreview` shape plus the LP/CA preview-specific fields.

3. Define execution-boundary rules in the entry-point layer from the agentic execution-mode model, adding product-policy rows for human approval, bot permission scope, emergency behavior, and KYC/RWA restrictions.

4. Fill `User flows/rwa-leverage.md` as a CA operator variant:
   - Analyze: RWA asset/compliance profile.
   - Propose: operation routing through KYC factory/wallet.
   - Preview: freeze/KYC/redemption/secondary-liquidity checks.
   - Execute: human or KYC-compatible route; ordinary bot execution blocked where applicable.
   - Monitor: own frozen status, investor registry status, KYC validity, redemption windows.

5. Keep thresholds as an open product decision. The agentic project confirms the taxonomy need but does not settle the numeric bands.

## Bottom line

The agentic product project turns many of the front vault's implicit ideas into stage contracts and data gaps. It should be treated as the implementation companion to the front knowledge base.

What it resolves:

- canonical runtime loop,
- SDK/MCP/frontend shared type principle,
- Preview as security gate,
- concrete Preview field set,
- execution mode split,
- RWA/KYC risk fields,
- monitoring/Health Factor attribution inputs,
- stage-based data slicing.

What it does not resolve:

- final threshold numbers,
- final backend type definitions,
- frontend component ownership,
- product policy for autonomous bot execution,
- the missing front-facing RWA and multi-position flows.
