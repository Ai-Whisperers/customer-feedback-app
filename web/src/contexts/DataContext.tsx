import React, { createContext, useContext, useState, useCallback, useMemo, useRef } from 'react';
import type { DataContextValue, DataState } from '@/types';
import type { AnalysisResults, UploadResponse } from '@/utils/api/types';
import * as api from '@/utils/api';

const DEFAULT_STATE: DataState = {
  currentAnalysis: null,
  taskStatus: null,
  uploadStatus: null,
  isLoading: false,
  error: null,
  cache: new Map(),
};

const POLL_INTERVAL_MS = 2000; // 2 seconds
const MAX_POLL_DURATION_MS = 1000 * 60 * 5; // 5 minutes

const DataContext = createContext<DataContextValue | null>(null);

export const DataProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, setState] = useState<DataState>(DEFAULT_STATE);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const pollingStartTimeRef = useRef<number | null>(null);

  // Helper to update state
  const updateState = useCallback((updates: Partial<DataState>) => {
    setState(prev => ({ ...prev, ...updates }));
  }, []);

  // Upload file
  const uploadFile = useCallback(async (file: File): Promise<string> => {
    try {
      updateState({ isLoading: true, error: null });

      const response: UploadResponse = await api.uploadFile(file);

      updateState({
        uploadStatus: response,
        isLoading: false,
      });

      return response.task_id;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to upload file';
      updateState({
        isLoading: false,
        error: errorMessage,
      });
      throw error;
    }
  }, [updateState]);

  // Clear polling interval
  const clearPolling = useCallback(() => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
    pollingStartTimeRef.current = null;
  }, []);

  // Poll task status
  const pollTaskStatus = useCallback(
    async (taskId: string): Promise<void> => {
      // Clear any existing polling
      clearPolling();

      pollingStartTimeRef.current = Date.now();

      const poll = async () => {
        try {
          // Check if polling has exceeded max duration
          if (
            pollingStartTimeRef.current &&
            Date.now() - pollingStartTimeRef.current > MAX_POLL_DURATION_MS
          ) {
            clearPolling();
            updateState({
              error: 'Task polling timeout exceeded. Please check status manually.',
              isLoading: false,
            });
            return;
          }

          const taskStatus = await api.getStatus(taskId);

          updateState({ taskStatus, error: null });

          // If completed or failed, stop polling and fetch results
          if (taskStatus.status === 'completed') {
            clearPolling();
            await fetchResults(taskId);
          } else if (taskStatus.status === 'failed') {
            clearPolling();
            updateState({
              isLoading: false,
              error: taskStatus.error || 'Analysis failed',
            });
          }
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to fetch status';
          updateState({ error: errorMessage });
          // Continue polling on error
        }
      };

      // Start polling
      updateState({ isLoading: true, error: null });
      await poll(); // First poll immediately
      pollingIntervalRef.current = setInterval(poll, POLL_INTERVAL_MS);
    },
    [clearPolling, updateState]
  );

  // Fetch results
  const fetchResults = useCallback(
    async (taskId: string): Promise<void> => {
      try {
        updateState({ isLoading: true, error: null });

        const results: AnalysisResults = await api.getResults(taskId);

        // Add to cache
        const cache = new Map(state.cache);
        cache.set(taskId, results);

        updateState({
          currentAnalysis: results,
          isLoading: false,
          cache,
        });
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to fetch results';
        updateState({
          isLoading: false,
          error: errorMessage,
        });
        throw error;
      }
    },
    [state.cache, updateState]
  );

  // Export results
  const exportResults = useCallback(
    async (taskId: string, format: 'csv' | 'xlsx' | 'all'): Promise<void> => {
      try {
        updateState({ isLoading: true, error: null });

        const blob = await api.exportResults(taskId, format === 'all' ? 'xlsx' : format);

        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `analysis_${taskId}.${format === 'csv' ? 'csv' : 'xlsx'}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        updateState({ isLoading: false });
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to export results';
        updateState({
          isLoading: false,
          error: errorMessage,
        });
        throw error;
      }
    },
    [updateState]
  );

  // Clear current analysis
  const clearAnalysis = useCallback(() => {
    clearPolling();
    updateState({
      currentAnalysis: null,
      taskStatus: null,
      uploadStatus: null,
      error: null,
      isLoading: false,
    });
  }, [clearPolling, updateState]);

  // Clear error
  const clearError = useCallback(() => {
    updateState({ error: null });
  }, [updateState]);

  // Get cached results
  const getCachedResults = useCallback(
    (taskId: string): AnalysisResults | null => {
      return state.cache.get(taskId) || null;
    },
    [state.cache]
  );

  // Set cached results
  const setCachedResults = useCallback(
    (taskId: string, results: AnalysisResults) => {
      const cache = new Map(state.cache);
      cache.set(taskId, results);
      updateState({ cache });
    },
    [state.cache, updateState]
  );

  // Reset entire state
  const resetState = useCallback(() => {
    clearPolling();
    api.cancelAllRequests();
    setState(DEFAULT_STATE);
  }, [clearPolling]);

  // Cleanup on unmount
  React.useEffect(() => {
    return () => {
      clearPolling();
      api.cancelAllRequests();
    };
  }, [clearPolling]);

  const value = useMemo<DataContextValue>(
    () => ({
      state,
      uploadFile,
      pollTaskStatus,
      fetchResults,
      exportResults,
      clearAnalysis,
      clearError,
      getCachedResults,
      setCachedResults,
      resetState,
    }),
    [
      state,
      uploadFile,
      pollTaskStatus,
      fetchResults,
      exportResults,
      clearAnalysis,
      clearError,
      getCachedResults,
      setCachedResults,
      resetState,
    ]
  );

  return <DataContext.Provider value={value}>{children}</DataContext.Provider>;
};

export const useDataContext = (): DataContextValue => {
  const context = useContext(DataContext);
  if (!context) {
    throw new Error('useDataContext must be used within DataProvider');
  }
  return context;
};
