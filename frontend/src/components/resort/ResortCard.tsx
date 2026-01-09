/**
 * ResortCard Component
 *
 * Displays a ski resort card with current conditions overview.
 * Links to the resort detail page.
 */

import { Link } from 'react-router-dom';
import { FiMapPin, FiTrendingUp, FiThermometer, FiWind } from 'react-icons/fi';
import type { ResortWithConditions } from '../../services/types';
import {
  formatNumber,
  formatTemperature,
  getQualityLabel,
  getQualityColorClass,
  formatRelativeTime,
} from '../../utils/formatting';

interface ResortCardProps {
  resort: ResortWithConditions;
}

export default function ResortCard({ resort }: ResortCardProps) {
  const conditions = resort.latest_condition;

  // Calculate lift percentage for progress bar
  const liftPercentage =
    conditions?.lifts_open && conditions?.lifts_total
      ? (conditions.lifts_open / conditions.lifts_total) * 100
      : 0;

  return (
    <Link
      to={`/resort/${resort.slug}`}
      className="block bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 overflow-hidden"
    >
      {/* Header with quality score badge */}
      <div className="relative p-6 pb-4">
        {/* Quality Score Badge */}
        {conditions?.snow_quality_score != null && (
          <div className="absolute top-4 right-4">
            <div
              className={`flex flex-col items-center justify-center w-16 h-16 rounded-full bg-gray-50 border-2 ${
                conditions.snow_quality_score >= 80
                  ? 'border-green-500'
                  : conditions.snow_quality_score >= 60
                    ? 'border-blue-500'
                    : conditions.snow_quality_score >= 40
                      ? 'border-yellow-500'
                      : 'border-red-500'
              }`}
            >
              <span
                className={`text-xl font-bold ${getQualityColorClass(conditions.snow_quality_score)}`}
              >
                {Math.round(conditions.snow_quality_score)}
              </span>
              <span className="text-[10px] text-gray-500 uppercase tracking-wide">
                {getQualityLabel(conditions.snow_quality_score)}
              </span>
            </div>
          </div>
        )}

        {/* Resort Name & Location */}
        <div className="pr-20">
          <h3 className="text-xl font-bold text-gray-900 truncate">
            {resort.name}
          </h3>
          <div className="flex items-center text-sm text-gray-600 mt-1">
            <FiMapPin className="mr-1 flex-shrink-0" size={14} />
            <span className="truncate">
              {[resort.state, resort.region].filter(Boolean).join(', ') ||
                'Location unknown'}
            </span>
          </div>
        </div>

        {/* Last Updated */}
        {conditions?.time && (
          <div className="text-xs text-gray-400 mt-2">
            Updated {formatRelativeTime(conditions.time)}
          </div>
        )}
      </div>

      {/* Conditions Grid */}
      {conditions ? (
        <div className="px-6 pb-4">
          <div className="grid grid-cols-3 gap-4">
            {/* 24h Snow */}
            <div className="text-center">
              <div className="text-sm text-gray-500 mb-1">24h Snow</div>
              <div className="text-lg font-semibold text-gray-900">
                {conditions.new_snow_24h_in != null
                  ? `${formatNumber(conditions.new_snow_24h_in)}"`
                  : '--'}
              </div>
              {conditions.new_snow_24h_in != null &&
                conditions.new_snow_24h_in >= 6 && (
                  <div className="text-xs text-green-600 font-medium mt-0.5">
                    Powder!
                  </div>
                )}
            </div>

            {/* Base Depth */}
            <div className="text-center">
              <div className="text-sm text-gray-500 mb-1">Base Depth</div>
              <div className="text-lg font-semibold text-gray-900">
                {conditions.base_depth_in != null
                  ? `${formatNumber(conditions.base_depth_in)}"`
                  : '--'}
              </div>
            </div>

            {/* Temperature */}
            <div className="text-center">
              <div className="text-sm text-gray-500 mb-1 flex items-center justify-center">
                <FiThermometer size={12} className="mr-1" />
                Temp
              </div>
              <div className="text-lg font-semibold text-gray-900">
                {formatTemperature(conditions.temperature_f)}
              </div>
            </div>
          </div>

          {/* Wind Info */}
          {conditions.wind_speed_mph != null && (
            <div className="flex items-center justify-center text-sm text-gray-600 mt-3">
              <FiWind size={14} className="mr-1" />
              <span>Wind: {Math.round(conditions.wind_speed_mph)} mph</span>
            </div>
          )}
        </div>
      ) : (
        <div className="px-6 pb-4">
          <div className="text-center text-gray-500 py-4">
            No recent data available
          </div>
        </div>
      )}

      {/* Lift Status Bar */}
      {conditions?.lifts_open != null && conditions?.lifts_total != null && (
        <div className="px-6 pb-4">
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600">Lifts Open</span>
            <span className="font-medium text-gray-900">
              {conditions.lifts_open} / {conditions.lifts_total}
            </span>
          </div>
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-500 rounded-full transition-all duration-300"
              style={{ width: `${liftPercentage}%` }}
            />
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="px-6 py-3 bg-gray-50 border-t border-gray-100">
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-600">
            {resort.summit_elevation_ft && (
              <span>Summit: {resort.summit_elevation_ft.toLocaleString()} ft</span>
            )}
          </div>
          <div className="flex items-center text-sm text-blue-600 font-medium">
            View Details
            <FiTrendingUp className="ml-1" size={14} />
          </div>
        </div>
      </div>
    </Link>
  );
}
