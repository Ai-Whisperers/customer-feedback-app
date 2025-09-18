import React from 'react';
import { GlassCard } from '../../components/ui';
import { EmotionsChart } from './EmotionsChart';
import { NPSChart } from './NPSChart';
import { PainPointsChart } from './PainPointsChart';
import { ChurnRiskChart } from './ChurnRiskChart';
import { SampleCommentsTable } from './SampleCommentsTable';
import { StatCard } from './StatCard';
import type { AnalysisResults } from '@/lib/api';

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
            <EmotionsChart rows={results.rows} />
          </GlassCard>
        )}

        <GlassCard>
          <NPSChart nps={results.summary.nps} />
        </GlassCard>

        <GlassCard>
          <PainPointsChart painPoints={results.summary.pain_points} />
        </GlassCard>

        {results.rows && (
          <GlassCard>
            <ChurnRiskChart rows={results.rows} averageRisk={results.summary.churn_risk.average} />
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