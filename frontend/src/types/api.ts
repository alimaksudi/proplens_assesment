/**
 * API request and response type definitions.
 */

import { Property } from './property';
import { Preferences } from './conversation';

export interface CreateConversationResponse {
  conversation_id: string;
  created_at: string;
}

export interface ChatRequest {
  conversation_id: string;
  message: string;
}

export interface StructuredData {
  preferences_captured?: Preferences;
  next_questions?: string[];
  booking?: {
    booking_id?: number;
    status?: string;
  };
}

export interface ResponseContent {
  message: string;
  intent?: string;
  structured_data?: StructuredData;
  state: string;
}

export interface Metadata {
  processing_time_ms: number;
  tools_used: string[];
}

export interface ChatResponse {
  conversation_id: string;
  response: ResponseContent;
  recommendations: Property[];
  metadata: Metadata;
}

export interface ErrorResponse {
  error: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface HealthResponse {
  status: string;
  database: string;
  version: string;
  project_count: number;
}
