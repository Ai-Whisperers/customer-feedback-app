import React from 'react';
import type { AnalysisResults } from '@/utils/api';

interface EmotionsChartProps {
  rows: AnalysisResults['rows'];
}

export const EmotionsChart: React.FC<EmotionsChartProps> = ({ rows }) => {
  // Calculate emotion averages
  const emotionTotals = (rows || []).reduce((acc, row) => {
    Object.entries(row.emotions).forEach(([emotion, value]) => {
      if (!acc[emotion]) acc[emotion] = { total: 0, count: 0 };
      acc[emotion].total += value;
      acc[emotion].count++;
    });
    return acc;
  }, {} as Record<string, { total: number; count: number }>);

  const emotionAverages = Object.entries(emotionTotals)
    .map(([emotion, { total, count }]) => ({
      emotion,
      average: total / count
    }))
    .sort((a, b) => b.average - a.average);

  return (
    <div className="bg-white rounded-lg p-6 shadow-sm">
      <h3 className="text-lg font-semibold mb-4">Distribución de Emociones</h3>
      <div className="space-y-3">
        {emotionAverages.slice(0, 8).map(({ emotion, average }) => (
          <div key={emotion} className="flex items-center">
            <span className="w-24 text-sm font-medium capitalize">
              {emotion.replace(/_/g, ' ')}
            </span>
            <div className="flex-1 mx-3">
              <div className="bg-gray-200 rounded-full h-6 relative">
                <div
                  className="bg-blue-500 h-6 rounded-full flex items-center justify-end px-2"
                  style={{ width: `${average * 100}%` }}
                >
                  <span className="text-white text-xs font-medium">
                    {(average * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};