/**
 * Feedback Repository - Handles all feedback analysis operations
 * Following Repository Pattern and Dependency Inversion Principle (DIP)
 */

import type { IHttpClient } from '../core/http-client';
import { requestManager } from '../core/request-manager';
import type {
  UploadResponse,
  TaskStatus,
  AnalysisResults
} from '../types/feedback-types';

export class FeedbackRepository {
  constructor(private httpClient: IHttpClient) {}

  /**
   * Uploads a file for analysis
   */
  async uploadFile(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

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
   * Gets the status of a task
   */
  async getStatus(taskId: string): Promise<TaskStatus> {
    const key = `status-${taskId}`;
    const controller = requestManager.createController(key);

    try {
      const response = await this.httpClient.get<TaskStatus>(
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