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

/** Classe aplicada ao wrapper do mapa quando `.dark` está ativo. */
export const DARK_TILE_FILTER_CLASS = 'leaflet-tiles-dark';

export function baseTiles(): TileSpec {
  return {
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  };
}
