/**
 * Presets leves de cor (Fase 3) — alternativa sem peso aos ~40 presets
 * oklch da referência (`shadcn-ui-theme-presets`).
 *
 * Cada preset define o conjunto COMPLETO de tokens que o customizer
 * sobrescreve na raiz (`use-theme-manager` → `applyToRoot`): primary,
 * charts categóricos 1–10, sidebar e headers, em light+dark. Escopo
 * estreito (só primary/hover/accent) deixava Terra/Âmbar/Padrão quase
 * invisíveis — por isso o preset carrega tudo que precisa trocar.
 *
 * Escolha de rótulos (causa 2): o default do app é `agro-v2` ("Verde
 * Agro v2"); a opção azul chama-se "Azul" (valor `default`, mantido por
 * compatibilidade com `landagri-preset` já persistido). "Restaurar
 * padrão" no customizer = voltar aos defaults do app (agro-v2 +
 * confortável + md + fonte padrão), NÃO à opção Azul. Reversível:
 * `resetCustomizations()` só recoloca esses estados (reaplica as vars).
 */
export interface ThemePresetColors {
  primary: string;
  primaryHover: string;
  primaryLight: string;
  accent: string;
  /** Paleta categórica — espelha `--color-chart-1..10` do `index.css`. */
  charts: readonly string[];
  sidebarBg: string;
  sidebarText: string;
  sidebarTextActive: string;
  sidebarActiveBg: string;
  sidebarHoverBg: string;
  /** Gradientes por módulo — espelham `--color-header-*` do `index.css`. */
  headerOverview: string;
  headerInitiative: string;
  headerAgricultural: string;
  headerAbout: string;
}

export interface ThemePreset {
  value: string;
  label: string;
  light: ThemePresetColors;
  dark: ThemePresetColors;
}

