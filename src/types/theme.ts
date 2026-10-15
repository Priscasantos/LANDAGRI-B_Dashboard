export type ModuleName =
  | 'Overview'
  | 'Initiative Analysis'
  | 'Agricultural Analysis'
  | 'About';

export type PageName =
  | 'Dashboard Overview'
  | 'Temporal Analysis'
  | 'Comparative Analysis'
  | 'Detailed Analysis'
  | 'Agriculture Overview'
  | 'Crop Calendar'
  | 'Agriculture Availability'
  | 'About the Dashboard';

export interface MenuItem {
  label: PageName;
  icon: string;
  path: string;
}

export interface MenuCategory {
  label: ModuleName;
  icon: string;
  pages: MenuItem[];
}

export interface ThemeColors {
  primary: string;
  secondary: string;
  accent: string[];
  background: string;
  card: string;
  text: string;
  textSecondary: string;
  border: string;
  /**
   * @deprecated Fase 3: full-bleed removido. `ModuleHeader` usa `primary`
   * como accent lateral (`MODULE_ACCENT`), sem fundo em gradiente.
   * Mantido para compatibilidade — não usar em código novo.
   */
  headerGradient: string;
  headerTextColor: string;
  headerSubtitleColor: string;
}

export const MODULE_THEMES: Record<ModuleName, ThemeColors> = {
  Overview: {
    primary: '#2e7d32',
    secondary: '#1b5e20',
    accent: ['#1B5E20', '#2E7D32'],
    background: 'linear-gradient(135deg, #f6f9f4 0%, #e8f5e9 100%)',
    card: '#ffffff',
    text: '#1a2b1e',
    textSecondary: '#4a6350',
    border: 'rgba(46, 125, 50, 0.12)',
    headerGradient: 'linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%)',
    headerTextColor: '#ffffff',
    headerSubtitleColor: '#fdebd6',
  },
  'Initiative Analysis': {
    primary: '#80400B',
    secondary: '#626C01',
    accent: ['#80400B', '#626C01'],
    background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
    card: '#ffffff',
    text: '#1e293b',
    textSecondary: '#64748b',
    border: 'rgba(148, 163, 184, 0.1)',
    headerGradient: 'linear-gradient(135deg, #80400B 0%, #626C01 100%)',
    headerTextColor: '#ffffff',
    headerSubtitleColor: '#fdebd6',
  },
  'Agricultural Analysis': {
    primary: '#EC9706',
    secondary: '#626C01',
    accent: ['#EC9706', '#626C01'],
    background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
    card: '#ffffff',
    text: '#1e293b',
    textSecondary: '#64748b',
    border: 'rgba(148, 163, 184, 0.1)',
    headerGradient: 'linear-gradient(135deg, #EC9706 0%, #626C01 100%)',
    headerTextColor: '#ffffff',
    headerSubtitleColor: '#fdebd6',
  },
  About: {
    primary: '#918C00',
    secondary: '#626C01',
    accent: ['#918C00', '#626C01'],
    background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
    card: '#ffffff',
    text: '#1e293b',
    textSecondary: '#64748b',
    border: 'rgba(148, 163, 184, 0.1)',
    headerGradient: 'linear-gradient(135deg, #918C00 0%, #626C01 100%)',
    headerTextColor: '#ffffff',
    headerSubtitleColor: '#fdebd6',
  },
};

// Chart color palettes (ported from modern_themes.py / modern_color_palettes.py)
// Categorical base = Verde Agro v2 (tokens `--color-chart-1..10` em index.css).
export const CATEGORICAL_COLORS = [
  '#2E7D32', '#43A047', '#7CB342', '#AED581', '#1B5E20',
  '#C2701D', '#E6A817', '#0E7C86', '#5C6BC0', '#B0BEC5',
  '#22c55e', '#14b8a6',
];

export const DIVERGING_COLORS = [
  '#d73027', '#fc8d59', '#fee08b', '#d9ef8b', '#91cf60', '#1a9850',
];

export const SEQUENTIAL_COLORS = [
  '#f7fcf0', '#e0f3db', '#ccebc5', '#a8ddb5', '#7bccc4', '#4eb3d3', '#2b8cbe', '#0868ac', '#084081',
];

export const LULC_CLASS_COLORS: Record<string, string> = {
  Forest: '#22c55e',
  Trees: '#22c55e',
  Water: '#06b6d4',
  Urban: '#ef4444',
  Built: '#ef4444',
  Cropland: '#eab308',
  Crops: '#eab308',
  Bare: '#a1a1aa',
  Snow: '#e2e8f0',
  Wetland: '#818cf8',
  Herbaceous: '#84cc16',
  Shrubland: '#f97316',
  Pasture: '#86efac',
  Mosaic: '#fde047',
};

export const METRIC_GRADIENTS = {
  accuracy: 'linear-gradient(135deg, #fef9c3 0%, #fde68a 100%)',
  resolution: 'linear-gradient(135deg, #d1fae5 0%, #6ee7b7 100%)',
  classes: 'linear-gradient(135deg, #fbcfe8 0%, #f472b6 100%)',
  frequency: 'linear-gradient(135deg, #bae6fd 0%, #38bdf8 100%)',
};

/**
 * Accent por seção (Fase 3) — substitui o `headerGradient` full-bleed.
 * Usado como detalhe lateral/texto, nunca como fundo.
 */
export const MODULE_ACCENT: Record<ModuleName, string> = {
  Overview: MODULE_THEMES.Overview.primary,
  'Initiative Analysis': MODULE_THEMES['Initiative Analysis'].primary,
  'Agricultural Analysis': MODULE_THEMES['Agricultural Analysis'].primary,
  About: MODULE_THEMES.About.primary,
};

// Menu structure matching app.py
export const MENU_STRUCTURE: MenuCategory[] = [
  {
    label: 'Overview',
    icon: 'binoculars',
    pages: [
      { label: 'Dashboard Overview', icon: 'binoculars', path: '/overview' },
    ],
  },
  {
    label: 'Initiative Analysis',
    icon: 'stopwatch',
    pages: [
      { label: 'Temporal Analysis', icon: 'stopwatch', path: '/initiative-analysis/temporal' },
      { label: 'Comparative Analysis', icon: 'layers', path: '/initiative-analysis/comparative' },
      { label: 'Detailed Analysis', icon: 'search', path: '/initiative-analysis/detailed' },
    ],
  },
  {
    label: 'Agricultural Analysis',
    icon: 'database',
    pages: [
      { label: 'Agriculture Overview', icon: 'database', path: '/agricultural-analysis/overview' },
      { label: 'Crop Calendar', icon: 'calendar', path: '/agricultural-analysis/crop-calendar' },
      { label: 'Agriculture Availability', icon: 'columns', path: '/agricultural-analysis/availability' },
    ],
  },
  {
    label: 'About',
    icon: 'info',
    pages: [
      { label: 'About the Dashboard', icon: 'info', path: '/about' },
    ],
  },
];
