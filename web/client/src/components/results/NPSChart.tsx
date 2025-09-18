import React, { useMemo } from 'react';
import { PlotlySafe as Plot } from '@/components/charts/PlotlySafe';
import { defaultLayoutConfig, plotConfig } from './chartConfig';
import type { AnalysisResults } from '@/lib/api';

interface NPSChartProps {
  nps: AnalysisResults['summary']['nps'];
}

export const NPSChart: React.FC<NPSChartProps> = ({ nps }) => {
  const chartData = useMemo(() => {
    const { promoters, passives, detractors, score } = nps;

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
        ...defaultLayoutConfig,
        title: {
          text: `Distribución NPS (Score: ${score})`,
          font: { size: 18 },
        },
      },
    };
  }, [nps]);

  return (
    <Plot
      data={chartData.data}
      layout={chartData.layout}
      config={plotConfig}
      className="w-full"
      chartName="NPS Distribution"
    />
  );
};