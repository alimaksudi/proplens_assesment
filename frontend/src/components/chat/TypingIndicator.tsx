/**
 * Typing indicator component.
 */

export function TypingIndicator() {
  return (
    <div className="flex items-center space-x-1 px-4 py-3">
      <div className="flex items-center space-x-1">
        <div className="w-2 h-2 bg-gray-400 rounded-full typing-dot" />
        <div className="w-2 h-2 bg-gray-400 rounded-full typing-dot" />
        <div className="w-2 h-2 bg-gray-400 rounded-full typing-dot" />
      </div>
      <span className="text-sm text-gray-500 ml-2">
        Agent is typing...
      </span>
    </div>
  );
}
