import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import LeafletMapInner from '../../components/overview/LeafletMapInner';

describe('LeafletMapInner (Expansão #3: TerraBrasilis WMS)', () => {
  it('renders a layers control with base + overlay toggles', () => {
    render(<LeafletMapInner />);
    expect(document.querySelector('.leaflet-control-layers')).not.toBeNull();
  });

  it('shows the noCoords fallback pill while no overlay is active', () => {
    render(<LeafletMapInner />);
    expect(screen.getByRole('status')).toHaveTextContent(/Sem coordenadas|No coordinates/);
  });

  it('keeps the Verde Agro base legend with an accessible title', () => {
    render(<LeafletMapInner />);
    expect(screen.getByLabelText(/Legenda|Legend/)).toBeInTheDocument();
  });
});
