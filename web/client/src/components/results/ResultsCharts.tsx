import React, { useMemo } from 'react';
import Plot from 'react-plotly.js';
import { GlassCard } from '../../components/ui';

interface AnalysisResults {
  task_id: string;
  summary: {
    n: number;
    nps: {
      promoters: number;
      passives: number;
      detractors: number;
      score: number;
    };
    churn_risk_avg: number;
  };
  emotions: Record<string, number>;
  pain_points: Array<{ key: string; freq: number }>;
  rows: Array<{
    i: number;
    text: string;
    emotions: Record<string, number>;
    nps: number;
    churn: number;
    tags: string[];
  }>;
}

interface ResultsChartsProps {
  results: AnalysisResults;
}

export const ResultsCharts: React.FC<ResultsChartsProps> = ({ results }) => {
  const layoutConfig = {
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: {
      family: 'system-ui, -apple-system, sans-serif',
      color: '#4b5563',
    },
    margin: { t: 40, b: 40, l: 40, r: 40 },
    showlegend: true,
    hovermode: 'closest' as const,
  };

  const emotionsChart = useMemo(() => {
    const sortedEmotions = Object.entries(results.emotions)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 10);

    return {
      data: [
        {
          x: sortedEmotions.map(([emotion]) => emotion),
          y: sortedEmotions.map(([, value]) => value),
          type: 'bar' as const,
          marker: {
            color: 'rgba(59, 130, 246, 0.8)',
            line: {
              color: 'rgba(59, 130, 246, 1)',
              width: 1,
            },
          },
          text: sortedEmotions.map(([, value]) => `${(value * 100).toFixed(1)}%`),
          textposition: 'outside' as const,
          hovertemplate: '%{x}<br>Probabilidad: %{y:.2%}<extra></extra>',
        },
      ],
      layout: {
        ...layoutConfig,
        title: {
          text: 'Top 10 Emociones Detectadas',
          font: { size: 18 },
        },
        xaxis: {
          title: { text: 'Emociones' },
          gridcolor: 'rgba(229, 231, 235, 0.3)',
        },
        yaxis: {
          title: { text: 'Probabilidad' },
          gridcolor: 'rgba(229, 231, 235, 0.3)',
          tickformat: '.0%',
        },
      },
    };
  }, [results.emotions]);

  const npsChart = useMemo(() => {
    const { promoters, passives, detractors } = results.summary.nps;
    // const total = promoters + passives + detractors; // Total not used in visualization

    return {
      data: [
        {
          values: [promoters, passives, detractors],
          labels: ['Promotores', 'Pasivos', 'Detractores'],
          type: 'pie' as const,
          marker: {
            colors: ['#10b981', '#f59e0b', '#ef4444'],
            line: {
              color: '#ffffff',
              width: 2,
            },
          },
          texttemplate: '%{label}<br>%{value} (%{percent})',
          textposition: 'outside' as const,
          hovertemplate: '%{label}<br>Cantidad: %{value}<br>Porcentaje: %{percent}<extra></extra>',
        },
      ],
      layout: {
        ...layoutConfig,
        title: {
          text: `Distribución NPS (Score: ${results.summary.nps.score})`,
          font: { size: 18 },
        },
      },
    };
  }, [results.summary.nps]);

  const painPointsChart = useMemo(() => {
    const topPainPoints = results.pain_points.slice(0, 10);

    return {
      data: [
        {
          y: topPainPoints.map(pp => pp.key).reverse(),
          x: topPainPoints.map(pp => pp.freq).reverse(),
          type: 'bar' as const,
          orientation: 'h' as const,
          marker: {
            color: 'rgba(239, 68, 68, 0.8)',
            line: {
              color: 'rgba(239, 68, 68, 1)',
              width: 1,
            },
          },
          text: topPainPoints.map(pp => pp.freq.toString()).reverse(),
          textposition: 'outside' as const,
          hovertemplate: '%{y}<br>Frecuencia: %{x}<extra></extra>',
        },
      ],
      layout: {
        ...layoutConfig,
        title: {
          text: 'Top 10 Puntos de Dolor',
          font: { size: 18 },
        },
        xaxis: {
          title: { text: 'Frecuencia' },
          gridcolor: 'rgba(229, 231, 235, 0.3)',
        },
        yaxis: {
          title: { text: '' },
          gridcolor: 'rgba(229, 231, 235, 0.3)',
        },
      },
    };
  }, [results.pain_points]);

  const churnRiskChart = useMemo(() => {
    const riskRanges = {
      'Bajo (0-0.3)': 0,
      'Medio (0.3-0.6)': 0,
      'Alto (0.6-0.8)': 0,
      'Crítico (0.8-1.0)': 0,
    };

    results.rows.forEach(row => {
      if (row.churn <= 0.3) riskRanges['Bajo (0-0.3)']++;
      else if (row.churn <= 0.6) riskRanges['Medio (0.3-0.6)']++;
      else if (row.churn <= 0.8) riskRanges['Alto (0.6-0.8)']++;
      else riskRanges['Crítico (0.8-1.0)']++;
    });

    return {
      data: [
        {
          x: Object.keys(riskRanges),
          y: Object.values(riskRanges),
          type: 'bar' as const,
          marker: {
            color: ['#10b981', '#f59e0b', '#f97316', '#ef4444'],
            line: {
              color: 'rgba(0,0,0,0.2)',
              width: 1,
            },
          },
          text: Object.values(riskRanges).map(v => v.toString()),
          textposition: 'outside' as const,
          hovertemplate: '%{x}<br>Cantidad: %{y}<extra></extra>',
        },
      ],
      layout: {
        ...layoutConfig,
        title: {
          text: `Distribución de Riesgo de Abandono (Promedio: ${(
            results.summary.churn_risk_avg * 100
          ).toFixed(1)}%)`,
          font: { size: 18 },
        },
        xaxis: {
          title: { text: 'Nivel de Riesgo' },
          gridcolor: 'rgba(229, 231, 235, 0.3)',
        },
        yaxis: {
          title: { text: 'Cantidad de Clientes' },
          gridcolor: 'rgba(229, 231, 235, 0.3)',
        },
      },
    };
  }, [results.rows, results.summary.churn_risk_avg]);

  return (
    <div className="space-y-6">
      <GlassCard variant="gradient">
        <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100 mb-6">
          Resultados del Análisis
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard
            label="Total Comentarios"
            value={results.summary.n.toString()}
            icon="📊"
          />
          <StatCard
            label="NPS Score"
            value={results.summary.nps.score.toString()}
            icon="⭐"
            color="blue"
          />
          <StatCard
            label="Riesgo Abandono Promedio"
            value={`${(results.summary.churn_risk_avg * 100).toFixed(1)}%`}
            icon="⚠️"
            color="yellow"
          />
          <StatCard
            label="Puntos de Dolor"
            value={results.pain_points.length.toString()}
            icon="🎯"
            color="red"
          />
        </div>
      </GlassCard>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <GlassCard>
          <Plot
            data={emotionsChart.data}
            layout={emotionsChart.layout}
            config={{ responsive: true, displayModeBar: false }}
            className="w-full"
          />
        </GlassCard>

        <GlassCard>
          <Plot
            data={npsChart.data}
            layout={npsChart.layout}
            config={{ responsive: true, displayModeBar: false }}
            className="w-full"
          />
        </GlassCard>

        <GlassCard>
          <Plot
            data={painPointsChart.data}
            layout={painPointsChart.layout}
            config={{ responsive: true, displayModeBar: false }}
            className="w-full"
          />
        </GlassCard>

        <GlassCard>
          <Plot
            data={churnRiskChart.data}
            layout={churnRiskChart.layout}
            config={{ responsive: true, displayModeBar: false }}
            className="w-full"
          />
        </GlassCard>
      </div>

      <GlassCard>
        <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">
          Muestra de Comentarios Analizados
        </h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50/50 dark:bg-gray-800/50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  #
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Comentario
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  NPS
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Riesgo
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Etiquetas
                </th>
              </tr>
            </thead>
            <tbody className="bg-white/50 dark:bg-gray-900/50 divide-y divide-gray-200 dark:divide-gray-700">
              {results.rows.slice(0, 5).map((row) => (
                <tr key={row.i}>
                  <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                    {row.i + 1}
                  </td>
                  <td className="px-4 py-4 text-sm text-gray-900 dark:text-gray-100">
                    <p className="truncate max-w-xs">{row.text}</p>
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                    {row.nps}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm">
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        row.churn < 0.3
                          ? 'bg-green-100 text-green-800'
                          : row.churn < 0.6
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {(row.churn * 100).toFixed(0)}%
                    </span>
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                    <div className="flex flex-wrap gap-1">
                      {row.tags.slice(0, 2).map((tag, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </GlassCard>
    </div>
  );
};

interface StatCardProps {
  label: string;
  value: string;
  icon: string;
  color?: 'blue' | 'green' | 'yellow' | 'red';
}

const StatCard: React.FC<StatCardProps> = ({ label, value, icon, color = 'green' }) => {
  const colorClasses = {
    blue: 'bg-blue-50 dark:bg-blue-900/20',
    green: 'bg-green-50 dark:bg-green-900/20',
    yellow: 'bg-yellow-50 dark:bg-yellow-900/20',
    red: 'bg-red-50 dark:bg-red-900/20',
  };

  return (
    <div className={`p-4 rounded-lg ${colorClasses[color]} backdrop-blur-sm`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-2xl">{icon}</span>
      </div>
      <p className="text-2xl font-bold text-gray-800 dark:text-gray-100">{value}</p>
      <p className="text-sm text-gray-600 dark:text-gray-400">{label}</p>
    </div>
  );
};