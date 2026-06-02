# Position risk and monitoring

Monitoring exists because a Gearbox position can become materially different from the position the user originally accepted. The agent's job is not to apply universal ok / watch / review / act numbers. The agent's job is to understand the position, the user's mandate, the asset properties, and the available action paths well enough to choose or request appropriate monitoring thresholds.

## Core rule

Do not invent default risk thresholds for the user.

If a required user policy is missing, the agent should do one of three things:

1. ask the user to set the policy;
2. continue in read-only / analysis mode with conservative language;
3. route any state-changing action to human review.

A threshold is valid only when it is grounded in at least one of these sources:

- explicit user policy;
- a mandate supplied by the user's representative agent;
- protocol or market constraints that are facts rather than preferences;
- asset-property analysis documented in the relevant flow;
- a product policy that intentionally blocks or escalates actions when data is missing.

## Why monitoring is needed

A position can become unsafe, uneconomic, or operationally blocked even when the original decision was sound.

Material drift comes from:

- collateral prices and volatility;
- borrow rate, quota rate, and reward changes;
- APY or incentive decay;
- liquidity deterioration and withdrawal pressure;
- oracle freshness, divergence, or methodology changes;
- governance, timelock, or parameter changes;
- Liquidation Threshold (LT) ramps;
- forbidden-token or safe-pricing changes;
- Credit Manager pause, facade pause, expiration, or debt-limit changes;
- redemption queues, cooldowns, or claim readiness;
- issuer, eligibility, freeze, or compliance-state changes;
- the user's own horizon, thesis, capital availability, or ability to react.

Monitoring should answer two questions before proposing action:

1. What changed since the last accepted state?
2. Does the current state still satisfy the user's forward-looking policy?

Entry conditions are not automatically authoritative. A position can be up in PnL and still be outside mandate if the forward-looking thesis is broken.

## How thresholds are chosen

Thresholds should be selected from the position's failure modes, not copied from a generic table.

The agent should consider:

- user risk tolerance and stated loss budget;
- hold horizon and how quickly the user can respond;
- target leverage and desired safety margin;
- collateral volatility, correlation, and depeg history;
- liquidation depth and realistic exit size;
- oracle type, staleness window, and main-vs-reserve divergence;
- borrow-rate sensitivity and IRM slope;
- whether LT ramps or parameter changes can cross the user's floor within horizon;
- whether collateral is freely transferable, queued, claim-based, or issuer-controlled;
- whether automation is allowed for the action class;
- whether missing data should be treated as unknown, review-required, or blocking.

The output can still use verdict labels such as `ok`, `watch`, `review`, or `act now`, but those labels must trace back to the user's policy or the asset-specific risk analysis.

## Pool position monitoring

For pool positions, monitoring focuses on whether the LP would still accept the pool today.

Core dimensions:

- yield quality: organic yield, incentive yield, reward expiry, and net return versus the user's floor;
- exit capacity: available liquidity, utilisation, withdrawal pressure, and the user's position size;
- exposure composition: dominant Credit Managers, dominant collateral, new collateral entrants, and concentration changes;
- governance and curator changes: pending changes, recent material changes, and curator behaviour;
- bad-debt canaries: share-price movement, insurance-fund movement, incident feeds, and frozen-account exposure when relevant;
- oracle or asset-specific drills when dominant collateral makes them material.

The agent should not treat a single pool metric as decisive without checking whether that metric is the user's actual gate. A high-yield pool can still be unacceptable if the yield depends on expiring incentives, a changed collateral mix, a weakened curator process, or blocked exit liquidity.

## Credit Account position management

For Credit Accounts, monitoring is position management. The agent watches safety, economics, actionability, and user mandate at the same time.

Core dimensions:

- safety: Health Factor, liquidation distance, time-to-liquidation, LT ramps, forbidden-token overlap, and safe-pricing exit state;
- economics: net APY after borrow and quota costs, reward attribution, account-value trend, and whether the strategy still clears the user's hurdle;
- composition: collateral balances, debt breakdown, leverage, strategy description, and concentration drift;
- governance and operational state: parameter changes, pause state, expiration, debt limits, delayed withdrawals, and claim readiness;
- oracle state: freshness, main-vs-reserve divergence, methodology fit, and methodology changes;
- collateral-specific branches such as issuer-controlled assets, redemption-window assets, LP tokens, LSTs, stablecoins, and volatile assets.

Emergency routing should be based on whether loss can materialize before a normal analysis cycle can finish. That can come from low or rapidly falling Health Factor, active LT ramps, blocked exit state, paused operation paths, forbidden-token safe pricing, issuer freeze, or another asset-specific condition.

## Asset-property branches

Asset properties determine which facts matter most.

- **Freely transferable liquid collateral:** prioritize volatility, DEX depth, oracle fit, and liquidation path.
- **LSTs / queued withdrawal assets:** add withdrawal queue duration, claim readiness, and depeg / redemption mechanics.
- **LP tokens:** inspect the underlying components, impermanent-loss profile, depeg-of-component risk, and DEX liquidity.
- **Stablecoins:** watch depeg history, issuer / reserve risk, oracle methodology, and redemption depth.
- **Issuer-controlled / tokenized-security / RWA-like collateral:** add issuer state, eligibility, freeze state, transfer restrictions, redemption windows, claim readiness, and eligible-liquidator depth. Treat missing material issuer or compliance state as review-required or blocking.
- **Expirable or administratively constrained markets:** check expiry, pause, debt-limit, forbidden-token, and safe-pricing conditions before assuming an action path is available.

## Missing data policy

When a material field is missing, the agent must say what is missing and how it affects the recommendation.

Default handling:

- missing field used only for explanation → mark unknown and continue;
- missing field used for ranking → do not rank as cleanly acceptable;
- missing field used for Preview or Execute safety → block automation and route to human review;
- missing issuer / eligibility / freeze / redemption state for issuer-controlled collateral → do not treat as ordinary liquid collateral;
- missing execution-package integrity binding → do not execute.

## Agent output shape

A monitoring answer should include:

1. current verdict against user policy;
2. changed facts since the last accepted state;
3. which asset properties drove the verdict;
4. missing or stale data;
5. whether the next step is no action, focused analysis, proposal, Preview, Execute, or human review;
6. if action is proposed, the exact user policy or asset-property reason for the action.
