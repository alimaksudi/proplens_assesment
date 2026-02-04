/**
 * Custom hook for managing conversation state.
 */

import { useState, useCallback, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import { Message, Preferences } from '@/types/conversation';
import { Property } from '@/types/property';

interface UseConversationReturn {
  conversationId: string | null;
  messages: Message[];
  preferences: Preferences;
  recommendations: Property[];
  isLoading: boolean;
  error: string | null;
  initializeConversation: () => Promise<void>;
  sendMessage: (content: string) => Promise<void>;
  clearError: () => void;
}

export function useConversation(): UseConversationReturn {
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [preferences, setPreferences] = useState<Preferences>({});
  const [recommendations, setRecommendations] = useState<Property[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateMessageId = () => {
    return `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  };

  const initializeConversation = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await apiClient.createConversation();
      setConversationId(response.conversation_id);

      // Add initial greeting message
      setMessages([
        {
          id: generateMessageId(),
          role: 'assistant',
          content:
            'Welcome to Silver Land Properties. I\'m here to help you find your perfect property. What are you looking for today?',
          timestamp: new Date(),
        },
      ]);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Failed to start conversation';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!conversationId || !content.trim()) {
        return;
      }

      // Add user message
      const userMessage: Message = {
        id: generateMessageId(),
        role: 'user',
        content: content.trim(),
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);
      setError(null);

      try {
        const response = await apiClient.sendMessage(conversationId, content);

        // Add assistant message
        const assistantMessage: Message = {
          id: generateMessageId(),
          role: 'assistant',
          content: response.response.message,
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, assistantMessage]);

        // Update preferences if captured
        if (response.response.structured_data?.preferences_captured) {
          setPreferences((prev) => ({
            ...prev,
            ...response.response.structured_data?.preferences_captured,
          }));
        }

        // Update recommendations
        if (response.recommendations && response.recommendations.length > 0) {
          setRecommendations(response.recommendations);
        }
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : 'Failed to send message';
        setError(errorMessage);

        // Add error message
        setMessages((prev) => [
          ...prev,
          {
            id: generateMessageId(),
            role: 'assistant',
            content:
              'I apologize, but I encountered an issue. Please try again.',
            timestamp: new Date(),
          },
        ]);
      } finally {
        setIsLoading(false);
      }
    },
    [conversationId]
  );

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Initialize conversation on mount
  useEffect(() => {
    initializeConversation();
  }, [initializeConversation]);

  return {
    conversationId,
    messages,
    preferences,
    recommendations,
    isLoading,
    error,
    initializeConversation,
    sendMessage,
    clearError,
  };
}
