/**
 * Message input component for chat.
 */

import { useState, FormEvent, KeyboardEvent, useRef, useEffect } from 'react';
import { Send } from 'lucide-react';
import { Button } from '@/components/common/Button';

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
      className="flex items-end space-x-2 p-4 bg-white border-t border-gray-200"
    >
      <div className="flex-1">
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
          className="w-full px-4 py-3 border border-gray-300 rounded-lg
                     focus:outline-none focus:ring-2 focus:ring-primary-500
                     focus:border-transparent resize-none
                     disabled:bg-gray-100 disabled:cursor-not-allowed
                     placeholder-gray-400"
          style={{ minHeight: '48px', maxHeight: '120px' }}
        />
      </div>
      <Button
        type="submit"
        disabled={!message.trim() || isLoading || disabled}
        isLoading={isLoading}
        className="h-12 w-12 !p-0 flex-shrink-0"
        aria-label="Send message"
      >
        <Send className="w-5 h-5" />
      </Button>
    </form>
  );
}
