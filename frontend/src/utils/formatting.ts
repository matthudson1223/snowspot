/**
 * Formatting utilities for displaying data
 */

/**
 * Format a number with optional decimal places
 */
export const formatNumber = (
  value: number | null | undefined,
  decimals: number = 1
): string => {
  if (value === null || value === undefined) {
    return '--';
  }
  return value.toFixed(decimals);
};

/**
 * Format temperature with degree symbol
 */
export const formatTemperature = (temp: number | null | undefined): string => {
  if (temp === null || temp === undefined) {
    return '--';
  }
  return `${Math.round(temp)}°F`;
};

/**
 * Format snow depth in inches
 */
export const formatSnowDepth = (inches: number | null | undefined): string => {
  if (inches === null || inches === undefined) {
    return '--';
  }
  return `${formatNumber(inches)}"`;
};

/**
 * Format wind speed in mph
 */
export const formatWindSpeed = (mph: number | null | undefined): string => {
  if (mph === null || mph === undefined) {
    return '--';
  }
  return `${Math.round(mph)} mph`;
};

/**
 * Format lift status (open/total)
 */
export const formatLiftStatus = (
  open: number | null | undefined,
  total: number | null | undefined
): string => {
  if (open === null || open === undefined || total === null || total === undefined) {
    return '--';
  }
  return `${open} / ${total}`;
};

/**
 * Format a ratio as a percentage
 */
export const formatPercentage = (
  value: number | null | undefined,
  decimals: number = 0
): string => {
  if (value === null || value === undefined) {
    return '--';
  }
  return `${value.toFixed(decimals)}%`;
};

/**
 * Format a date/time string relative to now
 */
export const formatRelativeTime = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffMins < 1) {
    return 'Just now';
  } else if (diffMins < 60) {
    return `${diffMins}m ago`;
  } else if (diffHours < 24) {
    return `${diffHours}h ago`;
  } else if (diffDays < 7) {
    return `${diffDays}d ago`;
  } else {
    return date.toLocaleDateString();
  }
};

/**
 * Format elevation in feet
 */
export const formatElevation = (feet: number | null | undefined): string => {
  if (feet === null || feet === undefined) {
    return '--';
  }
  return `${feet.toLocaleString()} ft`;
};

/**
 * Get quality score label
 */
export const getQualityLabel = (score: number | null | undefined): string => {
  if (score === null || score === undefined) {
    return 'Unknown';
  }
  if (score >= 90) return 'Epic';
  if (score >= 80) return 'Excellent';
  if (score >= 70) return 'Great';
  if (score >= 60) return 'Good';
  if (score >= 50) return 'Decent';
  if (score >= 40) return 'Fair';
  return 'Poor';
};

/**
 * Get quality score color class
 */
export const getQualityColorClass = (score: number | null | undefined): string => {
  if (score === null || score === undefined) {
    return 'text-gray-500';
  }
  if (score >= 80) return 'text-green-600';
  if (score >= 60) return 'text-blue-600';
  if (score >= 40) return 'text-yellow-600';
  return 'text-red-600';
};
