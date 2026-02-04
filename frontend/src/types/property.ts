/**
 * Property-related type definitions.
 */

export interface Property {
  id: number;
  project_name: string;
  city: string;
  country: string;
  latitude?: number;
  longitude?: number;
  property_type?: string;
  bedrooms?: number;
  bathrooms?: number;
  price_usd?: number;
  area_sqm?: number;
  completion_status?: string;
  key_features: string[];
  match_score?: number;
  description?: string;
  image_url?: string;
}

export interface PropertyRecommendation extends Property {
  match_score?: number;
}
