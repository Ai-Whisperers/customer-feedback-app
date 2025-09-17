export interface AnalysisResults {
  task_id: string;
  summary: {
    n: number;
    nps: {
      promoters: number;
      passives: number;
      detractors: number;
      score: number;
    };
    churn_risk_avg: number;
  };
  emotions: Record<string, number>;
  pain_points: Array<{ key: string; freq: number }>;
  rows: Array<{
    i: number;
    text: string;
    emotions: Record<string, number>;
    nps: number;
    churn: number;
    tags: string[];
  }>;
}

export interface ChartLayoutConfig {
  paper_bgcolor: string;
  plot_bgcolor: string;
  font: {
    family: string;
    color: string;
  };
  margin: { t: number; b: number; l: number; r: number };
  showlegend: boolean;
  hovermode: 'closest';
}