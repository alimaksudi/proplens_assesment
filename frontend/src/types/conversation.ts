/**
 * Conversation-related type definitions.
 */

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

export interface Preferences {
  city?: string;
  country?: string;
  bedrooms?: number;
  bathrooms?: number;
  budget_min?: number;
  budget_max?: number;
  property_type?: string;
  completion_status?: string;
  features?: string[];
}

export interface ConversationState {
  conversationId: string;
  messages: Message[];
  preferences: Preferences;
  isLoading: boolean;
  error: string | null;
}
