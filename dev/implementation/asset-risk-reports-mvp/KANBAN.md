# Asset Risk Dossiers MVP — Kanban board

Board slug: `asset-risk-dossiers-mvp`

Board DB: `~/.hermes/kanban/boards/asset-risk-dossiers-mvp/kanban.db`

Workspace: `dir:/Users/ilya/ai-assistant`

Methodology contract: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/methodology.md`

## Scope

Run the asset-specific mining pipeline for exactly the user-supplied tokens below. Do not choose, add, rank, or recommend tokens.

Initial four-asset batch:

- Ethereum mainnet, chain_id `1`, Saturn `sUSDat`, `0xd166337499e176bbc38a1fbd113ab144e5bd2df7`
- Ethereum mainnet, chain_id `1`, apyx `apyUSD`, `0x38eeb52f0771140d10c4e9a9a72349a329fe8a6a`
- Ethereum mainnet, chain_id `1`, Hastra `PRIME`, `0x19ebb35279A16207Ec4ba82799CC64715065F7F6`
- Base, chain_id `8453`, Centrifuge `deSPXA`, `0x9c5C365e764829876243d0b289733B9D2b729685`

Expansion batch added 2026-06-04:

- Ethereum mainnet, chain_id `1`, Saturn `USDat`, `0x23238F20B894f29041f48d88Ee91131c395aAA71`
- Ethereum mainnet, chain_id `1`, apyx `apxUSD`, `0x98A878b1Cd98131B271883B390f68D2c90674665`

Pendle PT-market batch, gated after six-asset completion:

- Pendle PT `apyUSD`, Ethereum mainnet, maturity `2026-08-27`, user days-to-maturity label `83 days`
- Pendle PT `apxUSD`, Ethereum mainnet, maturity `2026-11-05`, user days-to-maturity label `153 days`
- Pendle PT `USDat`, Ethereum mainnet, maturity `2026-08-27`, user days-to-maturity label `83 days`
- Pendle PT `sUSDat`, Ethereum mainnet, maturity `2026-08-27`, user days-to-maturity label `83 days`

PT-market analyses inherit the underlying-token risk profile, then add PT-specific yield profile, maturity/redemption, liquidity, Pendle market, and economic-risk details.

X research batch, gated after final Pendle PT verification:

- apyx `apyUSD` token + Pendle PT `apyUSD` maturity `2026-08-27`: research X estimates for points / airdrop anticipation, STAC or underlying-yield assumptions, PT discount / fixed-yield assumptions, and risks.
- apyx `apxUSD` token + Pendle PT `apxUSD` maturity `2026-11-05`: same X research scope.
- Saturn `USDat` token + Pendle PT `USDat` maturity `2026-08-27`: same X research scope.
- Saturn `sUSDat` token + Pendle PT `sUSDat` maturity `2026-08-27`: same X research scope.

X research is read-only, uses the `x-research` skill with Hermes `x_search`, and must separate social speculation from verified token/PT facts.

## Output paths

- Intermediate research: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/research/<asset-slug>/`
- Final dossiers: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/reports/<asset-slug>.md`
- Technical dossiers / source-audit originals: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/technical-reports/<asset-slug>.md`
- Per-asset verification: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/verification/<asset-slug>.md`
- Battery index: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/INDEX.md`
- Four-asset final battery verification: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/verification/final-battery-verification.md`
- Six-asset final battery verification: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/verification/final-six-asset-battery-verification.md`
- Pendle PT-market index: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/pendle-pt-index.md`
- Pendle PT-market final verification: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/verification/final-pendle-pt-battery-verification.md`
- X research artifacts: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/x-research/<topic-slug>.md`
- X research index: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/x-research/index.md`
- X research final verification: `projects/front-knowledge-base/dev/implementation/asset-risk-reports-mvp/verification/final-x-research-points-yield-verification.md`

## Board graph

Each asset has three parallel research cards, then synthesis, then verification.

### Saturn sUSDat — Ethereum mainnet

- `t_febf46af` — RESEARCH: Saturn sUSDat — onchain/admin
- `t_073b546d` — RESEARCH: Saturn sUSDat — issuer/backing/security
- `t_e77ef8de` — RESEARCH: Saturn sUSDat — transfer/liquidity/oracle/governance
- `t_9ac64412` — SYNTHESIZE: Saturn sUSDat — MVP asset dossier
  - parents: `t_febf46af`, `t_073b546d`, `t_e77ef8de`
