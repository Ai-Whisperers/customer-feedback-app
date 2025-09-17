import React from 'react';
import { GlassButton } from '@/components/ui';

interface FileInfoProps {
  file: File;
  onClear: () => void;
}

export const FileInfo: React.FC<FileInfoProps> = ({ file, onClear }) => {
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="p-4 bg-green-50/80 dark:bg-green-900/20 border border-green-300 dark:border-green-700 rounded-lg">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <svg
            className="w-8 h-8 text-green-600 dark:text-green-400"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
              clipRule="evenodd"
            />
          </svg>
          <div>
            <p className="font-medium text-gray-800 dark:text-gray-200">
              {file.name}
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {formatFileSize(file.size)}
            </p>
          </div>
        </div>
        <GlassButton
          onClick={onClear}
          variant="ghost"
          size="sm"
        >
          Cambiar
        </GlassButton>
      </div>
    </div>
  );
};