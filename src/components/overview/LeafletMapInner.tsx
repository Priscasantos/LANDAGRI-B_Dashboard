import type { ReactElement } from 'react';
import { MapContainer, TileLayer } from 'react-leaflet';

/**
 * LeafletMapInner — leaflet island internals (Fase 2).
 * Imported ONLY via `lazy()` in `OverviewMap`, so bundlers keep
 * `leaflet`/`react-leaflet` in the isolated `leaflet` chunk
 * (see `manualChunks` in `vite.config.ts`). Never import directly.
 */
export default function LeafletMapInner(): ReactElement {
  return (
    <div
      role="img"
      aria-label="Mapa das iniciativas LANDAGRI-B (Brasil)"
      className="w-full overflow-hidden rounded-xl border border-border h-[420px] md:h-[480px]"
    >
      <MapContainer
        center={[-14.235, -51.925]}
        zoom={4}
        scrollWheelZoom={false}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
      </MapContainer>
      <p className="sr-only">
        Mapa centrado no Brasil. Camada de cobertura das iniciativas carregada sob demanda.
      </p>
    </div>
  );
}
