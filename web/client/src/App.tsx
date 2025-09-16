/**
 * Main application component
 * Customer AI Driven Feedback Analyzer v3.1.0
 */

import React, { useState, useEffect } from 'react';
import { FileUpload } from '@/components/FileUpload';
import { ProgressTracker } from '@/components/ProgressTracker';
import { ResultsVisualization } from '@/components/ResultsVisualization';
import { getResults, UploadResponse, AnalysisResults, checkHealth } from '@/lib/api';

type AppState = 'idle' | 'uploading' | 'processing' | 'completed' | 'error';

function App() {
  const [state, setState] = useState<AppState>('idle');
  const [taskId, setTaskId] = useState<string | null>(null);
  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploadInfo, setUploadInfo] = useState<UploadResponse | null>(null);
  const [isHealthy, setIsHealthy] = useState(true);

  // Check API health on mount
  useEffect(() => {
    checkHealth().then(setIsHealthy);
  }, []);

  const handleUploadSuccess = (response: UploadResponse) => {
    setUploadInfo(response);
    setTaskId(response.task_id);
    setState('processing');
    setError(null);
  };

  const handleUploadError = (errorMessage: string) => {
    setState('error');
    setError(errorMessage);
  };

  const handleProcessingComplete = async () => {
    if (!taskId) return;

    try {
      const analysisResults = await getResults(taskId, 'json', true);
      setResults(analysisResults);
      setState('completed');
    } catch (err: any) {
      setState('error');
      setError('Failed to retrieve results');
    }
  };

  const handleProcessingError = (errorMessage: string) => {
    setState('error');
    setError(errorMessage);
  };

  const resetApp = () => {
    setState('idle');
    setTaskId(null);
    setResults(null);
    setError(null);
    setUploadInfo(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Customer Feedback Analyzer
              </h1>
              <p className="text-sm text-gray-500 mt-1">
                AI-powered sentiment and NPS analysis
              </p>
            </div>
            {!isHealthy && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded-md text-sm">
                API connection issue
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error State */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <div className="mt-1 text-sm text-red-700">{error}</div>
              </div>
              <div className="ml-auto pl-3">
                <button
                  onClick={resetApp}
                  className="text-red-600 hover:text-red-500 text-sm font-medium"
                >
                  Try Again
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Upload State */}
        {state === 'idle' && (
          <div className="space-y-6">
            <FileUpload
              onUploadSuccess={handleUploadSuccess}
              onUploadError={handleUploadError}
            />
          </div>
        )}

        {/* Processing State */}
        {state === 'processing' && taskId && (
          <div className="space-y-6">
            <ProgressTracker
              taskId={taskId}
              onComplete={handleProcessingComplete}
              onError={handleProcessingError}
            />

            {uploadInfo && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="text-sm font-medium text-blue-800 mb-2">
                  File Information
                </h3>
                <div className="text-sm text-blue-700 space-y-1">
                  <p>Total comments: {uploadInfo.file_info.total_comments}</p>
                  <p>Estimated time: {uploadInfo.estimated_time_seconds}s</p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Results State */}
        {state === 'completed' && results && taskId && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">
                Analysis Complete
              </h2>
              <button
                onClick={resetApp}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700"
              >
                Analyze Another File
              </button>
            </div>

            <ResultsVisualization results={results} taskId={taskId} />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
