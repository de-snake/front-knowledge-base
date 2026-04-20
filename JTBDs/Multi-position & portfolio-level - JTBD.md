### Aggregate visibility

> **When I** hold several Gearbox positions,  
> **I want to** see a single roll-up of total exposure, total equity, aggregate net APY, and worst-case risk across accounts,  
> **so I can** answer "what's my Gearbox book doing?" without visiting each account individually.

Sub-jobs
- total net deployed across pools and CAs; 
- aggregate net APY weighted by equity;
- concentration by curator / chain / collateral; 
- worst-HF across CAs as the "weakest link" indicator; 
- aggregate claimable rewards.

### Reallocation logic

> **When I** have capital spread across positions whose theses have drifted at different rates,  
> **I want to** compare expected return and tail risk across my current positions and candidate new ones,  
> **so I can** move money from underperforming or degrading positions to better ones without bouncing through multiple UIs.

Sub-jobs: 
- side-by-side comparison of held and candidate opportunities, 
- rebalance cost estimation, 
- dry-run of the move.

### Reporting / audit - ==is it necessary?==

> **When I** need to explain my Gearbox activity to a controller, auditor, or tax authority,  
> **I want to** export a complete, timestamped record of deposits, withdrawals, yield, rewards, fees, and realised PnL,  
> **so I can** satisfy reporting obligations without re-deriving the data from on-chain history.

Sub-jobs: CSV export, per-position performance summary, realised vs unrealised PnL separation, fee breakdown (borrow, quota, protection, gas).


## Session-type JTBD matrix

The ownership lifecycle surfaces four distinct session types. Each is a different traversal of the canonical loop entered at Stage 6, with its own JTBD, required data, and success criterion.

|Session type|Entry trigger|Loop path|Primary JTBD served|Session length|Success =|
|---|---|---|---|---|---|
|**Confirmation**|Scheduled check-in|Monitor → exit|Maintain conviction (§2.1)|10–30 s|Left reassured, no action|
|**Analysis**|Change detected or suspicion|Monitor → Analyze → exit _or_ Propose|Detect change early (§2.2)|2–10 min|Understood why, decided whether to act|
|**Action**|Deliberate optimisation or claim|Monitor → Propose → Preview → Execute|Optimise (§2.3) _or_ maintenance action|2–15 min|Action signed, before/after matched expected|
|**Emergency**|HF breach, oracle incident, governance alert|Monitor (danger) → Propose → Preview → Execute|Act under pressure (§2.4)|30 s – 3 min|Remediation signed in ≤ 2 clicks|
|**Exit**|Thesis broken, capital need|Monitor → Propose → Preview → Execute (exit variant)|Exit deliberately (§2.5)|5–20 min|Exit executed at expected cost and timeline|
|**Reallocation**|Better venue or strategy found|Monitor → Discover → Analyze → Propose → Preview → Execute|Optimise (§2.3) across venues|15–30 min|Moved capital with net positive expected value|
