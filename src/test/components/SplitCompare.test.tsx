import { describe, expect, it, vi, afterEach, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { LanguageProvider } from '../../i18n/LanguageContext';
import { LANGUAGE_STORAGE_KEY } from '../../i18n/types';
import { translate } from '../../i18n';
import { ThemeProvider } from '../../components/theme-provider';
import EChartsBase from '../../components/charts/echarts/EChartsBase';
import EChartsTimeline from '../../components/charts/echarts/EChartsTimeline';
import { buildLineOption } from '../../components/charts/echarts/echarts-options';
import { echarts } from '../../components/charts/echarts/echarts-setup';
import SplitCompareView from '../../components/initiative-analysis/ComparativeAnalysis/SplitCompareView';
import SplitCompareTab from '../../components/initiative-analysis/ComparativeAnalysis/SplitCompareTab';
import { useDashboardStore } from '../../stores/dashboardStore';
import type { InitiativeRow } from '../../types/initiative';

function seedTwo(): void {
  const base = {
    Provider: 'P',
    Source: 'S',
    Resolution_Min: 30,
    Resolution_Max: 30,
    Temporal_Duration: 1,
    Temporal_Frequency: 'Annual',
    Update_Frequency: 'Yearly',
    Reference_System: 'EPSG:4326',
    Classification_Method: 'RF',
    Accuracy_Min: 88,
    Accuracy_Max: 92,
    Class_Legend: '',
    Number_of_Agriculture_Classes: 2,
    Agricultural_Capabilities: '',
    Algorithm: '',
    Sensors: [],
    Detailed_Products: [],
    Has_Detailed_Products: false,
  };
  useDashboardStore.setState({
    initiatives: [
      {
        ...base,
        Name: 'MapBiomas',
        Display_Name: 'MapBiomas (MB)',
        Acronym: 'MB',
        Resolution: 30,
        Available_Years: [2000, 2001],
        Year_Start: 2000,
        Year_End: 2001,
        Methodology: 'Machine Learning',
        Coverage: 'National',
        Accuracy: 90,
        Number_of_Classes: 10,
      },
      {
        ...base,
        Name: 'TerraClass',
        Display_Name: 'TerraClass (TC)',
        Acronym: 'TC',
        Resolution: 60,
        Available_Years: [2001, 2004],
        Year_Start: 2001,
        Year_End: 2004,
        Methodology: 'Visual',
        Coverage: 'Regional',
        Accuracy: 85,
        Number_of_Classes: 8,
      },
    ] as InitiativeRow[],
    isLoading: false,
    error: null,
  });
}

function stubMatchMedia(reduced: boolean): void {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    configurable: true,
    value: (query: string): MediaQueryList =>
      ({
        matches: query.includes('prefers-reduced-motion') ? reduced : false,
        media: query,
        onchange: null,
        addListener: () => undefined,
        removeListener: () => undefined,
        addEventListener: () => undefined,
        removeEventListener: () => undefined,
        dispatchEvent: () => false,
      }) as unknown as MediaQueryList,
  });
}

function providers(ui: React.ReactElement): React.ReactElement {
  return (
    <LanguageProvider>
      <ThemeProvider>{ui}</ThemeProvider>
    </LanguageProvider>
  );
}

const TIMELINE_ITEMS = [
  { label: 'MapBiomas', years: [2000, 2001], color: '#2E7D32' },
  { label: 'TerraClass', years: [2001, 2004], color: '#43A047' },
];

