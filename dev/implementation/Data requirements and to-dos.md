# User scenario map

This is the human implementation handoff.

It answers one question:

> When the user arrives in a scenario, what do they ask for, what must the agent check, and what format should the user get back?

This file is not a database schema. It is the product contract that backend, frontend, and agent work should serve.

## Output formats

Use these names consistently.

**Glance card**

The first answer. One screen. No deep tables.

Contains:

- plain answer: `good`, `watch`, `review`, `act now`, or `blocked`
- 2–4 reasons
- top missing / stale data, if any
- next best action

**Analyze panel**

Expandable evidence behind the Glance card.

Contains:

- what changed
- current facts
- why the agent believes the answer
- what is unknown
- source timestamps

**Action card**

A non-transactional proposal.

Contains:

- action type
- amount / target
- route, if relevant
- why this action
- what policy or user approval is still missing

**Preview card**

The transaction safety screen. This is required before any Execute.

Contains:

- exact transaction package
- before → after state
- gas / price-impact / slippage warnings
- blocking warnings
- expiry time
- approval mode: human click, Safe signing, or scoped bot

**Receipt card**

Post-execution result.

Contains:

- tx hash / status
- what changed
- any failure reason
- new monitoring baseline

**Alert card**

Monitoring ping.

Contains:

- what changed
- severity
- affected position
- recommended next step

## Scenario diagram

```text
USER HAS NO POSITION

├─ Scenario A: user wants to deposit as LP
│
│  User asks / clicks:
│    “Where should I put this capital?”
│    “Compare Gearbox pools for me.”
│
│  Agent checks:
│    pool APY, incentives, utilization, TVL, withdrawal conditions,
│    collateral exposure, oracle setup, curator track record,
│    pending governance / parameter changes, existing portfolio overlap.
│
│  User gets:
│    1. Glance card: ranked pool options + top reason to pick / avoid each.
│    2. Analyze panel: evidence for selected pools.
│    3. Action card: deposit / split / skip / keep reserve.
│    4. Preview card: exact deposit transaction and before → after state.
│    5. Receipt card: tx result and new LP monitoring baseline.
│
│  Main user-facing format:
│    ranked opportunity cards → selected opportunity detail → transaction preview.
│
└─ Scenario B: user wants to open a Credit Account

   User asks / clicks:
     “Find a leveraged strategy.”
     “Open this strategy safely.”

   Agent checks:
     strategy economics, leverage range, liquidation risk, exit route,
     Credit Manager rules, oracle setup, allowed collateral,
     route / swap quote, pending governance changes, issuer-controlled asset branch if relevant.

   User gets:
     1. Glance card: best strategy candidates + risk label.
     2. Analyze panel: economics, safety, exit, manager/rule checks.
     3. Action card: open_ca / skip / reserve, with leverage and route.
     4. Preview card: exact open + borrow + swap multicall before execution.
     5. Receipt card: tx result and new Credit Account monitoring baseline.

   Main user-facing format:
     strategy cards → selected strategy detail → multicall preview.
```

```text
USER ALREADY HAS A POSITION

├─ Scenario C: user monitors an LP position
│
│  User asks / clicks:
│    “Is my pool position still okay?”
│    “Should I add, hold, or exit?”
│
│  Agent checks:
│    current value, APY drift, utilization drift, TVL / liquidity,
│    withdrawal conditions, collateral exposure, oracle changes,
│    curator / governance changes, issuer-controlled branch if relevant.
│
│  User gets:
│    1. Glance card: hold / watch / review / exit signal.
│    2. Analyze panel: what changed since baseline.
│    3. Action card if needed: top up / partial exit / full exit / hold.
│    4. Preview card before any top-up or exit transaction.
│    5. Receipt card after execution.
│
│  Main user-facing format:
│    position health card → change explanation → optional action preview.
│
└─ Scenario D: user monitors a Credit Account

   User asks / clicks:
     “Is my Credit Account safe?”
     “Should I add collateral, reduce leverage, claim, or exit?”

   Agent checks:
     Health Factor, leverage, equity, debt, collateral composition,
     liquidation thresholds, oracle freshness, borrow cost, rewards,
     delayed withdrawals / claims, Credit Manager rules,
     pending governance changes, issuer / KYC / freeze / redemption state when relevant.

   User gets:
     1. Glance card: safe / watch / review / act now / blocked.
     2. Analyze panel: safety, return, rule, oracle, and issuer-state explanation.
     3. Action card: add collateral / reduce leverage / increase leverage / claim / partial exit / full exit.
     4. Preview card: exact multicall and before → after HF, debt, equity, collateral.
     5. Receipt card after execution.

   Main user-facing format:
     Credit Account health card → reasoned action card → multicall preview.
```

```text
SPECIAL BRANCHES

├─ Emergency mode
│
│  When it triggers:
│    The user or monitoring state says immediate safety action may be needed.
│
│  User asks / clicks:
│    “Stabilize this now.”
│    “What is the fastest safe action?”
│
│  Agent checks:
│    current HF / debt / collateral, user safety floor, available collateral,
│    repay route, price impact, bot permissions, and whether action improves safety.
│
│  User gets:
│    1. Glance card: emergency summary.
│    2. One Action card only: usually add collateral or reduce leverage.
│    3. Preview card: required before execution, even in emergency.
│    4. Receipt card after execution.
│
│  Main user-facing format:
│    emergency card → one stabilizing action → preview.
│
└─ Issuer-controlled / tokenized-security asset branch

   When it triggers:
     A pool, strategy, or Credit Account touches tokenized securities,
     issuer-controlled collateral, redemption-window assets, freezeable assets,
     or compliance-gated assets.

   Agent checks:
     issuer state, KYC / eligibility validity, own freeze status,
     transfer restrictions, redemption / claim readiness,
     eligible-liquidator depth, and whether automation is allowed.

   User gets:
     1. Glance card: ordinary / restricted / human-review / blocked.
     2. Analyze panel: exact issuer or eligibility reason.
     3. Action card only if the required issuer state is known.
     4. Preview card before execution.

   Main user-facing format:
     compliance / issuer-state banner inside the normal LP or Credit Account flow.
```

## Build order that follows from the diagram

1. **Preview card first**
   - Every state-changing action depends on it.
   - If Preview is weak, Execute is unsafe.

2. **Unknown / stale / source labels**
   - The agent must show when data is missing instead of pretending the position is safe.

3. **Monitoring cards**
   - LP and Credit Account users need a clear “is this still okay?” answer.

4. **Issuer-controlled asset branch**
   - Tokenized-security / KYC / freeze / redemption state must block or route actions correctly.

5. **Opportunity cards**
   - Ranking pools and strategies is useful, but less urgent than safe Preview and monitoring.

6. **Receipts and history**
   - Needed for continuity and reporting after actions happen.

## What this PR does and does not do

This PR defines the product-facing contract above.

It does **not** implement:

- backend APIs
- database tables
- indexers
- frontend components
- transaction execution

A builder should be able to read this file and say:

> “These are the screens/cards we need, these are the checks behind each scenario, and this is the order we should build them in.”
