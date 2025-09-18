import React, { lazy, Suspense } from 'react';
import { GlassCard } from '../../components/ui';
import { SampleCommentsTable } from './SampleCommentsTable';
import { StatCard } from './StatCard';
import type { AnalysisResults } from '@/utils/api';

// Dynamic imports for chart components to isolate Plotly loading
const EmotionsChart = lazy(() =>
  import('./EmotionsChart').then(module => ({
    default: module.EmotionsChart
  }))
);

const NPSChart = lazy(() =>
  import('./NPSChart').then(module => ({
    default: module.NPSChart
  }))
);

const PainPointsChart = lazy(() =>
  import('./PainPointsChart').then(module => ({
    default: module.PainPointsChart
  }))
);

const ChurnRiskChart = lazy(() =>
  import('./ChurnRiskChart').then(module => ({
    default: module.ChurnRiskChart
  }))
);

// Chart loading skeleton
const ChartSkeleton = ({ height = '400px' }: { height?: string }) => (
  <div className="animate-pulse" style={{ minHeight: height }}>
    <div className="flex items-center justify-center h-full">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mb-4"></div>
        <p className="text-gray-500 dark:text-gray-400">Loading chart...</p>
      </div>
    </div>
  </div>
);

interface ResultsChartsProps {
  results: AnalysisResults;
}

export const ResultsCharts: React.FC<ResultsChartsProps> = ({ results }) => {

  return (
    <div className="space-y-6">
      <GlassCard variant="gradient">
        <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100 mb-6">
          Resultados del Análisis
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard
            label="Total Comentarios"
            value={results.metadata.total_comments.toString()}
            icon="Chart"
          />
          <StatCard
            label="NPS Score"
            value={results.summary.nps.score.toString()}
            icon="Star"
            color="blue"
          />
          <StatCard
            label="Riesgo Abandono Promedio"
            value={`${(results.summary.churn_risk.average * 100).toFixed(1)}%`}
            icon="Warning"
            color="yellow"
          />
          <StatCard
            label="Puntos de Dolor"
            value={results.summary.pain_points.length.toString()}
            icon="Target"
            color="red"
          />
        </div>
      </GlassCard>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {results.rows && results.rows.length > 0 && (
          <GlassCard>
            <Suspense fallback={<ChartSkeleton />}>
              <EmotionsChart rows={results.rows} />
            </Suspense>
          </GlassCard>
        )}

        <GlassCard>
          <Suspense fallback={<ChartSkeleton />}>
            <NPSChart nps={results.summary.nps} />
          </Suspense>
        </GlassCard>

        <GlassCard>
          <Suspense fallback={<ChartSkeleton />}>
            <PainPointsChart painPoints={results.summary.pain_points} />
          </Suspense>
        </GlassCard>

        {results.rows && (
          <GlassCard>
            <Suspense fallback={<ChartSkeleton />}>
              <ChurnRiskChart rows={results.rows} averageRisk={results.summary.churn_risk.average} />
            </Suspense>
          </GlassCard>
        )}
      </div>

      {results.rows && results.rows.length > 0 && (
        <GlassCard>
          <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">
            Muestra de Comentarios Analizados
          </h3>
          <SampleCommentsTable rows={results.rows} limit={5} />
        </GlassCard>
      )}
    </div>
  );
};