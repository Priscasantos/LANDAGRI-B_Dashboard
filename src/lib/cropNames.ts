/**
 * Display-level crop-name normalization.
 * Raw CONAB data uses "3th harvest" ("Beans (3th harvest)", "Corn (3th
 * harvest)"); the source files are preserved untouched and only the
 * rendered label is corrected to the proper ordinal ("3rd harvest").
 */
export function formatCropName(name: string): string {
  return name
    .replace(/\b1th\b/g, '1st')
    .replace(/\b2th\b/g, '2nd')
    .replace(/\b3th\b/g, '3rd');
}
