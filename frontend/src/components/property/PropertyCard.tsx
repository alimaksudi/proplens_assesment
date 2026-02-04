/**
 * Property card component for displaying individual properties.
 */

import { Property } from '@/types/property';
import {
  formatPrice,
  formatBedrooms,
  formatBathrooms,
  formatArea,
  formatStatus,
  formatMatchScore,
} from '@/lib/utils/formatters';
import { MapPin, Bed, Bath, Square, Calendar, CheckCircle } from 'lucide-react';
import { clsx } from 'clsx';

interface PropertyCardProps {
  property: Property;
  onSelect?: (property: Property) => void;
  isSelected?: boolean;
}

export function PropertyCard({
  property,
  onSelect,
  isSelected = false,
}: PropertyCardProps) {
  const handleClick = () => {
    if (onSelect) {
      onSelect(property);
    }
  };

  return (
    <div
      className={clsx(
        'card cursor-pointer transition-all duration-200',
        isSelected && 'ring-2 ring-primary-500',
        onSelect && 'hover:shadow-lg'
      )}
      onClick={handleClick}
      role={onSelect ? 'button' : undefined}
      tabIndex={onSelect ? 0 : undefined}
    >
      {/* Image Placeholder */}
      <div className="relative h-40 bg-gradient-to-br from-gray-200 to-gray-300">
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-gray-400 text-sm">No image available</span>
        </div>

        {/* Match Score Badge */}
        {property.match_score !== undefined && property.match_score !== null && (
          <div className="absolute top-2 right-2 bg-green-500 text-white text-xs font-medium px-2 py-1 rounded-full">
            {formatMatchScore(property.match_score)}
          </div>
        )}

        {/* Status Badge */}
        {property.completion_status && (
          <div className="absolute top-2 left-2 bg-white/90 text-gray-700 text-xs font-medium px-2 py-1 rounded-full flex items-center">
            <Calendar className="w-3 h-3 mr-1" />
            {formatStatus(property.completion_status)}
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Title */}
        <h3 className="font-semibold text-gray-900 text-base mb-1 line-clamp-1">
          {property.project_name}
        </h3>

        {/* Location */}
        <div className="flex items-center text-gray-500 text-sm mb-3">
          <MapPin className="w-4 h-4 mr-1 flex-shrink-0" />
          <span className="line-clamp-1">
            {property.city}, {property.country}
          </span>
        </div>

        {/* Price */}
        <div className="text-xl font-bold text-primary-600 mb-3">
          {formatPrice(property.price_usd)}
        </div>

        {/* Specs */}
        <div className="flex flex-wrap gap-3 text-sm text-gray-600 mb-3">
          {property.bedrooms !== undefined && property.bedrooms !== null && (
            <div className="flex items-center">
              <Bed className="w-4 h-4 mr-1" />
              {formatBedrooms(property.bedrooms)}
            </div>
          )}
          {property.bathrooms !== undefined && property.bathrooms !== null && (
            <div className="flex items-center">
              <Bath className="w-4 h-4 mr-1" />
              {formatBathrooms(property.bathrooms)}
            </div>
          )}
          {property.area_sqm !== undefined && property.area_sqm !== null && (
            <div className="flex items-center">
              <Square className="w-4 h-4 mr-1" />
              {formatArea(property.area_sqm)}
            </div>
          )}
        </div>

        {/* Features */}
        {property.key_features && property.key_features.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {property.key_features.slice(0, 3).map((feature, index) => (
              <span
                key={index}
                className="inline-flex items-center text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded"
              >
                <CheckCircle className="w-3 h-3 mr-1" />
                {feature}
              </span>
            ))}
            {property.key_features.length > 3 && (
              <span className="text-xs text-gray-400">
                +{property.key_features.length - 3} more
              </span>
            )}
          </div>
        )}
      </div>

      {/* Action Button */}
      {onSelect && (
        <div className="px-4 pb-4">
          <button
            className="w-full py-2 text-sm font-medium text-primary-600 bg-primary-50 rounded-lg hover:bg-primary-100 transition-colors"
            onClick={(e) => {
              e.stopPropagation();
              onSelect(property);
            }}
          >
            View Details
          </button>
        </div>
      )}
    </div>
  );
}
