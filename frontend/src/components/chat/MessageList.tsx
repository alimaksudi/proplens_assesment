/**
 * Message list component for displaying conversation history.
 */

import { useRef, useEffect } from 'react';
import { Message } from '@/types/conversation';
import { clsx } from 'clsx';
import { User, Bot } from 'lucide-react';

interface MessageListProps {
  messages: Message[];
}

interface MessageBubbleProps {
  message: Message;
}

function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const timeString = message.timestamp.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <article
      className={clsx(
        'flex items-start space-x-3 message-enter',
        isUser && 'flex-row-reverse space-x-reverse'
      )}
      role="article"
      aria-label={`${isUser ? 'Your message' : 'Agent message'} at ${timeString}`}
    >
      <div
        className={clsx(
          'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center',
          isUser ? 'bg-primary-100' : 'bg-gray-100'
        )}
      >
        {isUser ? (
          <User className="w-4 h-4 text-primary-600" />
        ) : (
          <Bot className="w-4 h-4 text-gray-600" />
        )}
      </div>
      <div
        className={clsx(
          'max-w-[75%] px-4 py-3 rounded-2xl',
          isUser
            ? 'bg-primary-600 text-white rounded-tr-md'
            : 'bg-white border border-gray-200 text-gray-800 rounded-tl-md'
        )}
      >
        <p className="text-sm whitespace-pre-wrap leading-relaxed">
          {message.content}
        </p>
        <span
          className={clsx(
            'text-xs mt-1 block',
            isUser ? 'text-primary-200' : 'text-gray-400'
          )}
        >
          {timeString}
        </span>
      </div>
    </article>
  );
}

export function MessageList({ messages }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center text-gray-500">
          <Bot className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p>Start a conversation to find your perfect property</p>
        </div>
      </div>
    );
  }

  // TODO: For 50+ messages, consider react-window virtualization
  // import { VariableSizeList } from 'react-window';

  return (
    <div
      className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50"
      role="log"
      aria-label="Chat messages"
      aria-live="polite"
    >
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
}
