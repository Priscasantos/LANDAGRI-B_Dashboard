import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import OverviewMap from '../../components/overview/OverviewMap';

describe('OverviewMap (Fase 2: leaflet island, lazy)', () => {
  it('renders a loading fallback with an accessible label while leaflet loads', () => {
    render(<OverviewMap />);
    expect(screen.getByRole('status', { name: /carregando mapa/i })).toBeInTheDocument();
  });
});
