/**
 * Query Keys for React Query (TanStack Query)
 *
 * Centralized query key management to avoid caching collisions.
 * Uses factory pattern for type-safe, hierarchical key generation.
 */

export const queryKeys = {
  resorts: {
    all: ['resorts'] as const,
    lists: () => [...queryKeys.resorts.all, 'list'] as const,
    list: (filters?: { state?: string; region?: string }) =>
      [...queryKeys.resorts.lists(), filters] as const,
    withConditions: () => [...queryKeys.resorts.all, 'with-conditions'] as const,
    withConditionsFiltered: (filters?: { state?: string; region?: string }) =>
      [...queryKeys.resorts.withConditions(), filters] as const,
    details: () => [...queryKeys.resorts.all, 'detail'] as const,
    detail: (slug: string) => [...queryKeys.resorts.details(), slug] as const,
    history: (slug: string, hours?: number) =>
      [...queryKeys.resorts.detail(slug), 'history', hours] as const,
  },

  conditions: {
    all: ['conditions'] as const,
    latest: () => [...queryKeys.conditions.all, 'latest'] as const,
    latestFiltered: (filters?: { state?: string }) =>
      [...queryKeys.conditions.latest(), filters] as const,
    resort: (resortId: number) =>
      [...queryKeys.conditions.all, 'resort', resortId] as const,
    resortLatest: (resortId: number) =>
      [...queryKeys.conditions.resort(resortId), 'latest'] as const,
    compare: (resortIds: number[]) =>
      [...queryKeys.conditions.all, 'compare', resortIds.sort()] as const,
    powderAlert: (state?: string) =>
      [...queryKeys.conditions.all, 'powder-alert', state] as const,
  },

  forecasts: {
    all: ['forecasts'] as const,
    resort: (resortId: number) =>
      [...queryKeys.forecasts.all, resortId] as const,
    resortDays: (resortId: number, days?: number) =>
      [...queryKeys.forecasts.resort(resortId), days] as const,
  },

  alerts: {
    all: ['alerts'] as const,
    user: (userId: number) => [...queryKeys.alerts.all, 'user', userId] as const,
    detail: (alertId: number) =>
      [...queryKeys.alerts.all, 'detail', alertId] as const,
  },
} as const;

// Type helpers for query key inference
export type ResortQueryKeys = typeof queryKeys.resorts;
export type ConditionQueryKeys = typeof queryKeys.conditions;
export type ForecastQueryKeys = typeof queryKeys.forecasts;
export type AlertQueryKeys = typeof queryKeys.alerts;
