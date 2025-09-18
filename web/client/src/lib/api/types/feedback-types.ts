/**
 * Feedback Domain Types
 * Following Clean Architecture - Domain Layer
 */

export interface UploadResponse {
  task_id: string;
  message: string;
  estimated_time_seconds: number;
  file_info: {
    total_comments: number;
    preview: Array<{
      nota: number;
      comentario_final: string;
    }>;
  };
}

export interface TaskStatus {
  task_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number;
  result?: string;
  error?: string;
  current_batch?: number;
  total_batches?: number;
  items_processed?: number;
  total_items?: number;
  message?: string;
  processed_rows?: number;
  total_rows?: number;
}

export interface AnalysisResults {
  summary: {
    nps: {
      score: number;
      promoters: number;
      promoters_percentage: number;
      passives: number;
      passives_percentage: number;
      detractors: number;
      detractors_percentage: number;
    };
    churn_risk: {
      average: number;
      high_risk_count: number;
      high_risk_percentage: number;
      distribution: Record<string, number>;
    };
    pain_points: Array<{
      category: string;
      count: number;
      percentage: number;
      examples: string[];
    }>;
  };
  rows?: Array<{
    index: number;
    original_text: string;
    nota: number;
    nps_category: string;
    sentiment: string;
    language: string;
    churn_risk: number;
    pain_points: string[];
    emotions: Record<string, number>;
  }>;
  metadata: {
    total_comments: number;
    processing_time_seconds: number;
    model_used: string;
    timestamp: string;
    batches_processed: number;
  };
}