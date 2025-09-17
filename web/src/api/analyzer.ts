const API_BASE_URL = '/api';

export interface UploadResponse {
  task_id: string;
}

export interface StatusResponse {
  state: 'PENDING' | 'PROCESSING' | 'SUCCESS' | 'FAILURE';
  progress: number;
  message?: string;
}

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

class AnalyzerAPI {
  async uploadFile(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Upload failed');
    }

    return response.json();
  }

  async getStatus(taskId: string): Promise<StatusResponse> {
    const response = await fetch(`${API_BASE_URL}/status/${taskId}`);

    if (!response.ok) {
      throw new Error('Failed to get status');
    }

    return response.json();
  }

  async getResults(taskId: string): Promise<AnalysisResults> {
    const response = await fetch(`${API_BASE_URL}/results/${taskId}`);

    if (!response.ok) {
      throw new Error('Failed to get results');
    }

    return response.json();
  }

  async exportResults(taskId: string, format: 'csv' | 'xlsx'): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/export/${taskId}?format=${format}`);

    if (!response.ok) {
      throw new Error('Export failed');
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analysis_${taskId}.${format}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }
}

export const analyzerApi = new AnalyzerAPI();