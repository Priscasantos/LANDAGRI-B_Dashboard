export const ROUTES = {
  overview: '/LANDAGRI-B_Dashboard/overview',
  initiativeAnalysis: '/LANDAGRI-B_Dashboard/initiative-analysis/temporal',
  agriculturalAnalysis: '/LANDAGRI-B_Dashboard/agricultural-analysis/overview',
  predictive: '/LANDAGRI-B_Dashboard/predictive',
  about: '/LANDAGRI-B_Dashboard/about',
} as const;

export const PAGE_TITLES: Record<string, RegExp> = {
  '/LANDAGRI-B_Dashboard/overview': /Visão Geral|Overview|Dashboard|LANDAGRI/,
  '/LANDAGRI-B_Dashboard/initiative-analysis/temporal': /Iniciativas|Initiatives|Initiative/,
  '/LANDAGRI-B_Dashboard/agricultural-analysis/overview': /Agricultura|Agriculture/,
  '/LANDAGRI-B_Dashboard/predictive': /Simulador|Simulator|Predictive/,
  '/LANDAGRI-B_Dashboard/about': /Sobre o Dashboard|About the LANDAGRI/,
};

export const NAV_MENU_ITEMS = [
  { label: /Visão Geral|Overview/, route: ROUTES.overview },
  { label: /Iniciativas|Initiatives/, route: ROUTES.initiativeAnalysis },
  { label: /Agricultura|Agriculture/, route: ROUTES.agriculturalAnalysis },
  { label: /Simulador|Simulator/, route: ROUTES.predictive },
  { label: /Sobre|About/, route: ROUTES.about },
];

export const TIMEOUTS = {
  pageLoad: 15000,
  chartRender: 8000,
  transition: 2000,
  dataLoad: 5000,
  animation: 1500,
};