- `t_4da59598` — VERIFY: Saturn sUSDat — dossier QA
  - parent: `t_9ac64412`

### apyx apyUSD — Ethereum mainnet

- `t_4eeef4fe` — RESEARCH: apyx apyUSD — onchain/admin
- `t_96b81463` — RESEARCH: apyx apyUSD — issuer/backing/security
- `t_e9bf5f7f` — RESEARCH: apyx apyUSD — transfer/liquidity/oracle/governance
- `t_8c481440` — SYNTHESIZE: apyx apyUSD — MVP asset dossier
  - parents: `t_4eeef4fe`, `t_96b81463`, `t_e9bf5f7f`
- `t_c77deba1` — VERIFY: apyx apyUSD — dossier QA
  - parent: `t_8c481440`

### Hastra PRIME — Ethereum mainnet

- `t_fb011cb4` — RESEARCH: Hastra PRIME — onchain/admin
- `t_82ecf098` — RESEARCH: Hastra PRIME — issuer/backing/security
- `t_0edca409` — RESEARCH: Hastra PRIME — transfer/liquidity/oracle/governance
- `t_6fa86a56` — SYNTHESIZE: Hastra PRIME — MVP asset dossier
  - parents: `t_fb011cb4`, `t_82ecf098`, `t_0edca409`
- `t_a5caae7e` — VERIFY: Hastra PRIME — dossier QA
  - parent: `t_6fa86a56`

### Centrifuge deSPXA — Base

- `t_7ea4fcb6` — RESEARCH: Centrifuge deSPXA — onchain/admin
- `t_7235a48f` — RESEARCH: Centrifuge deSPXA — issuer/backing/security
- `t_4174dbf0` — RESEARCH: Centrifuge deSPXA — transfer/liquidity/oracle/governance
- `t_9742558d` — SYNTHESIZE: Centrifuge deSPXA — MVP asset dossier
  - parents: `t_7ea4fcb6`, `t_7235a48f`, `t_4174dbf0`
- `t_1f1479a5` — VERIFY: Centrifuge deSPXA — dossier QA
  - parent: `t_9742558d`

### Saturn USDat — Ethereum mainnet expansion

- `t_21cec910` — RESEARCH: Saturn USDat — onchain/admin
- `t_bc33a5fd` — RESEARCH: Saturn USDat — issuer/backing/security
- `t_ee1235c4` — RESEARCH: Saturn USDat — transfer/liquidity/oracle/governance
- `t_b05fafeb` — SYNTHESIZE: Saturn USDat — technical + analyst risk report
  - parents: `t_21cec910`, `t_bc33a5fd`, `t_ee1235c4`
- `t_dcbf7b05` — VERIFY: Saturn USDat — technical + analyst report QA
  - parent: `t_b05fafeb`

### apyx apxUSD — Ethereum mainnet expansion

- `t_61242aa6` — RESEARCH: apyx apxUSD — onchain/admin
- `t_aa057914` — RESEARCH: apyx apxUSD — issuer/backing/security
- `t_ccf42d3f` — RESEARCH: apyx apxUSD — transfer/liquidity/oracle/governance
- `t_485ba2de` — SYNTHESIZE: apyx apxUSD — technical + analyst risk report
  - parents: `t_61242aa6`, `t_aa057914`, `t_ccf42d3f`
- `t_84fac95b` — VERIFY: apyx apxUSD — technical + analyst report QA
  - parent: `t_485ba2de`

### Four-asset battery fan-in (completed before expansion)

- `t_5e1d2816` — SYNTHESIZE: four-asset battery index and unknowns summary
  - parents: `t_4da59598`, `t_c77deba1`, `t_a5caae7e`, `t_1f1479a5`
- `t_685820b9` — VERIFY: final four-asset research battery
  - parent: `t_5e1d2816`

### Six-asset expansion fan-in

- `t_3daf2573` — SYNTHESIZE: six-asset battery index and unknowns summary
  - parents: `t_4da59598`, `t_c77deba1`, `t_a5caae7e`, `t_1f1479a5`, `t_dcbf7b05`, `t_84fac95b`
