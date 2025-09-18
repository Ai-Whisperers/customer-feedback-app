/**
 * Lazy loading wrapper for react-plotly.js
 * Reduces initial bundle size by loading Plotly on demand
 */

import React, { lazy, Suspense } from 'react';
import type { PlotParams } from 'react-plotly.js';

// Lazy load the Plot component
const Plot = lazy(() => import('react-plotly.js'));

// Loading component while Plot is being loaded
const PlotLoader = () => (
  <div className="flex items-center justify-center p-8">
    <div className="text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
      <p className="text-sm text-gray-600">Cargando gráfico...</p>
    </div>
  </div>
);

// Wrapper component with loading state
export const LazyPlot: React.FC<PlotParams> = (props) => {
  return (
    <Suspense fallback={<PlotLoader />}>
      <Plot {...props} />
    </Suspense>
  );
};

export default LazyPlot;