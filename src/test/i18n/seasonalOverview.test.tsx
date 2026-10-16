import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { pt } from '../../i18n/dictionaries/pt';
import { en } from '../../i18n/dictionaries/en';
import { LanguageProvider } from '../../i18n/LanguageContext';
import { ThemeProvider } from '../../components/theme-provider';
import SeasonalOverviewTab from '../../components/agricultural-analysis/CropCalendar/SeasonalOverviewTab';

import { LANGUAGE_STORAGE_KEY } from '../../i18n/types';

beforeEach(() => {
  window.localStorage.setItem(LANGUAGE_STORAGE_KEY, 'pt-BR');
  document.documentElement.lang = 'pt-BR';
});

type AgDict = Record<string, string | undefined>;

const agPt = pt.agricultural as unknown as AgDict;
const agEn = en.agricultural as unknown as AgDict;

const NEW_KEYS = [
  'breakdownNote',
  'emptyGroupNoData',
  'hSeasonalByCrop',
  'hSeasonalByRegion',
  'viewOverview',
  'viewByCrop',
  'viewByRegion',
] as const;

function renderTab(crops: string[], regions: string[]): void {
  render(
    <LanguageProvider>
      <ThemeProvider>
        <SeasonalOverviewTab selectedCrops={crops} selectedRegions={regions} />
      </ThemeProvider>
    </LanguageProvider>,
  );
}

describe('SeasonalOverviewTab por cultura / por região', () => {
  it('chaves novas existem espelhadas em PT/EN', () => {
    for (const key of NEW_KEYS) {
      expect(typeof agPt[key]).toBe('string');
      expect(typeof agEn[key]).toBe('string');
    }
  });

  it('três visões com rótulos curtos e distintos (PT)', () => {
    expect(agPt.viewOverview).toBe('Geral');
    expect(agPt.viewByCrop).toBe('Por cultura');
    expect(agPt.viewByRegion).toBe('Por região');
    expect(new Set([agPt.viewOverview, agPt.viewByCrop, agPt.viewByRegion]).size).toBe(3);
  });

  it('três visões com rótulos curtos e distintos (EN)', () => {
    expect(agEn.viewOverview).toBe('Overview');
    expect(agEn.viewByCrop).toBe('By crop');
    expect(agEn.viewByRegion).toBe('By region');
    expect(new Set([agEn.viewOverview, agEn.viewByCrop, agEn.viewByRegion]).size).toBe(3);
  });

  it('visão geral preservada como padrão; sub-abas navegam', () => {
    renderTab(['Soybean'], ['South']);
    expect(screen.getByRole('tab', { name: 'Geral' })).toHaveAttribute('aria-selected', 'true');
    expect(screen.getByRole('heading', { name: 'Panorama Sazonal' })).toBeInTheDocument();

    fireEvent.click(screen.getByRole('tab', { name: 'Por cultura' }));
    expect(screen.getByRole('heading', { name: 'Sazonalidade por Cultura' })).toBeInTheDocument();

    fireEvent.click(screen.getByRole('tab', { name: 'Por região' }));
    expect(screen.getByRole('heading', { name: 'Sazonalidade por Região' })).toBeInTheDocument();
  });

  it('empty state honesto sem filtros (visão atual intacta)', () => {
    renderTab([], []);
    expect(screen.getByRole('status')).toHaveTextContent('Sem dados para os filtros selecionados.');

    fireEvent.click(screen.getByRole('tab', { name: 'Por cultura' }));
    expect(screen.getByRole('status')).toHaveTextContent('Sem dados para os filtros selecionados.');
  });
});
