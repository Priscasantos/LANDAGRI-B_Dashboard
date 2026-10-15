import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import DataTable from '../../components/ui/DataTable';
import { LanguageProvider } from '../../i18n/LanguageContext';

const columns = [
  { key: 'name', label: 'Nome' },
  { key: 'value', label: 'Valor' },
];

const data = [
  { name: 'Zulu', value: 3 },
  { name: 'Alpha', value: 1 },
  { name: 'Miolo', value: 2 },
];

describe('DataTable locale (Fase 2 qualidade)', () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.lang = 'pt-BR';
  });
  it('sorts strings with the active locale (accent-aware)', () => {
    document.documentElement.lang = 'pt-BR';
    const rows = [
      { name: 'Água', value: 1 },
      { name: 'Abacaxi', value: 2 },
      { name: 'Zebra', value: 3 },
    ];
    render(<DataTable columns={columns} data={rows} />);
    fireEvent.click(screen.getByRole('columnheader', { name: 'Nome' }));
    const cells = screen.getAllByRole('cell');
    const names = cells.filter((_, i) => i % 2 === 0).map((c) => c.textContent);
    const expected = [...rows]
      .map((r) => r.name)
      .sort((a, b) => a.localeCompare(b, 'pt-BR'));
    expect(names).toEqual(expected);
  });

  it('translates pagination controls (PT default)', () => {
    document.documentElement.lang = 'pt-BR';
    render(<DataTable columns={columns} data={data} pageSize={2} />);
    expect(screen.getByRole('button', { name: /anterior/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /próxima/i })).toBeInTheDocument();
    expect(screen.getByText(/registro/i)).toBeInTheDocument();
  });

  it('translates pagination controls to EN inside the provider', () => {
    localStorage.setItem('landagri-lang', 'en');
    render(
      <LanguageProvider>
        <DataTable columns={columns} data={data} pageSize={2} />
      </LanguageProvider>,
    );
    expect(screen.getByRole('button', { name: /^previous$/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /^next$/i })).toBeInTheDocument();
    expect(screen.getByText(/records/i)).toBeInTheDocument();
  });
});
