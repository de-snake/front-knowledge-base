After the deposit is made, the LP spends the vast majority of their Gearbox time in a different mode — checking that the thesis still holds. The ownership JTBD is a separate, smaller job that recurs on every return visit.

> **When I** hold a Gearbox pool position,  
> **I want to** confirm in under a minute that yield is holding, exit is still open, and nothing has silently changed in my exposure,  
> **so I can** either leave reassured, or act deliberately before the change costs me money.

Five ownership questions 

| Ownership question                                        | What the LP needs to see                                                                                                                                                                                 | Fails today / needs work                                |
| --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| Am I earning what I expected?                             | Current APY with organic / incentive breakdown + 30d trend vs ==entry baseline==<br><br>==**note**: need to keep track of the user entry if we want to display this==                                    | Breakdown by source and entry-baseline delta            |
| Can I still exit at size?                                 | Current available liquidity vs the LP's position, utilisation 30d trend                                                                                                                                  | Utilisation trend chart, withdrawal fee reminder        |
| Is the pool still composed the way it was when I entered? | Quota composition today vs at entry; ==list of new CMs added to the pool==<br><br>==**note**: is that really necessary?<br>do we sort CMs by date added w/ some threshold for the user position entry?== | Explicit composition-delta tracking                     |
| Has anyone changed the rules?                             | Parameter change log + pending governance queue                                                                                                                                                          | `EventFeedItem` / `GovernanceChange[]` coverage         |
| Is the bad-debt canary intact?                            | Share price since entry; ==insurance-fund balance delta==                                                                                                                                                | Share-price history endpoint, insurance-fund delta feed |

For RWA pools add a sixth question: **is the compliance layer drifting against me?** — frozen accounts delta, frozen debt delta, whitelisted-liquidator changes.

An agent representing an LP should answer these five (six with RWA) questions first on every monitoring call, in the order above. If all answers are "no change," the session can end in under a minute with a single summary line. If any answer is "yes, changed," the agent loops back to Analyze for a fresh due-diligence pass — that is the explicit back-edge in the canonical loop

### Sub-jobs (ownership job map)

|#|Sub-job|Success looks like|
|---|---|---|
|1|Glance at yield|Net APY visible in one view, broken into organic vs incentive, with a 30d trend line vs the user's entry baseline.|
|2|Glance at exit feasibility|Current utilisation vs the user's position size — "you can exit X % today." Withdrawal fee surfaced.|
|3|Detect yield drift|Alert / badge when organic APY drops below the user's floor, or when composite APY drops > X % over N days.|
|4|Detect composition drift|Per-token quota composition today vs at entry. Alert when a new CM is added or an existing one is materially expanded.|
|5|Detect governance change|Pending Safe-TX / timelock items visible with description and execution time; historical parameter-change log reachable.|
|6|Detect bad-debt event|Share-price drop vs previous check as the canary. Insurance-fund balance delta.|
|7|Detect RWA drift (if applicable)|Frozen-accounts delta, frozen-debt delta, whitelisted-liquidator changes.|
|8|Decide top-up|Can I add more here given current thesis? Available liquidity, concentration cap, updated risk summary.|
|9|Decide partial exit|Current utilisation check, fee, price impact; partial-exit size that doesn't hit the exit-risk thresholds.|
|10|Decide full exit|Time-to-fill estimate at the user's size, withdrawal fee, any in-flight rewards that would be forfeited.|


### Edge cases & known failure modes

- **Incentive-only yield trap.** Headline APY looks great; organic APY alone is below the floor. Incentive campaign expires a month in, net yield collapses.
- **Utilisation spike lockout.** User tries to exit; utilisation is at 98 %; withdrawal is throttled until borrowers repay.
- **Silent composition shift.** No governance action, but borrowers migrate to a riskier collateral mix. Exposure the LP signed up for is no longer what they're holding.
- **Paused CM with outstanding debt.** CM is paused (no new positions, but also no liquidations). Underwater positions inside cannot be closed; bad debt accumulates until unpause.
- **RWA freeze cascade.** Securitize freezes multiple accounts. Their total debt exceeds the insurance fund. Socialised loss hits LPs.