/**
 * Home page component.
 */

import { Layout } from '@/components/layout/Layout';
import { ChatInterface } from '@/components/chat/ChatInterface';
import { PropertyMap } from '@/components/map/PropertyMap';
import { useConversation } from '@/hooks/useConversation';

export function Home() {
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
  
  return (
    <Layout>
      <div className="relative w-full h-full flex overflow-hidden">
         {/* Map Background (Base Layer) */}
         <div className="absolute inset-0 z-0">
             <PropertyMap properties={recommendations} />
         </div>

         {/* Floating Chat Panel (Right Side) */}
         <div className="absolute top-4 right-4 bottom-4 w-[480px] z-10 flex flex-col pointer-events-none">
             {/* Chat Interface Container - Enable pointer events for interaction */}
             <div className="w-full h-full rounded-2xl overflow-hidden shadow-2xl pointer-events-auto ring-1 ring-black/5 bg-white/80 backdrop-blur-md">
                <ChatInterface
                    messages={messages}
                    isLoading={isLoading}
                    error={error}
                    isOnline={isOnline}
                    lastFailedMessage={lastFailedMessage}
                    onSendMessage={sendMessage}
                    onRetryLastMessage={retryLastMessage}
                    onClearError={clearError}
                    onNewChat={initializeConversation}
                />
             </div>
         </div>
      </div>
    </Layout>
  );
}
