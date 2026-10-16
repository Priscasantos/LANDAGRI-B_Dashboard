import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { pt } from '../../i18n/dictionaries/pt';
import { en } from '../../i18n/dictionaries/en';
import { LanguageProvider } from '../../i18n/LanguageContext';
import { ThemeProvider } from '../../components/theme-provider';
import ActivitiesTimelineTab from '../../components/agricultural-analysis/CropCalendar/ActivitiesTimelineTab';

import { LANGUAGE_STORAGE_KEY } from '../../i18n/types';

beforeEach(() => {
  window.localStorage.setItem(LANGUAGE_STORAGE_KEY, 'pt-BR');
  document.documentElement.lang = 'pt-BR';
});

type AgDict = Record<string, string | undefined>;

const agPt = pt.agricultural as unknown as AgDict;
const agEn = en.agricultural as unknown as AgDict;

describe('CropCalendar tab consolidation (mensal x sazonal, polar)', () => {
  it('polar tem rotulo unico curto nas duas linguas (sem duplicata distribuicao-polar)', () => {
    expect(agPt.tabPolar).toBe('Polar');
    expect(agEn.tabPolar).toBe('Polar');
    expect('hPolarSeasonality' in pt.agricultural).toBe(false);
    expect('hPolarSeasonality' in en.agricultural).toBe(false);
  });

  it('sub-abas da cronologia renderizam com os rotulos consolidados (ids/estado intactos)', () => {
    render(
      <LanguageProvider>
        <ThemeProvider>
          <ActivitiesTimelineTab selectedCrops={['Soybean']} selectedRegions={['South']} />
        </ThemeProvider>
      </LanguageProvider>,
    );
    expect(screen.getByRole('tab', { name: 'Evolução Mensal' })).toHaveAttribute('aria-selected', 'true');
    expect(screen.getByRole('tab', { name: 'Gantt' })).toHaveAttribute('aria-selected', 'false');
    expect(screen.getByRole('tab', { name: 'Polar' })).toHaveAttribute('aria-selected', 'false');
  });

  it('gantt mantem nome unico curto nas duas linguas', () => {
    expect(agPt.tabGantt).toBe('Gantt');
    expect(agEn.tabGantt).toBe('Gantt');
  });

  it('rotulos mensal x sazonal sao curtos e distintos (PT)', () => {
    const labels = [
      agPt.hMonthlySeasonality,
      agPt.hSeasonal,
      agPt.hMonthlyHeatmap,
      agPt.hIntensityByMonth,
      agPt.hMonthlyStacked,
    ];
    for (const label of labels) {
      expect(typeof label).toBe('string');
      expect(label!.length).toBeLessThanOrEqual(30);
    }
    expect(new Set(labels).size).toBe(labels.length);
  });

  it('rotulos mensal x sazonal sao curtos e distintos (EN)', () => {
    const labels = [
      agEn.hMonthlySeasonality,
      agEn.hSeasonal,
      agEn.hMonthlyHeatmap,
      agEn.hIntensityByMonth,
      agEn.hMonthlyStacked,
    ];
    for (const label of labels) {
      expect(typeof label).toBe('string');
      expect(label!.length).toBeLessThanOrEqual(30);
    }
    expect(new Set(labels).size).toBe(labels.length);
  });
});
