import type { InitiativeMetadata, InitiativeRow, CoverageType, MethodologyType, DetailedProduct } from '../types/initiative';
import { ACCURACY_UNAVAILABLE_LABEL } from './accuracyDisplay';

/**
 * Parse initiatives metadata JSON → typed array of InitiativeRow.
 * Equivalent to interpret_initiatives_metadata() in json_interpreter.py
 */
export function parseInitiatives(metadata: Record<string, InitiativeMetadata>): InitiativeRow[] {
  return Object.entries(metadata)
    .filter(([, data]) => data && typeof data === 'object' && data.acronym)
    .map(([name, data]) => parseSingleInitiative(name, data));
}

function parseSingleInitiative(name: string, data: InitiativeMetadata): InitiativeRow {
  const resolutionInfo = parseResolution(data.spatial_resolution);
  const rawAccuracy: unknown = data.overall_accuracy ?? data.accuracy ?? null;
  const accuracyInfo = parseAccuracy(rawAccuracy);
  const accuracyDisplay = describeAccuracy(rawAccuracy, accuracyInfo.value);
  const years = Array.isArray(data.available_years) ? data.available_years : [];
  const yearStart = years.length > 0 ? Math.min(...years) : 0;
  const yearEnd = years.length > 0 ? Math.max(...years) : 0;

  return {
    Name: name,
    Display_Name: data.acronym ? `${name} (${data.acronym})` : name,
    Acronym: data.acronym || 'N/A',
    Provider: data.provider || '',
    Source: data.source || '',
    Resolution: resolutionInfo.value,
    Resolution_Min: resolutionInfo.minVal,
    Resolution_Max: resolutionInfo.maxVal,
    Available_Years: years,
    Year_Start: yearStart,
    Year_End: yearEnd,
    Temporal_Duration: years.length > 0 ? yearEnd - yearStart : 0,
    Temporal_Frequency: data.temporal_frequency || '',
    Update_Frequency: data.update_frequency || '',
    Reference_System: normalizeReferenceSystem(data.reference_system),
    Methodology: normalizeMethodology(data.methodology),
    Classification_Method: data.classification_method || '',
    Coverage: normalizeCoverage(data.coverage),
    Accuracy: accuracyInfo.value,
    Accuracy_Min: accuracyInfo.minVal,
    Accuracy_Max: accuracyInfo.maxVal,
    Accuracy_Label: accuracyDisplay.label,
    Accuracy_Note: accuracyDisplay.note,
    Number_of_Classes: data.number_of_classes || 0,
    Class_Legend: data.class_legend || '',
    Number_of_Agriculture_Classes: data.number_of_agriculture_classes || 0,
    Agricultural_Capabilities: data.agricultural_capabilities || '',
    Algorithm: data.algorithm || '',
    Sensors: data.sensors_referenced?.map((s) => s.sensor_key) || [],
    Detailed_Products: (data.detailed_products || []) as DetailedProduct[],
    Has_Detailed_Products: Array.isArray(data.detailed_products) && data.detailed_products.length > 0,
  };
}

function normalizeCoverage(coverage: string): CoverageType {
  const map: Record<string, CoverageType> = {
    global: 'Global',
    regional: 'Regional',
    national: 'National',
    other: 'Other',
  };
  return map[coverage?.toLowerCase()] || 'Other';
}

function normalizeMethodology(methodology: string): MethodologyType {
  const valid: MethodologyType[] = [
    'Deep Learning', 'Machine Learning', 'Hybrid',
    'Visual Interpretation', 'Automatic Classification',
  ];
  if (valid.includes(methodology as MethodologyType)) {
    return methodology as MethodologyType;
  }
  // Try fuzzy match
  const lower = methodology?.toLowerCase() || '';
  if (lower.includes('deep')) return 'Deep Learning';
  if (lower.includes('machine')) return 'Machine Learning';
  if (lower.includes('hybrid')) return 'Hybrid';
  if (lower.includes('visual')) return 'Visual Interpretation';
  if (lower.includes('automatic') || lower.includes('auto')) return 'Automatic Classification';
  return 'Automatic Classification';
}

function normalizeReferenceSystem(ref: unknown): string {
  if (typeof ref === 'string') return ref;
  if (Array.isArray(ref) && ref.length > 0) {
    const first = ref[0];
    if (typeof first === 'object' && first !== null && 'epsg_code' in first) {
      return (first as { epsg_code: string }).epsg_code;
    }
    return String(first);
  }
  return '';
}

interface ResolutionInfo { value: number; minVal: number; maxVal: number; }

