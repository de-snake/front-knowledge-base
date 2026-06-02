import { Address } from "viem";
// import { TokenRef } from "./assets";

export type OpportunityKind = "pool" | "strategy" | "market";
export type YieldType = "organic" | "incentivized" | "mixed";

export interface AssetRef {
  type: "stable" | "base" | "yield";
  ticker: string;
  price: number;

  // Optional objective metadata for assets with issuer, compliance, redemption,
  // or phantom-token mechanics. `redemptionWindowAsset` is only a routing flag:
  // if true, the agent should use opportunity access / terms links instead of
  // assuming ordinary ERC-20 transfer and exit behavior.
  issuerInfoUrl?: string | null;
  complianceRequired?: boolean;
  redemptionWindowAsset?: boolean;
  phantomToken?: boolean;
}

export interface TokenRef extends AssetRef {
  chainId: number;
  address: Address;
  symbol: string;
  decimals: number;
  // isPhantom: boolean;
}

// ═══════════════════════════════════════════════════════════════
// Rewards & Incentives
// ═══════════════════════════════════════════════════════════════

export interface TokenReward {
  type: "tokens";
  rewardToken: TokenRef;
  apy: number;
}

export interface PointsReward {
  type: "points";
  name: string;
  multiplier: number;
  condition: "deposit" | "cross-chain-deposit" | "holding";
}

interface IncentiveBase {
  description: string;
  startsAt: string;
  endsAt: string;
  isActive: boolean;
}

export interface TokenIncentive extends IncentiveBase {
  type: "tokens";
  reward: TokenReward;
}

export interface PointsIncentive extends IncentiveBase {
  type: "points";
  reward: PointsReward;
}

export type Incentive = TokenIncentive | PointsIncentive;

export interface ClaimableTokenIncentive extends TokenIncentive {
  claimable: number;
  claimableUsd: number;
  claimed: number;
  claimedUsd: number;
}

export interface ClaimablePointsIncentive extends PointsIncentive {
  earned: number;
}

export type ClaimableIncentive =
  | ClaimableTokenIncentive
  | ClaimablePointsIncentive;

// ═══════════════════════════════════════════════════════════════
// Yield Breakdown
// ═══════════════════════════════════════════════════════════════

/** Breakdown of all yield sources for an opportunity or position */
export interface YieldBreakdown<I extends Incentive = Incentive> {
  /** Organic yield from the protocol (supply rate, farming, etc.) */
  base: number;
  /** All active incentive programs (token rewards + points) */
  incentives: I[];
  /** base + sum of active token incentives' APY */
  totalApy: number;
}

export interface CollateralYield {
  token: TokenRef;
  /**
   * Collateral value denominated in the underlying (borrow) token,
   * divided by total position value in the same token.
   * All weights sum to 1.
   */
  weight: number;
  yield: YieldBreakdown;
}

/**
 * Yield breakdown for a leveraged strategy opportunity.
 *
 * weightedApy = sum(collateral[i].weight × collateral[i].yield.totalApy)
 * netApy = weightedApy × leverage − borrowApy × (leverage − 1)
 */
export interface LeveragedYieldBreakdown {
  leverage: number;
  collaterals: CollateralYield[];
  /** Pool borrow rate (positive number, represents cost) */
  borrowApy: number;
  /** Net APY after leverage and borrow costs */
  netApy: number;
}

// ═══════════════════════════════════════════════════════════════
// PnL Breakdown
// ═══════════════════════════════════════════════════════════════

export interface PointsPnl {
  name: string;
  earned: number;
}

export interface PnlBreakdown {
  /** PnL from organic yield (interest earned or farming) */
  interest: number;
  interestUsd: number;
  /** PnL from token reward incentives (claimed + claimable) */
  rewards: number;
  rewardsUsd: number;
  /** Points earned per program */
  points: PointsPnl[];
  /** interest + rewards (points excluded — not monetary) */
  total: number;
  totalUsd: number;
}

// ═══════════════════════════════════════════════════════════════
// Collaterals
// ═══════════════════════════════════════════════════════════════

export interface PoolCollateral {
  token: TokenRef;
  quotaLimit: number;
  quotaUsed: number;
  quotaRate: number;
  // price feeds

