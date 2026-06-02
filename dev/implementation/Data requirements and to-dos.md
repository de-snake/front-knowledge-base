# Backend / MCP data architecture

This is the implementation handoff for the backend and Gearbox MCP surface.

It answers one question:

> Given the repeated product flows in `user/`, what deterministic data read methods should backend / MCP expose, and why is this the right structure?

This file is not the agent-side response design. The agent remains the fuzzy reasoning layer: it compares facts to user policy, decides whether something is acceptable, writes explanations, and proposes actions.

Backend / MCP is the deterministic layer. It cannot satisfy every future agent's needs perfectly, so the right goal is a stable, composable read architecture derived from the flows we know users and agents will repeat.

## Design thesis

The canonical product flows reduce to four durable backend needs:

1. **Discover candidates**
   - pool opportunities for LP deposits;
   - Credit Account strategy / Credit Manager opportunities for leveraged positions.

2. **Read due-diligence facts**
   - yield, exposure, liquidity, curator / Credit Manager envelope, oracle state, change queue, route constraints, issuer / eligibility branch.

3. **Monitor existing positions**
   - current LP or Credit Account state;
   - history and deltas since a supplied timestamp;
   - executed and pending changes that can invalidate the thesis.

4. **Preview and verify state-changing actions**
   - exact calldata / multicall;
   - before → after simulation;
   - gas, route, slippage / price-impact facts;
   - integrity hash and receipt readback.

That structure comes from the four frequent flows:

- LP entry: `Pool deposit`
- LP ownership: `Pool monitoring`
- Credit Account entry: `Credit Account opening`
- Credit Account ownership: `Credit Account management`

The backend should not expose UI card names or agent verdicts as primary objects. It should expose deterministic facts, histories, event feeds, quotes, and simulations that agents can combine.

## Deterministic boundary

### Backend / MCP owns

- Protocol state reads.
- Indexed historical series.
- Event and governance-change feeds.
- Reward / incentive campaign facts.
- Curator / Credit Manager / pool metadata that has a declared source.
- Issuer / eligibility / freeze / redemption / eligible-liquidator facts when available.
- Deterministic derived values where the formula is fixed:
  - Health Factor;
  - utilisation;
  - borrowable liquidity;
  - max leverage from Liquidation Threshold;
  - safe-pricing exit Health Factor;
  - LT-ramp projection dates;
  - APY component decomposition;
  - route quote and price-impact estimates;
  - transaction simulation before / after state;
  - calldata or multicall hash.

### Agent / product layer owns

- User-specific verdicts: `good`, `watch`, `review`, `act now`, `blocked`, etc.
- User policy thresholds and mandate interpretation.
- Whether a data point is acceptable for this user.
- Material-vs-cosmetic interpretation when it depends on user horizon, size, or policy.
- Candidate ranking rationale.
- Action choice and sizing when multiple valid deterministic options exist.
- Final wording shown to the user.

### Shared rule

Every MCP response that can affect a user decision must carry:

```text
as_of
source_class
source_handle
freshness_status
unknown_or_stale_reason
block_number, if chain-derived
computed_from, if derived
```

A missing fact is a first-class result, not an omitted field.

Allowed status values:

```text
ok | stale | unknown | not_indexed | not_applicable | blocked
```

## Data-source classes

Use these source classes consistently across methods.

