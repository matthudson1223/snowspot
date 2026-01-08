/**
 * ErrorMessage Component
 *
 * Displays error messages with retry functionality.
 */

import { FiAlertCircle, FiRefreshCw } from 'react-icons/fi';

interface ErrorMessageProps {
  error: Error | unknown;
  onRetry?: () => void;
}

export default function ErrorMessage({ error, onRetry }: ErrorMessageProps) {
  const errorMessage =
    error instanceof Error
      ? error.message
      : 'An unexpected error occurred. Please try again.';

  return (
    <div className="flex flex-col items-center justify-center py-12 px-4">
      <div className="flex items-center justify-center w-16 h-16 rounded-full bg-red-100 mb-4">
        <FiAlertCircle className="w-8 h-8 text-red-600" />
      </div>
      <h3 className="text-lg font-medium text-gray-900 mb-2">
        Something went wrong
      </h3>
      <p className="text-sm text-gray-600 text-center max-w-md mb-4">
        {errorMessage}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors"
        >
          <FiRefreshCw className="mr-2" size={14} />
          Try Again
        </button>
      )}
    </div>
  );
}
