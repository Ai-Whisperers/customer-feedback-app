import React, { useMemo } from 'react';
import { PlotlySafe as Plot } from '@/components/charts/PlotlySafe';
import { defaultLayoutConfig, plotConfig } from './chartConfig';
import type { AnalysisResults } from '@/lib/api';

interface ChurnRiskChartProps {
  rows: AnalysisResults['rows'];
  averageRisk: number;
}

export const ChurnRiskChart: React.FC<ChurnRiskChartProps> = ({ rows, averageRisk }) => {
  const chartData = useMemo(() => {
    const riskRanges = {
      'Bajo (0-0.3)': 0,
      'Medio (0.3-0.6)': 0,
      'Alto (0.6-0.8)': 0,
      'Crítico (0.8-1.0)': 0,
    };

    if (!rows) return { data: [], layout: defaultLayoutConfig };

    rows.forEach(row => {
      const risk = row.churn_risk || 0;
      if (risk <= 0.3) riskRanges['Bajo (0-0.3)']++;
      else if (risk <= 0.6) riskRanges['Medio (0.3-0.6)']++;
      else if (risk <= 0.8) riskRanges['Alto (0.6-0.8)']++;
      else riskRanges['Crítico (0.8-1.0)']++;
    });

    return {
      data: [
        {
          x: Object.keys(riskRanges),
          y: Object.values(riskRanges),
          type: 'bar' as const,
          marker: {
            color: ['#10b981', '#f59e0b', '#f97316', '#ef4444'],
            line: {
              color: 'rgba(0,0,0,0.2)',
              width: 1,
            },
          },
          text: Object.values(riskRanges).map(v => v.toString()),
          textposition: 'outside' as const,
          hovertemplate: '%{x}<br>Cantidad: %{y}<extra></extra>',
        },
      ],
      layout: {
        ...defaultLayoutConfig,
        title: {
          text: `Distribución de Riesgo de Abandono (Promedio: ${(averageRisk * 100).toFixed(1)}%)`,
          font: { size: 18 },
        },
        xaxis: {
          title: { text: 'Nivel de Riesgo' },
          gridcolor: 'rgba(229, 231, 235, 0.3)',
        },
        yaxis: {
          title: { text: 'Cantidad de Clientes' },
          gridcolor: 'rgba(229, 231, 235, 0.3)',
        },
      },
    };
  }, [rows, averageRisk]);

  return (
    <Plot
      data={chartData.data}
      layout={chartData.layout}
      config={plotConfig}
      className="w-full"
      chartName="Churn Risk Distribution"
    />
  );
};