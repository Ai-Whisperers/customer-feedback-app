import React, { useMemo } from 'react';
import type { AnalysisResults } from '@/utils/api';

interface PainPointsChartProps {
  rows: AnalysisResults['rows'];
}

export const PainPointsChart: React.FC<PainPointsChartProps> = ({ rows }) => {
  const painPointsData = useMemo(() => {
    const painPointMap = new Map<string, number>();

    (rows || []).forEach(row => {
      row.pain_points.forEach(point => {
        const count = painPointMap.get(point) || 0;
        painPointMap.set(point, count + 1);
      });
    });

    return Array.from(painPointMap.entries())
      .map(([point, count]) => ({ point, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);
  }, [rows]);

  const maxCount = Math.max(...painPointsData.map(d => d.count), 1);

  return (
    <div className="bg-white rounded-lg p-6 shadow-sm">
      <h3 className="text-lg font-semibold mb-4">Principales Puntos de Dolor</h3>

      {painPointsData.length === 0 ? (
        <p className="text-gray-500 text-center py-8">
          No se encontraron puntos de dolor en los comentarios
        </p>
      ) : (
        <div className="space-y-3">
          {painPointsData.map(({ point, count }, index) => (
            <div key={point} className="flex items-center">
              <div className="w-6 text-xs font-bold text-gray-500">
                {index + 1}
              </div>
              <div className="flex-1 mx-3">
                <div className="mb-1 text-sm font-medium text-gray-700">
                  {point}
                </div>
                <div className="bg-gray-200 rounded-full h-4 relative">
                  <div
                    className="bg-purple-500 h-4 rounded-full flex items-center justify-end px-2"
                    style={{ width: `${(count / maxCount) * 100}%` }}
                  >
                    {count > 1 && (
                      <span className="text-white text-xs font-medium">
                        {count}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};