function parseResolution(resolution: unknown): ResolutionInfo {
  const defaultRes: ResolutionInfo = { value: 30, minVal: 30, maxVal: 30 };
  if (resolution === null || resolution === undefined) return defaultRes;
  if (typeof resolution === 'number') return { value: resolution, minVal: resolution, maxVal: resolution };
  if (typeof resolution === 'string') {
    const num = parseFloat(resolution.replace(/[^\d.]/g, ''));
    return isNaN(num) ? defaultRes : { value: num, minVal: num, maxVal: num };
  }
  if (Array.isArray(resolution)) {
    const values = resolution
      .map((item): number | null => {
        if (typeof item === 'number') return item;
        if (typeof item === 'object' && item !== null) {
          const obj = item as Record<string, unknown>;
          if ('resolution' in obj) {
            const v = typeof obj.resolution === 'number' ? obj.resolution : parseFloat(String(obj.resolution));
            return isNaN(v) ? null : v;
          }
        }
        return null;
      })
      .filter((v): v is number => v !== null);
    return values.length > 0
      ? { value: values[0], minVal: Math.min(...values), maxVal: Math.max(...values) }
      : defaultRes;
  }
  return defaultRes;
}

interface AccuracyInfo { value: number; minVal: number; maxVal: number; }

function parseAccuracy(accuracy: unknown): AccuracyInfo {
  const zero: AccuracyInfo = { value: 0, minVal: 0, maxVal: 0 };
  if (accuracy === null || accuracy === undefined) return zero;
  if (typeof accuracy === 'number') return { value: accuracy, minVal: accuracy, maxVal: accuracy };
  if (typeof accuracy === 'string') {
    const num = parseFloat(accuracy.replace(/[^\d.]/g, ''));
    return isNaN(num) ? zero : { value: num, minVal: num, maxVal: num };
  }
  if (typeof accuracy === 'object' && accuracy !== null) {
    const acc = accuracy as Record<string, unknown>;
    if (acc.status === 'not_available') return zero;
    if (typeof acc.overall === 'number') {
      const v = acc.overall;
      return { value: v, minVal: v, maxVal: v };
    }
    // Check by_product for average
    if (Array.isArray(acc.by_product) && acc.by_product.length > 0) {
      const accs = acc.by_product
        .map((p: Record<string, unknown>) => typeof p.accuracy === 'number' ? p.accuracy : null)
        .filter((v: number | null): v is number => v !== null);
      if (accs.length > 0) {
        const avg = accs.reduce((a: number, b: number) => a + b, 0) / accs.length;
        return { value: Math.round(avg * 10) / 10, minVal: Math.min(...accs), maxVal: Math.max(...accs) };
      }
    }
  }
  return zero;
}

/**
 * Human display for accuracy: numeric label when assessed, `"—/n.d."`
 * (literal do council) with the source justification when the assessment
 * is missing/incomplete (IBGE-MLCU sem avaliação, CONAB-AM incompleta).
 * Never invents a number — unassessed series stay `—/n.d.`, not `0.0`
 * (0 interno = ausente; ver `lib/accuracyDisplay.ts`).
 */
function describeAccuracy(raw: unknown, value: number): { label: string; note: string } {
  if (value > 0) return { label: value.toFixed(1), note: '' };
  let note = 'Accuracy not assessed for this series (n/a — no published assessment).';
  if (raw !== null && typeof raw === 'object') {
    const r = raw as Record<string, unknown>;
    if (typeof r.reason === 'string' && r.reason !== '') note = r.reason;
    else if (typeof r.description === 'string' && r.description !== '') note = r.description;
  }
  return { label: ACCURACY_UNAVAILABLE_LABEL, note };
}

/**
 * Min-max normalization helper (from Python's MinMaxScaler)
 */
export function normalizeValues(values: number[]): number[] {
  const min = Math.min(...values);
  const max = Math.max(...values);
  if (max === min) return values.map(() => 0.5);
  return values.map((v) => (v - min) / (max - min));
}

/**
 * Get available years from an initiative with parsing
 */
export function parseAvailableYears(yearsStr: string | number[]): number[] {
  if (Array.isArray(yearsStr)) return yearsStr;
  if (typeof yearsStr === 'string') {
    try {
      return JSON.parse(yearsStr);
    } catch {
      return [];
    }
  }
  return [];
}

/**
 * Clean column names (from Python's clean_column_names)
 */
export function cleanColumnName(name: string): string {
  return name
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())
    .replace(/(\d+)/g, ' $1')
    .trim();
}
