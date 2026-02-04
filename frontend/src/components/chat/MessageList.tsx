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

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import { PropertyCard } from '@/components/property/PropertyCard';
import { Property } from '@/types/property';

function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const timeString = message.timestamp.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className={clsx("flex flex-col space-y-2 message-enter", isUser ? "items-end" : "items-start")}>
      {/* Property Recommendations in Chat - Displayed BEFORE the message */}
      {!isUser && message.properties && message.properties.length > 0 && (
        <div className="pl-11 w-full max-w-2xl grid grid-cols-1 md:grid-cols-2 gap-3 mb-2">
            {message.properties.map((prop: Property) => (
                <div key={prop.id} className="transform scale-90 origin-top-left md:scale-100">
                    <PropertyCard property={prop} />
                </div>
            ))}
        </div>
      )}

      <article
        className={clsx(
          'flex items-start space-x-3 max-w-[85%]',
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
            'px-4 py-3 rounded-2xl shadow-sm',
            isUser
              ? 'bg-primary-600 text-white rounded-tr-md'
              : 'bg-white border border-gray-200 text-gray-800 rounded-tl-md'
          )}
        >
        <div className={clsx(
          "text-sm leading-relaxed prose prose-sm max-w-none prose-p:my-1 prose-ul:my-1",
          isUser ? "prose-invert text-white" : "text-gray-800"
        )}>
            <ReactMarkdown 
              remarkPlugins={[remarkGfm]}
              components={{
                p: ({children}) => <p className="mb-2 last:mb-0">{children}</p>,
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
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

    </div>
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
