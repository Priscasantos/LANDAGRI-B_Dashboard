# Data pipeline — source of truth (Fase 3)

Two different mechanisms serve data in this SPA. Do not mix them.

## 1. Build-time data (bundled imports)

- **Raw sources:** `data/` — `json/*.jsonc`, `csv/*.csv`, `*.xlsx`, top-level `*.json`.
- **Generate:** `npm run preprocess` → `scripts/preprocess-data.mjs` writes
  `src/data/processed/*.json`.
- **Consume:** static JSON imports, e.g.
  `AgriculturalCharts.tsx` ← `src/data/processed/brazilian_agricultural_data.json`.
  These files are **bundled** into JS chunks at build time.
- **Status:** `src/data/processed/` is committed (except `conab_safra_2425.json`,
  git-ignored as too large — regenerate via `npm run preprocess`).

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
