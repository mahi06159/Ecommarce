/**
 * Resolves a product image URL to an absolute URL.
 * - Relative media paths (e.g. /media/product_images/xxx.jpg) are prefixed
 *   with VITE_API_BASE_URL so production builds point to the deployed backend.
 * - Absolute URLs (Unsplash/Pexels) are returned as-is.
 * - null / undefined falls back to the generic placeholder.
 */
export const FALLBACK_IMG =
  'https://images.unsplash.com/photo-1531403009284-440f080d1e12?w=400';

export const API_BASE =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '') || '';

export function getImgSrc(img) {
  if (!img) return FALLBACK_IMG;
  if (img.startsWith('http')) return img;
  // Relative path – prepend the backend origin
  return `${API_BASE}${img.startsWith('/') ? '' : '/'}${img}`;
}

/**
 * Extracts the primary image URL from a product's images array
 * (as returned by ProductOutputSerializer).
 */
export function getPrimaryImg(product) {
  const images = product?.images || [];
  const primary = images.find((i) => i.is_primary) || images[0];
  return primary?.image || null;
}

/**
 * One-liner helper: get a resolved src URL for the primary image of a product.
 */
export function productImgSrc(product) {
  return getImgSrc(getPrimaryImg(product));
}
