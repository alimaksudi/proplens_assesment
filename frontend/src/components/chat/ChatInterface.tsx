/**
 * Main chat interface component.
 */

import { useConversation } from '@/hooks/useConversation';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { TypingIndicator } from './TypingIndicator';
import { PropertyList } from '@/components/property/PropertyList';
import { Skeleton, PropertyCardSkeleton } from '@/components/common/Skeleton';
import { AlertCircle, RefreshCw, WifiOff } from 'lucide-react';
import { Button } from '@/components/common/Button';

export function ChatInterface() {
  const {
    messages,
    recommendations,
    isLoading,
    error,
    isOnline,
    lastFailedMessage,
    sendMessage,
    retryLastMessage,
    clearError,
    initializeConversation,
  } = useConversation();

  const handleNewChat = () => {
    initializeConversation();
  };

  return (
    <div className="flex-1 flex">
      {/* Chat Section */}
      <div className="flex-1 flex flex-col max-w-3xl mx-auto w-full">
        {/* Offline Banner */}
        {!isOnline && (
          <div className="bg-yellow-50 border-b border-yellow-200 px-4 py-3">
            <div className="flex items-center space-x-2">
              <WifiOff className="w-5 h-5 text-yellow-600" />
              <span className="text-sm text-yellow-700">
                You're offline. Messages will be sent when you reconnect.
              </span>
            </div>
          </div>
        )}

        {/* Error Banner */}
        {error && (
          <div className="bg-red-50 border-b border-red-200 px-4 py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <AlertCircle className="w-5 h-5 text-red-500" />
                <span className="text-sm text-red-700">{error}</span>
              </div>
              <div className="flex items-center space-x-2">
                {lastFailedMessage && (
                  <button
                    onClick={retryLastMessage}
                    className="text-red-600 hover:text-red-800 text-sm font-medium"
                  >
                    Retry
                  </button>
                )}
                <button
                  onClick={clearError}
                  className="text-red-500 hover:text-red-700"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Messages */}
        <MessageList messages={messages} />

        {/* Typing Indicator */}
        {isLoading && <TypingIndicator />}

        {/* Input */}
        <MessageInput
          onSend={sendMessage}
          isLoading={isLoading}
          disabled={!isOnline}
          placeholder="Tell me what kind of property you're looking for..."
        />

        {/* New Chat Button */}
        <div className="p-2 bg-white border-t border-gray-100 text-center">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleNewChat}
            className="text-gray-500"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Start New Chat
          </Button>
        </div>
      </div>

      {/* Property Recommendations Sidebar */}
      <div className="hidden lg:block w-96 border-l border-gray-200 bg-white overflow-y-auto">
        {isLoading && recommendations.length === 0 ? (
          // Skeleton loading state
          <div className="p-4 space-y-4">
            <Skeleton className="h-6 w-48" variant="text" />
            <Skeleton className="h-4 w-32" variant="text" />
            <PropertyCardSkeleton />
            <PropertyCardSkeleton />
          </div>
        ) : recommendations.length > 0 ? (
          // Actual recommendations
          <>
            <div className="p-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">
                Recommended Properties
              </h2>
              <p className="text-sm text-gray-500">
                {recommendations.length} properties match your criteria
              </p>
            </div>
            <PropertyList properties={recommendations} />
          </>
        ) : (
          // Empty state
          <div className="p-8 text-center text-gray-400">
            <p className="text-sm">
              Property recommendations will appear here once you share your preferences.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
