/**
 * Home Page
 *
 * Main dashboard displaying all resorts with filtering options.
 */

import { useState, useMemo } from 'react';
import { useResortsWithConditions } from '../hooks/useResorts';
import { ResortCard } from '../components/resort';
import { LoadingSpinner, ErrorMessage } from '../components/common';

export default function Home() {
  const [stateFilter, setStateFilter] = useState<string>('');
  const [sortBy, setSortBy] = useState<'name' | 'snow' | 'quality'>('quality');

  const {
    data: resorts,
    isLoading,
    error,
    refetch,
  } = useResortsWithConditions({
    state: stateFilter || undefined,
  });

  // Get unique states for the filter dropdown
  const states = useMemo(() => {
    if (!resorts) return [];
    const stateSet = new Set(resorts.map((r) => r.state).filter(Boolean));
    return Array.from(stateSet).sort() as string[];
  }, [resorts]);

  // Sort resorts based on selection
  const sortedResorts = useMemo(() => {
    if (!resorts) return [];
    return [...resorts].sort((a, b) => {
      switch (sortBy) {
        case 'snow':
          return (
            (b.latest_condition?.new_snow_24h_in ?? -1) -
            (a.latest_condition?.new_snow_24h_in ?? -1)
          );
        case 'quality':
          return (
            (b.latest_condition?.snow_quality_score ?? -1) -
            (a.latest_condition?.snow_quality_score ?? -1)
          );
        case 'name':
        default:
          return a.name.localeCompare(b.name);
      }
    });
  }, [resorts, sortBy]);

  if (isLoading) {
    return <LoadingSpinner size="lg" message="Loading resorts..." />;
  }

  if (error) {
    return <ErrorMessage error={error} onRetry={() => refetch()} />;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Snow Conditions</h1>
        <p className="text-xl text-gray-600">
          Real-time conditions powered by automated data collection
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-4 mb-6 pb-6 border-b border-gray-200">
        {/* State Filter */}
        <div className="flex items-center space-x-2">
          <label
            htmlFor="state-filter"
            className="text-sm font-medium text-gray-700"
          >
            State:
          </label>
          <select
            id="state-filter"
            value={stateFilter}
            onChange={(e) => setStateFilter(e.target.value)}
            className="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
          >
            <option value="">All States</option>
            {states.map((state) => (
              <option key={state} value={state}>
                {state}
              </option>
            ))}
          </select>
        </div>

        {/* Sort By */}
        <div className="flex items-center space-x-2">
          <label htmlFor="sort-by" className="text-sm font-medium text-gray-700">
            Sort by:
          </label>
          <select
            id="sort-by"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
            className="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
          >
            <option value="quality">Snow Quality</option>
            <option value="snow">New Snow (24h)</option>
            <option value="name">Name</option>
          </select>
        </div>

        {/* Results Count */}
        <div className="ml-auto text-sm text-gray-500">
          {sortedResorts.length} resort{sortedResorts.length !== 1 ? 's' : ''}
        </div>
      </div>

      {/* Resort Grid */}
      {sortedResorts.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {sortedResorts.map((resort) => (
            <ResortCard key={resort.id} resort={resort} />
          ))}
        </div>
      ) : (
        <div className="text-center text-gray-500 py-12">
          No resorts found matching your filters
        </div>
      )}
    </div>
  );
}
