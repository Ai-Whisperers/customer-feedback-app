/**
 * API Module - Clean Architecture Implementation
 * Exports the configured API client with cancellation support
 */

import { AxiosHttpClient } from './infrastructure/axios-http-client';
import { FeedbackRepository } from './repositories/feedback-repository';
import { requestManager } from './core/request-manager';

// Re-export types
export type {
  UploadResponse,
  TaskStatus,
  AnalysisResults
} from './types/feedback-types';

// Create HTTP client instance
const httpClient = new AxiosHttpClient('/api');

// Create repository instance
const feedbackRepository = new FeedbackRepository(httpClient);

// Export API methods (maintaining backward compatibility)
export const uploadFile = feedbackRepository.uploadFile.bind(feedbackRepository);
export const getStatus = feedbackRepository.getStatus.bind(feedbackRepository);
export const getRawStatus = feedbackRepository.getRawStatus.bind(feedbackRepository);
export const getResults = feedbackRepository.getResults.bind(feedbackRepository);
export const exportResults = feedbackRepository.exportResults.bind(feedbackRepository);
export const checkHealth = feedbackRepository.checkHealth.bind(feedbackRepository);

// Export cancellation methods
export const cancelRequest = feedbackRepository.cancelRequest.bind(feedbackRepository);
export const cancelAllRequests = feedbackRepository.cancelAllRequests.bind(feedbackRepository);

// Export request manager for advanced usage
export { requestManager };