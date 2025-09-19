import React from 'react';
import { EmotionsChart } from './EmotionsChart';
import { NPSChart } from './NPSChart';
import { ChurnRiskChart } from './ChurnRiskChart';
import { PainPointsChart } from './PainPointsChart';
import { SampleCommentsTable } from './SampleCommentsTable';
import { StatCard } from './StatCard';
import type { AnalysisResults } from '@/utils/api';

interface ResultsChartsProps {
  results: AnalysisResults;
}

export const ResultsCharts: React.FC<ResultsChartsProps> = ({ results }) => {
  // Calculate key metrics
  const rows = results.rows || [];
  const totalComments = rows.length;
  const avgChurnRisk = totalComments > 0 ? rows.reduce((sum, r) => sum + r.churn_risk, 0) / totalComments : 0;
  const promoters = rows.filter(r => r.nps_category === 'promoter').length;
  const detractors = rows.filter(r => r.nps_category === 'detractor').length;
  const npsScore = totalComments > 0 ? ((promoters - detractors) / totalComments) * 100 : 0;

  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          label="Total Comentarios"
          value={totalComments.toString()}
          icon="📊"
          color="blue"
        />
        <StatCard
          label="NPS Score"
          value={npsScore.toFixed(0)}
          icon="⭐"
          color={npsScore > 0 ? 'green' : 'red'}
        />
        <StatCard
          label="Riesgo Promedio"
          value={`${(avgChurnRisk * 100).toFixed(1)}%`}
          icon="⚠️"
          color={avgChurnRisk < 0.4 ? 'green' : avgChurnRisk < 0.6 ? 'yellow' : 'red'}
        />
        <StatCard
          label="Tiempo Procesamiento"
          value={`${results.metadata.processing_time_seconds.toFixed(1)}s`}
          icon="⏱️"
          color="blue"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <EmotionsChart rows={rows} />
        <NPSChart rows={rows} />
        <ChurnRiskChart rows={rows} />
        <PainPointsChart rows={rows} />
      </div>

      {/* Sample Comments */}
      <SampleCommentsTable rows={rows} />
    </div>
  );
};