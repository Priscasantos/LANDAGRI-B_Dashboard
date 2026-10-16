# Data pipeline — source of truth (Fase 3)

Two different mechanisms serve data in this SPA. Do not mix them.

## 1. Build-time data (bundled imports)

- **Raw sources:** `data/` — `json/*.jsonc`, `csv/*.csv`, `*.xlsx`, top-level `*.json`.
- **Generate:** `npm run preprocess` → `scripts/preprocess-data.mjs` writes
  `src/data/processed/*.json`.
- **Consume:** static JSON imports, e.g.
  `AgriculturalCharts.tsx` ← `src/data/processed/brazilian_agricultural_data.json`.
  These files are **bundled** into JS chunks at build time.
- **Status:** `src/data/processed/` is committed (except `conab_safra_2425.json`
  and `conab_safra_2526.json`, git-ignored as too large — regenerate via `npm run preprocess`).

## 2. Runtime data (fetched over HTTP)

- **Consumers:** `src/hooks/useInitiatives.ts` fetches
  `{basename}/data/processed/initiatives.json` and `sensors.json`,
  where `basename` comes from `getBasename()` (`VITE_BASENAME` or
  `/LANDAGRI-B_Dashboard` default) — the same basename as the router,
  so deploys under a different sub-path keep working.
- **Source of truth:** `src/data/processed/{initiatives,sensors}.json`
  (the preprocess output). **Do not hand-edit `public/` copies.**
- **Sync:** `npm run prebuild` → `scripts/copy-data.mjs` copies
  `src/data/processed/*.json` → `public/data/processed/*.json`
  **idempotently** (SHA-256 compare; identical files are skipped so mtimes
  and caches are preserved). Missing `src/` files fail the build with
  a "run `npm run preprocess`" hint.
- **Publish:** `vite build` copies `public/` → `dist/` automatically
  (`copy-data` also mirrors to `dist/` best-effort when it exists).
  `QueryClient` defaults (`staleTime: 60s`, `retry: 1`, no refetch on focus)
  apply to future react-query usage; current loading uses fetch + zustand.

## 3. Perf / chunk map (Fase 3, verified 2026-10-14)

- `vite.config.ts → manualChunks`: `plotly` (~4.5 MB, `plotly.js-dist-min`),
  `router` (`react-router`), `leaflet` (`leaflet`/`react-leaflet`), `vendor`
  (rest of `node_modules`). Plotly loads on demand via dynamic `import()`
  (`PlotlyLazyChart`); recharts ships in the normal vendor path.
- **Leaflet:** `leaflet` + `react-leaflet` are declared deps and
  `src/index.css` imports `leaflet/dist/leaflet.css`, but **no component
  currently imports `react-leaflet`/`leaflet`** (only static charts on
  Overview). So today the `leaflet` chunk is empty/absent and adds no JS
  weight — the `manualChunks` rule is kept so a future Overview map split
  lands in its own chunk. When adding a map: `lazy()`-import it inside the
  Overview route only (per-route `Suspense` + `ErrorBoundary` already exist
  in `App.tsx` via Fase 1), never at module top level.
- **Regenerating this doc's claims:** `npm run build && vite preview`,
  then check `dist/assets/leaflet-*.js` absence and `plotly-*.js` presence.

## 4. Fase 4 hardening (verified 2026-10-14, no deploy)

- **Basename single source of truth:** `VITE_BASENAME` env. `vite.config.ts`
  derives `base` from it (explicit wins; else `/` for `vite dev`, else
  `/LANDAGRI-B_Dashboard/` for `vite build`), `src/config/routes.tsx`
  `getBasename()` follows the same rule (dev → `/`, prod → default),
  `index.html` uses `<base href="%BASE_URL%">` + `%BASE_URL%favicon.svg`
  (no hardcoded sub-path), and `public/404.html` resolves the basename at
  runtime (app-stored `landagri-basename` → first-path-segment fallback)
  while preserving query + hash into `sessionStorage.redirectPath`.
- **Drift gate:** `node scripts/copy-data.mjs --check` (alias `--verify`)
  exits 1 when `public/data` drifts from `src/data/processed`; CI job
  `data-drift` gates `build`. The `dist/` mirror strips the `public/`
  prefix (`dist/data/...`, never `dist/public/...`).
- **Runtime schema:** `useInitiatives` validates both payloads
  (`validateInitiativesPayload` / `validateSensorsPayload`) — malformed
  JSON surfaces as a store error, never a silent empty dashboard.
- **Local preview under basename:** `npm run preview` passes
  `--base ${VITE_BASENAME:-/LANDAGRI-B_Dashboard/}` (plain `vite preview`
  serves statics at root and 404s sub-path assets). e2e `webServer` uses it.
