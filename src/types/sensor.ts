export interface SpectralBand {
  band_name: string;
  band_id?: string;
  wavelength_nm: string;
  resolution_m: number | string;
}

export interface SensorMetadata {
  display_name: string;
  sensor_family: string;
  platform_name: string;
  instrument_names: string[];
  sensor_type_description: string;
  spectral_bands: SpectralBand[] | string;
  spatial_resolutions_m: (number | string)[];
  revisit_time_days: number | string;
  swath_width_km: number | string;
  launch_date: string;
  status: string;
  standard_processing_levels_available: string[];
  typical_geometric_correction_type: string;
  data_access_url: string;
  agency: string;
  notes?: string;
}

export type SensorMap = Record<string, SensorMetadata>;
