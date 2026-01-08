/**
 * TypeScript interfaces for the SnowSpot API
 */

export interface Resort {
  id: number;
  name: string;
  slug: string;
  latitude: number;
  longitude: number;
  timezone: string;
  state: string | null;
  region: string | null;
  country: string;
  base_elevation_ft: number | null;
  summit_elevation_ft: number | null;
  vertical_drop_ft: number | null;
  total_lifts: number | null;
  total_runs: number | null;
  total_acres: number | null;
  official_url: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Conditions {
  resort_id: number;
  time: string;
  base_depth_in: number | null;
  summit_depth_in: number | null;
  new_snow_24h_in: number | null;
  new_snow_48h_in: number | null;
  new_snow_7d_in: number | null;
  temperature_f: number | null;
  wind_speed_mph: number | null;
  wind_direction: number | null;
  precipitation_in: number | null;
  humidity_percent: number | null;
  visibility_miles: number | null;
  lifts_open: number | null;
  lifts_total: number | null;
  runs_open: number | null;
  runs_total: number | null;
  terrain_parks_open: number | null;
  snow_quality_score: number | null;
  skiability_index: number | null;
  crowd_level: number | null;
  data_sources: Record<string, unknown> | null;
  confidence_score: number | null;
}

export interface ResortWithConditions extends Resort {
  latest_conditions: Conditions | null;
}

export interface Forecast {
  id: number;
  resort_id: number;
  generated_at: string;
  forecast_for: string;
  temperature_high_f: number | null;
  temperature_low_f: number | null;
  predicted_snowfall_in: number | null;
  wind_speed_mph: number | null;
  precipitation_prob_percent: number | null;
  source: string;
  model: string | null;
  confidence: number | null;
}

export interface Alert {
  id: number;
  user_id: number;
  resort_id: number;
  alert_type: 'powder' | 'conditions' | 'crowds';
  threshold_config: Record<string, unknown>;
  delivery_method: 'email' | 'push' | 'sms';
  is_active: boolean;
  last_triggered_at: string | null;
  trigger_count: number;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: number;
  email: string;
  name: string | null;
  favorite_resort_ids: number[];
  timezone: string;
  is_active: boolean;
  email_verified: boolean;
  created_at: string;
  last_login: string | null;
}

// API Response types following the standardized envelope
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  meta?: {
    timestamp: string;
    pagination?: {
      total: number;
      page: number;
      per_page: number;
      total_pages: number;
    };
  };
}

export interface ResortHistory {
  resort: string;
  history: Conditions[];
}

export interface PowderAlertResult {
  resort: ResortWithConditions;
  new_snow_24h_in: number;
  snow_quality_score: number;
}

// Filter types
export interface ResortFilters {
  state?: string;
  region?: string;
  active_only?: boolean;
}

export interface ConditionsFilters {
  state?: string;
}
