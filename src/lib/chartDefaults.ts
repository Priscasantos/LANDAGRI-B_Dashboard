import type { Layout } from 'plotly.js';

/**
 * Build standard Plotly layout with modern styling.
 * Berry chart chrome (reversível, só neutros/geometria — série primária
 * segue Verde Agro via `colorway` em `getChartLayout`): legenda bottom,
 * grid no divider neutro #e3e8ef, tooltip escuro, legend.bg no token
 * de superfície. Margens l:80 r:60 t:60 b:100 preservadas.
 */

/** Berry legend marker — quadrado 8px (aplicar no nível do trace). */
export const BERRY_LEGEND_MARKER = { symbol: 'square', size: 8 } as const;
export function buildStandardLayout(overrides: Partial<Layout> = {}): Partial<Layout> {
  return {
    title: {
      text: '',
      x: 0.5,
      xanchor: 'center',
      font: { size: 16, color: '#1e293b', family: "Inter, system-ui, sans-serif", weight: 600 },
    },
    plot_bgcolor: 'rgba(0,0,0,0)',
    paper_bgcolor: 'rgba(0,0,0,0)',
    font: { family: "Inter, system-ui, sans-serif", size: 12, color: '#475569' },
    legend: {
      orientation: 'h',
      y: -0.28,
      x: 0.5,
      xanchor: 'center',
      yanchor: 'top',
      bordercolor: '#e3e8ef',
      borderwidth: 1,
      bgcolor: '#ffffff',
      font: { size: 11, color: '#475569' },
      itemclick: 'toggle',
      itemdoubleclick: 'toggleothers',
      tracegroupgap: 15,
    },
    // r:60 reserva espaço para a modebar vertical (evita sobreposição ao título/dados);
    // b:100 acomoda legenda horizontal com wrap em telas estreitas.
    margin: { l: 80, r: 60, t: 60, b: 100 },
    hovermode: 'closest',
    autosize: true,
    modebar: { orientation: 'v' },
    hoverlabel: {
      bgcolor: '#1e293b',
      font: { color: '#ffffff', size: 12, family: "Inter, system-ui, sans-serif" },
      bordercolor: 'rgba(0,0,0,0.1)',
      borderwidth: 1,
      namelength: 0,
    },
    xaxis: {
      title: { font: { size: 13, color: '#475569', family: "Inter, system-ui, sans-serif" } },
      tickfont: { size: 11, color: '#94a3b8' },
      gridcolor: '#e3e8ef',
      linecolor: 'rgba(148,163,184,0.3)',
      zerolinecolor: 'rgba(148,163,184,0.2)',
      automargin: true,
    },
    yaxis: {
      title: { font: { size: 13, color: '#475569', family: "Inter, system-ui, sans-serif" } },
      tickfont: { size: 11, color: '#94a3b8' },
      gridcolor: '#e3e8ef',
      linecolor: 'rgba(148,163,184,0.3)',
      zerolinecolor: 'rgba(148,163,184,0.2)',
      automargin: true,
    },
    separators: '.,',
    ...overrides,
  } as Partial<Layout>;
}

/**
 * Get theme-aware chart layout
 */
export function getChartLayout(theme: 'light' | 'dark' = 'light'): Partial<Layout> {
  const isDark = theme === 'dark';
  return {
    plot_bgcolor: 'transparent',
    paper_bgcolor: 'transparent',
    font: {
      family: "Inter, system-ui, sans-serif",
      size: 12,
      color: isDark ? '#e2e8f0' : '#475569',
    },
    hoverlabel: {
      bgcolor: isDark ? '#334155' : '#1e293b',
      font: { color: '#ffffff', size: 12, family: "Inter, system-ui, sans-serif" },
      bordercolor: isDark ? '#475569' : 'rgba(0,0,0,0.1)',
    },
    xaxis: {
      gridcolor: isDark ? 'rgba(51,65,85,0.5)' : '#e3e8ef',
      linecolor: isDark ? '#334155' : 'rgba(148,163,184,0.3)',
      zerolinecolor: isDark ? '#1e293b' : 'rgba(148,163,184,0.2)',
      tickfont: { size: 11, color: isDark ? '#94a3b8' : '#94a3b8' },
      title: { font: { color: isDark ? '#cbd5e1' : '#475569' } },
      automargin: true,
    },
    yaxis: {
      gridcolor: isDark ? 'rgba(51,65,85,0.5)' : '#e3e8ef',
      linecolor: isDark ? '#334155' : 'rgba(148,163,184,0.3)',
      zerolinecolor: isDark ? '#1e293b' : 'rgba(148,163,184,0.2)',
      tickfont: { size: 11, color: isDark ? '#94a3b8' : '#94a3b8' },
      title: { font: { color: isDark ? '#cbd5e1' : '#475569' } },
      automargin: true,
    },
    legend: {
      font: { color: isDark ? '#cbd5e1' : '#475569' },
      bordercolor: isDark ? '#334155' : '#e3e8ef',
      bgcolor: isDark ? 'rgba(30,41,59,0.9)' : '#ffffff',
      tracegroupgap: 15,
    },
    colorway: isDark
      ? ['#9CCC65', '#7CB342', '#C5E1A5', '#43A047', '#E8A04C', '#FFCA28', '#4DD0E1', '#9FA8DA', '#B0BEC5', '#66BB6A']
      : ['#2E7D32', '#43A047', '#7CB342', '#AED581', '#1B5E20', '#C2701D', '#E6A817', '#0E7C86', '#5C6BC0', '#B0BEC5'],
  };
}

export const STANDARD_CONFIG = {
  responsive: true,
  // 'hover' evita a modebar fixa sobreposta ao título/dados (r:60 reserva respiro).
  displayModeBar: 'hover' as const,
  displaylogo: false,
  modeBarButtonsToRemove: ['lasso2d', 'select2d', 'autoScale2d', 'toggleSpikelines', 'hoverCompareCartesian', 'hoverClosestCartesian'],
  modeBarButtonsToAdd: ['drawline', 'eraseshape'],
  toImageButtonOptions: {
    format: 'png' as const,
    filename: 'landagri-chart',
    height: 600,
    width: 1000,
    scale: 2,
  },
};

export const HOVER_TEMPLATES = {
  default: '<b>%{x}</b><br>Value: %{y}<extra></extra>',
  percent: '<b>%{label}</b><br>%{percent}<extra></extra>',
  initiative: '<b>%{x}</b><br>%{y}<extra></extra>',
  heatmap: '<b>%{x}</b> / <b>%{y}</b><br>Value: %{z:.2f}<extra></extra>',
  radar: '<b>%{theta}</b><br>%{r:.2f}<extra></extra>',
  scatter: '<b>%{x}</b><br>%{y:.1f}<extra></extra>',
  timeline: '<b>%{customdata[0]}</b><br>Year: %{x}<br>Period: %{customdata[1]}<extra></extra>',
};
