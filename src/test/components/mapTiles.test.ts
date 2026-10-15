import { describe, it, expect } from 'vitest';
import { baseTiles, DARK_TILE_FILTER_CLASS } from '../../components/overview/mapTiles';
import { translate } from '../../i18n';

describe('mapTiles (Fase 3)', () => {
  it('serves OSM tiles with attribution', () => {
    const spec = baseTiles();
    expect(spec.url).toContain('tile.openstreetmap.org');
    expect(spec.attribution).toContain('OpenStreetMap');
  });

  it('exposes a dark filter class for the tile pane', () => {
    expect(DARK_TILE_FILTER_CLASS).toBe('leaflet-tiles-dark');
  });
});

describe('map namespace (Fase 3)', () => {
  it('exposes translated fallback + legend keys', () => {
    expect(translate('pt-BR', 'map', 'noCoords')).toContain('Sem coordenadas');
    expect(translate('en', 'map', 'noCoords')).toContain('No coordinates');
    expect(translate('pt-BR', 'map', 'title')).toBe('Mapa das Iniciativas');
    expect(translate('en', 'map', 'title')).toBe('Initiatives Map');
  });
});
