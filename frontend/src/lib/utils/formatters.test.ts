/**
 * Formatter utility tests.
 */

import { describe, it, expect } from 'vitest';
import {
  formatPrice,
  formatBedrooms,
  formatBathrooms,
  formatArea,
  formatStatus,
  formatMatchScore,
  truncateText,
} from './formatters';

describe('formatPrice', () => {
  it('formats price with currency symbol', () => {
    expect(formatPrice(850000)).toBe('$850,000');
  });

  it('handles large numbers', () => {
    expect(formatPrice(2500000)).toBe('$2,500,000');
  });

  it('returns placeholder for undefined', () => {
    expect(formatPrice(undefined)).toBe('Price on request');
  });

  it('returns placeholder for null', () => {
    expect(formatPrice(null)).toBe('Price on request');
  });
});

describe('formatBedrooms', () => {
  it('formats single bedroom', () => {
    expect(formatBedrooms(1)).toBe('1 bed');
  });

  it('formats multiple bedrooms', () => {
    expect(formatBedrooms(3)).toBe('3 beds');
  });

  it('formats studio', () => {
    expect(formatBedrooms(0)).toBe('Studio');
  });

  it('returns empty for undefined', () => {
    expect(formatBedrooms(undefined)).toBe('');
  });
});

describe('formatBathrooms', () => {
  it('formats single bathroom', () => {
    expect(formatBathrooms(1)).toBe('1 bath');
  });

  it('formats multiple bathrooms', () => {
    expect(formatBathrooms(2)).toBe('2 baths');
  });

  it('returns empty for undefined', () => {
    expect(formatBathrooms(undefined)).toBe('');
  });
});

describe('formatArea', () => {
  it('formats area with unit', () => {
    expect(formatArea(150)).toBe('150 sqm');
  });

  it('formats large area with commas', () => {
    expect(formatArea(1500)).toBe('1,500 sqm');
  });

  it('returns empty for undefined', () => {
    expect(formatArea(undefined)).toBe('');
  });
});

describe('formatStatus', () => {
  it('formats available status', () => {
    expect(formatStatus('available')).toBe('Available Now');
  });

  it('formats off_plan status', () => {
    expect(formatStatus('off_plan')).toBe('Off Plan');
  });

  it('returns empty for undefined', () => {
    expect(formatStatus(undefined)).toBe('');
  });
});

describe('formatMatchScore', () => {
  it('formats score as percentage', () => {
    expect(formatMatchScore(0.95)).toBe('95% match');
  });

  it('rounds to nearest integer', () => {
    expect(formatMatchScore(0.876)).toBe('88% match');
  });

  it('returns empty for undefined', () => {
    expect(formatMatchScore(undefined)).toBe('');
  });
});

describe('truncateText', () => {
  it('returns text if shorter than max', () => {
    expect(truncateText('Hello', 10)).toBe('Hello');
  });

  it('truncates with ellipsis', () => {
    expect(truncateText('Hello World', 8)).toBe('Hello Wo...');
  });

  it('handles exact length', () => {
    expect(truncateText('Hello', 5)).toBe('Hello');
  });
});
