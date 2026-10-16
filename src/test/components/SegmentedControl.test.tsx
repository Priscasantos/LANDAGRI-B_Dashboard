import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import SegmentedControl from '../../components/ui/SegmentedControl';

const OPTIONS = [
  { value: 'temporal', label: 'Evolução', to: '/initiative-analysis/temporal' },
  { value: 'comparative', label: 'Comparar', to: '/initiative-analysis/comparative' },
  { value: 'detailed', label: 'Ficha', to: '/initiative-analysis/detailed' },
];

function renderControl(value = 'temporal') {
  return render(
    <MemoryRouter>
      <SegmentedControl label="Seções da análise" options={OPTIONS} value={value} />
    </MemoryRouter>,
  );
}

describe('SegmentedControl (Fase 3 route-backed tabs)', () => {
  it('preserves the deep-link `to=` on every option', () => {
    renderControl();
    for (const opt of OPTIONS) {
      const link = screen.getByRole('link', { name: opt.label });
      expect(link.getAttribute('href')).toBe(opt.to);
    }
  });

  it('marks only the active option with aria-current="page"', () => {
    renderControl('comparative');
    expect(screen.getByRole('link', { name: 'Comparar' })).toHaveAttribute('aria-current', 'page');
    expect(screen.getByRole('link', { name: 'Evolução' })).not.toHaveAttribute('aria-current');
    expect(screen.getByRole('link', { name: 'Ficha' })).not.toHaveAttribute('aria-current');
  });

  it('exposes an accessible group label', () => {
    renderControl();
    expect(screen.getByRole('navigation', { name: 'Seções da análise' })).toBeDefined();
  });
});
