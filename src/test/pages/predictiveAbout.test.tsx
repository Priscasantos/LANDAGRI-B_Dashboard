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

describe('PredictivePage (simulador 2025→2035)', () => {
  it('exposes labelled sliders operable by keyboard', () => {
    render(
      <MemoryRouter>
        <PredictivePage />
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
        <PredictivePage />
      </MemoryRouter>,
    );
    const reforestation = screen.getByLabelText(/reflorestamento/i) as HTMLInputElement;
    fireEvent.change(reforestation, { target: { value: '4' } });
    expect(reforestation.value).toBe('4');
    fireEvent.click(screen.getByRole('button', { name: /resetar padrão/i }));
    expect((screen.getByLabelText(/reflorestamento/i) as HTMLInputElement).value).not.toBe('4');
  });
});

describe('AboutPage (exports preserved)', () => {
  it('keeps CSV/JSON export buttons with accessible names', () => {
    render(
      <MemoryRouter>
        <AboutPage />
      </MemoryRouter>,
    );
    expect(screen.getByRole('button', { name: /exportar dados em csv/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /exportar dados em json/i })).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /copiar citação bibtex/i }),
    ).toBeInTheDocument();
  });
});
