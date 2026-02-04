/**
 * Property details component for full property view.
 */

import { Property } from '@/types/property';
import {
  formatPrice,
  formatStatus,
} from '../../lib/utils/formatters';
import {
  MapPin,
  Bed,
  Bath,
  Square,
  Calendar,
  CheckCircle,
  X,
  Building,
} from 'lucide-react';
import { Button } from '@/components/common/Button';

interface PropertyDetailsProps {
  property: Property;
  onClose: () => void;
  onBookViewing?: () => void;
}

export function PropertyDetails({
  property,
  onClose,
  onBookViewing,
}: PropertyDetailsProps) {
  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 transition-opacity"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative min-h-screen flex items-center justify-center p-4">
        <div className="relative bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          {/* Close Button */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 z-10 p-2 bg-white/90 rounded-full hover:bg-gray-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>

          {/* Image */}
          <div className="h-64 bg-gradient-to-br from-gray-200 to-gray-300 flex items-center justify-center">
            <Building className="w-16 h-16 text-gray-400" />
          </div>

          {/* Content */}
          <div className="p-6">
            {/* Header */}
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                {property.project_name}
              </h2>
              <div className="flex items-center text-gray-600">
                <MapPin className="w-5 h-5 mr-2" />
                {property.city}, {property.country}
              </div>
            </div>

            {/* Price */}
            <div className="text-3xl font-bold text-primary-600 mb-6">
              {formatPrice(property.price_usd)}
            </div>

            {/* Specs Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              {property.bedrooms !== undefined && (
                <div className="bg-gray-50 rounded-lg p-3 text-center">
                  <Bed className="w-5 h-5 mx-auto mb-1 text-gray-600" />
                  <div className="font-semibold">{property.bedrooms}</div>
                  <div className="text-xs text-gray-500">Bedrooms</div>
                </div>
              )}
              {property.bathrooms !== undefined && (
                <div className="bg-gray-50 rounded-lg p-3 text-center">
                  <Bath className="w-5 h-5 mx-auto mb-1 text-gray-600" />
                  <div className="font-semibold">{property.bathrooms}</div>
                  <div className="text-xs text-gray-500">Bathrooms</div>
                </div>
              )}
              {property.area_sqm !== undefined && (
                <div className="bg-gray-50 rounded-lg p-3 text-center">
                  <Square className="w-5 h-5 mx-auto mb-1 text-gray-600" />
                  <div className="font-semibold">{property.area_sqm}</div>
                  <div className="text-xs text-gray-500">Sq Meters</div>
                </div>
              )}
              {property.completion_status && (
                <div className="bg-gray-50 rounded-lg p-3 text-center">
                  <Calendar className="w-5 h-5 mx-auto mb-1 text-gray-600" />
                  <div className="font-semibold text-sm">
                    {formatStatus(property.completion_status)}
                  </div>
                  <div className="text-xs text-gray-500">Status</div>
                </div>
              )}
            </div>

            {/* Description */}
            {property.description && (
              <div className="mb-6">
                <h3 className="font-semibold text-gray-900 mb-2">Description</h3>
                <p className="text-gray-600 text-sm leading-relaxed">
                  {property.description}
                </p>
              </div>
            )}

            {/* Features */}
            {property.key_features && property.key_features.length > 0 && (
              <div className="mb-6">
                <h3 className="font-semibold text-gray-900 mb-2">
                  Features & Amenities
                </h3>
                <div className="flex flex-wrap gap-2">
                  {property.key_features.map((feature, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center text-sm bg-primary-50 text-primary-700 px-3 py-1 rounded-full"
                    >
                      <CheckCircle className="w-4 h-4 mr-1" />
                      {feature}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex space-x-3 pt-4 border-t border-gray-200">
              <Button
                variant="primary"
                className="flex-1"
                onClick={onBookViewing}
              >
                Book a Viewing
              </Button>
              <Button variant="secondary" onClick={onClose}>
                Close
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