| Source class | Meaning | Examples |
| --- | --- | --- |
| `protocol` | Direct contract state or canonical protocol artifact. | pool liquidity, Credit Manager parameters, quotas, LT, oracle prices, facade pause. |
| `indexer` | Derived from events, traces, subgraphs, or backend aggregation. | utilisation history, share-price history, top borrower concentration, executed change feed. |
| `external_market` | Market data outside Gearbox protocol state. | DEX depth, adapter quotes, aggregator quotes, 90d price / slippage series. |
| `incentive` | Reward campaign data. | Merkl campaign APY, expiry, top-up history, reference URL. |
| `curator_diligence` | Curator profile and operating history with declared source. | identity, governance mechanism, bad-debt incidents, liquidity incidents. |
| `issuer_compliance` | Issuer-controlled or compliance-gated asset state. | freeze state, eligibility, redemption window, eligible-liquidator depth. |
| `product_policy` | Product-owned rule, not user preference. | missing issuer state blocks automation; preview required before Execute. |
| `user_policy` | Supplied by user / representative / agent mandate. | HF floor, hold horizon, APY hurdle, route tolerance. Usually passed in request or stored outside protocol backend. |
| `computed` | Deterministic calculation over sourced facts. | max exposure, safe-pricing exit HF, breakeven horizon, action simulation. |

## Core entities

These are stable backend objects, not UI cards.

### `Asset`

Business meaning: token or position wrapper that can appear as pool underlying, Credit Account collateral, reward token, or transition-stage asset.

Key facts:

- `asset_id`: chain + address or canonical synthetic id.
- `symbol`, `decimals`, `asset_type`.
- `issuer_controlled`: boolean.
- `compliance_gated`: boolean.
- `redemption_window_asset`: boolean.
- `phantom_token`: boolean.
- oracle metadata.
- withdrawal / redemption metadata when applicable.

Why it exists: both LP and Credit Account flows need per-token exposure, oracle, liquidity, and issuer branch checks.

### `Pool`

Business meaning: Gearbox pool / lending market where LP capital is supplied and borrowed by Credit Accounts.

Key facts:

- underlying asset;
- expected liquidity, available liquidity, total borrowed, utilisation;
- share price;
- withdrawal fee and withdrawal mechanics;
- IRM parameters;
- quoted tokens / quota state;
- connected Credit Managers;
- insurance fund balance;
- current and historical yield components.

Why it exists: every LP deposit, LP monitoring, and Credit Account economics read depends on pool state.

### `CreditManager`

Business meaning: operational container that defines how a Credit Account can borrow, hold collateral, route swaps, and be liquidated.

Key facts:

- associated pool;
- debt limit and current debt;
- min / max debt;
- collateral list and per-token LT;
- LT-ramp schedules;
- forbidden-token status;
- quota rates and quota limits;
- allowed adapters;
- expiration, pause state, facade pause, per-block borrow capacity;
- compliance-gated execution flag.

Why it exists: Credit Account opening / management asks about safety, exit feasibility, operational envelope, and rule-change risk.

### `LpPosition`

Business meaning: user-owned pool position.

Key facts:

- owner wallet;
- pool id;
- shares;
- current value;
- share price at current read;
- deposit / withdrawal events;
- claimable rewards attributed to the position or owner.

Why it exists: LP monitoring compares the user's actual position size to current pool liquidity and drift.

### `CreditAccountPosition`

Business meaning: user-owned leveraged Gearbox account.

Key facts:

- Credit Account address;
- owner / wallet / wrapper when applicable;
- Credit Manager id;
- debt by asset;
- collateral balances;
- TWV / total value / equity;
- Health Factor;
- leverage;
- current borrow and quota rates;
- rewards;
- bot permissions;
- transition-stage assets / pending withdrawals.

Why it exists: Credit Account management must answer safety, returns, operational state, issuer-controlled collateral state, and action feasibility.

### `CuratorProfile`

Business meaning: the operating counterparty behind pool / Credit Manager parameters.

Key facts:

- identity and URLs;
- governance mechanism;
- signer / Safe / timelock metadata;
- first operation date;
- AUM;
- bad-debt incidents;
- liquidity incidents;
- parameter-change history summary.

Why it exists: LP and Credit Account flows ask who manages the risk envelope and whether the envelope is stable.

### `GovernanceChange`

Business meaning: executed or pending change to parameters that can alter a user's thesis.

Key facts:

