/**
 * Main chat interface component.
 */

import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { TypingIndicator } from './TypingIndicator';
import { AlertCircle, Plus, WifiOff } from 'lucide-react';
import { Message } from '@/types/conversation';

export interface ChatInterfaceProps {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  isOnline: boolean;
  lastFailedMessage: string | null;
  onSendMessage: (content: string) => Promise<void>;
  onRetryLastMessage: () => Promise<void>;
  onClearError: () => void;
  onNewChat: () => void;
}

export function ChatInterface({
  messages,
  isLoading,
  error,
  isOnline,
  lastFailedMessage,
  onSendMessage,
  onRetryLastMessage,
  onClearError,
  onNewChat,
}: ChatInterfaceProps) {

  return (
    <div className="flex flex-col w-full h-full bg-white/95 backdrop-blur-md shadow-xl border-r border-gray-200">
        {/* Connection Status Banner (if offline) */}
        {!isOnline && (
          <div className="bg-yellow-50 border-b border-yellow-200 px-4 py-2 text-center">
             <div className="inline-flex items-center space-x-2">
               <WifiOff className="w-4 h-4 text-yellow-600" />
               <span className="text-sm text-yellow-700">Offline mode</span>
             </div>
          </div>
        )}

        {/* Header Actions */}
        <div className="p-4 border-b border-gray-100 flex justify-between items-center bg-white/40 backdrop-blur-md z-10 sticky top-0">
           <div className="flex flex-col">
              <h2 className="text-sm font-bold text-gray-900 tracking-tight">Property Assistant</h2>
           </div>
           <button
            onClick={onNewChat}
            className="group flex items-center justify-center w-9 h-9 rounded-full bg-primary-600 text-white hover:bg-primary-700 transition-all shadow-md active:scale-95"
            title="Start New Conversation"
          >
            <Plus className="w-5 h-5 transition-transform group-hover:rotate-90" />
          </button>
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
                <button onClick={onRetryLastMessage} className="text-red-600 hover:text-red-800 text-sm font-medium underline">
                    Retry
                </button>
                )}
                <button onClick={onClearError} className="text-red-500 hover:text-red-700 ml-2">Dismiss</button>
            </div>
            </div>
        </div>
        )}

        {/* Messages List Area */}
        <div className="flex-1 overflow-hidden flex flex-col">
            <MessageList messages={messages} />
        </div>

        {/* Typing Indicator */}
        {isLoading && (
            <div className="px-4 py-2">
            <TypingIndicator />
            </div>
        )}
        
        {/* Input Area */}
        <div className="p-4 border-t border-gray-100 bg-white">
            <MessageInput
            onSend={onSendMessage}
            isLoading={isLoading}
            disabled={!isOnline}
            placeholder="Ask about properties..."
            />
            <div className="mt-2 text-center">
                    <p className="text-[10px] text-gray-400">
                        AI can make mistakes. Verify details.
                    </p>
            </div>
        </div>
    </div>
  );
}
