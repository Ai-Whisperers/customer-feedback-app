/**
 * Zod Validation Schemas for API Responses
 * Runtime validation to ensure type safety
 */

import { z } from 'zod';

// File info schema
export const FileInfoSchema = z.object({
  name: z.string(),
  rows: z.number().int().nonnegative(),
  size_mb: z.number().nonnegative(),
  columns_found: z.array(z.string()),
  has_nps_column: z.boolean()
});

// Upload response schema
export const UploadResponseSchema = z.object({
  success: z.boolean(),
  message: z.string().optional(),
  task_id: z.string(),
  estimated_time_seconds: z.number().int().nonnegative(),
  file_info: FileInfoSchema
});

// Backend task status enum
export const BackendTaskStatusSchema = z.enum(['queued', 'processing', 'completed', 'failed', 'expired']);

// Status response schema
export const StatusResponseSchema = z.object({
  task_id: z.string(),
  status: BackendTaskStatusSchema,
  progress: z.number().min(0).max(100),
  current_step: z.string().optional(),
  estimated_remaining_seconds: z.number().int().nonnegative().optional(),
  started_at: z.string().optional(),
  completed_at: z.string().optional(),
  duration_seconds: z.number().nonnegative().optional(),
  messages: z.array(z.string()).default([]),
  results_available: z.boolean().default(false),
  error: z.string().optional(),
  details: z.string().optional(),
  failed_at: z.string().optional(),
  retry_available: z.boolean().default(false)
});

// Analysis results schemas
export const NPSMetricsSchema = z.object({
  score: z.number(),
  promoters: z.number().int().nonnegative(),
  promoters_percentage: z.number().min(0).max(100),
  passives: z.number().int().nonnegative(),
  passives_percentage: z.number().min(0).max(100),
  detractors: z.number().int().nonnegative(),
  detractors_percentage: z.number().min(0).max(100)
});

export const ChurnRiskSchema = z.object({
  average: z.number().min(0).max(1),
  high_risk_count: z.number().int().nonnegative(),
  high_risk_percentage: z.number().min(0).max(100),
  distribution: z.record(z.string(), z.number())
});

export const PainPointSchema = z.object({
  category: z.string(),
  count: z.number().int().nonnegative(),
  percentage: z.number().min(0).max(100),
  examples: z.array(z.string())
});

export const AnalysisResultsSchema = z.object({
  summary: z.object({
    nps: NPSMetricsSchema,
    churn_risk: ChurnRiskSchema,
    pain_points: z.array(PainPointSchema)
  }),
  rows: z.array(z.object({
    index: z.number(),
    original_text: z.string(),
    nota: z.number(),
    nps_category: z.string(),
    sentiment: z.string(),
    language: z.string(),
    churn_risk: z.number(),
    pain_points: z.array(z.string()),
    emotions: z.record(z.string(), z.number())
  })).optional(),
  metadata: z.object({
    total_comments: z.number(),
    processing_time_seconds: z.number(),
    model_used: z.string(),
    timestamp: z.string(),
    batches_processed: z.number()
  })
});

// Error response schema
export const ErrorResponseSchema = z.object({
  error: z.string(),
  details: z.string().optional(),
  code: z.string().optional(),
  suggestions: z.array(z.string()).optional()
});

// Type exports from schemas
export type FileInfo = z.infer<typeof FileInfoSchema>;
export type UploadResponseValidated = z.infer<typeof UploadResponseSchema>;
export type StatusResponseValidated = z.infer<typeof StatusResponseSchema>;
export type AnalysisResultsValidated = z.infer<typeof AnalysisResultsSchema>;
export type ErrorResponse = z.infer<typeof ErrorResponseSchema>;