  // Product gap: verify whether quotaUsed is enough for current exposure,
  // or whether backend needs debt attributable to this collateral token.
  currentDebtByToken?: number;
}

export interface StrategyCollateral extends PoolCollateral {
  liquidationThreshold: number;
  yield: YieldBreakdown;
  // maxCollateral: number; quotaLimit - quotaUsed / collateralPriceInUnderlying

  // expectedWithdrawalTime: number;
  // isWithdrawalGuaranteed: boolean;
}

export interface UserCollateral extends Omit<StrategyCollateral, "yield"> {
  /**
   * Collateral value denominated in the underlying (borrow) token,
   * divided by total position value in the same token.
   * All weights sum to 1.
   */
  weight: number;
  balance: number;
  quota: number;
  yield: YieldBreakdown<ClaimableIncentive>;
  expectedWithdrawalTimestamp?: number;
}

// ═══════════════════════════════════════════════════════════════
// Opportunities
// ═══════════════════════════════════════════════════════════════

export interface Opportunity {
  id: string;
  chainId: number;
  type: "pool" | "strategy";
  title: string;
  curatorId: string;
  underlyingToken: TokenRef;
  // Downstream convenience field. Upstream access facts are asset-specific
  // and Credit Manager / DegenNFT-specific; this should be derived from them.
  access: {
    permissionless: boolean;
    kycRequired: boolean;
    kycUrl?: string | null;
  };
  // Downstream convenience field. Opportunity risk should be constructed from
  // upstream asset, leverage, curator, and Gearbox-specific facts.
  risk: {
    summary?: string | null;
    warnings: string[];
  };
}

export interface CuratorProfile {
  id: string;
  name: string;
  urls: string[];
  governance?: string;
  safeAddress?: Address;
  timelockAddress?: Address;
  firstOperationDate?: string;
  aumUsd?: number;
  badDebtIncidents?: number;
  parameterChangeHistorySummary?: string;
}

export interface PoolOpportunity extends Opportunity {
  type: "pool";
  poolAddress: Address;

  yield: YieldBreakdown;

  supplied: number;
  borrowed: number;
  utilization: number;

  tvl: string;
  tvlUsd: number;

  availableLiquidity: string;
  expectedLiquidity?: string;
  sharePrice?: number;
  withdrawalFee?: number;
  // isPaused: boolean;

  // irm info - how supplied liquidity changes supply apy?

  collaterals: PoolCollateral[];
}

// PoolOpportunityEnriched
// supplyApy7d: number;
// avgSupplyApy30D: number;
// incentives7d: Incentive[];

////////

export interface StrategyOpportunity extends Opportunity {
  type: "strategy";

  creditManagerAddress?: Address;
  minDebt: string;
  maxDebt: string;
  borrowableLiquidity: string;
  maxLeverage: number;

  borrowApy: number;

  /** Headline: best yield achievable at max leverage on best collateral */
  maxLeverageYield: LeveragedYieldBreakdown;
  /** Best collateral base yield without leverage */
  bestBaseYield: YieldBreakdown;

  collaterals: StrategyCollateral[];

  isPaused?: boolean;
  hasDelayedWithdrawal: boolean;
  allowedAdapters?: string[];
}

// ═══════════════════════════════════════════════════════════════
// Positions
// ═══════════════════════════════════════════════════════════════

export interface UserPoolPosition {
  chainId: number;
  poolAddress: Address;

  depositSize: number;
  depositSizeUsd: number;

  yield: YieldBreakdown<ClaimableIncentive>;

  pnl: PnlBreakdown;
}

/**
 * weightedApy = sum(collateral[i].weight × collateral[i].yield.totalApy)
 * netApy = weightedApy × leverage − borrowApy × (leverage − 1)
 */
export interface UserStrategyPosition {
  chainId: number;
  poolAddress: Address;
  creditManagerAddress: Address;
  creditAccountAddress: Address;

  leverage: number;
  borrowApy: number;
  netApy: number;

  debt: number;
  debtUsd: number;
  healthFactor: number;

  pnl: PnlBreakdown;

  collaterals: UserCollateral[];
  botPermissions?: BotPermission[];
}

