/**
 * Main chat interface component.
 */

import { useConversation } from '@/hooks/useConversation';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { TypingIndicator } from './TypingIndicator';
import { AlertCircle, RefreshCw, WifiOff } from 'lucide-react';
import { Button } from '@/components/common/Button';

export function ChatInterface() {
  const {
    messages,
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
    <div className="flex-1 flex bg-gray-50">
      {/* Chat Section */}
      <div className="flex-1 flex flex-col w-full h-full relative">
        {/* Connection Status Banner (if offline) */}
        {!isOnline && (
          <div className="absolute top-0 left-0 right-0 z-50 bg-yellow-50 border-b border-yellow-200 px-4 py-2 text-center">
             <div className="inline-flex items-center space-x-2">
               <WifiOff className="w-4 h-4 text-yellow-600" />
               <span className="text-sm text-yellow-700">You're offline. Messages will be sent when you reconnect.</span>
             </div>
          </div>
        )}

        {/* Messages Area - Centered and Full Height */}
        <div className="flex-1 overflow-hidden flex flex-col">
            <div className="flex-1 w-full max-w-4xl mx-auto flex flex-col bg-white shadow-sm border-x border-gray-100 h-full">
                
                {/* Header Actions */}
                <div className="p-3 border-b border-gray-100 flex justify-end bg-white/80 backdrop-blur-sm z-10 sticky top-0">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleNewChat}
                    className="text-gray-500 hover:text-primary-600"
                  >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    New Chat
                  </Button>
                </div>

                {/* Error Banner */}
                {error && (
                <div className="bg-red-50 border-b border-red-200 px-4 py-3 mx-4 mt-2 rounded-md">
                    <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        <AlertCircle className="w-5 h-5 text-red-500" />
                        <span className="text-sm text-red-700">{error}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                        {lastFailedMessage && (
                        <button onClick={retryLastMessage} className="text-red-600 hover:text-red-800 text-sm font-medium underline">
                            Retry
                        </button>
                        )}
                        <button onClick={clearError} className="text-red-500 hover:text-red-700 ml-2">Dismiss</button>
                    </div>
                    </div>
                </div>
                )}

                {/* Messages List */}
                <MessageList messages={messages} />

                {/* Typing Indicator */}
                {isLoading && (
                  <div className="px-4 py-2">
                    <TypingIndicator />
                  </div>
                )}
                
                {/* Input Area */}
                <div className="p-4 border-t border-gray-100 bg-white">
                    <MessageInput
                    onSend={sendMessage}
                    isLoading={isLoading}
                    disabled={!isOnline}
                    placeholder="Ask about properties in Dubai, or specific locations..."
                    />
                    <div className="mt-2 text-center">
                         <p className="text-xs text-gray-400">
                             AI can make mistakes. Please verify important details.
                         </p>
                    </div>
                </div>
            </div>
        </div>
      </div>
    </div>
  );
}
