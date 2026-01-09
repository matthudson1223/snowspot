/**
 * Resort Detail Page
 *
 * Shows detailed information about a specific resort.
 */

import { useParams, Link } from 'react-router-dom';
import { FiArrowLeft, FiMapPin, FiExternalLink } from 'react-icons/fi';
import { useResort, useResortHistory } from '../hooks/useResorts';
import { useForecast } from '../hooks/useForecast';
import { LoadingSpinner, ErrorMessage } from '../components/common';
import {
  formatTemperature,
  formatNumber,
  formatRelativeTime,
  getQualityLabel,
  getQualityColorClass,
} from '../utils/formatting';

export default function ResortPage() {
  const { slug } = useParams<{ slug: string }>();

  const {
    data: resort,
    isLoading: resortLoading,
    error: resortError,
    refetch,
  } = useResort(slug || '');

  // History data fetched for potential future use (e.g., charts)
  const { data: _history } = useResortHistory(slug || '', 48);
  const { data: forecasts } = useForecast(resort?.id || 0, 7);

  if (resortLoading) {
    return <LoadingSpinner size="lg" message="Loading resort details..." />;
  }

  if (resortError || !resort) {
    return <ErrorMessage error={resortError || new Error('Resort not found')} onRetry={() => refetch()} />;
  }

  const conditions = resort.latest_condition;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Back Link */}
      <Link
        to="/"
        className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-6"
      >
        <FiArrowLeft className="mr-2" size={16} />
        Back to all resorts
      </Link>

      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{resort.name}</h1>
            <div className="flex items-center text-gray-600 mt-2">
              <FiMapPin className="mr-2" size={16} />
              {[resort.state, resort.region, resort.country]
                .filter(Boolean)
                .join(', ')}
            </div>
            {resort.official_url && (
              <a
                href={resort.official_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800 mt-2"
              >
                Official Website
                <FiExternalLink className="ml-1" size={14} />
              </a>
            )}
          </div>

          {conditions?.snow_quality_score != null && (
            <div className="mt-4 md:mt-0 text-center">
              <div
                className={`text-5xl font-bold ${getQualityColorClass(conditions.snow_quality_score)}`}
              >
                {Math.round(conditions.snow_quality_score)}
              </div>
              <div className="text-sm text-gray-500">
                {getQualityLabel(conditions.snow_quality_score)} Conditions
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Current Conditions */}
      {conditions && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">
              Current Conditions
            </h2>
            <span className="text-sm text-gray-500">
              Updated {formatRelativeTime(conditions.time)}
            </span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-500 mb-1">24h Snowfall</div>
              <div className="text-2xl font-bold text-gray-900">
                {conditions.new_snow_24h_in != null
                  ? `${formatNumber(conditions.new_snow_24h_in)}"`
                  : '--'}
              </div>
            </div>

            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-500 mb-1">Base Depth</div>
              <div className="text-2xl font-bold text-gray-900">
                {conditions.base_depth_in != null
                  ? `${formatNumber(conditions.base_depth_in)}"`
                  : '--'}
              </div>
            </div>

            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-500 mb-1">Temperature</div>
              <div className="text-2xl font-bold text-gray-900">
                {formatTemperature(conditions.temperature_f)}
              </div>
            </div>

            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-500 mb-1">Wind</div>
              <div className="text-2xl font-bold text-gray-900">
                {conditions.wind_speed_mph != null
                  ? `${Math.round(conditions.wind_speed_mph)} mph`
                  : '--'}
              </div>
            </div>
          </div>

          {/* Lift Status */}
          {conditions.lifts_open != null && conditions.lifts_total != null && (
            <div className="mt-6 pt-6 border-t border-gray-200">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">
                  Lifts Open
                </span>
                <span className="text-lg font-bold text-gray-900">
                  {conditions.lifts_open} / {conditions.lifts_total}
                </span>
              </div>
              <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-blue-600 rounded-full"
                  style={{
                    width: `${(conditions.lifts_open / conditions.lifts_total) * 100}%`,
                  }}
                />
              </div>
            </div>
          )}
        </div>
      )}

      {/* Resort Stats */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Resort Info</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          {resort.summit_elevation_ft && (
            <div>
              <span className="text-gray-500">Summit:</span>{' '}
              <span className="font-medium">
                {resort.summit_elevation_ft.toLocaleString()} ft
              </span>
            </div>
          )}
          {resort.base_elevation_ft && (
            <div>
              <span className="text-gray-500">Base:</span>{' '}
              <span className="font-medium">
                {resort.base_elevation_ft.toLocaleString()} ft
              </span>
            </div>
          )}
          {resort.vertical_drop_ft && (
            <div>
              <span className="text-gray-500">Vertical:</span>{' '}
              <span className="font-medium">
                {resort.vertical_drop_ft.toLocaleString()} ft
              </span>
            </div>
          )}
          {resort.total_runs && (
            <div>
              <span className="text-gray-500">Runs:</span>{' '}
              <span className="font-medium">{resort.total_runs}</span>
            </div>
          )}
        </div>
      </div>

      {/* 7-Day Forecast */}
      {forecasts && forecasts.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            7-Day Forecast
          </h2>
          <div className="grid grid-cols-7 gap-2">
            {forecasts.slice(0, 7).map((forecast, index) => (
              <div
                key={index}
                className="text-center p-3 bg-gray-50 rounded-lg"
              >
                <div className="text-xs text-gray-500">
                  {new Date(forecast.forecast_for).toLocaleDateString('en-US', {
                    weekday: 'short',
                  })}
                </div>
                <div className="text-lg font-semibold text-gray-900 mt-1">
                  {forecast.predicted_snowfall_in != null
                    ? `${formatNumber(forecast.predicted_snowfall_in)}"`
                    : '--'}
                </div>
                <div className="text-xs text-gray-600 mt-1">
                  {forecast.temperature_high_f != null &&
                  forecast.temperature_low_f != null
                    ? `${Math.round(forecast.temperature_high_f)}° / ${Math.round(forecast.temperature_low_f)}°`
                    : '--'}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
