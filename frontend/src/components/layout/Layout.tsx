/**
 * Main layout component.
 */

import { ReactNode } from 'react';
import { Header } from './Header';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="h-screen flex flex-col bg-gray-50 overflow-hidden">
      <Header />
      <main className="flex-1 flex overflow-hidden relative">
        {children}
      </main>
    </div>
  );
}
