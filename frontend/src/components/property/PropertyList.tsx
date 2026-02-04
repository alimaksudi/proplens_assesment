/**
 * Property list component for displaying multiple properties.
 */

import { Property } from '@/types/property';
import { PropertyCard } from './PropertyCard';

interface PropertyListProps {
  properties: Property[];
  onSelect?: (property: Property) => void;
  selectedId?: number;
}

export function PropertyList({
  properties,
  onSelect,
  selectedId,
}: PropertyListProps) {
  if (properties.length === 0) {
    return (
      <div className="p-8 text-center text-gray-500">
        <p>No properties to display</p>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-4">
      {properties.map((property) => (
        <PropertyCard
          key={property.id}
          property={property}
          onSelect={onSelect}
          isSelected={selectedId === property.id}
        />
      ))}
    </div>
  );
}
