/**
 * useAnalysis Hook
 * Convenient hook for analysis data management
 */

import { useDataContext } from '@/contexts';

export const useAnalysis = () => {
  const {
    state,
    uploadFile,
    pollTaskStatus,
    fetchResults,
    exportResults,
    clearAnalysis,
    clearError,
    getCachedResults,
  } = useDataContext();

  return {
    // State
    analysis: state.currentAnalysis,
    taskStatus: state.taskStatus,
    uploadStatus: state.uploadStatus,
    isLoading: state.isLoading,
    error: state.error,

    // Actions
    uploadFile,
    pollTaskStatus,
    fetchResults,
    exportResults,
    clearAnalysis,
    clearError,
    getCachedResults,

    // Computed
    hasResults: !!state.currentAnalysis,
    isProcessing: state.taskStatus?.status === 'processing' || state.taskStatus?.status === 'pending',
    isCompleted: state.taskStatus?.status === 'completed',
    isFailed: state.taskStatus?.status === 'failed',
    progress: state.taskStatus?.progress || 0,
  };
};