- target scope: pool, Credit Manager, asset, oracle, curator;
- change type;
- parameter name;
- old value, new value;
- proposed / queued / executed timestamp;
- timelock / Safe / proposer;
- affected domains: yield, exposure, Health Factor, exit, oracle, issuer, operational.

Why it exists: both entry and monitoring flows ask what could change or what changed since last check.

### `IssuerControlState`

Business meaning: external or issuer-controlled facts that affect transferability, liquidation, redemption, or automation.

Key facts:

- issuer / program id;
- asset id;
- holder / Credit Account / wrapper address if applicable;
- eligibility / KYC state;
- own freeze state;
- frozen-account count and aggregate frozen debt when LP-facing;
- redemption window, notice deadline, claim readiness;
- eligible-liquidator set and depth;
- automation restrictions.

Why it exists: tokenized-security and issuer-controlled assets cannot be treated as ordinary liquid collateral when this state is missing.

### `PreviewPackage`

Business meaning: deterministic pre-execution artifact for a proposed state-changing action.

Key facts:

- action type;
- target position / pool / Credit Manager;
- exact calldata or multicall;
- calldata hash;
- simulation input block;
- before state;
- after state;
- gas estimate;
- route quote and price impact when relevant;
- hard blockers and warnings;
- expiry;
- approval mode required.

Why it exists: Preview is the integrity boundary before Execute.

## MCP method architecture

The method surface should have two layers:

1. **Composite methods** for the repeated product flows.
   - These bundle the facts most agents will need for LP deposit, LP monitoring, Credit Account opening, and Credit Account management.
   - They reduce round trips and make frequent flows consistent.

2. **Facet methods** for drill-down and alternate agents.
   - These expose raw pool, Credit Manager, oracle, issuer, route, history, and change-feed data.
   - They let a different agent build a different reasoning path without requiring a new backend endpoint for every idea.

This is the compromise between deterministic structure and agent flexibility.

## Composite methods

### `list_pool_opportunities`

Purpose: deterministic candidate discovery for LP deposit.

Request inputs:

```text
chain_id
wallet_address?          // optional, for balances / existing exposure
underlying_asset?        // optional
amount?                  // optional, improves availability / concentration facts
as_of?                   // optional historical/debug read
```

Returns:

- pool id;
- pool name / underlying;
- current TVL, available liquidity, utilisation;
- composite APY with organic / incentive split;
- incentive expiry presence;
- top exposure tokens by quota / current debt proxy;
- issuer-controlled exposure flag;
- pending material-change count by target scope;
- source / freshness envelope.

Why this method exists:

- Pool deposit Stage 1 needs a finite candidate set.
- Agents should not scrape multiple pool, reward, oracle, and governance endpoints just to know what can be analyzed.
- It does not rank by "best for user"; it returns deterministic opportunity facts that an agent can rank under its mandate.

### `get_pool_due_diligence`

Purpose: deterministic evidence bundle for Pool deposit Stage 2.

Request inputs:

```text
pool_id
amount?                  // optional; needed for concentration and exit-at-size checks
wallet_address?          // optional; existing-position overlap
history_window = 90d
include_t2 = false        // extended drill facts
```

Returns sections:

- `yield`: composite, organic, incentives, APY series, expiry / top-up references.
- `exposure`: quota used / quota limits, current exposure by token where available, max exposure formula inputs, insurance fund.
- `liquidity`: available liquidity, expected liquidity, utilisation series, withdrawal fee, withdrawal mechanics, borrower concentration when indexed.
- `curator`: identity, governance, track record, incidents, change-frequency summary.
- `changes`: executed parameter changes and pending governance queue.
- `oracles`: per-token main / reserve price, freshness, staleness window, methodology.
- `issuer_branch`: issuer-controlled asset facts when exposure is present; otherwise `not_applicable`.
- `gaps`: facts that are missing, stale, or not indexed.

Why this method exists:

- Pool deposit Q1–Q5 ask stable recurring questions.
- A single due-diligence dataset keeps these questions traceable without encoding the agent's final verdict.

