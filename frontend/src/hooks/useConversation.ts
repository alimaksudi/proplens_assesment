/**
 * Custom hook for managing conversation state.
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { apiClient } from '@/lib/api/client';
import { Message, Preferences } from '@/types/conversation';
import { Property } from '@/types/property';

const STORAGE_KEY = 'silverland_conversation';

interface StoredConversation {
  conversationId: string;
  messages: Array<{ id: string; role: string; content: string; timestamp: string }>;
  preferences: Preferences;
  recommendations: Property[];
}

interface UseConversationReturn {
  conversationId: string | null;
  messages: Message[];
  preferences: Preferences;
  recommendations: Property[];
  isLoading: boolean;
  error: string | null;
  isOnline: boolean;
  lastFailedMessage: string | null;
  initializeConversation: () => Promise<void>;
  sendMessage: (content: string) => Promise<void>;
  retryLastMessage: () => Promise<void>;
  clearError: () => void;
}

export function useConversation(): UseConversationReturn {
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [preferences, setPreferences] = useState<Preferences>({});
  const [recommendations, setRecommendations] = useState<Property[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isOnline, setIsOnline] = useState(typeof navigator !== 'undefined' ? navigator.onLine : true);
  const [lastFailedMessage, setLastFailedMessage] = useState<string | null>(null);
  const isInitialized = useRef(false);

  const generateMessageId = () => {
    return `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  };

  // Online/offline detection
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const initializeConversation = useCallback(async () => {
    // Clear storage on new conversation
    sessionStorage.removeItem(STORAGE_KEY);
    setLastFailedMessage(null);
    setRecommendations([]);
    setPreferences({});

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
        setLastFailedMessage(null); // Clear on success

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
        setLastFailedMessage(content); // Store failed message for retry

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

  const retryLastMessage = useCallback(async () => {
    if (lastFailedMessage) {
      // Remove the error assistant message
      setMessages((prev) => prev.slice(0, -1));
      setError(null);
      await sendMessage(lastFailedMessage);
    }
  }, [lastFailedMessage, sendMessage]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Load from storage or initialize on mount
  useEffect(() => {
    if (isInitialized.current) return;
    isInitialized.current = true;

    const stored = sessionStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        const data: StoredConversation = JSON.parse(stored);
        setConversationId(data.conversationId);
        setMessages(
          data.messages.map((m) => ({
            ...m,
            role: m.role as 'user' | 'assistant' | 'system',
            timestamp: new Date(m.timestamp),
          }))
        );
        setPreferences(data.preferences);
        setRecommendations(data.recommendations);
      } catch {
        initializeConversation();
      }
    } else {
      initializeConversation();
    }
  }, [initializeConversation]);

  // Save to storage on changes
  useEffect(() => {
    if (conversationId && messages.length > 0) {
      const data: StoredConversation = {
        conversationId,
        messages: messages.map((m) => ({
          id: m.id,
          role: m.role,
          content: m.content,
          timestamp: m.timestamp.toISOString(),
        })),
        preferences,
        recommendations,
      };
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    }
  }, [conversationId, messages, preferences, recommendations]);

  return {
    conversationId,
    messages,
    preferences,
    recommendations,
    isLoading,
    error,
    isOnline,
    lastFailedMessage,
    initializeConversation,
    sendMessage,
    retryLastMessage,
    clearError,
  };
}
