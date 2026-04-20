
### Pool LP (passive lender)

A depositor who wants yield on a base asset without operational overhead, volatility in principal, or liquidation exposure. 
#### Typical profiles

- **DeFi-native yield farmer** — cares about net APY vs comparable venues (Aave, Morpho, Euler), sustainability of incentives, and exit liquidity.
- **Treasury / fund operator** — cares about counterparty surface, governance transparency, curator track record, and concentration.
- **Institutional / RWA-oriented allocator** — cares about all of the above plus compliance-layer risks (freeze authority, liquidator whitelist, redemption mechanics).
- **Agent (LLM) acting for any of the above** — needs the same facts, serialised.

The LP has **no health factor, no liquidation, no leverage**. 
#### Loss vectors
- yield decay, 
- withdrawal blocked by utilisation, 
- bad-debt socialisation from a downstream Credit Manager, 
- silent exposure changes by the curator, 
- and — for RWA-backed pools — frozen accounts and liquidator scarcity.

### CA operator (leveraged user) // needs rewrite

> Они все ищут ответ на вопрос «готов ли я взять такой риск чтобы получить такую доходность»
> 
> Просто кто-то после взгляда на размер пула, твл коллатерала и куратора говорит похуй
> Кто-то дойдет до ораклов и ликвидности коллатерала
> А кто-то еще попросит куратора показать лицензию
> 
> Это как будто немного облегчает задачу
> Мы собираем все данные, которые нужны самым требовательным, и пропускаем их через три фильтра по степени сложности для восприятия

A user who opens and manages an isolated Credit Account to run a leveraged strategy. 
#### Typical profiles

- **Leveraged-yield farmer** — stETH / USDe / LP-token loop; cares about `collateral yield × leverage − borrow cost − quota − fees` and HF stability.
- **Structured-product / fund desk** — treats CAs as building blocks for a larger portfolio; cares about liquidity and exit paths under stress.
- **RWA-collateral user (new, post-Securitize integration)** — wants leverage on tokenised securities; additionally cares about freeze authority, redemption windows, KYC validity.
- **Agent (LLM) acting for any of the above** — runs the same decision loop autonomously or with human approval at Execute.

The CA operator owns an isolated position. 
#### Loss vectors 
- liquidation, 
- adverse LT ramp, 
  >есть процедура когда куратор поменял ЛТ. например блоы 0.9, стало 0.8. и ЛТ начнет постепенно уменьшаться в течение определенного срока (тоже параметр). если у тебя ХФ был 1.05 -  тебя гарантированно к концу процедуры ликвиднет…
  
- quota interest bleed, 
  > quota rate повысили резко - и у тебя проценты накапали и тебя ликвиднуло

- oracle manipulation, ? why not a problem for LPs?
  >ну для КА юзера это супер критично… тебя ликвиднет если цена чет не так…
  
- borrow-rate spike, 
  >у тебя проценты накапали и тебя ликвиднуло (например если кто то вытащить из пула много денег и утилизация подскочет)
  
- forbidden-token safe-pricing, ? 
  >forbidden токен - это когда этот токен больше нельзя как коллатерал использовать
  
- expirable CM, 
  >есть процедура когда кредит менеджер выключается - и тогда все аккаунты будут ликидированы.
  
- entry/exit slippage, 
  > ну тут про слипадж - тебе интерфейс показал что у тебя ХФ будет 1.001 при открытии - ты открыл акк, но цена в прцоессе чутка поменялась и после открытия тебя сразу ликвиднуло…
  
- and — for RWA — account freeze, KYC revocation, investor reassignment. 
  >у Секьюритайз есть процедура - например  EOA и юзер там KYC проходил. потом например к ним запрос приходят что актив морозится. у нас морозится кредит акк тоже. или что юзер умер и теперь владелец актива другой EOA (нотариус написал) - там есть похожие процедуры.

