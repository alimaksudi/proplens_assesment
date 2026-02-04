/**
 * Utility functions for formatting values.
 */

/**
 * Format price in USD with commas and currency symbol.
 */
export function formatPrice(price: number | undefined | null): string {
  if (price === undefined || price === null) {
    return 'Price on request';
  }
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(price);
}

/**
 * Format area in square meters.
 */
export function formatArea(area: number | undefined | null): string {
  if (area === undefined || area === null) {
    return '';
  }
  return `${area.toLocaleString()} sqm`;
}

/**
 * Format bedroom count.
 */
export function formatBedrooms(count: number | undefined | null): string {
  if (count === undefined || count === null) {
    return '';
  }
  if (count === 0) {
    return 'Studio';
  }
  return `${count} bed${count > 1 ? 's' : ''}`;
}

/**
 * Format bathroom count.
 */
export function formatBathrooms(count: number | undefined | null): string {
  if (count === undefined || count === null) {
    return '';
  }
  return `${count} bath${count > 1 ? 's' : ''}`;
}

/**
 * Format date string.
 */
export function formatDate(dateString: string | undefined | null): string {
  if (!dateString) {
    return '';
  }
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

/**
 * Format completion status for display.
 */
export function formatStatus(status: string | undefined | null): string {
  if (!status) {
    return '';
  }
  const statusMap: Record<string, string> = {
    available: 'Available Now',
    off_plan: 'Off Plan',
    under_construction: 'Under Construction',
    completed: 'Completed',
  };
  return statusMap[status] || status;
}

/**
 * Truncate text with ellipsis.
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) {
    return text;
  }
  return `${text.substring(0, maxLength)}...`;
}

/**
 * Format match score as percentage.
 */
export function formatMatchScore(score: number | undefined | null): string {
  if (score === undefined || score === null) {
    return '';
  }
  return `${Math.round(score * 100)}% match`;
}
