/**
 * Skeleton loading component for placeholder UI.
 */

import { clsx } from 'clsx';

interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular';
}

export function Skeleton({ className, variant = 'rectangular' }: SkeletonProps) {
  return (
    <div
      className={clsx(
        'animate-pulse bg-gray-200',
        variant === 'circular' && 'rounded-full',
        variant === 'text' && 'rounded h-4',
        variant === 'rectangular' && 'rounded-lg',
        className
      )}
      aria-hidden="true"
    />
  );
}

export function PropertyCardSkeleton() {
  return (
    <div className="card" aria-hidden="true">
      {/* Image placeholder */}
      <Skeleton className="h-40 w-full rounded-t-xl rounded-b-none" />

      {/* Content */}
      <div className="p-4 space-y-3">
        {/* Title */}
        <Skeleton className="h-5 w-3/4" variant="text" />

        {/* Location */}
        <Skeleton className="h-4 w-1/2" variant="text" />

        {/* Price */}
        <Skeleton className="h-6 w-1/3" variant="text" />

        {/* Specs */}
        <div className="flex gap-3">
          <Skeleton className="h-4 w-16" variant="text" />
          <Skeleton className="h-4 w-16" variant="text" />
          <Skeleton className="h-4 w-16" variant="text" />
        </div>

        {/* Features */}
        <div className="flex gap-2">
          <Skeleton className="h-5 w-20" variant="text" />
          <Skeleton className="h-5 w-20" variant="text" />
        </div>
      </div>

      {/* Button placeholder */}
      <div className="px-4 pb-4">
        <Skeleton className="h-10 w-full" variant="rectangular" />
      </div>
    </div>
  );
}
