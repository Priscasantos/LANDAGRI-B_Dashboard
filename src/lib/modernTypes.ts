export interface KPICardData {
  id: string;
  label: string;
  value: string | number;
  unit?: string;
  delta?: {
    value: string;
    positive: boolean;
    label: string;
  };
  icon: string;
  color: string;
}

export interface ChartDataPoint {
  name: string;
  [key: string]: string | number;
}

export interface PolicyParams {
  reforestationRate: number;
  agriExpansion: number;
  sustainableAdoption: number;
}

export interface PolicyResult {
  year: number;
  forestryArea: number;
  pastureArea: number;
  agricultureArea: number;
  carbonEmissionIndex: number;
}

export interface DataSource {
  initials: string;
  name: string;
  description: string;
  color: string;
  url?: string;
}
