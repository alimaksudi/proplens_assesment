/**
 * Application header component.
 */

import { Building2 } from 'lucide-react';

export function Header() {
  return (
    <header className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-10 h-10 bg-primary-100 rounded-lg">
              <Building2 className="w-6 h-6 text-primary-600" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-gray-900">
                Silver Land Properties
              </h1>
              <p className="text-xs text-gray-500">
                Find your perfect property
              </p>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