### `list_credit_account_opportunities`

Purpose: deterministic candidate discovery for Credit Account opening.

Request inputs:

```text
chain_id
wallet_address?
underlying_asset?
amount?
strategy_filter?
as_of?
```

Returns:

- strategy / Credit Manager id;
- pool id;
- target collateral / strategy label;
- min debt, max debt, max leverage from LT;
- borrow rate, quota rate, collateral-yield inputs;
- adapter availability;
- route-quote availability;
- issuer / compliance-gated flags;
- operational state: paused / expirable / per-block borrow capacity;
- source / freshness envelope.

Why this method exists:

- Credit Account opening Stage 1 needs a candidate set richer than pool discovery because route, leverage, and Credit Manager envelope matter from the start.

### `get_credit_account_due_diligence`

Purpose: deterministic evidence bundle for Credit Account opening Stage 2.

Request inputs:

```text
strategy_id or credit_manager_id
target_collateral?
amount?
target_leverage?
wallet_address?
history_window = 90d
include_t2 = false
```

Returns sections:

- `economics`: collateral yield, borrow rate, quota rate, fee inputs, APY / spread series, breakeven inputs.
- `safety`: LT, LT ramps, projected Health Factor inputs, safe-pricing exit inputs, forbidden-token status.
- `exit_feasibility`: adapters, route quotes, DEX depth, minDebt / iterative-unwind constraints, delayed-withdrawal / phantom-token state.
- `credit_manager_envelope`: pause, expiration, debt limits, per-block capacity, facade state, compliance-gated flag.
- `changes`: executed and pending changes affecting CM, pool, tokens, oracle, IRM, forbidden tokens.
- `oracles`: per held / target token freshness, main / reserve price, methodology.
- `issuer_branch`: issuer / freeze / eligibility / redemption / eligible-liquidator facts when relevant.
- `gaps`: missing, stale, or not-indexed facts.

Why this method exists:

- Credit Account opening Q1–Q5 are not arbitrary analysis; they repeatedly require economics, safety, exit feasibility, envelope stability, and change risk.
- The method returns inputs and deterministic projections, not a recommendation.

### `list_user_positions`

Purpose: deterministic entry point for monitoring.

Request inputs:

```text
chain_id
wallet_address
include_closed = false
```

Returns:

- LP positions: position id, pool id, shares, current value, last known activity.
- Credit Accounts: account address, Credit Manager id, current value, debt, Health Factor, leverage, status flags.
- Position types that include issuer-controlled collateral.
- Source / freshness envelope.

Why this method exists:

- Monitoring starts from ownership, not discovery.
- The backend needs one stable way for agents to find what exists before asking deeper questions.

### `get_lp_monitoring_dataset`

Purpose: deterministic fact bundle for Pool monitoring Stage 6.

Request inputs:

```text
position_id
since?                   // agent supplies previous-check timestamp if it has one
history_window = 30d
include_t2 = false
```

Returns sections:

- `position`: shares, current value, pool share price, rewards.
- `yield`: composite APY, 30d trend, incentive expiry facts.
- `exit`: withdrawable now, utilisation trend, withdrawal fee, withdrawal mechanics.
- `composition`: quoted-token quota composition, top-token delta since `since`, new CMs since `since`.
- `governance`: pending queue and executed pool changes since `since`.
- `bad_debt_canary`: share-price delta, insurance-fund delta, matching incident references.
- `oracle_drill`: present only if requested or triggered by change-feed / stale-feed facts.
- `issuer_branch`: frozen-account / eligible-liquidator / issuer facts if issuer-controlled exposure is material.
- `gaps`.

Why this method exists:

- LP monitoring has a stable recurring question: is yield holding, is exit open, did exposure or rules change, did the bad-debt canary fire?
- The agent owns the user's thesis and previous-check policy; backend returns deterministic current facts and deltas against the supplied timestamp.

