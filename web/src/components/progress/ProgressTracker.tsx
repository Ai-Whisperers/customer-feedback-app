import React from 'react';
import { GlassCard, GlassProgress, GlassBadge } from '@/components/ui';

interface ProgressTrackerProps {
  taskId: string;
  progress: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  message?: string;
  processedRows?: number;
  totalRows?: number;
  estimatedTime?: number;
  errors?: string[];
}

export const ProgressTracker: React.FC<ProgressTrackerProps> = ({
  taskId,
  progress,
  status,
  message,
  processedRows = 0,
  totalRows = 0,
  estimatedTime,
  errors = [],
}) => {
  const getStatusColor = () => {
    switch (status) {
      case 'pending':
        return 'warning';
      case 'processing':
        return 'primary';
      case 'completed':
        return 'success';
      case 'failed':
        return 'danger';
      default:
        return 'primary';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'pending':
        return 'En Espera';
      case 'processing':
        return 'Procesando';
      case 'completed':
        return 'Completado';
      case 'failed':
        return 'Error';
      default:
        return 'Desconocido';
    }
  };

  const formatTime = (seconds: number): string => {
    if (seconds < 60) return `${Math.round(seconds)} segundos`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.round(seconds % 60);
    return `${minutes}m ${remainingSeconds}s`;
  };

  return (
    <GlassCard variant="gradient" className="w-full">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100">
            Análisis en Progreso
          </h2>
          <GlassBadge variant={getStatusColor()} size="md">
            {getStatusText()}
          </GlassBadge>
        </div>

        <GlassProgress
          value={progress}
          label="Progreso General"
          variant={getStatusColor()}
          animated={status === 'processing'}
          size="lg"
        />

        {message && (
          <div className="p-4 bg-blue-50/50 dark:bg-blue-900/20 rounded-lg">
            <p className="text-sm text-blue-700 dark:text-blue-300">
              {message}
            </p>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-white/50 dark:bg-gray-800/50 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
              Filas Procesadas
            </p>
            <p className="text-2xl font-bold text-gray-800 dark:text-gray-200">
              {processedRows}
              {totalRows > 0 && (
                <span className="text-lg text-gray-500">/{totalRows}</span>
              )}
            </p>
          </div>

          <div className="text-center p-4 bg-white/50 dark:bg-gray-800/50 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
              ID de Tarea
            </p>
            <p className="text-xs font-mono text-gray-700 dark:text-gray-300 break-all">
              {taskId}
            </p>
          </div>

          {estimatedTime !== undefined && (
            <div className="text-center p-4 bg-white/50 dark:bg-gray-800/50 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                Tiempo Estimado
              </p>
              <p className="text-2xl font-bold text-gray-800 dark:text-gray-200">
                {formatTime(estimatedTime)}
              </p>
            </div>
          )}
        </div>

        {status === 'processing' && (
          <div className="space-y-3">
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
              Etapas del Proceso
            </h3>
            <div className="space-y-2">
              <ProcessStep
                label="Validación de datos"
                completed={progress > 10}
                active={progress >= 0 && progress <= 10}
              />
              <ProcessStep
                label="Normalización de texto"
                completed={progress > 25}
                active={progress > 10 && progress <= 25}
              />
              <ProcessStep
                label="Análisis de emociones"
                completed={progress > 60}
                active={progress > 25 && progress <= 60}
              />
              <ProcessStep
                label="Extracción de puntos de dolor"
                completed={progress > 80}
                active={progress > 60 && progress <= 80}
              />
              <ProcessStep
                label="Generación de reporte"
                completed={progress === 100}
                active={progress > 80}
              />
            </div>
          </div>
        )}

        {errors.length > 0 && (
          <div className="p-4 bg-red-50/50 dark:bg-red-900/20 rounded-lg">
            <h3 className="text-sm font-semibold text-red-700 dark:text-red-300 mb-2">
              Errores Encontrados
            </h3>
            <ul className="space-y-1">
              {errors.map((error, index) => (
                <li
                  key={index}
                  className="text-sm text-red-600 dark:text-red-400 flex items-start"
                >
                  <span className="mr-2">-</span>
                  <span>{error}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </GlassCard>
  );
};

interface ProcessStepProps {
  label: string;
  completed: boolean;
  active: boolean;
}

const ProcessStep: React.FC<ProcessStepProps> = ({ label, completed, active }) => {
  return (
    <div className="flex items-center space-x-3">
      <div
        className={`
          w-8 h-8 rounded-full flex items-center justify-center
          ${
            completed
              ? 'bg-green-500 text-white'
              : active
              ? 'bg-blue-500 text-white animate-pulse'
              : 'bg-gray-300 dark:bg-gray-600 text-gray-500'
          }
        `}
      >
        {completed ? (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 13l4 4L19 7"
            />
          </svg>
        ) : active ? (
          <div className="w-3 h-3 bg-white rounded-full animate-ping" />
        ) : (
          <div className="w-3 h-3 bg-gray-400 rounded-full" />
        )}
      </div>
      <span
        className={`
          text-sm
          ${
            completed || active
              ? 'text-gray-800 dark:text-gray-200 font-medium'
              : 'text-gray-500 dark:text-gray-400'
          }
        `}
      >
        {label}
      </span>
    </div>
  );
};