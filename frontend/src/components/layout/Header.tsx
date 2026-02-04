/**
 * Application header component.
 */

export function Header() {
  return (
    <header className="bg-white/80 backdrop-blur-md border-b border-gray-100 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-10 h-10 bg-primary-600 rounded-xl shadow-md shadow-primary-200 overflow-hidden group hover:scale-110 transition-transform ring-4 ring-white">
              <img 
                src="/assets/brand_logo.png" 
                alt="Silver Land Properties Logo" 
                className="w-full h-full object-contain p-1.5 brightness-0 invert"
              />
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