// ═══════════════════════════════════════════════════════════════
// Product-dictated monitoring / access / execution additions
// ═══════════════════════════════════════════════════════════════

export interface GovernanceChange {
  scope: "pool" | "creditManager" | "asset" | "oracle" | "curator";
  scopeId: string;
  parameter: string;
  oldValue?: string | number | boolean | null;
  newValue: string | number | boolean | null;
  status: "pending" | "queued" | "executed" | "cancelled";
  timestamp?: string;
  affectedDomains: Array<
    | "yield"
    | "exposure"
    | "healthFactor"
    | "exit"
    | "oracle"
    | "access"
    | "operational"
  >;
}

export type OpportunityAccessStatus = "eligible" | "not_eligible" | "not_sure";

export type OpportunityAccessReason =
  | "missing_degen_nft"
  | "missing_asset_waitlist_approval"
  | "unknown";

export interface OpportunityAccessCheck {
  opportunityId: string;
  walletAddress: Address;
  status: OpportunityAccessStatus;
  reasons: OpportunityAccessReason[];
  actionUrl?: string | null;
}

export interface BotPermission {
  botAddress: Address;
  scopes: string[];
  status: "active" | "revoked" | "unexpected" | "unknown";
}

export type PoolActionType = "deposit" | "top_up" | "partial_exit" | "full_exit";

export type CreditAccountActionType =
  | "open"
  | "add_collateral"
  | "reduce_leverage"
  | "increase_leverage"
  | "partial_exit"
  | "full_exit"
  | "rebalance"
  | "claim"
  | "bot_permission_update";

export interface PreviewPackage {
  actionType: PoolActionType | CreditAccountActionType;
  before: unknown;
  after: unknown;
  calldata?: string;
  multicall?: string[];
  calldataHash: string;
  simulationBlock: number;
  gasEstimate?: number;
  hardBlockers: string[];
  warnings: string[];
}

export interface ExecutionReceipt {
  txHash: string;
  status: "success" | "failed" | "pending" | "unknown";
  blockNumber?: number;
  matchedPreviewHash?: boolean;
  resultingPositionId?: string;
}

// Product-level MCP names from the architecture doc.
// These are intentionally lightweight here and should not be treated as final API signatures.
export interface GearboxMcpProductReads {
  list_pool_opportunities(args: {
    chainId: number;
    walletAddress?: Address;
    underlyingAsset?: Address;
    amount?: number;
    asOf?: string;
  }): Promise<PoolOpportunity[]>;

  get_pool_due_diligence(args: {
    poolAddress: Address;
    amount?: number;
    walletAddress?: Address;
    includeT2?: boolean;
  }): Promise<PoolOpportunity>;

  list_credit_account_opportunities(args: {
    chainId: number;
    walletAddress?: Address;
    underlyingAsset?: Address;
    amount?: number;
    strategyFilter?: string;
    asOf?: string;
  }): Promise<StrategyOpportunity[]>;

  get_credit_account_due_diligence(args: {
    creditManagerAddress: Address;
    targetCollateral?: Address;
    amount?: number;
    targetLeverage?: number;
    walletAddress?: Address;
    includeT2?: boolean;
  }): Promise<StrategyOpportunity>;

  check_opportunity_access(args: {
    opportunityId: string;
    walletAddress: Address;
  }): Promise<OpportunityAccessCheck>;

  list_user_positions(args: {
    chainId: number;
    walletAddress: Address;
    includeClosed?: boolean;
  }): Promise<{
    pools: UserPoolPosition[];
    strategies: UserStrategyPosition[];
  }>;

  get_lp_monitoring_dataset(args: {
    chainId: number;
    walletAddress: Address;
    poolAddress: Address;
    since?: string;
    includeT2?: boolean;
  }): Promise<UserPoolPosition>;

  get_credit_account_monitoring_dataset(args: {
    creditAccountAddress: Address;
    since?: string;
    includeT2?: boolean;
  }): Promise<UserStrategyPosition>;

  preview_pool_action(args: unknown): Promise<PreviewPackage>;
  preview_credit_account_action(args: unknown): Promise<PreviewPackage>;
  get_execution_receipt(args: { txHash: string; expectedPreviewHash?: string }): Promise<ExecutionReceipt>;
}
