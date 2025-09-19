import React, { useMemo } from 'react';
import type { AnalysisResults } from '@/utils/api';

interface NPSChartProps {
  rows: AnalysisResults['rows'];
}

export const NPSChart: React.FC<NPSChartProps> = ({ rows }) => {
  const npsData = useMemo(() => {
    const counts = { promoters: 0, passives: 0, detractors: 0 };

    (rows || []).forEach(row => {
      if (row.nps_category === 'promoter') counts.promoters++;
      else if (row.nps_category === 'passive') counts.passives++;
      else if (row.nps_category === 'detractor') counts.detractors++;
    });

    const total = counts.promoters + counts.passives + counts.detractors;
    const npsScore = ((counts.promoters - counts.detractors) / total) * 100;

    return {
      counts,
      percentages: {
        promoters: (counts.promoters / total) * 100,
        passives: (counts.passives / total) * 100,
        detractors: (counts.detractors / total) * 100,
      },
      npsScore,
      total
    };
  }, [rows]);

  return (
    <div className="bg-white rounded-lg p-6 shadow-sm">
      <h3 className="text-lg font-semibold mb-4">Distribución NPS</h3>

      <div className="mb-6 text-center">
        <div className="text-3xl font-bold text-blue-600">
          {npsData.npsScore.toFixed(0)}
        </div>
        <div className="text-sm text-gray-600">NPS Score</div>
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
            <span className="text-sm font-medium">Promotores</span>
          </div>
          <div className="text-sm">
            <span className="font-bold">{npsData.counts.promoters}</span>
            <span className="text-gray-500 ml-1">({npsData.percentages.promoters.toFixed(1)}%)</span>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-yellow-500 rounded-full mr-2"></div>
            <span className="text-sm font-medium">Pasivos</span>
          </div>
          <div className="text-sm">
            <span className="font-bold">{npsData.counts.passives}</span>
            <span className="text-gray-500 ml-1">({npsData.percentages.passives.toFixed(1)}%)</span>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
            <span className="text-sm font-medium">Detractores</span>
          </div>
          <div className="text-sm">
            <span className="font-bold">{npsData.counts.detractors}</span>
            <span className="text-gray-500 ml-1">({npsData.percentages.detractors.toFixed(1)}%)</span>
          </div>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t">
        <div className="flex h-8 rounded-full overflow-hidden">
          <div
            className="bg-green-500"
            style={{ width: `${npsData.percentages.promoters}%` }}
          ></div>
          <div
            className="bg-yellow-500"
            style={{ width: `${npsData.percentages.passives}%` }}
          ></div>
          <div
            className="bg-red-500"
            style={{ width: `${npsData.percentages.detractors}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
};