/**
 * React Query hooks for conditions data
 *
 * Uses queryKeys from services/queryKeys.ts to ensure consistent
 * cache key management and avoid caching collisions.
 */

import { useQuery } from '@tanstack/react-query';
import type { UseQueryOptions } from '@tanstack/react-query';
import { queryKeys } from '../services/queryKeys';
import {
  getLatestConditions,
  getResortConditions,
  getResortLatestCondition,
  compareConditions,
  getPowderAlerts,
} from '../services/api';
import type {
  Conditions,
  ResortWithConditions,
  PowderAlertResult,
} from '../services/types';

/**
 * Hook to fetch latest conditions across all resorts
 */
export const useLatestConditions = (
  state?: string,
  options?: Omit<UseQueryOptions<Conditions[], Error>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: queryKeys.conditions.latestFiltered({ state }),
    queryFn: () => getLatestConditions(state),
    staleTime: 3 * 60 * 1000, // 3 minutes
    refetchInterval: 5 * 60 * 1000, // Auto-refetch every 5 minutes
    ...options,
  });
};

/**
 * Hook to fetch conditions for a specific resort
 */
export const useResortConditions = (
  resortId: number,
  hours: number = 24,
  options?: Omit<UseQueryOptions<Conditions[], Error>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: queryKeys.conditions.resort(resortId),
    queryFn: () => getResortConditions(resortId, hours),
    staleTime: 5 * 60 * 1000, // 5 minutes
    enabled: !!resortId,
    ...options,
  });
};

/**
 * Hook to fetch the latest condition for a specific resort
 */
export const useResortLatestCondition = (
  resortId: number,
  options?: Omit<
    UseQueryOptions<Conditions | null, Error>,
    'queryKey' | 'queryFn'
  >
) => {
  return useQuery({
    queryKey: queryKeys.conditions.resortLatest(resortId),
    queryFn: () => getResortLatestCondition(resortId),
    staleTime: 3 * 60 * 1000, // 3 minutes
    enabled: !!resortId,
    ...options,
  });
};

/**
 * Hook to compare conditions between multiple resorts
 */
export const useCompareConditions = (
  resortIds: number[],
  options?: Omit<
    UseQueryOptions<ResortWithConditions[], Error>,
    'queryKey' | 'queryFn'
  >
) => {
  return useQuery({
    queryKey: queryKeys.conditions.compare(resortIds),
    queryFn: () => compareConditions(resortIds),
    staleTime: 3 * 60 * 1000, // 3 minutes
    enabled: resortIds.length > 0,
    ...options,
  });
};

/**
 * Hook to fetch powder alert results
 */
export const usePowderAlerts = (
  state?: string,
  minSnowfall: number = 6,
  options?: Omit<
    UseQueryOptions<PowderAlertResult[], Error>,
    'queryKey' | 'queryFn'
  >
) => {
  return useQuery({
    queryKey: queryKeys.conditions.powderAlert(state),
    queryFn: () => getPowderAlerts(state, minSnowfall),
    staleTime: 5 * 60 * 1000, // 5 minutes
    ...options,
  });
};
