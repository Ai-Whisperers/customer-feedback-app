import React, { useMemo } from 'react';
import { LazyPlot as Plot } from '@/components/charts/LazyPlot';
import { defaultLayoutConfig, plotConfig } from './chartConfig';
import type { AnalysisResults } from './types';

interface PainPointsChartProps {
  painPoints: AnalysisResults['pain_points'];
}

export const PainPointsChart: React.FC<PainPointsChartProps> = ({ painPoints }) => {
  const chartData = useMemo(() => {
    const topPainPoints = painPoints.slice(0, 10);

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
        ...defaultLayoutConfig,
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
  }, [painPoints]);

  return (
    <Plot
      data={chartData.data}
      layout={chartData.layout}
      config={plotConfig}
      className="w-full"
    />
  );
};