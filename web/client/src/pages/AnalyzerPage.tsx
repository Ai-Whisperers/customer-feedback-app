import React, { useState } from 'react';
import { FileUpload } from '@/components/upload/FileUpload';
import { ProgressTracker } from '@/components/progress/ProgressTracker';
import { ResultsVisualization } from '@/components/ResultsVisualization';
import { GlassCard } from '@/components/ui';
import { uploadFile, getStatus, getResults } from '@/lib/api';

type AppState = 'idle' | 'uploading' | 'processing' | 'completed' | 'error';

export const AnalyzerPage: React.FC = () => {
  const [appState, setAppState] = useState<AppState>('idle');
  const [taskId, setTaskId] = useState<string>('');
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string>('');
  const [statusMessage, setStatusMessage] = useState<string>('');
  const [processedRows, setProcessedRows] = useState(0);
  const [totalRows, setTotalRows] = useState(0);

  const handleFileUpload = async (file: File) => {
    setAppState('uploading');
    setError('');

    try {
      const response = await uploadFile(file);
      setTaskId(response.task_id);
      setAppState('processing');
      pollStatus(response.task_id);
    } catch (err) {
      setError('Error al cargar el archivo. Por favor, intente nuevamente.');
      setAppState('error');
    }
  };

  const pollStatus = async (id: string) => {
    const interval = setInterval(async () => {
      try {
        const status = await getStatus(id);
        setProgress(status.progress || 0);
        setStatusMessage(status.message || 'Procesando...');
        setProcessedRows(status.processed_rows || 0);
        setTotalRows(status.total_rows || 0);

        if (status.status === 'completed') {
          clearInterval(interval);
          const analysisResults = await getResults(id, 'json', true);
          setResults(analysisResults);
          setAppState('completed');
        } else if (status.status === 'failed') {
          clearInterval(interval);
          setError('El análisis falló. Por favor, verifique su archivo e intente nuevamente.');
          setAppState('error');
        }
      } catch (err) {
        clearInterval(interval);
        setError('Error al obtener el estado del análisis.');
        setAppState('error');
      }
    }, 2000);
  };

  // Export function is handled directly by ResultsVisualization component

  const handleReset = () => {
    setAppState('idle');
    setTaskId('');
    setProgress(0);
    setResults(null);
    setError('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 dark:from-gray-900 dark:via-purple-900 dark:to-blue-900">
      <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>

      <div className="relative z-10 container mx-auto px-4 py-8">
        <header className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
            Analizador de Comentarios con IA
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Descubre insights valiosos de tus clientes mediante análisis avanzado de emociones,
            riesgo de abandono y puntos de dolor
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
                    Cargando archivo...
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
              <ResultsVisualization results={results} taskId={taskId} />
              <div className="text-center">
                <button
                  onClick={handleReset}
                  className="px-6 py-3 bg-gradient-to-r from-gray-500 to-gray-600 text-white rounded-lg hover:from-gray-600 hover:to-gray-700 transition-all duration-300"
                >
                  Analizar Otro Archivo
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
                  Ocurrió un Error
                </h2>
                <p className="text-gray-600 dark:text-gray-400 mb-6">
                  {error}
                </p>
                <button
                  onClick={handleReset}
                  className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all duration-300"
                >
                  Intentar Nuevamente
                </button>
              </div>
            </GlassCard>
          )}
        </main>

        <footer className="text-center mt-16 pb-8">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Powered by OpenAI GPT-4 - Análisis en Español e Inglés
          </p>
        </footer>
      </div>
    </div>
  );
};