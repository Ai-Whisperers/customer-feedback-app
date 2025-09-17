import React, { useMemo } from 'react';
import { LazyPlot as Plot } from '@/components/charts/LazyPlot';
import { defaultLayoutConfig, plotConfig } from './chartConfig';

interface EmotionsChartProps {
  emotions: Record<string, number>;
}

export const EmotionsChart: React.FC<EmotionsChartProps> = ({ emotions }) => {
  const chartData = useMemo(() => {
    const sortedEmotions = Object.entries(emotions)
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
        ...defaultLayoutConfig,
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
  }, [emotions]);

  return (
    <Plot
      data={chartData.data}
      layout={chartData.layout}
      config={plotConfig}
      className="w-full"
    />
  );
};