- `t_0bd85a03` — VERIFY: final six-asset research battery
  - parent: `t_3daf2573`

### Pendle PT-market expansion, gated after final six-asset verification

- `t_02893769` — ANALYZE: Pendle PT apyUSD — 27 Aug 2026 — Pendle PT market risk/economics
  - parent: `t_0bd85a03`
- `t_8176ae89` — VERIFY: Pendle PT apyUSD — 27 Aug 2026 — Pendle PT market QA
  - parent: `t_02893769`
- `t_f4f2d9a1` — ANALYZE: Pendle PT apxUSD — 05 Nov 2026 — Pendle PT market risk/economics
  - parent: `t_0bd85a03`
- `t_0e9401e2` — VERIFY: Pendle PT apxUSD — 05 Nov 2026 — Pendle PT market QA
  - parent: `t_f4f2d9a1`
- `t_cadda4d2` — ANALYZE: Pendle PT USDat — 27 Aug 2026 — Pendle PT market risk/economics
  - parent: `t_0bd85a03`
- `t_cd74bf73` — VERIFY: Pendle PT USDat — 27 Aug 2026 — Pendle PT market QA
  - parent: `t_cadda4d2`
- `t_6008b498` — ANALYZE: Pendle PT sUSDat — 27 Aug 2026 — Pendle PT market risk/economics
  - parent: `t_0bd85a03`
- `t_319b1f00` — VERIFY: Pendle PT sUSDat — 27 Aug 2026 — Pendle PT market QA
  - parent: `t_6008b498`
- `t_9248837c` — SYNTHESIZE: Pendle PT four-market index and unknowns summary
  - parents: `t_8176ae89`, `t_0e9401e2`, `t_cd74bf73`, `t_319b1f00`
- `t_653751cb` — VERIFY: final Pendle PT four-market analysis battery
  - parent: `t_9248837c`

### X research expansion, gated after final Pendle PT verification

- `t_64da510f` — X-RESEARCH: apyx apyUSD + Pendle PT apyUSD 27 Aug 2026 — points/STAC/yield expectations and risks
  - parent: `t_653751cb`
- `t_cf82fe90` — X-RESEARCH: apyx apxUSD + Pendle PT apxUSD 05 Nov 2026 — points/STAC/yield expectations and risks
  - parent: `t_653751cb`
- `t_e7cf4292` — X-RESEARCH: Saturn USDat + Pendle PT USDat 27 Aug 2026 — points/STAC/yield expectations and risks
  - parent: `t_653751cb`
- `t_04cf951c` — X-RESEARCH: Saturn sUSDat + Pendle PT sUSDat 27 Aug 2026 — points/STAC/yield expectations and risks
  - parent: `t_653751cb`
- `t_453c94e0` — SYNTHESIZE: X social expectations for apyx/Saturn tokens and Pendle PTs
  - parents: `t_64da510f`, `t_cf82fe90`, `t_e7cf4292`, `t_04cf951c`
- `t_ebf8a511` — VERIFY: final X research points/STAC/yield social-expectations battery
  - parent: `t_453c94e0`

## Operating commands

```bash
hermes kanban --board asset-risk-dossiers-mvp stats
hermes kanban --board asset-risk-dossiers-mvp list --json
hermes kanban --board asset-risk-dossiers-mvp diagnostics
hermes kanban --board asset-risk-dossiers-mvp dispatch --max 4 --failure-limit 1 --json
```

## Worker contract

Every card explicitly instructs the worker to:

- use `methodology.md` as the methodology contract;
- use `requirements-brief.md` for analyst-readable report presentation where the card writes reports;
- not use generic deep-research as the methodology;
- not choose, add, rank, or recommend tokens;
- produce objective, source-linked facts;
- include actual source URLs or local evidence paths in source lists/maps;
- for Pendle PT cards, inherit underlying-token risk from completed underlying reports and add PT-specific yield/economics, maturity/redemption, liquidity, pricing/oracle, and scenario-risk analysis;
- for X research cards, use the `x-research` skill and Hermes `x_search`, keep the work read-only, separate social speculation from verified facts, and capture points / airdrop / STAC-yield / PT fixed-yield assumptions plus risks;
- write missing material fields with `missing_behavior`;
- block instead of passing verification if methodology coverage fails.
