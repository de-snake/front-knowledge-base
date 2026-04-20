### Main job statement

> **When I** have capital in a base asset and a target yield floor,  
> **I want to** place it into a curated, transparent lending venue where I can trace my indirect exposure, exit when I need to, and be warned before conditions change,  
> **so I can** earn a sustainable organic yield without taking liquidation risk or hidden compliance risk.

### Sub-jobs (job map)

The job decomposes into eight discrete sub-jobs. Each one corresponds to a step where the user can succeed or fail independently.

| #   | Sub-job                       | Success looks like                                                                                              |
| --- | ----------------------------- | --------------------------------------------------------------------------------------------------------------- |
| 1   | Define the mandate            | The user has a floor APY, base asset, chain, allowed access model, and concentration cap.                       |
| 2   | Locate candidates             | A 1–3 pool shortlist surfaces in under a minute.                                                                |
| 3   | Validate yield sustainability | Organic APY alone meets the floor, with 90d history to prove it.                                                |
| 4   | Trace exposure                | The full pool → CMs → tokens chain is legible, including ==insurance fund== and oracle methodology.             |
| 5   | Verify exit feasibility       | Available liquidity, utilisation trend, withdrawal fee, and IRM behaviour above U2 are all acceptable.          |
| 6   | Assess curator trust          | Curator identity, operating breadth, and cumulative bad-debt record are visible and ==within tolerance.==       |
| 7   | Commit capital                | Deposit is previewed, concentration stays under the cap, no preview warnings fire, bytes are signed.            |
| 8   | Maintain conviction           | Monitoring surfaces yield holding, composition stable, no pending adverse governance, no RWA freeze escalation. |
### Functional / emotional / social dimensions

- **Functional.** Earn a predictable net yield on a base asset, with full control over exit and visible evidence for every risk claim.
- **Emotional.** Trust the counterparty chain. Feel that nothing is silently changing. Know that if conditions shift, the system warns them before they take a loss.
- **Social.** For institutional LPs: be able to defend the allocation to an investment committee with evidence — "here is the organic yield history, here is the curator record, here is the bad-debt canary."
### Decision criteria & "good deposit" definition

A good Pool deposit satisfies all of:

1. Organic APY alone ≥ user's floor, with 90d history showing stability or positive drift.
2. No single CM dominates the pool's total debt (no concentration).
3. Utilisation 90d history normal; IRM above U2 incentivises repayment or borrowing-above-U2 is forbidden.
4. Curator has zero cumulative bad-debt across managed pools (or non-zero is understood and scoped).
5. No high-impact pending governance change within the user's monitoring cadence.
6. For RWA pools: freeze authority identified, whitelisted-liquidator count ==above internal threshold==, transfer-restriction type understood.
7. User's deposit leaves them below their ==internal concentration cap== on the pool.