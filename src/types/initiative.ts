/** Raw metadata for a single LULC initiative (from JSONC) */
export interface InitiativeMetadata {
  coverage: string;
  acronym: string;
  provider: string;
  source: string;
  spatial_resolution: number | ResolutionObject[];
  available_years: number[];
  temporal_frequency: string;
  update_frequency: string;
  reference_system: string | EpsgCode[];
  methodology: string;
  classification_method: string;
  number_of_classes: number;
  class_legend: string;
  overall_accuracy?: number | AccuracyObject;
  accuracy?: number | AccuracyObject;
  number_of_agriculture_classes: number;
  agricultural_capabilities: string;
  references?: string[];
  algorithm: string;
  sensors_referenced: SensorReference[];
  detailed_products?: DetailedProduct[];
  [key: string]: unknown;
}

export type CoverageType = 'Global' | 'Regional' | 'National' | 'Other';

export type MethodologyType =
  | 'Deep Learning'
  | 'Machine Learning'
  | 'Hybrid'
  | 'Visual Interpretation'
  | 'Automatic Classification';

interface ResolutionObject {
  resolution: number;
  current?: boolean;
  type?: string;
  description?: string;
}

interface EpsgCode {
  epsg_code: string;
  hemisphere: string;
  description: string;
  coverage: string;
  usage_context: string;
}

interface AccuracyObject {
  overall?: number;
  status?: string;
  by_product?: ProductAccuracy[];
  by_collection?: CollectionAccuracy[];
  by_class?: ClassAccuracy[];
}

interface ProductAccuracy {
  product: string;
  accuracy: number;
  current?: boolean;
}

interface CollectionAccuracy {
  collection: string;
  accuracy: number;
  current?: boolean;
}

interface ClassAccuracy {
  class_name: string;
  accuracy: number;
}

interface SensorReference {
  sensor_key: string;
}

export interface DetailedProduct {
  product_name: string;
  product_type: string;
  number_of_classes: number;
  class_legend: string;
  accuracy: number;
  description: string;
  access_type: string;
}

/** Interpreted flat row — DataFrame-like structure for the React app */
export interface InitiativeRow {
  Name: string;
  Display_Name: string;
  Acronym: string;
  Provider: string;
  Source: string;
  Resolution: number;
  Resolution_Min: number;
  Resolution_Max: number;
  Available_Years: number[];
  Year_Start: number;
  Year_End: number;
  Temporal_Duration: number;
  Temporal_Frequency: string;
  Update_Frequency: string;
  Reference_System: string;
  Methodology: MethodologyType;
  Classification_Method: string;
  Coverage: CoverageType;
  Accuracy: number;
  Accuracy_Min: number;
  Accuracy_Max: number;
  /**
   * Display label for accuracy: `"91.0"` when assessed, `"n/a"` when the
   * source reports no/incomplete assessment (never an invented number).
   */
  Accuracy_Label?: string;
  /** Justification for `n/a` (source `reason`/`description`), else `''`. */
  Accuracy_Note?: string;
  Number_of_Classes: number;
  Class_Legend: string;
  Number_of_Agriculture_Classes: number;
  Agricultural_Capabilities: string;
  Algorithm: string;
  Sensors: string[];
  Detailed_Products: DetailedProduct[];
  Has_Detailed_Products: boolean;
}