### `get_credit_account_monitoring_dataset`

Purpose: deterministic fact bundle for Credit Account management Stage 6.

Request inputs:

```text
credit_account_address
since?
history_window = 30d
include_t2 = false
```

Returns sections:

- `position`: Health Factor, debt, TWV / equity, collateral balances, leverage, rates.
- `safety`: liquidation distance, time-to-liquidation inputs, LT-ramp status, forbidden-token overlap, safe-pricing inputs.
- `returns`: net APY inputs, account-value history, borrow-vs-yield spread, unclaimed rewards.
- `governance`: pending and executed changes affecting the CM, held tokens, oracle, IRM, forbidden-token set.
- `operations`: expiration, pause, facade state, delayed withdrawals, phantom tokens, minDebt / partial-exit feasibility, bot permissions.
- `oracle_drill`: freshness, main / reserve divergence, methodology changes when requested or triggered.
- `issuer_branch`: own freeze, eligibility / KYC, registry, redemption / claim readiness, eligible-liquidator facts when relevant.
- `gaps`.

Why this method exists:

- Credit Account monitoring differs from LP monitoring: safety, debt cost, leverage, emergency path, and issuer-controlled own-account state are first-class.
- It should not return "safe" as a backend judgment. It should return the facts an agent needs to compare against user policy.

### `preview_pool_action`

Purpose: deterministic pre-execution package for LP deposit, top-up, partial exit, or full exit.

Request inputs:

```text
position_id?             // existing position action
pool_id?                 // new deposit action
action_type              // deposit | top_up | partial_exit | full_exit
amount
wallet_address
proposal_ref?            // optional agent-side proposal id/hash
slippage_policy?         // user or agent supplied, not backend default
```

Returns:

- before state;
- after state;
- ERC-4626 preview result;
- expected shares minted or underlying returned;
- share price at preview;
- withdrawal fee;
- route quote / price impact when relevant;
- gas estimate;
- hard blockers;
- warnings;
- exact calldata;
- calldata hash;
- expiry;
- required approval mode.

Why this method exists:

- Every state-changing LP action must be simulated against current state before signing.
- This method is deterministic and does not decide whether the user should proceed.

### `preview_credit_account_action`

Purpose: deterministic pre-execution package for Credit Account open, add collateral, reduce leverage, increase leverage, partial exit, full exit, rebalance, claim, or bot-permission update.

Request inputs:

```text
credit_account_address?  // existing account action
credit_manager_id?       // open action
action_type
amounts / targets
route_preferences?
wallet_address
proposal_ref?
slippage_policy?
hf_floor?                // passed for comparison; missing does not stop simulation but blocks readiness flag
```

Returns:

- before state;
- after state;
- Health Factor before / after;
- effective leverage after;
- position value / equity after;
- intermediate minimum Health Factor for multi-step actions;
- swap impact;
- route quote;
- delayed-withdrawal / time-to-settle facts;
- gas estimate;
- hard blockers;
- warnings;
- exact multicall;
- multicall hash;
- expiry;
- required approval mode;
- readiness facts, including which supplied policies were missing.

Why this method exists:

- Credit Account actions are multicall-heavy and can change Health Factor mid-route.
- Preview is the deterministic safety boundary before human signing or scoped bot execution.

### `get_execution_receipt`

Purpose: deterministic post-execution readback.

Request inputs:

```text
tx_hash
expected_preview_hash?
```

Returns:

- transaction status;
- block number;
- action type if decoded;
- matched preview hash or mismatch;
- actual before / after deltas when derivable;
- gas paid;
- resulting position handle;
- post-action monitoring baseline facts.

Why this method exists:

- After execution, the agent needs a new baseline for future monitoring and an integrity check that the confirmed transaction matches the previewed package.

## Facet methods

Composite methods should be backed by smaller facet methods. These keep the MCP useful for agents that need different reasoning paths.

### State facets

