import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import { Property } from '@/types/property';
import { divIcon, LatLngBoundsExpression } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useEffect, useMemo } from 'react';
import { PropertyCard } from '@/components/property/PropertyCard';

// City center coordinates for smart fallback
const CITY_CENTERS: Record<string, [number, number]> = {
    'dubai': [25.2048, 55.2708],
    'bangkok': [13.7563, 100.5018],
    'london': [51.5074, -0.1278],
    'new york': [40.7128, -74.0060],
    'singapore': [1.3521, 103.8198],
    'bali': [-8.4095, 115.1889],
};

// Helper to create custom numbered icons
const createNumberedIcon = (number: number) => {
    return divIcon({
        className: 'custom-numbered-marker',
        html: `<div class="marker-pin"><span class="marker-content">${number}</span></div>`,
        iconSize: [30, 42],
        iconAnchor: [15, 42],
        popupAnchor: [0, -40]
    });
};

// Helper to generate mock nearby coordinates around a center
const getMockCoordinates = (index: number, locationString?: string) => {
    let baseCoords: [number, number] = CITY_CENTERS['dubai']; // Global default
    
    if (locationString) {
        const lowerLoc = locationString.toLowerCase();
        for (const [city, coords] of Object.entries(CITY_CENTERS)) {
            if (lowerLoc.includes(city)) {
                baseCoords = coords;
                break;
            }
        }
    }
    
    // Deterministic scatter based on index to keep markers near the city center but separate
    const lat = baseCoords[0] + (Math.sin(index) * 0.02);
    const lng = baseCoords[1] + (Math.cos(index) * 0.02);
    
    return [lat, lng] as [number, number];
};

interface PropertyMapProps {
    properties: Property[];
    className?: string;
}

function MapUpdater({ properties }: { properties: Property[] }) {
    const map = useMap();

    useEffect(() => {
        if (properties.length > 0) {
            // Calculate bounds based on real or smart-mocked coordinates
            const points: [number, number][] = properties.map((p, i) => {
                return p.latitude && p.longitude 
                    ? [p.latitude, p.longitude] 
                    : getMockCoordinates(i, p.city);
            });
            
            if (points.length > 0) {
                // Animate the shift to new location
                map.fitBounds(points as LatLngBoundsExpression, { 
                    paddingBottomRight: [540, 100], // Offset for the 480px right-side chat panel
                    paddingTopLeft: [60, 100],
                    maxZoom: 14,
                    animate: true,
                    duration: 1.5
                });
            }
        }
    }, [properties, map]);

    return null;
}

export function PropertyMap({ properties, className }: PropertyMapProps) {
    // Memoize markers to prevent flickering
    const mapMarkers = useMemo(() => {
        return properties.map((property, index) => {
            const hasLocation = property.latitude && property.longitude;
            const position = hasLocation 
                ? [property.latitude!, property.longitude!] as [number, number]
                : getMockCoordinates(index, property.city);
            
            return {
                ...property,
                index: index + 1,
                position
            };
        });
    }, [properties]);

    return (
        <div className={`w-full h-full relative z-0 ${className || ''}`}>
            <MapContainer
                center={[25.2048, 55.2708]} // Initial default view (Dubai)
                zoom={12}
                style={{ width: '100%', height: '100%' }}
                zoomControl={false}
            >
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                
                {mapMarkers.map((property) => (
                    <Marker 
                        key={property.id} 
                        position={property.position}
                        icon={createNumberedIcon(property.index)}
                    >
                        <Popup className="property-map-popup">
                            <div className="w-[280px]">
                                <PropertyCard property={property} />
                            </div>
                        </Popup>
                    </Marker>
                ))}
                
                <MapUpdater properties={properties} />
            </MapContainer>
        </div>
    );
}
