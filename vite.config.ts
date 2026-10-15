import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const srcDir = path.dirname(fileURLToPath(import.meta.url))

/**
 * Single source of truth for the deploy sub-path is `VITE_BASENAME`.
 * - Explicit `VITE_BASENAME` always wins (dev and build).
 * - Otherwise: `/` for `vite dev` (serve at root, no local 404),
 *   `/LANDAGRI-B_Dashboard/` for `vite build` (gh-pages project page).
 * Must stay in sync with `getBasename()` in `src/config/routes.tsx`.
 */
const DEFAULT_PROD_BASENAME = '/LANDAGRI-B_Dashboard';

function normalizeBase(raw: string): string {
  const trimmed = raw.trim();
  if (!trimmed || trimmed === '/') return '/';
  return `/${trimmed.replace(/^\/+|\/+$/g, '')}/`;
}

export default defineConfig(({ command }) => {
  const envBasename = process.env.VITE_BASENAME;
  const base =
    envBasename && envBasename.trim()
      ? normalizeBase(envBasename)
      : command === 'build'
        ? `${DEFAULT_PROD_BASENAME}/`
        : '/';
  return {
  plugins: [react(), tailwindcss()].flat(),
  resolve: {
    alias: {
      '@': path.join(srcDir, 'src'),
    },
  },
  base,
  build: {
    outDir: 'dist',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks(id: string) {
          // Plotly - largest library, separate chunk
          if (id.includes('plotly.js-dist-min')) return 'plotly'
          // React Router - often changes less
          if (id.includes('react-router')) return 'router'
          // Leaflet - only used on overview map
          if (id.includes('leaflet')) return 'leaflet'
          // Other node_modules in a vendor chunk
          if (id.includes('node_modules')) return 'vendor'
        },
      },
    },
  },
  };
})
