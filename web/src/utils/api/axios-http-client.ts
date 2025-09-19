/**
 * Axios HTTP Client Implementation
 * Implements IHttpClient with AbortController support
 */

import axios from 'axios';
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import type { IHttpClient, HttpRequestConfig, HttpResponse, HttpError } from './http-client';
import type { ZodSchema } from 'zod';

export class AxiosHttpClient implements IHttpClient {
  private axiosInstance: AxiosInstance;
  private validationSchemas: Map<string, ZodSchema> = new Map();

  constructor(baseURL: string, defaultHeaders?: Record<string, string>) {
    this.axiosInstance = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
        ...defaultHeaders,
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Response interceptor for error handling
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      (error) => {
        // Log full error for debugging
        console.error('[AxiosHttpClient] Request failed:', {
          url: error.config?.url,
          method: error.config?.method,
          status: error.response?.status,
          data: error.response?.data,
          message: error.message
        });

        const httpError: HttpError = {
          message: 'An error occurred',
          status: error.response?.status,
          code: error.code,
        };

        if (error.response) {
          // Handle different response formats from backend
          const responseData = error.response.data;

          if (responseData?.detail) {
            // FastAPI error format
            httpError.message = responseData.detail?.details ||
                              responseData.detail?.error ||
                              responseData.detail ||
                              httpError.message;
            httpError.details = responseData.detail;
          } else if (responseData?.error) {
            // Alternative error format
            httpError.message = responseData.error;
            httpError.details = responseData;
          } else if (responseData?.message) {
            // Generic message format
            httpError.message = responseData.message;
            httpError.details = responseData;
          } else if (typeof responseData === 'string') {
            // Plain text error
            httpError.message = responseData;
          }
        } else if (error.code === 'ECONNABORTED') {
          httpError.message = 'Request was cancelled';
        } else if (error.code === 'ERR_NETWORK') {
          httpError.message = 'Network error - Unable to connect to server';
        } else if (error.message) {
          httpError.message = error.message;
        }

        return Promise.reject(httpError);
      }
    );
  }

  private mapConfig(config?: HttpRequestConfig): AxiosRequestConfig {
    return {
      headers: config?.headers,
      params: config?.params,
      signal: config?.signal,
      responseType: config?.responseType as AxiosRequestConfig['responseType'],
      timeout: config?.timeout,
    };
  }

  private mapResponse<T>(response: AxiosResponse<T>): HttpResponse<T> {
    return {
      data: response.data,
      status: response.status,
      headers: response.headers as Record<string, string>,
    };
  }

  /**
   * Register a validation schema for a specific endpoint
   */
  registerSchema(endpoint: string, schema: ZodSchema): void {
    this.validationSchemas.set(endpoint, schema);
  }


  async get<T = unknown>(url: string, config?: HttpRequestConfig): Promise<HttpResponse<T>> {
    const response = await this.axiosInstance.get<T>(url, this.mapConfig(config));
    return this.mapResponse(response);
  }

  async post<T = unknown>(url: string, data?: unknown, config?: HttpRequestConfig): Promise<HttpResponse<T>> {
    const response = await this.axiosInstance.post<T>(url, data, this.mapConfig(config));
    return this.mapResponse(response);
  }

  async put<T = unknown>(url: string, data?: unknown, config?: HttpRequestConfig): Promise<HttpResponse<T>> {
    const response = await this.axiosInstance.put<T>(url, data, this.mapConfig(config));
    return this.mapResponse(response);
  }

  async delete<T = unknown>(url: string, config?: HttpRequestConfig): Promise<HttpResponse<T>> {
    const response = await this.axiosInstance.delete<T>(url, this.mapConfig(config));
    return this.mapResponse(response);
  }
}