/** Localized string pair from `pam_unified.json` (single numeric payload). */
export interface PamLocalized {
  pt?: string | null;
  en?: string | null;
}

export interface CropProduction {
  code: string;
  /** EN display name (stable crop key lives on the parent record). */
  name: string;
  /** PT display name. */
  nome: string;
  production_quantity_tonnes: Record<string, number>;
  harvested_area_hectares: Record<string, number>;
  average_yield_kg_per_ha?: Record<string, number>;
}

export interface IBGEData {
  metadata: {
    source: PamLocalized;
    survey: PamLocalized;
    survey_code?: string | null;
    territory_level?: PamLocalized;
    periodicity?: PamLocalized;
    period_range?: string | null;
    last_updated?: string | null;
    pam_2025_status?: PamLocalized;
  };
  crops: Record<string, CropProduction>;
  summary_annual: Record<string, Record<string, unknown>>;
}

export interface ConabCropCalendar {
  state: string;
  crop: string;
  planting_start: number;
  planting_end: number;
  harvest_start: number;
  harvest_end: number;
  [key: string]: unknown;
}

export interface ConabAvailability {
  state: string;
  crop: string;
  availability: string;
  [key: string]: unknown;
}

export interface ConabSafra {
  safra: string;
  produto: string;
  estado: string;
  area_plantada?: number;
  area_colhida?: number;
  producao?: number;
  rendimento?: number;
  [key: string]: unknown;
}

export interface ConabMappingData {
  [key: string]: unknown;
}
