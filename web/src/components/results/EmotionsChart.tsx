import React, { useMemo } from 'react';
import { PlotlySafe as Plot } from '@/components/charts/PlotlySafe';
import { defaultLayoutConfig, plotConfig } from './chartConfig';

import type { AnalysisResults } from '@/utils/api';

interface EmotionsChartProps {
  rows: AnalysisResults['rows'];
}

export const EmotionsChart: React.FC<EmotionsChartProps> = ({ rows }) => {
  const chartData = useMemo(() => {
    if (!rows || rows.length === 0) return { data: [], layout: defaultLayoutConfig };

    // Aggregate emotions from all rows
    const emotionTotals: Record<string, number> = {};
    rows.forEach(row => {
      if (row.emotions) {
        Object.entries(row.emotions).forEach(([emotion, value]) => {
          emotionTotals[emotion] = (emotionTotals[emotion] || 0) + value;
        });
      }
    });

    // Calculate averages
    const emotionAverages = Object.entries(emotionTotals).map(([emotion, total]) => [
      emotion,
      total / rows.length
    ] as [string, number]);

    const sortedEmotions = emotionAverages
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
  }, [rows]);

  return (
    <Plot
      data={chartData.data}
      layout={chartData.layout}
      config={plotConfig}
      className="w-full"
      chartName="Emotions Analysis"
    />
  );
};