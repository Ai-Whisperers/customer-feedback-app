/**
 * API client for Customer Feedback Analyzer
 * Handles all communication with the backend through the BFF proxy
 */

import axios from 'axios';

const API_BASE = '/api';

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const { detail } = error.response.data;
      const message = detail?.details || detail?.error || 'An error occurred';
      console.error('API Error:', message);
    }
    return Promise.reject(error);
  }
);

// Types
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

// API Methods
export const uploadFile = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<UploadResponse>('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const getStatus = async (taskId: string): Promise<TaskStatus> => {
  const response = await api.get<TaskStatus>(`/status/${taskId}`);
  return response.data;
};

export const getResults = async (
  taskId: string,
  format: 'json' | 'summary' = 'json',
  includeRows: boolean = true
): Promise<AnalysisResults> => {
  const response = await api.get<AnalysisResults>(`/results/${taskId}`, {
    params: {
      format,
      include_rows: includeRows,
    },
  });
  return response.data;
};

export const exportResults = async (
  taskId: string,
  format: 'csv' | 'xlsx',
  include: 'all' | 'summary' | 'detailed' = 'all'
): Promise<Blob> => {
  const response = await api.get(`/export/${taskId}`, {
    params: { format, include },
    responseType: 'blob',
  });
  return response.data;
};

export const checkHealth = async (): Promise<boolean> => {
  try {
    await api.get('/health');
    return true;
  } catch {
    return false;
  }
};