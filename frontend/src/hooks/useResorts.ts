/**
 * React Query hooks for resort data
 *
 * Uses queryKeys from services/queryKeys.ts to ensure consistent
 * cache key management and avoid caching collisions.
 */

import { useQuery } from '@tanstack/react-query';
import type { UseQueryOptions } from '@tanstack/react-query';
import { queryKeys } from '../services/queryKeys';
import {
  getResorts,
  getResortsWithConditions,
  getResort,
  getResortHistory,
} from '../services/api';
import type {
  Resort,
  ResortWithConditions,
  ResortHistory,
  ResortFilters,
} from '../services/types';

/**
 * Hook to fetch all resorts
 */
export const useResorts = (
  filters?: ResortFilters,
  options?: Omit<UseQueryOptions<Resort[], Error>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: queryKeys.resorts.list(filters),
    queryFn: () => getResorts(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
    ...options,
  });
};

/**
 * Hook to fetch resorts with their latest conditions
 */
export const useResortsWithConditions = (
  filters?: ResortFilters,
  options?: Omit<
    UseQueryOptions<ResortWithConditions[], Error>,
    'queryKey' | 'queryFn'
  >
) => {
  return useQuery({
    queryKey: queryKeys.resorts.withConditionsFiltered(filters),
    queryFn: () => getResortsWithConditions(filters),
    staleTime: 3 * 60 * 1000, // 3 minutes (conditions update frequently)
    refetchInterval: 5 * 60 * 1000, // Auto-refetch every 5 minutes
    ...options,
  });
};

/**
 * Hook to fetch a single resort by slug
 */
export const useResort = (
  slug: string,
  options?: Omit<
    UseQueryOptions<ResortWithConditions, Error>,
    'queryKey' | 'queryFn'
  >
) => {
  return useQuery({
    queryKey: queryKeys.resorts.detail(slug),
    queryFn: () => getResort(slug),
    staleTime: 3 * 60 * 1000, // 3 minutes
    enabled: !!slug,
    ...options,
  });
};

/**
 * Hook to fetch resort history
 */
export const useResortHistory = (
  slug: string,
  hours: number = 24,
  options?: Omit<UseQueryOptions<ResortHistory, Error>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: queryKeys.resorts.history(slug, hours),
    queryFn: () => getResortHistory(slug, hours),
    staleTime: 10 * 60 * 1000, // 10 minutes
    enabled: !!slug,
    ...options,
  });
};
