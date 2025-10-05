/**
 * Data State Types
 * Global state for backend data, analysis results, and business logic
 * Re-exports API types for consistency
 */

import type { AnalysisResults, TaskStatus, UploadResponse } from '@/utils/api/types';

export interface DataState {
  currentAnalysis: AnalysisResults | null;
  taskStatus: TaskStatus | null;
  uploadStatus: UploadResponse | null;
  isLoading: boolean;
  error: string | null;
  cache: Map<string, AnalysisResults>;
}

export interface DataContextValue {
  state: DataState;
  uploadFile: (file: File) => Promise<string>;
  pollTaskStatus: (taskId: string) => Promise<void>;
  fetchResults: (taskId: string) => Promise<void>;
  exportResults: (taskId: string, format: 'csv' | 'xlsx' | 'all') => Promise<void>;
  clearAnalysis: () => void;
  clearError: () => void;
  getCachedResults: (taskId: string) => AnalysisResults | null;
  setCachedResults: (taskId: string, results: AnalysisResults) => void;
  resetState: () => void;
}