describe('split-view + timeline animada (Expansão #4)', () => {
  beforeEach(() => {
    window.localStorage.clear();
    window.localStorage.setItem(LANGUAGE_STORAGE_KEY, 'pt-BR');
    document.documentElement.lang = 'pt-BR';
    stubMatchMedia(false);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('i18n PT/EN cobre play/pause e split', () => {
    expect(translate('pt-BR', 'charts', 'timelinePlay')).toBe('Reproduzir linha do tempo');
    expect(translate('en', 'charts', 'timelinePlay')).toBe('Play timeline');
    expect(translate('pt-BR', 'charts', 'timelinePause')).toBe('Pausar linha do tempo');
    expect(translate('en', 'charts', 'timelinePause')).toBe('Pause timeline');
    expect(translate('pt-BR', 'initiative', 'tabSplit')).toBe('Lado a Lado');
    expect(translate('en', 'initiative', 'tabSplit')).toBe('Side by Side');
  });

  it('EChartsBase conecta charts do mesmo grupo (tooltip/zoom sincronizados)', async () => {
    const option = buildLineOption({
      series: [{ name: 'S', x: [2020], y: [1] }],
      theme: 'light',
      locale: 'pt-BR',
    });
    const { container } = render(
      providers(
        <>
          <EChartsBase option={option} ariaLabel="A" group="landagri-split-test" />
          <EChartsBase option={option} ariaLabel="B" group="landagri-split-test" />
        </>,
      ),
    );
    expect(screen.getByRole('img', { name: 'A' })).toBeInTheDocument();
    expect(screen.getByRole('img', { name: 'B' })).toBeInTheDocument();
    // onChartReady é assíncrono (echarts-for-react inicializa com await).
    await waitFor(() => {
      const divs = container.querySelectorAll('div[_echarts_instance_]');
      expect(divs.length).toBe(2);
      const groups = [...divs].map(
        (d) => echarts.getInstanceByDom(d as HTMLElement)?.group,
      );
      expect(groups).toEqual(['landagri-split-test', 'landagri-split-test']);
    });
  });

  it('timeline animada: play/pause traduzido alterna o autoplay', () => {
    render(providers(<EChartsTimeline items={TIMELINE_ITEMS} animated />));
    const pause = screen.getByRole('button', { name: /pausar linha do tempo/i });
    expect(pause).toHaveAttribute('aria-pressed', 'true');
    fireEvent.click(pause);
    expect(screen.getByRole('button', { name: /reproduzir linha do tempo/i })).toHaveAttribute(
      'aria-pressed',
      'false',
    );
  });

  it('timeline animada: prefers-reduced-motion desliga o autoplay inicial', () => {
    stubMatchMedia(true);
    render(providers(<EChartsTimeline items={TIMELINE_ITEMS} animated />));
    expect(
      screen.getByRole('button', { name: /reproduzir linha do tempo/i }),
    ).toBeInTheDocument();
  });

  it('SplitCompareView renderiza dois painéis rotulados lado a lado', () => {
    render(
      providers(
        <SplitCompareView
          paneA={{ title: 'MapBiomas', selector: <button type="button">Sel A</button>, chart: <div>Chart A</div> }}
          paneB={{ title: 'TerraClass', selector: <button type="button">Sel B</button>, chart: <div>Chart B</div> }}
        />,
      ),
    );
    expect(screen.getByRole('region', { name: 'MapBiomas' })).toBeInTheDocument();
    expect(screen.getByRole('region', { name: 'TerraClass' })).toBeInTheDocument();
    expect(screen.getByText('Chart A')).toBeInTheDocument();
    expect(screen.getByText('Chart B')).toBeInTheDocument();
  });

  it('SplitCompareTab alterna modo iniciativa/ano sem quebrar', () => {
    seedTwo();
    render(providers(<SplitCompareTab />));
    expect(screen.getByRole('button', { name: /por iniciativa/i })).toHaveAttribute(
      'aria-pressed',
      'true',
    );
    fireEvent.click(screen.getByRole('button', { name: /por ano/i }));
    expect(screen.getByRole('button', { name: /por ano/i })).toHaveAttribute(
      'aria-pressed',
      'true',
    );
    expect(screen.getAllByRole('img').length).toBeGreaterThanOrEqual(2);
  });

  it('SplitCompareTab em EN traduz o toggle', () => {
    seedTwo();
    window.localStorage.setItem(LANGUAGE_STORAGE_KEY, 'en');
    render(providers(<SplitCompareTab />));
    expect(screen.getByRole('button', { name: /by initiative/i })).toBeInTheDocument();
  });
});