export const THEME_PRESETS: readonly ThemePreset[] = [
  {
    value: 'default',
    label: 'Azul',
    light: {
      primary: '#3b82f6',
      primaryHover: '#2563eb',
      primaryLight: '#eff6ff',
      accent: '#eff6ff',
      charts: [
        '#2563eb',
        '#3b82f6',
        '#60a5fa',
        '#93c5fd',
        '#1e40af',
        '#0e7c86',
        '#e6a817',
        '#5c6bc0',
        '#c2701d',
        '#94a3b8',
      ],
      sidebarBg: '#ffffff',
      sidebarText: '#334155',
      sidebarTextActive: '#2563eb',
      sidebarActiveBg: '#eff6ff',
      sidebarHoverBg: '#f1f5f9',
      headerOverview:
        'linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)',
      headerInitiative:
        'linear-gradient(135deg, #1e3a8f 0%, #60a5fa 100%)',
      headerAgricultural:
        'linear-gradient(135deg, #1d4ed8 0%, #93c5fd 100%)',
      headerAbout:
        'linear-gradient(135deg, #172554 0%, #3b82f6 100%)',
    },
    dark: {
      primary: '#60a5fa',
      primaryHover: '#3b82f6',
      primaryLight: '#1e3a5f',
      accent: '#1e3a5f',
      charts: [
        '#93c5fd',
        '#60a5fa',
        '#3b82f6',
        '#bfdbfe',
        '#2563eb',
        '#4dd0e1',
        '#ffca28',
        '#9fa8da',
        '#e8a04c',
        '#cbd5e1',
      ],
      sidebarBg: '#0b1526',
      sidebarText: '#93a4bd',
      sidebarTextActive: '#93c5fd',
      sidebarActiveBg: '#1e3a5f',
      sidebarHoverBg: '#111f36',
      headerOverview:
        'linear-gradient(135deg, #0c1a3a 0%, #1e40af 100%)',
      headerInitiative:
        'linear-gradient(135deg, #0f172a 0%, #1e3a8f 100%)',
      headerAgricultural:
        'linear-gradient(135deg, #172554 0%, #1d4ed8 100%)',
      headerAbout:
        'linear-gradient(135deg, #020617 0%, #1e40af 100%)',
    },
  },
  {
    value: 'agro',
    label: 'Verde Agro',
    light: {
      primary: '#626C01',
      primaryHover: '#4d5601',
      primaryLight: '#f7fee7',
      accent: '#f7fee7',
      charts: [
        '#626C01',
        '#7a8602',
        '#a3b018',
        '#c0ca33',
        '#4d5601',
        '#c2701d',
        '#e6a817',
        '#0e7c86',
        '#5c6bc0',
        '#94a3b8',
      ],
      sidebarBg: '#ffffff',
      sidebarText: '#3f5546',
      sidebarTextActive: '#4d5601',
      sidebarActiveBg: '#f7fee7',
      sidebarHoverBg: '#f6f9f4',
      headerOverview:
        'linear-gradient(135deg, #4d5601 0%, #626C01 100%)',
      headerInitiative:
        'linear-gradient(135deg, #80400B 0%, #626C01 100%)',
      headerAgricultural:
        'linear-gradient(135deg, #92400e 0%, #a3b018 100%)',
      headerAbout:
        'linear-gradient(135deg, #3f6212 0%, #626C01 100%)',
    },
    dark: {
      primary: '#a3b018',
      primaryHover: '#626C01',
      primaryLight: '#1a2e05',
      accent: '#1a2e05',
      charts: [
        '#c0ca33',
        '#a3b018',
        '#7a8602',
        '#d9e021',
        '#626C01',
        '#e8a04c',
        '#ffca28',
        '#4dd0e1',
        '#9fa8da',
        '#cbd5e1',
      ],
      sidebarBg: '#0c1510',
      sidebarText: '#9db4a3',
      sidebarTextActive: '#c0ca33',
      sidebarActiveBg: '#1a2e05',
      sidebarHoverBg: '#122019',
      headerOverview:
        'linear-gradient(135deg, #141a05 0%, #4d5601 100%)',
      headerInitiative:
        'linear-gradient(135deg, #292524 0%, #44403c 100%)',
      headerAgricultural:
        'linear-gradient(135deg, #1a2e05 0%, #292524 100%)',
      headerAbout:
        'linear-gradient(135deg, #1c1917 0%, #292524 100%)',
    },
  },
  {
    value: 'agro-v2',
    label: 'Verde Agro v2',
    light: {
      primary: '#2E7D32',
      primaryHover: '#1B5E20',
      primaryLight: '#E8F5E9',
      accent: '#E8F5E9',
      charts: [
        '#2E7D32',
        '#43A047',
        '#7CB342',
        '#AED581',
        '#1B5E20',
        '#C2701D',
        '#E6A817',
        '#0E7C86',
        '#5C6BC0',
        '#B0BEC5',
      ],
      sidebarBg: '#ffffff',
      sidebarText: '#3f5546',
      sidebarTextActive: '#1b5e20',
      sidebarActiveBg: '#e8f5e9',
      sidebarHoverBg: '#f6f9f4',
      headerOverview:
        'linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%)',
      headerInitiative:
        'linear-gradient(135deg, #80400b 0%, #626c01 100%)',
      headerAgricultural:
        'linear-gradient(135deg, #ec9706 0%, #626c01 100%)',
      headerAbout:
        'linear-gradient(135deg, #918c00 0%, #626c01 100%)',
    },
    dark: {
      primary: '#9CCC65',
      primaryHover: '#AED581',
      primaryLight: '#16241a',
      accent: '#16241A',
      charts: [
        '#9CCC65',
        '#7CB342',
        '#C5E1A5',
        '#43A047',
        '#E8A04C',
        '#FFCA28',
        '#4DD0E1',
        '#9FA8DA',
        '#B0BEC5',
        '#66BB6A',
      ],
      sidebarBg: '#0c1510',
      sidebarText: '#9db4a3',
      sidebarTextActive: '#9ccc65',
      sidebarActiveBg: '#16241a',
      sidebarHoverBg: '#122019',
      headerOverview:
        'linear-gradient(135deg, #0c1510 0%, #1b5e20 100%)',
      headerInitiative:
        'linear-gradient(135deg, #44403c 0%, #292524 100%)',
      headerAgricultural:
        'linear-gradient(135deg, #451a03 0%, #292524 100%)',
      headerAbout:
        'linear-gradient(135deg, #3f3f46 0%, #27272a 100%)',
    },
  },
  {
    value: 'terra',
    label: 'Terra',
    light: {
      primary: '#80400B',
      primaryHover: '#653208',
      primaryLight: '#fef3c7',
      accent: '#fef3c7',
      charts: [
        '#80400B',
        '#a0522d',
        '#c2701d',
        '#e6a817',
        '#653208',
        '#2e7d32',
        '#0e7c86',
        '#5c6bc0',
        '#7cb342',
        '#94a3b8',
      ],
      sidebarBg: '#ffffff',
      sidebarText: '#57534e',
      sidebarTextActive: '#653208',
      sidebarActiveBg: '#fef3c7',
      sidebarHoverBg: '#fafaf9',
      headerOverview:
        'linear-gradient(135deg, #653208 0%, #80400B 100%)',
      headerInitiative:
        'linear-gradient(135deg, #451a03 0%, #a0522d 100%)',
      headerAgricultural:
        'linear-gradient(135deg, #92400e 0%, #c2701d 100%)',
      headerAbout:
        'linear-gradient(135deg, #57534e 0%, #80400B 100%)',
    },
    dark: {
      primary: '#d08a3e',
      primaryHover: '#80400B',
      primaryLight: '#451a03',
      accent: '#451a03',
      charts: [
        '#e8a04c',
        '#d08a3e',
        '#c2701d',
        '#f0b35c',
        '#a0522d',
        '#9ccc65',
        '#4dd0e1',
        '#9fa8da',
        '#c5e1a5',
        '#cbd5e1',
      ],
      sidebarBg: '#1a120a',
      sidebarText: '#b8a89a',
      sidebarTextActive: '#e8a04c',
      sidebarActiveBg: '#451a03',
      sidebarHoverBg: '#241610',
      headerOverview:
        'linear-gradient(135deg, #241610 0%, #653208 100%)',
      headerInitiative:
        'linear-gradient(135deg, #292524 0%, #44403c 100%)',
      headerAgricultural:
        'linear-gradient(135deg, #451a03 0%, #292524 100%)',
      headerAbout:
        'linear-gradient(135deg, #1c1917 0%, #292524 100%)',
    },
  },
  {
    value: 'ambar',
    label: 'Âmbar',
    light: {
      primary: '#EC9706',
      primaryHover: '#c67d05',
      primaryLight: '#ffedd5',
      accent: '#ffedd5',
      charts: [
        '#EC9706',
        '#f59e0b',
        '#fbbf24',
        '#fcd34d',
        '#c67d05',
        '#0e7c86',
        '#2e7d32',
        '#5c6bc0',
        '#c2701d',
        '#94a3b8',
      ],
      sidebarBg: '#ffffff',
      sidebarText: '#57534e',
      sidebarTextActive: '#c67d05',
      sidebarActiveBg: '#ffedd5',
      sidebarHoverBg: '#fafaf9',
      headerOverview:
        'linear-gradient(135deg, #92400e 0%, #EC9706 100%)',
      headerInitiative:
        'linear-gradient(135deg, #78350f 0%, #f59e0b 100%)',
      headerAgricultural:
        'linear-gradient(135deg, #b45309 0%, #fbbf24 100%)',
      headerAbout:
        'linear-gradient(135deg, #57534e 0%, #EC9706 100%)',
    },
    dark: {
      primary: '#fbbf24',
      primaryHover: '#EC9706',
      primaryLight: '#451a03',
      accent: '#451a03',
      charts: [
        '#fcd34d',
        '#fbbf24',
        '#f59e0b',
        '#fde68a',
        '#EC9706',
        '#4dd0e1',
        '#9ccc65',
        '#9fa8da',
        '#e8a04c',
        '#cbd5e1',
      ],
      sidebarBg: '#1a120a',
      sidebarText: '#b8a89a',
      sidebarTextActive: '#fbbf24',
      sidebarActiveBg: '#451a03',
      sidebarHoverBg: '#241610',
      headerOverview:
        'linear-gradient(135deg, #241610 0%, #92400e 100%)',
      headerInitiative:
        'linear-gradient(135deg, #292524 0%, #44403c 100%)',
      headerAgricultural:
        'linear-gradient(135deg, #451a03 0%, #292524 100%)',
      headerAbout:
        'linear-gradient(135deg, #1c1917 0%, #292524 100%)',
    },
  },
];

export const DEFAULT_PRESET = 'agro-v2';

export function getThemePreset(value: string): ThemePreset {
  return (
    THEME_PRESETS.find((p) => p.value === value) ??
    THEME_PRESETS.find((p) => p.value === DEFAULT_PRESET) ??
    THEME_PRESETS[0]
  );
}
