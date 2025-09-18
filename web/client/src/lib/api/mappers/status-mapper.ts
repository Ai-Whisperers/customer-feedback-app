/**
 * Status Mapper - Maps backend status to frontend format
 * Handles the discrepancy between backend and frontend status values
 */

import type {
  StatusResponse,
  TaskStatus,
  BackendTaskStatus,
  FrontendTaskStatus
} from '../types/feedback-types';

/**
 * Maps backend status enum to frontend status enum
 */
export function mapBackendStatusToFrontend(status: BackendTaskStatus): FrontendTaskStatus {
  const statusMap: Record<BackendTaskStatus, FrontendTaskStatus> = {
    'queued': 'pending',
    'processing': 'processing',
    'completed': 'completed',
    'failed': 'failed',
    'expired': 'failed'
  };

  return statusMap[status] || 'pending';
}

/**
 * Maps full StatusResponse from backend to simplified TaskStatus for frontend
 */
export function mapStatusResponseToTaskStatus(response: StatusResponse): TaskStatus {
  // Extract the first message from messages array if available
  const message = response.messages && response.messages.length > 0
    ? response.messages[0]
    : response.current_step || 'Procesando...';

  // Calculate processed/total rows from progress if not available
  // This is an approximation since backend doesn't send these fields
  const estimatedTotalRows = 100; // Default estimation
  const processedRows = Math.round((response.progress / 100) * estimatedTotalRows);

  return {
    task_id: response.task_id,
    status: mapBackendStatusToFrontend(response.status),
    progress: response.progress,
    message,
    processed_rows: processedRows,
    total_rows: estimatedTotalRows,
    error: response.error
  };
}

/**
 * Extracts detailed information from StatusResponse
 * Useful for displaying additional details in UI
 */
export function extractStatusDetails(response: StatusResponse) {
  return {
    currentStep: response.current_step,
    estimatedTimeRemaining: response.estimated_remaining_seconds,
    startedAt: response.started_at,
    completedAt: response.completed_at,
    duration: response.duration_seconds,
    resultsReady: response.results_available,
    canRetry: response.retry_available,
    errorDetails: response.details,
    allMessages: response.messages
  };
}