```text
get_pool_state(pool_id)
get_credit_manager_state(credit_manager_id)
get_lp_position_state(position_id)
get_credit_account_state(credit_account_address)
get_asset_state(asset_id)
```

Use when an agent needs current facts without the full flow bundle.

### History facets

```text
get_pool_series(pool_id, series[], window, granularity)
get_credit_account_series(credit_account_address, series[], window, granularity)
get_asset_price_or_oracle_series(asset_id, window, granularity)
```

Required series:

- pool utilisation;
- TVL / expected liquidity / available liquidity;
- share price;
- organic APY;
- incentive APY;
- borrow rate;
- quota rate;
- Health Factor;
- account value;
- oracle price / last update.

Use when trend or drift matters.

### Change facets

```text
get_change_feed(scope_type, scope_id, since?, include_pending = true)
get_pending_governance(scope_type, scope_id)
get_change_frequency(scope_type, scope_id, windows = [30d, 90d, 365d])
```

Returned changes should include raw changed fields and affected domains. They should not decide if the change is acceptable for a specific user.

### Oracle facets

```text
get_oracle_state(asset_id, scope_id?)
get_oracle_methodology(asset_id, scope_id?)
get_oracle_divergence(asset_id, scope_id?)
```

Use when an agent drills from position monitoring into oracle-specific reasoning.

### Incentive / reward facets

```text
get_incentive_layers(pool_id, window?)
get_reward_claims(wallet_address, position_id?)
```

Use when yield depends on campaigns and when a Credit Account or LP has claimable rewards.

### Curator facets

```text
get_curator_profile(curator_id)
get_curator_incidents(curator_id, since?)
get_curator_activity(curator_id, since?)
```

Use when agent due diligence asks whether the pool / Credit Manager manager has a credible operating record.

### Issuer / compliance facets

```text
get_issuer_program_state(asset_id)
get_holder_issuer_state(asset_id, holder_address)
get_credit_account_issuer_state(asset_id, credit_account_address)
get_redemption_state(asset_id, holder_address?)
get_eligible_liquidator_state(asset_id, scope_id?)
```

Use when assets are tokenized securities, issuer-controlled, redemption-window assets, freezeable assets, or compliance-gated.

If these methods cannot source a fact, they must return `unknown` or `not_indexed`, not omit the branch.

### Route / quote facets

```text
get_adapter_routes(credit_manager_id, from_asset, to_asset)
quote_route(credit_manager_id, from_asset, to_asset, amount)
compare_external_route(from_asset, to_asset, amount, venues[])
```

Use when entry, exit, rebalance, or leverage adjustment has non-trivial route risk.

### Data health facet

```text
get_data_health(scope_type, scope_id)
```

Returns:

- indexed sources available;
- latest successful update per source;
- stale sources;
- unsupported source classes;
- known blocked facts.

Use before agents present high-confidence analysis.

## Traceability from product flows to methods

