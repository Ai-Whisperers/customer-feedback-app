/**
 * Feedback Domain Types
 * Following Clean Architecture - Domain Layer
 * Aligned with backend schemas
 */

// Upload types matching backend schemas
export interface FileInfo {
  name: string;
  rows: number;
  size_mb: number;
  columns_found: string[];
  has_nps_column: boolean;
}

export interface UploadResponse {
  success: boolean;
  message?: string;
  task_id: string;
  estimated_time_seconds: number;
  file_info: FileInfo;
}

// Status types matching backend schemas
export type BackendTaskStatus = 'queued' | 'processing' | 'completed' | 'failed' | 'expired';
export type FrontendTaskStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface StatusResponse {
  task_id: string;
  status: BackendTaskStatus;
  progress: number;
  current_step?: string;
  estimated_remaining_seconds?: number;
  started_at?: string;
  completed_at?: string;
  duration_seconds?: number;
  messages: string[];
  results_available: boolean;
  error?: string;
  details?: string;
  failed_at?: string;
  retry_available: boolean;
}

// Simplified interface for backward compatibility
export interface TaskStatus {
  task_id: string;
  status: FrontendTaskStatus;
  progress?: number;
  message?: string;
  processed_rows?: number;
  total_rows?: number;
  error?: string;
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