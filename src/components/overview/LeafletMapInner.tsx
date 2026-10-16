import { useEffect, useRef, useState, type ReactElement } from 'react';
import { LayersControl, MapContainer, TileLayer, WMSTileLayer, useMapEvents } from 'react-leaflet';
import type { LeafletEvent, Map as LeafletMap } from 'leaflet';
import { MousePointer2 } from 'lucide-react';
import { useT } from '../../i18n/LanguageContext';
import { baseLayers, terrabrasilisOverlays, DARK_TILE_FILTER_CLASS } from './mapTiles';

/**
 * LeafletMapInner — leaflet island internals (Fase 3 + Expansão #3).
 * Imported ONLY via `lazy()` in `OverviewMap`, so bundlers keep
 * `leaflet`/`react-leaflet` in the isolated `leaflet` chunk
 * (see `manualChunks` in `vite.config.ts`). Never import directly.
 *
 * Dados: nenhum JSON do pipeline traz lat/lng (hermes não acionado —
 * sem inventar coords). Fallback: mapa base do Brasil + mensagem
 * `map:noCoords` traduzida. Quando houver coordenadas,
 * plugar CircleMarkers aqui (markercluster só acima de 100 pts).
 *
 * Expansão #3 (reversível): overlays WMS do TerraBrasilis (INPE —
 * PRODES taxa anual + DETER alertas, Amazônia) via `L.tileLayer.wms`,
 * desligados por padrão. O endpoint OWS
 * (`https://terrabrasilis.dpi.inpe.br/geoserver/ows`) não respondeu à
 * tentativa de GetCapabilities a partir deste ambiente (timeout de rede),
 * então o componente assume degradação graciosa: qualquer `tileerror`
 * do WMS troca o aviso para `map:wmsUnavailable` e mantém o mapa base.
 * Reversão: remover `LayersControl` + `terrabrasilisOverlays()` e
 * voltar ao `<TileLayer>` único.
 */

const BRAZIL_CENTER: [number, number] = [-14.235, -51.925];

function readIsDark(): boolean {
  if (typeof document === 'undefined') return false;
  return document.documentElement.classList.contains('dark');
}

/** Nome da camada vindo do evento `overlayadd`/`overlayremove` do Leaflet. */
function overlayNameOf(event: LeafletEvent): string | null {
  const name = (event as unknown as { name?: unknown }).name;
  return typeof name === 'string' && name.length > 0 ? name : null;
}

/** Cor do chip da legenda para cada overlay (fallback estático). */
function overlayChipClass(name: string, prodesName: string, deterName: string): string {
  if (name === prodesName) return 'bg-red-700';
  if (name === deterName) return 'bg-amber-500';
  return 'bg-fg-muted';
}

/** Repassa overlayadd/overlayremove do Leaflet para o estado React (v5: sem `eventHandlers` no MapContainer). */
function OverlayTracker({
  onAdd,
  onRemove,
}: {
  onAdd: (event: LeafletEvent) => void;
  onRemove: (event: LeafletEvent) => void;
}): null {
  useMapEvents({
    overlayadd: onAdd,
    overlayremove: onRemove,
  });
  return null;
}

export default function LeafletMapInner(): ReactElement {
  const { t } = useT('map');
  const mapRef = useRef<LeafletMap | null>(null);
  const [isDark, setIsDark] = useState<boolean>(readIsDark);
  const [scrollEnabled, setScrollEnabled] = useState<boolean>(false);
  const [activeOverlays, setActiveOverlays] = useState<string[]>([]);
  const [wmsAvailable, setWmsAvailable] = useState<boolean>(true);

  // Acompanha o toggle light/dark (classe `.dark` na raiz).
  useEffect(() => {
    const root = document.documentElement;
    const observer = new MutationObserver(() => setIsDark(readIsDark()));
    observer.observe(root, { attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);

  const bases = baseLayers();
  const overlays = terrabrasilisOverlays();
  const prodesName = t('overlayProdes');
  const deterName = t('overlayDeter');
  const hasActiveOverlay = activeOverlays.length > 0;

  const handleOverlayAdd = (event: LeafletEvent): void => {
    const name = overlayNameOf(event);
    if (name === null) return;
    setActiveOverlays((prev) => (prev.includes(name) ? prev : [...prev, name]));
  };

  const handleOverlayRemove = (event: LeafletEvent): void => {
    const name = overlayNameOf(event);
    if (name === null) return;
    setActiveOverlays((prev) => prev.filter((item) => item !== name));
  };

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

  const statusText = !hasActiveOverlay
    ? t('noCoords')
    : !wmsAvailable
      ? t('wmsUnavailable')
      : t('activeLayers');

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
        <OverlayTracker onAdd={handleOverlayAdd} onRemove={handleOverlayRemove} />
        <LayersControl position="topleft">
          {bases.map((base) => (
            <LayersControl.BaseLayer
              key={base.key}
              name={base.key === 'osm' ? t('baseOsm') : t('baseCarto')}
              checked={base.isDefault}
            >
              <TileLayer attribution={base.attribution} url={base.url} />
            </LayersControl.BaseLayer>
          ))}
          {overlays.map((overlay) => (
            <LayersControl.Overlay
              key={overlay.key}
              name={overlay.key === 'prodes' ? prodesName : deterName}
              checked={false}
            >
              <WMSTileLayer
                url={overlay.url}
                layers={overlay.layers}
                format={overlay.format}
                transparent={overlay.transparent}
                version={overlay.version}
                opacity={overlay.opacity}
                attribution={overlay.attribution}
                eventHandlers={{
                  tileerror: () => setWmsAvailable(false),
                }}
              />
            </LayersControl.Overlay>
          ))}
        </LayersControl>
      </MapContainer>

      {/* Aviso traduzido: noCoords (base) → activeLayers / wmsUnavailable (camada ativa) */}
      <p
        role="status"
        className="absolute left-1/2 top-3 z-[500] w-max max-w-[calc(100%-2rem)] -translate-x-1/2 rounded-full border border-border bg-surface/95 px-3 py-1.5 text-center text-xs text-fg-secondary shadow-sm"
      >
        {statusText}
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

      {/* Legenda Verde Agro + camadas ativas (fallback estático se WMS cair) */}
      <div
        aria-label={t('legendTitle')}
        className="absolute bottom-3 right-3 z-[500] flex max-w-[calc(100%-1.5rem)] flex-col gap-1 rounded-lg border border-border bg-surface/95 px-2.5 py-1.5 text-xs text-fg-secondary shadow-sm"
      >
        <span className="flex items-center gap-2">
          <span
            aria-hidden="true"
            className="size-2.5 shrink-0 rounded-full"
            style={{ backgroundColor: 'var(--color-primary)' }}
          />
          {t('legendBase')}
        </span>
        {hasActiveOverlay && (
          <span className="flex flex-col gap-1 border-t border-border pt-1">
            <span className="font-semibold">{t('legendActiveTitle')}</span>
            {activeOverlays.map((name) => (
              <span key={name} className="flex items-center gap-2">
                <span
                  aria-hidden="true"
                  className={`size-2.5 shrink-0 rounded-[3px] ${overlayChipClass(name, prodesName, deterName)}`}
                />
                {name}
              </span>
            ))}
          </span>
        )}
      </div>

      {/* Equivalente textual para leitores de tela */}
      <p className="sr-only">{t('srDescription')}</p>
      <ul className="sr-only">
        <li>{t('noCoords')}</li>
        {activeOverlays.map((name) => (
          <li key={name}>{name}</li>
        ))}
      </ul>
    </div>
  );
}
