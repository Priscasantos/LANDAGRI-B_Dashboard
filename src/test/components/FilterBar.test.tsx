import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import FilterBar from '../../components/ui/FilterBar';

const OPTIONS = [
  { value: 'overview', label: 'Panorama', to: '/agricultural-analysis/overview' },
  { value: 'crop-calendar', label: 'Calendário', to: '/agricultural-analysis/crop-calendar' },
  { value: 'availability', label: 'Disponibilidade', to: '/agricultural-analysis/availability' },
];

function renderBar(value = 'overview') {
  return render(
    <MemoryRouter>
      <FilterBar label="Filtrar visão agrícola" options={OPTIONS} value={value} />
    </MemoryRouter>,
  );
}

describe('FilterBar (Fase 3 route-backed filter)', () => {
  it('preserves the deep-link `to=` on every filter', () => {
    renderBar();
    for (const opt of OPTIONS) {
      const link = screen.getByRole('link', { name: opt.label });
      expect(link.getAttribute('href')).toBe(opt.to);
    }
  });

  it('marks only the active filter with aria-current="page"', () => {
    renderBar('crop-calendar');
    expect(screen.getByRole('link', { name: 'Calendário' })).toHaveAttribute('aria-current', 'page');
    expect(screen.getByRole('link', { name: 'Panorama' })).not.toHaveAttribute('aria-current');
  });

  it('exposes a toolbar landmark with an accessible label', () => {
    renderBar();
    expect(screen.getByRole('toolbar', { name: 'Filtrar visão agrícola' })).toBeDefined();
  });
});
