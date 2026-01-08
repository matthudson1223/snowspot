/**
 * API Service using Axios
 *
 * Centralized API client for all SnowSpot backend interactions.
 */

import axios from 'axios';
import type { AxiosInstance, AxiosError } from 'axios';
import type {
  Resort,
  ResortWithConditions,
  Conditions,
  Forecast,
  Alert,
  ApiResponse,
  ResortHistory,
  ResortFilters,
  PowderAlertResult,
} from './types';

// API Base URL from environment variable or default
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Create Axios instance with default configuration
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth tokens (if needed)
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: string; message?: string }>) => {
    // Handle common error cases
    if (error.response) {
      const message =
        error.response.data?.detail ||
        error.response.data?.message ||
        'An error occurred';
      console.error(`API Error [${error.response.status}]:`, message);
    } else if (error.request) {
      console.error('Network Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// ============================================================================
// Resort Endpoints
// ============================================================================

/**
 * Get all resorts with optional filtering
 */
export const getResorts = async (filters?: ResortFilters): Promise<Resort[]> => {
  const response = await api.get<ApiResponse<Resort[]>>('/resorts/', {
    params: {
      state: filters?.state,
      region: filters?.region,
      active_only: filters?.active_only ?? true,
    },
  });
  return response.data.data;
};

/**
 * Get resorts with their latest conditions
 */
export const getResortsWithConditions = async (
  filters?: ResortFilters
): Promise<ResortWithConditions[]> => {
  const response = await api.get<ApiResponse<ResortWithConditions[]>>(
    '/resorts/with-conditions',
    {
      params: {
        state: filters?.state,
        region: filters?.region,
        active_only: filters?.active_only ?? true,
      },
    }
  );
  return response.data.data;
};

/**
 * Get a single resort by slug with optional conditions
 */
export const getResort = async (
  slug: string,
  includeConditions: boolean = true
): Promise<ResortWithConditions> => {
  const response = await api.get<ApiResponse<ResortWithConditions>>(
    `/resorts/${slug}`,
    {
      params: { include_conditions: includeConditions },
    }
  );
  return response.data.data;
};

/**
 * Get historical conditions for a resort
 */
export const getResortHistory = async (
  slug: string,
  hours: number = 24
): Promise<ResortHistory> => {
  const response = await api.get<ApiResponse<ResortHistory>>(
    `/resorts/${slug}/history`,
    {
      params: { hours },
    }
  );
  return response.data.data;
};

// ============================================================================
// Conditions Endpoints
// ============================================================================

/**
 * Get latest conditions across all resorts
 */
export const getLatestConditions = async (
  state?: string
): Promise<Conditions[]> => {
  const response = await api.get<ApiResponse<Conditions[]>>(
    '/conditions/latest',
    {
      params: { state },
    }
  );
  return response.data.data;
};

/**
 * Get conditions for a specific resort
 */
export const getResortConditions = async (
  resortId: number,
  hours: number = 24
): Promise<Conditions[]> => {
  const response = await api.get<ApiResponse<Conditions[]>>(
    `/conditions/resort/${resortId}`,
    {
      params: { hours },
    }
  );
  return response.data.data;
};

/**
 * Get latest condition for a specific resort
 */
export const getResortLatestCondition = async (
  resortId: number
): Promise<Conditions | null> => {
  const response = await api.get<ApiResponse<Conditions | null>>(
    `/conditions/${resortId}/latest`
  );
  return response.data.data;
};

/**
 * Compare conditions between multiple resorts
 */
export const compareConditions = async (
  resortIds: number[]
): Promise<ResortWithConditions[]> => {
  const response = await api.get<ApiResponse<ResortWithConditions[]>>(
    '/conditions/compare',
    {
      params: { resort_ids: resortIds.join(',') },
    }
  );
  return response.data.data;
};

/**
 * Get powder alert results (resorts with significant new snow)
 */
export const getPowderAlerts = async (
  state?: string,
  minSnowfall: number = 6
): Promise<PowderAlertResult[]> => {
  const response = await api.get<ApiResponse<PowderAlertResult[]>>(
    '/conditions/powder-alert',
    {
      params: { state, min_snowfall_in: minSnowfall },
    }
  );
  return response.data.data;
};

// ============================================================================
// Forecast Endpoints
// ============================================================================

/**
 * Get weather forecasts for a resort
 */
export const getForecasts = async (
  resortId: number,
  days: number = 7
): Promise<Forecast[]> => {
  const response = await api.get<ApiResponse<Forecast[]>>(
    `/forecasts/${resortId}`,
    {
      params: { days },
    }
  );
  return response.data.data;
};

// ============================================================================
// Alert Endpoints
// ============================================================================

/**
 * Get alerts for the current user
 */
export const getUserAlerts = async (userId: number): Promise<Alert[]> => {
  const response = await api.get<ApiResponse<Alert[]>>(`/alerts/user/${userId}`);
  return response.data.data;
};

/**
 * Create a new alert
 */
export const createAlert = async (
  alert: Omit<Alert, 'id' | 'created_at' | 'updated_at' | 'last_triggered_at' | 'trigger_count'>
): Promise<Alert> => {
  const response = await api.post<ApiResponse<Alert>>('/alerts/', alert);
  return response.data.data;
};

/**
 * Update an existing alert
 */
export const updateAlert = async (
  alertId: number,
  updates: Partial<Alert>
): Promise<Alert> => {
  const response = await api.patch<ApiResponse<Alert>>(
    `/alerts/${alertId}`,
    updates
  );
  return response.data.data;
};

/**
 * Delete an alert
 */
export const deleteAlert = async (alertId: number): Promise<void> => {
  await api.delete(`/alerts/${alertId}`);
};

// ============================================================================
// Health Check
// ============================================================================

/**
 * Check API health status
 */
export const healthCheck = async (): Promise<{
  status: string;
  database: string;
  redis: string;
  celery: string;
}> => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
