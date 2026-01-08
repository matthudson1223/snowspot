/**
 * Alerts Page
 *
 * Manage powder alerts and notifications.
 */

import { FiBell, FiPlus } from 'react-icons/fi';
import { usePowderAlerts } from '../hooks/useConditions';
import { LoadingSpinner, ErrorMessage } from '../components/common';
import { formatNumber, getQualityColorClass } from '../utils/formatting';

export default function AlertsPage() {
  const {
    data: powderAlerts,
    isLoading,
    error,
    refetch,
  } = usePowderAlerts(undefined, 6);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Powder Alerts</h1>
        <button className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
          <FiPlus className="mr-2" size={16} />
          Create Alert
        </button>
      </div>

      {/* Current Powder Conditions */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex items-center mb-4">
          <FiBell className="text-blue-600 mr-2" size={20} />
          <h2 className="text-lg font-semibold text-gray-900">
            Current Powder Conditions (6"+ in 24h)
          </h2>
        </div>

        {isLoading ? (
          <LoadingSpinner message="Checking powder conditions..." />
        ) : error ? (
          <ErrorMessage error={error} onRetry={() => refetch()} />
        ) : powderAlerts && powderAlerts.length > 0 ? (
          <div className="space-y-4">
            {powderAlerts.map((alert) => (
              <div
                key={alert.resort.id}
                className="flex items-center justify-between p-4 bg-blue-50 rounded-lg border border-blue-100"
              >
                <div>
                  <h3 className="font-semibold text-gray-900">
                    {alert.resort.name}
                  </h3>
                  <p className="text-sm text-gray-600">
                    {alert.resort.state}, {alert.resort.region}
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-blue-600">
                    {formatNumber(alert.new_snow_24h_in)}"
                  </div>
                  <div className="text-sm text-gray-500">24h snowfall</div>
                </div>
                <div className="text-center px-4">
                  <div
                    className={`text-xl font-bold ${getQualityColorClass(alert.snow_quality_score)}`}
                  >
                    {Math.round(alert.snow_quality_score)}
                  </div>
                  <div className="text-xs text-gray-500">Quality</div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center text-gray-500 py-8">
            No powder alerts at this time. Check back soon!
          </div>
        )}
      </div>

      {/* My Alerts */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">My Alerts</h2>
        <div className="text-center text-gray-500 py-8">
          <p>You don't have any alerts set up yet.</p>
          <p className="text-sm mt-2">
            Create an alert to get notified when powder days hit your favorite
            resorts.
          </p>
        </div>
      </div>
    </div>
  );
}
