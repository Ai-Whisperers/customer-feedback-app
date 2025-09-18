/**
 * API client for Customer Feedback Analyzer
 * This file now re-exports the new modular API implementation
 * Maintaining backward compatibility while using Clean Architecture
 */

// Re-export everything from the new modular API
export {
  // Types
  type UploadResponse,
  type TaskStatus,
  type StatusResponse,
  type AnalysisResults,
  type FileInfo,
  // Methods
  uploadFile,
  getStatus,
  getRawStatus,
  getResults,
  exportResults,
  checkHealth,
  // New cancellation methods
  cancelRequest,
  cancelAllRequests,
  requestManager
} from './api/index';