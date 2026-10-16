import { describe, it, expect } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import { ThemeProvider } from '../../components/theme-provider';
import { LanguageProvider } from '../../i18n/LanguageContext';
import { LANGUAGE_STORAGE_KEY } from '../../i18n/types';
import AgricultureAvailabilityPage from '../../components/agricultural-analysis/AgricultureAvailability/AgricultureAvailabilityPage';
import { isNationalAggregateUf } from '../../lib/nationalAggregates';

function renderPage(): void {
  localStorage.setItem(LANGUAGE_STORAGE_KEY, 'pt-BR');
  render(
    <LanguageProvider>
      <ThemeProvider>
        <AgricultureAvailabilityPage />
      </ThemeProvider>
    </LanguageProvider>,
  );
  localStorage.removeItem(LANGUAGE_STORAGE_KEY);
}

describe('AgricultureAvailabilityPage exclui agregado BR da visão por estado (reversível)', () => {
  it('não conta o agregado nacional "BR" no KPI Estados/Disp.', async () => {
    renderPage();
    const kpi = await screen.findByRole('group', { name: 'Estados/Disp.' });
    // conab_availability.json tem 16 UFs + 1 linha agregada BR → visão por estado mostra 16.
    expect(within(kpi).getByText('16')).toBeInTheDocument();
  });

  it('isNationalAggregateUf detecta BR/Brazil/Brasil e preserva UFs reais', () => {
    expect(isNationalAggregateUf('BR')).toBe(true);
    expect(isNationalAggregateUf(' br ')).toBe(true);
    expect(isNationalAggregateUf('Brazil')).toBe(true);
    expect(isNationalAggregateUf('Brasil')).toBe(true);
    expect(isNationalAggregateUf('GO')).toBe(false);
    expect(isNationalAggregateUf('SP')).toBe(false);
    expect(isNationalAggregateUf('')).toBe(false);
  });
});
