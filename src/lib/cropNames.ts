import { normalizeCropOrdinals } from '../data/glossary';

/**
 * Display-level crop-name normalization.
 * Raw CONAB data uses "3th harvest" ("Beans (3th harvest)", "Corn (3th
 * harvest)"); the source files are preserved untouched and only the
 * rendered label is corrected to the proper ordinal ("3rd harvest").
 * Delegates to `normalizeCropOrdinals` (src/data/glossary.ts) — single
 * source of truth. For locale-aware labels use `translateCropName`.
 */
export function formatCropName(name: string): string {
  return normalizeCropOrdinals(name);
}
