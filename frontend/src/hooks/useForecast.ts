/**
 * React Query hooks for forecast data
 *
 * Uses queryKeys from services/queryKeys.ts to ensure consistent
 * cache key management and avoid caching collisions.
 */

import { useQuery } from '@tanstack/react-query';
import type { UseQueryOptions } from '@tanstack/react-query';
import { queryKeys } from '../services/queryKeys';
import { getForecasts } from '../services/api';
import type { Forecast } from '../services/types';

/**
 * Hook to fetch weather forecasts for a resort
 */
export const useForecast = (
  resortId: number,
  days: number = 7,
  options?: Omit<UseQueryOptions<Forecast[], Error>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: queryKeys.forecasts.resortDays(resortId, days),
    queryFn: () => getForecasts(resortId, days),
    staleTime: 30 * 60 * 1000, // 30 minutes (forecasts don't change as often)
    enabled: !!resortId,
    ...options,
  });
};
