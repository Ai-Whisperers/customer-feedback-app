import React, { useState, useEffect, useRef } from 'react';
import { FileUpload } from '@/components/upload/FileUpload';
import { ProgressTracker } from '@/components/progress/ProgressTracker';
import { ResultsCharts } from '@/components/results/ResultsCharts';
import { ExportResults } from '@/components/export/ExportResults';
import { GlassCard } from '@/components/ui';
import { useTranslations } from '@/i18n';
import {
  uploadFile,
  getStatus,
  getResults,
  exportResults,
  cancelAllRequests
} from '@/utils/api';
import type { AnalysisResults } from '@/utils/api';

type AppState = 'idle' | 'uploading' | 'processing' | 'completed' | 'error';

export const AnalyzerPage: React.FC = () => {
  const { t } = useTranslations();
  const [appState, setAppState] = useState<AppState>('idle');
  const [taskId, setTaskId] = useState<string>('');
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [error, setError] = useState<string>('');
  const [statusMessage, setStatusMessage] = useState<string>('');
  const [processedRows, setProcessedRows] = useState(0);
  const [totalRows, setTotalRows] = useState(0);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const lastProgressRef = useRef<number>(0);
  const stallTimeRef = useRef<number>(Date.now());
  const currentTaskIdRef = useRef<string>('');

  const handleFileUpload = async (file: File) => {
    setAppState('uploading');
    setError('');

    try {
      const response = await uploadFile(file, {
        language_hint: 'es', // Default to Spanish, could be made configurable
        priority: 'normal'
      });

      // Check if upload was successful
      if (response.success && response.task_id) {
        setTaskId(response.task_id);
        setAppState('processing');

        // Show file info if available
        if (response.file_info) {
          if (import.meta.env.DEV) {
            console.log(`Processing ${response.file_info.rows} rows from ${response.file_info.name}`);
          }
        }
      } else {
        setError(response.message || t('analyzer.upload.error'));
        setAppState('error');
      }
    } catch (error) {
      // Log error details for debugging
      console.error('[AnalyzerPage] Upload error:', error);

      // Extract meaningful error message
      let errorMessage = t('analyzer.upload.errorRetry');

      if (error && typeof error === 'object') {
        if ('message' in error) {
          errorMessage = `Error: ${error.message}`;
        } else if ('details' in error) {
          errorMessage = `Error: ${(error as any).details}`;
        }
      }

      setError(errorMessage);
      setAppState('error');
    }
  };

  // Cleanup interval on unmount or when taskId changes
  useEffect(() => {
    if (!taskId || appState !== 'processing') return;

    // Cancel previous task's polling
    if (currentTaskIdRef.current && currentTaskIdRef.current !== taskId) {
      cancelAllRequests(); // Cancel previous task's requests
    }
    currentTaskIdRef.current = taskId;

    // Reset stall detection on new task
    lastProgressRef.current = 0;
    stallTimeRef.current = Date.now();

    const pollStatus = async () => {
      // Guard against race condition - only process if still the current task
      if (currentTaskIdRef.current !== taskId) {
        return;
      }

      try {
        const status = await getStatus(taskId);

        // Update UI with mapped status fields
        const currentProgress = status.progress || 0;
        setProgress(currentProgress);
        setStatusMessage(status.message || t('analyzer.analysis.inProgress'));

        // Use processed_rows and total_rows if available
        // These are now properly mapped from backend response
        if (status.processed_rows !== undefined) {
          setProcessedRows(status.processed_rows);
        }
        if (status.total_rows !== undefined) {
          setTotalRows(status.total_rows);
        }

        // Check for stall (no progress for 60 seconds)
        if (status.status === 'processing' || status.status === 'pending') {
          if (currentProgress > lastProgressRef.current || (status.processed_rows ?? 0) > lastProgressRef.current) {
            lastProgressRef.current = Math.max(currentProgress, status.processed_rows ?? 0);
            stallTimeRef.current = Date.now();
          } else {
            const stallDuration = Date.now() - stallTimeRef.current;
            if (stallDuration > 60000) { // 60 seconds timeout
              setError(t('analyzer.analysis.stalled'));
              setAppState('error');
              if (intervalRef.current) {
                clearInterval(intervalRef.current);
                intervalRef.current = null;
              }
              return;
            }
          }
        }

        if (status.status === 'completed') {
          // Double-check we're still the current task before fetching results
          if (currentTaskIdRef.current === taskId) {
            const analysisResults = await getResults(taskId, 'json', true);
            // Final check before setting results
            if (currentTaskIdRef.current === taskId) {
              setResults(analysisResults);
              setAppState('completed');
            }
          }
          if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
          }
        } else if (status.status === 'failed') {
          setError(t('analyzer.analysis.failed'));
          setAppState('error');
          if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
          }
        }
      } catch {
        setError(t('analyzer.analysis.statusError'));
        setAppState('error');
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
      }
    };

    // Start polling immediately
    pollStatus();

    // Set up interval
    intervalRef.current = setInterval(pollStatus, 2000);

    // Cleanup function
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      // Cancel any pending API requests
      cancelAllRequests();
    };
  }, [taskId, appState]);

  const handleExport = async (format: 'csv' | 'xlsx') => {
    if (!taskId) return;
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

  const handleReset = () => {
    // Clear any running interval
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    // Cancel any pending API requests
    cancelAllRequests();
    setAppState('idle');
    setTaskId('');
    setProgress(0);
    setResults(null);
    setError('');
    setStatusMessage('');
    setProcessedRows(0);
    setTotalRows(0);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 dark:from-gray-900 dark:via-purple-900 dark:to-blue-900">
      <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>

      <div className="relative z-10 container mx-auto px-4 py-8">
        <header className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
            {t('analyzer.title')}
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            {t('analyzer.subtitle')}
          </p>
        </header>

        <main className="max-w-7xl mx-auto space-y-8">
          {appState === 'idle' && (
            <div className="animate-fadeIn">
              <FileUpload
                onFileSelect={handleFileUpload}
                isLoading={false}
              />
            </div>
          )}

          {appState === 'uploading' && (
            <GlassCard variant="gradient">
              <div className="flex items-center justify-center py-12">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
                  <p className="text-lg text-gray-700 dark:text-gray-300">
                    {t('analyzer.upload.uploading')}
                  </p>
                </div>
              </div>
            </GlassCard>
          )}

          {appState === 'processing' && (
            <div className="animate-fadeIn">
              <ProgressTracker
                taskId={taskId}
                progress={progress}
                status="processing"
                message={statusMessage}
                processedRows={processedRows}
                totalRows={totalRows}
              />
            </div>
          )}

          {appState === 'completed' && results && (
            <div className="space-y-8 animate-fadeIn">
              <ResultsCharts results={results} />
              <ExportResults taskId={taskId} onExport={handleExport} />
              <div className="text-center">
                <button
                  onClick={handleReset}
                  className="px-6 py-3 bg-gradient-to-r from-gray-500 to-gray-600 text-white rounded-lg hover:from-gray-600 hover:to-gray-700 transition-all duration-300"
                >
                  {t('analyzer.actions.analyzeAnother')}
                </button>
              </div>
            </div>
          )}

          {appState === 'error' && (
            <GlassCard variant="gradient">
              <div className="text-center py-12">
                <div className="text-red-500 mb-4">
                  <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-100 mb-2">
                  {t('analyzer.error.title')}
                </h2>
                <p className="text-gray-600 dark:text-gray-400 mb-6">
                  {error}
                </p>
                <button
                  onClick={handleReset}
                  className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all duration-300"
                >
                  {t('analyzer.actions.tryAgain')}
                </button>
              </div>
            </GlassCard>
          )}
        </main>

        <footer className="text-center mt-16 pb-8">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {t('analyzer.footer.poweredBy')}
          </p>
        </footer>
      </div>
    </div>
  );
};