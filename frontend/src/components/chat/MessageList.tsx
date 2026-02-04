import { useRef, useEffect } from 'react';
import { Message } from '@/types/conversation';
import { clsx } from 'clsx';

interface MessageListProps {
  messages: Message[];
}

interface MessageBubbleProps {
  message: Message;
}

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const timeString = message.timestamp.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className={clsx("flex flex-col space-y-2 message-enter", isUser ? "items-end" : "items-start")}>
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
            'flex-shrink-0 w-10 h-10 rounded-full overflow-hidden flex items-center justify-center bg-white shadow-md border-2 border-gray-100 transition-transform hover:scale-105'
          )}
        >
          {isUser ? (
            <img 
              src="/assets/user_avatar.png" 
              alt="User" 
              className="w-full h-full object-cover"
              onError={(e) => {
                (e.target as HTMLImageElement).parentElement!.classList.add('bg-primary-50');
                (e.target as HTMLImageElement).src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTIgMTJhNSA1IDAgMSAwLTktOSAwIDUgNSAwIDAgMCAxMCAwek0yMCAyMGE4IDggMCAwIDAtMTYgMCIgZmlsbD0iIzYzNjZmMSIvPjwvc3ZnPg==';
              }}
            />
          ) : (
            <img 
              src="/assets/ai_guide_avatar.png" 
              alt="AI Guide" 
              className="w-full h-full object-cover"
              onError={(e) => {
                (e.target as HTMLImageElement).parentElement!.classList.add('bg-gray-50');
                (e.target as HTMLImageElement).src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTIgMkwyIDIyaDIwTDEyIDJ6IiBmaWxsPSIjREREREREIi8+PC9zdmc+';
              }}
            />
          )}
        </div>
        <div
          className={clsx(
            'px-4 py-3 rounded-2xl shadow-sm transition-all duration-300',
            isUser
              ? 'bg-gradient-to-br from-primary-600 to-primary-700 text-white rounded-tr-md shadow-md shadow-primary-500/10'
              : 'bg-white/90 backdrop-blur-md border border-gray-100 text-gray-800 rounded-tl-md shadow-sm'
          )}
        >
        <div className={clsx(
          "text-sm leading-relaxed prose prose-sm max-w-none prose-p:my-1 prose-ul:my-1",
          isUser ? "prose-invert text-white font-medium" : "text-gray-800"
        )}>
            <ReactMarkdown 
              remarkPlugins={[remarkGfm]}
              components={{
                p: ({children}) => <p className="mb-2 last:mb-0 leading-relaxed">{children}</p>,
                strong: ({children}) => <strong className={clsx("font-bold", isUser ? "text-white underline decoration-white/30" : "text-primary-700")}>{children}</strong>,
                ul: ({children}) => <ul className="list-disc pl-4 mb-2 space-y-1">{children}</ul>,
                li: ({children}) => <li className="text-sm">{children}</li>,
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
      <div className="flex-1 flex items-center justify-center p-8 bg-gray-50/50">
        <div className="text-center">
          <div className="w-24 h-24 mx-auto mb-6 rounded-full overflow-hidden shadow-2xl border-4 border-white">
             <img src="/assets/ai_guide_avatar.png" alt="AI Guide" className="w-full h-full object-cover scale-110" />
          </div>
          <h3 className="text-lg font-semibold text-gray-800 mb-2">Welcome! I'm your AI Guide.</h3>
          <p className="text-sm text-gray-500 max-w-[280px] mx-auto">
            I'm here to help you navigate the world of premium real estate. What are you looking for today?
          </p>
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
