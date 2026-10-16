import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { translate } from '../../i18n';
import { LanguageProvider } from '../../i18n/LanguageContext';
import { LANGUAGE_STORAGE_KEY } from '../../i18n/types';
import PredictivePage from '../../pages/PredictivePage';
import AboutPage from '../../pages/AboutPage';
import OverviewMap from '../../components/overview/OverviewMap';
import { ThemeProvider } from '../../components/theme-provider';

function renderEN(ui: React.ReactElement): void {
  window.localStorage.setItem(LANGUAGE_STORAGE_KEY, 'en');
  document.documentElement.lang = 'en';
  render(
    <LanguageProvider>
      <ThemeProvider>{ui}</ThemeProvider>
    </LanguageProvider>,
  );
}

beforeEach(() => {
  window.localStorage.clear();
  document.documentElement.lang = 'pt-BR';
});

describe('Fase 2b page bodies (RED→GREEN)', () => {
  it('exposes predictive body keys in both locales', () => {
    expect(translate('pt-BR', 'predictive', 'simulatorBadge')).toBe('Simulador de Cenários');
    expect(translate('en', 'predictive', 'simulatorBadge')).toBe('Scenario Simulator');
  });

  it('renders PredictivePage in English after toggle', () => {
    renderEN(
      <MemoryRouter>
        <PredictivePage />
      </MemoryRouter>,
    );
    expect(screen.getByRole('button', { name: /reset to defaults/i })).toBeInTheDocument();
    expect(screen.getByText(/scenario simulator/i)).toBeInTheDocument();
  });

  it('renders AboutPage sources section in English after toggle', () => {
    renderEN(
      <MemoryRouter>
        <AboutPage />
      </MemoryRouter>,
    );
    expect(screen.getByText('Data Sources and References')).toBeInTheDocument();
    expect(screen.getByText('Citation')).toBeInTheDocument();
    expect(
      screen.getAllByRole('link', { name: /santos et al\. \(2025\)/i }),
    ).toHaveLength(2);
    expect(
      screen.getByRole('link', { name: /priscilla\.santos@inpe\.br/i }),
    ).toBeInTheDocument();
    expect(screen.queryByText(/export data/i)).not.toBeInTheDocument();
  });

  it('renders the map section title in English after toggle', () => {
    renderEN(<OverviewMap />);
    expect(screen.getByText('Initiatives Map')).toBeInTheDocument();
  });
});
