/**
 * Drag and drop file upload component
 * Supports CSV and Excel file formats
 */

import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { uploadFile } from '@/lib/api';
import type { UploadResponse } from '@/lib/api';

interface FileUploadProps {
  onUploadSuccess: (response: UploadResponse) => void;
  onUploadError: (error: string) => void;
}

export const FileUpload: React.FC<FileUploadProps> = ({
  onUploadSuccess,
  onUploadError,
}) => {
  const [isUploading, setIsUploading] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (acceptedFiles.length === 0) return;

      const file = acceptedFiles[0];
      setFileName(file.name);
      setIsUploading(true);

      try {
        const response = await uploadFile(file);
        onUploadSuccess(response);
      } catch (error: any) {
        const message = error.response?.data?.detail?.details ||
                       error.response?.data?.detail?.error ||
                       'Upload failed';
        onUploadError(message);
        setFileName(null);
      } finally {
        setIsUploading(false);
      }
    },
    [onUploadSuccess, onUploadError]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
    },
    maxFiles: 1,
    disabled: isUploading,
  });

  return (
    <div
      {...getRootProps()}
      className={`
        relative overflow-hidden rounded-lg border-2 border-dashed p-12
        transition-all duration-200 cursor-pointer
        ${isDragActive
          ? 'border-primary-500 bg-primary-50'
          : 'border-gray-300 bg-white hover:border-gray-400'
        }
        ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}
      `}
    >
      <input {...getInputProps()} />

      <div className="text-center">
        {/* Upload Icon */}
        <svg
          className={`mx-auto h-12 w-12 ${isDragActive ? 'text-primary-500' : 'text-gray-400'}`}
          stroke="currentColor"
          fill="none"
          viewBox="0 0 48 48"
          aria-hidden="true"
        >
          <path
            d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
            strokeWidth={2}
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>

        {/* Text */}
        <div className="mt-4">
          {isUploading ? (
            <div className="space-y-2">
              <div className="text-sm font-medium text-gray-900">
                Uploading {fileName}...
              </div>
              <div className="animate-pulse">
                <div className="h-2 bg-primary-200 rounded-full w-48 mx-auto"></div>
              </div>
            </div>
          ) : isDragActive ? (
            <p className="text-sm font-medium text-primary-600">
              Drop your file here
            </p>
          ) : (
            <>
              <p className="text-sm font-medium text-gray-900">
                Drop your CSV or Excel file here, or click to browse
              </p>
              <p className="mt-1 text-xs text-gray-500">
                Supported formats: CSV, XLSX, XLS
              </p>
            </>
          )}
        </div>

        {/* File requirements */}
        {!isUploading && (
          <div className="mt-6 text-xs text-gray-500">
            <p>File must contain columns:</p>
            <ul className="mt-1 space-y-1">
              <li>• Nota (rating 0-10)</li>
              <li>• Comentario Final (min 3 characters)</li>
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};