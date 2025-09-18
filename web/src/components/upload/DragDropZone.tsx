import React from 'react';
import { GlassButton, GlassBadge } from '@/components/ui';

interface DragDropZoneProps {
  dragActive: boolean;
  onDragEnter: (e: React.DragEvent) => void;
  onDragLeave: (e: React.DragEvent) => void;
  onDragOver: (e: React.DragEvent) => void;
  onDrop: (e: React.DragEvent) => void;
  onFileSelect: () => void;
  isLoading: boolean;
  maxSizeMB: number;
  error: boolean;
}

export const DragDropZone: React.FC<DragDropZoneProps> = ({
  dragActive,
  onDragEnter,
  onDragLeave,
  onDragOver,
  onDrop,
  onFileSelect,
  isLoading,
  maxSizeMB,
  error,
}) => {
  return (
    <div
      className={`
        relative
        border-2
        border-dashed
        rounded-xl
        p-8
        transition-all
        duration-300
        ${
          dragActive
            ? 'border-blue-500 bg-blue-50/50 dark:bg-blue-900/20'
            : 'border-gray-300 dark:border-gray-600 hover:border-blue-400'
        }
        ${error ? 'border-red-400 bg-red-50/30' : ''}
      `}
      onDragEnter={onDragEnter}
      onDragLeave={onDragLeave}
      onDragOver={onDragOver}
      onDrop={onDrop}
    >
      <div className="text-center space-y-4">
        <div className="flex justify-center">
          <svg
            className={`w-16 h-16 ${
              dragActive ? 'text-blue-500' : 'text-gray-400'
            }`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.5"
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
        </div>

        <div>
          <p className="text-lg text-gray-700 dark:text-gray-300">
            {dragActive
              ? 'Suelta el archivo aquí'
              : 'Arrastra y suelta tu archivo aquí'}
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">o</p>
        </div>

        <GlassButton
          onClick={onFileSelect}
          variant="primary"
          disabled={isLoading}
          loading={isLoading}
        >
          Seleccionar Archivo
        </GlassButton>

        <div className="flex flex-wrap justify-center gap-2 mt-4">
          <GlassBadge variant="info" size="sm">
            CSV
          </GlassBadge>
          <GlassBadge variant="info" size="sm">
            XLSX
          </GlassBadge>
          <GlassBadge variant="info" size="sm">
            XLS
          </GlassBadge>
          <span className="text-xs text-gray-500">
            Máximo {maxSizeMB}MB
          </span>
        </div>
      </div>
    </div>
  );
};