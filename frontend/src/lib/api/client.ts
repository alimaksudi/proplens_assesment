/**
 * API client for backend communication.
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import {
  CreateConversationResponse,
  ChatRequest,
  ChatResponse,
  ErrorResponse,
  HealthResponse,
} from '@/types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000, // 30 seconds
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<ErrorResponse>) => {
        if (error.response) {
          const errorData = error.response.data;
          console.error('API Error:', errorData);
          throw new Error(errorData?.message || 'An error occurred');
        }
        if (error.request) {
          throw new Error('Network error. Please check your connection.');
        }
        throw error;
      }
    );
  }

  /**
   * Check API health status.
   */
  async healthCheck(): Promise<HealthResponse> {
    const response = await this.client.get<HealthResponse>('/health/');
    return response.data;
  }

  /**
   * Create a new conversation session.
   */
  async createConversation(): Promise<CreateConversationResponse> {
    const response = await this.client.post<CreateConversationResponse>(
      '/conversations/'
    );
    return response.data;
  }

  /**
   * Send a message to the agent.
   */
  async sendMessage(
    conversationId: string,
    message: string
  ): Promise<ChatResponse> {
    const payload: ChatRequest = {
      conversation_id: conversationId,
      message,
    };

    const response = await this.client.post<ChatResponse>(
      '/agents/chat',
      payload
    );
    return response.data;
  }

  /**
   * Get conversation details.
   */
  async getConversation(conversationId: string): Promise<Record<string, unknown>> {
    const response = await this.client.get(`/conversations/${conversationId}`);
    return response.data;
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
