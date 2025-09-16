/**
 * Real-time progress tracking component
 * Polls for task status and displays progress
 */

import React, { useEffect, useState } from 'react';
import { getStatus, TaskStatus } from '@/lib/api';

interface ProgressTrackerProps {
  taskId: string;
  onComplete: () => void;
  onError: (error: string) => void;
}

export const ProgressTracker: React.FC<ProgressTrackerProps> = ({
  taskId,
  onComplete,
  onError,
}) => {
  const [status, setStatus] = useState<TaskStatus | null>(null);
  const [pollCount, setPollCount] = useState(0);

  useEffect(() => {
    if (!taskId) return;

    const pollStatus = async () => {
      try {
        const taskStatus = await getStatus(taskId);
        setStatus(taskStatus);

        if (taskStatus.status === 'completed') {
          onComplete();
          return;
        }

        if (taskStatus.status === 'failed') {
          onError(taskStatus.error || 'Task failed');
          return;
        }

        // Continue polling
        setPollCount(prev => prev + 1);
      } catch (error) {
        console.error('Failed to get status:', error);
        setPollCount(prev => prev + 1);
      }
    };

    // Initial poll
    pollStatus();

    // Set up interval for polling
    const interval = setInterval(pollStatus, 2000);

    // Clean up
    return () => clearInterval(interval);
  }, [taskId, pollCount, onComplete, onError]);

  if (!status) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          <div className="h-2 bg-gray-200 rounded w-full"></div>
        </div>
      </div>
    );
  }

  const progress = status.progress || 0;
  const progressPercentage = Math.round(progress * 100);

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <div className="space-y-4">
        {/* Status Header */}
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900">
            Processing Feedback
          </h3>
          <span
            className={`
              inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
              ${status.status === 'processing'
                ? 'bg-blue-100 text-blue-800'
                : status.status === 'completed'
                ? 'bg-green-100 text-green-800'
                : status.status === 'failed'
                ? 'bg-red-100 text-red-800'
                : 'bg-gray-100 text-gray-800'
              }
            `}
          >
            {status.status.charAt(0).toUpperCase() + status.status.slice(1)}
          </span>
        </div>

        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm text-gray-600">
            <span>Progress</span>
            <span>{progressPercentage}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div
              className="bg-primary-600 h-2.5 rounded-full transition-all duration-300 ease-out"
              style={{ width: `${progressPercentage}%` }}
            ></div>
          </div>
        </div>

        {/* Details */}
        {status.current_batch && status.total_batches && (
          <div className="text-sm text-gray-600">
            Processing batch {status.current_batch} of {status.total_batches}
          </div>
        )}

        {status.items_processed !== undefined && status.total_items && (
          <div className="text-sm text-gray-600">
            Analyzed {status.items_processed} of {status.total_items} comments
          </div>
        )}

        {/* Processing Animation */}
        {status.status === 'processing' && (
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-primary-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-2 h-2 bg-primary-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-2 h-2 bg-primary-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
            <span>Analyzing with AI...</span>
          </div>
        )}
      </div>
    </div>
  );
};