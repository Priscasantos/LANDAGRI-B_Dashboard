import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

vi.mock('recharts', async (importOriginal) => {
  const actual = await importOriginal<typeof import('recharts')>();
  const React = await import('react');
  return {
    ...actual,
    ResponsiveContainer: ({ children }: { children: React.ReactElement }) =>
      React.cloneElement(
        children as React.ReactElement<{ width?: number; height?: number }>,
        { width: 600, height: 320 },
      ),
  };
});

import PredictivePage from '../../pages/PredictivePage';
import AboutPage from '../../pages/AboutPage';
import { ThemeProvider } from '../../components/theme-provider';

describe('PredictivePage (simulador 2025→2035)', () => {
  it('exposes labelled sliders operable by keyboard', () => {
    render(
      <MemoryRouter>
        <ThemeProvider>
          <PredictivePage />
        </ThemeProvider>
      </MemoryRouter>,
    );
    const reforestation = screen.getByLabelText(/reflorestamento/i);
    reforestation.focus();
    expect(reforestation).toHaveFocus();
    fireEvent.change(reforestation, { target: { value: '2.5' } });
    expect(reforestation).toHaveAttribute('aria-valuetext', '+2.5% por ano');
    expect(screen.getByLabelText(/expansão agrícola/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/adoção sustentável/i)).toBeInTheDocument();
  });

  it('reset button restores defaults', () => {
    render(
      <MemoryRouter>
        <ThemeProvider>
          <PredictivePage />
        </ThemeProvider>
      </MemoryRouter>,
    );
    const reforestation = screen.getByLabelText(/reflorestamento/i) as HTMLInputElement;
    fireEvent.change(reforestation, { target: { value: '4' } });
    expect(reforestation.value).toBe('4');
    fireEvent.click(screen.getByRole('button', { name: /resetar padrão/i }));
    expect((screen.getByLabelText(/reflorestamento/i) as HTMLInputElement).value).not.toBe('4');
  });
});

describe('AboutPage (matches legacy Streamlit about.py)', () => {
  it('renders data sources, citation and contact without export/metadata blocks', () => {
    render(
      <MemoryRouter>
        <AboutPage />
      </MemoryRouter>,
    );
    expect(screen.getByText('Fontes de Dados e Referências')).toBeInTheDocument();
    expect(screen.getByText('Citação')).toBeInTheDocument();
    expect(
      screen.getByRole('link', { name: /priscilla\.santos@inpe\.br/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('link', { name: /github\.com\/landagri-b/i }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole('button', { name: /exportar dados em/i }),
    ).not.toBeInTheDocument();
    expect(screen.queryByText(/metadados técnicos/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/bibtex/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/researchgate/i)).not.toBeInTheDocument();
  });
});
