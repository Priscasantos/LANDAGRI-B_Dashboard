/**
 * Mapa base (Fase 3): OSM em ambos os temas.
 *
 * CARTO `dark_matter` foi avaliado e descartado com evidência: sem API key
 * os tiles retornam placeholder "API KEY REQUIRED" (carto.com/basemaps/apikey).
 * No `.dark`, o tile pane OSM recebe filtro CSS (inversão + hue-rotate),
 * técnica padrão sem novo provedor/atribuição. Reversível: trocar `url`
 * aqui + remover a regra `.leaflet-tiles-dark` em `src/index.css`.
 */
export interface TileSpec {
  url: string;
  attribution: string;
}

/** Camada base selecionável no controle de camadas (uma é a padrão). */
export interface BaseLayerSpec extends TileSpec {
  key: 'osm' | 'carto';
  isDefault: boolean;
}

/**
 * Overlay WMS do TerraBrasilis (INPE) para `L.tileLayer.wms` /
 * `<WMSTileLayer>` do react-leaflet. `layers` usa o par
 * `workspace:layer` do GeoServer.
 */
export interface WmsOverlaySpec {
  key: 'prodes' | 'deter';
  url: string;
  layers: string;
  format: 'image/png';
  transparent: true;
  version: '1.1.1';
  opacity: number;
  attribution: string;
}

/** Endpoint OWS global do GeoServer TerraBrasilis (vale p/ todos os workspaces). */
export const TERRABRASILIS_WMS_URL = 'https://terrabrasilis.dpi.inpe.br/geoserver/ows';

export const TERRABRASILIS_ATTRIBUTION =
  'Camadas: <a href="https://terrabrasilis.dpi.inpe.br/">INPE/TerraBrasilis</a> (PRODES/DETER)';

/**
 * PRODES Amazônia (taxa anual de desmatamento) + DETER Amazônia (alertas).
 * Nomes seguem a convenção pública `workspace:layer_AAAA` do GeoServer
 * TerraBrasilis — confirmar via GetCapabilities
 * (`{url}?service=WMS&version=1.1.0&request=GetCapabilities`) e ajustar o
 * ano quando um novo PRODES for publicado. Anos já publicados permanecem
 * disponíveis, então o pin não quebra da noite para o dia; se o WMS cair
 * ou a camada sumir, o mapa cai para o fallback (`wmsUnavailable`) sem
 * quebrar a base. Reversível: remover `terrabrasilisOverlays()` + usos.
 */
export function terrabrasilisOverlays(): WmsOverlaySpec[] {
  return [
    {
      key: 'prodes',
      url: TERRABRASILIS_WMS_URL,
      layers: 'prodes-amazonia:prodes_amazonia_2024',
      format: 'image/png',
      transparent: true,
      version: '1.1.1',
      opacity: 0.75,
      attribution: TERRABRASILIS_ATTRIBUTION,
    },
    {
      key: 'deter',
      url: TERRABRASILIS_WMS_URL,
      layers: 'deter-amazonia:deter_amazonia_2024',
      format: 'image/png',
      transparent: true,
      version: '1.1.1',
      opacity: 0.75,
      attribution: TERRABRASILIS_ATTRIBUTION,
    },
  ];
}

/** Bases do controle de camadas: OSM padrão + CARTO claro alternativo. */
export function baseLayers(): BaseLayerSpec[] {
  return [
    {
      key: 'osm',
      isDefault: true,
      url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    },
    {
      key: 'carto',
      isDefault: false,
      url: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
    },
  ];
}

/** Classe aplicada ao wrapper do mapa quando `.dark` está ativo. */
export const DARK_TILE_FILTER_CLASS = 'leaflet-tiles-dark';

export function baseTiles(): TileSpec {
  return {
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  };
}
