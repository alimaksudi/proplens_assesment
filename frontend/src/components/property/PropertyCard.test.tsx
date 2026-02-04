/**
 * PropertyCard component tests.
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { PropertyCard } from './PropertyCard';
import { Property } from '@/types/property';

const mockProperty: Property = {
  id: 1,
  project_name: 'Test Property',
  city: 'Chicago',
  country: 'US',
  property_type: 'apartment',
  bedrooms: 2,
  bathrooms: 2,
  price_usd: 850000,
  area_sqm: 150,
  completion_status: 'available',
  key_features: ['gym', 'pool', 'parking'],
  match_score: 0.95,
  description: 'A beautiful property',
};

describe('PropertyCard', () => {
  it('renders property name', () => {
    render(<PropertyCard property={mockProperty} />);
    expect(screen.getByText('Test Property')).toBeInTheDocument();
  });

  it('renders location', () => {
    render(<PropertyCard property={mockProperty} />);
    expect(screen.getByText('Chicago, US')).toBeInTheDocument();
  });

  it('renders formatted price', () => {
    render(<PropertyCard property={mockProperty} />);
    expect(screen.getByText('$850,000')).toBeInTheDocument();
  });

  it('renders bedroom count', () => {
    render(<PropertyCard property={mockProperty} />);
    expect(screen.getByText('2 beds')).toBeInTheDocument();
  });

  it('renders bathroom count', () => {
    render(<PropertyCard property={mockProperty} />);
    expect(screen.getByText('2 baths')).toBeInTheDocument();
  });

  it('renders match score badge', () => {
    render(<PropertyCard property={mockProperty} />);
    expect(screen.getByText('95% match')).toBeInTheDocument();
  });

  it('renders key features', () => {
    render(<PropertyCard property={mockProperty} />);
    expect(screen.getByText('gym')).toBeInTheDocument();
    expect(screen.getByText('pool')).toBeInTheDocument();
  });

  it('handles click when onSelect is provided', () => {
    const handleSelect = vi.fn();
    render(<PropertyCard property={mockProperty} onSelect={handleSelect} />);

    fireEvent.click(screen.getByText('Test Property'));
    expect(handleSelect).toHaveBeenCalledWith(mockProperty);
  });

  it('applies selected styles', () => {
    const { container } = render(
      <PropertyCard property={mockProperty} isSelected />
    );
    expect(container.firstChild).toHaveClass('ring-2');
  });
});
