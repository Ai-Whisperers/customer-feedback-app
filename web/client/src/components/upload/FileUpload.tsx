import React, { useState, useRef } from 'react';
import { GlassCard } from '@/components/ui';
import { DragDropZone } from './DragDropZone';
import { FileInfo } from './FileInfo';
import { FormatRequirements } from './FormatRequirements';
import { ErrorMessage } from './ErrorMessage';

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

        <input
          ref={inputRef}
          type="file"
          accept={accept}
          onChange={handleChange}
          className="hidden"
          disabled={isLoading}
        />

        <DragDropZone
          dragActive={dragActive}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onFileSelect={() => inputRef.current?.click()}
          isLoading={isLoading}
          maxSizeMB={maxSizeMB}
          error={!!error}
        />

        {error && <ErrorMessage message={error} />}

        {selectedFile && !error && (
          <FileInfo
            file={selectedFile}
            onClear={() => {
              setSelectedFile(null);
              setError('');
            }}
          />
        )}

        <FormatRequirements />
      </div>
    </GlassCard>
  );
};