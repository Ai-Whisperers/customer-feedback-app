import React, { useState, useRef } from 'react';
import { GlassCard, GlassButton, GlassBadge } from '../../components/ui';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  accept?: string;
  maxSizeMB?: number;
  isLoading?: boolean;
}

export const FileUpload: React.FC<FileUploadProps> = ({
  onFileSelect,
  accept = '.csv,.xlsx,.xls',
  maxSizeMB = 20,
  isLoading = false,
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string>('');
  const inputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File): boolean => {
    setError('');

    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    if (file.size > maxSizeBytes) {
      setError(`El archivo excede el tamaño máximo de ${maxSizeMB}MB`);
      return false;
    }

    const fileExtension = file.name.split('.').pop()?.toLowerCase();
    const acceptedExtensions = accept.replace(/\./g, '').split(',');

    if (fileExtension && !acceptedExtensions.includes(fileExtension)) {
      setError('Formato de archivo no soportado. Use CSV o Excel.');
      return false;
    }

    return true;
  };

  const handleFile = (file: File) => {
    if (validateFile(file)) {
      setSelectedFile(file);
      onFileSelect(file);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <GlassCard variant="gradient" className="w-full">
      <div className="space-y-4">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100 mb-2">
            Cargar Archivo de Comentarios
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Sube un archivo CSV o Excel con los comentarios de clientes
          </p>
        </div>

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
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            ref={inputRef}
            type="file"
            accept={accept}
            onChange={handleChange}
            className="hidden"
            disabled={isLoading}
          />

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
              onClick={() => inputRef.current?.click()}
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

        {error && (
          <div className="p-3 bg-red-100/80 dark:bg-red-900/30 border border-red-300 dark:border-red-700 rounded-lg">
            <p className="text-red-700 dark:text-red-400 text-sm">{error}</p>
          </div>
        )}

        {selectedFile && !error && (
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
                    {selectedFile.name}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {formatFileSize(selectedFile.size)}
                  </p>
                </div>
              </div>
              <GlassButton
                onClick={() => {
                  setSelectedFile(null);
                  setError('');
                }}
                variant="ghost"
                size="sm"
              >
                Cambiar
              </GlassButton>
            </div>
          </div>
        )}

        <div className="bg-blue-50/50 dark:bg-blue-900/20 p-4 rounded-lg">
          <h3 className="font-semibold text-blue-800 dark:text-blue-300 mb-2">
            Formato Requerido
          </h3>
          <ul className="space-y-1 text-sm text-blue-700 dark:text-blue-400">
            <li className="flex items-start">
              <span className="mr-2">•</span>
              <span>
                <strong>Columna "Nota":</strong> Calificación del 0 al 10
              </span>
            </li>
            <li className="flex items-start">
              <span className="mr-2">•</span>
              <span>
                <strong>Columna "Comentario Final":</strong> Texto del comentario (3-2000 caracteres)
              </span>
            </li>
            <li className="flex items-start">
              <span className="mr-2">•</span>
              <span>
                <strong>Columna "NPS" (opcional):</strong> Si existe, se usará directamente
              </span>
            </li>
          </ul>
        </div>
      </div>
    </GlassCard>
  );
};