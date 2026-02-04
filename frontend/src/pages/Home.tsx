/**
 * Home page component.
 */

import { Layout } from '@/components/layout/Layout';
import { ChatInterface } from '@/components/chat/ChatInterface';

export function Home() {
  return (
    <Layout>
      <ChatInterface />
    </Layout>
  );
}