| Product flow need | Backend / MCP method group | Why this structure follows from the flow |
| --- | --- | --- |
| LP wants candidate pools. | `list_pool_opportunities` | Pool deposit starts with finite opportunity discovery before analysis. |
| LP asks where yield comes from. | `get_pool_due_diligence.yield`, `get_incentive_layers` | Pool deposit Q1 needs organic vs incentive yield and expiry / durability facts. |
| LP asks maximum token exposure. | `get_pool_due_diligence.exposure`, `get_pool_state`, `get_credit_manager_state`, `get_oracle_state`, issuer facets | Pool deposit Q2 needs quota, CM limits, current exposure, oracle, and issuer-controlled token facts. |
| LP asks whether withdrawal is possible. | `get_pool_due_diligence.liquidity`, `get_pool_series`, route / market facets when exit routes need swaps | Pool deposit Q3 and Pool monitoring Q2 need current liquidity plus history. |
| LP asks who manages the pool. | `get_curator_profile`, `get_curator_incidents`, `get_change_feed` | Pool deposit Q4 asks for manager identity, governance, and record. |
| LP asks what can change. | `get_change_feed`, `get_pending_governance`, `get_change_frequency` | Pool deposit Q5 and monitoring Q4 need executed and pending parameter changes. |
| LP monitors an existing position. | `list_user_positions`, `get_lp_monitoring_dataset` | Pool monitoring Stage 6 is a recurring current-state + delta read. |
| Credit Account user wants candidates. | `list_credit_account_opportunities` | CA opening starts with strategy / Credit Manager candidates, not generic pool candidates. |
| Credit Account user asks economics. | `get_credit_account_due_diligence.economics`, history facets | CA opening Q1 needs borrow, quota, collateral yield, fees, and breakeven inputs. |
| Credit Account user asks liquidation safety. | `get_credit_account_due_diligence.safety`, oracle facets, issuer facets | CA opening Q2 and CA management Q1 need HF, LT, ramps, oracle, forbidden-token, and issuer facts. |
| Credit Account user asks exit feasibility. | `get_credit_account_due_diligence.exit_feasibility`, route facets | CA opening Q3 and CA management Q4 need adapters, minDebt, liquidity, queues, and route quotes. |
| Credit Account user asks envelope stability. | `get_credit_account_due_diligence.credit_manager_envelope`, `get_change_feed` | CA opening Q4 / Q5 and CA management Q3 / Q4 need CM operational and change state. |
| Credit Account user monitors position. | `list_user_positions`, `get_credit_account_monitoring_dataset` | CA management Stage 6 is a richer safety / returns / operational / issuer recurring read. |
| Any flow reaches state-changing action. | `preview_pool_action`, `preview_credit_account_action` | Preview is mandatory before Execute and must be deterministic. |
| Any action confirms. | `get_execution_receipt` | Monitoring requires a post-action baseline and integrity readback. |

## What not to model as backend fields

Do not persist or expose these as backend-owned facts unless they are explicitly tied to a source policy object:

- `is_good_pool`
- `safe_credit_account`
- `should_deposit`
- `should_reduce_leverage`
- `recommended_action`
- `risk_score` without source methodology
- `material_change` without raw change context and policy basis
- fixed universal HF / APY / slippage thresholds

Backend can expose `affected_domains`, raw deltas, and deterministic projections. The agent decides whether those facts are acceptable for this user.

## Unknown and stale handling

Every method must distinguish:

- `not_applicable`: branch does not apply, e.g. no issuer-controlled asset exposure.
- `unknown`: branch applies, but source did not return a fact.
- `not_indexed`: source could exist but backend does not yet collect it.
- `stale`: fact exists but failed freshness SLA.
- `blocked`: source cannot be accessed due to permissions or unsupported integration.

Examples:

```text
issuer_branch.status = not_applicable
// ordinary ERC-20-only pool, no issuer-controlled asset exposure

issuer_branch.status = unknown
// tokenized-security exposure exists, but issuer freeze state was not returned

curator.incidents.status = not_indexed
// curator incident log is not implemented yet
```

## Data gaps to implement

These gaps are backend / MCP gaps, not agent response-design gaps.

1. **Current debt attributable to collateral token**
   - Needed for LP max/current exposure by token.
   - Current proxy `quotaUsed` may not be equivalent; verify or build aggregate.

2. **Incentive campaign durability**
   - Needed for yield decomposition and expiry risk.
   - Requires Merkl / campaign history, expiry, top-up, renewal references.

3. **Executed and pending parameter-change feeds**
   - Needed across LP and Credit Account entry / monitoring.
   - Scope filters: pool, Credit Manager, asset, oracle, curator.

4. **Change-frequency aggregate**
   - Counts by change type over 30d / 90d / 365d.
   - Used as deterministic input for curator / envelope volatility reasoning.

