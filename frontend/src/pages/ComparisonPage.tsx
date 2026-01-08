/**
 * Comparison Page
 *
 * Compare conditions between multiple resorts.
 */

import { useState } from 'react';
import { useResortsWithConditions } from '../hooks/useResorts';
import { useCompareConditions } from '../hooks/useConditions';
import { LoadingSpinner, ErrorMessage } from '../components/common';
import {
  formatNumber,
  formatTemperature,
  getQualityLabel,
  getQualityColorClass,
} from '../utils/formatting';

export default function ComparisonPage() {
  const [selectedResorts, setSelectedResorts] = useState<number[]>([]);

  const {
    data: allResorts,
    isLoading: resortsLoading,
    error: resortsError,
  } = useResortsWithConditions();

  const {
    data: comparisonData,
    isLoading: comparisonLoading,
  } = useCompareConditions(selectedResorts);

  const toggleResort = (resortId: number) => {
    setSelectedResorts((prev) =>
      prev.includes(resortId)
        ? prev.filter((id) => id !== resortId)
        : [...prev, resortId]
    );
  };

  if (resortsLoading) {
    return <LoadingSpinner size="lg" message="Loading resorts..." />;
  }

  if (resortsError) {
    return <ErrorMessage error={resortsError} />;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Compare Resorts</h1>

      {/* Resort Selection */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Select Resorts to Compare ({selectedResorts.length} selected)
        </h2>
        <div className="flex flex-wrap gap-2">
          {allResorts?.map((resort) => (
            <button
              key={resort.id}
              onClick={() => toggleResort(resort.id)}
              className={`px-3 py-1.5 text-sm rounded-full transition-colors ${
                selectedResorts.includes(resort.id)
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {resort.name}
            </button>
          ))}
        </div>
      </div>

      {/* Comparison Table */}
      {selectedResorts.length > 0 && (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          {comparisonLoading ? (
            <LoadingSpinner message="Loading comparison..." />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Metric
                    </th>
                    {comparisonData?.map((resort) => (
                      <th
                        key={resort.id}
                        className="text-center px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        {resort.name}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {/* Quality Score */}
                  <tr>
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">
                      Quality Score
                    </td>
                    {comparisonData?.map((resort) => (
                      <td key={resort.id} className="px-6 py-4 text-center">
                        <span
                          className={`text-2xl font-bold ${getQualityColorClass(resort.latest_conditions?.snow_quality_score)}`}
                        >
                          {resort.latest_conditions?.snow_quality_score != null
                            ? Math.round(resort.latest_conditions.snow_quality_score)
                            : '--'}
                        </span>
                        <div className="text-xs text-gray-500 mt-1">
                          {getQualityLabel(resort.latest_conditions?.snow_quality_score)}
                        </div>
                      </td>
                    ))}
                  </tr>

                  {/* 24h Snowfall */}
                  <tr className="bg-gray-50">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">
                      24h Snowfall
                    </td>
                    {comparisonData?.map((resort) => (
                      <td
                        key={resort.id}
                        className="px-6 py-4 text-center text-lg font-semibold"
                      >
                        {resort.latest_conditions?.new_snow_24h_in != null
                          ? `${formatNumber(resort.latest_conditions.new_snow_24h_in)}"`
                          : '--'}
                      </td>
                    ))}
                  </tr>

                  {/* Base Depth */}
                  <tr>
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">
                      Base Depth
                    </td>
                    {comparisonData?.map((resort) => (
                      <td
                        key={resort.id}
                        className="px-6 py-4 text-center text-lg font-semibold"
                      >
                        {resort.latest_conditions?.base_depth_in != null
                          ? `${formatNumber(resort.latest_conditions.base_depth_in)}"`
                          : '--'}
                      </td>
                    ))}
                  </tr>

                  {/* Temperature */}
                  <tr className="bg-gray-50">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">
                      Temperature
                    </td>
                    {comparisonData?.map((resort) => (
                      <td
                        key={resort.id}
                        className="px-6 py-4 text-center text-lg font-semibold"
                      >
                        {formatTemperature(resort.latest_conditions?.temperature_f)}
                      </td>
                    ))}
                  </tr>

                  {/* Lifts Open */}
                  <tr>
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">
                      Lifts Open
                    </td>
                    {comparisonData?.map((resort) => (
                      <td
                        key={resort.id}
                        className="px-6 py-4 text-center text-lg font-semibold"
                      >
                        {resort.latest_conditions?.lifts_open != null &&
                        resort.latest_conditions?.lifts_total != null
                          ? `${resort.latest_conditions.lifts_open}/${resort.latest_conditions.lifts_total}`
                          : '--'}
                      </td>
                    ))}
                  </tr>
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {selectedResorts.length === 0 && (
        <div className="text-center text-gray-500 py-12 bg-white rounded-lg shadow-md">
          Select resorts above to compare their conditions
        </div>
      )}
    </div>
  );
}
