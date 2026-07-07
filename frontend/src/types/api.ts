export interface Market {
  id: number;
  platform: 'kalshi' | 'polymarket';
  external_market_id: string;
  title: string | null;
  category: string | null;
  open_date: string | null;
  resolution_date: string | null;
  resolved: boolean;
  resolved_outcome: string | null;
}

export interface Trader {
  id: number;
  platform: string;
  external_trader_id: string;
}

export interface AnomalyScores {
  bet_id: number;
  self_score: number | null;
  market_score: number | null;
  lifecycle_weight: number;
  composite_score: number;
  flagged: boolean;
  scoring_mode: 'full' | 'market_only';
}

export interface FlaggedBet {
  id: number;
  market_id: number;
  trader_id: number | null;
  side: 'yes' | 'no';
  size: number;
  price: number;
  bet_timestamp: string;
  time_to_resolution_hours: number | null;
  created_at: string;
  // Anomaly data
  self_score: number | null;
  market_score: number | null;
  lifecycle_weight: number;
  composite_score: number;
  scoring_mode: 'full' | 'market_only';
  // Context
  market_title: string | null;
  platform: 'kalshi' | 'polymarket';
  category: string | null;
  trader_win_rate: number | null;
  calibration_hit_rate: number | null;
  calibration_sample_size: number | null;
}

export interface NewsEvent {
  id: number;
  bet_id: number;
  headline: string;
  source: string | null;
  published_at: string | null;
  url: string | null;
  relevance_score: number | null;
  sentiment_label: 'positive' | 'negative' | 'neutral' | null;
  sentiment_score: number | null;
  event_category: string | null;
}

export interface CalibrationSummary {
  total_flagged: number;
  correct: number;
  hit_rate: number;
  score_range: string;
  platform: string | null;
  category: string | null;
  caveat: string | null;
}

export interface TraderHistory {
  trader: Trader;
  bets: FlaggedBet[];
  median_bet_size: number | null;
  mad_bet_size: number | null;
  win_rate: number | null;
  total_resolved_bets: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface DashboardFilters {
  platform: 'all' | 'kalshi' | 'polymarket';
  category: string | null;
  scoreMin: number;
  scoreMax: number;
  flaggedOnly: boolean;
  sortBy: string;
  sortOrder: 'asc' | 'desc';
  limit: number;
  offset: number;
}
