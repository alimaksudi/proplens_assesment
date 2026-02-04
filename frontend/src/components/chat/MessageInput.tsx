/**
 * Message input component for chat.
 */

import { useState, FormEvent, KeyboardEvent, useRef, useEffect } from 'react';
import { ArrowUp } from 'lucide-react';
import { Button } from '@/components/common/Button';
import { clsx } from 'clsx';

interface MessageInputProps {
  onSend: (message: string) => void;
  isLoading?: boolean;
  disabled?: boolean;
  placeholder?: string;
}

export function MessageInput({
  onSend,
  isLoading = false,
  disabled = false,
  placeholder = 'Type your message...',
}: MessageInputProps) {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-focus on mount
  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  // Re-focus after loading completes (message sent)
  useEffect(() => {
    if (!isLoading && !disabled) {
      textareaRef.current?.focus();
    }
  }, [isLoading, disabled]);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading && !disabled) {
      onSend(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="relative"
    >
      <div className="relative flex items-center group">
        <label htmlFor="chat-input" className="sr-only">
          Type your message
        </label>
        <textarea
          id="chat-input"
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={isLoading || disabled}
          rows={1}
          className="w-full pl-4 pr-12 py-3.5 border border-gray-200 rounded-2xl
                     focus:outline-none focus:ring-2 focus:ring-primary-500/20
                     focus:border-primary-500 resize-none bg-gray-50/50
                     disabled:bg-gray-100 disabled:cursor-not-allowed
                     placeholder-gray-400 text-sm transition-all duration-200
                     shadow-sm hover:border-gray-300"
          style={{ minHeight: '52px', maxHeight: '160px' }}
        />
        
        <div className="absolute right-2 flex items-center h-full">
          <Button
            type="submit"
            disabled={!message.trim() || isLoading || disabled}
            className={clsx(
              "h-8 w-8 !p-0 flex-shrink-0 shadow-sm rounded-lg transition-all active:scale-90",
              message.trim() ? "bg-primary-600 text-white hover:bg-primary-700" : "bg-gray-100 text-gray-400"
            )}
            aria-label="Send message"
          >
            <ArrowUp className={clsx("w-4 h-4", isLoading ? "animate-pulse" : "")} />
          </Button>
        </div>
      </div>
    </form>
  );
}
