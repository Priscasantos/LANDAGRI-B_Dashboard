import { describe, it, expect, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ThemeProvider } from '../../components/theme-provider';
import { LanguageProvider } from '../../i18n/LanguageContext';
import { LANGUAGE_STORAGE_KEY } from '../../i18n/types';
import ConabMappingTab from '../../components/agricultural-analysis/AgricultureOverview/ConabMappingTab';

function renderWithProviders(ui: React.ReactElement): void {
  render(
    <LanguageProvider>
      <ThemeProvider>{ui}</ThemeProvider>
    </LanguageProvider>,
  );
}

afterEach(() => {
  localStorage.removeItem(LANGUAGE_STORAGE_KEY);
});

describe('ConabMappingTab temporal coverage evolution', () => {
  it('renders integer-year evolution heading + translated chart (pt-BR)', async () => {
    localStorage.setItem(LANGUAGE_STORAGE_KEY, 'pt-BR');
    renderWithProviders(<ConabMappingTab />);
    expect(
      await screen.findByRole('heading', { name: /evolução da cobertura temporal/i }),
    ).toBeInTheDocument();
    expect(
      await screen.findByRole('img', { name: /mapeamento ativo/i }),
    ).toBeInTheDocument();
  });

  it('follows the i18n toggle (EN heading + caption)', async () => {
    localStorage.setItem(LANGUAGE_STORAGE_KEY, 'en');
    renderWithProviders(<ConabMappingTab />);
    expect(
      await screen.findByRole('heading', { name: /temporal coverage evolution/i }),
    ).toBeInTheDocument();
    expect(
      await screen.findByRole('img', { name: /active mapping/i }),
    ).toBeInTheDocument();
  });
});
