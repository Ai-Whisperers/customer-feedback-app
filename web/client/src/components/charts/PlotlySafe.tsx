import React, { Component, Suspense } from 'react';
import type { ReactNode } from 'react';
import type { PlotParams } from 'react-plotly.js';

// Lazy load Plotly to isolate potential loading issues
const Plot = React.lazy(() => import('react-plotly.js'));

// Error boundary to catch and isolate chart failures
interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

class ChartErrorBoundary extends Component<
  { children: ReactNode },
  ErrorBoundaryState
> {
  constructor(props: { children: ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    console.error('[ChartErrorBoundary] Chart rendering failed:', error);
    return { hasError: true, error };
  }

  componentDidCatch(_error: Error, errorInfo: React.ErrorInfo) {
    console.error('[ChartErrorBoundary] Error details:', errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center p-8 bg-gray-50 dark:bg-gray-900 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-700">
          <svg
            className="w-16 h-16 text-gray-400 dark:text-gray-600 mb-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
            />
          </svg>
          <p className="text-gray-600 dark:text-gray-400 font-medium mb-2">
            Chart temporarily unavailable
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-500">
            The visualization could not be loaded. Data is still being processed.
          </p>
        </div>
      );
    }

    return this.props.children;
  }
}

// Loading component for chart
const ChartLoadingFallback = () => (
  <div className="flex items-center justify-center p-8">
    <div className="text-center">
      <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mb-4"></div>
      <p className="text-gray-600 dark:text-gray-400">Loading chart...</p>
    </div>
  </div>
);

// Safe Plotly wrapper component
export function PlotlySafe(props: PlotParams) {
  return (
    <ChartErrorBoundary>
      <Suspense fallback={<ChartLoadingFallback />}>
        <Plot
          {...props}
          // Ensure responsive behavior
          config={{
            responsive: true,
            displaylogo: false,
            ...props.config,
          }}
          // Default styles for consistency
          style={{
            width: '100%',
            height: '100%',
            ...props.style,
          }}
        />
      </Suspense>
    </ChartErrorBoundary>
  );
}

// Re-export for backward compatibility
export default PlotlySafe;