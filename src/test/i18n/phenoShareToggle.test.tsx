import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { pt } from '../../i18n/dictionaries/pt';
import { en } from '../../i18n/dictionaries/en';
import { LanguageProvider } from '../../i18n/LanguageContext';
import { ThemeProvider } from '../../components/theme-provider';
import ShareModeToggle from '../../components/agricultural-analysis/CropCalendar/ShareModeToggle';
import PhenologyLegend from '../../components/agricultural-analysis/CropCalendar/PhenologyLegend';
import { LANGUAGE_STORAGE_KEY } from '../../i18n/types';

beforeEach(() => {
  window.localStorage.setItem(LANGUAGE_STORAGE_KEY, 'pt-BR');
  document.documentElement.lang = 'pt-BR';
});

function renderWithProviders(ui: React.ReactElement): void {
  render(
    <LanguageProvider>
      <ThemeProvider>{ui}</ThemeProvider>
    </LanguageProvider>,
  );
}

describe('ShareModeToggle + PhenologyLegend (Gaia)', () => {
  it('dicionários PT/EN cobrem as chaves novas', () => {
    const keys = [
      'shareModeLabel',
      'shareModeAreaUnavailable',
      'legendBoth',
      'legendBothNote',
      'legendCodingNote',
      'seasonBadge',
      'ganttLanesNote',
    ];
    for (const key of keys) {
      expect(pt.agricultural[key], `pt.${key}`).toBeTruthy();
      expect(en.agricultural[key], `en.${key}`).toBeTruthy();
    }
  });

  it('toggle mostra % UFs ativo e % área desabilitada com nota quando sem área por UF', () => {
    const onChange = vi.fn();
    renderWithProviders(<ShareModeToggle mode="uf" hasArea={false} onChange={onChange} />);
    const group = screen.getByRole('radiogroup');
    expect(group).toBeInTheDocument();
    const area = screen.getByRole('radio', { name: /área/i });
    expect(area).toHaveAttribute('aria-checked', 'false');
    expect(area).toHaveAttribute('aria-disabled', 'true');
    expect(screen.getByText(/sem área por UF/i)).toBeInTheDocument();
    fireEvent.click(area);
    expect(onChange).not.toHaveBeenCalled();
  });

  it('toggle permite alternar quando há área por UF', () => {
    const onChange = vi.fn();
    renderWithProviders(<ShareModeToggle mode="uf" hasArea onChange={onChange} />);
    const area = screen.getByRole('radio', { name: /área/i });
    fireEvent.click(area);
    expect(onChange).toHaveBeenCalledWith('area');
  });

  it('legenda fixa mostra P, H e PH com codificação documentada', () => {
    renderWithProviders(<PhenologyLegend />);
    expect(screen.getByText('Plantio')).toBeInTheDocument();
    expect(screen.getByText('Colheita')).toBeInTheDocument();
    expect(screen.getByTitle(/2º ciclo/i)).toBeInTheDocument();
  });
});
