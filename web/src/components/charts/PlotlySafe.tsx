import React, { Component, Suspense } from 'react';
import type { ReactNode } from 'react';
import createPlotlyComponent from 'react-plotly.js/factory';
import type { PlotParams } from 'react-plotly.js';

// Declare window.Plotly for TypeScript
declare global {
  interface Window {
    Plotly?: any;
  }
}

// Cache for the Plot component
let PlotComponent: React.ComponentType<PlotParams> | null = null;

/**
 * Get or create the Plotly component using the global Plotly object
 * This approach uses the CDN-loaded Plotly to avoid bundling issues
 */
const getPlotlyComponent = (): React.ComponentType<PlotParams> | null => {
  if (PlotComponent) {
    return PlotComponent;
  }

  // Check if Plotly is available from CDN
  if (typeof window !== 'undefined' && window.Plotly) {
    console.log('[PlotlySafe] Using Plotly from CDN');
    PlotComponent = createPlotlyComponent(window.Plotly);
    return PlotComponent;
  }

  // Plotly not yet loaded from CDN
  console.warn('[PlotlySafe] Plotly not yet available from CDN');
  return null;
};

/**
 * Wait for Plotly to load from CDN
 */
const waitForPlotly = (): Promise<React.ComponentType<PlotParams>> => {
  return new Promise((resolve, reject) => {
    let attempts = 0;
    const maxAttempts = 50; // 5 seconds max wait

    const checkPlotly = () => {
      attempts++;

      const component = getPlotlyComponent();
      if (component) {
        resolve(component);
        return;
      }

      if (attempts >= maxAttempts) {
        reject(new Error('Plotly failed to load from CDN'));
        return;
      }

      // Check again in 100ms
      setTimeout(checkPlotly, 100);
    };

    checkPlotly();
  });
};

// Lazy component that waits for CDN Plotly
const LazyPlotlyChart = React.lazy(() =>
  waitForPlotly().then(Plot => ({
    default: (props: PlotParams) => (
      <Plot
        {...props}
        config={{
          responsive: true,
          displaylogo: false,
          ...props.config,
        }}
        style={{
          width: '100%',
          height: '100%',
          ...props.style,
        }}
      />
    ),
  }))
);

// Error boundary to catch and isolate chart failures
interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorCount: number;
}

class ChartErrorBoundary extends Component<
  { children: ReactNode; chartName?: string },
  ErrorBoundaryState
> {
  constructor(props: { children: ReactNode; chartName?: string }) {
    super(props);
    this.state = { hasError: false, error: null, errorCount: 0 };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    console.error('[ChartErrorBoundary] Chart rendering failed:', error);
    return { hasError: true, error };
  }

  componentDidCatch(_error: Error, errorInfo: React.ErrorInfo) {
    console.error('[ChartErrorBoundary] Error details:', errorInfo);

    // Track error count for potential retry logic
    this.setState(prevState => ({
      errorCount: prevState.errorCount + 1
    }));
  }

  handleRetry = () => {
    // Clear the cached component to force reload
    PlotComponent = null;
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      const chartName = this.props.chartName || 'Chart';

      return (
        <div className="flex flex-col items-center justify-center p-8 bg-gray-50 dark:bg-gray-900 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-700">
          <svg
            className="w-16 h-16 text-gray-400 dark:text-gray-600 mb-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
            />
          </svg>

          <p className="text-gray-600 dark:text-gray-400 font-medium mb-2">
            {chartName} temporarily unavailable
          </p>

          <p className="text-sm text-gray-500 dark:text-gray-500 mb-4 text-center max-w-md">
            The visualization could not be loaded. The data is still being processed.
          </p>

          {this.state.errorCount < 3 && (
            <button
              onClick={this.handleRetry}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Retry Loading
            </button>
          )}

          {/* Debug info in development */}
          {process.env.NODE_ENV === 'development' && this.state.error && (
            <details className="mt-4 text-xs text-gray-500">
              <summary className="cursor-pointer">Error Details</summary>
              <pre className="mt-2 p-2 bg-gray-100 rounded overflow-auto max-w-full">
                {this.state.error.toString()}
              </pre>
            </details>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}

// Loading component for chart
const ChartLoadingFallback = ({ name = 'chart' }: { name?: string }) => (
  <div className="flex items-center justify-center p-8">
    <div className="text-center">
      <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mb-4"></div>
      <p className="text-gray-600 dark:text-gray-400">Loading {name}...</p>
    </div>
  </div>
);

// Main export: Safe Plotly wrapper component
interface PlotlySafeProps extends PlotParams {
  chartName?: string;
}

export function PlotlySafe({ chartName, ...plotProps }: PlotlySafeProps) {
  return (
    <ChartErrorBoundary chartName={chartName}>
      <Suspense fallback={<ChartLoadingFallback name={chartName} />}>
        <LazyPlotlyChart {...plotProps} />
      </Suspense>
    </ChartErrorBoundary>
  );
}

// Export error boundary for external use if needed
export { ChartErrorBoundary };

// Default export for compatibility
export default PlotlySafe;