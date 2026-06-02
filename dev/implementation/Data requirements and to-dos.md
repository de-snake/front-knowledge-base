# User scenario map

This is the single human implementation handoff.

It answers one question:

> When the user is in a scenario, what do they ask or click, what must the agent check, and what should the user get back?

This file is not a schema, glossary, or UI taxonomy. It is a scenario map for product, frontend, backend, and agent work.

## Scenario map

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
│  User gets back:
│    1. Ranked pool list:
│       pool name, expected return, main reason to choose / avoid,
│       visible watch flags, and missing data if any.
│
│    2. Selected pool detail:
│       why this pool fits or does not fit, current utilization / liquidity,
│       collateral exposure, curator notes, oracle notes, pending changes.
│
│    3. Deposit proposal:
│       deposit this pool / split between pools / skip / keep reserve.
│
│    4. Transaction preview before signing:
│       exact deposit transaction, before → after position state,
│       warnings, approval method, expiry.
│
│    5. Execution result:
│       transaction status and new position baseline for monitoring.
│
│  Main response shape:
│    ranked pool list → pool detail → deposit proposal → transaction preview.
│
└─ Scenario B: user wants to open a Credit Account

   User asks / clicks:
     “Find a leveraged strategy.”
     “Open this strategy safely.”

   Agent checks:
     strategy economics, leverage range, liquidation risk, exit route,
     Credit Manager rules, oracle setup, allowed collateral,
     route / swap quote, pending governance changes,
     issuer-controlled asset branch if relevant.

   User gets back:
     1. Ranked strategy list:
        strategy name, expected return, leverage range, main risk,
        visible watch flags, and missing data if any.

     2. Selected strategy detail:
        economics, liquidation safety, exit feasibility,
        Credit Manager limits, oracle notes, route notes.

     3. Open-position proposal:
        strategy, size, target leverage, route, reserve amount, skip reason if skipped.

     4. Transaction preview before signing:
        exact open + borrow + swap multicall,
        before → after HF / debt / equity / collateral,
        warnings, approval method, expiry.

     5. Execution result:
        transaction status and new Credit Account baseline for monitoring.

   Main response shape:
     ranked strategy list → strategy detail → open-position proposal → multicall preview.
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
│  User gets back:
│    1. Short position status:
│       hold / watch / review / exit, with the top reasons.
│
│    2. Change explanation:
│       what changed since the original thesis or last monitoring baseline.
│
│    3. Proposed next step if needed:
│       hold, top up, partial exit, full exit, or review missing data.
│
│    4. Transaction preview before any top-up or exit:
│       exact transaction, before → after position state, warnings, approval method, expiry.
│
│    5. Execution result after action:
│       transaction status and updated monitoring baseline.
│
│  Main response shape:
│    position status → change explanation → optional action → transaction preview.
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

   User gets back:
     1. Short account status:
        safe / watch / review / act now / blocked, with the top reasons.

     2. Change explanation:
        safety, return, rule, oracle, and issuer-state changes since baseline.

     3. Proposed next step:
        add collateral, reduce leverage, increase leverage, claim, partial exit,
        full exit, hold, or review missing data.

     4. Transaction preview before signing:
        exact multicall, before → after HF / leverage / debt / equity / collateral,
        warnings, approval method, expiry.

     5. Execution result after action:
        transaction status and updated monitoring baseline.

   Main response shape:
     account status → reasoned next step → multicall preview.
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
│  User gets back:
│    1. Emergency status:
│       what is unsafe and why.
│
│    2. One stabilizing proposal:
│       usually add collateral or reduce leverage, with exact amount / target.
│
│    3. Transaction preview before execution:
│       required even in emergency.
│
│    4. Execution result after action.
│
│  Main response shape:
│    emergency status → one stabilizing proposal → transaction preview.
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

   User gets back:
     1. Visible issuer / eligibility status:
        ordinary / restricted / human-review / blocked.

     2. Reason:
        exact issuer, KYC, freeze, transferability, redemption, or liquidation-depth issue.

     3. Proposed next step only if required issuer state is known.

     4. Transaction preview before execution.

   Main response shape:
     issuer-state warning inside the normal LP or Credit Account flow.
```

## Build order implied by the scenario map

1. **Transaction preview first**
   - Every state-changing action depends on it.
   - If the preview is weak, execution is unsafe.

2. **Missing / stale / source-state visibility**
   - The user must see when data is missing or stale instead of getting a fake safe answer.

3. **Monitoring answers**
   - LP and Credit Account users need a clear “is this still okay?” answer before polished discovery matters.

4. **Issuer-controlled asset branch**
   - Tokenized-security / KYC / freeze / redemption state must block or route actions correctly.

5. **Opportunity discovery**
   - Ranking pools and strategies is useful, but less urgent than safe preview and monitoring.

6. **Execution history**
   - Needed for continuity and reporting after actions happen.

## What this PR does and does not do

This PR defines the scenario map above.

It does **not** implement:

- backend APIs
- database tables
- indexers
- frontend components
- transaction execution

A builder should be able to read this file and say:

> “For each user scenario, I understand what the user asks, what the agent must check, what response the user receives, and what should be built first.”
