export interface SummaryResponse {
  total_records: number;
  date_range_start: string | null;
  date_range_end: string | null;
  keywords: string[];
  courts: string[];
  data_collected_at: string | null;
  min_required: number;
  sufficient: boolean;
}

export interface MonthlyPoint {
  period: string;
  count: number;
  ma_3m?: number | null;
  ma_12m?: number | null;
  yoy_pct_change?: number | null;
  volatility?: number | null;
}

export interface YearlyPoint {
  year: number;
  count: number;
}

export interface KeywordPoint {
  period: string;
  search_keyword: string;
  count: number;
}

export interface CourtPoint {
  court_type: string;
  count: number;
}

export interface AnomalyPoint {
  period: string;
  count: number;
  method: string;
  threshold: number;
  score: number;
  is_anomaly: boolean;
}

export interface DecompositionPoint {
  period: string;
  observed: number;
  trend: number | null;
  seasonal: number | null;
  resid: number | null;
}

export interface ForecastPoint {
  date: string;
  actual: number | null;
  forecast: number | null;
  lower_ci: number | null;
  upper_ci: number | null;
  model: string;
}

export interface ForecastResponse {
  disclaimer: string;
  points: ForecastPoint[];
}

export interface InsightsResponse {
  available: boolean;
  summary: string;
  observations: string[];
  interpretations: string[];
  hypotheses: string[];
  limitations: string[];
  reason?: string | null;
}

export interface ApiError {
  blocked: true;
  message: string;
}
