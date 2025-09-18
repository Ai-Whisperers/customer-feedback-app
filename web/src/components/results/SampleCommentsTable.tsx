import React from 'react';
import type { AnalysisResults } from '@/utils/api';

interface SampleCommentsTableProps {
  rows: AnalysisResults['rows'];
  limit?: number;
}

export const SampleCommentsTable: React.FC<SampleCommentsTableProps> = ({ rows, limit = 5 }) => {
  if (!rows || rows.length === 0) {
    return <div className="text-center text-gray-500">No hay comentarios para mostrar</div>;
  }

  return (
    <div className="overflow-x-auto rounded-lg bg-white/5 backdrop-blur-sm border border-white/20">
      <table className="min-w-full divide-y divide-gray-200/20 dark:divide-gray-700/20">
        <thead className="bg-gradient-to-r from-blue-500/10 to-purple-600/10 backdrop-blur-sm">
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
        <tbody className="bg-white/10 dark:bg-gray-900/30 divide-y divide-gray-200/10 dark:divide-gray-700/10">
          {rows.slice(0, limit).map((row) => (
            <tr key={row.index}>
              <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                {row.index + 1}
              </td>
              <td className="px-4 py-4 text-sm text-gray-900 dark:text-gray-100">
                <p className="truncate max-w-xs">{row.original_text}</p>
              </td>
              <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                {row.nota}
              </td>
              <td className="px-4 py-4 whitespace-nowrap text-sm">
                <span
                  className={`px-2 py-1 rounded-full text-xs font-medium backdrop-blur-sm ${
                    row.churn_risk < 0.3
                      ? 'bg-green-500/20 text-green-300 border border-green-500/30'
                      : row.churn_risk < 0.6
                      ? 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30'
                      : 'bg-red-500/20 text-red-300 border border-red-500/30'
                  }`}
                >
                  {(row.churn_risk * 100).toFixed(0)}%
                </span>
              </td>
              <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                <div className="flex flex-wrap gap-1">
                  {row.pain_points && row.pain_points.slice(0, 2).map((tag, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-1 bg-blue-500/20 text-blue-300 border border-blue-500/30 rounded-md text-xs backdrop-blur-sm"
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
  );
};