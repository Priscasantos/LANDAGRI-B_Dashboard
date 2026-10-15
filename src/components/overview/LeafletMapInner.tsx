import { useEffect, useRef, useState, type ReactElement } from 'react';
import { MapContainer, TileLayer } from 'react-leaflet';
import type { Map as LeafletMap } from 'leaflet';
import { MousePointer2 } from 'lucide-react';
import { useT } from '../../i18n/LanguageContext';
import { baseTiles, DARK_TILE_FILTER_CLASS } from './mapTiles';

/**
 * LeafletMapInner — leaflet island internals (Fase 3).
 * Imported ONLY via `lazy()` in `OverviewMap`, so bundlers keep
 * `leaflet`/`react-leaflet` in the isolated `leaflet` chunk
 * (see `manualChunks` in `vite.config.ts`). Never import directly.
 *
 * Dados: nenhum JSON do pipeline traz lat/lng (hermes não acionado —
 * sem inventar coords). Fallback Fase 3: mapa base do Brasil +
 * mensagem `map:noCoords` traduzida. Quando houver coordenadas,
 * plugar CircleMarkers aqui (markercluster só acima de 100 pts).
 */

const BRAZIL_CENTER: [number, number] = [-14.235, -51.925];

function readIsDark(): boolean {
  if (typeof document === 'undefined') return false;
  return document.documentElement.classList.contains('dark');
}

export default function LeafletMapInner(): ReactElement {
  const { t } = useT('map');
  const mapRef = useRef<LeafletMap | null>(null);
  const [isDark, setIsDark] = useState<boolean>(readIsDark);
  const [scrollEnabled, setScrollEnabled] = useState<boolean>(false);

  // Acompanha o toggle light/dark (classe `.dark` na raiz).
  useEffect(() => {
    const root = document.documentElement;
    const observer = new MutationObserver(() => setIsDark(readIsDark()));
    observer.observe(root, { attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);

  const tiles = baseTiles();

  const toggleScroll = (): void => {
    const map = mapRef.current;
    setScrollEnabled((prev) => {
      const next = !prev;
      if (map) {
        if (next) map.scrollWheelZoom.enable();
        else map.scrollWheelZoom.disable();
      }
      return next;
    });
  };

  return (
    <div
      role="application"
      aria-label={t('mapAria')}
      className={`relative w-full min-w-0 overflow-hidden rounded-xl border border-border z-0 h-[380px] sm:h-[440px] lg:h-[520px] ${isDark ? DARK_TILE_FILTER_CLASS : ''}`}
    >
      <MapContainer
        ref={mapRef}
        center={BRAZIL_CENTER}
        zoom={4}
        scrollWheelZoom={false}
        keyboard
        style={{ height: '100%', width: '100%', zIndex: 0 }}
      >
        <TileLayer attribution={tiles.attribution} url={tiles.url} />
      </MapContainer>

      {/* Fallback Fase 3: sem coords — aviso traduzido, sem pontos inventados */}
      <p
        role="status"
        className="absolute left-1/2 top-3 z-[500] w-max max-w-[calc(100%-2rem)] -translate-x-1/2 rounded-full border border-border bg-surface/95 px-3 py-1.5 text-center text-xs text-fg-secondary shadow-sm"
      >
        {t('noCoords')}
      </p>

      {/* Controle de scroll-zoom (a11y: mapa não rouba a roda por padrão) */}
      <button
        type="button"
        onClick={toggleScroll}
        aria-pressed={scrollEnabled}
        className="absolute right-3 top-3 z-[500] inline-flex cursor-pointer items-center gap-1.5 rounded-lg border border-border bg-surface/95 px-2.5 py-1.5 text-xs font-semibold text-fg-secondary shadow-sm transition-colors hover:text-primary focus-visible:outline-2 focus-visible:outline-primary"
      >
        <MousePointer2 size={13} aria-hidden="true" />
        {scrollEnabled ? t('disableScroll') : t('enableScroll')}
      </button>

      {/* Legenda Verde Agro */}
      <div
        aria-label={t('legendTitle')}
        className="absolute bottom-3 right-3 z-[500] flex items-center gap-2 rounded-lg border border-border bg-surface/95 px-2.5 py-1.5 text-xs text-fg-secondary shadow-sm"
      >
        <span
          aria-hidden="true"
          className="size-2.5 shrink-0 rounded-full"
          style={{ backgroundColor: 'var(--color-primary)' }}
        />
        {t('legendBase')}
      </div>

      {/* Equivalente textual para leitores de tela */}
      <p className="sr-only">{t('srDescription')}</p>
      <ul className="sr-only">
        <li>{t('noCoords')}</li>
      </ul>
    </div>
  );
}
