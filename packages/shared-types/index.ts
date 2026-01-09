// Account Types
export interface ConnectedAccount {
  id: string;
  userId: string;
  platform: 'tradovate' | 'ninjatrader' | 'rithmic';
  accountId: string;
  accountName: string;
  firm: 'apex' | 'topstep' | 'myfundedfutures' | 'other';
  accountType: 'eval' | 'pa' | 'funded';
  accountSize: number; // Starting balance in USD
  ruleSetVersion: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

// Rule Set Types
export interface RuleSet {
  id: string;
  firm: string;
  accountType: 'eval' | 'pa' | 'funded';
  version: string;
  rules: FirmRules;
  effectiveDate: string;
}

export interface FirmRules {
  trailingDrawdown?: TrailingDrawdownRule;
  dailyLossLimit?: DailyLossLimitRule;
  overallMaxLoss?: OverallMaxLossRule;
  maxPositionSize?: MaxPositionSizeRule;
  tradingHours?: TradingHoursRule;
  consistencyRule?: ConsistencyRule;
  minimumTradingDays?: number;
  inactivityDays?: number;
}

export interface TrailingDrawdownRule {
  enabled: boolean;
  maxDrawdownPercent: number; // e.g., 5 for 5%
  includeUnrealizedPnL: boolean;
  resetOnProfitTarget?: boolean;
  profitTargetPercent?: number;
}

export interface DailyLossLimitRule {
  enabled: boolean;
  maxLossAmount: number; // USD
  resetTime: string; // e.g., "17:00 CT"
  timezone: string;
}

export interface OverallMaxLossRule {
  enabled: boolean;
  maxLossAmount: number; // USD
  fromStartingBalance: boolean;
}

export interface MaxPositionSizeRule {
  enabled: boolean;
  maxContracts: number;
  maxRiskPerTrade?: number; // USD
}

export interface TradingHoursRule {
  enabled: boolean;
  allowedHours: Array<{
    day: number; // 0-6, Sunday-Saturday
    start: string; // "HH:MM"
    end: string; // "HH:MM"
    timezone: string;
  }>;
  forcedCloseTime?: string; // "HH:MM"
}

export interface ConsistencyRule {
  enabled: boolean;
  maxDailyProfitPercent?: number; // e.g., 30 for 30% of total profit
  minTradesPerDay?: number;
}

// Account State Types
export interface AccountState {
  accountId: string;
  timestamp: string;
  equity: number;
  balance: number;
  realizedPnL: number;
  unrealizedPnL: number;
  highWaterMark: number; // Highest equity reached
  openPositions: Position[];
  dailyPnL: number;
  ruleStates: RuleStates;
}

export interface Position {
  symbol: string;
  quantity: number; // Positive = long, negative = short
  avgPrice: number;
  currentPrice: number;
  unrealizedPnL: number;
  openedAt: string;
}

export interface RuleStates {
  trailingDrawdown?: RuleState;
  dailyLossLimit?: RuleState;
  overallMaxLoss?: RuleState;
  maxPositionSize?: RuleState;
  tradingHours?: RuleState;
  consistency?: RuleState;
}

export interface RuleState {
  ruleName: string;
  currentValue: number;
  threshold: number;
  remainingBuffer: number; // How much room until violation
  bufferPercent: number; // 0-100, how close to violation
  status: 'safe' | 'caution' | 'critical' | 'violated';
  distanceToViolation: DistanceMetric;
  warnings: string[];
}

export interface DistanceMetric {
  dollars?: number;
  ticks?: number;
  contracts?: number;
  timeRemaining?: string; // ISO duration
  percent?: number;
}

// WebSocket Message Types
export interface WebSocketMessage {
  type: 'account_state_update' | 'rule_violation' | 'warning' | 'error';
  accountId: string;
  data: any;
  timestamp: string;
}

export interface AccountStateUpdate extends WebSocketMessage {
  type: 'account_state_update';
  data: AccountState;
}

export interface RuleViolation extends WebSocketMessage {
  type: 'rule_violation';
  data: {
    ruleName: string;
    accountId: string;
    violatedAt: string;
    details: any;
  };
}

// User Types
export interface User {
  id: string;
  email: string;
  createdAt: string;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

// Dashboard Types
export interface AccountOverview {
  account: ConnectedAccount;
  state: AccountState;
  riskLevel: 'safe' | 'caution' | 'critical';
  criticalRules: RuleState[];
}

