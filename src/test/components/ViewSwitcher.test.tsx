import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ViewSwitcher from '../../components/ui/ViewSwitcher';

const OPTIONS = [
  { id: 'pairwise', label: 'Par a par' },
  { id: 'split', label: 'Lado a lado' },
  { id: 'table', label: 'Tabela' },
];

describe('ViewSwitcher (Fase 3 ToggleGroup + Select)', () => {
  it('renders a radiogroup with aria-checked synced to value', () => {
    render(<ViewSwitcher label="Escolher visão" options={OPTIONS} value="split" onChange={() => undefined} />);
    const group = screen.getByRole('radiogroup', { name: 'Escolher visão' });
    expect(group).toBeDefined();
    expect(screen.getByRole('radio', { name: 'Lado a lado' })).toHaveAttribute('aria-checked', 'true');
    expect(screen.getByRole('radio', { name: 'Par a par' })).toHaveAttribute('aria-checked', 'false');
  });

  it('notifies onChange when a radio option is activated', () => {
    const onChange = vi.fn();
    render(<ViewSwitcher label="Escolher visão" options={OPTIONS} value="pairwise" onChange={onChange} />);
    fireEvent.click(screen.getByRole('radio', { name: 'Tabela' }));
    expect(onChange).toHaveBeenCalledWith('table');
  });

  it('supports arrow-key navigation between options', () => {
    const onChange = vi.fn();
    render(<ViewSwitcher label="Escolher visão" options={OPTIONS} value="pairwise" onChange={onChange} />);
    fireEvent.keyDown(screen.getByRole('radio', { name: 'Par a par' }), { key: 'ArrowRight' });
    expect(onChange).toHaveBeenCalledWith('split');
  });

  it('renders a native select synced to the same value', () => {
    const onChange = vi.fn();
    render(<ViewSwitcher label="Escolher visão" options={OPTIONS} value="table" onChange={onChange} />);
    const select = screen.getByRole('combobox', { name: 'Escolher visão' }) as HTMLSelectElement;
    expect(select.value).toBe('table');
    fireEvent.change(select, { target: { value: 'split' } });
    expect(onChange).toHaveBeenCalledWith('split');
  });
});
