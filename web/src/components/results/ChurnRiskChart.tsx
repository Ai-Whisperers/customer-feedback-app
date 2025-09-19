import React, { useMemo } from 'react';
import type { AnalysisResults } from '@/utils/api';

interface ChurnRiskChartProps {
  rows: AnalysisResults['rows'];
}

export const ChurnRiskChart: React.FC<ChurnRiskChartProps> = ({ rows }) => {
  const riskDistribution = useMemo(() => {
    const bins = {
      veryLow: 0,
      low: 0,
      medium: 0,
      high: 0,
      veryHigh: 0
    };

    (rows || []).forEach(row => {
      const risk = row.churn_risk;
      if (risk < 0.2) bins.veryLow++;
      else if (risk < 0.4) bins.low++;
      else if (risk < 0.6) bins.medium++;
      else if (risk < 0.8) bins.high++;
      else bins.veryHigh++;
    });

    const total = (rows || []).length;
    const avgRisk = total > 0 ? (rows || []).reduce((sum, r) => sum + r.churn_risk, 0) / total : 0;

    return {
      bins,
      percentages: {
        veryLow: (bins.veryLow / total) * 100,
        low: (bins.low / total) * 100,
        medium: (bins.medium / total) * 100,
        high: (bins.high / total) * 100,
        veryHigh: (bins.veryHigh / total) * 100,
      },
      avgRisk,
      total
    };
  }, [rows]);

  const riskLevels = [
    { key: 'veryLow', label: 'Muy Bajo', color: 'bg-green-600', range: '0-20%' },
    { key: 'low', label: 'Bajo', color: 'bg-green-400', range: '20-40%' },
    { key: 'medium', label: 'Medio', color: 'bg-yellow-500', range: '40-60%' },
    { key: 'high', label: 'Alto', color: 'bg-orange-500', range: '60-80%' },
    { key: 'veryHigh', label: 'Muy Alto', color: 'bg-red-600', range: '80-100%' },
  ];

  return (
    <div className="bg-white rounded-lg p-6 shadow-sm">
      <h3 className="text-lg font-semibold mb-4">Riesgo de Abandono</h3>

      <div className="mb-6 text-center">
        <div className="text-3xl font-bold text-orange-600">
          {(riskDistribution.avgRisk * 100).toFixed(1)}%
        </div>
        <div className="text-sm text-gray-600">Riesgo Promedio</div>
      </div>

      <div className="space-y-3">
        {riskLevels.map(level => (
          <div key={level.key} className="flex items-center">
            <div className="w-20 text-sm font-medium">{level.label}</div>
            <div className="flex-1 mx-3">
              <div className="bg-gray-200 rounded-full h-6 relative">
                <div
                  className={`${level.color} h-6 rounded-full flex items-center justify-end px-2`}
                  style={{
                    width: `${riskDistribution.percentages[level.key as keyof typeof riskDistribution.percentages]}%`
                  }}
                >
                  {riskDistribution.percentages[level.key as keyof typeof riskDistribution.percentages] > 5 && (
                    <span className="text-white text-xs font-medium">
                      {riskDistribution.bins[level.key as keyof typeof riskDistribution.bins]}
                    </span>
                  )}
                </div>
              </div>
            </div>
            <div className="text-xs text-gray-500 w-16 text-right">
              {level.range}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};