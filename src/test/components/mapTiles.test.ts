import { describe, it, expect } from 'vitest';
import {
  baseTiles,
  baseLayers,
  terrabrasilisOverlays,
  TERRABRASILIS_WMS_URL,
  DARK_TILE_FILTER_CLASS,
} from '../../components/overview/mapTiles';
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

  it('exposes translated TerraBrasilis layer + fallback keys (Expansão #3)', () => {
    expect(translate('pt-BR', 'map', 'overlayProdes')).toContain('PRODES');
    expect(translate('en', 'map', 'overlayProdes')).toContain('PRODES');
    expect(translate('pt-BR', 'map', 'overlayDeter')).toContain('DETER');
    expect(translate('en', 'map', 'overlayDeter')).toContain('DETER');
    expect(translate('pt-BR', 'map', 'baseOsm')).toContain('OpenStreetMap');
    expect(translate('en', 'map', 'baseCarto')).toContain('CARTO');
    expect(translate('pt-BR', 'map', 'wmsUnavailable')).toContain('indisponível');
    expect(translate('en', 'map', 'wmsUnavailable')).toContain('unavailable');
    expect(translate('pt-BR', 'map', 'activeLayers')).toContain('TerraBrasilis');
    expect(translate('en', 'map', 'activeLayers')).toContain('TerraBrasilis');
  });
});

describe('mapTiles bases (Expansão #3)', () => {
  it('exposes OSM default + CARTO alternate base layers', () => {
    const layers = baseLayers();
    expect(layers).toHaveLength(2);
    expect(layers[0]?.url).toContain('tile.openstreetmap.org');
    expect(layers[1]?.url).toContain('basemaps.cartocdn.com');
    expect(layers.filter((l) => l.isDefault)).toHaveLength(1);
    expect(layers[0]?.isDefault).toBe(true);
  });
});

describe('TerraBrasilis WMS overlays (Expansão #3)', () => {
  it('points at the INPE GeoServer OWS endpoint', () => {
    expect(TERRABRASILIS_WMS_URL).toBe(
      'https://terrabrasilis.dpi.inpe.br/geoserver/ows',
    );
  });

  it('exposes PRODES annual + DETER alerts overlays with INPE attribution', () => {
    const overlays = terrabrasilisOverlays();
    expect(overlays).toHaveLength(2);
    const keys = overlays.map((o) => o.key);
    expect(keys).toEqual(['prodes', 'deter']);
    for (const overlay of overlays) {
      expect(overlay.url).toBe(TERRABRASILIS_WMS_URL);
      expect(overlay.layers).toContain(':');
      expect(overlay.format).toBe('image/png');
      expect(overlay.transparent).toBe(true);
      expect(overlay.attribution).toContain('INPE');
    }
    expect(overlays[0]?.layers).toContain('prodes-amazonia');
    expect(overlays[1]?.layers).toContain('deter-amazonia');
  });
});
