/**
 * Results visualization component
 * Displays analysis results with Plotly charts
 */

import React from 'react';
import Plot from 'react-plotly.js';
import { exportResults } from '@/lib/api';
import type { AnalysisResults } from '@/lib/api';

interface ResultsVisualizationProps {
  results: AnalysisResults;
  taskId: string;
}

export const ResultsVisualization: React.FC<ResultsVisualizationProps> = ({
  results,
  taskId,
}) => {
  const handleExport = async (format: 'csv' | 'xlsx') => {
    try {
      const blob = await exportResults(taskId, format, 'all');
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analysis_${taskId}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  const { summary, metadata } = results;

  // NPS Distribution Data
  const npsData = {
    values: [
      summary.nps.promoters,
      summary.nps.passives,
      summary.nps.detractors,
    ],
    labels: ['Promoters', 'Passives', 'Detractors'],
    marker: {
      colors: ['#10b981', '#f59e0b', '#ef4444'],
    },
  };

  // Emotions Heatmap Data
  const emotionCategories = results.rows?.length
    ? Object.keys(results.rows[0].emotions)
    : [];
  const emotionValues = results.rows?.map(row =>
    emotionCategories.map(emotion => row.emotions[emotion])
  ) || [];

  return (
    <div className="space-y-6">
      {/* Export Buttons */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex justify-between items-center">
          <h2 className="text-xl font-semibold text-gray-900">Analysis Results</h2>
          <div className="space-x-3">
            <button
              onClick={() => handleExport('csv')}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              Export CSV
            </button>
            <button
              onClick={() => handleExport('xlsx')}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700"
            >
              Export Excel
            </button>
          </div>
        </div>
      </div>

      {/* NPS Score Card */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Net Promoter Score</h3>
        <div className="flex items-center justify-between">
          <div className="text-5xl font-bold text-primary-600">
            {summary.nps.score}
          </div>
          <div className="flex-1 ml-8">
            <Plot
              data={[{
                type: 'pie',
                ...npsData,
                textinfo: 'label+percent',
                hoverinfo: 'label+value',
              }]}
              layout={{
                height: 250,
                width: 350,
                margin: { t: 0, b: 0, l: 0, r: 0 },
                showlegend: false,
              }}
              config={{ displayModeBar: false }}
            />
          </div>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Total Comments */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="text-sm font-medium text-gray-500">Total Comments</div>
          <div className="mt-2 text-3xl font-semibold text-gray-900">
            {metadata.total_comments}
          </div>
        </div>

        {/* Average Churn Risk */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="text-sm font-medium text-gray-500">Avg Churn Risk</div>
          <div className="mt-2 text-3xl font-semibold text-gray-900">
            {(summary.churn_risk.average * 100).toFixed(1)}%
          </div>
        </div>

        {/* High Risk Customers */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="text-sm font-medium text-gray-500">High Risk Customers</div>
          <div className="mt-2 text-3xl font-semibold text-red-600">
            {summary.churn_risk.high_risk_count}
          </div>
        </div>
      </div>

      {/* Pain Points */}
      {summary.pain_points.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Top Pain Points</h3>
          <Plot
            data={[{
              type: 'bar',
              x: summary.pain_points.map(p => p.category),
              y: summary.pain_points.map(p => p.count),
              marker: {
                color: '#3b82f6',
              },
            }]}
            layout={{
              height: 300,
              margin: { t: 20, b: 40, l: 40, r: 20 },
              xaxis: { title: { text: '' } },
              yaxis: { title: { text: 'Count' } },
            }}
            config={{ displayModeBar: false }}
          />
        </div>
      )}

      {/* Emotions Heatmap */}
      {emotionValues.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Emotion Analysis</h3>
          <Plot
            data={[{
              type: 'heatmap',
              z: emotionValues,
              x: emotionCategories,
              y: results.rows?.map((_, i) => `Comment ${i + 1}`),
              colorscale: 'RdBu',
              reversescale: true,
            }]}
            layout={{
              height: 400,
              margin: { t: 20, b: 40, l: 80, r: 20 },
              xaxis: { title: { text: 'Emotions' }, side: 'bottom' },
              yaxis: { title: { text: '' }, autorange: 'reversed' },
            }}
            config={{ displayModeBar: false }}
          />
        </div>
      )}

      {/* Processing Metadata */}
      <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-600">
        <div className="flex justify-between">
          <span>Processing Time: {metadata.processing_time_seconds.toFixed(2)}s</span>
          <span>Model: {metadata.model_used}</span>
          <span>Batches: {metadata.batches_processed}</span>
        </div>
      </div>
    </div>
  );
};