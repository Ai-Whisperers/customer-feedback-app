/**
 * Feedback Repository - Handles all feedback analysis operations
 * Following Repository Pattern and Dependency Inversion Principle (DIP)
 */

import type { IHttpClient } from '../core/http-client';
import { requestManager } from '../core/request-manager';
import type {
  UploadResponse,
  TaskStatus,
  StatusResponse,
  AnalysisResults
} from '../types/feedback-types';
import { mapStatusResponseToTaskStatus } from '../mappers/status-mapper';

export class FeedbackRepository {
  private httpClient: IHttpClient;

  constructor(httpClient: IHttpClient) {
    this.httpClient = httpClient;
  }

  /**
   * Uploads a file for analysis
   */
  async uploadFile(
    file: File,
    options?: {
      language_hint?: 'es' | 'en';
      segment?: string;
      priority?: 'normal' | 'high';
    }
  ): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    // Add optional form parameters
    if (options?.language_hint) {
      formData.append('language_hint', options.language_hint);
    }
    if (options?.segment) {
      formData.append('segment', options.segment);
    }
    if (options?.priority) {
      formData.append('priority', options.priority);
    }

    const controller = requestManager.createController('upload');

    try {
      const response = await this.httpClient.post<UploadResponse>(
        '/upload',
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' },
          signal: controller.signal,
        }
      );

      requestManager.complete('upload');
      return response.data;
    } catch (error) {
      requestManager.complete('upload');
      throw error;
    }
  }

  /**
   * Gets the status of a task (returns simplified TaskStatus)
   */
  async getStatus(taskId: string): Promise<TaskStatus> {
    const key = `status-${taskId}`;
    const controller = requestManager.createController(key);

    try {
      const response = await this.httpClient.get<StatusResponse>(
        `/status/${taskId}`,
        { signal: controller.signal }
      );

      requestManager.complete(key);
      // Map backend StatusResponse to frontend TaskStatus
      return mapStatusResponseToTaskStatus(response.data);
    } catch (error) {
      requestManager.complete(key);
      throw error;
    }
  }

  /**
   * Gets the raw status response from backend
   */
  async getRawStatus(taskId: string): Promise<StatusResponse> {
    const key = `status-raw-${taskId}`;
    const controller = requestManager.createController(key);

    try {
      const response = await this.httpClient.get<StatusResponse>(
        `/status/${taskId}`,
        { signal: controller.signal }
      );

      requestManager.complete(key);
      return response.data;
    } catch (error) {
      requestManager.complete(key);
      throw error;
    }
  }

  /**
   * Gets the analysis results
   */
  async getResults(
    taskId: string,
    format: 'json' | 'summary' = 'json',
    includeRows: boolean = true
  ): Promise<AnalysisResults> {
    const key = `results-${taskId}`;
    const controller = requestManager.createController(key);

    try {
      const response = await this.httpClient.get<AnalysisResults>(
        `/results/${taskId}`,
        {
          params: {
            format,
            include_rows: includeRows,
          },
          signal: controller.signal,
        }
      );

      requestManager.complete(key);
      return response.data;
    } catch (error) {
      requestManager.complete(key);
      throw error;
    }
  }

  /**
   * Exports results in specified format
   */
  async exportResults(
    taskId: string,
    format: 'csv' | 'xlsx',
    include: 'all' | 'summary' | 'detailed' = 'all'
  ): Promise<Blob> {
    const key = `export-${taskId}`;
    const controller = requestManager.createController(key);

    try {
      const response = await this.httpClient.get<Blob>(
        `/export/${taskId}`,
        {
          params: { format, include },
          responseType: 'blob',
          signal: controller.signal,
        }
      );

      requestManager.complete(key);
      return response.data;
    } catch (error) {
      requestManager.complete(key);
      throw error;
    }
  }

  /**
   * Checks API health
   */
  async checkHealth(): Promise<boolean> {
    const controller = requestManager.createController('health');

    try {
      await this.httpClient.get('/health', {
        signal: controller.signal,
        timeout: 5000
      });
      requestManager.complete('health');
      return true;
    } catch {
      requestManager.complete('health');
      return false;
    }
  }

  /**
   * Cancels a specific request
   */
  cancelRequest(key: string): void {
    requestManager.cancel(key);
  }

  /**
   * Cancels all active requests
   */
  cancelAllRequests(): void {
    requestManager.cancelAll();
  }
}