- **Dead code removed:** `DashboardLayout` + `Sidebar` + `Breadcrumbs` +
  `PageTransition` (nothing imported them; shell is `RootLayout` +
  `Header`). Drawer a11y (Escape, `role=dialog`/`aria-modal`, focus trap,
  `aria-current`, `<Link>`) lives in `Header.tsx`.

## 5. CONAB typed outputs (P0, reversible; Fase 1 saneamento 2026-10-16)

- **Calendar/availability:** `processCsv` is delimiter-aware (`;`/`,`, BOM/CRLF)
  and emits typed rows only (`{crop, uf, months[12]}` Oct→Sep; `{crop, uf,
anos_1s, anos_2s, is_long_aggregate}`). The legacy `;`-joined single keys
  were removed — all 8 consumers (`CropCalendar/*Tab` × 7,
  `AgricultureAvailabilityPage`) read typed arrays
  (`src/types/calendar.ts`: `ConabCalendarRow`/`ConabAvailabilityRow`).
  `src/test/data/noLegacySemicolon.test.ts` regresses this.
- **Canonical availability:** `src/types/calendar.ts` →
  `CalendarAvailability {cropId, month 1-12, region UF, plantingPct,
harvestPct, areaSharePct?, source, vintage, updatedAt}` +
  `normalizeCalendarRows()` (P→100/0, H→0/100, PH→50/50, blank→0/0).
- **PAM i18n único:** `brazilian_agricultural_data.json` (PT) +
  `brazilian_ibge_agricultural_data.json` (EN) carry identical numerics, so
  preprocess fuses them into `src/data/processed/pam_unified.json`
  (stable EN slugs + `{pt, en}` name dictionary, single numeric payload;
  `buildPamUnified` throws on any PT/EN divergence). The per-language copies
  are no longer emitted — bundle payload ~halved (23.5 KB → 12.8 KB).
- **`Anos (1S)/(2S)`:** crop years with mapping in the 1st/2nd-semester
  campaign (`"YYYY-YYYY"` pairs). Empty crop cells forward-fill from the
  row above; Area `Brazil` → `BR` (national aggregate). Full notes in
  `src/data/processed/conab_data_notes.json`.
- **Long aggregates** (`2000-2014`, `2000-2015`, …) are multi-year rollups,
  not single agricultural years — flagged `is_long_aggregate`, keep them
  out of per-year axes (covered by `src/test/scripts/preprocess-data.test.ts`).
- **Safra XLSX:** header-row detection + merged sub-header folding
  (`SAFRAS 24/25`, `PRODUÇÃO (Em mil t) Safra 25/26 (f)`); zero `__EMPTY`
  keys; all-null columns trimmed. `conab_safra_2023_24.xlsx` re-downloaded
  2026-10-16 (12º levantamento 2023/24, 76 sheets) — marker `_unavailable`
  substituído por dados reais. `conab_serie_historica.xlsx` segue marcador
  de download falho: série histórica CONAB não tem URL estável trivial
  (portal é SPA sem link direto) — ingestão pulada com nota, sem inventar
  dados.
- **Seasons:** `conab_agricultural_data.json` carries `2024/25` (closed,
  Jul/2025) + `2025/26` (forecast; CONAB grain total 361.7 Mt —
  9 tracked crops sum ~357.1 Mt). `ConabEstimatesTab` KPIs use the last
  closed harvest (`2024/25`); charts also plot the forecast.
- **Naming:** initiative `coverage: "National"`, dictionary `Country →
Nacional/National` (glossary `REGION.National`); `Brazil`/`Brasil` remain
  only in territory metadata strings.
- **Area shares cultura×UF (Gaia, 2026-10-16):** heatmaps de calendário
  ponderavam por nº de UFs (`mode: 'uf'`) por falta de área por UF.
  `scripts/preprocess-data.mjs → buildAreaShares()` deriva
  `areaSharePct` (% da área nacional da cultura na UF) das abas por UF de
  `data/conab_safra_2024_25.xlsx` (safra 2024/25 fechada, Jul/2025; matriz
  completa em `src/data/processed/conab_area_shares.json`, 10/10 culturas
  do calendário, soma-UFs == total nacional com diff 0%) e
  `attachAreaShares()` grava o campo em `conab_calendar.json`
  (`src/types/calendar.ts → normalizeCalendarRows` propaga só nº finito;
  cultura sem fonte UF fica sem o campo e o UI mantém o fallback `uf`
  rotulado). PAM do repo é nacional-agregada (`territory_level: Nacional`)
  e **não** fornece UF — lacuna documentada, nada estimado.
