import React from 'react';
import type { AnalysisResults } from './types';

interface SampleCommentsTableProps {
  rows: AnalysisResults['rows'];
  limit?: number;
}

export const SampleCommentsTable: React.FC<SampleCommentsTableProps> = ({ rows, limit = 5 }) => {
  return (
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
          {rows.slice(0, limit).map((row) => (
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
  );
};