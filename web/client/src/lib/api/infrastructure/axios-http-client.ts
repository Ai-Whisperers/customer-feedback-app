/**
 * Axios HTTP Client Implementation
 * Implements IHttpClient with AbortController support
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import type { IHttpClient, HttpRequestConfig, HttpResponse, HttpError } from '../core/http-client';
import { ZodSchema } from 'zod';

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
        const httpError: HttpError = {
          message: 'An error occurred',
          status: error.response?.status,
          code: error.code,
        };

        if (error.response) {
          const { detail } = error.response.data;
          httpError.message = detail?.details || detail?.error || httpError.message;
          httpError.details = detail;
        } else if (error.code === 'ECONNABORTED') {
          httpError.message = 'Request was cancelled';
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

  /**
   * Validate response data if schema is registered
   */
  private validateResponse<T>(endpoint: string, data: unknown): T {
    const schema = this.validationSchemas.get(endpoint);
    if (schema) {
      try {
        return schema.parse(data) as T;
      } catch (error) {
        console.error(`Validation failed for ${endpoint}:`, error);
        // In development, throw the error; in production, log and continue
        if (process.env.NODE_ENV === 'development') {
          throw error;
        }
      }
    }
    return data as T;
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