5. **Curator profile and incident logs**
   - Identity, governance, bad-debt incidents, liquidity incidents, activity log.
   - Must carry source handles and confidence / editorial ownership.

6. **Borrower / debt concentration**
   - Top-N borrower share and debt distribution.
   - Needed for LP exit-lock and utilisation-spike reasoning.

7. **Oracle methodology and history**
   - Per-token category, main / reserve setup, staleness window, last update, divergence, 90d series.
   - Needed for both LP risk and Credit Account safety.

8. **Adapter route and external quote comparison**
   - Gearbox adapter route quote vs external market depth where relevant.
   - Needed for Credit Account open / exit / rebalance and some LP exit cases.

9. **Delayed-withdrawal / phantom-token feed**
   - Supported assets, queue duration, claimableAt, blocking reasons.
   - Needed for Credit Account exit feasibility and management.

10. **Rewards / claims endpoint**
    - Claimable rewards per wallet, pool position, Credit Account, and Merkl attribution.
    - Needed for monitoring and claim action previews.

11. **Issuer / eligibility / freeze / redemption state**
    - Issuer program status, holder state, Credit Account state, redemption windows, eligible-liquidator depth.
    - Missing state must block ordinary-liquid-collateral treatment.

12. **Bot registry / permission state**
    - Active bots, permission scopes, expected vs unexpected bot permissions.
    - Needed for Credit Account management and automation boundary checks.

13. **Preview integrity package**
    - Calldata / multicall hash, simulation block, expiry, policy inputs supplied, before / after state.
    - Needed before any Execute path.

14. **Receipt readback and baseline generation**
    - Decode transaction result, match preview hash, derive post-action monitoring baseline.
    - Needed for reliable monitoring continuity.

## Build order

1. **Method envelope and identifiers**
   - Standardize `chain_id`, ids, timestamps, block numbers, source classes, freshness, unknown states.
   - Without this, later methods cannot be trusted or composed.

2. **Current state primitives**
   - `get_pool_state`, `get_credit_manager_state`, `get_lp_position_state`, `get_credit_account_state`, `list_user_positions`.
   - These are dependencies for every flow.

3. **Preview integrity methods**
   - `preview_pool_action`, `preview_credit_account_action`, `get_execution_receipt`.
   - Any Execute path is unsafe without deterministic preview and receipt readback.

4. **History and change feeds**
   - Series, executed changes, pending governance, change-frequency aggregate.
   - Required for monitoring and for explaining why a previously valid thesis may no longer hold.

5. **Monitoring composites**
   - `get_lp_monitoring_dataset`, `get_credit_account_monitoring_dataset`.
   - Highest recurring user value after current state and preview safety.

6. **Issuer-controlled asset branch**
   - Issuer / freeze / eligibility / redemption / eligible-liquidator methods.
   - Required because unknown issuer state changes the safety interpretation and automation boundary.

7. **Opportunity and due-diligence composites**
   - `list_pool_opportunities`, `get_pool_due_diligence`, `list_credit_account_opportunities`, `get_credit_account_due_diligence`.
   - These improve entry decisions after the monitoring / preview safety backbone exists.

8. **Extended drill facets**
   - Curator incident history, external route comparisons, top-borrower concentration, advanced oracle / market history.
   - Useful for sophisticated agents and T2 flows, but less foundational than current state, preview, and monitoring.

## Review standard for this architecture

A backend / MCP method is ready only if it answers all of these:

- Which product-flow question requires it?
- Which entity owns the fact?
- Is the fact current, historical, event-based, or computed?
- What is the source class?
- What is the freshness rule?
- What happens if the fact is unknown, stale, or not indexed?
- Is the method returning deterministic facts, or accidentally returning an agent verdict?
- Which composite methods reuse this facet?
- What test proves the method can answer or correctly block the product-flow question?

This is the reason for the exact structure above: product flows define repeated questions; repeated questions define deterministic facts; facts define entities and MCP methods; agents consume those methods and still do the user-specific reasoning.