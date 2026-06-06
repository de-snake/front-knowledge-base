# Gearbox price-feed parsing reference

Source: [Gearbox Curators — Add required Price Feeds](https://docs.gearbox.finance/curators/add-required-price-feeds).

Use this reference inside the oracle analysis workflow whenever the protocol scope is Gearbox.

## PFS context

- The Price Feed Store (PFS) is a chain-specific registry of tokens and price feeds available within Gearbox on that chain.
- A token must be added to PFS, with available price feeds, before it can be used as collateral.
- Only the chain-specific **Instance Owner** multisig can add or update PFS entries.
- PFS status is a technical availability condition, not a risk conclusion. The workflow still needs a side-aware oracle memo for LPs, borrowers, liquidators, and curators.

## Side-aware invariant

The same Gearbox feed can be favorable for one side and unfavorable for another.

Do not write a single universal verdict such as `safe`, `unsafe`, `good`, or `bad`.

Every conclusion must name:

- the position side: pool LP, Credit Account borrower, liquidator, or curator/operator;
- the token role: collateral token, borrowed token, pool quoted token, vault share, LP token, PT, or transition-stage asset;
- the stress direction: price down, price up, depeg, stale update, liquidity loss, manipulation, or delayed redemption;
- the loss bearer: borrower liquidation, LP bad debt, LP locked liquidity, liquidator execution risk, or curator intervention requirement.

Examples:

- A hardcoded or constant feed can be borrower-friendly for collateral during a temporary secondary-market drop because it avoids immediate liquidation, while being LP-unfriendly if the collateral cannot be sold near the hardcoded value.
- A market feed can protect LPs by recognizing collateral stress early, while being borrower-unfriendly when temporary thin-liquidity dislocations trigger liquidation.
- An upper bound on a borrowed token can protect borrowers from debt-value spikes, while an upper bound on collateral can protect LPs from manipulated collateral inflation and can cap borrower upside from genuine appreciation.

## Gearbox feed-source inventory

### External AggregatorV3-compatible feed

Official guide examples: Chainlink, Redstone push, EO, custom AggregatorV3-compatible feeds, Midas NAV.

Configuration signals:

- `priceFeedAddress`.
- `Staleness Period`.
- Provider identity and methodology in the feed name, for example `SampleDebtToken (Chainlink)` or `mTBILL (Midas NAV)`.

Parsing rule:

- Classify by the underlying economic source, not by the `External` wrapper label.
- Chainlink/EO/Redstone market feeds are usually `market` or market-reference primitives.
- Midas NAV or issuer-style feeds may be `NAV` or `fundamental`; verify the provider methodology.
- Record heartbeat or expected update cadence and compare it with Gearbox staleness period. The guide recommends heartbeat plus a small buffer: for 24-hour feeds, `87,300s` on slower chains such as Ethereum, or `86,520s` on faster chains.

### ERC4626 exchange-rate feed

Configuration signals:

- `Vault`.
- `underlyingPriceFeed`.
- The vault `asset()` method identifies which token the underlying feed must price.

Formula:

```text
vault share USD price
= ERC4626 mint/redeem exchange rate
  × underlying asset USD feed
```

Parsing rule:

- Classify the exchange-rate node as `NAV` / accounting unless evidence shows the exchange rate is directly market-derived.
- Recurse into `underlyingPriceFeed` and classify that child independently.
- Audit whether the ERC4626 accounting value is executable at the relevant size and timing. Queue-based or permissioned redemption can make this borrower-friendly and LP-risky under stress.

### Pyth pull feed

Configuration signals:

- `Token`.
- `priceFeedId`.
- Pyth singleton contract address for the chain.
- `maxConfToPriceRatio` in basis points.
- `Staleness Period`; guide recommendation for pull feeds: `240s`.
- Newly deployed Pyth feeds require a small ETH transfer to the feed address before they function and can be added to PFS.

Parsing rule:

- Classify the economic source by the Pyth feed methodology, for example market or redemption-rate feed.
- Audit price, confidence interval, confidence-to-price ratio, update timestamp, and whether fresh update data is needed for the transaction path.
- Treat excessive confidence interval or stale data as a revert / blocked-operation condition, not merely a soft warning.

### Redstone pull feed

Configuration signals:

- `Token`.
- `dataServiceId`.
- `dataFeedId`.
- `signersThreshold`.
- signer addresses.

Parsing rule:

- Classify by Redstone feed methodology, for example market or fundamental.
- Audit signer threshold, signer set, update cadence, and pull-update operational requirements.
- The guide notes Redstone currently has up to five nodes and historically Gearbox used threshold `5`, with the tradeoff that temporary node outages can block operation.

### Bounded / upper-bound feed

Official guide side framing:

- Bound borrowed tokens to protect borrowers from liquidations.
- Bound collateral tokens to protect LPs from price manipulation.

Parsing rule:

- Treat the bounded wrapper as `hybrid` because the economic behavior depends on the underlying feed plus the bound.
- Record the underlying feed and bound value.
- The same bound has different side effects depending on token role:
  - borrowed token: can protect borrowers from debt-value spikes;
  - collateral token: can protect LPs from inflated collateral valuations;
  - collateral token with real appreciation: can cap borrower collateral value;
  - collateral token with real collapse below bound: may still depend on the underlying path and safe-pricing rules.
- For PT and LP setups, the official guide commonly deploys a bounded Gearbox oracle with `bound = 1` after the PT TWAP or composite feed; parse the underlying feed before evaluating the bound.

### Composite feed

Official guide purpose: multiply two feed prices, often for correlated token pairs.

Formula:

```text
composite price = feed1 price × feed2 price
```

Parsing rule:

- Treat as `hybrid`.
- Recurse into both feeds.
- Explain the economic meaning of each leg, for example `PT/SY × SY/USD` or `staked-token/base × base/USD`.
- Do not average the child risks. The weak link or delayed leg can dominate the stress behavior.

### Constant price feed

Official guide purpose: hardcode pegged assets or apply a premium/discount when combined with a composite feed.

Parsing rule:

- Classify as `hardcoded`.
- Record the invariant being assumed.
- Evaluate by side:
  - borrower-friendly when a collateral depeg is temporary and the hardcoded feed avoids liquidation;
  - LP-risky when executable exit value diverges from the constant and liquidations cannot clear;
  - borrower-risky when the hardcoded value suppresses genuine collateral upside or fails to reflect a favorable debt-token move.

### Curve LP feed

Configuration signals:

- Feed type: `Curve_stable` or `Curve_crypto`.
- `Token`: LP token address.
- `Pool`: Curve pool address.
- `underlyingPriceFeed0/1/2/3`: feeds for pool tokens by index.

Parsing rule:

- Treat as `hybrid`: pool share accounting plus underlying-token price feeds.
- Recurse into every underlying token feed.
- Audit pool composition, balances, amplification/crypto-pool dynamics, and whether the LP token can exit near the oracle value at the analyzed size.

### Curve TWAP token feed

Official guide purpose: price experimental tokens based on Curve pool trades.

Parsing rule:

- Classify the Curve TWAP component as `market` because it observes DEX trade-derived price.
- Recurse into any child quote feed used to express the pool price in USD.
- Audit pool liquidity, imbalance, TWAP window, manipulation cost, and whether the relevant position size can exit through the same market.

### Pendle PT TWAP feed

Official guide deployment signals:

- Before deployment, Pendle market cardinality should be at least `twapWindow / blockTime + 1`.
- Cardinality check: LP contract `_storage()[4]`.
- Cardinality update: call `increaseObservationsCardinalityNext` on the LP contract.
- Factory path: deploy PT-to-SY oracle with `createOracle`, `baseOracleType = 0` for PT-to-SY price, then add as external with staleness period `1`, combine with SY/USD in a composite feed, and wrap with a bounded feed with `bound = 1`.
- Direct Gearbox PT TWAP type parameters: `market`, `UnderlyingPriceFeed`, `priceToSy`, `twapWindow`; guide says `1800s` was usually used.

Parsing rule:

- Treat the Pendle PT TWAP component as `market` because it observes PT/SY market price over a TWAP window.
- Recurse into `UnderlyingPriceFeed`, which should price SY in USD when `priceToSy` is checked; otherwise understand whether the child prices the asset instead of SY.
- Record maturity behavior and separate PT discount/yield risk from underlying SY/USD oracle risk.
- Audit TWAP cardinality/readiness and whether the market has enough liquidity for liquidation or exit.
- If wrapped in bounded/composite layers, classify the top-level path as `hybrid`, not simply `Pendle`.

### Pendle LP feed

Official guide deployment signals:

- Factory `baseOracleType = 2` for LP-to-SY price.
- Then combine LP-to-SY with SY/USD in a composite feed and wrap with a bounded feed with `bound = 1`.

Parsing rule:

- Treat as `hybrid`: LP-to-SY market/accounting layer plus SY/USD child feed plus bound.
- Audit cardinality, LP liquidity, SY/USD source, and bound side effects.

### Kodiak Island feed

Configuration signals:

- `kodiakIsland`.
- `PriceFeed0` and `PriceFeed1` for the island underlying tokens.

Parsing rule:

- Treat as `hybrid`: island share price plus both underlying-token USD feeds.
- Recurse into both child feeds and audit island liquidity/share accounting.

### Balancer V3 LP feed

Official guide signals:

- Balancer chainlink-compatible factory addresses are listed for supported chains.
- Underlying token feeds used for deployment should not be updatable pull feeds such as Redstone Pull or Pyth pull.

Parsing rule:

- Treat as `hybrid`: Balancer pool share pricing plus underlying-token feeds.
- Recurse into every underlying feed and record the non-updatable-feed constraint.

## Generic Gearbox probes

Start with these calls when a feed address is known, then add feed-type-specific getters from verified source or ABI.

```text
contractType()(bytes32)
version()(uint256)
decimals()(uint8)
description()(string)
stalenessPeriod()(uint32)
latestRoundData()(uint80,int256,uint256,uint256,uint80)
priceFeed()(address)
underlyingPriceFeed()(address)
basePriceFeed()(address)
targetPriceFeed()(address)
token()(address)
vault()(address)
asset()(address)
pool()(address)
market()(address)
sy()(address)
pt()(address)
priceToSy()(bool)
twapWindow()(uint32)
lowerBound()(int256)
upperBound()(int256)
skipCheck()(bool)
```

Getter names are not guaranteed across all feed implementations. If a getter reverts, record the revert and inspect verified source or constructor arguments rather than assuming the child does not exist.
